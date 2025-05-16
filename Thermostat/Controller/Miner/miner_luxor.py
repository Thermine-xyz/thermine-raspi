"""
Official doc https://docs.luxor.tech/docs/firmware/api/intro
It uses CGMiner API integration https://github.com/ckolivas/cgminer/blob/master/API-README
"""
from ..utils import Utils
from .miner_utils import MinerUtils

import asyncio
import json

class MinerLuxor(MinerUtils.MinerBase):
    """
    All CGMiner methods
    """
    @staticmethod
    async def sendCommand(jObj, command):
        """
        Send a JSON command to the miner over TCP and return the response.
        
        Args:
            ip (str): Miner IP address
            port (int): Miner port (e.g., 4028)
            command (dict): Command in JSON format
        
        Returns:
            dict: Response from the miner, or None if an error occurs
        """
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        try:
            reader, writer = await asyncio.open_connection(jObj['ip'], 4028)
            writer.write(json.dumps(command).encode() + b"\n")
            await writer.drain()
            data = await reader.read(4096)  # Buffer size for response
            writer.close()
            await writer.wait_closed()
            return json.loads(data.decode())
        except Exception as e:
            print(f"Error connecting to {ip}:{port} - {e}")
            return None

    @staticmethod
    def cgmCommand(jObj, command):
        if isinstance(command, str):
            response = MinerLuxor.sendCommand(jObj, {"command": command})
        elif isinstance(command, dict):
            response = MinerLuxor.sendCommand(jObj, command)
        else:
            Utils.throwExceptionInvalidValue(f"LUXminer wrong cgmCommand: {command}")
        Utils.jsonCheckIsObj(response)
        Utils.jsonCheckKeyExists(response, 'STATUS', True)
        Utils.jsonCheckIsAry(response['STATUS'])
        Utils.jsonCheckKeyTypeStr(response['STATUS'][0], 'STATUS', True, False)
        if not response['STATUS'][0]['STATUS'].strip() == 'S':
            Utils.throwExceptionInvalidValue(f"LUXminer wrong status: {response['STATUS']}")
        return response

    @staticmethod
    def cgmConfig(jObj):
        jR = MinerLuxor.cgmCommand(jObj, 'config')
        Utils.jsonCheckKeyExists(jR, 'CONFIG', True)
        Utils.jsonCheckIsAry(jR['CONFIG'])
        return jR
    @staticmethod
    def cgmCurtail(jObj, action):
        sessionId = MinerLuxor.cgmSessionId(jObj)
        command = { "command" : "curtail", "parameter" : sessionId + "," + action }
        jR = MinerLuxor.cgmCommand(jObj, command)
        Utils.jsonCheckKeyExists(jR, 'CURTAIL', True)
        return jR
    @staticmethod
    def cgmSessionId(jObj):
        jR = MinerLuxor.cgmCommand(jObj, 'session')
        Utils.jsonCheckKeyExists(jR, 'SESSION', True)
        Utils.jsonCheckKeyTypeStr(jR['SESSION'][0], 'SessionID', True, False)    
        return jR
    @staticmethod
    def cgmSummary(jObj):
        jR = MinerLuxor.cgmCommand(jObj, 'summary')
        Utils.jsonCheckKeyExists(jR, 'SUMMARY', True)
        return jR
    @staticmethod
    def cgmTempctrl(jObj):
        jR = MinerLuxor.cgmCommand(jObj, 'tempctrl')
        Utils.jsonCheckKeyExists(jR, 'TEMPCTRL', True)
        return jR
    @staticmethod
    def cgmTemps(jObj):
        jR = MinerLuxor.cgmCommand(jObj, 'temps')
        Utils.jsonCheckKeyExists(jR, 'TEMPS', True)
        return jR
    @staticmethod
    def cgmVersion(jObj):
        jR = MinerLuxor.cgmCommand(jObj, 'version')
        Utils.jsonCheckKeyExists(jR, 'VERSION', True)
        return jR
    """
    All CGMiner methods END
    """

    """
    Inherited methods
    """
    @classmethod
    def echo(cls, jObj):
        # luxor CGHMiner version 3.7 expects STATUS and VERSION array
        jR = MinerLuxor.cgmVersion(jObj)
        Utils.jsonCheckKeyTypeStr(jR['STATUS'][0], 'Msg', True, False)
        if not jR['STATUS'][0].lower().startswith('luxminer'): # Luxor replies a specific Msg value "LUXminer versions"
            Utils.throwExceptionInvalidValue(f"Miner is not LUXminer: {jR['STATUS'][0]['Msg']}")
        return None
    # Check if the miner is online, raises exception if NOT
    @classmethod
    def getToken(cls, jObj):
        # luxor CGHMiner version 3.7 expects STATUS and VERSION array
        jR = MinerLuxor.cgmSessionId(jObj)
        return {"SessionID": jR['SESSION'][0]['SessionID']}
    @classmethod
    def status(cls, jObj):
        jR = MinerLuxor.cgmConfig(jObj)
        jAry = jR['CONFIG']
        if not Utils.jsonCheckKeyExists(jAry[0], 'CurtailMode', False):
            return MinerUtils.MinerStatus.MinerUnknown
        if jAry[0]['CurtailMode'] == 'WakeUp':
            return MinerUtils.MinerStatus.MinerNormal
        elif jAry[0]['Msg'] == 'Sleep':
            return MinerUtils.MinerStatus.MinerNotReady
        else:
            return MinerUtils.MinerStatus.MinerUnknown
    """
    Inherited methods END
    """

    """
    All Thermine methods
    here are all methods that manage data to return default JSONs for the API
    """
    @staticmethod
    def pause(jObj):
        return MinerLuxor.cgmCurtail(jObj, 'sleep')
    @staticmethod
    def resume(jObj):
        return MinerLuxor.cgmCurtail(jObj, 'wakeup')
    """
    All Thermine methods END
    """

    """
    MinerService
    """
    # Get data from miner and save it locally
    @classmethod
    def minerServiceGetData(cls, jObj):
        if MinerLuxor.status(jObj) == MinerUtils.MinerStatus.MinerNormal:
            try: # Hashrate(MHs)
                jObjRtr = MinerLuxor.cgmSummary(jObj)
                hashRate = 0.0
                for jObjS in jObjRtr['SUMMARY']:
                    hashRate = hashRate + jObjS['GHS 5s']
                hashRate = round(hashRate/1000,4) #convert from G to T
                path = Utils.pathDataMinerHashrate(jObj)
                lock = Utils.getFileLock(path).gen_wlock() # lock for reading, method "wlock"
                with lock:
                    with open(path, 'a', encoding='utf-8') as file:
                        file.write(f"{Utils.nowUtc()};{hashRate}\n")
            except Exception as e:
                Utils.logger.error(f"MinerLuxor minerServiceGetData hashrate {jObj['uuid']} error {e}")
            try: # Temp
                jObjRtr = MinerLuxor.cgmTemps(jObj)
                MinerBraiinsS9.cgCheckStatusResponse(jObjRtr)
                temp = 0.0
                if len(jObjRtr['TEMPS']) > 0:
                    temp1 = 0.0
                    for jObjS in jObjRtr['TEMPS']:
                        temp1 = jObjS['BottomLeft'] + jObjS['BottomRight'] + jObjS['TopLeft'] + jObjS['TopRight']
                    temp = temp + (temp1/4)
                    temp = round(temp / len(jObjRtr['TEMPS']),4)
                    path = Utils.pathDataMinerTemp(jObj)
                    lock = Utils.getFileLock(path).gen_wlock() # lock for reading, method "wlock"
                    with lock:
                        with open(path, 'a', encoding='utf-8') as file:
                            file.write(f"{Utils.nowUtc()};{temp}\n")
            except Exception as e:
                Utils.logger.error(f"MinerLuxor minerServiceGetData temp {jObj['uuid']} error {e}")
    @classmethod
    def minerThermalControl(cls, jObj: dict, tCurrent: float): # tCurrent=current temperature, from miner OR sensor
        if Utils.jsonCheckKeyExists(jObj, 'sensor', False):
            tTarget = float(jObj['sensor']['temp_target'])
        else:
            jConfig = MinerLuxor.cgmTempctrl(jObj)
            Utils.jsonCheckKeyExists(jConfig, 'ChipHot', True)
            tTarget = float(jConfig['ChipHot'])

        mStatus = MinerLuxor.status(jObj)

        if tCurrent >= tTarget:
            MinerLuxor.pause(jObj)
            Utils.logger.warning(f"MinerLuxor.minerThermalControl {jObj['uuid']} Pausing, Temperature to high: Target {tTarget} Current {tCurrent}")
            return
        if tCurrent <= tTarget-2 and mStatus == MinerUtils.MinerStatus.MinerNotReady:
            MinerLuxor.resume(jObj)
            Utils.logger.warning(f"MinerLuxor.minerThermalControl {jObj['uuid']} Restarting, Temperature to low: Target {tTarget} Current {tCurrent}")
            # loop 5min or till the miner is OK
            started = time.time()
            time30s = started
            while (time.time() - started) < (5 * 60): # 5 min looping
                if MinerLuxor.status(jObj) == MinerUtils.MinerStatus.MinerNormal:
                    break
                if (time.time() - time30s) >= 30: # every 30 secs
                    time30s = time.time()
                    Utils.logger.warning(f"MinerLuxor.minerThermalControl {jObj['uuid']} restarted, waiting status NORMAL")
                time.sleep(5) # wait 5 secs till next verification
            return
        return
    """
    MinerService END
    """