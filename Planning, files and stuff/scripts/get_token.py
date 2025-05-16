import requests
import json

# Configurazione del miner (queste dovrebbero essere lette da un file di configurazione in un progetto reale)
MINER_IP = "192.168.178.180"  # Sostituisci con l'IP del tuo miner
PASSWORD = "admin"  # Sostituisci con la tua password

def get_jwt_token():
    """Richiede un token JWT al miner."""
    endpoint = f"http://{MINER_IP}/api/v1/unlock"
    payload = {"pw": PASSWORD}
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        response_data = response.json()
        
        if 'token' in response_data:
            return response_data['token']
        else:
            print("Errore: Nessun token JWT ricevuto.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta del token: {e}")
        return None

if __name__ == "__main__":
    token = get_jwt_token()
    if token:
        print(f"Token JWT ottenuto: {token}")
    else:
        print("Fallimento nell'ottenere il token.")
