from ..utils import Utils
from .miner_braiins_v1_proto import MinerBraiinsV1Proto
from .Braiins import actions_pb2
from .Braiins import actions_pb2_grpc
from .Braiins import authentication_pb2
from .Braiins import authentication_pb2_grpc
from .Braiins import configuration_pb2
from .Braiins import configuration_pb2_grpc
from .Braiins import cooling_pb2
from .Braiins import cooling_pb2_grpc
from .Braiins import miner_pb2
from .Braiins import miner_pb2_grpc
from .Braiins import version_pb2
from .Braiins import version_pb2_grpc

import grpc
import json

class MinerBraiinsV1:


    # Check if the miner is online
    @staticmethod
    def echo(jObj):
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object")
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        channel = Utils.grpcChannel(MinerBraiinsV1.minerIp(jObj))
        try:
            stub = version_pb2_grpc.ApiVersionServiceStub(channel)
            request = version_pb2.ApiVersionRequest()
            response = stub.GetApiVersion(request)
        finally:
            channel.close()
        return None

    """
    HTTP handler
    """
    @staticmethod
    def httpHandlerGet(path, headers, jObj):        
        """if path.endswith("/Generic"):
            sHeader: str = headers.get('command')
            if sHeader is None:
                Utils.throwExceptionHttpMissingHeader('command')
            return MinerBraiinsS9.cgMinerRequest(jObj['ip'], sHeader), 200, 'application/json'"""
        if path.endswith("/ApiVersion"):
            return MinerBraiinsV1Proto.getApiVersion(jObj), 200, 'application/json'
        elif path.endswith("/Config"):
            return MinerBraiinsV1Proto.getConfiguration(jObj), 200, 'application/json'
        elif path.endswith("/Constraints"):
            return MinerBraiinsV1Proto.getConstraints(jObj), 200, 'application/json'
        else:
            return 'Not found', 400, 'text/html'

    @staticmethod
    def httpHandlerPatch(path, headers, jObj):        
        if path.endswith("/DisablePool"):
            index: int = headers.get('index')
            if index is None:
                Utils.throwExceptionHttpMissingHeader('inedx')
            index = int(index)
            return MinerBraiinsS9.sshDisablePool(jObj, index), 200, 'application/json'
        elif path.endswith("/Password"):
            newPassword: str = headers.get('newpassword')
            if newPassword is None or newPassword.strip() == '':
                Utils.throwExceptionHttpMissingHeader('newpassword')
            return MinerBraiinsV1Proto.setPassword(jObj, newPassword), 200, 'application/json'
        else:
            return 'Not found', 400, 'text/html'
    
    @staticmethod
    def httpHandlerPost(path, headers, jObj, contentStr):        
        if path.endswith("/Config"):
            return MinerBraiinsV1Proto.setConfiguration(jObj), 200, 'application/json'
        else:
            return 'Not found', 400, 'text/html'
    """
    HTTP handler END
    """