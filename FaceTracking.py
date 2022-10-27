import cv2
import numpy as np
from djitellopy import tello
import time


me = tello.Tello()
me.connect()

print(me.get_battery())

me.streamon()
me.takeoff()
#take-off and go up to be at the level of the face
me.send_rc_control(0,0,25,0)
time.sleep(2.2)


#picture area forward and backward range
fbRange = [6200, 6700]
#propotionnal, integral, derivative controler parameters
pid=[0.4,0.4,0]
pError = [0,0]
#image size
w,h=360,240
def findFace(img):
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    imgGray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray,1.2,8)

    myFaceListC=[]
    myFaceListArea=[]
    for (x,y,w,h) in faces:
        #rectangle values first point bottom left second point top right
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
        #compute face center, area and store it
        cx=x + w//2
        cy=y + h//2
        area = w*h
        myFaceListC.append([cx,cy])
        myFaceListArea.append(area)
        cv2.circle(img,(cx,cy),5,(0,255,0),cv2.FILLED)
    # focus only on the max area face (the closest)
    if len(myFaceListArea) !=0:
        i =myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i],myFaceListArea[i]]
    else:
        return img, [[0,0],0]

def trackFace(me,info,w,h,pid,pError):
    
    area=info[1]
    x,y=info[0]
    fb=0
    error_x=x- w//2
    error_y=y- h//2

    speed=pid[0]*error_x + pid[1]* (error_x-pError[0])
    ud=-pid[0]*error_y - pid[1]* (error_y-pError[1])
    #cap the max speed to avoid dangerous conditions
    speed= int(np.clip(speed,-100,100))
    ud= int(np.clip(ud,-25,25))



    #if face too close move back if face too far move forward
    
    if area > fbRange[0] and area< fbRange[1]: #if in green zone, stay there
        fb=0
    elif area>fbRange[1]:
        fb=-20
    elif area< fbRange[0] and area !=0: #area != because if no image otherwise will move fwrd
        fb=20

    # if nothing detected:
    if x==0:
        speed=0
        ud=0
        error_x,error_y=0,0

    me.send_rc_control(0,fb,ud,speed)

    return [error_x,error_y]

#cap =cv2.VideoCapture(0)
while True:
    #_,img = cap.read()
    img = me.get_frame_read().frame
    img=cv2.resize(img,(w,h))
    img,info = findFace(img)
    pError= trackFace(me,info,w,h,pid,pError)
    #print(f'Center: {info[0]} | Area: {info[1]}')

    cv2.imshow('Output',img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        me.land()
        break