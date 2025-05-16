(heater_env) heatminer@heatminer:/heater$ grpcurl -plaintext -v -d '{"username": "root", "password": ""}' 192.168.178.184:50051 'braiins.bos.v1.AuthenticationService/Login' 2>&1 | grep authorization:
authorization: fioUmS7ahVC4OQ6K

grpcurl -plaintext -v -d '{"username": "root", "password": ""}' "minerIP":50051 'braiins.bos.v1.AuthenticationService/Login' 2>&1 | grep authorization:







import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from w1thermsensor import W1ThermSensor
import grpc
from bos.v1 import miner_pb2
from bos.v1 import miner_pb2_grpc
from bos.v1 import actions_pb2
from bos.v1 import actions_pb2_grpc

# Miner configuration
MINER_IP = "192.168.178.184:50051"
AUTH_TOKEN = "fioUmS7ahVC4OQ6K"  # Real token

def create_grpc_channel():
    """Create a gRPC channel without channel-level authentication."""
    return grpc.insecure_channel(MINER_IP)

async def read_temperature():
    """Read the temperature from the DS1820 sensor."""
    sensor = W1ThermSensor()
    try:
        temp = sensor.get_temperature()
        return round(temp, 2)
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return None

async def get_miner_status(stub):
    """Get the miner status with the token in metadata."""
    metadata = [('authorization', AUTH_TOKEN)]  # Or "Bearer {AUTH_TOKEN}" if needed
    try:
    response = stub.GetMinerDetails(miner_pb2.GetMinerDetailsRequest(), metadata=metadata)
        status = response.status
        return miner_pb2.MinerStatus.Name(status)  # Return the status name (e.g., "MINER_STATUS_NORMAL")
    except grpc.RpcError as e:
        print(f"Error retrieving status: {e}")
        return None

async def execute_miner_action(stub, action, action_name):
    """Execute an action on the miner with the token in metadata."""
    metadata = [('authorization', AUTH_TOKEN)]  # Or "Bearer {AUTH_TOKEN}" if needed
    try:
        if action == "start":
            response = stub.Start(actions_pb2.StartRequest(), metadata=metadata)
        elif action == "stop":
            response = stub.Stop(actions_pb2.StopRequest(), metadata=metadata)
        print(f"Action '{action_name}' executed successfully.")
    except grpc.RpcError as e:
        print(f"Error during action '{action_name}': {e}")

async def thermal_control(temp, target_temp):
    if temp is None:
        return

    channel = create_grpc_channel()
    miner_stub = miner_pb2_grpc.MinerServiceStub(channel)
    actions_stub = actions_pb2_grpc.ActionsServiceStub(channel)

    current_status = await get_miner_status(miner_stub)
    if current_status is None:
        print("Unable to retrieve miner status.")
        channel.close()
        return
    print(f"Miner Status: {current_status}")

    if temp <= target_temp - 2 and current_status != "MINER_STATUS_NORMAL":
        await execute_miner_action(actions_stub, "start", "start mining")
        print("Temperature too low: Mining started")
    elif temp >= target_temp:
        await execute_miner_action(actions_stub, "stop", "stop mining")
        print("Temperature OK: Mining stopped")

    channel.close()

async def main():
    target_temp = float(input("Target temperature: "))

    while True:
        temp = await read_temperature()
        if temp is not None:
            print(f"Temperature: {temp:.2f}°C")
            await thermal_control(temp, target_temp)
        else:
            print("Unable to read temperature.")
        await asyncio.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    asyncio.run(main())

