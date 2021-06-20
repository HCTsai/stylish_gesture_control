'''
Created on 2021年5月29日

@author: HC
'''
import cv2
import mediapipe as mp



class HandDetector():
    '''
    手勢識別
    '''
    def __init__(self, mode=False, max_hands=2, detection_con=0.65, track_con=0.4):
        '''
        初始化
        :param mode: 使否是靜態圖片，預設为False
        :param max_hands: 偵測幾隻手，預設2隻
        :param detection_con: Hand Object Detection Confidence，0.5 以上偵測效果較好
        :param track_con: Landmarks 最小Confidence，低於0.5 使偵測可靈敏一點
         https://solutions.mediapipe.dev/hands#min_detection_confidence.
         https://solutions.mediapipe.dev/hands#min_tracking_confidence
        '''
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        self.hands = mp.solutions.hands.Hands(self.mode, self.max_hands, self.detection_con, self.track_con)

    def find_hands(self, img, draw=True):
        '''
               檢測手
        :param img: video frame
        :param draw: 手否畫出手適中的節點與連線
        :return: 處理過的圖片
        '''
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # 处理图片，检测是否有手势，将数据存进self.results中
        self.results = self.hands.process(imgRGB)
        if draw:
            if self.results.multi_hand_landmarks:
                for handlms in self.results.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(img, handlms, mp.solutions.hands.HAND_CONNECTIONS)
        return img

    def find_positions(self, img, hand_no=0, pos_type=1):
        '''
               取得手勢數據 (主要為 landmarks)
        :param img: vedio frame
        :param hand_no: 手的編號
        :return: 手勢數據表，數據由 id, x, y 组成，代表關鍵點 id, 位置 (x,y)
        https://google.github.io/mediapipe/images/mobile/hand_landmarks.png
        '''
        hand_label = ""
        self.lmslist = []
        if self.results.multi_hand_landmarks:
            #len(self.results.multi_hand_landmarks) 手的數量
            
            hand_label = self.results.multi_handedness[hand_no].classification[0].label  
            # label gives if hand is left or right
            #account for inversion in webcams
            hand_id = 0
            if hand_label == "Left":
                hand_label = "Right"
                hand_id = 1 #右手 
            elif hand_label == "Right":
                hand_label = "Left"   
                hand_id = 0  #左手 0
            hand = self.results.multi_hand_landmarks[hand_no]
            
            for id, lm in enumerate(hand.landmark):
                if pos_type == 0 :
                    cx, cy = lm.x, lm.y                                      
                    self.lmslist.append([hand_id, cx, cy])
                else :  
                    
                    h, w, c = img.shape
                    #print ("image shape:{},{},{}".format(h,w,c))
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.lmslist.append([hand_id, cx, cy])  
            '''
            hand = self.results.multi_hand_landmarks[1]
            print ("hand_1")
            for id, lm in enumerate(hand.landmark):
                if pos_type == 0 :
                    cx, cy = lm.x, lm.y  
                    print ([hand_id, cx, cy])                    
                    #self.lmslist.append([hand_id, cx, cy])
                else :  
                    h, w, c = img.shape
                    #print ("image shape:{},{},{}".format(h,w,c))
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    #self.lmslist.append([hand_id, cx, cy])  
            '''
        #lmslist 長度為 21 ，每筆資料紀錄 hand_id, x , y            
        return self.lmslist, hand_label
