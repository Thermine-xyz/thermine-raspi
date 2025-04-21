from ..utils import Utils
from .Braiins import authentication_pb2
from .Braiins import authentication_pb2_grpc
from .Braiins import configuration_pb2
from .Braiins import configuration_pb2_grpc
from .Braiins import version_pb2
from .Braiins import version_pb2_grpc

import grpc
from google.protobuf.json_format import MessageToDict
import json

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
        elif path.endswith("/Constraints"):
            return MinerBraiinsV1.getConstraints(jObj), 200, 'application/json'
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
            return MinerBraiinsV1.setConfiguration(jObj), 200, 'application/json'
        else:
            return 'Not found', 400, 'text/html'
    """
    HTTP handler END
    """
    
    @staticmethod
    def getConfiguration(jObj):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = configuration_pb2.GetMinerConfigurationRequest()
        response = Utils.grpcCall(
            configuration_pb2_grpc.ConfigurationServiceStub,
            "GetMinerConfiguration",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        response_dict = MessageToDict(response, preserving_proto_field_name=True)
        response_json = json.dumps(response_dict, indent=2)
        return response_json

    @staticmethod
    def getConstraints(jObj):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = configuration_pb2.GetConstraintsRequest()
        response = Utils.grpcCall(
            configuration_pb2_grpc.ConfigurationServiceStub,
            "GetConstraints",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        print(f"getConstraints {response}")
        response_dict = MessageToDict(response, preserving_proto_field_name=True)
        response_json = json.dumps(response_dict, indent=2)
        return response_json
        
        
    # Get the token from miner, param jObj: a miner JSON Object with IP and password
    @staticmethod
    def getJwtToken(jObj):
        #return {"token": MinerBraiinsV1.getJwtTokenStr, "exp": response.timeout_s}
        tokenStr = MinerBraiinsV1.getJwtTokenStr(jObj)
        return {"token": tokenStr}
    
    @staticmethod
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
    
    @staticmethod
    def setConfiguration(jObj):
        print("setConfiguration1")
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        aip = f"{jObj['ip']}:{50051}"
        request = configuration_pb2.SetMinerConfigurationRequest()

        # Atualizar pools (exemplo)
        pool_group = request.pool_groups.add()
        pool_group.uid = "0"
        pool_group.name = "Default"
        pool = pool_group.pools.add()
        pool.uid = "1"
        pool.url = "stratum+tcp://192.168.178.138:23334"
        pool.user = "bc1pdl59vd7up437l2a2gft8mhx5qd5dys3p2m4tvht3rc5m63csjgzqtjmphc"
        pool.password = "x1"
        pool.enabled = True

        # Atualizar tuner (exemplo)
        request.tuner.enabled = True
        request.tuner.tuner_mode = configuration_pb2.TunerConfiguration.TUNER_MODE_HASHRATE_TARGET
        request.tuner.hashrate_target.terahash_per_second = 70  # Novo valor

        response = Utils.grpcCall(
            configuration_pb2_grpc.ConfigurationServiceStub,
            "SetMinerConfiguration",
            request,
            token,
            aip
        )
        print("Set Config Response")
        print(response)
        response_json = Utils.protobufToJson(response)
        print("JSON Set Response:")
        print(json.dumps(response_json, indent=2))
        return {"status": "OK", "data": response_json}