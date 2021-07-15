'''
Created on 2021年5月29日

@author: Hsiao-Chien Tsai(蔡効謙)
'''
import cv2
import mediapipe as mp

'''
#RGB
213,12,30
69,151,38
0,107,178
'''
##drawing style, BGR system
mark_draw_spec = mp.solutions.drawing_utils.DrawingSpec()
conn_draw_spec = mp.solutions.drawing_utils.DrawingSpec()
mark_draw_spec.color = (30, 12, 213)
mark_draw_spec.thickness =3
conn_draw_spec.color = (38, 151, 69)
class HandDetector():
    '''
    手勢識別
    '''
    def __init__(self, mode=False, max_hands=2, detection_con=0.69, track_con=0.4):
        '''
        初始化
        :param mode: 使否是靜態圖片，預設为False
        :param max_hands: 偵測幾隻手，預設2隻
        :param detection_con: Hand Object Detection Confidence，0.5 以上偵測效果較好 (0.6-0.7)
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
                    mp.solutions.drawing_utils.draw_landmarks(img, handlms, mp.solutions.hands.HAND_CONNECTIONS,
                         landmark_drawing_spec = mark_draw_spec,
                         connection_drawing_spec = conn_draw_spec)
        return img

    def find_positions(self, img, hand_no=0):
        '''
        取得手勢數據 (主要為 landmarks)
        :param img: vedio frame
        :param hand_no: 手的編號
        :return: 手勢數據表，數據由 hand_id, x, y 组成，代表關鍵點 id, 位置 (x,y)
        https://google.github.io/mediapipe/images/mobile/hand_landmarks.png
        '''
        hand_label = ""
        self.lmslist = []
        if self.results.multi_hand_landmarks:
            #len(self.results.multi_hand_landmarks) 手的數量
            hand_label = self.results.multi_handedness[hand_no].classification[0].label  
            # label gives if hand is left or right
            # account for inversion in webcams
            hand_id = 0
            if hand_label == "Left":
                hand_id = 0 #左手 
            elif hand_label == "Right":
                hand_id = 1  #右手 1
            #print ("hand label:{}".format(hand_label))
            hand = self.results.multi_hand_landmarks[hand_no]            
            for id, lm in enumerate(hand.landmark):
                cx, cy = lm.x, lm.y                                      
                self.lmslist.append([hand_id, cx, cy])                
        #lmslist 長度為 21 ，每筆資料紀錄 hand_id, x , y            
        return self.lmslist
    def find_two_positions(self, img):
        '''
        取得手勢數據 (主要為 landmarks)
        :param img: vedio frame
        :return: 手勢數據表，數據由 hand_id, x, y 组成，代表關鍵點 id, 位置 (x,y)
        https://google.github.io/mediapipe/images/mobile/hand_landmarks.png
        '''
        hand_label = ""
        self.lmslist = []
        if self.results.multi_hand_landmarks:
            #print (len(self.results.multi_hand_landmarks)) # 手的數量
            for hand_no, hand in enumerate(self.results.multi_hand_landmarks) :
                h = self.results.multi_handedness[hand_no] 
                hand_label = h.classification[0].label  
                # label gives if hand is left or right
                #account for inversion in webcams
                hand_id = 0
                if hand_label == "Left":                    
                    hand_id = 0 #左手 
                elif hand_label == "Right":
                    hand_id = 1  #左手 0  
                for id, lm in enumerate(hand.landmark):                    
                        cx, cy = lm.x, lm.y                                      
                        self.lmslist.append([hand_id, cx, cy])  
        return self.lmslist