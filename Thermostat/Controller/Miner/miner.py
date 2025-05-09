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
import mmap
import os
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
        }
    }

    * Current we are compatible only with DS1820 and Python library w1thermsensor
    ** JSON Object "sensor" is not mandatory
    """
    uuid: str
    name: str
    ip: str
    fwtp: str # Firmware Type = braiins,vnish  | Default or Empty=vnish

    @staticmethod
    def binaryReadingFile(fileName, dateFrom, dateTo):
        results = []
        with open(fileName, 'r', encoding='utf-8') as file:
            size = os.path.getsize(fileName)
            with mmap.mmap(file.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
                start = 0
                end = size

                # find the start of the line
                def findLineStart(pos):
                    while pos > 0 and mm[pos - 1:pos] != b'\n':
                        pos -= 1
                    return pos

                # Binary search to find first timestamp
                posStart = None
                while start < end:
                    mid = (start+end) // 2
                    lineStart = findLineStart(mid)
                    mm.seek(lineStart)
                    line = mm.readline().decode().strip()
                    if not line:
                        break
                    try:
                        timestamp = int(line.split(";")[0])
                    except ValueError:
                        break
                    if timestamp < dateFrom:
                        start = mm.tell()
                    else:
                        end = lineStart
                        posStart = lineStart
                if posStart is None:
                    return []  # Nenhum dado no intervalo

                # Lê linhas sequencialmente a partir da posição encontrada
                mm.seek(posStart)
                while True:
                    line = mm.readline()
                    if not line:
                        break
                    line = line.decode().strip()
                    if not line:
                        continue
                    try:
                        timestamp = int(line.split(";")[0])
                        if timestamp > dateTo:
                            break
                        if dateFrom <= timestamp <= dateTo:
                            results.append(line)
                    except ValueError:
                        continue
        return results

                    
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
        uuidLocal = uuid
        if isinstance(uuidLocal, str): # in case it is string, should be miner unique UUID
            if not Utils.uuidIsValid(uuidLocal):
                Utils.throwExceptionInvalidValue(f"Is not miner UUID: {uuid}")
        elif Utils.jsonCheckIsObj(uuid):
            Utils.jsonCheckKeyTypeStr(uuid, 'uuid', True, False)
            uuidLocal = uuid['uuid']
            
        # Loop the current miner list, finding the uuid
        jObj = next((jObj for jObj in Miner.dataAsJson() if jObj["uuid"] == uuidLocal), None)
        if jObj == None:
            Utils.throwExceptionResourceNotFound(f"Miner UUID {uuid}")
        return jObj

    # Returns the full JSON Array as string
    @staticmethod
    def dataAsJsonString():
        jAry = Miner.dataAsJson()
        return json.dumps(jAry)

    # Handles HTTP request for BraiinsS9
    @staticmethod
    def httpHandlerBraiinsS9Get(path, headers, s):
        jObj = Miner.dataAsJsonObjectUuid(s)
        if jObj == None: # didn't find the JSON object with same s=uuid
            if isinstance(s, dict): # JSON object
                jObj = s
            else:
                Utils.throwExceptionInvalidValue("Expect UUID string or JSON Object string")
        return MinerBraiinsS9.httpHandlerGet(path, headers, jObj)
    @staticmethod
    def httpHandlerBraiinsS9Patch(path, headers, s):
        jObj = Miner.dataAsJsonObjectUuid(s)
        if jObj == None: # didn't find the JSON object with same s=uuid
            if isinstance(s, dict): # JSON object
                jObj = s
            else:
                Utils.throwExceptionInvalidValue("Expect UUID string or JSON Object string")
        return MinerBraiinsS9.httpHandlerPatch(path, headers, jObj)
    @staticmethod
    def httpHandlerBraiinsS9Post(path, headers, s, contentStr):
        jObj = Miner.dataAsJsonObjectUuid(s)
        if jObj == None: # didn't find the JSON object with same s=uuid
            if isinstance(s, dict): # JSON object
                jObj = s
            else:
                Utils.throwExceptionInvalidValue("Expect UUID string or JSON Object string")
        return MinerBraiinsS9.httpHandlerPost(path, headers, jObj, contentStr)

    # Handles HTTP request for BraiinsV1
    @staticmethod
    def httpHandlerBraiinsV1Get(path, headers, s):
        jObj = Miner.dataAsJsonObjectUuid(s)
        if jObj == None: # didn't find the JSON object with same s=uuid
            if isinstance(s, dict): # JSON object
                jObj = s
            else:
                Utils.throwExceptionInvalidValue("Expect UUID string or JSON Object string")
        return MinerBraiinsV1.httpHandlerGet(path, headers, jObj)
    @staticmethod
    def httpHandlerBraiinsV1Post(path, headers, s, contentStr):
        jObj = Miner.dataAsJsonObjectUuid(s)
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
                Utils.logger.error(f"minerFirmware  {fwtp} error {e}")
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
    
    @staticmethod
    def minerSummary(s):
        jObj = Miner.dataAsJsonObjectUuid(s)
        # It is expected to have jObj with the miners data
        fwtp = Miner.CompatibleFirmware.get(jObj.get('fwtp'))
        if fwtp == Miner.CompatibleFirmware.braiinsV1:
            return MinerBraiinsV1.summary(jObj)
        elif fwtp == Miner.CompatibleFirmware.braiinsS9:
            return MinerBraiinsS9.summary(jObj)
        else:
            return MinerVnish.summary(jObj)

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
        """
        If update the whole array list, it will not publish data has changed action
        """
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
            action = "update"
            if not isFound: # add in case new UUID
                jAry.append(jData)
                action = "add"
            event = {"action":action,"data":jData}
            Utils.pubsub_instance.publish(Utils.PubSub.TOPIC_DATA_HAS_CHANGED, event)
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
    
    """
    MinerService
    """
    # Get data from miner and save it locally
    @staticmethod
    def minerServiceGetData(jObj):
        Utils.jsonCheckIsObj(jObj)
        fwtp = Miner.CompatibleFirmware.get(jObj.get('fwtp'))
        if fwtp == Miner.CompatibleFirmware.braiinsV1:
            MinerBraiinsV1.minerServiceGetData(jObj)
        elif fwtp == Miner.CompatibleFirmware.braiinsS9:
            MinerBraiinsS9.minerServiceGetData(jObj)
        else:
            Utils.throwExceptionInvalidValue(f"minerServiceGetData Unknown Firmware: {fwtp}")
        
        # Returns OK if no error was raised
        return Utils.resultJsonOK()
    
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
        if Utils.jsonCheckKeyExists(jObj, 'sensor', False):
            tsMiner, temp = MinerUtils.dataTemperatureSensorLast(jObj)
        else:
            tsMiner, tBoard, temp = MinerUtils.dataTemperatureLast(jObj)
        fwtp = Miner.CompatibleFirmware.get(jObj.get('fwtp'))
        if fwtp == Miner.CompatibleFirmware.braiinsV1:
            print(f"Miner.minerThermalControl MinerBraiinsV1")
            MinerBraiinsV1.minerThermalControl(jObj, temp)
        elif fwtp == Miner.CompatibleFirmware.braiinsS9:
            MinerBraiinsS9.minerThermalControl(jObj, temp)
        else:
            Utils.throwExceptionInvalidValue(f"minerThermalControl Unknown Firmware: {fwtp}")
    """
    MinerService END
    """