from Controller import Utils
from ..Miner import Miner

import json
import time

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
        "name":"Miner",
        "desc":"get Miner (list)",
        "permission":"pri",
        "verb":"get"
        })
    json_array.append({
        "name":"Miner/Auth",
        "desc":"post Miner/Auth",
        "permission":"pri",
        "verb":"post"
        })
    json_array.append({
        "name":"Miner/Echo",
        "desc":"get Miner/Echo",
        "permission":"pri",
        "verb":"get"
        })
    json_array.append({
        "name":"Miner/Firmware",
        "desc":"get Miner/Firmware",
        "permission":"pri",
        "verb":"get"
        })
    json_array.append({
        "name":"Miner/Firmware/Compatibility/List",
        "desc":"get Miner/Firmware/Compatibility/List",
        "permission":"pri",
        "verb":"get"
        })
    
    json_array.append({
        "name":"DateTime",
        "desc":"get DateTime",
        "permission":"pri",
        "verb":"get"
        })
    json_array.append({
        "name":"Uuid",
        "desc":"get Uuid",
        "permission":"pri",
        "verb":"get"
        })
    json_array.append({
        "name":"Miner",
        "desc":"post Miner",
        "permission":"pri",
        "verb":"post"
        })
    json_array.append({
        "name":"processSomething",
        "desc":"post processSomething",
        "permission":"pri",
        "verb":"post"
        })    
    return json.dumps(json_array)

def handle_get(path, headers):
    if path == "/Echo":
        return Utils.resultJsonOK(), 200, 'application/json'
    
    elif path == "/favicon.ico":
        return None, 200, 'image/x-icon'
    
    elif path == "/DateTime":
        return {"result": Utils.nowUtc()}, 200, 'application/json'
    
    elif path == "/Miner":
        return Miner.dataAsJsonString(), 200, 'application/json'
    elif path == "/Miner/Echo":
        sHeader: str = headers.get('uuid')
        if sHeader is None or sHeader.strip() == '':
            sHeader = json.loads(headers.get('miner-json'))
        if sHeader is None:
            Utils.throwExceptionHttpMissingHeader('uuid or miner-json')
        return Miner.minerEcho(sHeader), 200, 'application/json'
    elif path == "/Miner/Firmware":
        sHeader: str = headers.get('uuid')
        if sHeader is None or sHeader.strip() == '':
            sHeader = json.loads(headers.get('miner-json'))
        if sHeader is None:
            Utils.throwExceptionHttpMissingHeader('uuid or miner-json')
        return Miner.minerFirmware(sHeader), 200, 'application/json'
    elif path == "/Miner/Firmware/Compatibility/List":
        enum_values = [firmware.value for firmware in Miner.CompatibleFirmware]
        return {"result": enum_values}, 200, 'application/json'
    elif path.startswith("/Miner/BraiinsS9"):
        sHeader: str = headers.get('uuid')
        if sHeader is None or sHeader.strip() == '':
            sHeader = json.loads(headers.get('miner-json'))
        if sHeader is None:
            Utils.throwExceptionHttpMissingHeader('uuid or miner-json')
        return Miner.httpHandlerBraiinsS9Get(path, headers, sHeader)
    elif path.startswith("/Miner/BraiinsV1"):
        sHeader: str = headers.get('uuid')
        if sHeader is None or sHeader.strip() == '':
            sHeader = json.loads(headers.get('miner-json'))
        if sHeader is None:
            Utils.throwExceptionHttpMissingHeader('uuid or miner-json')
        return Miner.httpHandlerBraiinsV1Get(path, headers, sHeader)
    elif path == "/Miner/Summary":
        sHeader: str = headers.get('uuid')
        if sHeader is None or sHeader.strip() == '':
            sHeader = json.loads(headers.get('miner-json'))
        if sHeader is None:
            Utils.throwExceptionHttpMissingHeader('uuid or miner-json')
        return Miner.minerSummary(sHeader), 200, 'application/json'
        
    
    elif path == "/RegisteredEndPoints":
        return registeredEndPoints(), 200, 'application/json'
    
    elif path == "/Uuid":
        return Utils.thermineUuid(), 200, 'application/json'
    
    else:
        return 'Not found', 400, 'text/html'

def handle_patch(path, headers, post_data):
    if path == "/processSomething":
        json_data = json.loads(post_data.decode('utf-8'))
        # As example, add a timestamp
        json_data["timestamp"] = int(time.time())
        return json_data, 200, 'application/json'
    
    elif path.startswith("/Miner/BraiinsS9"):
        sHeader: str = headers.get('uuid')
        if sHeader is None or sHeader.strip() == '':
            sHeader = json.loads(headers.get('miner-json'))
        if sHeader is None:
            Utils.throwExceptionHttpMissingHeader('uuid or miner-json')
        return Miner.httpHandlerBraiinsS9Patch(path, headers, sHeader)
    else:
        return 'Not found', 400, 'text/html' 

def handle_post(path, headers, post_data):
    if path == "/processSomething":
        json_data = json.loads(post_data.decode('utf-8'))
        # As example, add a timestamp
        json_data["timestamp"] = int(time.time())
        return json_data, 200, 'application/json'
    
    elif path == "/Miner":
        contentStr = post_data.decode('utf-8')
        Miner.setDataStr(contentStr);
        return Utils.resultJsonOK(), 200, 'application/json'
    elif path == "/Miner/Auth":
        json_data = json.loads(post_data.decode('utf-8'))
        Miner.minerAuth(json_data);
        return Utils.resultJsonOK(), 200, 'application/json'
    elif path.startswith("/Miner/BraiinsS9"):
        sHeader: str = headers.get('uuid')
        if sHeader is None or sHeader.strip() == '':
            sHeader = json.loads(headers.get('miner-json'))
        if sHeader is None:
            Utils.throwExceptionHttpMissingHeader('uuid or miner-json')
        contentStr = post_data.decode('utf-8')
        return Miner.httpHandlerBraiinsS9Post(path, headers, sHeader, contentStr)
    elif path.startswith("/Miner/BraiinsV1"):
        sHeader: str = headers.get('uuid')
        if sHeader is None or sHeader.strip() == '':
            sHeader = json.loads(headers.get('miner-json'))
        if sHeader is None:
            Utils.throwExceptionHttpMissingHeader('uuid or miner-json')
        contentStr = post_data.decode('utf-8')
        return Miner.httpHandlerBraiinsV1Post(path, headers, sHeader, contentStr)
    else:
        return 'Not found', 400, 'text/html' 