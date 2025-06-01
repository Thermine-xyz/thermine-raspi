from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Any, Callable, List, Type, TypeVar
from .log import Logger

from google.protobuf.json_format import MessageToDict
import grpc
import json
import os
import paramiko
import re
from readerwriterlock import rwlock
import threading
import time
import uuid

class Utils:
    
    T = TypeVar('T')
    
    logger : Logger = None
    lockFileConfigThermine = None
    filesLock = {} # Stores the locks for random files
    
    @classmethod
    def initialize(cls):
        # Lock the read and write for the file, 1 proccess per time
        cls.lockFileConfigThermine = Utils.threadingLock() # threading.Lock()
        cls.logger = Logger(log_path=Utils.pathData(), log_file="log.log", log_level=Logger.DEBUG).get_logger()

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

    @staticmethod
    def getFileLock(fileName):
        if fileName not in Utils.filesLock:
            Utils.filesLock[fileName] = rwlock.RWLockFair()
        return Utils.filesLock[fileName]

    # Creates a gRPC channel without channel-level authentication
    @staticmethod
    def grpcChannel(aip: str):
        return grpc.insecure_channel(aip)
    @staticmethod
    def grpcChannelSecure(aip: str, token: str):
        credentials = grpc.access_token_call_credentials(token)
        composite_creds = grpc.composite_channel_credentials(
            grpc.ssl_channel_credentials(),
            credentials
        )
        return grpc.secure_channel(aip, composite_creds)
        # no credentials grpc.secure_channel(SERVER_ADDRESS, grpc.ssl_channel_credentials())
        """ With extra HTTPS options
        lOptions = [
            ('grpc.ssl_target_name_override', '192.168.178.184'),
            ('grpc.default_authority', '192.168.178.184'),
            ('grpc.ssl_version', 'TLSv1_1')
            ] 
        credentials = grpc.access_token_call_credentials(token)
        composite_creds = grpc.composite_channel_credentials(
            grpc.ssl_channel_credentials(),
            credentials
            )
        return grpc.secure_channel(aip, composite_creds, options=lOptions)"""

    @staticmethod
    def grpcCall(stubClass: Type[Any], methodName: str, request: Any, token: str, aip: str) -> Any:
        if aip.lower().startswith('https'):
            channel = Utils.grpcChannelSecure(aip)
        else:
            channel = Utils.grpcChannel(aip)

        try:
            stub = stubClass(channel)
            method = getattr(stub, methodName)
            metadata = [('authorization', token)]
            response = method(request, metadata=metadata, timeout=10)
            return response
        finally:
            channel.close()
    # Converts a Protbuf msg to JSON Object
    @staticmethod
    def grpcProtobufToJson(response: Any) -> dict:
        return MessageToDict(response, preserving_proto_field_name=True)
    # Converts a Protbuf msg to JSON string
    @staticmethod
    def grpcProtobufToStr(response: Any) -> str:
        jObj = Utils.grpcProtobufToJson(response)
        return json.dumps(jObj, indent=2)

    @staticmethod
    def jsonCheckIsObj(jObj, isRaiseExcpt: bool = True):
        if not isinstance(jObj, dict):
            if isRaiseExcpt:
                Utils.throwExceptionInvalidValue(f"Value is not JSON Object: {jObj}")
            else:
                return False
        return True
    @staticmethod
    def jsonCheckIsAry(jObj, isCheckEmpty: bool = True, isRaiseExcpt: bool = True):
        if not isinstance(jObj, list):
            if isRaiseExcpt:
                Utils.throwExceptionInvalidValue(f"Value is not JSON Array: {jObj}")
            else:
                return False
        if isCheckEmpty and len(jObj) == 0:
            if isRaiseExcpt:
                Utils.throwExceptionInvalidValue(f"JSON Array is empty: {jObj}")
            else:
                return False
        return True
    
    # check if key exists
    @staticmethod
    def jsonCheckKeyExists(jObj: dict[str, str], key: str, isRaiseExcpt: bool):
        if key in jObj:
            return True
        elif isRaiseExcpt:
            Utils.throwExceptionResourceNotFound(f"JSON key not found: {key}, json {jObj}")
        else:
            return False
    
    # check if key exists and if it is string type
    @staticmethod
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

    @staticmethod
    def minerIpBraiinsV1(jObj) -> str:
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        ip = jObj['ip'].strip()  # Remove espaços em branco
        # Checks if current IP contains a port
        if ':' in ip:
            # Check if port is number only
            ip_parts = ip.split(':')
            if len(ip_parts) == 2 and ip_parts[1].isdigit():
                return ip
            else:
                raise ValueError(f"Invalid IP format with port: {ip}")
        else:
            # Adds the default port
            return f"{ip}:50051"

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
            os.makedirs(path, exist_ok=True)
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

    @staticmethod
    def pathDataMinerHashrate(jObj):
        """file format: utc timestamp;THs"""
        path = os.path.join(Utils.pathData(),f"hashrate_{jObj['uuid']}")
        return path
    @staticmethod
    def pathDataMinerTemp(jObj):
        """file format: utc timestamp;avg board temp;avg chip temp"""
        path = os.path.join(Utils.pathData(),f"temp_{jObj['uuid']}")
        return path
    @staticmethod
    def pathDataMinerTempSensor(jObj):
        """file format: utc timestamp;sensor temp"""
        path = os.path.join(Utils.pathData(),f"temp_sensor_{jObj['uuid']}")
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
    def sshExecCommand(ip: str, user: str, pwrd: str, cmd: str):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, port=22, username=user, password=pwrd, timeout=2)
        try:
           stdin, stdout, stderr = ssh.exec_command(cmd)
           exit_status = stdout.channel.recv_exit_status() # wait till process to finish
           output = stdout.read().decode('utf-8').strip()
           error = stderr.read().decode('utf-8').strip()
           if error != None and error.strip() != '':
               raise Exception(error)
           return output
        finally:
            if ssh.get_transport() is not None:
                ssh.get_transport().close()
            ssh.close;

    # Return a semaphor for locking access to variable or files
    @staticmethod
    def threadingLock():
        return threading.Lock()
    
    # Returns the thermine_config.uuid value (may be create a file for this stuff?)
    @staticmethod
    def thermineUuid():
        path = Utils.pathConfigThermine()
        with Utils.lockFileConfigThermine:
            with open(path, 'r', encoding='utf-8') as file:
                jObj = json.load(file)
        if jObj.get('uuid') is None or jObj.get('uuid').strip() == '':
            jObj['uuid'] = Utils.uuidRandom()
            with Utils.lockFileConfigThermine:
                with open(path, 'w', encoding='utf-8') as file:
                    json.dump(jObj, file, ensure_ascii=False, indent=2)
        jObjReturn = {"uuid":jObj['uuid']}
        return json.dumps(jObjReturn)
    
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
    
    class PubSub:
        # Expected JSON format: {"action":add,update,del,"data":JSON array or objet changed}
        TOPIC_DATA_HAS_CHANGED = 'DataHasChanged'
        
        def __init__(self):
            self.subscribers = {}  # Dictionary: topics -> callback list

        def subscribe(self, topic, callback):
            """Subscribe for a topic"""
            if topic not in self.subscribers:
                self.subscribers[topic] = []
            self.subscribers[topic].append(callback)

        def unsubscribe(self, topic, callback):
            """Remove the topic subscription"""
            if topic in self.subscribers:
                self.subscribers[topic].remove(callback)
                if not self.subscribers[topic]:
                    del self.subscribers[topic]

        def publish(self, topic, *args, **kwargs):
            """Publish a msg for all topic's subcriber"""
            if topic in self.subscribers:
                for callback in self.subscribers[topic]:
                    callback(*args, **kwargs)
    # Global PubSub instance
    pubsub_instance = PubSub()

# Explicit calls initialization
Utils.initialize()
    
class HttpException(Exception):
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)