'''
Created on 2021年5月29日

@author: Hsiao-Chien Tsai(蔡効謙)
'''
import cv2
from tool import HandDetection
from tool import filetools
from tool import gesture_detector
import time
import keyboard
import queue
from threading import Thread, Event

# 輸出中文
# Noto Sans CJK TC https://www.google.com/get/noto/#sans-hant
import numpy as np
from PIL import ImageFont, ImageDraw, Image, ImageGrab
(screen_w, screen_h) = ImageGrab.grab().size
font_path = "data/NotoSansCJKtc-Bold.otf" # <== Noto Sans CJK TC 
font_style = ImageFont.truetype(font_path, 35, encoding="utf-8")

# 创建手勢偵測物件
detector = HandDetection.HandDetector()
# 用來顯示最近偵測到的手勢
gesture_status_label = ""
gesture_hide_countdown = 15


# 用來動態 顯示 關閉 視窗
hand_status = 0
window_countdown_status = False
window_hidden_countdown = 18
window_show_countdown = 5 # 5-10
#用來記錄手勢事件
finger_queue = queue.Queue()

st = time.time()
# 監控動作的計時器
last_check = time.time()
last_gesture_detect = time.time()

# 手勢轉鍵盤動作
gesture_config_path = "data/gesture_to_keyboard.txt"
gesture_keyborad = filetools.file_to_list(gesture_config_path)
# gesture names to keyboard keys dictionary
gesture_to_keyboard = {gk[0]:gk[1] for gk in gesture_keyborad}
keyboard_to_desc = {gk[1]:gk[2] for gk in gesture_keyborad}
# 紀錄 image 資訊
h,w,c = 0,0,0 # image height, width, channel
window_w, window_h = 320, 240

def cv2ImgAddText(img, text, left, top, textColor=(255,100, 100,128)):
    
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)     
    #RGBA 
    draw.text((left, top), text, textColor, font=font_style)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

def show_video_window(name):   
    global window_w, window_h
    cv2.moveWindow(name, int( (screen_w - window_w) * 0.9),-40)  # Move it to (40,30)
def hide_video_window(name):
    global window_w, window_h
    cv2.moveWindow(name, int( (screen_w - window_w) * 0.9),-600) # Move it to invisible area
def hide_control_panel():
    global hand_status, window_countdown_status, window_hidden_countdown, window_show_countdown
    if hand_status == 1 : #原本有手變沒手
        window_countdown_status = True    
    hand_status = 0
    # hide control panel after some frames
    if window_countdown_status :
        window_hidden_countdown -= 1
    if window_hidden_countdown == 0 :
        window_countdown_status  = False 
        window_hidden_countdown = 25
        window_show_countdown = 10
        hide_video_window("AI CAM")
def show_control_panel():
    global hand_status, window_countdown_status, window_hidden_countdown, window_show_countdown
    # 如果畫面是從 沒有手，變成有手，顯示視窗
    if (hand_status == 0) :
        window_countdown_status = True 
    hand_status = 1
    # display control panel on some frames
    if window_countdown_status :
        window_show_countdown  -= 1
        if window_show_countdown == 0 :
            window_countdown_status  = False 
            window_hidden_countdown = 25
            window_show_countdown = 10
            show_video_window("AI CAM")
def show_gesture_label(img):
     #chi_font = True
        #if chi_font == True :
    global gesture_status_label, gesture_hide_countdown
    if gesture_status_label != ""  :
        # OpenCV putText() only support ASCII font , BGR color
        # cv2.putText(img, gesture_status_label, (20, 70), cv2.FONT_HERSHEY_DUPLEX, 2.5, (100, 100, 255),3)
        #RGBA 
        img = cv2ImgAddText(img, keyboard_to_desc[gesture_status_label], 20, 5,(255,100,100,218))
        # display gesture label on some frames
        gesture_hide_countdown -= 1 
        #print (gesture_hide_countdown)
        if gesture_hide_countdown == 0 :
            gesture_hide_countdown = 15 
            #gesture_countdown_status = FALSE
            gesture_status_label = ""
    return img

def store_finger_features(img, lmslist, hand_label):
    global h, w, c , gesture_status_label, font, hand_status, window_countdown_status, window_hidden_countdown, window_show_countdown
    if len(lmslist) > 0:
        finger_queue.put(lmslist)
        show_control_panel()
        
        # 顯示手指
        # cnt = gesture_detector.detect_finger_count(img, lmslist, hand_label)
        # 文字/左上角座標/字體/字體大小scale/顏色/字体粗細
        #cv2.putText(img, str(cnt), (25, 100), cv2.FONT_HERSHEY_DUPLEX, 4, (0, 0, 255),8)        
        '''
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)        
        draw.text((20, 70),  "中文", font = font , fill = (100, 100, 255, 128))
        img = np.array(img_pil)
        '''
        #
        #cv2.moveWindow("AI CAM", 1500,-40)  # Move it to (40,30)
    else : # 畫面沒有手。開始倒數，倒數結束關閉視窗
        hide_control_panel()
    #    cv2.moveWindow("AI CAM", 2500,-40)  # Move it to (40,30)
   
        
def gestures_to_keyboard(gestures):
    print ("偵測到手勢事件:{}".format(gestures))    
    keyboard_list = []
    for g in gestures  :
        keyboard_list.append(gesture_to_keyboard[g]) 
    return list(set(keyboard_list))
def check_gustures():
    """
    檢查 finger_queue 內是否有特殊的 手勢
    """    
    global last_gesture_detect ,gesture_status_label, gesture_countdown_status
    print ("check_gustures")
    landmark_list = list(finger_queue.queue) 
    #while not finger_queue.empty() :
    #    finger_queue.get_nowait()  
    #finger_queue.queue.clear() hanging
    dup_action_thres = 1.0    
    check_time = time.time()
    #detect_finger_features(img, lmslist, hand_label)
    gestures = gesture_detector.detect_rock_gesture(landmark_list)
    gestures += gesture_detector.detect_heart_gesture(landmark_list)
    gestures += gesture_detector.detect_thumb_gesture(landmark_list)
    #gestures += detect_direction(img, landmark_list)
    if len(gestures) > 0 and check_time - last_gesture_detect > dup_action_thres:
        keyboard_actions = gestures_to_keyboard(gestures)
        for k in keyboard_actions :
            keyboard.press_and_release(k)
        last_gesture_detect = check_time
        gesture_status_label = keyboard_actions[-1]
    finger_queue.queue.clear()

class GustureMonitorThread(Thread):
    
    # 專門監控是否有特殊手勢的 Thread
    def __init__(self, event, interval):
        Thread.__init__(self)
        self.stopped = event
        self.interval = interval

    def run(self):          
        while not self.stopped.wait(self.interval):          
            if finger_queue.qsize() > 3  :            
                check_gustures()  
            
            # call a function
if __name__ == "__main__" :     
    # 產生一個 Thread 專門監控是否有特殊手勢
    gesture_monitor_interval = 0.35          
    stop_thread_flag = Event()
    gesture_thread = GustureMonitorThread(stop_thread_flag, interval = gesture_monitor_interval)
    gesture_thread.start()
    # 打開 Web cam
    cap = cv2.VideoCapture(0)
    # 讀取 video frame
    img_count = 0
    fps_unit = 1000 
    while cap.isOpened():
        success, img = cap.read()
        
        h, w, c = img.shape
        img_count += 1
        if success:
            # 檢測手 
            img = detector.find_hands(img, draw=True)
            # 取得 手的 landmarks , hand_label 
            lmslist, hand_label = detector.find_positions(img,pos_type=0)
            # 計算 FPS
            if (img_count % fps_unit == 0) :
                et = time.time()
                duration = et-st 
                fps1 = img_count / duration
                print ("image fps:{}".format(fps1))
                img_count = 1
                st = et
            # 手指特徵抽取
            # 將手指特徵放到 queue 內，並顯示手指畫面
            store_finger_features(img, lmslist, hand_label)
            #  
        window_name = "AI CAM"           
        #cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        #cv2.setWindowProperty(window_name,cv2.WND_PROP_FULLSCREEN,0) 
         
        img = cv2.resize(img, (window_w, window_h))   
        img = show_gesture_label(img)
       
        
        
        cv2.imshow(window_name, img)
        #always on top      
        
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)  
       
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
    stop_thread_flag.set()  # 停止Thread
    cap.release()
    cv2.destroyAllWindows()

