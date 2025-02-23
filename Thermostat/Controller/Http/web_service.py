'''
In case you need to test form external network, please, use NGROK
https://download.ngrok.com/downloads/linux
'''

from Controller import utils

import http.server
import socketserver
import base64
import json
import time
import threading

# Fixed user and pass
USERNAME = "admin"
PASSWORD = "senha123"

CWebServicePort = 1579 # 819242 % 2009, 1st OCEAN block height MOD first block year

# Check authentication creadentials
def checkAuthentication(headers):
    auth_header = headers.get('Authorization')
    
    if not auth_header:
        return False
    
    # The header for BASIC Authentication follows the patter "Basic <Base64(user:pass)>"
    prefix, encoded_credentials = auth_header.split(' ', 1)
    
    if prefix.lower() != 'basic':
        return False
    
    # Decoding the auth base64 string
    decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
    
    # BASIC auth is separated by :
    username, password = decoded_credentials.split(':', 1)
    
    # Checking if username and password matches
    return username == USERNAME and password == PASSWORD

'''
Returns all the registered endpoints in JSON format, keep it manually updated (latter maybe Swagger?)
if key "content-type" not present, dafult is always application/json
'''
def registeredEndPoints():
    json_array = json.loads('[]')
    json_array.append({
        "name":"Echo",
        "desc":"get Echo",
        "permission":"pub",
        "verb":"get"
        })
    json_array.append({
        "name":"DateTime",
        "desc":"get DateTime",
        "permission":"pri",
        "verb":"get"
        })
    json_array.append({
        "name":"processSomething",
        "desc":"post processSomething",
        "permission":"pri",
        "verb":"post"
        })    
    return json.dumps(json_array)
    

# HTTP class handler
class HttpHandler(http.server.BaseHTTPRequestHandler):
    # Generic response
    def send_response_generic(self, status_code, content_type, response_data):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        # Checks the type of response_data
        if isinstance(response_data, str):
            self.wfile.write(response_data.encode('utf-8'))
        else:
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def do_GET(self):
        try:
            # If not public paths, check authentication
            if self.path not in ['/Echo', '/favicon.ico']:
                if not checkAuthentication(self.headers):
                    self.send_response_generic(403, 'text/html', 'Forbidden')
                    return
            
            # [Public] checks if server is alive
            if self.path == "/Echo":
                response = {"result": "OK"}
                self.send_response_generic(200, 'application/json', response)

            
            # [Public] Only when requesting from browser, doesn't return anything
            elif self.path == "/favicon.ico":
                self.send_response(200)
                self.send_header('Content-type', 'image/x-icon')
                self.end_headers()
                return
            
            # ## Keep all public methods above this line ##
            
            # Returns current date time in timestamp UTC
            elif self.path == "/DateTime":
                response = {"result": utils.nowUtc()}
                self.send_response_generic(200, 'application/json', response)
            
            elif self.path == "/RegisteredEndPoints":
                self.send_response_generic(200, 'application/json', registeredEndPoints())
            
            # Returns the saved /config/thermine_config.json Uuid key, creates a new one if empty
            elif self.path == "/Uuid":
                # utils.pathConfig()
                self.send_response_generic(200, 'application/json', utils.thermineUuid())
            
            else:
                self.send_response_generic(400, 'text/html', 'Not found')

        except Exception as e: # catch error if need
            error_msg = str(e) # get the excpetion as String
            response = {"error": f"{self.path} {error_msg}"};
            self.send_response_generic(500, 'application/json', response)
            return
    
    def do_POST(self):
        try:
            # If not public paths, check authentication
            if self.path not in ['/NoPublicPathYet']: 
                if not checkAuthentication(self.headers):
                    self.send_response_generic(403, 'text/html', 'Forbidden')
                    return

            # Example of Post for processing something
            if self.path == "/processSomething":
                # Examples of how to work with headers
                headers = self.headers
                for header, value in headers.items():
                    print(f"{header}: {value}")
                
                content_length = int(self.headers['Content-Length'])  # read the size of content
                post_data = self.rfile.read(content_length)  # read the content
            
                json_data = json.loads(post_data.decode('utf-8'))  # serialize to JSON
                # print("DEBUG LOG, data received:", json_data)

                # Work with the JSON as you wish: change local files, read DB, etc
                # Example: we add new data
                json_data["timestamp"] = int(time.time())
                self.send_response_generic(200, 'application/json', json_data)
                
            else:
                self.send_response_generic(400, 'text/html', 'Not found')

        except Exception as e: # catch error if need
            error_msg = str(e) # get the excpetion as String
            response = {"error": f"{self.path} {error_msg}"};
            self.send_response_generic(500, 'application/json', response)
            return

Handler = HttpHandler

# Start listen (locks the process)
def Listen():
    with socketserver.TCPServer(("", CWebServicePort), Handler) as httpd:
        print(f"Server HTTP runing on port {CWebServicePort}")
        httpd.serve_forever()

# Start listen in a thread, doest not lock the process
def ListenThread():
    server_thread = threading.Thread(target=Listen)
    server_thread.start()