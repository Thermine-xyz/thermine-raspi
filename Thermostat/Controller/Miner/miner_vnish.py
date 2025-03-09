from ..utils import Utils
from ..utils import HttpException
import requests
import json

class MinerVnish:        
    # Check if the miner is online
    def echo(jObj):
        try:
            if not isinstance(jObj, dict):
                Utils.throwExceptionInvalidValue("jObj is not JSON Object");
            Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
            endpoint = f"http://{jObj['ip']}/api/v1/status"

            response = requests.get(endpoint)
            response.raise_for_status()
            if not isinstance(response.text, dict): # based on vnish swagger doc, reponse should be 200 and a JSON object
                raise HttpException("vnish status response expected a JSON object string", 502)
            return None
        except HttpException as httpExc:
            raise
        except requests.exceptions.RequestException as e:
            raise Exception(f"echo: {e}")

    
    # Get the token from miner, param jObj: a miner JSON Object with IP and password
    def getJwtToken(jObj):
        try:
            if not isinstance(jObj, dict):
                Utils.throwExceptionInvalidValue("jObj is not JSON Object");
            Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
            Utils.jsonCheckKeyTypeStr(jObj, 'password', True, False)
            endpoint = f"http://{jObj['ip']}/api/v1/unlock"
            payload = {"pw": jObj['password']}

            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            response_data = response.json()
            
            if 'token' in response_data:
                return response_data['token']
            else:
                Utils.throwExceptionResourceNotFound(f"Token JWT: {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"getJwtToken: {e}")
