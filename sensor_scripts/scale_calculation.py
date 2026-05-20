import RPi.GPIO as GPIO
import time
from hx711 import HX711


hx = HX711(
    dout_pin=5,
    pd_sck_pin=6,
    channel='A',
    gain=64
        
)

#total_off = 0
hx.reset()
#print("calcuating")
#time.sleep(5)
#for i in range(20):
#    offset_values = hx.get_raw_data()
#    offset = sum(offset_values) / len(offset_values)
#    total_off += offset

#print(total_off / 20)


offset_values = hx.get_raw_data()
offset = sum(offset_values) / len(offset_values)

scale = 32682

while True:
    values = hx.get_raw_data()
    avg = sum(values) / len(values)
    
    weight = (avg - offset) / scale
    weight_g = ((avg - offset) / scale) * 1000
    
    print("Weight (kg):", round(weight, 2))
    print("Weight (g):", round(weight_g, 2))
    
    time.sleep(5)

    