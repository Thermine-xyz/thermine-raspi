"""
Generic methods to manage miners
Some methods are managing local data, some are connecting to the miner
For methods connecting and managing the miner it self, the method's name starts with miner
"""
from ..utils import Utils
from .miner_braiins_s9 import MinerBraiinsS9
from .miner_braiins_v1 import MinerBraiinsV1
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
    class CompatibleFirmware(Enum):
        braiinsV1 = 'braiinsV1'
        braiinsS9 = 'braiinsS9'
        vnish = 'vnish'
        # Returns the enum based on the param as name (string) of index (int), default=vnish
        @classmethod
        def get(cls, param):
            try:
                if param == None:
                    return cls.vnish
                elif isinstance(param, str):
                    if param.strip() == '':
                        return cls.vnish
                    else:
                        return cls[param]
                elif isinstance(param, int):
                    return list(cls)[param]
            except:
                Utils.throwExceptionInvalidValue(f"We are not compatible with this Firmware yet: {param}")

    def __init__(self, uuid, ip):
        self.uuid = uuid
        self.ip = ip
    
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

    # Returns the miner JSON Object with same UUID
    @staticmethod
    def dataAsJsonObjectUuid(uuid):
        if isinstance(uuid, str): # in case it is string, should be miner unique UUID
            if not Utils.uuidIsValid(uuid):
                Utils.throwExceptionInvalidValue(f"Is not miner UUID: {uuid}")
            # Loop the current miner list, finding the uuid
            jObj = next((jObj for jObj in Miner.dataAsJson() if jObj["uuid"] == uuid), None)
            if jObj == None:
                Utils.throwExceptionResourceNotFound(f"Miner UUID {uuid}")
            return jObj
        return None

    # Returns the full JSON Array as string
    @staticmethod
    def dataAsJsonString():
        jAry = Miner.dataAsJson()
        return json.dumps(jAry)

    # Handles HTTP request for S9
    @staticmethod
    def httpHandlerS9Get(path, headers, s):
        jObj = Miner.dataAsJsonObjectUuid(s)
        if jObj == None: # didn't find the JSON object with same s=uuid
            if isinstance(s, dict): # JSON object
                jObj = s
            else:
                Utils.throwExceptionInvalidValue("Expect UUID string or JSON Object string")
        return MinerBraiinsS9.httpHandlerGet(path, headers, jObj)
    @staticmethod
    def httpHandlerS9Patch(path, headers, s):
        jObj = Miner.dataAsJsonObjectUuid(s)
        if jObj == None: # didn't find the JSON object with same s=uuid
            if isinstance(s, dict): # JSON object
                jObj = s
            else:
                Utils.throwExceptionInvalidValue("Expect UUID string or JSON Object string")
        return MinerBraiinsS9.httpHandlerPatch(path, headers, jObj)
    @staticmethod
    def httpHandlerS9Post(path, headers, s, contentStr):
        jObj = Miner.dataAsJsonObjectUuid(s)
        if jObj == None: # didn't find the JSON object with same s=uuid
            if isinstance(s, dict): # JSON object
                jObj = s
            else:
                Utils.throwExceptionInvalidValue("Expect UUID string or JSON Object string")
        return MinerBraiinsS9.httpHandlerPost(path, headers, jObj, contentStr)
    
    # Tries to connect to miner based on the firmware type
    @staticmethod
    def minerAuth(jObj):
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object");
        Utils.jsonCheckKeyTypeStr(jObj, 'uuid', True, False)
        # It is expected to have jObj with the miners data
        fwtp = Miner.CompatibleFirmware.get(jObj.get('fwtp'))
        if fwtp == Miner.CompatibleFirmware.braiinsV1:
            MinerBraiinsV1.getJwtToken(jObj)
        else:
            MinerVnish.getJwtToken(jObj)
        
        # Returns OK if no error was raised
        return Utils.resultJsonOK()

    # Finds the miner firmware looping all compatible integrations till it can Echo
    @staticmethod
    def minerFirmware(s):
        jObj = Miner.dataAsJsonObjectUuid(s)
        if jObj == None: # didn't find the JSON object with same s=uuid
            if isinstance(s, dict): # JSON object
                jObj = s
            else:
                Utils.throwExceptionInvalidValue("Expect UUID string or JSON Object string")

        sOrigianl = json.dumps(jObj)
        # Loops the compatible firwares and check the Echo for each one
        result = False
        for fwtp in Miner.CompatibleFirmware:
            try:
                jObj['fwtp'] = fwtp.value
                Miner.minerEcho(jObj)
                result = True
                return { "result": jObj['fwtp']}
                break
            except Exception as e:
                print(f"minerFirmware {fwtp} error {e}")
                pass # Do nothing, keep looping
        if result == False:
          Utils.throwExceptionResourceNotFound(f"Firmware for: {sOrigianl}")

    # Tries to 'ping' the miner based on the firmware type
    @staticmethod
    def minerEcho(s):
        jObj = Miner.dataAsJsonObjectUuid(s)
        if jObj == None: # didn't find the JSON object with same s=uuid
            if isinstance(s, dict): # JSON object
                jObj = s
            else:
                Utils.throwExceptionInvalidValue("Expect UUID string or JSON Object string")

        # It is expected to have jObj with the miners data
        fwtp = Miner.CompatibleFirmware.get(jObj.get('fwtp'))
        if fwtp == Miner.CompatibleFirmware.braiinsV1:
            MinerBraiinsV1.echo(jObj)
        elif fwtp == Miner.CompatibleFirmware.braiinsS9:
            MinerBraiinsS9.echo(jObj)
        else:
            MinerVnish.echo(jObj)

        # Returns OK if no error was raised
        return Utils.resultJsonOK()

    # Returns the miner.json full path, creates it if doesn't exists
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
            isFound = False
            jAry = Miner.dataAsJson()
            for index, jObj in enumerate(jAry):
                if jObj["uuid"] == jData["uuid"]:
                    jAry[index] = jData
                    isFound = True
                    break

            if not isFound: # add in case new UUID
                jAry.append(jData)
            Miner.setData(jAry)
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