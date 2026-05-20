import time
import vl53l5cx_ctypes as vl53l5cx

vl53 = vl53l5cx.VL53L5CX()

vl53.set_resolution(8*8)
vl53.enable_motion_indicator(8*8)
vl53.set_motion_distance(400, 1400)

vl53.start_ranging()

print("Motion sensor has activated")

while True:
    if vl53.data_ready():
        data = vl53.get_data()
        motion = list(data.motion_indicator.motion)
        
        if max(motion) > 50:
            print("Motion has been detected")
            
    time.sleep(0.05)
                    
                    
                    