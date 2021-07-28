'''
Created on 2021年7月27日

@author: Hsiao-Chien Tsai(蔡効謙)
'''
import cv2
import numpy as np
#
vari = 0.03
vari = 0.00001
vari = 0.0005
vari = 0.05
kalman = cv2.KalmanFilter(4, 2) # 4: State number, including (x, y, dx, dy) coordinates and speed (distance of each movement); 2: Observation, what can be seen is the coordinate value
kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32) # System measurement matrix
kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32) # State transition matrix
kalman.processNoiseCov = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)*vari # System process noise covariance
#
last_measurement = current_measurement = np.array([[np.float32(320)], [np.float32(240)]])
last_prediction = current_prediction = np.array([[np.float32(320)], [np.float32(240)]])

def update_position(x, y):
    global frame, current_measurement, measurements, last_measurement, current_prediction, last_prediction
    
    last_prediction = current_prediction # Store the current forecast as the last forecast
    last_measurement = current_measurement # Save the current measurement as the last measurement
    
    current_measurement = np.array([[np.float32(x)], [np.float32(y)]]) # Current measurement
    kalman.correct(current_measurement) # Use the current measurement to calibrate the Kalman filter    
    current_prediction = kalman.predict() # Calculate Kalman forecast value as the current forecast
    
    #print (last_measurement)
    lmx, lmy = last_measurement[0], last_measurement[1] # Last measured coordinates
    cmx, cmy = current_measurement[0], current_measurement[1] # Current measurement coordinates
    lpx, lpy = last_prediction[0], last_prediction[1] # Last predicted coordinates
    cpx, cpy = current_prediction[0], current_prediction[1] # Current forecast coordinates
    
    last_x, last_y = lmx[0].astype(np.int_), lmy[0].astype(np.int_)
    curr_x, curr_y = cmx[0].astype(np.int_),  cmy[0].astype(np.int_)
    
    last_p_x, last_p_y = lpx[0].astype(np.int_), lpy[0].astype(np.int_)
    curr_p_x, curr_p_y = cpx[0].astype(np.int_), cpy[0].astype(np.int_)

    '''
    # Draw two lines from the last measurement to the current measurement and from the last prediction to the current prediction
    cv2.line(frame, (lmx[0].astype(np.int_), lmy[0].astype(np.int_)),
                    (cmx[0].astype(np.int_), cmy[0].astype(np.int_)), (0,255,0))
    # Trace the path of the prediction in red. BGR
    cv2.line(frame, (lpx[0].astype(np.int_), lpy[0].astype(np.int_)),
                (cpx[0].astype(np.int_), cpy[0].astype(np.int_)), (0,0,255))    
     #BGR
    cv2.circle(frame, (cmx[0].astype(np.int_), cmy[0].astype(np.int_)), 4, (50, 150, 0), -1)      # current measured point
    cv2.circle(frame, (cpx[0].astype(np.int_), cpy[0].astype(np.int_)), 4, (0, 12, 255), -1)      # current predicted point
    '''
    
    
    return curr_p_x, curr_p_y