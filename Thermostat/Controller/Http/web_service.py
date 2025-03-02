'''
In case you need to test form external network, please, use NGROK
https://download.ngrok.com/downloads/linux
'''

from Controller.Http import web_service_handler

import http.server
import socketserver
import base64
import json
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
            
            response_data, status_code, content_type = web_service_handler.handle_get(self.path, self.headers)

            if response_data is None:  # In case no content response
                self.send_response(status_code)
                self.send_header('Content-type', content_type)
                self.end_headers()
                return

            self.send_response_generic(status_code, content_type, response_data)

        except Exception as e:
            error_msg = str(e)
            response = {"error": f"{self.path} {error_msg}"}
            self.send_response_generic(500, 'application/json', response)

    def do_POST(self):
        try:
            # If not public paths, check authentication
            if self.path not in ['/NoPublicPathYet']:
                if not checkAuthentication(self.headers):
                    self.send_response_generic(403, 'text/html', 'Forbidden')
                    return

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            response_data, status_code, content_type = web_service_handler.handle_post(self.path, self.headers, post_data)

            self.send_response_generic(status_code, content_type, response_data)

        except Exception as e:
            error_msg = str(e)
            response = {"error": f"{self.path} {error_msg}"}
            self.send_response_generic(500, 'application/json', response)

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