from influxdb import InfluxDBClient

# Configurazione InfluxDB
INFLUXDB_CONFIG = {
    'host': 'localhost',
    'port': 8086,
    'username': 'admin',
    'password': 'M33k0',
    'database': 'heater_data'
}

client = InfluxDBClient(**INFLUXDB_CONFIG)

def write_to_influx(data):
    if data:
        client.write_points(data)
        print(f"Dati scritti in InfluxDB: {data}")

# Questo script non ha una funzione main, è utilizzato da altri script
