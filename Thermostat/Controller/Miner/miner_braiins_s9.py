"""
Official docs followed to create this class
https://academy.braiins.com/en/braiins-os/papi-bosminer/
https://github.com/ckolivas/cgminer/blob/master/API-README

S9 over SSH
https://github.com/UpstreamData/pyasic/blob/master/pyasic/miners/backends/braiins_os.py#L112-L675
https://github.com/UpstreamData/pyasic/blob/master/pyasic/ssh/braiins_os.py
https://github.com/UpstreamData/pyasic/blob/master/pyasic/ssh/base.py

This file works with the gRPC API which can be found on Official Docs and SSH
the gRPC API has only few "GET" metohds and a couple of "POST" ones
"""

from ..utils import Utils
from .miner_utils import MinerUtils

import json
import socket
import time

class MinerBraiinsS9(MinerUtils.MinerBase):

    lockServiceBosminer = Utils.threadingLock()
    lockFileBosminerToml = Utils.threadingLock()

    @staticmethod
    def cgMinerRequest(ip, command, isCheckResponse: bool = True):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, 4028))
        sock.sendall(json.dumps({"command": command}).encode('utf-8'))
        response = ""
        while True:
            data = sock.recv(4096).decode('utf-8')
            if not data:
                break
            response += data
        sock.close()
        # print(f"{response}")
        jObj = json.loads(response.replace('\x00', ''))
        if isCheckResponse:
            MinerBraiinsS9.cgCheckStatusResponse(jObj)
        return jObj

    # Check if the gRPC status response is STATUS=S, raise exception if find anything wrong
    @staticmethod
    def cgCheckStatusResponse(jObj):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyExists(jObj, 'STATUS', True) # based on return of Summary method
        if not isinstance(jObj['STATUS'], list) or len(jObj['STATUS']) == 0:
            Utils.throwExceptionInvalidValue("jObj['STATUS'] is not JSON Array")
        jAry = jObj['STATUS']
        Utils.jsonCheckKeyExists(jAry[0], 'STATUS', True)
        value = jAry[0]['STATUS']
        if not isinstance(value, str) or value.strip() != 'S':
            Utils.throwExceptionInvalidValue(f"cgMinerRequest response {jObj}")
        return None
    """
    All gRPC methods
    """
    @staticmethod
    def grpcAscconut(jObj):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'asccount')

    @staticmethod
    def grpcConfig(jObj):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'config')

    @staticmethod
    def grpcDevDetails(jObj):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'devdetails')

    @staticmethod
    def grpcDevs(jObj, isOnlyData: bool = False):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        jR = MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'devs')
        if isOnlyData:
            jR = jR['DEVS']
        return jR

    @staticmethod
    def grpcFans(jObj, isOnlyData: bool = False):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        jR = MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'fans')
        if isOnlyData:
            jR = jR['FANS']
        return jR

    @staticmethod
    def grpcPause(jObj):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'pause')

    @staticmethod
    def grpcPools(jObj):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'pools')

    @staticmethod
    def grpcResume(jObj):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'resume')

    @staticmethod
    def grpcStats(jObj):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'stats')

    # from Braiins Summary command we know two JSON results as follow
    # OK: {"STATUS":[{"STATUS":"S","When":1742142723,"Code":11,"Msg":"Summary","Description":"BOSer boser-openwrt 0.1.0-26ba61b9"}],"SUMMARY":[{"Accepted":870,"Best Share":262144,"Device Hardware%":0.001495793976241377,"Device Rejected%":0.000010152599664517497,"Difficulty Accepted":228065280.0,"Difficulty Rejected":786432.0,"Difficulty Stale":0.0,"Discarded":0,"Elapsed":260281,"Found Blocks":0,"Get Failures":0,"Getworks":7165,"Hardware Errors":442,"Last getwork":1742142723,"Local Work":302879644,"MHS 15m":3902137.274920272,"MHS 1m":3888120.962872575,"MHS 24h":3901468.405107843,"MHS 5m":3877463.8022084557,"MHS 5s":4143268.055883251,"MHS av":3853538.4688909017,"Network Blocks":0,"Pool Rejected%":0.3436426116838488,"Pool Stale%":0.0,"Rejected":3,"Remote Failures":0,"Stale":0,"Total MH":1003005293182.8448,"Utility":0.20055247981988697,"Work Utility":54493.12380607131}]
    # Error: {"STATUS":[{"STATUS":"E","When":1742142791,"Code":23,"Msg":"Invalid JSON","Description":"BOSer boser-openwrt 0.1.0-26ba61b9"}]    
    @staticmethod
    def grpcSummary(jObj):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'summary')

    @staticmethod
    def grpcTemps(jObj, isOnlyData: bool = False):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        jR = MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'temps', isOnlyData)
        if isOnlyData:
            jR = jR['TEMPS']
        return jR

    @staticmethod
    def grpcTunerStatus(jObj):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'tunerstatus')

    @staticmethod
    def grpcVersion(jObj):
        Utils.jsonCheckIsObj(jObj)
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'version')
    """
    All gRPC methods END
    """

    """
    HTTP handler
    """
    @staticmethod
    def httpHandlerGet(path, headers, jObj):        
        if path.endswith("/Generic"):
            sHeader: str = headers.get('command')
            if sHeader is None:
                Utils.throwExceptionHttpMissingHeader('command')
            return MinerBraiinsS9.cgMinerRequest(jObj['ip'], sHeader), 200, 'application/json'
        elif path.endswith("/Config"):
            return MinerBraiinsS9.sshConfigJsonStr(jObj), 200, 'application/json'
        elif path.endswith("/Devs"):
            return MinerBraiinsS9.grpcDevs(jObj), 200, 'application/json'
        elif path.endswith("/Fans"):
            return MinerBraiinsS9.grpcFans(jObj), 200, 'application/json'
        elif path.endswith("/Pause"):
            return MinerBraiinsS9.grpcPause(jObj), 200, 'application/json'
        elif path.endswith("/Pools"):
            return MinerBraiinsS9.grpcPools(jObj), 200, 'application/json'
        elif path.endswith("/Restart"):
            return MinerBraiinsS9.sshRestart(jObj), 200, 'application/json'
        elif path.endswith("/Resume"):
            return MinerBraiinsS9.grpcResume(jObj), 200, 'application/json'
        elif path.endswith("/Summary"):
            return MinerBraiinsS9.grpcSummary(jObj), 200, 'application/json'
        elif path.endswith("/Stats"):
            return MinerBraiinsS9.grpcStats(jObj), 200, 'application/json'
        elif path.endswith("/Temps"):
            return MinerBraiinsS9.grpcTemps(jObj), 200, 'application/json'
        elif path.endswith("/TunerStatus"):
            return MinerBraiinsS9.grpcTunerStatus(jObj), 200, 'application/json'
        elif path.endswith("/Version"):
            return MinerBraiinsS9.grpcVersion(jObj), 200, 'application/json'
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
            return MinerBraiinsS9.sshConfigPostJsonStr(jObj, contentStr), 200, 'application/json'
        else:
            return 'Not found', 400, 'text/html'
    """
    HTTP handler END
    """

    """
    All SSH methods
    """
    # Returns the bosminer.toml as string
    @staticmethod
    def sshConfig(jObj: dict):
        with MinerBraiinsS9.lockFileBosminerToml:
            return MinerBraiinsS9.sshCommand(jObj, "cat /etc/bosminer.toml")
    @staticmethod
    def sshConfigJsonStr(jObj: dict):
        tomlStr = MinerBraiinsS9.sshConfig(jObj)
        config = BraiinsConfig.load_from_str(tomlStr)
        return config.to_json()
    @staticmethod
    def sshConfigPostJsonStr(jObj: dict, json: str):
        config = BraiinsConfig.load_json_str(json)
        config.save(jObj['ip'], jObj['username'], jObj['password'])
        return  Utils.resultJsonOK()
        
    @staticmethod
    def sshCommand(jObj: dict, cmd: str):
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        Utils.jsonCheckKeyTypeStr(jObj, 'username', True, False)
        Utils.jsonCheckKeyTypeStr(jObj, 'password', True, False)
        return Utils.sshExecCommand(jObj['ip'], jObj['username'], jObj['password'], cmd)
 
    @staticmethod
    def sshDisablePool(jObj, index: int):
        tomlStr = MinerBraiinsS9.sshConfig(jObj)
        config = BraiinsConfig.load_from_str(tomlStr)
        config.groups[0].pools[index].enabled = False
        config.save(jObj['ip'], jObj['username'], jObj['password'])
        with MinerBraiinsS9.lockFileBosminerToml:
            tomlStr = MinerBraiinsS9.sshCommand(jObj, "cat /etc/bosminer.toml")
        return Utils.resultJsonOK()
    
    # Turns ON/OFF the fault light (warning...)
    @staticmethod
    def sshFaultLight(jObj, isEnabled: bool):
        Utils.jsonCheckIsObj(jObj)
        with MinerBraiinsS9.lockServiceBosminer:
            if isEnabled:
                MinerBraiinsS9.sshCommand(jObj, "miner fault_light on")
            else:
                MinerBraiinsS9.sshCommand(jObj, "miner fault_light off")
        return Utils.resultJsonOK()
    
    # Restart the BOSMiner service on the device
    @staticmethod
    def sshRestart(jObj):
        Utils.jsonCheckIsObj(jObj)
        with MinerBraiinsS9.lockServiceBosminer:
            MinerBraiinsS9.sshCommand(jObj, "/etc/init.d/bosminer restart")
        return Utils.resultJsonOK()

    @staticmethod
    def sshUpTime(jObj) -> int:
        """
        Returns:
            Int, started time in seconds
        """
        Utils.jsonCheckIsObj(jObj)
        with MinerBraiinsS9.lockServiceBosminer:
            startedTime = MinerBraiinsS9.sshCommand(jObj, "cat /proc/uptime | cut -d' ' -f1 | cut -d'.' -f1")
        return int(startedTime)
    """
    All SSH methods END
    """

    """
    Inherited methods
    """
    # Check if the miner is online, raises exception if NOT
    @classmethod
    def echo(cls, jObj):
        # gRPC test
        MinerBraiinsS9.grpcStats(jObj)
        return None
    @classmethod
    def getToken(cls, jObj):
        MinerBraiinsS9.sshConfig(jObj)
        return None
    @classmethod
    def pause(cls, jObj):
        return MinerBraiinsS9.grpcPause(jObj)
    @classmethod
    def reboot(cls, jObj):
        return MinerBraiinsS9.sshRestart(jObj)
    @classmethod
    def resume(cls, jObj):
        return MinerBraiinsS9.grpcResume(jObj)
    # In case miner is paused, grpcTemps returns "Not Ready"
    @classmethod
    def status(cls, jObj):
        jTemp = MinerBraiinsS9.grpcTemps(jObj, False)
        Utils.jsonCheckIsObj(jTemp, True)
        Utils.jsonCheckKeyExists(jTemp, 'STATUS', True)
        if not isinstance(jTemp['STATUS'], list) or len(jTemp['STATUS']) == 0:
            Utils.throwExceptionInvalidValue("jObj['STATUS'] is not JSON Array")
        jAry = jTemp['STATUS']
        if Utils.jsonCheckKeyExists(jAry[0], 'STATUS', False) and jAry[0]['STATUS'] == 'S':
            return MinerUtils.MinerStatus.MinerNormal
        elif Utils.jsonCheckKeyExists(jAry[0], 'Msg', False) and jAry[0]['Msg'] == 'Not ready':
            return MinerUtils.MinerStatus.MinerNotReady
        else:
            return MinerUtils.MinerStatus.MinerUnknown
    """
    Inherited methods
    """

    """
    All Thermine methods END
    """
    @staticmethod
    def summary(jObj):
        json_str = MinerBraiinsS9.sshConfigJsonStr(jObj)
        jConfig = json.loads(json_str)
        
        jReturn = {}
        
        # Config
        jGroup1 = {}
        jReturn['config'] = jGroup1
        # Temp
        jGroup2 = {}
        jGroup2['hot'] = jConfig['temp_control']['hot_temp']
        jGroup2['dangerous'] = jConfig['temp_control']['dangerous_temp']
        jGroup1['temp'] = jGroup2
        # Fans
        jGroup2 = {}
        jGroup2['speed'] = jConfig['fan_control']['speed']
        jGroup2['count'] = jConfig['fan_control']['min_fans']
        jGroup1['fans'] = jGroup2
        # Autotuning
        if Utils.jsonCheckKeyExists(jConfig, 'autotuning', False):
            jGroup2 = {}
            jGroup2['autoTuningEnabled'] = jConfig['autotuning']['enabled']
            jGroup2['target'] = jConfig['autotuning']['power_target']
            jGroup1['power'] = jGroup2

        # Data
        jGroup1 = {}
        jReturn['data'] = jGroup1
        jGroup1['pool'] = jConfig['group']
        jGroup1['board'] = []
        # Data - ASIC
        jGrpc = MinerBraiinsS9.grpcDevs(jObj, True)
        for item in jGrpc:
            jGroup2 = {}
            jGroup2['id'] = item['ID']
            jGroup2['enabled'] = item['Enabled']
            jGroup2['status'] = item['Status']
            jGroup2['hr5s'] = item['MHS 5s']
            jGroup1['board'].append(jGroup2)
        # Data - ASIC temp
        jGrpc = MinerBraiinsS9.grpcTemps(jObj, True)
        for item1 in jGroup1['board']:
            for item2 in jGrpc:
                if item1['id'] == item2['ID']:
                    item1['tempBoard'] = item2['Board']
                    item1['tempChip'] = item2['Chip']
                    jGrpc.remove(item2)
                    break

        return jReturn
    """
    All Thermine methods END
    """

    """
    MinerService
    """
    # Get data from miner and save it locally
    @classmethod
    def minerServiceGetData(cls, jObj):
        try: # Hashrate(MHs)
            jObjRtr = MinerBraiinsS9.grpcSummary(jObj)
            MinerBraiinsS9.cgCheckStatusResponse(jObjRtr)
            hashRate = 0.0
            for jObjS in jObjRtr['SUMMARY']:
                hashRate = hashRate + jObjS['MHS 5s']
            hashRate = round((hashRate/1000)/1000,4)
            Utils.dataBinaryWriteFile(Utils.pathDataMinerHashrate(jObj), [hashRate])
        except Exception as e:
            Utils.logger.error(f"BraiinsS9 minerServiceGetData hashrate {jObj['uuid']} error {e}")

        if MinerBraiinsS9.status(jObj) == MinerUtils.MinerStatus.MinerNormal:        
            try: # Temp
                jObjRtr = MinerBraiinsS9.grpcTemps(jObj)
                MinerBraiinsS9.cgCheckStatusResponse(jObjRtr)
                tBoard = 0.0
                tChip = 0.0
                if len(jObjRtr['TEMPS']) > 0:
                    for jObjS in jObjRtr['TEMPS']:
                        tBoard = tBoard + jObjS['Board']
                        tChip = tChip + jObjS['Chip']
                    tBoard = round(tBoard / len(jObjRtr['TEMPS']),4)
                    tChip = round(tChip / len(jObjRtr['TEMPS']),4)
                    Utils.dataBinaryWriteFile(Utils.pathDataMinerTemp(jObj), [tBoard, tChip])
            except Exception as e:
                Utils.logger.error(f"BraiinsS9 minerServiceGetData temp {jObj['uuid']} error {e}")
        return Utils.resultJsonOK()

    @classmethod
    def minerThermalControl(cls, jObj: dict, tCurrent: float): # tCurrent=current temperature, from miner OR sensor
        if Utils.jsonCheckKeyExists(jObj, 'sensor', False):
            tTarget = float(jObj['sensor']['temp_target'])
        else:
            jConfig = json.loads(MinerBraiinsS9.sshConfigJsonStr(jObj))
            Utils.jsonCheckKeyExists(jConfig, 'temp_control', True)
            Utils.jsonCheckKeyExists(jConfig['temp_control'], 'hot_temp', True)
            tTarget = float(jConfig['temp_control']['hot_temp'])

        mStatus = MinerBraiinsS9.status(jObj)

        if tCurrent >= tTarget:
            if mStatus == MinerUtils.MinerStatus.MinerNormal:
                MinerBraiinsS9.grpcPause(jObj)
                Utils.logger.warning(f"MinerBraiinsS9.minerThermalControl {jObj['uuid']} Pausing, Temperature to high: Target {tTarget} Current {tCurrent}")
            return
        if tCurrent <= tTarget-2 and mStatus == MinerUtils.MinerStatus.MinerNotReady:
            MinerBraiinsS9.sshRestart(jObj)
            Utils.logger.warning(f"MinerBraiinsS9.minerThermalControl {jObj['uuid']} Restarting, Temperature to low: Target {tTarget} Current {tCurrent}")
            # loop 5min or till the miner is OK
            started = time.time()
            time30s = started
            while (time.time() - started) < (5 * 60): # 5 min looping
                if MinerBraiinsS9.status(jObj) == MinerUtils.MinerStatus.MinerNormal:
                    break
                if (time.time() - time30s) >= 30: # every 30 secs
                    time30s = time.time()
                    Utils.logger.warning(f"MinerBraiinsS9.minerThermalControl {jObj['uuid']} restarted, waiting status NORMAL")
                time.sleep(5) # wait 5 secs till next verification
            return
        return
    """
    MinerService END
    """
    
# Classes to manage SSH files bosminer.toml
import toml
from collections import OrderedDict
from typing import List, Optional

class Format:
    def __init__(self, version: str, model: str, generator: str, timestamp: int):
        self.version = version
        self.model = model
        self.generator = generator
        self.timestamp = timestamp

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "model": self.model,
            "generator": self.generator,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(data: dict) -> 'Format':
        return Format(
            version=data["version"],
            model=data["model"],
            generator=data["generator"],
            timestamp=data["timestamp"]
        )

class TempControl:
    def __init__(self, mode: str, hot_temp: float, dangerous_temp: float):
        self.mode = mode
        self.hot_temp = hot_temp
        self.dangerous_temp = dangerous_temp

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "hot_temp": self.hot_temp,
            "dangerous_temp": self.dangerous_temp
        }

    @staticmethod
    def from_dict(data: dict) -> 'TempControl':
        return TempControl(
            mode=data["mode"],
            hot_temp=data["hot_temp"],
            dangerous_temp=data["dangerous_temp"]
        )

class FanControl:
    def __init__(self, speed: int, min_fans: int):
        self.speed = speed
        self.min_fans = min_fans

    def to_dict(self) -> dict:
        return {
            "speed": self.speed,
            "min_fans": self.min_fans
        }

    @staticmethod
    def from_dict(data: dict) -> 'FanControl':
        return FanControl(
            speed=data["speed"],
            min_fans=data["min_fans"]
        )

class Pool:
    def __init__(self, enabled: bool, url: str, user: str, password: str):
        self.enabled = enabled
        self.url = url
        self.user = user
        self.password = password

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "url": self.url,
            "user": self.user,
            "password": self.password
        }

    @staticmethod
    def from_dict(data: dict) -> 'Pool':
        return Pool(
            enabled=data["enabled"],
            url=data["url"],
            user=data["user"],
            password=data["password"]
        )

class Group:
    def __init__(self, name: str, pools: List[Pool]):
        self.name = name
        self.pools = pools

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "pool": [pool.to_dict() for pool in self.pools]
        }

    @staticmethod
    def from_dict(data: dict) -> 'Group':
        return Group(
            name=data["name"],
            pools=[Pool.from_dict(pool) for pool in data["pool"]]
        )

class Autotuning:
    def __init__(self, enabled: bool, power_target: int):
        self.enabled = enabled
        self.power_target = power_target

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "power_target": self.power_target
        }

    @staticmethod
    def from_dict(data: dict) -> 'Autotuning':
        return Autotuning(
            enabled=data["enabled"],
            power_target=data["power_target"]
        )

class BraiinsConfig:
    def __init__(
        self,
        format: Format,
        temp_control: TempControl,
        fan_control: FanControl,
        groups: List[Group],
        autotuning: Autotuning
    ):
        self.format = format
        self.temp_control = temp_control
        self.fan_control = fan_control
        self.groups = groups
        self.autotuning = autotuning

    def save(self, ip: str, user: str, pwrd: str, filepath: str = "/etc/bosminer.toml"):
        toml_str = self.to_str()
        toml_str = toml_str.replace('"', '\\"').replace('\n', '\\n')
        cmd = f'echo -e "{toml_str}" > {filepath}'
        return Utils.sshExecCommand(ip, user, pwrd, cmd)

    def to_dict(self) -> dict:
        """Serialize to TOML format"""
        return {
            "format": self.format.to_dict(),
            "temp_control": self.temp_control.to_dict(),
            "fan_control": self.fan_control.to_dict(),
            "group": [group.to_dict() for group in self.groups],
            "autotuning": self.autotuning.to_dict()
        }
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    def to_str(self) -> str:
        return toml.dumps(self.to_dict())

    # Load from TOML string
    @staticmethod
    def load_from_str(toml_str: str) -> 'BraiinsConfig':
        data = toml.loads(toml_str)
        return BraiinsConfig(
            format=Format.from_dict(data["format"]),
            temp_control=TempControl.from_dict(data["temp_control"]),
            fan_control=FanControl.from_dict(data["fan_control"]),
            groups=[Group.from_dict(group) for group in data["group"]],
            autotuning=Autotuning.from_dict(data["autotuning"])
        )
    @staticmethod
    def load_json_str(json_str: str) -> 'BraiinsConfig':
        data = json.loads(json_str)
        return BraiinsConfig(
            format=Format.from_dict(data["format"]),
            temp_control=TempControl.from_dict(data["temp_control"]),
            fan_control=FanControl.from_dict(data["fan_control"]),
            groups=[Group.from_dict(group) for group in data["group"]],
            autotuning=Autotuning.from_dict(data["autotuning"])
        )