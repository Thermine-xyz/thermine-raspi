import asyncio
import logging
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# InfluxDB 2.x Configuration
INFLUXDB_CONFIG = {
    'url': "http://localhost:8086",
    'token': "ivhL4ksD9VOh99xGltO89rSE27Smjjdjy20NyuDta1yqT0-Itg8F39FMb6Y7gQHr49mWoSfGGUKNCFDd5_B3VQ==",
    'org': "heatpunks",
    'bucket': "heatminer"  # Updated with the correct bucket name
}

client = InfluxDBClient(url=INFLUXDB_CONFIG['url'], token=INFLUXDB_CONFIG['token'], org=INFLUXDB_CONFIG['org'])
write_api = client.write_api(write_options=SYNCHRONOUS)

async def collect_data():
    try:
        # Simulate data collection for demonstration
        miner_data = {
            'measurement': 'miner_stats',
            'tags': {'miner_ip': '192.168.178.180'},
            'fields': {
                'hashrate': 100.0,
                'status': 'mining'
            }
        }
        temp_data = {
            'measurement': 'temperature',
            'tags': {'sensor_type': 'DS1820'},
            'fields': {'value': 25.0}
        }
        mqtt_data = {
            'measurement': 'sonoff_energy',
            'tags': {'device': 'sonoff'},
            'fields': {
                'power': 100,
                'voltage': 230,
                'current': 0.434
            }
        }
        
        points = []
        
        if miner_data:
            point = Point(miner_data['measurement']) \
                        .tag("miner_ip", miner_data['tags']['miner_ip']) \
                        .field("hashrate", miner_data['fields']['hashrate']) \
                        .field("status", miner_data['fields']['status'])
            points.append(point)
            logger.info("Miner data collected successfully.")
        
        if temp_data:
            point = Point(temp_data['measurement']) \
                        .tag("sensor_type", temp_data['tags']['sensor_type']) \
                        .field("value", temp_data['fields']['value'])
            points.append(point)
            logger.info("Temperature data collected successfully.")
        
        if mqtt_data:
            point = Point(mqtt_data['measurement']) \
                        .tag("device", mqtt_data['tags']['device']) \
                        .field("power", mqtt_data['fields']['power']) \
                        .field("voltage", mqtt_data['fields']['voltage']) \
                        .field("current", mqtt_data['fields']['current'])
            points.append(point)
            logger.info("MQTT data collected successfully.")
        
        if points:
            write_api.write(bucket=INFLUXDB_CONFIG['bucket'], record=points)
            logger.info(f"Data written to InfluxDB: {len(points)} entries.")
    except Exception as e:
        logger.error(f"Error writing data to InfluxDB: {e}")

    # Keep the loop running
    try:
        while True:
            logger.info("Waiting for next data collection cycle...")
            await asyncio.sleep(30)
    except KeyboardInterrupt:
        logger.info("Stopping data collection due to KeyboardInterrupt.")

if __name__ == "__main__":
    logger.info("Starting data collection...")
    try:
        asyncio.run(collect_data())
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        client.close()
