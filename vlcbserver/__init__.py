#import  vlcbserver
from flask import Flask
from flask_wtf.csrf import CSRFProtect
import time
import logging, os
import random
import string

# Globals for passing information between threads
# needs default settings
debug = True

# List containing data received
data = []
data_index = 0 # index number for first entry in array
# eg. if 10 entries removed from start then this will be increased to 10 and
# new entries will be relative to that

messages = []

def send_data(data_string):
    messages.append(data_string)

# Returns data as a list
# First entry is a status entry
def get_data(start=0, last=None):
    # if start is higher than last then return error
    data_last = data_index + len(data)
    if start > data_last:
        return ["Read,0,0,-1"]
    # if start is 1 more than last entry then that would be the next
    if start == data_last + 1:
        return ["Read,0,0,0"]
    # if start is negative then it's relative from end
    if start < 0:
        start = data_last + start # Add as start is negative this is from end
    # Now check for within range
    if start < data_index:
        start = data_index
    if last == None or last > data_last:
        last = data_last
    # If no data return null status
    if last <= start:
        return ["Read,0,0,0"]
    # Reach here there should be some data we can send
    return_data = [f"Read,{start},{last-1},{last-start}"]
    for i in range (start, last):
        return_data.append(f"{i},{data[i-data_index]}")
    return return_data

# Should always run with csrf=True
# csrf_enable=False is only included for testing purposes (disables CSRF)
# debug = True (include debug messages in log - eg Testing)
# debug = False - minimum INFO messages are logged
def create_app():
    #pixelserver.auth_config_filename = auth_config_filename
    #pixelserver.auth_users_filename = auth_users_filename
    
    if debug==False:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    
#    start_logging (log_filename, log_level)
    #vlcbserver.auth = ServerAuth(auth_config_filename, auth_users_filename)
    
    #if csrf_enable:
    csrf = CSRFProtect()
    app = Flask(
        __name__,
        template_folder="www"
        )
    # Create a secret_key to last whilst the program is running
    app.secret_key = ''.join(random.choice(string.ascii_letters) for i in range(15))
    #if csrf_enable:
    csrf.init_app(app)
    register_blueprints(app)
    return app
    
#Turn on logging through systemd
#def start_logging(log_filename, log_level=logging.INFO):
#    logging.basicConfig(level=log_level, filename=log_filename, filemode='a', format='%(asctime)s %(levelname)-4s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
#    logging.info ("PixelServer application start")
    
#Register routes as @requests
def register_blueprints(app):
    from vlcbserver.requests import requests_blueprint
    app.register_blueprint(requests_blueprint)