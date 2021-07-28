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
last_click_time = time.time()
#按下按紐的時間的持續時間
press_down_time = time.time()
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
#判斷click or drag
click_time_thres  = 0.6
click_dist_thres = 30
screen_w, screen_h = autopy.screen.size()

p_fs_x = 320
p_fs_y = 240

def init_mouse_control(w,h):
    global cam_w, cam_h
    global mouse_status , last_click_time , press_down_time
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
def control_mouse(cv2, img, lmslist):
    #需注意，取得的img size 是原始camera 的size ，與視窗顯示無關
    global cam_w, cam_h
    global mouse_status , last_click_time , press_down_time
    global p_x, p_y, c_x, c_y
    global w_ctrl_panel, h_ctrl_panel
    global top_padding, left_top_x, left_top_y
    global smothening, click_time_thres
    global auto_click_time
    global p_fs_x, p_fs_y
   
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
        
        cv2.rectangle(img, ( int(left_top_x * ratio_w), int(left_top_y * ratio_h) ), 
                      ( int((left_top_x + w_ctrl_panel) * ratio_w) , int((left_top_y + h_ctrl_panel)*ratio_h)),
                     (255, 0, 255), 1)
        
        # Step: Index finger pointing or mouse dragging
        #if fingers[1] == 1 and fingers[2] == 0:
        gesture = gesture_detector.get_finger_gesture(fingers) 
        if ((gesture == "pointer") or 
            (gesture == "scissor" and mouse_status =="left_down" and time.time() - press_down_time > click_time_thres )):
            #(gesture == "scissor" and mouse_status =="left_down" and time.time() - press_down_time > click_time_thres )):
            # Step5: 滑鼠可控範圍，轉換成全螢幕座標
            full_screen_x = np.interp(x1, (left_top_x, left_top_x + w_ctrl_panel ), (0, screen_w))
            full_screen_y = np.interp(y1, (left_top_y, left_top_y + h_ctrl_panel ), (0, screen_h))
            
            movement = math.hypot(full_screen_x - p_fs_x, full_screen_y - p_fs_y)
            print ("movement:{}".format(movement))
            # Step6: 平滑移動座標，拆成 smoothening 次移動
            # first order lag filtering
            # Y(n) = (a) Y(n-1) + (1-a) X(n) 
            # a = 1 , 
            # 1-a = 1/s 
            # 1 = s - sa    
            #c_x = p_x + (full_screen_x - p_x) / smooth
            #c_y = p_y + (full_screen_y - p_y) / smooth
            c_x = 0.85 * p_x + 0.15 * (full_screen_x) 
            c_y = 0.85 * p_y + 0.15 * (full_screen_y) 
            # kalman_filter  
            # c_x, c_y = kalman_filter.update_position(c_x, c_y)
            padding = 8
            if c_x < 3 :
                c_x = padding
            if c_y < 3 :
                c_y = padding
            if c_x >= screen_w - 3 :
                c_x = screen_w - padding
            if c_y >= screen_h - 3 :
                c_y = screen_h - padding
                
            # Step7: 自動移動滑鼠
            #autopy.mouse.move(screen_w - c_x, c_y)
            #print ("{} {}".format(c_x,c_y))
            #if (movement > 15) :
            autopy.mouse.move(c_x, c_y)
            #畫出手指位置，轉換成圖片座標
            h,w,c = img.shape
            x1, y1 = lmslist[8][1:]
            x1, y1 = int(x1 * w), int(y1 * h) 
            cv2.circle(img, (x1, y1), 4, (255, 0, 255), cv2.FILLED)
            p_x, p_y = c_x, c_y
            
            p_fs_x, p_fs_y = full_screen_x , full_screen_y

        # Step: Index and middle are up: 食指與中指都存在。點擊操作模式        
        #if gesture == "scissor":
        if gesture == "scissor":
            # Step9: 計算手指之間的距離
            # length, img, [x1, y1, x2, y2, cx, cy]
            # Step10: Click mouse if distance short
            length, img, lineInfo = gesture_detector.find_distance(lmslist, 8, 12, img, r=4)
            if length < click_dist_thres and time.time() - last_click_time > 1.0 and  mouse_status == "" :
            #if time.time() - last_click_time > 1.0 and  mouse_status == "" :
                print ("press mouse left")
                img, px, py = gesture_detector.find_center(lmslist, [4,8,12,16,20], img=img, draw=False)
                cv2.circle(img, (px, py), 4, (0, 255, 0), cv2.FILLED)
                #autopy.mouse.click() 自動按下滑鼠左鍵不放
                autopy.mouse.toggle(button=autopy.mouse.Button.LEFT,down=True)
                mouse_status = "left_down"                
                last_click_time = time.time()
                press_down_time = time.time()
            
            if length > click_dist_thres and mouse_status == "left_down" :
                print ("release mouse left")
                # 自動鬆開滑鼠左鍵
                autopy.mouse.toggle(button=autopy.mouse.Button.LEFT,down=False)
                # 需要根據滑鼠按下的時間狀態，決定是否 click or draging 意圖
                if time.time() - press_down_time < click_time_thres :
                    print ("This is click action")
                    if time.time() - auto_click_time > 0.5 :
                        # mouse.click() 與 滑鼠 click 行為有時會不同
                        autopy.mouse.click() #
                        auto_click_time = time.time()
                else :
                    print ("This is dragging action")
                #回復原始狀態
                mouse_status = ""
                
        '''  
        else :
            if (mouse_status == "left_down") :
                print ("release mouse left")
                # 自動鬆開滑鼠左鍵
                autopy.mouse.toggle(button=autopy.mouse.Button.LEFT,down=False)                
                # 需要根據滑鼠按下的時間狀態，決定是否 click or draging 意圖
                if time.time() - press_down_time < click_time_thres :
                    print ("This is click action")
                    if time.time() - auto_click_time > 1.0 :
                        autopy.mouse.click()
                        auto_click_time = time.time()
                else :
                    print ("This is dragging action")
                #回復原始狀態
                mouse_status = ""
        '''