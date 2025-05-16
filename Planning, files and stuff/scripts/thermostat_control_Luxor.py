import asyncio
import json

# Miner configuration (replace with your miner's IP)
MINER_IP = "192.168.178.184"
MINER_PORT = 4028  # Standard port for CGMiner-like APIs

async def send_command(ip, port, command):
    """
    Send a JSON command to the miner over TCP and return the response.
    
    Args:
        ip (str): Miner IP address
        port (int): Miner port (e.g., 4028)
        command (dict): Command in JSON format
    
    Returns:
        dict: Response from the miner, or None if an error occurs
    """
    try:
        reader, writer = await asyncio.open_connection(ip, port)
        writer.write(json.dumps(command).encode() + b"\n")
        await writer.drain()
        data = await reader.read(4096)  # Buffer size for response
        writer.close()
        await writer.wait_closed()
        return json.loads(data.decode())
    except Exception as e:
        print(f"Error connecting to {ip}:{port} - {e}")
        return None

async def start_session(miner_ip, miner_port):
    """
    Start a session with the miner and return the session ID.
    
    Note: Replace "startsession" with the actual command from the docs
    (https://docs.luxor.tech/docs/firmware/api/sessions).
    
    Returns:
        str: Session ID, or None if failed
    """
    command = {"command": "startsession"}  # Adjust based on documentation
    response = await send_command(miner_ip, miner_port, command)
    if response is None:
        print("Failed to send session start command.")
        return None

    print(f"Session start response: {response}")
    
    # Extract SessionID (adjust parsing based on actual response structure)
    try:
        session_id = response["SESSION"][0]["SessionID"]
        if not session_id:
            raise ValueError("Session ID is empty")
        return session_id
    except (KeyError, IndexError, ValueError) as e:
        print(f"Error extracting session ID: {e}")
        return None

async def curtail_mining(miner_ip, miner_port, session_id, state):
    """
    Send the curtail command to start or stop mining.
    
    Args:
        miner_ip (str): Miner IP address
        miner_port (int): Miner port
        session_id (str): Active session ID
        state (str): "sleep" to start mining, "active" to stop mining
    
    Note: Confirm "curtail" parameters in
    https://docs.luxor.tech/docs/firmware/api/available_commands#m02
    """
    command = {
        "command": "curtail",
        "session": session_id,
        "parameter": state
    }
    response = await send_command(miner_ip, miner_port, command)
    if response is None:
        print("Failed to send curtail command.")
        return

    print(f"Curtail response: {response}")
    
    # Check if the command was successful
    if "STATUS" in response and response["STATUS"][0]["STATUS"] == "S":
        print(f"Successfully set mining state to {state}")
    else:
        print(f"Curtail command failed: {response.get('STATUS', 'No status')}")
        # Optionally, restart session if it fails due to invalid session

async def read_temperature():
    """
    Placeholder for reading the miner's temperature.
    
    Returns:
        float: Temperature in Â°C, or None if unavailable
    
    Replace this with actual implementation (e.g., API call or sensor reading).
    """
    # Example: return a dummy value for testing
    return 25.0  # Implement actual temperature reading here

async def main():
    """Main loop to monitor temperature and control mining."""
    # Get target temperature from user
    target_temp = float(input("Enter target temperature (Â°C): "))
    print(f"Target temperature set to: {target_temp}Â°C")

    # Initialize session
    session_id = await start_session(MINER_IP, MINER_PORT)
    if not session_id:
        print("Cannot proceed without a valid session ID. Exiting.")
        return

    print(f"Session started with ID: {session_id}")

    # Main control loop
    while True:
        temp = await read_temperature()
        if temp is not None:
            print(f"Current temperature: {temp:.2f}Â°C")
            if temp <= target_temp - 2:
                # Start mining when temperature is 2Â°C below target
                await curtail_mining(MINER_IP, MINER_PORT, session_id, "sleep")
            elif temp >= target_temp:
                # Stop mining when temperature reaches or exceeds target
                await curtail_mining(MINER_IP, MINER_PORT, session_id, "active")
        else:
            print("Temperature reading unavailable.")

        await asyncio.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    asyncio.run(main())
