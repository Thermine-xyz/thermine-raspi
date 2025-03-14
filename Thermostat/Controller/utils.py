import json
import os
import time
import uuid
import threading
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Type, TypeVar

class Utils:
    
    T = TypeVar('T')
    
    # Lock the read and write for the file, 1 proccess per time
    lockFileConfigThermine = threading.Lock()

    # Returns a JSONArray from a List of dataclass
    @staticmethod
    def dataClassListToJson(objList: List[T]) -> str:
        objListDict= [asdict(obj) for obj in objList]
        return json.dumps(objListDict)
    
    # Returns dataclass list from a JSONArray
    @staticmethod
    def dataClassListToJson(jsonStr: str, dataClassType: Type[T]) -> List[T]:
        objListDict = json.loads(jsonStr)
        return [dataClassType(**objDict) for objDict in objListDict]
    
    # check if key exists
    def jsonCheckKeyExists(jObj: dict[str, str], key: str, isRaiseExcpt: bool):
        if key in jObj:
            return True
        elif isRaiseExcpt:
            Utils.throwExceptionResourceNotFound(f"JSON key not found: {key}")
        else:
            return False
    
    # check if key exists and if it is string type
    def jsonCheckKeyTypeStr(jObj: dict[str, str], key: str, isRaiseExcpt: bool, isAcceptEmpty: bool):
        if Utils.jsonCheckKeyExists(jObj, key, isRaiseExcpt):
            if isinstance(jObj[key], str):
                if isAcceptEmpty:
                    return True
                elif jObj.get(key).strip() == '':
                    if isRaiseExcpt:
                        Utils.throwExceptionInvalidValue(f"JSON key cant be empty: {key}")
                    else:
                        return False
                else:
                    return True
            elif isRaiseExcpt:
                Utils.throwExceptionInvalidValue(f"JSON key is not string: {key}")
            else:
                return False        
    
    # Returns the thermine_config.uuid value (may be create a file for this stuff?)
    @staticmethod
    def thermineUuid():
        path = Utils.pathConfigThermine()
        with Utils.lockFileConfigThermine:
            with open(path, 'r', encoding='utf-8') as file:
                jObj = json.load(file)
        if jObj.get('uuid') is None or jObj.get('uuid').strip() == '':
            jObj['uuid'] = uuidRandom()
            with Utils.lockFileConfigThermine:
                with open(path, 'w', encoding='utf-8') as file:
                    json.dump(jObj, file, ensure_ascii=False, indent=2)
        jObjReturn = {"uuid":jObj['uuid']}
        return json.dumps(jObjReturn)

    # Returns current date time in timestamp UTC
    @staticmethod
    def nowUtc():
        current_time = time.time()
        return int(current_time)

    # Returns the user/Documents/heater_control path
    @staticmethod
    def pathDocuments():
        path = os.path.join(Path.home(),'Documents')
        path = os.path.join(path,'heater_control')
        if not os.path.exists(path):
            Utils.throwExceptionResourceNotFound('user Documents path [' + path + ']')
        return path

    # Returns the config path, creates if doesn't exist
    @staticmethod
    def pathConfig():
        path = os.path.join(Utils.pathDocuments(),'config')
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    # Returns the data path, creates if doesn't exist
    @staticmethod
    def pathData():
        path = os.path.join(Utils.pathDocuments(),'data')
        if not os.path.exists(path):
            os.makedirs(path)
        return path


    # Returns the thermine_config.json path, creates if doesn't exist
    @staticmethod
    def pathConfigThermine():
        path = os.path.join(Utils.pathConfig(), 'thermine_config.json')
        if not os.path.exists(path):
            jObj = {"version":1}
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(jObj, file, ensure_ascii=False, indent=2)
        return path

    # Returns the current .py path is running from
    @staticmethod
    def pathCurrent():
        return os.path.join(os.getcwd(), 'heater_control')

    @staticmethod
    def resultJsonOK():
        return {"result": "OK"}

    @staticmethod
    def throwExceptionHttpMissingHeader(msg):
        raise HttpException(f"Missing header: {msg}", 400)
    
    @staticmethod
    def throwExceptionInvalidValue(msg):
        raise Exception('Invalid value: ' + msg)
    
    @staticmethod
    def throwExceptionResourceNotFound(msg):
        raise Exception('Resource not found: ' + msg)
    
    # Returns if the string is a valid UUID format
    @staticmethod
    def uuidIsValid(s):
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", 
            re.IGNORECASE
        )
        return bool(uuid_pattern.match(s)) 
    
    # Returns a random UUID
    @staticmethod
    def uuidRandom():
        return str(uuid.uuid4())
    
class HttpException(Exception):
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)