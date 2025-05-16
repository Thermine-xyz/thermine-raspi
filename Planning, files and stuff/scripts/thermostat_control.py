import asyncio
from w1thermsensor import W1ThermSensor
import requests
import json

# Configurazione del miner
MINER_IP = "192.168.178.180"
API_ENDPOINT = f"http://{MINER_IP}/api/v1"

def get_jwt_token():
    """Ottiene un nuovo token JWT dal miner."""
    endpoint = f"{API_ENDPOINT}/unlock"
    payload = {"pw": "admin"}  # Password del miner
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()['token']
    except requests.exceptions.RequestException as e:
        print(f"Errore durante l'ottenimento del token: {e}")
        return None

async def read_temperature():
    """Legge la temperatura dal sensore DS1820."""
    sensor = W1ThermSensor()
    try:
        temp = sensor.get_temperature()
        return round(temp, 2)  # Arrotonda a due decimali
    except Exception as e:
        print(f"Errore durante la lettura della temperatura: {e}")
        return None

async def execute_miner_action(endpoint, action_name):
    """Esegue un'azione sul miner, ottenendo un nuovo token ogni volta."""
    token = get_jwt_token()
    if token is None:
        print(f"Impossibile ottenere un token JWT valido per {action_name}.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(endpoint, headers=headers)
        response.raise_for_status()
        print(f"Azione {action_name} eseguita con successo.")
    except requests.exceptions.RequestException as e:
        print(f"Errore durante l'azione {action_name}: {e}")
        if 'response' in locals() and hasattr(response, 'status_code'):
            print(f"Codice di stato della risposta: {response.status_code}")
            if response.status_code == 401:
                print("Token potrebbe essere scaduto o non valido.")

async def thermal_control(temp, target_temp):
    if temp is None:
        return

    status_endpoint = f"{API_ENDPOINT}/status"
    token = get_jwt_token()
    if token is None:
        print("Impossibile ottenere un token JWT valido per controllare lo stato del miner.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    try:
        status_response = requests.get(status_endpoint, headers=headers)
        status_response.raise_for_status()
        miner_status = status_response.json()
        current_status = miner_status.get('miner_state', 'unknown')

        print(f"Miner Status: {current_status}")

        if temp <= target_temp - 2 and current_status not in ['mining', 'starting']:
            await execute_miner_action(f"{API_ENDPOINT}/mining/start", "start mining")
            print("Temperature too low: Mining Started")
        elif temp >= target_temp and current_status == 'mining':
            await execute_miner_action(f"{API_ENDPOINT}/mining/stop", "stop mining")
            print("Temperature is ok: Mining Stopped")

    except requests.exceptions.RequestException as e:
        print(f"Mining control error: {e}")

async def main():
    target_temp = float(input("Target temperature: "))

    while True:
        temp = await read_temperature()
        if temp is not None:
            print(f"T: {temp:.2f}°C")
            await thermal_control(temp, target_temp)
        else:
            print("Impossible to read temperature.")
        await asyncio.sleep(10)  # Controlla ogni 10 secondi per aggiornamento più frequente

if __name__ == "__main__":
    asyncio.run(main())
