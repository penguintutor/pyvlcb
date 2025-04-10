from flask import Flask

class FlaskApi:
    
    api = Flask(__name__)
    
    def __init__ (self, requests, responses):
        #self.api = Flask(__name_)
        self.api.run(host="0.0.0.0", port=8000)
        
    @api.route("/")
    def root_file():
        return "<p>Hello</p>"