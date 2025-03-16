from ..utils import Utils
from .Braiins import authentication_pb2
from .Braiins import authentication_pb2_grpc
from .Braiins import version_pb2
from .Braiins import version_pb2_grpc

import grpc

class MinerBraiins:
    # Check if the miner is online
    def echo(jObj):
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object");
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        channel = Utils.grpcChannel(f"{jObj['ip']}:{50051}")
        try:
            stub = version_pb2_grpc.ApiVersionServiceStub(channel)
            request = version_pb2.ApiVersionRequest()
            response = stub.GetApiVersion(request)
        finally:
            channel.close()
        return None

    # Get the token from miner, param jObj: a miner JSON Object with IP and password
    def getJwtToken(jObj):
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object");
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        Utils.jsonCheckKeyTypeStr(jObj, 'username', True, False)
        Utils.jsonCheckKeyTypeStr(jObj, 'password', True, False)
        print("1")
        channel = Utils.grpcChannel(f"{jObj['ip']}:{50051}")
        try:
            print("2")
            stub = authentication_pb2_grpc.AuthenticationServiceStub(channel)
            print("3")
            request = authentication_pb2.LoginRequest(
                username=jObj['username'],
                password=jObj['password']
            )
            print("4")
            response = stub.Login(request)
            print("5")
            return {"token": response.token, "exp": response.timeout_s}
            print("6")
        finally:
            channel.close()
        return None 