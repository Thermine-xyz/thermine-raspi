from ..utils import Utils
from enum import Enum

import json
import mmap
import os

class MinerUtils:

    @staticmethod
    def binaryReadingFileStr(fileName: str, dateFrom: int, dateTo: int):
        result = []
        records = Utils.binaryReadingFile(fileName, dateFrom, dateTo)
        for record in records:
            if len(record) != 2:
                Utils.logger.warning(f"binaryReadingFileStr {path}: unexpected data {record}.")
                continue
            
            timestamp, values = record
            line = f"{timestamp}"
            for value in values:
                line = line + f";{value}"
            result.append(line)
        return result


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
        jObj = next((jObj for jObj in MinerUtils.dataAsJson() if jObj["uuid"] == uuidLocal), None)
        if jObj == None:
            Utils.throwExceptionResourceNotFound(f"Miner UUID {uuid}")
        return jObj

    # Returns the full JSON Array as string
    @staticmethod
    def dataAsJson():
        path = MinerUtils.pathData()
        lock = Utils.getFileLock(path).gen_rlock()
        with lock:
            with open(path, 'r', encoding='utf-8') as file:
                jObj = json.load(file)
        if isinstance(jObj.get('data'), list):
            return jObj.get('data')
        else:
            return []

    # Returns the full JSON Array as string
    @staticmethod
    def dataAsJsonString():
        jAry = MinerUtils.dataAsJson()
        return json.dumps(jAry)

    # Returns the last reading Temp, hashrate, etc
    @staticmethod
    def dataCurrentStatus(jObj):
        if not isinstance(jObj, dict):
            jObj = MinerUtils.dataAsJsonObjectUuid(jObj)
        result = {}
        result['hasrate'] = MinerUtils.dataHashrateLastJson(jObj)
        result['temp'] = MinerUtils.dataTemperatureLastJson(jObj)
        if Utils.jsonCheckKeyExists(jObj, 'sensor', False):
            result['temp_sensor'] = MinerUtils.dataTemperatureSensorLastJson(jObj)
        return result

    @staticmethod
    def dataHashrate(jObj, dateFrom, dateTo):
        result = []
        if not isinstance(jObj, dict):
            jObj = MinerUtils.dataAsJsonObjectUuid(jObj)
        path = Utils.pathDataMinerHashrate(jObj)
        lock = Utils.getFileLock(path).gen_rlock() # lock for reading, method "rlock"
        with lock:
            result = MinerUtils.binaryReadingFileStr(path, dateFrom, dateTo)
        return "\n".join(result)
    @staticmethod
    def dataHashrateLast(jObj):
        if not isinstance(jObj, dict):
            jObj = MinerUtils.dataAsJsonObjectUuid(jObj)
        tupleData = Utils.dataBinaryReadLastLine(Utils.pathDataMinerHashrate(jObj))
        if tupleData is None:
            return None
        else:
            timestamp, dataValues = tupleData
            return timestamp, dataValues[0]
    @staticmethod
    def dataHashrateLastJson(jObj):
        timestamp, hashrate = MinerUtils.dataHashrateLast(jObj)
        return { "timestamp" : timestamp, "hashrate" : hashrate}

    @staticmethod
    def dataTemperature(jObj, dateFrom, dateTo):
        result = []
        if not isinstance(jObj, dict):
            jObj = MinerUtils.dataAsJsonObjectUuid(jObj)
        path = Utils.pathDataMinerTemp(jObj)
        lock = Utils.getFileLock(path).gen_rlock() # lock for reading, method "rlock"
        with lock:
            result = MinerUtils.binaryReadingFileStr(path, dateFrom, dateTo)
        return "\n".join(result)
    @staticmethod
    def dataTemperatureLast(jObj):
        if not isinstance(jObj, dict):
            jObj = MinerUtils.dataAsJsonObjectUuid(jObj)
        tupleData = Utils.dataBinaryReadLastLine(Utils.pathDataMinerTemp(jObj))
        if tupleData is None:
            return None
        else:
            timestamp, dataValues = tupleData
            return timestamp, dataValues[0], dataValues[1]
    @staticmethod
    def dataTemperatureLastJson(jObj):
        timestamp, tBoard, tChip = MinerUtils.dataTemperatureLast(jObj)
        return { "timestamp" : timestamp, "tBoard" : tBoard, "tChip" : tChip}

    @staticmethod
    def dataTemperatureSensor(jObj, dateFrom, dateTo):
        result = []
        if not isinstance(jObj, dict):
            jObj = MinerUtils.dataAsJsonObjectUuid(jObj)
        path = Utils.pathDataMinerTempSensor(jObj)
        lock = Utils.getFileLock(path).gen_rlock() # lock for reading, method "rlock"
        with lock:
            result = MinerUtils.binaryReadingFileStr(path, dateFrom, dateTo)
        return "\n".join(result)
    @staticmethod
    def dataTemperatureSensorLast(jObj):
        if not isinstance(jObj, dict):
            jObj = MinerUtils.dataAsJsonObjectUuid(jObj)
        tupleData = Utils.dataBinaryReadLastLine(Utils.pathDataMinerTempSensor(jObj))
        if tupleData is None:
            return None
        else:
            timestamp, dataValues = tupleData
            return timestamp, dataValues[0]
    @staticmethod
    def dataTemperatureSensorLastJson(jObj):
        timestamp, temp = MinerUtils.dataTemperatureSensorLast(jObj)
        return { "timestamp" : timestamp, "temp" : temp}
    
    # Returns the miner.json full path, creates it if doesn't exists
    @staticmethod
    def pathData():
        path = os.path.join(Utils.pathData(), 'miner.json')
        if not os.path.exists(path):
            lock = Utils.getFileLock(path).gen_wlock()
            with lock:
                with open(path, 'w', encoding='utf-8') as file:
                    file.close()
        
        lock = Utils.getFileLock(path).gen_rlock()
        with lock:
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    jObj = json.load(file)
            except json.JSONDecodeError as e:
                jObj = None

        lock = Utils.getFileLock(path).gen_wlock()
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
            path = MinerUtils.pathData()
            lock = Utils.getFileLock(path).gen_rlock()
            with lock:
                with open(path, 'r', encoding='utf-8') as file:
                    jObj = json.load(file)
                file.close()
                jObj["data"] = jData
                with open(path, 'w', encoding='utf-8') as file:
                    json.dump(jObj, file, ensure_ascii=False, indent=2)
        elif isinstance(jData, dict):
            isFound = False
            jAry = MinerUtils.dataAsJson()
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
            MinerUtils.setData(jAry)
        else:
            Utils.throwExceptionInvalidValue(json.dumps(jData));
            
    # Returns the full JSON Array as string
    @staticmethod
    def setDataStr(jStr: str):
        try:
            jData = json.loads(jStr)
        except Exception as e:
            Utils.throwExceptionInvalidValue(jStr);
        MinerUtils.setData(jData)

    class CompatibleFirmware(Enum):
        braiinsV1 = 'braiinsV1'
        braiinsS9 = 'braiinsS9'
        luxor = 'luxor'
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

    class MinerStatus(Enum):
        MinerNormal = 'MINER_STATUS_NORMAL'
        MinerNotReady = 'MINER_STATUS_NOT_READY'
        MinerNotStarted = 'MINER_STATUS_NOT_STARTED'
        MinerUnknown = 'MINER_STATUS_UNKNOWN'

        
    """
    Base class for the miners
    """
    class MinerBase:
        # All methods must be overrided on inherited class
        @classmethod
        def echo(cls, jObj):
            Utils.throwExceptionResourceNotFound('Method not implemented MinerBase.echo')
        @classmethod
        def getToken(cls, jObj):
            Utils.throwExceptionResourceNotFound('Method not implemented MinerBase.getToken')
        @classmethod
        def minerServiceGetData(cls, jObj):
            Utils.throwExceptionResourceNotFound('Method not implemented MinerBase.minerServiceGetData')
        @classmethod
        def minerThermalControl(cls, jObj: dict, tCurrent: float):
            Utils.throwExceptionResourceNotFound('Method not implemented MinerBase.minerThermalControl')
        @classmethod
        def status(cls, jObj):
            Utils.throwExceptionResourceNotFound('Method not implemented MinerBase.status')

    @staticmethod
    def getMinerClass(firmware: str) -> MinerBase:
        from .miner_braiins_v1 import MinerBraiinsV1
        from .miner_braiins_s9 import MinerBraiinsS9
        from .miner_luxor import MinerLuxor
        from .miner_vnish import MinerVnish

        fwtp = MinerUtils.CompatibleFirmware.get(firmware)
        if fwtp == MinerUtils.CompatibleFirmware.braiinsV1:
            return MinerBraiinsV1
        elif fwtp == MinerUtils.CompatibleFirmware.braiinsS9:
            return MinerBraiinsS9
        elif fwtp == MinerUtils.CompatibleFirmware.luxor:
            return MinerLuxor
        elif fwtp == MinerUtils.CompatibleFirmware.vnish:
            return MinerVnish
        else:
            Utils.throwExceptionInvalidValue(f"MinerUtils.getMinerClass Unknown Firmware: {firmware}")
            