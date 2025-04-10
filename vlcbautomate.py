# Provides ability to automate actions
# Also handles the creation of the GUI process and messages between the GUI and the app

from multiprocessing import Lock, Process, Queue, current_process
#from fastapi import FastAPI
#from serverapi import ServerApi
from flaskapi import FlaskApi
import time
import queue

class VLCBAutomate ():
    def __init__ (self, requests, responses, commands, status):
        self.debug = False
        self.requests = requests
        self.responses = responses
        self.commands = commands
        self.status = status
        # Create extra set of queues to communicate with GUI process
        self.api_requests = Queue()    
        self.api_responses = Queue()   # Typically these are responses to requests, but could be error / not connected - also copy of requests from automate

        # create processes
        # process for handling events
        self.api_process = Process(target=self.start_api, args=(self.api_requests, self.api_responses))
        
        
    def start_api(self, api_requests, api_responses):
        print ("Starting API")
        api = FlaskApi(api_requests, api_responses)
        

    def run (self):
        self.api_process.start()
        while True:
            if self.debug:
                print ("Checking loop")
            # First check if any commands from the api
            # those normally take priority, but only send one at a time as otherwise could
            # result in not clearing any off the status and/or response queue
            try:
                api_request = self.api_requests.get_nowait()
            except queue.Empty:
                if self.debug:
                    print ("Queue empty")
                pass
            else:
                if self.debug:
                    print (f"Requests received {api_request}")
                # If quit pass on to the app, then break out of the loop
                # If app has already closed then this will meet join at the end
                if api_command == "quit" or api_command == "exit":
                    self.commands.put("exit")
                    break
                # for other commands then handle here
                else:
                    pass
            
            if self.debug:
                print ("Any status")
            # Check for any responses to commands these should be approx 1:1 so don't need to keep polling
            try:
                current_status = self.status.get_nowait()
            except queue.Empty:
                if self.debug:
                    print ("Status empty")
            else:
                # print any response received
                if self.debug:
                    print (f"Status {current_status}")
            
            # Check to see if we have any responses
            # This includes any other messages on the CBUS
            # Do this to clear input queue before sending any new requests
            try:
                response = self.responses.get_nowait()
            except queue.Empty:
                if self.debug:
                    print ("Response queue empty")
            else:
                if self.debug:
                    print (f"Response received {response}")
                # Todo - handle responses
            # Todo Handle errors
            
            if self.debug:
                print ("Any requests")
            # Do we have a request to send out?
            # If so send it now
            #self.requests.put(api_request)
            # Also echo to api_responses
            #self.api_responses.put(api_request)
                
            # Todo check if we have any of our own requests to send out
            
            
            # Short sleep to reduce number of checks
            time.sleep(0.5)

        if self.debug:
            print ("Automate loop closed")
        self.api_process.join()


