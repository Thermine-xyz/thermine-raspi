from ..utils import Utils
from .miner_utils import MinerUtils
from .Whatsminer import *

class MinerWhatsminer(MinerUtils.MinerBase):
    """
    API
    """
    @staticmethod
    def getApiMinerStatus(jObj, param=None):
        try:
            api, tcp = getSession(jObj)
            
            req_info = api.get_request_cmds("get.miner.status", param);
            req_length = len(req_info)
            rsp_info = tcp.send(req_info, req_length)
            return = rsp_info
        finally:
            tcp.close()
    """
    API END
    """

    """
    Inherited methods
    """
    @classmethod
    def echo(cls, jObj):
        api, tcp = getSession(jObj)

        try:
            tcp.connect()
        finally:
            tcp.close()
        return None

    @classmethod
    def pause(cls, jObj):
        rsp_info = None
        try:
            api, tcp = getSession(jObj)
            req_info = api.set_miner_service("stop");
            req_length = len(req_info)
            rsp_info = tcp.send(req_info, req_length)
            return rsp_info
        finally:
            tcp.close()
        return rsp_info

    @classmethod
    def reboot(cls, jObj):
        rsp_info = None
        try:
            api, tcp = getSession(jObj)
            req_info = api.set_miner_service("restart");
            req_length = len(req_info)
            rsp_info = tcp.send(req_info, req_length)
            return rsp_info
        finally:
            tcp.close()
        return rsp_info

    @classmethod
    def resume(cls, jObj):
        rsp_info = None
        try:
            api, tcp = getSession(jObj)
            req_info = api.set_miner_service("start");
            req_length = len(req_info)
            rsp_info = tcp.send(req_info, req_length)
            return rsp_info
        finally:
            tcp.close()
        return rsp_info

    @classmethod
    def getToken(cls, jObj):
        try:
            api, tcp, salt = getSession(jObj)
        finally:
            tcp.close()
        return {"salt": salt}
    
    @classmethod
    def status(cls, jObj):
        try:
            api, tcp = getSession(jObj)
            
            req_info = api.get_request_cmds("get.device.info", "miner");
            req_length = len(req_info)
            rsp_info = tcp.send(req_info, req_length)
            miner_working = rsp_info['msg']['working']
            if miner_working == 'false':
                return MinerUtils.MinerStatus.MinerNotStarted
            elif miner_working == 'true':
                req_info = whatsminer_api.get_request_cmds("get.miner.status", "summary");
                req_length = len(req_info)
                rsp_info = whatsminer_tcp.send(req_info, req_length)
                bootup_time = rsp_info['msg']['summary']['bootup-time']
                if bootup_time >= 30: # Fixing a safe time of X secs to consider the miner working
                    return MinerUtils.MinerStatus.MinerNormal
                else:
                    return MinerUtils.MinerStatus.MinerNotReady
            else:
                return MinerUtils.MinerStatus.MinerUnknown
        finally:
            tcp.close()
    """
    Inherited methods END
    """

    @staticmethod
    def getSession(jObj) -> WhatsminerAPIv3, WhatsminerTCP, str:
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        Utils.jsonCheckKeyTypeStr(jObj, 'username', True, False)
        Utils.jsonCheckKeyTypeStr(jObj, 'password', True, False)

        whatsminer_api = WhatsminerAPIv3(jObj['username'], jObj['password'])
        whatsminer_tcp = WhatsminerTCP(jObj['ip'], 4433, jObj['username'], jObj['password'])
        whatsminer_tcp.connect()
        req_info = whatsminer_api.get_request_cmds("get.device.info", "salt");
        req_length = len(req_info)
        rsp_info = whatsminer_tcp.send(req_info, req_length)
        if rsp_info['code'] == 0:
            miner_salt = rsp_info['msg']['salt']
            whatsminer_api.set_salt(miner_salt)
        else:
            Utils.throwExceptionResourceNotFound(f"Whatsminer status cmd [get.device.info] wrong code: {rsp_info}")

        return whatsminer_api, whatsminer_tcp, miner_salt
    
    """
    MinerService
    """
    # Get data from miner and save it locally
    @classmethod
    def minerServiceGetData(cls, jObj):
        mStatus : MinerUtils.MinerStatus = MinerWhatsminer.status(jObj)
        if mStatus == MinerUtils.MinerStatus.MinerNormal:
            try: # Hashrate(THs) and Board temp
                hashRate = 0.0
                tBoard = 0.0
                tChip = 0.0
                try:
                    api, tcp = getSession(jObj)

                    req_info = whatsminer_api.get_request_cmds("get.miner.status", "summary");
                    req_length = len(req_info)
                    rsp_info = whatsminer_tcp.send(req_info, req_length)
                    hashRate = rsp_info['msg']['summary']['hash-realtime']
                    tBoardAry = rsp_info['msg']['summary']['board-temperature']
                    tBoard = round(sum(tBoardAry) / len(tBoardAry),4)
                    tChip = rsp_info['msg']['summary']['chip-temp-avg']
                    
                    Utils.dataBinaryWriteFile(Utils.pathDataMinerHashrate(jObj), [hashRate])
                    Utils.dataBinaryWriteFile(Utils.pathDataMinerTemp(jObj), [tBoard, tChip])
                finally:
                    tcp.close()
            except Exception as e:
                Utils.logger.error(f"MinerWhatsminer minerServiceGetData {jObj['uuid']} error {e}")
                pass
        return Utils.resultJsonOK()

    @classmethod
    def minerThermalControl(cls, jObj: dict, tCurrent: float): # tCurrent=current temperature, from miner OR sensor
        mStatus : MinerUtils.MinerStatus = MinerWhatsminer.status(jObj)
        print(f"minerThermalControl status {mStatus}")
        if mStatus in [MinerUtils.MinerStatus.MinerNotReady, MinerUtils.MinerStatus.MinerUnknown]:
            Utils.logger.warning(f"MinerWhatsminer minerThermalControl {jObj['uuid']} miner status {mStatus}")
            return None
        
        if Utils.jsonCheckKeyExists(jObj, 'sensor', False):
            tTarget = float(jObj['sensor']['temp_target'])
        else:
            jConfig = MinerWhatsminer.getApiMinerStatus(jObj, "summary")            
            tBoardAry = rsp_info['msg']['summary']['board-temperature']
            tBoard = round(sum(tBoardAry) / len(tBoardAry),4)
            tChip = rsp_info['msg']['summary']['chip-temp-avg']
            if tBoard > tChip:
                tTarget = tBoard
            else:
                tTarget = tChip

        if not Utils.jsonCheckKeyExists(jObj, 'runControl', False):
            jObj['runControl'] = {}
        if not Utils.jsonCheckKeyExists(jObj['runControl'], 'thermal_last_cmd', False):
            jObj['runControl']['thermal_last_cmd'] = None
        thermalLastCmd = jObj['runControl']['thermal_last_cmd']
        print(f"minerThermalControl runControl {jObj['runControl']}")
        if tCurrent <= tTarget - 2 and mStatus != MinerUtils.MinerStatus.MinerNormal and thermalLastCmd != 'RESUME':
            print(f"minerThermalControl Resume")
            jObj['runControl']['thermal_last_cmd'] = 'RESUME'
            event = {"action":"update","data":jObj}
            Utils.pubsub_instance.publish(Utils.PubSub.TOPIC_DATA_HAS_CHANGED, event)
            MinerWhatsminer.postResume(jObj)
            Utils.logger.info(f"MinerWhatsminer minerThermalControl {jObj['uuid']} Temperature too low {tTarget}/{tCurrent}ºC, mining started")
        elif tCurrent >= tTarget and mStatus == MinerUtils.MinerStatus.MinerNormal: 
            print(f"minerThermalControl status Pause")
            jObj['runControl']['thermal_last_cmd'] = 'PAUSE'
            event = {"action":"update","data":jObj}
            Utils.pubsub_instance.publish(Utils.PubSub.TOPIC_DATA_HAS_CHANGED, event)
            MinerWhatsminer.postPause(jObj)
            Utils.logger.warning(f"MinerWhatsminer minerThermalControl {jObj['uuid']} Temperature too high {tTarget}/{tCurrent}ºC, mining stopped")
        return None
    """
    MinerService END
    """