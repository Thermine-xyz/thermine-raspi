from ..utils import Utils

import os
import threading
import json

class Miner:
    
    # Lock the read and write for the file, 1 proccess per time
    lockFile = threading.Lock()
    
    def __init__(self, uuid, ip):
        self.uuid = uuid
        self.ip = ip
    
    # Returns the path of the thermine_miner.json file, format {"version":INT,"data":[]}
    @staticmethod
    def pathData():
        path = os.path.join(Utils.pathData(), 'thermine_miner.json')
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
    
    # Save the JSON value in the data array
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
        
    # Returns the full JSON Array as string
    @staticmethod
    def dataAsJsonString():
        jAry = Miner.dataAsJson()
        return json.dumps(jAry)