import cv2
import numpy as np
import math
 
from matplotlib import pyplot
import statistics
# Create an empty frame and define (700, 700, 3) drawing area
frame = np.ones((1080, 1920, 3), np.uint8) 
frame *= 255 #white background

#draw button
def draw_button(x1=int(1920*(2/3)),x2=int(1920*(2/3))+50,y1=int(1080*(2/3)),y2=int(1080*(2/3))+50):
    for y, row in enumerate(frame) :
        for x, col in enumerate(row) :
            if x > x1 and x < x2 and y > y1 and y < y2 :
                frame[y][x] = np.array([255,0,0])
draw_button()
# Initialize the array of measurement coordinates and mouse motion prediction
last_measurement = current_measurement = np.array([[np.float32(0)], [np.float32(0)]])
last_prediction = current_prediction = np.array([[np.float32(0)], [np.float32(0)]])

test_count, stable_count, move_count = 0,0,0 
p_x, p_y = 0,0
p_weight = 0.85

trajecotories = []
speeds = []
#
def get_dynamic_weight(px,py,cx,cy):
    
    
    global move_count, stable_count, test_count
    global p_weight
    movement = math.hypot(cx - px, cy - py)
    #movement_list.append(movement)
    #print ("movement:{}".format(movement))
    test_count += 1
    weight = p_weight
    if movement < 15: # 如何設計一個參數 adaptive 調整 stop intent and move intent 
        weight = 0.95 
        #print ("stable")
        stable_count += 1
        #print ("decrease move speed")
    elif movement > 100 : #80-90
        weight = 0.03
        #print ("increase move speed")
        #print ("speed")
        move_count += 1
    else :
        # 移動越快， weight 越小
        # [15,150] --->[0.95,0.05]
        w = 0.95 - ((movement - 15)/(100-15) * (0.95-0.03)) 
        weight = w
        #print ("move")
        move_count+=1
        #print ("m:{} w:{}".format(movement,w))
    if (test_count % 500 == 0) :
        print ("move/test  ={}/{} = {}".format(move_count,test_count,str(move_count/test_count)))
    
    speeds.append(movement)
    return weight

# Define mouse callback function to draw tracking results
def mousemove(event, x, y, s, p):
    global frame, current_measurement, measurements, last_measurement, current_prediction, last_prediction
    global p_x, p_y
    last_prediction = current_prediction # Store the current forecast as the last forecast
    last_measurement = current_measurement # Save the current measurement as the last measurement
    current_measurement = np.array([[np.float32(x)], [np.float32(y)]]) # Current measurement
    kalman.correct(current_measurement) # Use the current measurement to calibrate the Kalman filter
    
    current_prediction = kalman.predict() # Calculate Kalman forecast value as the current forecast
    # real position
    lmx, lmy = last_measurement[0], last_measurement[1] # Last measured coordinates
    cmx, cmy = current_measurement[0], current_measurement[1] # Current measurement coordinates
    #kalman
    lpx, lpy = last_prediction[0], last_prediction[1] # Last predicted coordinates
    cpx, cpy = current_prediction[0], current_prediction[1] # Current forecast coordinates

    p_fs_x, p_fs_y, full_screen_x, full_screen_y = lmx[0].astype(np.int_),lmy[0].astype(np.int_),cmx[0].astype(np.int_),cmy[0].astype(np.int_)
    
    #dynamic
    weight = get_dynamic_weight(p_fs_x, p_fs_y, full_screen_x, full_screen_y)
    c_x = weight * p_x + (1-weight ) * (full_screen_x) 
    c_y = weight * p_y + (1-weight ) * (full_screen_y)  

    # Draw two lines from the last measurement to the current measurement and from the last prediction to the current prediction
    #cv2.line(frame, (lmx, lmy), (cmx, cmy), (255, 0, 0)) # The blue line is the measured value
    #cv2.line(frame, (lpx, lpy), (cpx, cpy), (255, 0, 255)) # The pink line is the predicted value
    
    # real position , BGR color
    cv2.line(frame, (p_fs_x, p_fs_y),
                    (full_screen_x, full_screen_y), (0,255,0),3)
    
    kp_x,kp_y,kc_x,kc_y = lpx[0].astype(np.int_), lpy[0].astype(np.int_), cpx[0].astype(np.int_), cpy[0].astype(np.int_)
    # Kalman  
    cv2.line(frame, ( kp_x,kp_y), (kc_x,kc_y), (0,0,255),3)
    # proposed method
    cv2.line(frame, (int(p_x), int(p_y)),(int(c_x), int(c_y)), (255,0,0),3)
    
    p_x, p_y = c_x, c_y
    
    #BGR
    #cv2.circle(frame, (cmx[0].astype(np.int_), cmy[0].astype(np.int_)), 4, (50, 150, 0), -1)      # current measured point
    #cv2.circle(frame, (cpx[0].astype(np.int_), cpy[0].astype(np.int_)), 4, (0, 12, 255), -1)      # current predicted point
    trajecotories.append([full_screen_x, full_screen_y,kc_x, kc_y,int(c_x), int(c_y)])
# Window initialization
window_name = "tracker"
cv2.namedWindow(window_name)

# opencv uses the setMouseCallback function to handle mouse events. The specific event must be handled by the first parameter of the callback (event) function, which determines the type of trigger event (click, move, etc.)
cv2.setMouseCallback(window_name, mousemove)
#vari = 0.05
vari = 0.0005
#vari = 0.001
kalman = cv2.KalmanFilter(4, 2) # 4: State number, including (x, y, dx, dy) coordinates and speed (distance of each movement); 2: Observation, what can be seen is the coordinate value
kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32) # System measurement matrix
kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32) # State transition matrix
kalman.processNoiseCov = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)*vari # System process noise covariance


def draw_trajectory():
   
    font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 16,
        }
    
    samples = []
    for i, s in enumerate(trajecotories) :
        if i % 5 == 1 :
            samples.append(s)
    x1,y1, x2,y2, x3,y3 = [t[0] for t in samples], [t[1] for t in samples], [t[2] for t in samples], [t[3] for t in samples], [t[4] for t in samples], [t[5] for t in samples]
    # y3,y4,...yn
    
    sum_len_k = 0
    sum_len_p = 0 
    
    dist_k =  0
    dist_p =  0    
    for i, s in enumerate(samples[1:]) :   
        sum_len_k += math.hypot(s[2] - s[0], s[3] - s[1])
        sum_len_p += math.hypot(s[4] - s[0], s[5] - s[1])
        dist_k += math.hypot(s[2] - samples[i-1][2], s[3] - samples[i-1][3])
        dist_p += math.hypot(s[4] - samples[i-1][4], s[5] - samples[i-1][5])
    
    avg_len_k = round(sum_len_k/len(samples),4) 
    avg_len_p = round(sum_len_p/len(samples),4) 
    avg_speed = round(statistics.mean(speeds),4)
    dist_k = round(dist_k,4)
    dist_p = round(dist_p,4)
    
    l1, = pyplot.plot(x1,y1, marker="^")
    l2, = pyplot.plot(x2,y2, marker="s")
    l3, = pyplot.plot(x3,y3, marker="o")
    
    pyplot.legend(handles=[l1,l2,l3],labels=["Real trajectory","Kalman filter","first-order filter"],loc="best")
    pyplot.gca().invert_yaxis()
    
    #
    title_text = "Average moving speed:{} pixels/frame\ndist:{} dist:{}, diff:{} diff:{}".format(avg_speed, dist_k, dist_p, avg_len_k, avg_len_p)
    
    
    pyplot.title(title_text  , fontdict=font)
    pyplot.show()

if __name__ == "__main__" :     
  
    while True:        
        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):           
            break
        if key == ord('c'):
            frame = np.ones((1080, 1920, 3), np.uint8) 
            frame = frame * 255 # white background      
            trajecotories = []   
            speeds = []  
            draw_button()  
        if key == ord('t'):
            draw_trajectory()
            
   
    cv2.destroyAllWindows()