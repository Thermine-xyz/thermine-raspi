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

    # Check if the miner is online
    @staticmethod
    def getJwtToken(jObj):
        MinerBraiinsV1Proto.getJwtToken(jObj)
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
        
        elif path.endswith("/Miner/Details"):
            return MinerBraiinsV1Proto.getMinerDetails(Obj), 200, 'application/json'
        elif path.endswith("/Miner/Errors"):
            return MinerBraiinsV1Proto.getMinerErrors(Obj), 200, 'application/json'
        elif path.endswith("/Miner/Hashboards"):
            return MinerBraiinsV1Proto.getMinerHashboards(Obj), 200, 'application/json'
        elif path.endswith("/Miner/Status"):
            return MinerBraiinsV1Proto.getMinerStatus(Obj), 200, 'application/json'
        elif path.endswith("/Miner/Stats"):
            return MinerBraiinsV1Proto.getMinerStats(Obj), 200, 'application/json'
        elif path.endswith("/Miner/SupportArchive"):
            return MinerBraiinsV1Proto.getMinerSupportArchive(Obj), 200, 'application/json'
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

    
    """
    MinerService
    """
    # Get data from miner and save it locally
    @staticmethod
    def minerServiceGetData(jObj):
        try: # Hashrate(THs) and Board temp
            jObjRtr = MinerBraiinsV1Proto.getHashboards(jObj)
            hashRate = 0.0
            tBoard = 0.0
            for jObjS in jObjRtr['hashboards']:
                hashRate = hashRate + jObjS['hashrate_ths']
                tBoard = tBoard + jObjS['temperature_celsius']
            hashRate = round(hashRate,4)
            tBoard = round(tBoard / len(jObjRtr['hashboards']),4)
            path = Utils.pathDataMinerHashrate(jObj)
            lock = Utils.getFileLock(path).gen_wlock() # lock for reading, method "wlock"
            with lock:
                with open(path, 'a', encoding='utf-8') as file:
                    file.write(f"{Utils.nowUtc()};{hashRate}\n")
        except Exception as e:
            Utils.logger.error(f"BraiinsS9 minerServiceGetData hashrate {jObj['uuid']} error {e}")

        try: # Chip temp
            jObjRtr = MinerBraiinsV1Proto.getCoolingState(jObj)
            tChip = 0.0
            if (
                Utils.jsonCheckKeyExists(jObjRtr, 'high_temperature', False, False) and
                jObjRtr['high_temperature']['location'] == "SENSOR_LOCATION_CHIP"
            ):
                tChip = jObjRtr['high_temperature']['temperature']['celsius']
            else:
                tChip = -1
            path = Utils.pathDataMinerTemp(jObj)
            lock = Utils.getFileLock(path).gen_wlock() # lock for reading, method "wlock"
            with lock:
                with open(path, 'a', encoding='utf-8') as file:
                    file.write(f"{Utils.nowUtc()};{tBoard};{tChip}\n")
        except Exception as e:
            Utils.logger.error(f"BraiinsV1 minerServiceGetData temp {jObj['uuid']} error {e}")
        # Returns OK if no error was raised
        return Utils.resultJsonOK()
    """
    MinerService END
    """