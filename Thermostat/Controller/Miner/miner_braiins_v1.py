from ..utils import Utils
from .Braiins import actions_pb2
from .Braiins import actions_pb2_grpc
from .Braiins import authentication_pb2
from .Braiins import authentication_pb2_grpc
from .Braiins import configuration_pb2
from .Braiins import configuration_pb2_grpc
from .Braiins import cooling_pb2
from .Braiins import cooling_pb2_grpc
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
        if path.endswith("/ApiVersion"):
            return MinerBraiinsV1.getApiVersion(jObj), 200, 'application/json'
        elif path.endswith("/Config"):
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
        elif path.endswith("/Password"):
            newPassword: str = headers.get('newpassword')
            if newPassword is None or newPassword.strip() == '':
                Utils.throwExceptionHttpMissingHeader('newpassword')
            return MinerBraiinsV1.setPassword(jObj, newPassword), 200, 'application/json'
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
    
    """
    actions_pb2
    """
    # Get LED status 
    @staticmethod
    def getLocateDeviceStatus(jObj):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = actions_pb2.GetLocateDeviceStatusRequest()
        response = Utils.grpcCall(
            actions_pb2_grpc.ActionsServiceStub,
            "GetLocateDeviceStatus",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        return Utils.grpcProtobufToJson(response)

    # Set LED status
    @staticmethod
    def postLocateDeviceStatus(jObj, enabled: bool):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = actions_pb2.SetLocateDeviceStatusRequest()
        request.enabled = enabled
        response = Utils.grpcCall(
            actions_pb2_grpc.ActionsServiceStub,
            "SetLocateDeviceStatus",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def postPause(jObj):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = actions_pb2.PauseMiningRequest()
        response = Utils.grpcCall(
            actions_pb2_grpc.ActionsServiceStub,
            "PauseMining",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def postReboot(jObj):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = actions_pb2.RebootRequest()
        response = Utils.grpcCall(
            actions_pb2_grpc.ActionsServiceStub,
            "RebootMining",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def postRestart(jObj):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = actions_pb2.RestartRequest()
        response = Utils.grpcCall(
            actions_pb2_grpc.ActionsServiceStub,
            "RestartMining",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def postResume(jObj):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = actions_pb2.ResumeMiningRequest()
        response = Utils.grpcCall(
            actions_pb2_grpc.ActionsServiceStub,
            "ResumeMining",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def postStart(jObj):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = actions_pb2.StartRequest()
        response = Utils.grpcCall(
            actions_pb2_grpc.ActionsServiceStub,
            "Start",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def postStop(jObj):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = actions_pb2.StopRequest()
        response = Utils.grpcCall(
            actions_pb2_grpc.ActionsServiceStub,
            "Stop",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        return Utils.grpcProtobufToJson(response)
    """
    actions_pb2 END
    """

    """
    authentication_pb2
    """
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
    def setPassword(jObj, newPassword: str):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'newpassword', True, False)
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = authentication_pb2.SetPasswordRequest()
        request.password = newPassword
        response = Utils.grpcCall(
            authentication_pb2_grpc.AuthenticationServiceStub,
            "SetPassword",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        return Utils.grpcProtobufToJson(response)
    """
    authentication_pb2 END
    """

    """
    configuration_pb2
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
        return Utils.grpcProtobufToJson(response)

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
        return Utils.grpcProtobufToJson(response)
    """
    configuration_pb2 END
    """

    """
    cooling_pb2
    """
    @staticmethod
    def getCoolingState(jObj):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = cooling_pb2.GetCoolingStateRequest()
        response = Utils.grpcCall(
            cooling_pb2_grpc.CoolingServiceStub,
            "GetCoolingState",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def postImmersionMode(jObj, enabled: bool):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = cooling_pb2.SetImmersionModeRequest()
        request.enabled = enbaled
        response = Utils.grpcCall(
            cooling_pb2_grpc.CoolingServiceStub,
            "SetImmersionMode",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        print(f"getConstraints {response}")
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def postCoolingMode(jObj, mode: str, fanSpeedRpm: int = None):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = cooling_pb2.SetCoolingModeRequest()
        if mode is None or mode.strip() == '':
            Utils.throwExceptionHttpMissingHeader('mode')
        request.mode = mode
        if fanSpeedRpm is not None:
            request.fan_speed_rpm = fanSpeedRpm
        response = Utils.grpcCall(
            cooling_pb2_grpc.CoolingServiceStub,
            "SetCoolingMode",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        print(f"getConstraints {response}")
        return Utils.grpcProtobufToJson(response)
    """
    cooling_pb2 END
    """

    """
    version_pb2
    """
    @staticmethod
    def getApiVersion(jObj):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = version_pb2.ApiVersionRequest()
        response = Utils.grpcCall(
            version_pb2_grpc.ApiVersionServiceStub,
            "GetApiVersion",
            request,
            token,
            f"{jObj['ip']}:{50051}"
        )
        return Utils.grpcProtobufToJson(response)
    """
    version_pb2 END
    """