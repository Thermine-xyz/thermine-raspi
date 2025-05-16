import requests
import json
import asyncio

# Configurazione del miner (queste dovrebbero essere lette da un file di configurazione in un progetto reale)
MINER_IP = "192.168.178.180"  # Sostituisci con l'IP del tuo miner
JWT_TOKEN = "dMQjN5kMVyO63a6eNDw9GNvdR07XRYWj"

def get_auth_headers():
    """Prepara le intestazioni di autenticazione."""
    return {"Authorization": f"Bearer {JWT_TOKEN}"}

async def get_miner_data():
    """Ottiene hashrate, temperatura e frequenza dei chip dal miner."""
    endpoint = f"http://{MINER_IP}/api/v1/summary"
    try:
        response = requests.get(endpoint, headers=get_auth_headers())
        response.raise_for_status()
        miner_data = response.json().get('miner', {})
        
        # Hashrate
        hashrate = miner_data.get('hr_average', None)
        
        # Temperatura
        pcb_temp = miner_data.get('pcb_temp', {}).get('max', 'N/A')
        chip_temp = miner_data.get('chip_temp', {}).get('max', 'N/A')
        
        # Frequenza dei chip (MHz)
        chains = miner_data.get('chains', [])
        freq_mhz = chains[0].get('frequency', 'N/A') if chains else 'N/A'
        
        return {
            'hashrate': hashrate,
            'pcb_temp': pcb_temp,
            'chip_temp': chip_temp,
            'freq_mhz': freq_mhz
        }
    except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta dei dati del miner: {e}")
        return None

async def main():
    while True:
        data = await get_miner_data()
        if data:
            print(f"Hashrate: {data['hashrate']} GH/s")
            print(f"Temperatura PCB: {data['pcb_temp']}°C")
            print(f"Temperatura Chip: {data['chip_temp']}°C")
            print(f"Frequenza dei Chip: {data['freq_mhz']} MHz")
        else:
            print("Non è stato possibile ottenere i dati dal miner.")
        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
