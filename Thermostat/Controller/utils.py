import json
import os
import time
import uuid
import threading

lockFileConfigThermine = threading.Lock()

# Returns the thermine_config.uuid value (may be create a file for this stuff?)
def thermineUuid():
    path_config = pathConfigThermine()
    with lockFileConfigThermine:
        with open(path_config, 'r', encoding='utf-8') as file:
            jObj = json.load(file)
    if jObj.get('uuid') is None or jObj.get('uuid').strip() == '':
        jObj['uuid'] = uuidRandom()
        with lockFileConfigThermine:
            with open(path_config, 'w', encoding='utf-8') as file:
                json.dump(jObj, file, ensure_ascii=False, indent=2)
    jObjReturn = {"uuid":jObj['uuid']}
    return json.dumps(jObjReturn)

# Returns current date time in timestamp UTC
def nowUtc():
    current_time = time.time()
    return int(current_time)

# Returns the config path, creates if doesn't exist
def pathConfig():
    path_config = os.path.join(pathCurrent(),'config')
    if not os.path.exists(path_config):
        os.makedirs(path_config)
    return path_config


# Returns the thermine_config.json path, creates if doesn't exist
def pathConfigThermine():
    path_config = os.path.join(pathConfig(), 'thermine_config.json')
    if not os.path.exists(path_config):
        jObj = {"version":1}
        with open(path_config, 'w', encoding='utf-8') as file:
            json.dump(jObj, file, ensure_ascii=False, indent=2)
    return path_config

# Returns the current .py path is running from
def pathCurrent():
    return os.path.join(os.getcwd(), 'heater_control')

# Returns a random UUID
def uuidRandom():
    return str(uuid.uuid4())