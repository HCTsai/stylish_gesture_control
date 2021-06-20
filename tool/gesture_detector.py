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
        if (tid == 8)  :
            #print ("食指位置:{},{}".format(x,y))
            #finger_queue.put((lmslist[tid][1],lmslist[tid][2]))
            pass
        cv2.circle(img, (x, y), 10, (0, 255, 0), cv2.FILLED)
        # 如果是大拇指，如果大拇指指尖x位置大於大拇指第二關節的位置，則認為大拇指打開，否則認為大拇指關閉
        # 還要判斷手
        if tid == 4 :
            if hand_label == "Right" :
                if landmark_list[tid][1] > landmark_list[tid - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else : #左手
                if landmark_list[tid][1] < landmark_list[tid - 1][1]:
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
    return finger_count

def detect_heart_gesture(landmark_list):
    
    gestures = []  
    right_action_count = 0    
    left_action_count = 0
    for lmks in landmark_list[0:] :
        if ( (lmks[4][2] < lmks[12][2] and lmks[4][2] < lmks[16][2] and lmks[4][2] < lmks[20][2]) and  
             (lmks[8][2] < lmks[12][2] and lmks[4][2] < lmks[16][2] and lmks[4][2] < lmks[20][2]) and  
            #小指 高於 中指，無名指
            lmks[8][1] > lmks[4][1] and  math.fabs(lmks[8][2] - lmks[4][2]) < 0.05 #食指拇指交叉
            and lmks[0][0] == 1): # 右手
                    right_action_count += 1
        if ( (lmks[4][2] < lmks[12][2] and lmks[4][2] < lmks[16][2] and lmks[4][2] < lmks[20][2]) and  
             (lmks[8][2] < lmks[12][2] and lmks[4][2] < lmks[16][2] and lmks[4][2] < lmks[20][2]) and  
            #小指 高於 中指，無名指
            lmks[8][1] < lmks[4][1] and  math.fabs(lmks[8][2] - lmks[4][2]) < 0.05#食指拇指交叉
            and lmks[0][0] == 0): # 左手
                    left_action_count += 1
        #print (lmks[8][2] - lmks[4][2])         
    if right_action_count > len(landmark_list)/2 :
        print ("right_heart:{}".format(right_action_count))   
        gestures.append("right_heart")
    if left_action_count > len(landmark_list)/2 :
        print ("left_heart:{}".format(left_action_count))   
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
            lmks[4][1] > lmks[3][1] #拇指內灣 
            and lmks[0][0] == 1): # 右手
                    right_action_count += 1
        if (lmks[8][2] < lmks[20][2] and  
            lmks[20][2] < lmks[12][2] and lmks[20][2] < lmks[16][2] and 
            lmks[4][1] < lmks[3][1] 
            and lmks[0][0] == 0): #左手
                    left_action_count += 1
                 
    if right_action_count > len(landmark_list)/2 :
        print ("right_rock:{}".format(right_action_count))   
        gestures.append("right_rock")
    if left_action_count > len(landmark_list)/2 :
        print ("left_rock:{}".format(left_action_count))   
        gestures.append("left_rock")      
    
    return gestures

def detect_thumb_gesture(landmark_list):   
    gestures = []  
    right_action_count = 0    
    left_action_count = 0
    for lmks in landmark_list[0:] :
        if (lmks[4][2] < lmks[3][2] < lmks[5][2] < lmks[9][2] < lmks[13][2] <  lmks[17][2] 
                and lmks[8][1] < lmks[6][1]  #食指向內彎
                and lmks[0][0] == 1): #右手
                    right_action_count += 1
        if (lmks[4][2] < lmks[3][2] < lmks[5][2] < lmks[9][2] < lmks[13][2] <  lmks[17][2] 
                and lmks[8][1] > lmks[6][1] #食指向內彎
                and lmks[0][0] == 0): #左手
                    left_action_count += 1
    if right_action_count > len(landmark_list)/2 :
        print ("right_thumbs_up:{}".format(right_action_count))   
        gestures.append("right_thumbs_up")
    if left_action_count > len(landmark_list)/2 :
        print ("left_thumbs_up:{}".format(left_action_count))   
        gestures.append("left_thumbs_up") 
        print ("left_thumbs_up:{}".format(right_action_count)) 
    return gestures

def detect_direction(img, landmark_list):
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
        if (x < last_x) :
            right_count += 1 
        if (x > last_x) :
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
        gestures.append("left")
    if left_count < right_count and move_range_x > move_thres_x :
        gestures.append("right")
    '''
    move_thres_y = 90
    move_thres_y = 0.19
    if up_count > down_count and move_range_y > move_thres_y :
        gestures.append("up") 
    if up_count < down_count and move_range_y > move_thres_y :
        gestures.append("down")
    '''
    print ("move range:x:{},y:{}".format(move_range_x,move_range_y))
    return gestures