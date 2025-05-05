/**
 * @file mhd_mq_example.c
 * @brief Example demonstrating communication from a libmicrohttpd request
 * handler thread to the main thread using POSIX message queues.
 *
 * Compilation:
 * gcc mhd_mq_example.c -o mhd_mq_example -lmicrohttpd -lrt
 *
 * Usage:
 * ./mhd_mq_example
 * Then, access http://localhost:8888/some/path in your browser or using curl.
 * The main program will print messages received from the handler thread.
 * Press Ctrl+C to stop the server.
 */
 
#include <termios.h>
#include <sys/types.h>
#ifndef _WIN32
#include <sys/select.h>
#include <sys/socket.h>
#else
#include <winsock2.h>
#endif
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h> // For signal handling (Ctrl+C)
#include <unistd.h> // For sleep, unlink
#include <errno.h>  // For errno
#include <fcntl.h>  // For O_* constants
#include <sys/stat.h> // For mode constants
#include <mqueue.h> // For POSIX message queues

// Include libmicrohttpd header AFTER system headers that define types it uses
#include <microhttpd.h>

/* settings for canusb */
/* baudrate settings are defined in <asm/termbits.h>, which is
included by <termios.h> */
/* 115200 */
#define BAUDRATE B1152000          
/* change this definition for the correct port */
#define MODEMDEVICE "/dev/ttyACM0"
#define _POSIX_SOURCE 1 /* POSIX compliant source */

/* Settings for API */
#define PORT 8888

/* Settings for queue / shared memory */
#define MQ_NAME "/mhd_main_queue" // Message queue name (must start with /)
#define MAX_MSG_SIZE 50           // Maximum size of a single read from CBUS (just used for READ - can combine messages)
#define MAX_MESSAGES 10           // Maximum number of messages in the mqueue
#define MAX_DATA 110               // Maximum number of CBUS messages stored
#define SAFE_MAX_DATA 100          // The maximum number of values it is safe to return (must be less than MAX_DATA) to avoid race conditions
// SAFE_MAX_DATA vs MAX_DATA avoids needing to use mutex / spinlock to protect data
// MAX_DATA is the size of the array, but as it wraps then need to be able to guarentee all data read is not written 
// the difference is a buffer that is safe to write but cannot read without checking it's not been overwritten

// --- Global Variables ---
volatile sig_atomic_t keep_running = 1; // Flag to control the main loop
mqd_t mq_main_reader = -1;              // Message queue descriptor for main thread (reader)
struct MHD_Daemon *daemon_ptr = NULL;   // Pointer to the MHD daemon instance
char data [MAX_DATA][MAX_MSG_SIZE];     // Shared memory - write in main thread - read in API
//int first_data_pos = 0;                 // array position in data where first data is (either 0, or scroll where overwrite)
int next_data_pos = 0;                  // array position in data where next data to be written (this -1 is the last written)
unsigned long long num_messages_received = 0;          // Incremented each time a message is received (never reset unless app restarted)      
// If this was a unsigned long int then expected to be a least a year before this limit is reached using usnigned long long more likely to be thousands of years   

// Basic check that the request is a cbus message
// First character must be :
// Last character must be ;
// All others must be alphanumeric
// returns 0 for True, -1 for invalid character
int check_cbus_message (const char *message_string) 
{
    int length = strlen(message_string);
    if (message_string[0] != ':' || message_string[length-1] != ';') return -1;
    // search rest (excluding final)
    for (int i = 1; i < length - 1; i++)
    {
        if (!isalnum(message_string[i]))
        {
            return -1;
        }
    }
    return 0;
}

void copy_to_data (char *new_string)
{
    // copy into the next position
    strcpy (data[next_data_pos], new_string);
    printf ("Copied %s\n", data[next_data_pos]);
    num_messages_received += 1;
    // increment next pos
    next_data_pos += 1;
    // if reached end then move to beginning
    if (next_data_pos >= MAX_MSG_SIZE)
    {
        next_data_pos = 0;
    }
}

/*int discovery (int fd)
{
	char discovery[256] = ":SB780N0D;";
	char ch;
	int res;
	
	for (int i = 0; discovery[i] != '\0'; i++) {
		ch = discovery[i];
		printf("Writing character :%c ASCII:%d\n", ch, ch);
		res = write(fd, &ch, sizeof(ch));
		if (res < 0) {
			perror("write on SERIAL_DEVICE failed");
			return 2;
		}
	}
}*/


int send_data (int fd, char *data_string)
{
    char ch;
	int res;
    for (int i=0; data_string[i] != '\0'; i++) 
	{
		ch = data_string[i];
		res = write (fd, &ch, sizeof(ch));
		if (res < 0) 
		{
				perror ("Write failed on serial");
				return 2;
		}
	}
}

// --- Message Structure ---
typedef struct
{
    char text[MAX_MSG_SIZE];
} message_t;



// --- Signal Handler ---
void sigint_handler(int sig)
{
    (void)sig; // Unused parameter
    fprintf(stderr, "\nCtrl+C detected. Shutting down...\n");
    keep_running = 0;

    // Attempt graceful shutdown from signal handler (use with caution)
    if (daemon_ptr)
    {
        MHD_stop_daemon(daemon_ptr);
        daemon_ptr = NULL; // Avoid double-stopping in main cleanup
    }
    if (mq_main_reader != (mqd_t)-1)
    {
        mq_close(mq_main_reader);
        mq_unlink(MQ_NAME); // Clean up the queue name
        mq_main_reader = -1; // Avoid double-closing/unlinking
    }
     // Exit immediately if necessary, though letting main loop finish is cleaner
    // _exit(0);
}

// --- libmicrohttpd Request Handler ---
/**
 * @brief Handles incoming HTTP requests.
 * Sends the requested URL to the main thread via the message queue.
 * @param cls User-defined closure (unused here).
 * @param connection MHD connection handle.
 * @param url The requested URL string.
 * @param method The HTTP method (e.g., "GET", "POST").
 * @param version The HTTP version string.
 * @param upload_data Data uploaded by the client (if any).
 * @param upload_data_size Size of the uploaded data.
 * @param con_cls Per-connection closure pointer.
 * @return MHD_YES on success, MHD_NO on failure.
 */
enum MHD_Result answer_to_connection(void *cls, struct MHD_Connection *connection,
                                     const char *url, const char *method,
                                     const char *version, const char *upload_data,
                                     size_t *upload_data_size, void **con_cls)
{
    (void)cls;            // Unused parameter
    (void)method;         // Unused parameter
    (void)version;        // Unused parameter
    (void)upload_data;    // Unused parameter
    (void)upload_data_size; // Unused parameter
    (void)con_cls;        // Unused parameter

    mqd_t mq_writer = -1;
    message_t msg;
    struct MHD_Response *response;
    enum MHD_Result ret;
    int send_status;
    
    // Allow 1kb respoonse
    char response_data[1024] = "Error command not recognised";   // This will be replaced later if valid request
    
    const char *value;

    printf("Handler Thread: Received request for URL: %s\n", url);
    /* Handle URL here - see if we handle directly (eg. query) or pass to the message queue */
    // Is this a vlcb command (ie. raw format)
    const char *vlcb = "/vlcb";
    //if (strncmp (url, vlcb, 6))
    if (strcmp (url, vlcb) == 0)
    {
        printf ("Matches /vlcb\n");
        // Do we have a send request?
        value = MHD_lookup_connection_value(connection, MHD_GET_ARGUMENT_KIND, "send");
        if (value != NULL)
        {
            printf ("Value is %s - size %d\n", value, strlen(value));
            // Check that the string is a valid C Bus message
            if (check_cbus_message(value) != 0) 
            {
                perror ("Invalid message format - skipping");
                strcpy (response_data, "Error, invalid message format");
            }
            else
            {
                // --- Send message to main thread ---
                // Open the existing message queue for writing
                // Note: This happens in the context of a request handler thread.
                // The queue MUST have been created by the main thread already.
                mq_writer = mq_open(MQ_NAME, O_WRONLY);
                if (mq_writer == (mqd_t)-1)
                {
                    perror("Handler Thread: mq_open (writer) failed");
                    // Decide how to handle this - maybe send an error response?
                    // Log and update response
                    strcpy (response_data, "Error, failed top open message queue");
                }
                else
                {
                    // Send the message (non-blocking isn't strictly necessary for send,
                    // but good practice if the queue could be full, though unlikely here)
                    // not sizeof(value)
                    send_status = mq_send(mq_writer, value, strlen(value), 0); // Priority 0
                    if (send_status == -1)
                    {
                        perror("Handler Thread: mq_send failed");
                        // Log error, maybe respond differently to the client
                        strcpy (response_data, "Error, send meessage failed");
                    }
                    else
                    {
                        printf("Handler Thread: Message sent to main thread for URL: %s Value: %s Status %d\n", url, value, send_status);
                        strcpy (response_data, "Success, message sent");
                    }

                    // Close the writer descriptor
                    if (mq_close(mq_writer) == -1)
                    {
                        perror("Handler Thread: mq_close (writer) failed");
                    }
                }
            }
        } // End send
        else
        { 
            // check if it's a query of responses 
            // If so can get straight from shared memory
            value = MHD_lookup_connection_value(connection, MHD_GET_ARGUMENT_KIND, "query");
            if (value != NULL)
            {
                long int end_val;
                long int query_val = strtol (value,NULL,0);
                printf ("Query data from %d", query_val);
                
                // if it's negative then convert to actual value
                if (query_val < 0) query_val = num_messages_received - query_val;
                
                // check if end (last value to get)
                value = MHD_lookup_connection_value(connection, MHD_GET_ARGUMENT_KIND, "end");
                if (value != NULL) 
                {
                    end_val = strtol (value,NULL,0);
                    // If value is not valid (or does not make sense) then ignore the parameter
                    if (end_val < query_val) query_val = num_messages_received -1;  // -1 as index starts at 0
                }
                else end_val = num_messages_received -1; // -1 as index starts at 0
                
                
                /* Useful values from structure:
                 * num_messages_received -1 (last pos) is at next_data_pos -1
                 * if < 0 then next_data_pos -1 = MAX_DATA-1
                 * 
                 * message_num at index0 
                 *     zero_pos_msg_num = num_messages_received - next_data_pos
                 * 
                 * lowest safe message_num
                 *     first_data_pos = SAFE_MAX_DATA - next_data_pos
                 *     first_data_msg_num = zero_pos_msg_num - MAX_DATA + first_data_pos
                 * /**/
                                
                // Now get the data from query_val to the end
                // simplist is if we have not yet exceeded max value - just return all values to that point
                if (num_messages_received < SAFE_MAX_DATA) 
                {
                    response_data[0] = '\0';
                    for (int i=query_val; i<=end_val; i++)
                    {
                        strcat (response_data, data[i]);
                        strcat (response_data, "\n");
                    }
                }
                
                /** TODO - HANDLE other conditions - check edge cases **/
                
            } // End of query
        } // end of else (from first check for send)
    }


    // --- Send HTTP response back to the client ---
    //const char *page = "<html><body>Message sent to server's main thread.</body></html>";
    char page[255];
    sprintf(page, "<html><body>%s</body></html>", response_data);
    printf ("Response Page %s ", page);
    response = MHD_create_response_from_buffer(strlen(page),
                                               (void *)page,
                                               MHD_RESPMEM_MUST_COPY);  // copy the string


    if (!response)
    {
        fprintf(stderr, "Handler Thread: Failed to create MHD response.\n");
        return MHD_NO; // Internal error
    }

    MHD_add_response_header(response, MHD_HTTP_HEADER_CONTENT_TYPE, "text/html");
    ret = MHD_queue_response(connection, MHD_HTTP_OK, response);
    MHD_destroy_response(response); // Clean up the response object

    return ret;
}

// --- Main Function ---
int main(void)
{
    struct MHD_Daemon *daemon;
    struct mq_attr mq_attributes;
    message_t received_msg;
    ssize_t bytes_read;

    // --- Setup Signal Handling for Ctrl+C ---
    struct sigaction act;
    memset(&act, 0, sizeof(act));
    act.sa_handler = sigint_handler;
    sigaction(SIGINT, &act, NULL); // Handle interrupt signal

    // --- Initialize Message Queue ---
    printf("Main Thread: Setting up POSIX message queue: %s\n", MQ_NAME);

    // Define attributes for the message queue
    mq_attributes.mq_flags = 0;               // Flags (0 for blocking read by default)
    mq_attributes.mq_maxmsg = MAX_MESSAGES;   // Max messages in queue
    mq_attributes.mq_msgsize = sizeof(message_t); // Max message size
    mq_attributes.mq_curmsgs = 0;             // Current messages (ignored for mq_open)

    // Create/Open the message queue for reading by the main thread
    // O_CREAT: Create if it doesn't exist
    // O_RDONLY: Open for reading only
    // O_NONBLOCK: Make mq_receive non-blocking
    // 0660: Permissions (owner/group read/write)
    mq_main_reader = mq_open(MQ_NAME, O_CREAT | O_RDONLY | O_NONBLOCK, 0660, &mq_attributes);

    if (mq_main_reader == (mqd_t)-1)
    {
        perror("Main Thread: mq_open (reader) failed");
        // Try unlinking a potentially stale queue and retry
        fprintf(stderr, "Main Thread: Attempting to unlink potentially stale queue...\n");
        mq_unlink(MQ_NAME); // Best effort cleanup
        mq_main_reader = mq_open(MQ_NAME, O_CREAT | O_RDONLY | O_NONBLOCK, 0660, &mq_attributes);
        if (mq_main_reader == (mqd_t)-1) {
             perror("Main Thread: mq_open (reader) failed again after unlink");
             return 1; // Exit if queue cannot be created
        }
         printf("Main Thread: Successfully opened queue after unlinking.\n");
    } else {
        printf("Main Thread: Message queue opened successfully (Descriptor: %d).\n", (int)mq_main_reader);
    }
    

    // --- Start libmicrohttpd Daemon ---
    printf("Main Thread: Starting libmicrohttpd server on port %d\n", PORT);
    // MHD_USE_THREAD_PER_CONNECTION: Use a separate thread for each connection
    // MHD_USE_INTERNAL_POLLING_THREAD: Use internal select/poll thread (simpler)
    // Other options exist like MHD_USE_SELECT_INTERNALLY, MHD_USE_POLL
    daemon = MHD_start_daemon(MHD_USE_THREAD_PER_CONNECTION | MHD_USE_INTERNAL_POLLING_THREAD,
                              PORT, NULL, NULL,
                              &answer_to_connection, NULL, // Pass the handler function
                              MHD_OPTION_END);
    if (NULL == daemon)
    {
        fprintf(stderr, "Main Thread: Failed to start MHD daemon.\n");
        if (mq_main_reader != (mqd_t)-1) {
            mq_close(mq_main_reader);
            mq_unlink(MQ_NAME); // Clean up queue if daemon fails
        }
        return 1;
    }
    daemon_ptr = daemon; // Store globally for signal handler access
    printf("Main Thread: Server started. Waiting for requests and messages...\n");


    // Handle serial communications with CANUSB4    
	int fd,c, ch, res;
	struct termios oldtio,newtio;
	char buf[MAX_MSG_SIZE + 10];  // Must be at least MAX_MSG_SIZE - made larger so no risk of overflow
    char rec_data[MAX_MSG_SIZE+10]; // Remaining data is stored in this prior to transferring to data storage
    char rec_data_pos = 0; //next pos to store rec data
    char msg_q_rec[MAX_MSG_SIZE];
	
	fd = open(MODEMDEVICE, O_RDWR | O_NOCTTY ); 
	if (fd <0) {perror(MODEMDEVICE); return 2; }
	
	tcgetattr(fd,&oldtio); /* save current port settings */
        
	bzero(&newtio, sizeof(newtio));
	newtio.c_cflag = BAUDRATE | CRTSCTS | CS8 | CLOCAL | CREAD;
	newtio.c_iflag = IGNPAR;
	newtio.c_oflag = 0;
	
	/* set input mode (non-canonical, no echo,...) */
	newtio.c_lflag = 0;
	 
	newtio.c_cc[VTIME]    = 5;   /* inter-character timer unused  - 5 * 0.1 sec*/
	newtio.c_cc[VMIN]     = 0;   /* non blocking read */
	
	tcflush(fd, TCIFLUSH);
	tcsetattr(fd,TCSANOW,&newtio);


    // --- Main Loop ---
    // Keep running and check for messages from the API queue and CANUSB
    while (keep_running)
    {
        //printf ("Main Thread: Start of loop\n");
        // Attempt to receive a message (non-blocking)
        //bytes_read = mq_receive(mq_main_reader, (char *)&received_msg, sizeof(message_t), NULL);
        bytes_read = mq_receive(mq_main_reader, msg_q_rec, sizeof(message_t), NULL);
        

        if (bytes_read >= 0)
        {
            // Message received successfully
            //printf("Main Thread: <<< Received message: \"%s\" (%zd bytes) >>>\n",
            //       received_msg.text, bytes_read);
            // Add terminating 0
            msg_q_rec[bytes_read] = '\0';
            printf ("Q Data is %s - %d\n", msg_q_rec, bytes_read);
            // Add null termination just in case, though snprintf should handle it
            //received_msg.text[MAX_MSG_SIZE - 1] = '\0';
            // Process the message
            send_data (fd, msg_q_rec);
        }
        else
        {
            // No message received or an error occurred
            if (errno == EAGAIN)
            {
                // EAGAIN means the queue was empty (expected in non-blocking mode)
                // Do nothing, just wait
            }
            else if (errno == EINTR && !keep_running) {
                 // Interrupted by our signal handler, break the loop
                 break;
            }
            else
            {
                // An actual error occurred
                perror("Main Thread: mq_receive failed");
                // Consider breaking the loop or handling the error more robustly
                // For now, we just print the error and continue trying
            }
        }
        
        // check for USB
		res = read(fd,buf,MAX_MSG_SIZE);   /* returns after MAX_MSG_SIZE chars have been input */
        buf[res]=0;               /* Terminates the string */
        if (res > 0) printf("%s\n", buf);
        // rec_data
        // Todo split into data blocks - starting with : and ending with ;
        // first copy into rec_data and check for valid structure
        // then transfer that to the data storage and reset the counter in rec_data
        // any remaining chars are left on rec_data ready for next block
        // As reset each time there is a : then any corrupt messages will be dropped
        for (int i=0; i<MAX_MSG_SIZE; i++)
        {
            //printf ("In for loop i %d, buf size %d\n", i, res);
            // finish if reach end of new data (string terminator)
            if (buf[i] == 0) break;
            // move next char to rec_data
            rec_data[rec_data_pos] = buf[i];
            // if it's a : then restart (end not received so possibly corrupt)
            if (buf[i] == ':')
            {
                rec_data_pos = 0;
                continue;
            }
            // if it's a ; then reached end of packet
            // could perform additional processing if required 
            else if (buf[i] == ';')
            {
                // terminate the string
                rec_data[rec_data_pos+1] = 0;
                // copy into data
                copy_to_data (rec_data);
                // reset pos ready for next data
                rec_data_pos = 0;
                continue;
            }
            else 
            {
                rec_data_pos ++;
            }
            
        }

        // Sleep for a short duration to avoid busy-waiting
        // Adjust the sleep time as needed for responsiveness vs CPU usage
        usleep(100000); // Sleep for 100 milliseconds (100,000 microseconds)

        // Check keep_running again in case the signal arrived during sleep/receive
        if (!keep_running) {
            break;
        }
    }

    // --- Cleanup ---
    printf("Main Thread: Shutting down...\n");

    // Stop the MHD daemon if it hasn't been stopped by the signal handler
    if (daemon_ptr) {
        MHD_stop_daemon(daemon_ptr);
        printf("Main Thread: MHD daemon stopped.\n");
    } else {
        printf("Main Thread: MHD daemon already stopped (likely by signal handler).\n");
    }


    // Close and unlink the message queue if not done by signal handler
    if (mq_main_reader != (mqd_t)-1) {
        if (mq_close(mq_main_reader) == -1)
        {
            perror("Main Thread: mq_close (reader) failed");
        } else {
             printf("Main Thread: Message queue descriptor closed.\n");
        }

        // Unlink the message queue name from the system
        if (mq_unlink(MQ_NAME) == -1)
        {
            // Don't report ENOENT (No such file or directory) as an error
            // if it was already unlinked (e.g., by the signal handler or a previous run)
            if (errno != ENOENT) {
                 perror("Main Thread: mq_unlink failed");
            } else {
                 printf("Main Thread: Message queue already unlinked.\n");
            }
        } else {
             printf("Main Thread: Message queue unlinked successfully (%s).\n", MQ_NAME);
        }
    } else {
         printf("Main Thread: Message queue already closed/unlinked (likely by signal handler).\n");
    }


    printf("Main Thread: Exiting.\n");
    return 0;
}

    
    
    
    
