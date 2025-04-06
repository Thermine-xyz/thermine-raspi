from ..utils import Utils
from .Braiins import authentication_pb2
from .Braiins import authentication_pb2_grpc
from .Braiins import configuration_pb2
from .Braiins import configuration_pb2_grpc
from .Braiins import version_pb2
from .Braiins import version_pb2_grpc

import grpc

class MinerBraiinsV1:
    # Check if the miner is online
    @staticmethod
    def echo(jObj):
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object")
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        channel = Utils.grpcChannel(f"{jObj['ip']}:{50051}")
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
        if path.endswith("/Config"):
            return MinerBraiinsV1.getConfiguration(jObj), 200, 'application/json'
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
        elif path.endswith("/FaultLight"):
            isEnabled: bool = headers.get('enabled') == "true"
            isEnabled = bool(isEnabled)
            return MinerBraiinsS9.sshFaultLight(jObj, isEnabled), 200, 'application/json'
        else:
            return 'Not found', 400, 'text/html'
    
    @staticmethod
    def httpHandlerPost(path, headers, jObj, contentStr):        
        if path.endswith("/Config"):
            return MinerBraiinsS9.sshConfigPostJsonStr(jObj, contentStr), 200, 'application/json'
        else:
            return 'Not found', 400, 'text/html'
    """
    HTTP handler END
    """
    
    @staticmethod
    def getConfiguration(jObj):
        print("getConfiguration1")
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        print(f"getConfiguration2 {token}")
        # channel = Utils.grpcChannelSecure(f"{jObj['ip']}:{50051}", token)
        # Keeps using the insecure channel
        # channel = Utils.grpcChannel(f"{jObj['ip']}:{50051}")
        print("getConfiguration3")
        try:
            stub = configuration_pb2_grpc.ConfigurationServiceStub(channel)
            print("getConfiguration4")
            request = configuration_pb2.GetMinerConfigurationRequest()
            # metadata = [('authorization', f'{token}')]
            # response = stub.GetMinerConfiguration(request, metadata=metadata)
            response = Utils.grpcCall(stub, stub.GetMinerConfiguration, request, token, aip)
            # htts improve it later response = stub.GetMinerConfiguration(request)
            print(f"Configs {response}")
            return Utils.resultJsonOK()
        finally:
            channel.close()
        
        
    # Get the token from miner, param jObj: a miner JSON Object with IP and password
    @staticmethod
    def getJwtToken(jObj):
        return {"token": MinerBraiinsV1.getJwtTokenStr, "exp": response.timeout_s}
    def getJwtTokenStr(jObj):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        Utils.jsonCheckKeyTypeStr(jObj, 'username', True, False)
        Utils.jsonCheckKeyTypeStr(jObj, 'password', True, False)
        channel = Utils.grpcChannel(f"{jObj['ip']}:{50051}")
        try:
            stub = authentication_pb2_grpc.AuthenticationServiceStub(channel)

            request = authentication_pb2.LoginRequest(
                username=jObj['username'],
                password=jObj['password']
            )

            response = stub.Login(request)
            return response.token
        finally:
            channel.close()