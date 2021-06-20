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

# 创建手勢偵測物件
detector = HandDetection.HandDetector()
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
g2k = {gk[0]:gk[1] for gk in gesture_keyborad}
# 紀錄 image 資訊
h,w,c = 0,0,0 # image height, width, channel

def store_finger_features(img, lmslist, hand_label):
    
    global h, w, c 
    if len(lmslist) > 0:
        finger_queue.put(lmslist) 
        
        # 顯示手指
        # cnt = gesture_detector.detect_finger_count(img, lmslist, hand_label)
        # 文字/左上角座標/字體/字體大小/顏色/字体粗細
        #cv2.putText(img, str(cnt), (25, 100), cv2.FONT_HERSHEY_DUPLEX, 4, (0, 0, 255),8)
        
def gestures_to_keyboard(gestures):
    print ("偵測到手勢事件:{}".format(gestures))    
    keyboard_list = []
    for g in gestures  :
        keyboard_list.append(g2k[g]) 
    return list(set(keyboard_list))
def check_gustures():
    """
    檢查 finger_queue 內是否有特殊的 手勢
    """    
    global last_gesture_detect
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
    if len(gestures) > 0 and check_time-last_gesture_detect > dup_action_thres:
        for k in gestures_to_keyboard(gestures) :
            keyboard.press_and_release(k)
            
        last_gesture_detect = check_time
        
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
    gesture_monitor_interval = 0.4          
    stop_thread_flag = Event()
    thread = GustureMonitorThread(stop_thread_flag, interval = gesture_monitor_interval)
    thread.start()
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
        cv2.imshow('Gesture Image', img)    
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
    stop_thread_flag.set()  # 停止Thread
    cap.release()
    cv2.destroyAllWindows()

