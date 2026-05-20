import board
import time
from adafruit_bme280 import basic as adafruit_bme280

i2c = board.I2C()
sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

print("\nTemperature: %0.1fC " % sensor.temperature)
print("Pressure: %0.1f hpa" % sensor.pressure)
print("Humidity: %0.1f %% " % sensor.relative_humidity)
time.sleep(2)