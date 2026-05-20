import RPi.GPIO as GPIO
import time
from hx711 import HX711


try:
    hx = HX711(
        dout_pin=5,
        pd_sck_pin=6,
        channel='A',
        gain=64
        
    )

    hx.reset()
    print("Starting the readings...")
    time.sleep(2)
    print("Calibrating... leave empty")
    offset = hx.get_raw_data()
    print("Baseline:", offset)
    
    while True:
        #get multiple readings
        measures = hx.get_raw_data()
        delta = offset[0]
        
        if measures:
            for m in measures:
                print("Raw value:", m)
            print("Change:", (m - delta))
                
        else:
            print("No data received")
            
        time.sleep(1)

finally:
    GPIO.cleanup()