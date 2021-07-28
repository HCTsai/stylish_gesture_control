'''
Created on 2021年6月20日

@author: Hsiao-Chien Tsai(蔡効謙)
'''
import sys
import math
import cv2

def detect_finger_count(img, landmark_list, hand_label):
    h,w,c = img.shape
    fingers = []
    # 指尖列表，分别代表大拇指、食指、中指、無名指，小指的指尖
    tip_ids = [4, 8, 12, 16, 20]
    for tid in tip_ids:
        # 找到每個指尖的位置
        x, y = int(landmark_list[tid][1] * w), int(landmark_list[tid][2] *h)
        #cv2.circle(img, (x, y), 10, (0, 255, 0), cv2.FILLED)
        # 如果是大拇指，如果大拇指指尖x位置大於大拇指第二關節的位置，則認為大拇指打開，否則認為大拇指關閉
        # 還要判斷手
        if tid == 4 :
            if hand_label == 1 : #右手
                if landmark_list[tid][1] < landmark_list[tid - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else : #左手
                if landmark_list[tid][1] > landmark_list[tid - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        # 如果是其他手指，如果這些手指的指尖的y位置大於第二關節的位置，則認為這個手指打開，否則認為這個手指關閉
        else:
            if landmark_list[tid][2] < landmark_list[tid - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
    # fingers是这样一个列表，5个数据，0代表一个手指关闭，1代表一个手指打开
    # 判断有几个手指打开
    finger_count  = fingers.count(1)
    return finger_count, fingers

def get_finger_gesture(fingers):
    gesture = ""    
    if fingers == [0,1,0,0,0] or fingers == [1,1,0,0,0] :
        gesture = "pointer"
    #Rock paper scissors
    if fingers == [0,1,1,0,0 ]or fingers == [1,1,1,0,0] :
        gesture = "scissor"    
    if fingers == [0,0,0,0,0 ]:
        gesture = "rock"
    if fingers == [1,1,1,1,1 ]:
        gesture = "paper"
# totalFingers = fingers.count(1)
    return gesture 

def find_distance(lmslist, p1, p2, img, draw=True, r=4, t=2):
    h,w,c = img.shape
    x1, y1 = lmslist[p1][1:]
    x2, y2 = lmslist[p2][1:]
    x1 = int(x1 * w) 
    y1 = int(y1 * h) 
    x2 = int(x2 * w) 
    y2 = int(y2 * h) 
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    if draw:
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
        cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
    length = math.hypot(x2 - x1, y2 - y1)
    return length, img, [x1, y1, x2, y2, cx, cy]  
def find_center(lmslist, point_ids, img, draw=True, r=4, t=2):
    h,w,c = img.shape
    x_sum = 0
    y_sum = 0
    for pid in point_ids :         
        x1, y1 = lmslist[pid][1:]
        x_sum += x1
        y_sum += y1
    avg_x, avg_y = int(x_sum/len(point_ids)), int(y_sum/len(point_ids))    
    px, py  = int(avg_x*w), int(avg_y*h)   
    if draw:       
        cv2.circle(img, (px, py), r, (0, 0, 255), cv2.FILLED)
    return img, px, py 
def get_area(x,y):
    
    index_y = int(y/0.333) 
    #index_x = 3-int(x/0.333)  # mirror mode
    index_x = int(x/0.333) 
    area = index_y * 3 + index_x
    return area     
    
def detect_click_area(landmark_list):
    gestures = []  
    right_action_count = 0    
    area = -1
    for lmks in landmark_list : #大拇指，食指 高於其他手指
        if ( #(lmks[4][2]  < lmks[16][2] and lmks[4][2] < lmks[20][2]) and  
             #(lmks[12][2] < lmks[16][2] and lmks[12][2] < lmks[20][2]) and  
            #小指 高於 中指，無名指
            #lmks[8][1] > lmks[4][1] and  math.fabs(lmks[8][2] - lmks[4][2]) < 0.05 #食指拇指交叉
            # x and y
            math.fabs(lmks[4][1] - lmks[8][1]) < 0.05 and  math.fabs(lmks[4][2] - lmks[8][2]) < 0.05 #食指拇指交叉
            and lmks[0][0] == 1): # 右手   
            right_action_count += 1     
            
            center_x, center_y = (lmks[4][1] + lmks[8][1])/2 , (lmks[4][2] + lmks[8][2])/2
            area = get_area(center_x, center_y)
            
    if right_action_count > len(landmark_list)/2 :
        print ("right_click area:{}".format(area))   
        #gestures.append("right_click")    
    return gestures

def detect_click_gesture(landmark_list):
    gestures = []  
    right_action_count = 0    
    left_action_count = 0
    right_click_finger = [0,0,0,0] # 食指，中指，無名，小指
    left_click_finger = [0,0,0,0]# 食指，中指，無名，小指
    gesture_labels = ["click_{}".format(i) for i in range(8)]
    dist = 0.05
    for lmks in landmark_list[0:] : 
        #判斷拇指與各手指的距離
        if (math.fabs(lmks[8][1] - lmks[4][1]) < dist and  math.fabs(lmks[8][2] - lmks[4][2]) < dist) :
            if lmks[0][0] == 1 :# right hand
                right_click_finger[0] += 1
                right_action_count += 1
            else :
                left_click_finger[3] += 1
                left_action_count +=1
        if (math.fabs(lmks[12][1] - lmks[4][1]) < dist and  math.fabs(lmks[12][2] - lmks[4][2]) < dist) :
            if lmks[0][0] == 1 :# right hand
                right_click_finger[1] += 1
                right_action_count += 1
            else :
                left_click_finger[2] += 1 
                left_action_count +=1   
        if (math.fabs(lmks[16][1] - lmks[4][1]) < dist and  math.fabs(lmks[16][2] - lmks[4][2]) < dist) :
            if lmks[0][0] == 1 :# right hand
                right_click_finger[2] += 1
                right_action_count += 1
            else :
                left_click_finger[1] += 1   
                left_action_count +=1
        if (math.fabs(lmks[20][1] - lmks[4][1]) < dist and  math.fabs(lmks[20][2] - lmks[4][2]) < dist) :
            if lmks[0][0] == 1 :# right hand
                right_click_finger[3] += 1
                right_action_count += 1
            else :
                left_click_finger[0] += 1   
                left_action_count +=1
    for i, n in enumerate(right_click_finger) :
        if n > len(landmark_list)/2 :
            right_click_finger[i] = 1
        else :
            right_click_finger[i] = 0
    for i, n in enumerate(left_click_finger) :
        if n > len(landmark_list)/2 :
            left_click_finger[i] = 1
        else :
            left_click_finger[i] = 0    
    
    #print ("Left finger clicks:{}  right finger clicks{}"
    #       .format(left_click_finger,right_click_finger))
    for i, f in enumerate(left_click_finger + right_click_finger) :
        if f > 0 :
            gestures.append(gesture_labels[i])
    return gestures
def detect_heart_gesture(landmark_list):
    gestures = []  
    right_action_count = 0    
    left_action_count = 0
    for lmks in landmark_list[0:] : #大拇指，食指 高於其他手指
        if ( (lmks[4][2] < lmks[12][2] and lmks[4][2] < lmks[16][2] and lmks[4][2] < lmks[20][2]) and  
             (lmks[8][2] < lmks[12][2] and lmks[4][2] < lmks[16][2] and lmks[4][2] < lmks[20][2]) and  
             # 中指，無名指，小指 順序
             (lmks[12][1] >  lmks[20][1] ) and
             #食指拇指相近
              math.fabs(lmks[8][1] - lmks[4][1]) < 0.05 and  math.fabs(lmks[8][2] - lmks[4][2]) < 0.05 
              and lmks[0][0] == 1): # 右手
                    right_action_count += 1
        if ( (lmks[4][2] < lmks[12][2] and lmks[4][2] < lmks[16][2] and lmks[4][2] < lmks[20][2]) and  
             (lmks[8][2] < lmks[12][2] and lmks[4][2] < lmks[16][2] and lmks[4][2] < lmks[20][2]) and  
            # 中指，無名指，小指 順序
             (lmks[12][1] < lmks[20][1]) and
             #食指拇指相近
            math.fabs(lmks[8][1] - lmks[4][1]) < 0.05 and  math.fabs(lmks[8][2] - lmks[4][2]) < 0.05#食指拇指交叉
            and lmks[0][0] == 0): # 左手
                    left_action_count += 1
        #print (lmks[8][1] - lmks[4][1])         
    if right_action_count > len(landmark_list)/2 :
        #print ("right_heart count:{}".format(right_action_count))   
        gestures.append("right_heart")
    if left_action_count > len(landmark_list)/2 :
        #print ("left_heart count:{}".format(left_action_count))   
        gestures.append("left_heart")      
    
    return gestures

def detect_rock_gesture(landmark_list):
    
    gestures = []  
    right_action_count = 0    
    left_action_count = 0
    for lmks in landmark_list[0:] :
        if (lmks[8][2] < lmks[20][2] and # 食指 高於 小指
            #小指 高於 中指，無名指
            lmks[20][2] < lmks[12][2] and lmks[20][2] < lmks[16][2] and 
            math.fabs(lmks[4][1] - lmks[12][1]) < 0.04#拇指接近中指
            and lmks[0][0] == 1): # 右手
                    right_action_count += 1
        if (lmks[8][2] < lmks[20][2] and  
            lmks[20][2] < lmks[12][2] and lmks[20][2] < lmks[16][2] and 
            math.fabs(lmks[4][1] - lmks[12][1]) < 0.04#拇指接近中指
            and lmks[0][0] == 0): #左手
                    left_action_count += 1
        #print (math.fabs(lmks[4][1] - lmks[12][1]))         
    if right_action_count > len(landmark_list)/2 :
        #print ("right_rock count:{}".format(right_action_count))   
        gestures.append("right_rock")
    if left_action_count > len(landmark_list)/2 :
        #print ("left_rock count:{}".format(left_action_count))   
        gestures.append("left_rock")      
    
    return gestures

def detect_thumb_gesture(landmark_list):   
    gestures = []  
    right_action_count = 0    
    left_action_count = 0
    right_landmark_count = 0
    left_landmark_count = 0
    for lmks in landmark_list :
        if lmks[0][0] == 1 : 
            right_landmark_count +=1 # 右手
        else : 
            left_landmark_count += 1
        if (lmks[4][2] < lmks[3][2] < lmks[5][2] < lmks[9][2] < lmks[13][2] <  lmks[17][2] 
                and lmks[8][1] > lmks[6][1]  #食指向內彎
                and lmks[20][1] > lmks[19][1]  #小指向內彎
                and lmks[0][0] == 1): #右手
                    right_action_count += 1
        if (lmks[4][2] < lmks[3][2] < lmks[5][2] < lmks[9][2] < lmks[13][2] <  lmks[17][2] 
                and lmks[8][1] < lmks[6][1] #食指向內彎
                and lmks[20][1] < lmks[19][1]  #小指向內彎
                and lmks[0][0] == 0): #左手
                    left_action_count += 1
    if right_action_count > right_landmark_count/2 :
        #print ("right_thumbs_up count:{}".format(right_action_count))   
        gestures.append("right_thumbs_up")
    if left_action_count > left_landmark_count/2 :
        #print ("left_thumbs_up count :{}".format(left_action_count))   
        gestures.append("left_thumbs_up") 
        #print ("left_thumbs_up count:{}".format(right_action_count)) 
    return gestures

def detect_direction(landmark_list):
    #系統參數
    #建議 0.1-0.15之間
    move_thres_x = 0.13

    gestures = []
    max_x = -sys.maxsize   
    max_y = -sys.maxsize
    min_x = sys.maxsize    
    min_y = sys.maxsize    
    left_count = 0
    right_count = 0    
    up_count = 0
    down_count = 0 
    fid = 8
    (last_x,last_y) = landmark_list[0][fid][1], landmark_list[0][fid][2]
    for lmks in landmark_list[1:] :
        (x,y) = lmks[fid][1], lmks[fid][2]
        if (x > last_x) :
            right_count += 1 
        if (x < last_x) :
            left_count += 1
        if (y < last_y) :
            up_count += 1 
        if (y > last_y) :
            down_count += 1
        if x > max_x :
            max_x = x
        if x < min_x :
            min_x = x
        if y > max_y :
            max_y = y
        if y < min_y :
            min_y = y
        #cv2.line(img, ( int(last_x * w), int( last_y *h) ), ( int(x*w) , int(y*h) ), (0, 0, 255), 3)
        (last_x,last_y)  =  (x,y)
    move_range_x = max_x - min_x    
    move_range_y = max_y - min_y

    if left_count > right_count and move_range_x > move_thres_x :
        gestures.append("move_left")
    if left_count < right_count and move_range_x > move_thres_x :
        gestures.append("move_right")
    '''
    move_thres_y = 90
    move_thres_y = 0.19
    if up_count > down_count and move_range_y > move_thres_y :
        gestures.append("up") 
    if up_count < down_count and move_range_y > move_thres_y :
        gestures.append("down")
    '''
    #print ("move range:x:{},y:{}".format(move_range_x,move_range_y))
    return gestures