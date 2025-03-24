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

import socket
import json

class MinerBraiinsS9:

    lockServiceBosminer = Utils.threadingLock()
    lockFileBosminerToml = Utils.threadingLock()

    @staticmethod
    def cgMinerRequest(ip, command):
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
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object");
        Utils.jsonCheckKeyExists(jObj, 'STATUS', True) # based on return of Summary method
        if not isinstance(jObj['STATUS'], list) or len(jObj['STATUS']) == 0:
            Utils.throwExceptionInvalidValue("jObj['STATUS'] is not JSON Array");
        jAry = jObj['STATUS']
        Utils.jsonCheckKeyExists(jAry[0], 'STATUS', True)
        value = jAry[0]['STATUS']
        if not isinstance(value, str) or value.strip() != 'S':
            Utils.throwExceptionInvalidValue(f"cgMinerRequest response {jObj}");
        return jObj

    # Check if the miner is online
    @staticmethod
    def echo(jObj):
        MinerBraiinsS9.summary(jObj)
        return None

    @staticmethod
    def grpcConfig(jObj):
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object");
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'config')
    
    @staticmethod
    def grpcDevs(jObj):
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object");
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'devs')

    @staticmethod
    def grpcPools(jObj):
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object");
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'pools')

    @staticmethod
    def grpcStats(jObj):
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object");
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'stats')

    # from Braiins Summary command we know two JSON results as follow
    # OK: {"STATUS":[{"STATUS":"S","When":1742142723,"Code":11,"Msg":"Summary","Description":"BOSer boser-openwrt 0.1.0-26ba61b9"}],"SUMMARY":[{"Accepted":870,"Best Share":262144,"Device Hardware%":0.001495793976241377,"Device Rejected%":0.000010152599664517497,"Difficulty Accepted":228065280.0,"Difficulty Rejected":786432.0,"Difficulty Stale":0.0,"Discarded":0,"Elapsed":260281,"Found Blocks":0,"Get Failures":0,"Getworks":7165,"Hardware Errors":442,"Last getwork":1742142723,"Local Work":302879644,"MHS 15m":3902137.274920272,"MHS 1m":3888120.962872575,"MHS 24h":3901468.405107843,"MHS 5m":3877463.8022084557,"MHS 5s":4143268.055883251,"MHS av":3853538.4688909017,"Network Blocks":0,"Pool Rejected%":0.3436426116838488,"Pool Stale%":0.0,"Rejected":3,"Remote Failures":0,"Stale":0,"Total MH":1003005293182.8448,"Utility":0.20055247981988697,"Work Utility":54493.12380607131}]
    # Error: {"STATUS":[{"STATUS":"E","When":1742142791,"Code":23,"Msg":"Invalid JSON","Description":"BOSer boser-openwrt 0.1.0-26ba61b9"}]    
    @staticmethod
    def grpcSummary(jObj):
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object");
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'summary')

    @staticmethod
    def grpcVersion(jObj):
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object");
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'version')

    @staticmethod
    def httpHandlerGet(path, headers, jObj):        
        if path.endswith("/Generic"):
            sHeader: str = headers.get('command')
            if sHeader is None:
                Utils.throwExceptionHttpMissingHeader('command')
            print(sHeader)
            return MinerBraiinsS9.cgMinerRequest(jObj['ip'], sHeader), 200, 'application/json'
        if path.endswith("/Config"):
            return MinerBraiinsS9.sshConfigJsonStr(jObj), 200, 'application/json'
        elif path.endswith("/Devs"):
            return MinerBraiinsS9.grpcDevs(jObj), 200, 'application/json'
        elif path.endswith("/Pools"):
            return MinerBraiinsS9.grpcPools(jObj), 200, 'application/json'
        elif path.endswith("/Summary"):
            return MinerBraiinsS9.grpcSummary(jObj), 200, 'application/json'
        elif path.endswith("/Stats"):
            return MinerBraiinsS9.grpcStats(jObj), 200, 'application/json'
        elif path.endswith("/Restart"):
            return MinerBraiinsS9.sshRestart(jObj), 200, 'application/json'
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
        else:
            return 'Not found', 400, 'text/html'
    
    @staticmethod
    def httpHandlerPost(path, headers, jObj, contentStr):        
        if path.endswith("/Config"):
            return MinerBraiinsS9.sshConfigPostJsonStr(jObj, contentStr), 200, 'application/json'
        else:
            return 'Not found', 400, 'text/html'

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
    
    # Restart the BOSMiner service on the device
    @staticmethod
    def sshRestart(jObj):
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object");
        with Utils.lockServiceBosminer:
            MinerBraiinsS9.sshCommand(jObj, "/etc/init.d/bosminer restart")
        return Utils.resultJsonOK()
    
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

# Exemplo de uso com a string TOML fornecida
if __name__ == "__main__":
    # String TOML fornecida
    toml_string = """
[format]
version = '2.0'
model = 'Antminer S9'
generator = 'BOSer (boser-openwrt 0.1.0-26ba61b9)'
timestamp = 1742733351

[temp_control]
mode = 'manual'
hot_temp = 105.0
dangerous_temp = 110.0

[fan_control]
speed = 45
min_fans = 2

[[group]]
name = 'Default'

[[group.pool]]
enabled = true
url = 'stratum+tcp://mine.ocean.xyz:3334'
user = 'bc1q7e2tw0le8gxr4637kn0rncgvf48d45hysvy07k.kresnic'
password = 'x'

[[group.pool]]
enabled = true
url = 'stratum+tcp://eusolo.ckpool.org:3333'
user = 'bc1q7e2tw0le8gxr4637kn0rncgvf48d45hysvy07k.kresnic'
password = ''

[[group.pool]]
enabled = true
url = 'stratum2+tcp://v2.eu.stratum.braiins.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt'
user = 'igorbastosib.hauseheating'
password = '.~co?KmK[bB%Vl#7'

[autotuning]
enabled = true
power_target = 350
"""

    # Carregar da string
    config = BraiinsConfig.LoadFromStr(toml_string)
    print("Configuração carregada:")
    print(config.ToStr())

    # Criar uma nova instância e serializar
    config_manual = BraiinsConfig(
        format=Format("2.0", "Antminer S9", "BOSer (boser-openwrt 0.1.0-26ba61b9)", 1742733351),
        temp_control=TempControl("manual", 105.0, 110.0),
        fan_control=FanControl(45, 2),
        groups=[Group("Default", [
            Pool(True, "stratum+tcp://mine.ocean.xyz:3334", "bc1q7e2tw0le8gxr4637kn0rncgvf48d45hysvy07k.kresnic", "x"),
            Pool(True, "stratum+tcp://eusolo.ckpool.org:3333", "bc1q7e2tw0le8gxr4637kn0rncgvf48d45hysvy07k.kresnic", ""),
            Pool(True, "stratum2+tcp://v2.eu.stratum.braiins.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt", "igorbastosib.hauseheating", ".~co?KmK[bB%Vl#7")
        ])],
        autotuning=Autotuning(True, 350)
    )
    print("Configuração manual serializada:")
    print(config_manual.ToStr())