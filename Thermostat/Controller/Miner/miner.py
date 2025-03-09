from ..utils import Utils
from .miner_vnish import MinerVnish

from enum import Enum

import os
import threading
import json

class Miner:

    uuid: str
    name: str
    ip: str
    fwtp: str # Firmware Type = braiins,vnish  | Default or Empty=vnish

    # Lock the read and write for the file, 1 proccess per time
    lockFile = threading.Lock()

    def __init__(self, uuid, ip):
        self.uuid = uuid
        self.ip = ip

    # Tries to connect to miner based on the firmware type
    @staticmethod
    def auth(jObj):
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object");
        Utils.jsonCheckKeyTypeStr(jObj, 'uuid', True, False)
        # It is expected to have jObj with the miners data
        if jObj.get('fwtp') is None or jObj.get('fwtp').strip() == '':
            MinerVnish.getJwtToken(jObj)
        else:
            Utils.throwExceptionInvalidValue("We are not compatible with this Firmware yet")
        
        # Returns OK if no error was raised
        return Utils.resultJsonOK()
    
    # Returns the full JSON Array as string
    @staticmethod
    def dataAsJson():
        path = Miner.pathData()
        with Miner.lockFile:
            with open(path, 'r', encoding='utf-8') as file:
                jObj = json.load(file)
        if isinstance(jObj.get('data'), list):
            return jObj.get('data')
        else:
            return []

    # Returns the full JSON Array as string
    @staticmethod
    def dataAsJsonString():
        jAry = Miner.dataAsJson()
        return json.dumps(jAry)

    # Tries to connect to miner based on the firmware type
    @staticmethod
    def echo(s):
        if isinstance(s, str): # in case it is string, should be miner unique UUID
            if not Utils.uuidIsValid(s):
                Utils.throwExceptionInvalidValue(f"Is not miner UUID: {s}")
            # Loop the current miner list, finding the uuid
            jObj = next((jObj for jObj in Miner.dataAsJson() if jObj["uuid"] == s), None)
            if jObj == None:
                Utils.throwExceptionResourceNotFound(f"Miner UUID {s}")            
        elif isinstance(s, dict): # JSON object
            jObj = json.loads(s)
        
        # It is expected to have jObj with the miners data
        if jObj.get('fwtp') is None or jObj.get('fwtp').strip() == '':
            MinerVnish.echo(jObj)
        else:
            Utils.throwExceptionInvalidValue("We are not compatible with this Firmware yet")
        
        # Returns OK if no error was raised
        return Utils.resultJsonOK()

    @staticmethod
    def pathData():
        path = os.path.join(Utils.pathData(), 'miner.json')
        with Miner.lockFile:
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as file:
                    file.close()
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    jObj = json.load(file)
            except json.JSONDecodeError as e:
                jObj = []
            if not isinstance(jObj, dict):
                jObj = {"version":1}
                with open(path, 'w', encoding='utf-8') as file:
                    json.dump(jObj, file, ensure_ascii=False, indent=2)
        return path
    
    # Save the JSON value in the data array, if Obj, finds and save. If Array, override
    @staticmethod
    def setData(jData):
        if isinstance(jData, list):
            path = Miner.pathData()
            with Miner.lockFile:
                with open(path, 'r', encoding='utf-8') as file:
                    jObj = json.load(file)
                file.close()
                jObj["data"] = jData
                with open(path, 'w', encoding='utf-8') as file:
                    json.dump(jObj, file, ensure_ascii=False, indent=2)
        elif isinstance(jData, dict):
            jAry = Miner.dataAsJson()
            for index, jObj in enumerate(jAry):
                if jObj["uuid"] == jData["uuid"]:
                    jAry[index] = jData
                    Miner.setData(jAry)
                    break
        else:
            Utils.throwExceptionInvalidValue(json.dumps(jData));
            
    # Returns the full JSON Array as string
    @staticmethod
    def setDataStr(jStr: str):
        try:
            jData = json.loads(jStr)
        except Exception as e:
            Utils.throwExceptionInvalidValue(jStr);
        Miner.setData(jData)