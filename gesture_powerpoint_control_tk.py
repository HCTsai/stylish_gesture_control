'''n
Created on 2021年5月29日

@author: Hsiao-Chien Tsai(蔡効謙)
'''
import cv2
from tool import HandDetection
from tool import filetools
from tool import gesture_detector
from tool import selfie_segmentation
import time
import keyboard
import queue
from threading import Thread
from threading import Event as ev

# 設定 PYTHONPATH 為專案的根目錄

# 輸出中文
# Noto Sans CJK TC https://www.google.com/get/noto/#sans-hant
import numpy as np
from PIL import ImageFont, ImageDraw, Image, ImageGrab
(screen_w, screen_h) = ImageGrab.grab().size
font_path = "data/NotoSansCJKtc-Bold.otf" # <== Noto Sans CJK TC 
fs = ImageFont.truetype(font_path, 53, encoding="utf-8")
# 创建手勢偵測物件
detector = HandDetection.HandDetector()
# 用來顯示最近偵測到的手勢
gesture_status_label = ""
gesture_hide_countdown = 10


# 用來動態 顯示 關閉 視窗
hand_status = 0
window_countdown_status = False
window_hidden_countdown = 10
window_show_countdown = 10 # 5-10
#用來記錄finger landmark sequence 
finger_queue = queue.Queue()
#紀錄 gesture sequence
gesture_queue = queue.Queue()


# 監控動作的計時器
last_check = time.time()
last_gesture_detect = time.time()

# 手勢轉鍵盤動作
gesture_config_path = "data/gesture_to_keyboard.txt"
gesture_keyborad = filetools.file_to_list(gesture_config_path)
# gesture names to keyboard keys dictionary
gesture_to_keyboard = {gk[0]:gk[1] for gk in gesture_keyborad}
gesture_to_desc = {gk[0]:gk[2] for gk in gesture_keyborad}
# 紀錄 image 資訊
h,w,c = 0,0,0 # image height, width, channel
window_w, window_h = 400, 300
window_name = "AI CAM"



import PIL
from PIL import Image,ImageTk
from tkinter import Tk, Label

window_width = 400
widow_height = 300
root = Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.bind('<Escape>', lambda e: root.quit())
appHeight = 140
padding = 8
left_padding = 300
#geo_str = str(window_width) + "x" + str(widow_height) + "+"+ str(screen_width-window_width-30) +"+" + str(screen_height - widow_height -60)
left_padding = 300
geo_str = str(window_width) + "x" + str(widow_height) + "+"+ str(screen_width-window_width-30) +"+" + str(20)
print (geo_str)
root.geometry(geo_str)
lmain = Label(root,background='white',borderwidth = 0, highlightthickness = 0)
lmain.pack()


def show_config():
    print("Window name:{}, screen_w:{}, screen_h:{}, window_w:{}, window_h:{}"
          .format(window_name,screen_w, screen_h,window_w, window_h))
show_config()
# N: Normal Display
# H: Auto Hide 
window_display_mode = "A"
def cv2ImgAddText(img, text, left, top, textColor=(255,100, 100,128),font_size=35):
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    #RGBA 
    #fs = ImageFont.truetype(font_path, font_size, encoding="utf-8")
    #, stroke_width=1, stroke_fill=stroke_color
    stroke_color = (255,255,255)
    draw.text((left, top), text, textColor, font=fs, stroke_width=3, stroke_fill=stroke_color)
    #draw.text((left, top), text, textColor, font=fs)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
def show_video_window(name):   
    
    global window_w, window_h, screen_w, screen_h, window_name
    #cv2.moveWindow(window_name, int( (screen_w - window_w) * 0.97),-40)  # Move it to (40,30)  
    move_tk_window(int((screen_w - window_w) * 0.97),20) 
def hide_video_window(name):
    global window_w, window_h, screen_w, screen_h, window_name
    #cv2.moveWindow(window_name, int( (screen_w - window_w) * 0.97),-500) # Move it to invisible area
    move_tk_window(int( (screen_w - window_w) * 0.97),-500)
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
        hide_video_window(window_name)
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
            show_video_window(window_name)
def show_gesture_label(img, font_size=35):
     #chi_font = True
        #if chi_font == True :
    global gesture_status_label, gesture_hide_countdown
    if gesture_status_label != ""  :
        # OpenCV putText() only support ASCII font , BGR color
        # cv2.putText(img, gesture_status_label, (20, 70), cv2.FONT_HERSHEY_DUPLEX, 2.5, (100, 100, 255),3)
        #RGBA 
        '''
        213,12,30 R
        69,151,38 G
        0,107,178 B
        '''
        left = 30
        top = 50
        if gesture_status_label in gesture_to_desc:
            img = cv2ImgAddText(img, gesture_to_desc[gesture_status_label], left, top,(0,107,178,2),font_size=font_size)
        else :
            img = cv2ImgAddText(img, gesture_status_label, left, top,(0,107,178,2),font_size=font_size)
        # display gesture label on some frames
        gesture_hide_countdown -= 1 
        #print (gesture_hide_countdown)
        if gesture_hide_countdown == 0 :
            gesture_hide_countdown = 15 
            #gesture_countdown_status = FALSE
            gesture_status_label = ""
    return img

def store_finger_features(img, lmslist):
    global h, w, c , gesture_status_label, font, hand_status
    global window_countdown_status, window_hidden_countdown, window_show_countdown
    if len(lmslist) > 0:
        finger_queue.put(lmslist)
        if (window_display_mode  == "A") :
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
        if (window_display_mode  == "A") :
            hide_control_panel()
    #    cv2.moveWindow("AI CAM", 2500,-40)  # Move it to (40,30)
   
        
def gestures_to_keyboard(gestures):
    print ("偵測到手勢事件:{}".format(gestures))    
    keyboard_list = []
    for g in gestures  :
        if g in gesture_to_keyboard :
            keyboard_list.append(gesture_to_keyboard[g]) 
    return list(set(keyboard_list))
def detect_gestures():
    """
    檢查 finger_queue 內是否有特殊的 手勢
    """    
    global last_gesture_detect ,gesture_status_label, gesture_countdown_status
    #print ("check_gustures")
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
    #gestures += gesture_detector.detect_click_area(landmark_list)
    #gestures += gesture_detector.detect_click_gesture(landmark_list)
    #gestures += gesture_detector.detect_direction(landmark_list)
    #print(gesture_detector.detect_click_gesture(landmark_list))
    if len(gestures) > 0 and check_time - last_gesture_detect > dup_action_thres:
        keyboard_actions = gestures_to_keyboard(gestures)
        for k in keyboard_actions :
            if k != "" : # empty keypress in configurations
                keyboard.press_and_release(k)
        last_gesture_detect = check_time
        gesture_status_label = gestures[-1]
        #
        #record gesture sequence
        for g in gestures :
            gesture_queue.put(g)
    finger_queue.queue.clear()
def image_transparent(image_rgba):
    newImage = []
    for item in image_rgba.getdata():
        if item[:3] == (255, 255, 255):
            newImage.append((255, 255, 255, 0))
        else:
            newImage.append(item)

    image_rgba.putdata(newImage)
    return image_rgba    
def detect_gesture_sequence():
    """
    檢查 finger_queue 內是否有特殊的 手勢
    """    
    global last_gesture_detect ,gesture_status_label, gesture_countdown_status
    #print ("check_gustures")
    seq_list = list(gesture_queue.queue) 
    #
    #print (seq_list[-5:-1])
    if len(seq_list) > 2 and "click_3" == seq_list[-2] and "right_thumbs_up" == seq_list[-1]:
        print ("----------------")
        keyboard.press_and_release("3+enter")
        gesture_status_label = "跳頁"
        gesture_queue.queue.clear()
def move_tk_window(x,y):
    geo_str = str(window_width) + "x" + str(widow_height) + "+"+ str(x) +"+" + str(y)    
    root.geometry(geo_str)
class GustureMonitorThread(Thread):
    
    # 專門監控是否有特殊手勢的 Thread
    def __init__(self, event, interval, thread_type):
        Thread.__init__(self)
        self.stopped = event
        self.interval = interval
        self.thread_type = thread_type

    def run(self):          
        while not self.stopped.wait(self.interval):
            if self.thread_type == "g"    :      
                if finger_queue.qsize() > 3  :            
                    detect_gestures()  # 偵測 single gesture
                    detect_gesture_sequence() #偵測連續 gesture sequence
            if self.thread_type == "f" :         
                show_frame()

img_count = 0
st = time.time()
def show_frame():    
    global img_count,st
    fps_unit = 300 
    success, img = cap.read()
    if not success :
        return
    img_count +=1 
    #
    #img = cv2.resize(img,((int(window_width/4), int(widow_height/4))))
    #
    img = cv2.flip(img, 1)
    # 處理手勢偵測
    img = detector.find_hands(img, draw=True)
        # 取得 手的 landmarks , hand_label 
        #lmslist = detector.find_two_positions(img)
    lmslist = detector.find_positions(img)
        # 手指特徵抽取h
        # 將手指特徵放到 queue 內，並顯示手指畫面
    store_finger_features(img, lmslist)
    #處理 opencv img 邏輯
    img = selfie_segmentation.image_selfie_segmentation_bg(img) 
    #output_image = cv2.resize(output_image, (window_width, widow_height)) 
    base_font_size = 80
    img = show_gesture_label(img,font_size=base_font_size)
    #處理 tkinter GUI 邏輯
    cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)    
    img = PIL.Image.fromarray(cv2image)
    #img = image_transparent(img)
    img = img.resize((window_width, widow_height))
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(40, show_frame)
    if (img_count % fps_unit == 0) :
        et = time.time()
        fps = img_count /(et-st)
        print ("image fps:{}".format(fps))
        img_count = 0
        st = et
        #print("fps:{}".format(1/(et-st))) 
    
if __name__ == "__main__" :     
    # 產生一個 Thread 專門監控是否有特殊手勢
    global window_mode
    gesture_monitor_interval = 0.35          
    stop_thread_flag = ev()
    gesture_thread = GustureMonitorThread(stop_thread_flag, gesture_monitor_interval,thread_type="g")
    gesture_thread.start()
    # 打開 Web cam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3); 
    #cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) #captureDevice = camera
    # 讀取 video frame
    '''
    frame_ana_interval = 0.03          
    stop_frame_thread_flag = ev()
    frame_thread = GustureMonitorThread(stop_frame_thread_flag,frame_ana_interval,thread_type="f")
    frame_thread.start()
    '''
    show_frame()
    root.wm_attributes('-transparentcolor','white')
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    root.mainloop() 
    stop_thread_flag.set()  # 停止Thread
    cap.release()
    

