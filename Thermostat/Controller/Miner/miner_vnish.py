from ..utils import Utils
from ..utils import HttpException
from .miner_utils import MinerUtils
import requests
import json

class MinerVnish(MinerUtils.MinerBase):        
    """
    Inherited methods
    """
    # Check if the miner is online
    @classmethod
    def echo(cls, jObj):
        """ Based on official doc (https://vnish.group/en/faq-vnish-en/#api) """
        jR = MinerVnish.httpCommand(jObj, 'docs/api-doc.json')
        Utils.jsonCheckKeyExists(jR, 'info', True)
        Utils.jsonCheckIsObj(jR['info'], True)
        Utils.jsonCheckKeyTypeStr(jR['info'], 'title', True, False)
        if jR['info']['title'].lower() != 'xminer-api':
            Utils.throwExceptionInvalidValue("Miner is not xminer-api")
    # Get the token from miner, param jObj: a miner JSON Object with IP and password
    @classmethod
    def getToken(cls, jObj):
        print(f"getToken 1 {e}")
        Utils.jsonCheckKeyTypeStr(jObj, 'password', True, False)
        jR = MinerVnish.httpCommandApi(jObj, 'unlock', {"pw": jObj['password']})
        Utils.jsonCheckKeyTypeStr(jR, 'token', True, False)
        return {"token": jR['token']}
    @classmethod
    def pause(jObj):
        return MinerVnish.httpCommandAuth(jObj, 'mining/pause', [])
    @classmethod
    def reboot(jObj):
        return MinerVnish.httpCommandAuth(jObj, 'mining/restart', [])
    @classmethod
    def resume(jObj):
        return MinerVnish.httpCommandAuth(jObj, 'mining/resume', [])
    # In case miner is paused, grpcTemps returns "Not Ready"
    @classmethod
    def status(cls, jObj):
        jR = MinerVnish.httpCommandApi(jObj, 'status')
        print(f"status {jR}")
        if Utils.jsonCheckKeyExists(jR, 'status', False):
            if jR['status'] == 'MINER_STATUS_NORMAL':
                return MinerUtils.MinerStatus.MinerNormal
            if jR['status'] == 'MINER_STATUS_NOT_STARTED':
                return MinerUtils.MinerStatus.MinerNotStarted
            elif jR['status'] == 'Not ready':
                return MinerUtils.MinerStatus.MinerNotReady
            else:
                return MinerUtils.MinerStatus.MinerUnknown
        else:
            return MinerUtils.MinerStatus.MinerUnknown
    """
    Inherited methods END
    """
    
    """
    HTTP methods
    """
    @staticmethod
    def httpCommand(jObj, context: str, payload: dict = None, headers: dict = None):
        try:
            Utils.jsonCheckIsObj(jObj, True)
            Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
            endpoint = f"http://{jObj['ip']}/" + context

            if payload is None:
                response = requests.get(endpoint, headers=headers)
            else:
                response = requests.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"MinerVnish httpGetCommand {context}: {e}")
    @staticmethod
    def httpCommandApi(jObj, context: str, payload: dict = None, headers: dict = None):
        return MinerVnish.httpCommand(jObj, "api/v1/" + context, payload, headers)
    @staticmethod
    def httpCommandAuth(jObj, context: str, payload: dict, headers: dict):
        """run authenticated commands"""
        token = MinerVnish.getToken(jObj)
        headers['Authorization'] = token['token']
        return MinerVnish.httpCommandApi(jObj, context, payload, headers)
    """
    HTTP methods
    """

    """
    MinerService
    """
    # Get data from miner and save it locally
    @classmethod
    def minerServiceGetData(cls, jObj):
        mStatus : MinerUtils.MinerStatus = MinerVnish.status(jObj)
        if mStatus == MinerUtils.MinerStatus.MinerNormal:
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

    @classmethod
    def minerThermalControl(cls, jObj: dict, tCurrent: float): # tCurrent=current temperature, from miner OR sensor
        mStatus : MinerUtils.MinerStatus = MinerBraiinsV1.status(jObj)
        if mStatus in [MinerUtils.MinerStatus.MinerNotReady, MinerUtils.MinerStatus.MinerUnknown]:
            Utils.logger.warning(f"BraiinsV1 minerThermalControl {jObj['uuid']} miner status {mStatus}")
            return None
        
        if Utils.jsonCheckKeyExists(jObj, 'sensor', False):
            tTarget = float(jObj['sensor']['temp_target'])
        else:
            jConfig = MinerBraiinsV1Proto.getConfiguration(jObj)            
            Utils.jsonCheckKeyExists(jConfig, 'temperature', True)
            Utils.jsonCheckKeyExists(jConfig['temperature'], 'target_temperature', True)
            tTarget = float(jConfig['temperature']['target_temperature'])

        if not Utils.jsonCheckKeyExists(jObj, 'runControl', False):
            jObj['runControl'] = {}
        if not Utils.jsonCheckKeyExists(jObj['runControl'], 'thermal_last_cmd', False):
            jObj['runControl']['thermal_last_cmd'] = None
        thermalLastCmd = jObj['runControl']['thermal_last_cmd']
        if tCurrent <= tTarget - 2 and mStatus != MinerUtils.MinerStatus.MinerNormal and thermalLastCmd != 'START':
            jObj['runControl']['thermal_last_cmd'] = 'START'
            event = {"action":"update","data":jObj}
            Utils.pubsub_instance.publish(Utils.PubSub.TOPIC_DATA_HAS_CHANGED, event)
            MinerBraiinsV1Proto.postStart(jObj)
            Utils.logger.info(f"BraiinsV1 minerThermalControl {jObj['uuid']} Temperature too low {tTarget}/{tCurrent}ºC, mining started")
        elif tCurrent >= tTarget and mStatus == MinerUtils.MinerStatus.MinerNormal: 
            jObj['runControl']['thermal_last_cmd'] = 'STOP'
            event = {"action":"update","data":jObj}
            Utils.pubsub_instance.publish(Utils.PubSub.TOPIC_DATA_HAS_CHANGED, event)
            MinerBraiinsV1Proto.postStop(jObj)
            Utils.logger.warning(f"BraiinsV1 minerThermalControl {jObj['uuid']} Temperature too high {tTarget}/{tCurrent}ºC, mining stopped")
        return None
    """
    MinerService END
    """
