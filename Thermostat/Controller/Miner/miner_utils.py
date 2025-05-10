from ..utils import Utils
from enum import Enum
import json
import mmap
import os

class MinerUtils:

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
            timestamp, temp = MinerUtils.dataTemperatureSensorLast(jObj)
            result['temp_sensor'] = {"timestamp" : timestamp, "temp" : temp}
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
            print(f"dataHashrateLast {jObj}")
            jObj = MinerUtils.dataAsJsonObjectUuid(jObj)
            print(f"dataHashrateLast {jObj}")
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

    class MinerStatus(Enum):
        MinerNormal = 'MINER_STATUS_NORMAL'
        MinerNotReady = 'MINER_STATUS_NOT_READY'
        MinerNotStarted = 'MINER_STATUS_NOT_STARTED'
        MinerUnknown = 'MINER_STATUS_UNKNOWN'