"""
Generic methods to manage miners
Some methods are managing local data, some are connecting to the miner
For methods connecting and managing the miner it self, the method's name starts with miner
"""
from ..utils import Utils
from .miner_utils import MinerUtils
from .miner_braiins_s9 import MinerBraiinsS9
from .miner_braiins_v1 import MinerBraiinsV1
from .miner_vnish import MinerVnish

from enum import Enum
import json
import threading

class Miner:
    """
    Current JSON format we expect for miner
    Last update 2025-05-06
    {
        "uuid": "",
        "ip": "",
        "name": "",
        "username": "",
        "password": "",
        "fwtp": "",
        "do_thermal_control": bool # allow Raspi to control theminer temp, turning it on and off
        "sensor": {
            "temp_target": int # temp in celsius
        },
        # The field below are only for memory control
        "runControl": {
            "thermal_last_cmd": ""
        }        
    }

    * Current we are compatible only with DS1820 and Python library w1thermsensor
    ** JSON Object "sensor" is not mandatory
    """
    uuid: str
    name: str
    ip: str
    fwtp: str # Firmware Type = braiins,vnish  | Default or Empty=vnish

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

    # Handles HTTP request for BraiinsS9
    @staticmethod
    def httpHandlerBraiinsS9Get(path, headers, s):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
        if jObj == None: # didn't find the JSON object with same s=uuid
            if isinstance(s, dict): # JSON object
                jObj = s
            else:
                Utils.throwExceptionInvalidValue("Expect UUID string or JSON Object string")
        return MinerBraiinsS9.httpHandlerGet(path, headers, jObj)
    @staticmethod
    def httpHandlerBraiinsS9Patch(path, headers, s):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
        if jObj == None: # didn't find the JSON object with same s=uuid
            if isinstance(s, dict): # JSON object
                jObj = s
            else:
                Utils.throwExceptionInvalidValue("Expect UUID string or JSON Object string")
        return MinerBraiinsS9.httpHandlerPatch(path, headers, jObj)
    @staticmethod
    def httpHandlerBraiinsS9Post(path, headers, s, contentStr):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
        if jObj == None: # didn't find the JSON object with same s=uuid
            if isinstance(s, dict): # JSON object
                jObj = s
            else:
                Utils.throwExceptionInvalidValue("Expect UUID string or JSON Object string")
        return MinerBraiinsS9.httpHandlerPost(path, headers, jObj, contentStr)

    # Handles HTTP request for BraiinsV1
    @staticmethod
    def httpHandlerBraiinsV1Get(path, headers, s):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
        if jObj == None: # didn't find the JSON object with same s=uuid
            if isinstance(s, dict): # JSON object
                jObj = s
            else:
                Utils.throwExceptionInvalidValue("Expect UUID string or JSON Object string")
        return MinerBraiinsV1.httpHandlerGet(path, headers, jObj)
    @staticmethod
    def httpHandlerBraiinsV1Post(path, headers, s, contentStr):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
        if jObj == None: # didn't find the JSON object with same s=uuid
            if isinstance(s, dict): # JSON object
                jObj = s
            else:
                Utils.throwExceptionInvalidValue("Expect UUID string or JSON Object string")
        return MinerBraiinsV1.httpHandlerPost(path, headers, jObj, contentStr)

    # Tries to connect to miner based on the firmware type
    @staticmethod
    def minerAuth(jObj):
        Utils.jsonCheckIsObj(jObj)
        #Utils.jsonCheckKeyTypeStr(jObj, 'uuid', True, False)
        # It is expected to have jObj with the miners data
        fwtp = Miner.CompatibleFirmware.get(jObj.get('fwtp'))
        if fwtp == Miner.CompatibleFirmware.braiinsV1:
            MinerBraiinsV1.getJwtToken(jObj)
        elif fwtp == Miner.CompatibleFirmware.braiinsS9:
            MinerBraiinsS9.sshConfig(jObj)
        else:
            MinerVnish.getJwtToken(jObj)
        
        # Returns OK if no error was raised
        return Utils.resultJsonOK()

    # Finds the miner firmware looping all compatible integrations till it can Echo
    @staticmethod
    def minerFirmware(s):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
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
                Utils.logger.error(f"minerFirmware  {fwtp} error {e}")
                pass # Do nothing, keep looping
        if result == False:
          Utils.throwExceptionResourceNotFound(f"Firmware for: {sOrigianl}")

    # Tries to 'ping' the miner based on the firmware type
    @staticmethod
    def minerEcho(s):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
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
    
    @staticmethod
    def minerSummary(s):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
        # It is expected to have jObj with the miners data
        fwtp = Miner.CompatibleFirmware.get(jObj.get('fwtp'))
        if fwtp == Miner.CompatibleFirmware.braiinsV1:
            return MinerBraiinsV1.summary(jObj)
        elif fwtp == Miner.CompatibleFirmware.braiinsS9:
            return MinerBraiinsS9.summary(jObj)
        else:
            return MinerVnish.summary(jObj)
    
    """
    MinerService
    """
    # Get data from miner and save it locally
    @staticmethod
    def minerServiceGetData(jObj):
        print("minerServiceGetData1")
        Utils.jsonCheckIsObj(jObj)
        fwtp = Miner.CompatibleFirmware.get(jObj.get('fwtp'))
        if fwtp == Miner.CompatibleFirmware.braiinsV1:
            MinerBraiinsV1.minerServiceGetData(jObj)
        elif fwtp == Miner.CompatibleFirmware.braiinsS9:
            MinerBraiinsS9.minerServiceGetData(jObj)
        else:
            Utils.throwExceptionInvalidValue(f"minerServiceGetData Unknown Firmware: {fwtp}")
        print("minerServiceGetData2")
        # Returns OK if no error was raised
        return None
    
    @staticmethod
    def minerThermalControl(jObj):
        print("minerThermalControl1")
        Utils.jsonCheckIsObj(jObj)
        if (
            not Utils.jsonCheckKeyExists(jObj, 'do_thermal_control', False) or
            not isinstance(jObj['do_thermal_control'], bool) or
            jObj['do_thermal_control'] == False
        ): # do nothing it is not configured to do thermal control
            return
        tsNow = Utils.nowUtc()
        # Reads from sensor or from miner
        if Utils.jsonCheckKeyExists(jObj, 'sensor', False):
            tsMiner, temp = MinerUtils.dataTemperatureSensorLast(jObj)
        else:
            tsMiner, tBoard, temp = MinerUtils.dataTemperatureLast(jObj)
        fwtp = Miner.CompatibleFirmware.get(jObj.get('fwtp'))
        if fwtp == Miner.CompatibleFirmware.braiinsV1:
            MinerBraiinsV1.minerThermalControl(jObj, temp)
        elif fwtp == Miner.CompatibleFirmware.braiinsS9:
            MinerBraiinsS9.minerThermalControl(jObj, temp)
        else:
            Utils.throwExceptionInvalidValue(f"minerThermalControl Unknown Firmware: {fwtp}")
        print("minerThermalControl2")
        return None
    """
    MinerService END
    """