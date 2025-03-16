from ..utils import Utils

import socket
import json

class MinerBraiinsS9:
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
        MinerBraiinsS9.summaryS9(jObj)
        return None
    
    # from Braiins Summary command we know two JSON results as follow
    # OK: {"STATUS":[{"STATUS":"S","When":1742142723,"Code":11,"Msg":"Summary","Description":"BOSer boser-openwrt 0.1.0-26ba61b9"}],"SUMMARY":[{"Accepted":870,"Best Share":262144,"Device Hardware%":0.001495793976241377,"Device Rejected%":0.000010152599664517497,"Difficulty Accepted":228065280.0,"Difficulty Rejected":786432.0,"Difficulty Stale":0.0,"Discarded":0,"Elapsed":260281,"Found Blocks":0,"Get Failures":0,"Getworks":7165,"Hardware Errors":442,"Last getwork":1742142723,"Local Work":302879644,"MHS 15m":3902137.274920272,"MHS 1m":3888120.962872575,"MHS 24h":3901468.405107843,"MHS 5m":3877463.8022084557,"MHS 5s":4143268.055883251,"MHS av":3853538.4688909017,"Network Blocks":0,"Pool Rejected%":0.3436426116838488,"Pool Stale%":0.0,"Rejected":3,"Remote Failures":0,"Stale":0,"Total MH":1003005293182.8448,"Utility":0.20055247981988697,"Work Utility":54493.12380607131}]
    # Error: {"STATUS":[{"STATUS":"E","When":1742142791,"Code":23,"Msg":"Invalid JSON","Description":"BOSer boser-openwrt 0.1.0-26ba61b9"}]    
    @staticmethod
    def summaryS9(jObj):
        if not isinstance(jObj, dict):
            Utils.throwExceptionInvalidValue("jObj is not JSON Object");
        Utils.jsonCheckKeyTypeStr(jObj, 'ip', True, False)
        return MinerBraiinsS9.cgMinerRequest(jObj['ip'], 'summary')