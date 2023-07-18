import numpy as np
import time
import datetime

import threading
import sys
from queue import Queue

import cv2
import imutils
from imutils.video import FPS


############################################

url = "rtsp://admin2:admin002@172.16.25.107"
save_path = "/Users/henrypascall/Desktop/CamImages"

def testDevice(source):
   cap = cv2.VideoCapture(source) 
   if cap is None or not cap.isOpened():
       print('Warning: unable to open video source: ', source)

testDevice(url)

############################################

class FileVideoStream:
    def __init__(self, path, queueSize = 256):

        self.stream = cv2.VideoCapture(path)
        self.stopped = False
        self.Q = Queue(maxsize=queueSize)

    def run_thread(self):
        t = threading.Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        time.sleep(0.1)
        return self
        
    
    def update(self):
        while True:
            if self.stopped:
                return
            if not self.Q.full():
                (grabbed, frame) = self.stream.read()
                
                if not grabbed:
                    self.stop()
                    print("[ERROR] No Video Stream")
                    return
                self.Q.put(frame)
                
                
            

    def read(self):
        return self.Q.get()
    def more(self):
        return self.Q.qsize() > 0
    def stop(self):
        self.stopped = True
        
###########################################################################################################

print("[INFO] starting video file thread...")
fvs = FileVideoStream(url).run_thread()
print(fvs.stream)


#Video properties
length = int(fvs.stream.get(cv2.CAP_PROP_FRAME_COUNT))
rec_fps = int(fvs.stream.get(cv2.CAP_PROP_FPS))
size = [int(fvs.stream.get(cv2.CAP_PROP_FRAME_WIDTH)), int(fvs.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))]
print("[INFO] frame resolution: ({}, {})".format(size[0], size[1]))
print("[INFO] stream FPS: {}".format(rec_fps))

print(fvs.Q.qsize())

############################################################################################################
#Motion
#Initialise Variables
frame_num = 0


frame = np.zeros((100,100,3), dtype=np.uint8)
counter = 0

#left_motion_window = frame[ly_min:ly_min + motion_dy, lx_min:lx_min + motion_dx].copy()
#right_motion_window = frame[ry_min:ry_min + motion_dy, rx_min:rx_min + motion_dx].copy()

while fvs.more():
    frame_num += 1
   #frame_prev = frame.copy
    if fvs.Q.qsize() == 0:
       print("[WARNING] frame buffer empty, waiting...")
       time.sleep(0.5)
       counter += 1
       if counter == 10:
           print("[ERROR] Video stream lost")
           break
    frame = fvs.read()

    cv2.imshow('img', frame)


    if cv2.waitKey(1) & 0xFF == ord("s"):
        cv2.imshow('img', frame)
        img_save = save_path+'/'+'{}_{}{}'.format('camera1', str(datetime.date.today()), '.bmp')
        print("[SAVE]",img_save)
        cv2.imwrite(img_save,frame)
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("[INFO] Motion detection stopped by user")
        break
    

cv2.destroyAllWindows()
fvs.stop()



