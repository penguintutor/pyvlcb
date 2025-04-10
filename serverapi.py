from fastapi import FastAPI
import unicorn
import asyncio

class ServerApi:
    
    def __init__(self):
        self.api = FastAPI()
        
    @self.api.get("/")
    async def read_root():
        return {"Message": "Test message"}
        
    def run(self):
        asyncio.run(start_server())
        
    def start_server(self):
        config = uvicorn.Config(self.api)
        server = uvicorn.Server(config)
        await server.serve()
        #self.api.uvicorn.run("main:server.app", host="0.0.0.0", port=8000)
            
        