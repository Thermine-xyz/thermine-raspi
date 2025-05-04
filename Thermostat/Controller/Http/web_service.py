'''
In case you need to test form external network, please, use NGROK
https://download.ngrok.com/downloads/linux
'''

from Controller.Http import web_service_handler
from Controller import Utils
from Controller import HttpException

import http.server
import socketserver
import base64
import json
import threading
import queue

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
    def send_response_generic(self, status_code, content_type, response_data, path):
        if not(status_code > 199 and status_code < 300):
            Utils.logger.error(f"{path} - {response_data}")
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
            if self.path not in ['/Echo', '/favicon.ico', '/Miner/Echo']:
                if not checkAuthentication(self.headers):
                    self.send_response_generic(403, 'text/html', 'Forbidden', self.path)
                    return
            
            response_data, status_code, content_type = web_service_handler.handle_get(self.path, self.headers)

            if response_data is None:  # In case no content response
                self.send_response(status_code)
                self.send_header('Content-type', content_type)
                self.end_headers()
                return

            self.send_response_generic(status_code, content_type, response_data, self.path)

        except HttpException as httpExc:
            response = {"error": f"{str(httpExc.message)}"}
            self.send_response_generic(httpExc.status_code, 'application/json', response, self.path)
        except Exception as e:
            error_msg = str(e)
            response = {"error": f"{self.path} {error_msg}"}
            self.send_response_generic(500, 'application/json', response, self.path)

    def do_PATCH(self):
        try:
            # If not public paths, check authentication
            if self.path not in ['/NoPublicPathYet']:
                if not checkAuthentication(self.headers):
                    self.send_response_generic(403, 'text/html', 'Forbidden', self.path)
                    return

            content_length = int(self.headers['Content-Length'])
            content = self.rfile.read(content_length)
            response_data, status_code, content_type = web_service_handler.handle_patch(self.path, self.headers, content)

            self.send_response_generic(status_code, content_type, response_data, self.path)

        except HttpException as httpExc:
            response = {"error": f"Erro de requisição: {str(httpExc.message)}"}
            self.send_response_generic(httpExc.status_code, 'application/json', response, self.path)
        except Exception as e:
            error_msg = str(e)
            response = {"error": f"{self.path} {error_msg}"}
            self.send_response_generic(500, 'application/json', response, self.path)

    def do_POST(self):
        try:
            # If not public paths, check authentication
            if self.path not in ['/NoPublicPathYet']:
                if not checkAuthentication(self.headers):
                    self.send_response_generic(403, 'text/html', 'Forbidden', self.path)
                    return

            content_length = int(self.headers['Content-Length'])
            content = self.rfile.read(content_length)
            response_data, status_code, content_type = web_service_handler.handle_post(self.path, self.headers, content)

            self.send_response_generic(status_code, content_type, response_data, self.path)

        except HttpException as httpExc:
            response = {"error": f"Erro de requisição: {str(httpExc.message)}"}
            self.send_response_generic(httpExc.status_code, 'application/json', response, self.path)
        except Exception as e:
            error_msg = str(e)
            response = {"error": f"{self.path} {error_msg}"}
            self.send_response_generic(500, 'application/json', response, self.path)

Handler = HttpHandler

# Start listen (locks the process)
def Listen(statusQueue):
    try:
        with socketserver.TCPServer(("", CWebServicePort), Handler) as httpd:
            Utils.logger.info(f"Server HTTP runing on port {CWebServicePort}")
            statusQueue.put(True)
            httpd.serve_forever()
    except Exception as e:
        Utils.logger.error(f"web_service Listen error {e}")
        statusQueue.put(False)

# Start listen in a thread, doest not lock the process
def ListenThread():
    statusQueue = queue.Queue()
    server_thread = threading.Thread(target=Listen, args=(statusQueue,))
    server_thread.start()
    try:
        started_ok = statusQueue.get(timeout=5) # wait 5 sec for the Thread process
        if started_ok:
            Utils.logger.info("web_service ListenThread")
        else:
            raise Exception("web_service ListenThread did not started properly")
    except queue.Empty:
        Utils.logger.error("web_service ListenThread error timeout")