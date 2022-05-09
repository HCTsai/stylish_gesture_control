'''
Created on 2021年7月22日

@author: Hsiao-Chien Tsai(蔡効謙)
'''
import numpy as np
import time
import autopy
from tool import gesture_detector
from tool import kalman_filter
import math
#status
mouse_status =""
#
last_left_click_time = time.time()
last_right_click_time = time.time()
#按下按紐的時間的持續時間
left_press_down_time = time.time()
#避免重複auto click
auto_click_time = time.time()
# control and display 
p_x, p_y = 0, 0
c_x, c_y = 0, 0
cam_w, cam_h = 640, 480
w_ctrl_panel, h_ctrl_panel = 400, 160
top_padding = 50
left_top_x , left_top_y = top_padding,top_padding
smooth = 7 # 均線移動的意思
smooth = 10 
p_weight = 0.85
#判斷click or drag
click_time_thres  = 0.9
click_dist_thres = 25
screen_w, screen_h = autopy.screen.size()

p_fs_x = 320
p_fs_y = 240

movement_list = []
filter = "weight_speed"

        
import queue
mouse_gesture_list = []

    


def init_mouse_control(w,h):
    global cam_w, cam_h
    global mouse_status , last_left_click_time , left_press_down_time
    global p_x, p_y, c_x, c_y
    global w_ctrl_panel, h_ctrl_panel
    global top_padding, left_top_x, left_top_y
    global smothening
    #初始化數值
    cam_w, cam_h = w, h
    print ("initial camera:{},{}".format(cam_w,cam_h))
    #wh_ratio = cam_w/cam_h
    w_control_ratio = 0.60
    h_control_ratio = 0.33 
    w_ctrl_panel = int(cam_w * w_control_ratio)   
    h_ctrl_panel = int(cam_h * h_control_ratio)
    top_padding  = int(cam_h/9) 
    left_top_x = int((cam_w-w_ctrl_panel)/2)
    left_top_y = top_padding
    smoothening = 7 # 8-12 
    screen_w, screen_h = autopy.screen.size()
    
def mouse_smooth_move(cx, cy, px, py,move_dist=20):
    global screen_w, screen_h
    #calibration
    padding = 10
    if cx < 3 :
        cx = padding
    if cy < 3 :
        cy = padding
    if cx >= screen_w - 3 :
        cx = screen_w - padding
    if cy >= screen_h - 3 :
        cy = screen_h - padding
    #step 每次移動距離
    dx = move_dist # 每次移動距離 
    if (cx < px) :
        dx = -move_dist
    dy = move_dist # 每次移動距離 
    if (cy < py) :
        dy = -move_dist
    tx, ty = px, py
    while ( math.fabs(tx - cx) > move_dist and math.fabs(ty - cy) > move_dist) :
        tx, ty = tx + dx , ty + dy
        #print ("smoth move:{} {}".format(tx,ty))
        autopy.mouse.move(tx , ty)
    #print ("smoth move:{} {}".format(cx,cy))
    autopy.mouse.move(cx, cy)
stable_count = 0
move_count = 0
test_count = 0

def get_dynamic_weight(px,py,cx,cy):
    
    global movement_list
    global move_count, stable_count, test_count
    global p_weight
    movement = math.hypot(cx - px, cy - py)
    movement_list.append(movement)
    #print ("movement:{}".format(movement))
    test_count += 1
    weight = p_weight
    if movement < 20: # 如何設計一個參數 adaptive 調整 stop intent and move intent 
        weight = 0.95 
        #print ("stable")
        stable_count += 1
        #print ("decrease move speed")
    elif movement > 150 : #80-90
        weight = 0.03
        #print ("increase move speed")
        #print ("speed")
        move_count += 1
    else :
        # 手移動越快， weight 越小，座標變動越大，即時追蹤真實座標
        # 手移動越慢， weight 越大，座標變動越小，越穩定
        # [15,150] --->[0.95,0.05]
        weight = 0.95 - ((movement - 20)/(150-20) * (0.95-0.03)) 
        #print ("move")
        move_count+=1
        #print ("m:{} w:{}".format(movement,w))
    if (test_count % 500 == 0) :
        print ("move/test  ={}/{} = {}".format(move_count,test_count,str(move_count/test_count)))
    return weight
def release_mouse():
    global auto_click_time, mouse_status
    autopy.mouse.toggle(button=autopy.mouse.Button.LEFT,down=False)  
    #autopy.mouse.toggle(button=autopy.mouse.Button.RIGHT,down=False)             
    # 需要根據滑鼠按下的時間狀態，決定是否 click or draging 意圖
    out_text = ""
    mouse_click_duration = time.time() - left_press_down_time 
    if mouse_click_duration > 0.05  :
        #print ("This is click action")
        if mouse_click_duration < click_time_thres :
            # autopy.mouse.click() #
            out_text  = "click"
        else :
            print ("This is dragging action")
            out_text = "drag"
    mouse_status = ""
         
    return out_text 
       
def control_mouse(cv2, img, lmslist):
    #需注意，取得的img size 是原始camera 的size ，與視窗顯示無關
    global cam_w, cam_h
    global mouse_status , last_left_click_time , last_right_click_time , left_press_down_time
    global p_x, p_y, c_x, c_y
    global w_ctrl_panel, h_ctrl_panel
    global top_padding, left_top_x, left_top_y
    global smothening, click_time_thres
    global auto_click_time
    global p_fs_x, p_fs_y
    global filter
    
    
    label_text = ""
    if len(lmslist) != 0:
        #初始化滑鼠位置
        #相對座標
        x1, y1 = lmslist[8][1:]
        x2, y2 = lmslist[12][1:]
        
        #轉換成顯示絕對座標
        x1 = int(x1 * cam_w) 
        y1 = int(y1 * cam_h) 
        x2 = int(x2 * cam_w) 
        y2 = int(y2 * cam_h) 
        # Step: 取得手指狀態
        _, fingers = gesture_detector.detect_finger_count(img, lmslist, hand_label=lmslist[0][0])
        
        # 畫出滑鼠可控制範圍，要使用圖片座標
        
        h,w,_ = img.shape
        ratio_w = w/cam_w 
        ratio_h = h/cam_h
        # control area
        
        cv2.rectangle(img, ( int(left_top_x * ratio_w), int(left_top_y * ratio_h) ), 
                      ( int((left_top_x + w_ctrl_panel) * ratio_w) , int((left_top_y + h_ctrl_panel)*ratio_h)),
                     (255, 0, 255), 1)
        
        # Step: Index finger pointing or mouse dragging
        #if fingers[1] == 1 and fingers[2] == 0:
        gesture = gesture_detector.get_finger_gesture(fingers) 
        
       
        
        # 移動corsor 或 drag
        if ((gesture == "pointer") or 
            (gesture == "scissor" and mouse_status =="left_down" and time.time() - left_press_down_time > click_time_thres )):
            #(gesture == "scissor" and mouse_status =="left_down" and time.time() - left_press_down_time > click_time_thres )):
            # Step5: 滑鼠可控範圍，轉換成全螢幕座標
            full_screen_x = np.interp(x1, (left_top_x, left_top_x + w_ctrl_panel ), (0, screen_w))
            full_screen_y = np.interp(y1, (left_top_y, left_top_y + h_ctrl_panel ), (0, screen_h))
            
            # Step6: 平滑移動座標，拆成 smoothening 次移動
            
            if (filter) :
                weight = get_dynamic_weight(p_fs_x, p_fs_y, full_screen_x, full_screen_y)
                c_x = weight * p_x + (1-weight ) * (full_screen_x) 
                c_y = weight * p_y + (1-weight ) * (full_screen_y) 
                # kalman_filter  
                # c_x, c_y = kalman_filter.update_position(c_x, c_y)
                # Step7: 自動移動滑鼠
                #autopy.mouse.move(screen_w - c_x, c_y)
                #print ("{} {}".format(c_x,c_y))
                #if (movement > 15) :
                mouse_smooth_move(c_x, c_y, p_x, p_y, move_dist=10)
            else :
                mouse_smooth_move(full_screen_x, full_screen_y, p_fs_x, p_fs_y, move_dist=10) 
            #utopy.mouse.move(c_x, c_y)
            #畫出手指位置，轉換成圖片座標
            h,w,c = img.shape
            x1, y1 = lmslist[8][1:]
            x1, y1 = int(x1 * w), int(y1 * h) 
            cv2.circle(img, (x1, y1), 3, (0, 255, 0), cv2.FILLED)
            p_x, p_y = c_x, c_y
            p_fs_x, p_fs_y = full_screen_x , full_screen_y
        
                
        # Step: Index and middle are up: 食指與中指都存在。點擊操作模式        
        #if gesture == "scissor":
        if gesture == "scissor": # click buttom
            # Step9: 計算手指之間的距離
            # length, img, [x1, y1, x2, y2, cx, cy]
            # Step10: Click mouse if distance short
            length, img, lineInfo = gesture_detector.find_distance(lmslist, 8, 12, img,draw=False, r=4)
            if length < click_dist_thres and  mouse_status == "" and time.time() - last_left_click_time > 1.0  :
            #if time.time() - last_left_click_time > 1.0 and  mouse_status == "" :
                print ("press mouse left")
                #img, px, py = gesture_detector.find_center(lmslist, [4,8,12,16,20], img=img, draw=False)
                #cv2.circle(img, (px, py), 4, (0, 255, 0), cv2.FILLED)
                #autopy.mouse.click() 自動按下滑鼠左鍵不放                
                
                autopy.mouse.toggle(button=autopy.mouse.Button.LEFT,down=True)
                
                mouse_status = "left_down"                
                last_left_click_time = time.time()
                left_press_down_time = time.time()
            
            if length > click_dist_thres and mouse_status == "left_down" :
                out_text = release_mouse()
                label_text = out_text
        if gesture == "three" :
            if time.time() - last_right_click_time > 1.0 and  mouse_status == "" : 
                mouse_status = "right_down"  
                
                autopy.mouse.toggle(button=autopy.mouse.Button.RIGHT,down=True) 
                autopy.mouse.toggle(button=autopy.mouse.Button.RIGHT,down=False)  
                                     
                last_right_click_time = time.time()
                mouse_status = ""  
                print (mouse_status)
        if (gesture == "pointer") and (mouse_status =="left_down" ) :            
            out_text = release_mouse()
            label_text = out_text
        '''  
        else :
            if (mouse_status == "left_down") :
                print ("release mouse left")
                # 自動鬆開滑鼠左鍵
                autopy.mouse.toggle(button=autopy.mouse.Button.LEFT,down=False)                
                # 需要根據滑鼠按下的時間狀態，決定是否 click or draging 意圖
                if time.time() - left_press_down_time < click_time_thres :
                    print ("This is click action")
                    if time.time() - auto_click_time > 1.0 :
                        autopy.mouse.click()
                        auto_click_time = time.time()
                else :
                    print ("This is dragging action")
                #回復原始狀態
                mouse_status = ""
        '''
    return ""
    #return label_text