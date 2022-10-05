import KeyPressModule as kp
from djitellopy import tello
from time import sleep 
import numpy as np

###### Parameters #######
fSpeed=117/10 # Forward speed in cm/s measured (15cm/s)

aSpeed=360/10 # Angular speed deg/s

interval=0.25

dInterval=fSpeed*interval
aInterval=aSpeed*interval

#########################


kp.init()
me = tello.Tello()
me.connect()
print(me.get_battery())


def getKeyboardInput():
    lr, fb, ud, yv = 0,0,0,0
    speed=50
    if kp.getKey("LEFT"): lr=-speed
    elif kp.getKey("RIGHT"): lr=speed

    if kp.getKey("UP"): fb=speed
    elif kp.getKey("DOWN"): fb=-speed

    if kp.getKey("w"): ud=-speed
    elif kp.getKey("s"): ud=-speed

    if kp.getKey("a"): yv=speed
    elif kp.getKey("d"): yv=-speed

    if kp.getKey("q"): yv=me.land()

    if kp.getKey("e"): yv=me.takeoff()

    return [lr,fb,ud,yv]



while True:
    vals=getKeyboardInput()
    me.send_rc_control(vals[0],vals[1],vals[2],vals[3])
    img=