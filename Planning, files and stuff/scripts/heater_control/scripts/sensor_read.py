from w1thermsensor import W1ThermSensor
import asyncio

async def read_temperature():
    sensor = W1ThermSensor()
    try:
        temp = sensor.get_temperature()
        return temp
    except Exception as e:
        print(f"Errore durante la lettura della temperatura: {e}")
        return None

async def main():
    while True:
        temperature = await read_temperature()
        if temperature is not None:
            print(f"Temperatura attuale: {temperature}°C")
        await asyncio.sleep(30)  # Leggi la temperatura ogni 30 secondi

if __name__ == "__main__":
    asyncio.run(main())
