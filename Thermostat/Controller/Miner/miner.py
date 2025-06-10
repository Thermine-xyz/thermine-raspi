"""
Generic methods to manage miners
Some methods are managing local data, some are connecting to the miner
For methods connecting and managing the miner it self, the method's name starts with miner
"""
from ..utils import Utils
from .miner_utils import MinerUtils
from .miner_braiins_s9 import MinerBraiinsS9
from .miner_braiins_v1 import MinerBraiinsV1
from .miner_luxor import MinerLuxor
from .miner_vnish import MinerVnish
from ..w1thermsensor_utils import W1ThermSensorUtils

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
        return MinerBraiinsS9.httpHandlerPatch(path, headers, jObj)
    @staticmethod
    def httpHandlerBraiinsS9Post(path, headers, s, contentStr):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
        return MinerBraiinsS9.httpHandlerPost(path, headers, jObj, contentStr)

    # Handles HTTP request for BraiinsV1
    @staticmethod
    def httpHandlerBraiinsV1Get(path, headers, s):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
        return MinerBraiinsV1.httpHandlerGet(path, headers, jObj)
    @staticmethod
    def httpHandlerBraiinsV1Post(path, headers, s, contentStr):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
        return MinerBraiinsV1.httpHandlerPost(path, headers, jObj, contentStr)

    # Tries to connect to miner based on the firmware type
    @staticmethod
    def minerAuth(jObj):
        Utils.jsonCheckIsObj(jObj)
        #Utils.jsonCheckKeyTypeStr(jObj, 'uuid', True, False)
        # It is expected to have jObj with the miners data
        minerCls = MinerUtils.getMinerClass(jObj['fwtp'])
        minerCls.getToken(jObj)        
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
        for fwtp in MinerUtils.CompatibleFirmware:
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
        minerCls = MinerUtils.getMinerClass(jObj['fwtp'])
        minerCls.echo(jObj)
        # Returns OK if no error was raised
        return Utils.resultJsonOK()
    
    @staticmethod
    def minerPause(s):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
        minerCls = MinerUtils.getMinerClass(jObj['fwtp'])
        result = minerCls.pause(jObj)
        if result is None:
            return Utils.resultJsonOK()
        else:
            return result
    @staticmethod
    def minerReboot(s):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
        minerCls = MinerUtils.getMinerClass(jObj['fwtp'])
        result = minerCls.reboot(jObj)
        if result is None:
            return Utils.resultJsonOK()
        else:
            return result
    
    @staticmethod
    def minerResume(s):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
        minerCls = MinerUtils.getMinerClass(jObj['fwtp'])
        result = minerCls.resume(jObj)
        if result is None:
            return Utils.resultJsonOK()
        else:
            return result
    
    @staticmethod
    def minerSummary(s):
        jObj = MinerUtils.dataAsJsonObjectUuid(s)
        # It is expected to have jObj with the miners data
        fwtp = MinerUtils.CompatibleFirmware.get(jObj.get('fwtp'))
        if fwtp == MinerUtils.CompatibleFirmware.braiinsV1:
            return MinerBraiinsV1.summary(jObj)
        elif fwtp == MinerUtils.CompatibleFirmware.braiinsS9:
            return MinerBraiinsS9.summary(jObj)
        elif fwtp == MinerUtils.CompatibleFirmware.luxor:
            return MinerLuxor.cgmConfig(jObj)
        else:
            return MinerVnish.summary(jObj)
    
    """
    MinerService
    """
    # Get data from miner and save it locally
    @staticmethod
    def minerServiceGetData(jObj):
        Utils.jsonCheckIsObj(jObj)
        try: # Hashrate(MHs)
            minerCls = MinerUtils.getMinerClass(jObj['fwtp'])
            minerCls.minerServiceGetData(jObj)
        except Exception as e:
            Utils.logger.error(f"minerServiceGetData {jObj['uuid']} error {e}")

        # Sensor temp
        if Utils.jsonCheckKeyExists(jObj, 'sensor', False) and W1ThermSensorUtils.isW1SensorPresent():
            """w1thermsensor"""
            try: # Reads sensor temp if it found the sensor JSON obj
                W1ThermSensorUtils.saveTempToDataFile(jObj)
            except Exception as e:
                Utils.logger.error(f"minerServiceGetData Sensor temp {jObj['uuid']} error {e}")
                pass
        return None
    
    @staticmethod
    def minerThermalControl(jObj):
        Utils.jsonCheckIsObj(jObj)
        if (
            not Utils.jsonCheckKeyExists(jObj, 'do_thermal_control', False) or
            not isinstance(jObj['do_thermal_control'], bool) or
            jObj['do_thermal_control'] == False
        ): # do nothing it is not configured to do thermal control
            return

        tsNow = Utils.nowUtc()
        # Reads from sensor or from miner
        if Utils.jsonCheckKeyExists(jObj, 'sensor', False) and W1ThermSensorUtils.isW1SensorPresent():
            tsMiner, temp = MinerUtils.dataTemperatureSensorLast(jObj)
        else:
            tsMiner, tBoard, temp = MinerUtils.dataTemperatureLast(jObj)
        minerCls = MinerUtils.getMinerClass(jObj['fwtp'])
        minerCls.minerThermalControl(jObj, temp)
        return None
    """
    MinerService END
    """