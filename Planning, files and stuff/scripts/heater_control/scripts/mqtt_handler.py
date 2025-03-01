import paho.mqtt.client as mqtt
import json
import asyncio

# Carica la configurazione MQTT
with open('../config/mqtt_config.json', 'r') as f:
    mqtt_config = json.load(f)

async def mqtt_client():
    client = mqtt.Client(protocol=mqtt.MQTTv311, transport="tcp")

    def on_connect(client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        # Subscribe to topics here
        client.subscribe(f"tele/{mqtt_config['topic_prefix']}/SENSOR")

    def on_message(client, userdata, msg):
        payload = json.loads(msg.payload.decode())
        if 'ENERGY' in payload:
            energy_data = payload['ENERGY']
            print(f"Power: {energy_data['Power']}W, Voltage: {energy_data['Voltage']}V, Current: {energy_data['Current']}A")
        else:
            print("No ENERGY data in the message.")

    client.on_connect = on_connect
    client.on_message = on_message

    await asyncio.sleep(0.1)  # Give it a moment to connect
    client.connect(mqtt_config['broker'], mqtt_config['port'], 60)

    # We use loop_start here instead of loop_forever to be able to run in an async context
    client.loop_start()

    try:
        while True:
            await asyncio.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        print("Shutting down MQTT client...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    asyncio.run(mqtt_client())
