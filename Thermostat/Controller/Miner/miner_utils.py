from ..utils import Utils
from enum import Enum

class MinerUtils:
    # Returns the last reading Temp, hashrate, etc
    @staticmethod
    def dataCurrentStatus(jObj):
        result = {}
        result['hasrate'] = MinerUtils.dataHashrateLastJson(jObj)
        result['temp'] = MinerUtils.dataTemperatureLastJson(jObj)
        if Utils.jsonCheckKeyExists(jObj, 'sensor', False):
            result['temp_sensor'] = MinerUtils.dataTemperatureSensorLast(jObj)
        return result

    @staticmethod
    def dataHashrate(jObj, dateFrom, dateTo):
        result = []
        if not isinstance(jObj, dict):
            jObj = MinerUtils.dataAsJsonObjectUuid(jObj)
        path = Utils.pathDataMinerHashrate(jObj)
        lock = Utils.getFileLock(path).gen_rlock() # lock for reading, method "rlock"
        with lock:
            result = MinerUtils.binaryReadingFile(path, dateFrom, dateTo)
        return "\n".join(result)
    @staticmethod
    def dataHashrateLast(jObj):
        if not isinstance(jObj, dict):
            jObj = MinerUtils.dataAsJsonObjectUuid(jObj)
        path = Utils.pathDataMinerHashrate(jObj)
        lock = Utils.getFileLock(path).gen_rlock() # lock for reading, method "rlock"
        with lock:
            with open(path, 'r', encoding='utf-8') as file:
                # find the list line
                lineLast = file.readlines()[-1]
                timestamp, hashrate = lineLast.strip().split(';')

                timestamp = int(timestamp)
                hashrate = float(hashrate)                
                return timestamp, hashrate
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
            result = MinerUtils.binaryReadingFile(path, dateFrom, dateTo)
        return "\n".join(result)
    @staticmethod
    def dataTemperatureLast(jObj):
        if not isinstance(jObj, dict):
            jObj = MinerUtils.dataAsJsonObjectUuid(jObj)
        path = Utils.pathDataMinerTemp(jObj)
        lock = Utils.getFileLock(path).gen_rlock() # lock for reading, method "rlock"
        with lock:
            with open(path, 'r', encoding='utf-8') as file:
                # find the list line
                lineLast = file.readlines()[-1]
                timestamp, tBoard, tChip = lineLast.strip().split(';')

                timestamp = int(timestamp)
                tBoard = float(tBoard)
                tChip = float(tChip)                
                return timestamp, tBoard, tChip
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
            result = MinerUtils.binaryReadingFile(path, dateFrom, dateTo)
        return "\n".join(result)
    @staticmethod
    def dataTemperatureSensorLast(jObj):
        if not isinstance(jObj, dict):
            jObj = MinerUtils.dataAsJsonObjectUuid(jObj)
        path = Utils.pathDataMinerTempSensor(jObj)
        lock = Utils.getFileLock(path).gen_rlock() # lock for reading, method "rlock"
        with lock:
            with open(path, 'r', encoding='utf-8') as file:
                # find the list line
                lineLast = file.readlines()[-1]
                timestamp, temp = lineLast.strip().split(';')

                timestamp = int(timestamp)
                temp = float(temp)
                return timestamp, temp
    class MinerStatus(Enum):
        MinerNormal = 'MINER_STATUS_NORMAL'
        MinerNotReady = 'MINER_STATUS_NOT_READY'
        MinerNotStarted = 'MINER_STATUS_NOT_STARTED'
        MinerUnknown = 'MINER_STATUS_UNKNOWN'