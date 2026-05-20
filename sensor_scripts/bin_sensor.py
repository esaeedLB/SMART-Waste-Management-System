import time
import board
import vl53l5cx_ctypes as vl53l5cx
from adafruit_bme280 import basic as adafruit_bme280
import numpy as np
import RPi.GPIO as GPIO
from hx711 import HX711

#Load Cell Initialisation
hx = HX711(
        dout_pin=5,
        pd_sck_pin=6,
        channel='A',
        gain=64 
    )
hx.reset()
global offset
global scale

offset_values = hx.get_raw_data()
offset = sum(offset_values) / len(offset_values)
scale = 32682


#Temp sensor

i2c = board.I2C()
temp_sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

vl53 = vl53l5cx.VL53L5CX()
vl53.set_resolution(8 * 8)

#Enable motion detection

vl53.enable_motion_indicator(8 * 8)
vl53.set_motion_distance(400, 1400)

vl53.start_ranging()

print("Bin sensor activated")

while True:
    
    if vl53.data_ready():
        
        data = vl53.get_data()
        motion = list(data.motion_indicator.motion)
        
        if max(motion) > 50:
           print("Motion detected, waiting 10 seconds to detect bin level")
           
           time.sleep(10)
           
           distances = list(data.distance_mm[0])
           print("distance count:", len(distances))
           center_distance = ((distances[35] + distances[36] + distances[43] + distances[44]) / 4)
           print("New bin level:", center_distance, "mm")
           arr = np.array(data.distance_mm).reshape((8,8))
           
           #print 8x8 grid
           
           print("-" * 40)
           for row in arr:
               print(" ".join(f"{d:4}" for d in row))
           print("-" * 40)
           print("\n")
            
            
           time.sleep(1)
           print("Displaying bin temperature and other information: \n")
           print("\nTemperature: %0.1fC " % temp_sensor.temperature)
           print("Pressure: %0.1f hpa" % temp_sensor.pressure)
           print("Humidity: %0.1f %% " % temp_sensor.relative_humidity)
           print("\n")
           time.sleep(2)
           
           print("Calculating weight inside bin, please allow time...")
           
           
           weight_readings_kg = []
           for i in range(10):
               values = hx.get_raw_data()
               avg = sum(values) / len(values)
        
               weight = (avg - offset) / scale
               #weight_g = ((avg - offset) / scale) * 1000
               
               weight_readings_kg.append(weight)
        
               #print("Weight (kg):", abs(round(weight, 2)))
               #print("Weight (g):", abs(round(weight_g, 2)))
        
               time.sleep(0.5)
           
           weight_cumulative = 0
           for x in range(len(weight_readings_kg)):
               weight_cumulative += weight_readings_kg[x]
           mean_weight = ((weight_cumulative)/len(weight_readings_kg))
           
           mean_weight_g = mean_weight * 1000
           
           print("Weight (kg):", abs(round(mean_weight, 2)))
           print("Weight (g):", abs(round(mean_weight_g, 2)))
           print(weight_readings_kg)
           
               
        
    time.sleep(0.05)
