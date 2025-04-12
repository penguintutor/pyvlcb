from flask import Flask
import json

class FlaskApi:
    
    api = Flask(__name__)
    data = ""
    
    def __init__ (self, requests, responses):
        #self.api = Flask(__name_)
        self.api.run(host="0.0.0.0", port=8000)
        
        # get secret key
        with open("secret.cfg") as secret_file:
            FlaskApi.data = json.load(secret_file)
        #apisecret = 
        
    @api.route("/")
    def root_file():
        return f"<p>Hello{FlaskApi.data}</p>"