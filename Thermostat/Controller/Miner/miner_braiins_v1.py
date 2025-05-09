from ..utils import Utils
from .miner_utils import MinerUtils
from ..w1thermsensor_utils import W1ThermSensorUtils
from .miner_braiins_v1_proto import MinerBraiinsV1Proto

import grpc
import json

class MinerBraiinsV1:
    # Check if the miner is online
    @staticmethod
    def echo(jObj):
        MinerBraiinsV1Proto.getApiVersion(jObj)
        return None
    
    # In case miner is paused, grpcTemps returns "Not Ready"
    @staticmethod
    def status(jObj):
        jMDetails = MinerBraiinsV1Proto.minerGetDetails(jObj)
        print(f"MinerBraiinsV1.status {jMDetails}")
        Utils.jsonCheckIsObj(jMDetails, True)
        if Utils.jsonCheckKeyExists(jMDetails, 'status', False) and jMDetails['status'] == 'MINER_STATUS_NORMAL':
            return MinerUtils.MinerStatus.MinerNormal
        elif Utils.jsonCheckKeyExists(jMDetails, 'status', False) and jMDetails['status'] == 'Not ready':
            return MinerUtils.MinerStatus.MinerNotReady
        else:
            return MinerUtils.MinerStatus.MinerUnknown

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
        if path.endswith("/ApiVersion"):
            return MinerBraiinsV1Proto.getApiVersion(jObj), 200, 'application/json'
        elif path.endswith("/Config"):
            return MinerBraiinsV1Proto.getConfiguration(jObj), 200, 'application/json'
        elif path.endswith("/Constraints"):
            return MinerBraiinsV1Proto.getConstraints(jObj), 200, 'application/json'
        
        elif path.endswith("/Cooling/State"):
            return MinerBraiinsV1Proto.getCoolingState(jObj), 200, 'application/json'
        
        elif path.endswith("/Miner/Details"):
            return MinerBraiinsV1Proto.minerGetDetails(jObj), 200, 'application/json'
        elif path.endswith("/Miner/Errors"):
            return MinerBraiinsV1Proto.minerGetErrors(jObj), 200, 'application/json'
        elif path.endswith("/Miner/Hashboards"):
            return MinerBraiinsV1Proto.minerGetHashboards(jObj), 200, 'application/json'
        elif path.endswith("/Miner/Status"):
            return MinerBraiinsV1Proto.minerGetStatus(jObj), 200, 'application/json'
        elif path.endswith("/Miner/Stats"):
            return MinerBraiinsV1Proto.minerGetStats(jObj), 200, 'application/json'
        elif path.endswith("/Miner/SupportArchive"):
            return MinerBraiinsV1Proto.minerGetSupportArchive(jObj), 200, 'application/json'
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
            jObjRtr = MinerBraiinsV1Proto.minerGetHashboards(jObj)
            hashRate = 0.0
            tBoard = 0.0
            for jObjS in jObjRtr['hashboards']:
                hashRate = hashRate + jObjS['stats']['real_hashrate']['last_5s']['gigahash_per_second']
                tBoard = tBoard + jObjS['board_temp']['degree_c']
            hashRate = round((hashRate / len(jObjRtr['hashboards'])) / 1000,4)
            tBoard = round(tBoard / len(jObjRtr['hashboards']),4)
            path = Utils.pathDataMinerHashrate(jObj)
            lock = Utils.getFileLock(path).gen_wlock() # lock for reading, method "wlock"
            with lock:
                with open(path, 'a', encoding='utf-8') as file:
                    file.write(f"{Utils.nowUtc()};{hashRate}\n")
        except Exception as e:
            Utils.logger.error(f"BraiinV1 minerServiceGetData hashrate {jObj['uuid']} error {e}")
            pass

        try: # Chip temp
            jObjRtr = MinerBraiinsV1Proto.getCoolingState(jObj)
            tChip = 0.0
            if (
                Utils.jsonCheckKeyExists(jObjRtr, 'highest_temperature', False) and
                jObjRtr['highest_temperature']['location'] == "SENSOR_LOCATION_CHIP"
            ):
                tChip = jObjRtr['highest_temperature']['temperature']['degree_c']
            else:
                tChip = -1
            path = Utils.pathDataMinerTemp(jObj)
            lock = Utils.getFileLock(path).gen_wlock() # lock for reading, method "wlock"
            with lock:
                with open(path, 'a', encoding='utf-8') as file:
                    file.write(f"{Utils.nowUtc()};{tBoard};{tChip}\n")
        except Exception as e:
            Utils.logger.error(f"BraiinsV1 minerServiceGetData temp {jObj['uuid']} error {e}")
            pass

        if Utils.jsonCheckKeyExists(jObj, 'sensor', False):
            """w1thermsensor"""
            try: # Reads sensor temp if it found the sensor JSON obj
                W1ThermSensorUtils.saveTempToDataFile(jObj)
            except Exception as e:
                Utils.logger.error(f"BraiinsV1 minerServiceGetData temp {jObj['uuid']} error {e}")
                pass
        return Utils.resultJsonOK()

    @staticmethod
    def minerThermalControl(jObj: dict, tCurrent: float): # tCurrent=current temperature, from miner OR sensor
        print(f"MinerBraiinsV1.minerThermalControl 1")
        mStatus : MinerUtils.MinerStatus = MinerBraiinsV1.status(jObj)
        print(f"MinerBraiinsV1.minerThermalControl mStatus {mStatus}")
        if mStatus in [MinerUtils.MinerStatus.MinerNotReady, MinerUtils.MinerStatus.MinerUnknown]:
            Utils.logger.warning(f"BraiinsV1 minerThermalControl {jObj['uuid']} miner status {mStatus}")
            return None
        
        if Utils.jsonCheckKeyExists(jObj, 'sensor', False):
            print(f"MinerBraiinsV1.minerThermalControl readuing from Sensor")
            tTarget = float(jObj['sensor']['temp_target'])
        else:
            print(f"MinerBraiinsV1.minerThermalControl readuing from Miner")
            jConfig = MinerBraiinsV1Proto.getConfiguration(jObj)            
            print(f"MinerBraiinsV1.minerThermalControl jConfig {jConfig}")
            Utils.jsonCheckKeyExists(jConfig, 'temperature', True)
            Utils.jsonCheckKeyExists(jConfig['temperature'], 'target_temperature', True)
            tTarget = float(jConfig['temperature']['target_temperature'])

        print(f"MinerBraiinsV1.minerThermalControl tTarget {tTarget}")
        if tCurrent <= tTarget - 2:
            MinerBraiinsV1Proto.postStart(jObj)
            Utils.logger.info(f"BraiinsV1 minerThermalControl {jObj['uuid']} Temperature too low {tCurrent}ºC, mining started")
        elif tCurrent >= tTarget:
            MinerBraiinsV1Proto.postStop(jObj)
            Utils.logger.warning(f"BraiinsV1 minerThermalControl {jObj['uuid']} Temperature too high {tCurrent}ºC, mining stopped")
        return None
    """
    MinerService END
    """