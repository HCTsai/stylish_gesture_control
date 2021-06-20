# 型男手勢控制系統 
![logo](img/jpg/hand_gesture_remote_control.jpg)

讓你用 帥氣的手勢 控制設備

## 安裝說明
### 使用 pip 安裝以下 Library
* pip install mediapipe==0.8.3
* pip install opencv-python==4.5.2.52
* pip install keyboard==0.13.5

若安裝opencv-python 遇到權限問題，可改用:
* pip install --user opencv-python==4.5.2.52

### 手勢操作電腦
運行 guesture_control.py 
立即可使用手勢操作電腦

### 手勢操作範例
* [右手比讚] --> [電腦自動按下鍵盤 page down] --> [簡報下一頁]
* [左手比讚] --> [電腦自動按下鍵盤 page up] --> [簡報上一頁]

* [右手比心] --> [電腦自動按下鍵盤 shift+F5] --> [播放簡報]
* [左手比心] --> [電腦自動按下鍵盤 esc] --> [停止播放簡報]

![star_gesture_heart](img/gif/star_heart_gesture.gif)

* [右手Rock] --> [電腦自動按下鍵盤 shift+F5] --> [播放簡報]
* [左手Rock] --> [電腦自動按下鍵盤 esc] --> [停止播放簡報]

### 設定 Hand Gestures 所對應的鍵盤動作


![gesture_to_action](img/jpg/gestures_to_actions.jpg)

data/gesture_to_keyboard.txt
可設定 gesture_name, keyboard_key 之間的對應關係

* ["right_thumbs_up"] ---> ["page down"]
* ["left_thumbs_up"] ---> ["page up"]

* ["right_heart"] ---> ["shift+F5"]
* ["left_heart"] ---> ["esc"]

### 原理說明

* 1.擷取視訊中的frame
* 2.分析 frame 出現的手，與關鍵節點 (landmarks)
[landmarks 圖](https://google.github.io/mediapipe/images/mobile/hand_landmarks.png)
* 3.將關鍵節點，放入一個 Queue 內等待分析
* 4.定期分析Queue 內，是否存在某些 Gestures
	* 規則偵測 Gesture pattern
	* 時間序列模型偵測 Gesture

* 5.將 Gesutre 轉換成鍵盤事件執行

### 疑難排解

* 問題1: 運行程式碼出現錯誤訊息

from mediapipe.python._framework_bindings import resource_util ImportError: DLL load failed: 
The specified module could not be found.
https://github.com/google/mediapipe/issues/1839

* 原因: 

沒有安裝 Microsoft Visual C++ Redistributable，無法運行opencv
https://github.com/google/mediapipe/issues/1839

* 解決方法：安裝 Microsoft Visual C++ Redistributable

https://support.microsoft.com/en-us/topic/the-latest-supported-visual-c-downloads-2647da03-1eea-4433-9aff-95f26a218cc0
https://aka.ms/vs/16/release/vc_redist.x64.exe

### 延伸應用
* 智慧製造：
![factory_application](img/jpg/factory_application.jpg)

* 明星產品發表會：
![meeting_application](img/jpg/meeting_application.jpg)