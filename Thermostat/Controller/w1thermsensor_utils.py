import os
import glob
import random
import time
import json
from typing import Optional
from .utils import Utils

class MockW1ThermSensor:
    """
    Mock sensor to simulate temperature when no physical sensor is present
    """
    def __init__(self, sensor_id: str = "mock-000000000000"):
        self.sensor_id = sensor_id
        self._last_temp = None
        self._last_read = 0

    def get_temperature(self) -> float:
        """Simulate temperature between 20.0–30.0°C with small fluctuations."""
        current_time = time.time()
        if self._last_temp is None or (current_time - self._last_read) > 5:
            base_temp = 25.0  # Base ambient temperature
            fluctuation = random.uniform(-2.0, 2.0)  # ±2°C variation
            self._last_temp = max(20.0, min(30.0, base_temp + fluctuation))
            self._last_read = current_time
        return self._last_temp

    def id(self) -> str:
        return self.sensor_id

class W1ThermSensorUtils:
    @staticmethod
    def isW1SensorPresent() -> bool:
        """
        Check if a 1-Wire sensor is present in /sys/bus/w1/devices/.
        Returns True if at least one 28-XXXXXXXXXXXX device is found.
        """
        try:
            # Look for devices starting with '28-' (DS18B20 family)
            devices = glob.glob("/sys/bus/w1/devices/28-*")
            return len(devices) > 0
        except Exception as e:
            Utils.logger.error(f"W1ThermSensorUtils.is_w1_sensor_present error: {e}")
            return False

    @staticmethod
    def loadW1Modules() -> bool:
        """
        Attempt to load w1-gpio and w1-therm kernel modules.
        Returns True if successful, False otherwise.
        """
        try:
            os.system("sudo modprobe w1-gpio")
            os.system("sudo modprobe w1-therm")
            # Verify modules are loaded
            result = os.popen("lsmod | grep w1").read()
            return "w1_gpio" in result and "w1_therm" in result
        except Exception as e:
            Utils.logger.error(f"W1ThermSensorUtils.load_w1_modules error: {e}")
            return False

    @staticmethod
    def getTemperature() -> Optional[float]:
        """
        Get temperature from W1ThermSensor if a sensor is present, else use mock.
        Returns temperature in °C or None if failed.
        """
        if W1ThermSensorUtils.isW1SensorPresent():
            # Try to import w1thermsensor exceptions, with fallback
            try:
                from w1thermsensor import W1ThermSensor, KernelModuleLoadError, NoSensorFoundError, SensorNotReadyError
            except ImportError as e:
                Utils.logger.error(f"W1ThermSensorUtils.get_temperature Failed import sensor, error {e}")
                W1ThermSensor = None
                KernelModuleLoadError = NoSensorFoundError = SensorNotReadyError = Exceptionprint("getTemperature1")
        if W1ThermSensorUtils.isW1SensorPresent() and W1ThermSensor is not None:
            try:
                # Ensure modules are loaded
                if not W1ThermSensorUtils.loadW1Modules():
                    Utils.logger.error("W1ThermSensorUtils.get_temperature Failed to load w1-gpio and w1-therm modules")
                    return None
                sensor = W1ThermSensor()
                temp = sensor.get_temperature()
                return temp
            except KernelModuleLoadError as e:
                Utils.logger.error(f"W1ThermSensorUtils.get_temperature Kernel module error: {e}")
                Utils.logger.error("W1ThermSensorUtils.get_temperature Ensure dtoverlay=w1-gpio is in /boot/config.txt")
                return None
            except NoSensorFoundError as e:
                Utils.logger.error(f"W1ThermSensorUtils.get_temperature No sensor found: {e}")
                return None
            except SensorNotReadyError as e:
                Utils.logger.error(f"W1ThermSensorUtils.get_temperature Sensor not ready: {e}")
                return None
            except Exception as e:
                Utils.logger.error(f"W1ThermSensorUtils.get_temperature Unexpected W1ThermSensor error: {e}")
                return None
        else:
            Utils.logger.info("W1ThermSensorUtils.get_temperature No 1-Wire sensor detected, using mock sensor")
            try:
                sensor = MockW1ThermSensor()
                temp = sensor.get_temperature()
                return temp
            except Exception as e:
                Utils.logger.info(f"W1ThermSensorUtils.get_temperature Mock sensor error: {e}")
                return None

    @staticmethod
    def saveTempToDataFile(jObj):
        tSensor = W1ThermSensorUtils.getTemperature()
        if isinstance(tSensor, float):
            tSensor = round(tSensor,4)
            path = Utils.pathDataMinerTempSensor(jObj)
            lock = Utils.getFileLock(path).gen_wlock() # lock for reading, method "wlock"
            with lock:
                with open(path, 'a', encoding='utf-8') as file:
                    file.write(f"{Utils.nowUtc()};{tSensor}\n")
