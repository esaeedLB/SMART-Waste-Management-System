import time
import board
import vl53l5cx_ctypes as vl53l5cx
from adafruit_bme280 import basic as adafruit_bme280
import numpy as np
import RPi.GPIO as GPIO
from hx711 import HX711
import json
from datetime import datetime

# Bin configuration
BIN_ID = "BIN_001"
BIN_HEIGHT_MM = 200
FULL_THRESHOLD = 80

# Load cell configuration
scale = 32682
WEIGHT_THRESHOLD_KG = 0.03


def get_average_raw(samples=10, delay=0.05):
    readings = []

    for _ in range(samples):
        values = hx.get_raw_data()
        avg = sum(values) / len(values)
        readings.append(avg)
        time.sleep(delay)

    return sum(readings) / len(readings)


def calculate_fill_percentage(distance_mm):
    fill_percent = ((BIN_HEIGHT_MM - distance_mm) / BIN_HEIGHT_MM) * 100
    fill_percent = max(0, min(100, fill_percent))
    return fill_percent


def save_bin_data_to_json(
    bin_id,
    center_distance,
    fill_level,
    status,
    current_weight,
    current_weight_g,
    delta_weight_g,
    temperature,
    pressure,
    humidity,
    filename="bin_data.json"
):
    bin_data = {
        "bin_id": bin_id,
        "timestamp": datetime.now().isoformat(timespec="seconds"),

        "fill_level": {
            "distance_mm": round(center_distance, 2),
            "percentage": round(fill_level, 1),
            "status": status
        },

        "weight": {
            "current_weight_kg": round(current_weight, 3),
            "current_weight_g": round(current_weight_g, 2),
            "weight_change_g": round(delta_weight_g, 2)
        },

        "environment": {
            "temperature_c": round(temperature, 1),
            "pressure_hpa": round(pressure, 1),
            "humidity_percent": round(humidity, 1)
        }
    }

    with open(filename, "w") as json_file:
        json.dump(bin_data, json_file, indent=4)

    print(f"JSON data saved to {filename}")


# Load Cell Initialisation
hx = HX711(
        dout_pin=5,
        pd_sck_pin=6,
        channel='A',
        gain=64 
    )

hx.reset()

offset_values = hx.get_raw_data()
offset = sum(offset_values) / len(offset_values)

# Store first stable weight baseline
last_stable_raw = get_average_raw(samples=10)


# Temp sensor
i2c = board.I2C()
temp_sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

vl53 = vl53l5cx.VL53L5CX()
vl53.set_resolution(8 * 8)

# Enable motion detection
vl53.enable_motion_indicator(8 * 8)
vl53.set_motion_distance(400, 1400)

vl53.start_ranging()

print("Bin sensor activated")

while True:
    
    if vl53.data_ready():
        
        data = vl53.get_data()
        motion = list(data.motion_indicator.motion)
        
        if max(motion) > 50:
           print("Motion detected, waiting 5 seconds to detect bin level")
           
           time.sleep(5)

           # Get fresh ToF data after waiting
           if vl53.data_ready():
               data = vl53.get_data()
           
           distances = list(data.distance_mm[0])
           print("distance count:", len(distances))

           center_distance = ((distances[35] + distances[36] + distances[43] + distances[44]) / 4)
           fill_level = calculate_fill_percentage(center_distance)

           print("New bin level:", center_distance, "mm")
           print("Fill level:", round(fill_level, 1), "%")

           if fill_level >= FULL_THRESHOLD:
               status = "Collection required"
           elif fill_level >= 60:
               status = "Nearly full"
           else:
               status = "Available"

           print("Status:", status)

           arr = np.array(data.distance_mm).reshape((8,8))
           
           # print 8x8 grid
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
           
           # Load cell reading
           new_raw = get_average_raw(samples=10)
           
           raw_delta = new_raw - last_stable_raw
           delta_weight = raw_delta / scale

           current_weight = (new_raw - offset) / scale
           current_weight_g = current_weight * 1000
           delta_weight_g = delta_weight * 1000

           print("Previous raw:", round(last_stable_raw, 2))
           print("New raw:", round(new_raw, 2))
           print("Raw delta:", round(raw_delta, 2))

           print("Weight (kg):", round(current_weight, 2))
           print("Weight (g):", round(current_weight_g, 2))
           print("Weight change (g):", round(delta_weight_g, 2))

           if delta_weight > WEIGHT_THRESHOLD_KG:
               print("Waste deposit detected")
           elif delta_weight < -WEIGHT_THRESHOLD_KG:
               print("Weight decrease detected")
           else:
               print("No significant weight change detected")

           # Save latest bin event data to JSON
           save_bin_data_to_json(
               bin_id=BIN_ID,
               center_distance=center_distance,
               fill_level=fill_level,
               status=status,
               current_weight=current_weight,
               current_weight_g=current_weight_g,
               delta_weight_g=delta_weight_g,
               temperature=temp_sensor.temperature,
               pressure=temp_sensor.pressure,
               humidity=temp_sensor.relative_humidity
           )

           # Update baseline after calculating delta
           last_stable_raw = new_raw
    
           time.sleep(1)
        
    time.sleep(0.05)