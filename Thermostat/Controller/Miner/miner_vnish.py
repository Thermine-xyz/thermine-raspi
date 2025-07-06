from ..utils import Utils
from ..utils import HttpException
from .miner_utils import MinerUtils
import requests
import json

class MinerVnish(MinerUtils.MinerBase):
    TOKEN = ""
    
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
        if cls.TOKEN == '':
            Utils.jsonCheckKeyTypeStr(jObj, 'password', True, False)
            jR = MinerVnish.httpCommandApi(jObj, 'unlock', {"pw": jObj['password']})
            Utils.jsonCheckKeyTypeStr(jR, 'token', True, False)
            cls.TOKEN = jR['token']
        return {"token": cls.TOKEN}
    @classmethod
    def pause(cls, jObj):
        return MinerVnish.httpCommandAuth(jObj, 'mining/pause', {}) # Empty {} to force POST
    @classmethod
    def reboot(cls, jObj):
        return MinerVnish.httpCommandAuth(jObj, 'mining/restart', {}) # Empty {} to force POST
    @classmethod
    def resume(cls, jObj):
        return MinerVnish.httpCommandAuth(jObj, 'mining/resume', {}) # Empty  to force POST

    @classmethod
    def status(cls, jObj):
        """
        All status from Vnish
        
        failure
        restarting
        mining
        starting
        shutting-down
        initializing
        stopped
        """
        jR = MinerVnish.httpCommandApi(jObj, 'status')
        if Utils.jsonCheckKeyExists(jR, 'miner_state', False):
            if jR['miner_state'] == 'mining':
                return MinerUtils.MinerStatus.MinerNormal
            if jR['miner_state'] in ['stopped']:
                return MinerUtils.MinerStatus.MinerNotStarted
            elif jR['miner_state'] in ['initializing', 'starting', 'initializing', 'restarting']:
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
            if 'application/json' in response.headers.get('Content-Type', ''):
                respData = response.json()
            else:
                respData = response.text
            return respData
        except Exception as e:
            raise Exception(f"MinerVnish httpGetCommand {context}: {e}")
    @staticmethod
    def httpCommandApi(jObj, context: str, payload: dict = None, headers: dict = None):
        return MinerVnish.httpCommand(jObj, f"api/v1/{context}", payload, headers)
    @staticmethod
    def httpCommandAuth(jObj, context: str, payload: dict = None, headers: dict = None):
        """run authenticated commands"""
        token = MinerVnish.getToken(jObj)
        if headers is None:
            headers = {}
        headers['Authorization'] = f"Bearer {token['token']}"
        jR = MinerVnish.httpCommandApi(jObj, context, payload, headers)
        return jR
    """
    HTTP methods
    """

    """
    xminer-api methods
    """
    @staticmethod
    def xminerApiAuthCheck(jObj):
        jR = MinerVnish.httpCommandAuth(jObj, 'auth-check')
    @staticmethod
    def xminerApiChainsGetMiner(jObj):
        jR = MinerVnish.httpCommandApi(jObj, 'chains')
        return jR

    @staticmethod
    def xminerApiGetMinerInfo(jObj):
        jR = MinerVnish.httpCommandApi(jObj, 'info')
        return jR

    @staticmethod
    def xminerApiGetSummary(jObj):
        jR = MinerVnish.httpCommandApi(jObj, 'summary')
        print(f"xminerApiGetSummary {jR}")
        return jR
    @staticmethod
    def xminerApiGetSummaryPerf(jObj):
        jR = MinerVnish.httpCommandApi(jObj, 'perf-summary')
        print(f"xminerApiGetSummaryPerf {jR}")
        return jR
    """
    xminer-api methods
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
                jObjRtr = MinerVnish.xminerApiChainsGetMiner(jObj)
                hashRate = 0.0
                tBoard = 0.0
                tChip = 0.0
                count = 0
                for jObjS in jObjRtr:
                    hashRate = hashRate + jObjS['hr_realtime']
                    for jObjT in jObjS['sensors']:
                        if Utils.jsonCheckKeyTypeStr(jObjT, 'state', False, False) and jObjT['state'] == 'measure':
                            count += 1
                            tBoard = tBoard + jObjT['board']
                            tChip = tChip + jObjT['chip']
                    if count > 0:
                        tBoard = round(tBoard / count, 4)
                        tChip = round(tChip / count, 4)
                hashRate = round((hashRate / len(jObjRtr)),4)
                tBoard = round(tBoard / len(jObjRtr),4)
                tChip = round(tChip / len(jObjRtr),4)
                
                # Must check the hashrate measure system, force Tera
                jObjRtr = MinerVnish.xminerApiGetMinerInfo(jObj)
                if jObjRtr['hr_measure'] == 'GH/s':
                    hashRate = round(hashRate / 1000,4)
                elif jObjRtr['hr_measure'] == 'EH/s':
                    hashRate = hashRate * 1000
                else:
                    Utils.throwExceptionInvalidValue(f"MinerVnish minerServiceGetData hr_measure {jObjRtr['hr_measure']}")
                
                Utils.dataBinaryWriteFile(Utils.pathDataMinerHashrate(jObj), [hashRate])
                Utils.dataBinaryWriteFile(Utils.pathDataMinerTemp(jObj), [tBoard, tChip])
            except Exception as e:
                Utils.logger.error(f"MinerVnish minerServiceGetData hashrate {jObj['uuid']} error {e}")
                pass
        return Utils.resultJsonOK()

    @classmethod
    def minerThermalControl(cls, jObj: dict, tCurrent: float): # tCurrent=current temperature, from miner OR sensor
        mStatus : MinerUtils.MinerStatus = MinerVnish.status(jObj)
        if mStatus in [MinerUtils.MinerStatus.MinerNotReady, MinerUtils.MinerStatus.MinerUnknown]:
            Utils.logger.warning(f"MinerVnish minerThermalControl {jObj['uuid']} miner status {mStatus}")
            return None
        
        if Utils.jsonCheckKeyExists(jObj, 'sensor', False):
            tTarget = float(jObj['sensor']['temp_target'])
        else:
            jConfig = MinerVnish.xminerApiGetSummaryPerf(jObj)
            Utils.jsonCheckKeyExists(jConfig, 'preset_switcher', True)
            Utils.jsonCheckKeyExists(jConfig['preset_switcher'], 'decrease_temp', True)
            tTarget = float(jConfig['preset_switcher']['decrease_temp'])

        if not Utils.jsonCheckKeyExists(jObj, 'runControl', False):
            jObj['runControl'] = {}
        if not Utils.jsonCheckKeyExists(jObj['runControl'], 'thermal_last_cmd', False):
            jObj['runControl']['thermal_last_cmd'] = None
        thermalLastCmd = jObj['runControl']['thermal_last_cmd']
        if tCurrent <= tTarget - 2 and mStatus != MinerUtils.MinerStatus.MinerNormal and thermalLastCmd != 'START':
            jObj['runControl']['thermal_last_cmd'] = 'START'
            event = {"action":"update","data":jObj}
            Utils.pubsub_instance.publish(Utils.PubSub.TOPIC_DATA_HAS_CHANGED, event)
            MinerVnish.resume(jObj)
            Utils.logger.info(f"MinerVnish minerThermalControl {jObj['uuid']} Temperature too low {tTarget}/{tCurrent}ºC, mining resumed")
        elif tCurrent >= tTarget and mStatus == MinerUtils.MinerStatus.MinerNormal: 
            jObj['runControl']['thermal_last_cmd'] = 'STOP'
            event = {"action":"update","data":jObj}
            Utils.pubsub_instance.publish(Utils.PubSub.TOPIC_DATA_HAS_CHANGED, event)
            MinerVnish.pause(jObj)
            Utils.logger.warning(f"MinerVnish minerThermalControl {jObj['uuid']} Temperature too high {tTarget}/{tCurrent}ºC, mining paused")
        return None
    """
    MinerService END
    """
