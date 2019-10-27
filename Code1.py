"""
Created on Sun Apr 10 21:48:30 2016

@author: NikhilT
"""

import numpy as np
import cv2
import win32api
import win32con
import time
import math

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
height, width = gray.shape
gray = cv2.flip(gray, 1); #flip horizontally
thresh = np.zeros((height/2, width/2))

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1); #flip horizontally 
    frame1 = frame
    
    # Our operations on the frame come here
    
    # crop the image in region of interest
    crop = frame[0:height/2, width/2:width]
    
    # BGR to Gray       
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)        
    cv2.imshow('Gray', gray)
    
    # apply gaussina blur
    blur = cv2.GaussianBlur(gray,(15,15),0)
    cv2.imshow('Blur', blur)
    
    # Thresholding the Gaussina blured image
#    ret,thresh1 = cv2.threshold(blur,150,255,cv2.THRESH_BINARY)    #abovethres=1, belowthresh=0
#    ret,thresh2 = cv2.threshold(blur,150,255,cv2.THRESH_BINARY_INV) #abovethres=0, belowthresh=1
#    ret,thresh3 = cv2.threshold(blur,150,255,cv2.THRESH_TRUNC) #works as a chopper/low pass, chops higgher value
#    ret,thresh4 = cv2.threshold(blur,150,255,cv2.THRESH_TOZERO) #works as highpass 
#    ret,thresh5 = cv2.threshold(blur,150,255,cv2.THRESH_TOZERO_INV) #works as a chopper, turn chopped value zero
#    ret,thresh6 = cv2.threshold(blur,0,255,cv2.THRESH_OTSU)
    ret,thresh7 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    cv2.imshow('Threshold_OSTU + BIN_INV', thresh7)
    
#    # Draw contours
    im2, contours, hierarchy = cv2.findContours(thresh7, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)                          
#    
#    # count contours 
    max_area = -1
    for i in range(len(contours)):
        cnt=contours[i]
        area = cv2.contourArea(cnt)
        # selecting contour with max area
        if(area > max_area):
            max_area = area
            ci=i
    cnt=contours[ci] # indexing the contour with maximum area
    x, y, w, h = cv2.boundingRect(cnt)
    
    draw = np.zeros(crop.shape,np.uint8)
    cv2.rectangle(draw, (x,y), (x+w,y+h), (0,0,255), 2)  # fitting a bounding rectangle      
    
    # drawing contours & hull   
    hull = cv2.convexHull(cnt) #provides curves for hull 
    cv2.drawContours(draw,[cnt],-1,(0,255,0),1)  # draws contours with green
    cv2.drawContours(draw,[hull],0,(0,0,255),1) #draws hulls with red  #giving error 

    
    # drawing contours defects 
    hull = cv2.convexHull(cnt, returnPoints = False)  #provides points for hull
    defects = cv2.convexityDefects(cnt, hull)       

    
    # draw circle at centroid
    M = cv2.moments(contours[0])
    if M['m00']!=0:
        cx = int(M['m10']/M['m00']) # x coordinate of centroid
        cy = int(M['m01']/M['m00']) # y coordinate of centroid
    else:
        cx,cy = 0,0
    cv2.circle(draw, (cx, cy), 20, (255,0,0), 2)
    cv2.imshow('Draw_all', draw)
    
    count=0
    for i in range(defects.shape[0]):
        s,e,f,d = defects[i,0]
        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])
        #length
        E = math.sqrt((start[0] - far[0])**2 + (start[1] - far[1])**2)
        S = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
        F = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        # appling cosine formula to calculate angle made by defect with hull points
        aplha = math.acos((S**2 + E**2 - F**2)/(2*S*E)) * 57
        if aplha <= 90:
            count += 1
            cv2.circle(draw,far,5,[0,0,255],-1) 
    cv2.imshow('Defects', draw)
    
    # control operation 
    s=5 #mouse sentitivity
    cv2.putText(frame,"Fingers counted %d" % count, (50,100), cv2.FONT_HERSHEY_PLAIN, 2, 2)
    if count==5:
       cv2.putText(frame,"High Five sir, Mouse is ON", (50,50), cv2.FONT_HERSHEY_PLAIN, 2, 2)              
       win32api.SetCursorPos((s*(cx), s*(cy)))
       time.sleep(0.01)
    elif count==2:
       cv2.putText(frame,"ok!! Left click", (50,50), cv2.FONT_HERSHEY_PLAIN, 2, 2)
       time.sleep(0.1) 
       win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
       time.sleep(0.01) 
       win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
       time.sleep(0.01)
    elif count==3:
       time.sleep(0.1) 
       cv2.putText(frame,"ok!! Right click", (50,50), cv2.FONT_HERSHEY_PLAIN, 2, 2)
       win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
       time.sleep(0.01) 
       win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)
       time.sleep(0.01)
    elif count==4:      
       cv2.putText(frame,"Char bootal.., kam mera roz ka..", (50,50), cv2.FONT_HERSHEY_PLAIN, 2, 2)
          
    else:
        cv2.putText(frame,"Welcome Sir", (50,50), cv2.FONT_HERSHEY_PLAIN, 2, 2)   
    cv2.imshow('Frame', frame) 
        
    
    if cv2.waitKey(1) & 0xFF == ord('q'): #command to exit the video window
        break
    

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()