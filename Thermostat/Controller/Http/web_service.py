'''
In case you need to test form external network, please, use NGROK
https://download.ngrok.com/downloads/linux
'''

import http.server
import socketserver
import base64
import json
import time

# Fixed user and pass
USERNAME = "admin"
PASSWORD = "senha123"

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

# HTTP class handler
class HttpHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        try:
            # If not public paths, check authentication
            if self.path not in ['/Echo', '/favicon.ico']:
                if not checkAuthentication(self.headers):
                    self.send_response(403)
                    self.send_header('WWW-Authenticate', 'Basic realm="Autenticação necessária"')
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write('Forbidden'.encode('utf-8'))
                    return
            
            # [Public] checks if server is alive
            if self.path == "/Echo":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"result": "OK"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            
            # [Public] Only when requesting from browser, doesn't return anything
            elif self.path == "/favicon.ico":
                self.send_response(200)
                self.send_header('Content-type', 'image/x-icon')
                self.end_headers()
                return
            
            # ## Keep all public methods above this line ##
            
            # Returns current date time in timestamp UTC
            elif self.path == "/DateTime":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                current_time = time.time()
                response = {"result": int(current_time)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('Not found'.encode('utf-8'))

        except Exception as e: # catch error if need
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_msg = str(e) # get the excpetion as String
            response = {"error": f"{self.path} {error_msg}"};
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
    
    def do_POST(self):
        try:
            # If not public paths, check authentication
            if self.path not in ['/NoPublicPathYet']: 
                if not checkAuthentication(self.headers):
                    self.send_response(403)
                    self.send_header('WWW-Authenticate', 'Basic realm="Autenticação necessária"')
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write('Forbidden'.encode('utf-8'))
                    return

            # Example of Post for processing something
            if self.path == "/processSomething":
                content_length = int(self.headers['Content-Length'])  # read the size of content
                post_data = self.rfile.read(content_length)  # read the content
            
                json_data = json.loads(post_data.decode('utf-8'))  # serialize to JSON
                # print("DEBUG LOG, data received:", json_data)

                # Work with the JSON as you wish: change local files, read DB, etc
                # Example: we add new data
                json_data["timestamp"] = int(time.time())
                
                # Send response (if necessary)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(json_data).encode('utf-8'))  # Retorna o JSON modificado
                
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('Not found'.encode('utf-8'))

        except Exception as e: # catch error if need
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_msg = str(e) # get the excpetion as String
            response = {"error": f"{self.path} {error_msg}"};
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

# Fixed port
PORT = 8000

Handler = HttpHandler

# Start listen
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server HTTP runing on port {PORT}")
    httpd.serve_forever()