from ..utils import Utils
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

class MinerBraiinsV1Proto:    
    
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
            Utils.minerIpBraiinsV1(jObj)
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
            Utils.minerIpBraiinsV1(jObj)
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
            Utils.minerIpBraiinsV1(jObj)
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
            Utils.minerIpBraiinsV1(jObj)
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
            Utils.minerIpBraiinsV1(jObj)
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
            Utils.minerIpBraiinsV1(jObj)
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
            Utils.minerIpBraiinsV1(jObj)
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
            Utils.minerIpBraiinsV1(jObj)
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
        channel = Utils.grpcChannel(Utils.minerIpBraiinsV1(jObj))
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
            Utils.minerIpBraiinsV1(jObj)
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
            Utils.minerIpBraiinsV1(jObj)
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
            Utils.minerIpBraiinsV1(jObj)
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
            Utils.minerIpBraiinsV1(jObj)
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
            Utils.minerIpBraiinsV1(jObj)
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
            Utils.minerIpBraiinsV1(jObj)
        )
        print(f"getConstraints {response}")
        return Utils.grpcProtobufToJson(response)
    """
    cooling_pb2 END
    """

    """
    miner_pb2
    """
    # Get LED status 
    @staticmethod
    def getMinerStatus(jObj):
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = miner_pb2.GetMinerStatusRequest()
        response = Utils.grpcCall(
            miner_pb2_grpc.MinerServiceStub,
            "GetMinerStatus",
            request,
            token,
            Utils.minerIpBraiinsV1(jObj)
        )
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def getMinerDetails(jObj):
        print("getMinerDetails1")
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = miner_pb2.GetMinerDetailsRequest()
        response = Utils.grpcCall(
            miner_pb2_grpc.MinerServiceStub,
            "GetMinerDetails",
            request,
            token,
            Utils.minerIpBraiinsV1(jObj)
        )
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def getMinerStats(jObj):
        print("getMinerStats1")
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = miner_pb2.GetMinerStatsRequest()
        response = Utils.grpcCall(
            miner_pb2_grpc.MinerServiceStub,
            "GetMinerStats",
            request,
            token,
            Utils.minerIpBraiinsV1(jObj)
        )
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def getErrors(jObj):
        print("getErrors1")
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = miner_pb2.GetErrorsRequest()
        response = Utils.grpcCall(
            miner_pb2_grpc.MinerServiceStub,
            "GetErrors",
            request,
            token,
            Utils.minerIpBraiinsV1(jObj)
        )
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def getHashboards(jObj):
        print("getHashboards1")
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = miner_pb2.GetHashboardsRequest()
        response = Utils.grpcCall(
            miner_pb2_grpc.MinerServiceStub,
            "GetHashboards",
            request,
            token,
            Utils.minerIpBraiinsV1(jObj)
        )
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def enableHashboards(jObj, hashboard_ids: list):
        print("enableHashboards1")
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = miner_pb2.EnableHashboardsRequest()
        request.hashboard_ids.extend(hashboard_ids)
        response = Utils.grpcCall(
            miner_pb2_grpc.MinerServiceStub,
            "EnableHashboards",
            request,
            token,
            Utils.minerIpBraiinsV1(jObj)
        )
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def disableHashboards(jObj, hashboard_ids: list):
        print("disableHashboards1")
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = miner_pb2.DisableHashboardsRequest()
        request.hashboard_ids.extend(hashboard_ids)
        response = Utils.grpcCall(
            miner_pb2_grpc.MinerServiceStub,
            "DisableHashboards",
            request,
            token,
            Utils.minerIpBraiinsV1(jObj)
        )
        return Utils.grpcProtobufToJson(response)

    @staticmethod
    def getSupportArchive(jObj):
        print("getSupportArchive1")
        token = MinerBraiinsV1.getJwtTokenStr(jObj)
        request = miner_pb2.GetSupportArchiveRequest()
        response = Utils.grpcCall(
            miner_pb2_grpc.MinerServiceStub,
            "GetSupportArchive",
            request,
            token,
            Utils.minerIpBraiinsV1(jObj)
        )
        # Para dados binários, não convertemos diretamente para JSON
        archive_data = response.archive_data
        # Salvar o arquivo localmente (ex.: ZIP ou tar.gz)
        with open("support_archive.zip", "wb") as f:
            f.write(archive_data)
        print("Support archive saved to support_archive.zip")
        return {"status": "Archive saved", "filename": "support_archive.zip"}

    """
    miner_pb2 END
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
            Utils.minerIpBraiinsV1(jObj)
        )
        return Utils.grpcProtobufToJson(response)
    """
    version_pb2 END
    """
