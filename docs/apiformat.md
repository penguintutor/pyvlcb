# API format for PyVLCB (not yet implemented - initial thoughts only)

## Connect to API

Used for authentication with API
First try and connect - if valid token then allow and confirm
if not then require login

/connect
/login POST username, password
handled locally within api


## Raw Commands
These are the only ones currently implemented
Note for simplicity these are provided in a strict order and format

/vlcb?read=<id of first data packet>&format=txt&[&end=<id last packet to retrieve]
/vlcb?send=<string of send request>&format=txt

read can also use read=-<value> to count from end instead of packet number
if a start packet doesn't exist then start from lowest value


#read is used to "read" stored data

possibly allow get / query to integrate individual items - but currently expect the client to create
these as send commands

Send must be a single CBUS message starting with : and ending with ; (url encoded)
All content must be alphanum - anything else and it will not be sent to CBUS










## Server commands

Issue command to the server, includes quit or future connect to different USB port etc.

/server?cmd=quit
server,quit

/server?cmd=status
server,status


## Raw commands

/vlcb?data=<raw data>
vlcb,data
(data typically :S???????;

## Console

Query the console
/console?start=<lognum>
console,lognum
Returns log entries starting with lognum
Numbering starts with 0, so 0 will try and return all entries, but limited internally to set number
response includes total number of log entries
Passing a negative number will count that far back from end of log

## Query

These query the local nodes database within vlcbautomate 

/query,type=nodes
query,nodes
returns list of nodes

/query,type=events,node=<nodeid>
query,events,<nodeid>
returns list of events associated with a node

Raw data format msg_num,timestamp,message


