from Controller import Utils
from ..Miner import Miner
from Controller.Miner import MinerUtils

import json
import time

def checkHeaderDateFrom(headers) -> int:
    try:
        header = int(headers.get('date-from'))
        if header is None or header <= 0:
            Utils.throwExceptionHttpMissingHeader(f"date-from {header}")
        return header
    except (IndexError, ValueError):
        Utils.throwExceptionInvalidValue("Header [date-from] is not integer")
def checkHeaderDateTo(headers) -> int:
    try:
        header = int(headers.get('date-to'))
        if header is None or header <= 0:
            Utils.throwExceptionHttpMissingHeader(f"date-to {header}")
        return header
    except (IndexError, ValueError):
        Utils.throwExceptionInvalidValue("Header [date-to] is not integer")
def checkHeaderUuid(headers, raiseException=False) -> str:
    header: str = headers.get('uuid')
    if (header is None or header.strip() == '') and raiseException:
        Utils.throwExceptionHttpMissingHeader('uuid')
    return header
def checkHeaderMinerJson(headers, raiseException=False) -> str:
    header: str = headers.get('miner-json')
    if (header is None or header.strip() == '') and raiseException:
        Utils.throwExceptionHttpMissingHeader('miner-json')
    return header

def handle_del(path, headers):
    if path == "/Miner":
        contentStr = post_data.decode('utf-8')
        Miner.setDataStr(contentStr);
        return Utils.resultJsonOK(), 200, 'application/json'

def handle_get(path, headers):
    if path == "/Echo":
        return Utils.resultJsonOK(), 200, 'application/json'
    
    elif path == "/favicon.ico":
        return None, 200, 'image/x-icon'
    
    elif path == "/DateTime":
        return {"result": Utils.nowUtc()}, 200, 'application/json'
    
    elif path == "/Miner":
        return MinerUtils.dataAsJsonString(), 200, 'application/json'
    elif path == "/Miner/Config":
        sHeader = checkHeaderUuid(headers)
        if sHeader is None or sHeader.strip() == '':
            sHeader = json.loads(checkHeaderMinerJson(headers, raiseException=True))
        return Miner.minerSummary(sHeader), 200, 'application/json'
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
        enum_values = [firmware.value for firmware in MinerUtils.CompatibleFirmware]
        return {"result": enum_values}, 200, 'application/json'
    elif path == "/Miner/Hashrate":
        sHeader = checkHeaderUuid(headers, raiseException=True)
        dateFrom = checkHeaderDateFrom(headers)
        dateTo = checkHeaderDateTo(headers) 
        return MinerUtils.dataHashrate(sHeader, dateFrom, dateTo), 200, 'text/plain'
    elif path == "/Miner/Hashrate/Last":
        sHeader = checkHeaderUuid(headers, raiseException=True)
        return MinerUtils.dataHashrateLastJson(sHeader), 200, 'application/jsonn'
    elif path == "/Miner/Status":
        sHeader = checkHeaderUuid(headers, raiseException=True)
        return MinerUtils.dataCurrentStatus(sHeader), 200, 'application/json'
    elif path == "/Miner/Temperature":
        sHeader = checkHeaderUuid(headers, raiseException=True)
        dateFrom = checkHeaderDateFrom(headers)
        dateTo = checkHeaderDateTo(headers) 
        return MinerUtils.dataTemperature(sHeader, dateFrom, dateTo), 200, 'text/plain'
    elif path == "/Miner/Temperature/Last":
        sHeader = checkHeaderUuid(headers, raiseException=True)
        return MinerUtils.dataTemperatureLastJson(sHeader), 200, 'application/json'
    elif path == "/Miner/Temperature/Sensor":
        sHeader = checkHeaderUuid(headers, raiseException=True)
        dateFrom = checkHeaderDateFrom(headers)
        dateTo = checkHeaderDateTo(headers) 
        return MinerUtils.dataTemperatureSensor(sHeader, dateFrom, dateTo), 200, 'text/plain'
    elif path == "/Miner/Temperature/Sensor/Last":
        sHeader = checkHeaderUuid(headers, raiseException=True)
        return MinerUtils.dataTemperatureSensorLastJson(sHeader), 200, 'application/json'

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
        MinerUtils.setDataStr(contentStr);
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
    elif path == "/Miner/Pause":
        sHeader = checkHeaderUuid(headers, raiseException=True)
        return Miner.minerPause(sHeader), 200, 'application/json'
    elif path == "/Miner/Reboot":
        sHeader = checkHeaderUuid(headers, raiseException=True)
        return Miner.minerReboot(sHeader), 200, 'application/json'
    elif path == "/Miner/Resume":
        sHeader = checkHeaderUuid(headers, raiseException=True)
        return Miner.minerResume(sHeader), 200, 'application/json'
    else:
        return 'Not found', 400, 'text/html' 