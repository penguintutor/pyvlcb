# Client interface for VLCB server 
# sends using url to vlcbserver (c version)
# Needs url (eg. http://127.0.0.1:8888/)

# Note due to url restrictions : and ; need to be encoded

import urllib.request, urllib.parse

class VLCBClient():
    def __init__ (self, url):
        self.url = url
        self.debug = False
     
    
    def send (self, message):
        message = urllib.parse.quote(message)
        request_string = f"{self.url}vlcb?send={message}&format=txt"
        if (self.debug):
            print (f"Send request {request_string}")
        try:
            request_url = urllib.request.urlopen(request_string)
            #print(request_url.read())
            #print ("\n")
            response = request_url.read()
        except:
            print ("Error sending via http")
            # None indicates not connected
            return None
        if response[0:7] == "Success":
            #print ("Success")
            return True
        return False
    
    # Read after last packet 
    def read (self, last_packet):
        # if lastpacket does not have a value then read from 0 (have no data)
        if last_packet == None:
            last_packet = -5
        else:
            last_packet += 1	# Read next packet
        request_string = f"{self.url}vlcb?read={last_packet}&format=txt"
        if (self.debug):
            print (f"Reading {request_string}")
        try:
            request_url = urllib.request.urlopen(request_string)
            response = request_url.read().decode('utf-8')
        except:
            print ("Error reading from http request")
            return None
        #print(response)
        #print ("\n")
        return response
        
        