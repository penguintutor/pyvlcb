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
#define MAX_MSG_SIZE 255           // Maximum size of a message
#define MAX_MESSAGES 10           // Maximum number of messages in the queue
#define MAX_DATA 100              // Maximum number of CBUS messages

// --- Global Variables ---
volatile sig_atomic_t keep_running = 1; // Flag to control the main loop
mqd_t mq_main_reader = -1;              // Message queue descriptor for main thread (reader)
struct MHD_Daemon *daemon_ptr = NULL;   // Pointer to the MHD daemon instance
char data [MAX_DATA][MAX_MSG_SIZE];     // Shared memory - write in main thread - read in API


int discovery (int fd)
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

    printf("Handler Thread: Received request for URL: %s\n", url);

    // --- Send message to main thread ---
    // Open the existing message queue for writing
    // Note: This happens in the context of a request handler thread.
    // The queue MUST have been created by the main thread already.
    mq_writer = mq_open(MQ_NAME, O_WRONLY);
    if (mq_writer == (mqd_t)-1)
    {
        perror("Handler Thread: mq_open (writer) failed");
        // Decide how to handle this - maybe send an error response?
        // For simplicity, we'll just log and continue, but not send a message.
    }
    else
    {
        // Prepare the message
        snprintf(msg.text, MAX_MSG_SIZE, "Request received for: %s", url);

        // Send the message (non-blocking isn't strictly necessary for send,
        // but good practice if the queue could be full, though unlikely here)
        send_status = mq_send(mq_writer, (const char *)&msg, sizeof(msg), 0); // Priority 0
        if (send_status == -1)
        {
            perror("Handler Thread: mq_send failed");
            // Log error, maybe respond differently to the client
        }
        else
        {
            printf("Handler Thread: Message sent to main thread for URL: %s\n", url);
        }

        // Close the writer descriptor
        if (mq_close(mq_writer) == -1)
        {
            perror("Handler Thread: mq_close (writer) failed");
        }
    }

    // --- Send HTTP response back to the client ---
    //const char *page = "<html><body>Message sent to server's main thread.</body></html>";
    char page[255];
    sprintf(page, "<html><body>%s</body></html>", data[0]);
    printf ("Response Page %s ", page);
    response = MHD_create_response_from_buffer(strlen(page),
                                               (void *)page,
                                               MHD_RESPMEM_MUST_COPY);  // copy the string
                                               //MHD_RESPMEM_PERSISTENT); // Use PERSISTENT as page is const char*
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
	char buf[255];
	
	fd = open(MODEMDEVICE, O_RDWR | O_NOCTTY ); 
	if (fd <0) {perror(MODEMDEVICE); return 2; }
	
	tcgetattr(fd,&oldtio); /* save current port settings */
        
	bzero(&newtio, sizeof(newtio));
	newtio.c_cflag = BAUDRATE | CRTSCTS | CS8 | CLOCAL | CREAD;
	newtio.c_iflag = IGNPAR;
	newtio.c_oflag = 0;
	
	/* set input mode (non-canonical, no echo,...) */
	newtio.c_lflag = 0;
	 
	newtio.c_cc[VTIME]    = 0;   /* inter-character timer unused */
	newtio.c_cc[VMIN]     = 5;   /* blocking read until 5 chars received */
	
	tcflush(fd, TCIFLUSH);
	tcsetattr(fd,TCSANOW,&newtio);


    char *s = "Test string";

    // Convert the string to a char array
    strcpy(data[0], s);
    
    
    discovery (fd);

    // --- Main Loop ---
    // Keep running and check for messages from the API queue and CANUSB
    while (keep_running)
    {
        // Attempt to receive a message (non-blocking)
        bytes_read = mq_receive(mq_main_reader, (char *)&received_msg, sizeof(message_t), NULL);

        if (bytes_read >= 0)
        {
            // Message received successfully
            printf("Main Thread: <<< Received message: \"%s\" (%zd bytes) >>>\n",
                   received_msg.text, bytes_read);
            // Add null termination just in case, though snprintf should handle it
            received_msg.text[MAX_MSG_SIZE - 1] = '\0';
            // Process the message here...
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
		res = read(fd,buf,255);   /* returns after 5 chars have been input */
        buf[res]=0;               /* so we can printf... */
        printf("%s\n", buf);

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

    
    
    
    
