'''
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
from tool import mouse_control


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

window_name = "AI CAM"

play_mode = "N"
hide_status = False
gesture_detect_status = True
mouse_control_status = True

import PIL
from PIL import Image,ImageTk
from tkinter import Tk, Label

window_width =  int(640  * 0.8)
window_height = int(480  * 0.8)
root = Tk()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
root.bind('<Escape>', lambda e: root.quit())
root.title("AI CAM")
appHeight = 140
padding = 8
left_padding = 300
window_x = screen_w-window_width-30
window_y = screen_h- window_height -60
geo_str = str(window_width) + "x" + str(window_height) + "+"+ str(window_x) +"+" + str(window_y)
print (geo_str)
root.geometry(geo_str)
lmain = Label(root,background='white',borderwidth = 0, highlightthickness = 0)
lmain.pack()


def show_config():
    print("Window name:{}, screen_w:{}, screen_h:{}, window_width:{}, window_height:{}"
          .format(window_name,screen_w, screen_h,window_width, window_height))
show_config()

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
def show_video_window():   
    global screen_w, screen_h, window_name,window_x, window_y
    global hide_status
    #cv2.moveWindow(window_name, int( (screen_w -m window_w) * 0.97),-40)  # Move it to (40,30)  
    #window_x = int((screen_w - window_width) * 0.97)
    #window_y = 20t
    window_x = screen_w-window_width-30
    window_y = screen_h- window_height -60
    move_tk_window(window_x,window_y) 
    hide_status = False
def hide_video_window():
    global screen_w, screen_h, window_name,window_x, window_y
    global hide_status     
    #cv2.moveWindow(window_name, int( (screen_w - window_w) * 0.97),-500) # Move it to invisible area
    window_x = int( (screen_w - window_width) * 0.97)
    window_y = -600
    move_tk_window(window_x,window_y)
    hide_status = True
def hide_control_panel():
    global hand_status, window_countdown_status, window_hidden_countdown, window_show_countdown
    global hide_mode 
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
        hide_video_window()
        #改變視窗狀態 
        
        root.overrideredirect(False)
        root.wm_attributes('-transparentcolor',"")  
        
        hide_mode = True
def show_control_panel():
    global hand_status, window_countdown_status, window_hidden_countdown, window_show_countdown
    global hide_modee
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
            # 不改變視窗狀態 沿用原始設定
            root.overrideredirect(True)
            root.wm_attributes('-transparentcolor',"white")  
            # 可考慮不停的視窗狀態，使用不同的顯示方式
            show_video_window()
            hide_mode = False
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
        left = int(window_width/8.5)
        top =  int(window_height/4.5) 
        if gesture_status_label in gesture_to_desc:
            img = cv2ImgAddText(img, gesture_to_desc[gesture_status_label], left, top,(0,107,178,2),font_size=font_size)
        else :
            img = cv2ImgAddText(img, gesture_status_label, left, top,(0,107,178,2),font_size=font_size)
        # display gesture label on some frames
        gesture_hide_countdown -= 1 
        #print (gesture_hide_countdown)
        if gesture_hide_countdown == 0 :
            #每次 gesture label 顯示的 frame 數量
            gesture_hide_countdown = 15 
            #gesture_countdown_status = FALSE
            gesture_status_label = ""
    return img

def store_finger_features(img, lmslist):
    global h, w, c , gesture_status_label, font, hand_status
    global window_countdown_status, window_heightidden_countdown, window_show_countdown
    global play_mode
    if len(lmslist) > 0:
        finger_queue.put(lmslist)
        if (play_mode  == "Auto") :
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
        if (play_mode  == "Auto") :
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
    #gestures += gesture_detector.detect_heart_gesture(landmark_list)
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
    geo_str = str(window_width) + "x" + str(window_height) + "+"+ str(x) +"+" + str(y)    
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
                    #detect_gesture_sequence() #偵測連續 gesture sequence
            if self.thread_type == "f" :         
                get_frame()

img_count = 0
st = time.time()
def get_frame():    
    global img_count, st, play_mode
    fps_unit = 300 
    success, img = cap.read()
    if not success :
        return
    img_count +=1   
    img = cv2.flip(img, 1)    #
    
    #處理手勢偵測
    if gesture_detect_status :
        img = detector.find_hands(img, draw=True)
        lmslist = detector.find_positions(img)     
        store_finger_features(img, lmslist)
        
            
    img = selfie_segmentation.image_selfie_segmentation(img,stype="blur") 
    if (not hide_status) and (play_mode != "Normal") :
        #處理 opencv img 邏輯
        
        img = selfie_segmentation.image_selfie_segmentation(img,stype="") 
    
    if mouse_control_status :
        mouse_control.control_mouse(cv2, img, lmslist)
    #img = selfie_segmentation.image_selfie_segmentation(img) 
    #output_image = cv2.resize(output_image, (window_widthidth, widow_height)) 
    base_font_size = 80
    img = show_gesture_label(img,font_size=base_font_size)
    #處理 tkinter GUI 邏輯
    cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)    
    img = PIL.Image.fromarray(cv2image)
    #img = image_transparent(img)
    img = img.resize((window_width, window_height))
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(1, get_frame)
    # 計算FPS
    if (img_count % fps_unit == 0) :
        et = time.time()
        fps = img_count /(et-st)
        print ("image fps:{}".format(fps))
        img_count = 0
        st = et
        #print("fps:{}".format(1/(et-st)))
play_mode_list = ["Trans","Title", "Normal"] 
change_mode_index = 1 
def change_play_mode():
    global play_mode, play_mode_list, change_mode_index
    global hide_status 
    change_type = play_mode_list[change_mode_index % len(play_mode_list)]
    if change_type == "Trans" :
        play_mode = "Trans"
        root.overrideredirect(True)    
        root.wm_attributes('-transparentcolor','white')        
        show_video_window()
        #if cap == None:
        #    cap = cv2.VideoCapture(0)
        print ("change mode:{}".format(play_mode))
    if change_type == "Title" :
        play_mode = "Title"
        root.overrideredirect(False)  
        root.wm_attributes('-transparentcolor','white')   
        #show_frame()          
        show_video_window()    
        print ("change mode:{}".format(play_mode))
    if change_type == "Normal" :
        play_mode = "Normal"
        root.overrideredirect(False)
        root.wm_attributes('-transparentcolor',"")  
        show_video_window()   
        hide_status = False 
        print ("change mode:{}".format(play_mode))
    change_mode_index +=1 
    
def keyboard_process(k):
    global window_width, window_height, screen_w, screen_h, window_name,window_x, window_y
    global play_mode, gesture_detect_status, mouse_control_status
    scale = 20
    move_x = int(screen_w / scale)
    move_y = int(screen_h / scale)
    if (k.event_type == "down") :
        if k.name == "i" :
            window_y -= move_y
        if k.name == "k" :
            window_y += move_y
        if k.name == "l" :
            window_x += move_x
        if k.name == "j" :
            window_x -= move_x   
        move_tk_window(window_x, window_y)
        if k.name == "m" :            
            change_play_mode()
        if k.name == "h" :            
            play_mode = "H"
            hide_video_window()
            root.overrideredirect(False)
            root.wm_attributes('-transparentcolor',"")        
            #不關閉Camera 因為啟動太慢
            #cap.release()
            #cap = None
            print ("change mode:{}".format(play_mode))
        if k.name == "g" :
            gesture_detect_status = not gesture_detect_status          
            print ("change gesture status:{}".format(gesture_detect_status))
        if k.name == "c" :
            mouse_control_status = not mouse_control_status          
            print ("change mouse status:{}".format(gesture_detect_status))    
        if k.name == "a" :
            play_mode = "Auto"          
            hide_video_window()
            print ("change mode:{}".format(play_mode))
def keyboard_monitor(type):
    keyboard.hook(keyboard_process)    
if __name__ == "__main__" :     
    # 產生一個 Thread 專門監控是否有特殊手勢
    play_mode = "Trans"
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
    #
    #監聽鍵盤
    keyboard_thread = Thread(target=keyboard_monitor,args=(0,))
    keyboard_thread.start()
    #
    mouse_control.init_mouse_control(window_width,window_height)
    
    get_frame()
    root.wm_attributes('-transparentcolor','white')
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    root.mainloop() 
    stop_thread_flag.set()  # 停止Thread
    cap.release()
    

