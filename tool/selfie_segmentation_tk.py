'''
Created on 2021年7月14日

@author: Hsiao-Chien Tsai(蔡効謙)
'''
import cv2
import mediapipe as mp
import numpy as np
import keyboard
from threading import Thread
from keyboard import play
from hashlib import new
from pip._internal.self_outdated_check import _get_statefile_name

from matplotlib import animation

mp_drawing = mp.solutions.drawing_utils
mp_selfie_segmentation = mp.solutions.selfie_segmentation
selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=0) 

import PIL
from PIL import Image,ImageTk
from tkinter import *
import os 
# 
#4:3
camera_w = 640
camera_h = 480

window_width =  int(camera_w  * 0.3)
window_height = int(camera_h  * 0.3)
play_mode = "Trans"

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
#用來記錄隱藏式窗前的位置，用於恢復位置
last_geo_x = window_x
last_geo_y = window_y
#用來記錄隱藏視窗前的位置
vanish_x = 0 
vanish_y = 0
#geo_str = str(window_width) + "x" + str(window_height) + "+"+ str(screen_width-window_width-30) +"+" + str(screen_height - window_height -60)
print (geo_str)
root.geometry(geo_str)
lmain = Label(root,background='white',borderwidth = 0, highlightthickness = 0)
lmain.pack()

#user hot key
user_hotkey_file = "selfie_config.txt"
hotkey_dict = {}
def get_user_hotkey(user_hotkey_file) :
    global hotkey_dict
    if not os.path.exists(user_hotkey_file) :
        print ("user hot_key file not found")
        return None  
    with open(user_hotkey_file,"r",encoding="utf-8") as f:
        hotkeys = [l.replace("\n","") for l in f.readlines()]
        for hotkey in hotkeys :
            h = hotkey.split(",")
            hotkey_dict[h[0]] = h[1:]

get_user_hotkey(user_hotkey_file)

#cap = None
def move_tk_window(x, y, animation = False):
    global last_geo_x, last_geo_y
    if animation :
        #Animation
        step = 8 #移動次數
        x_step = int((x-last_geo_x)/(step-1)) 
        y_step = int((y-last_geo_y)/(step-1))
        for i in range(0,step) :
            geo_str = str(window_width) + "x" + str(window_height) + "+"+ str(last_geo_x + x_step) +"+" + str(last_geo_y + y_step) 
            root.geometry(geo_str)
            last_geo_x = last_geo_x + x_step 
            last_geo_y = last_geo_y + y_step
        #
    geo_str = str(window_width) + "x" + str(window_height) + "+"+ str(x) +"+" + str(y) 
    root.geometry(geo_str)
    root.geometry(geo_str)
    last_geo_x = x 
    last_geo_y = y

def show_default_video_window():  
    window_x = screen_w-window_width-30
    window_y = screen_h- window_height -60
    move_tk_window(window_x,window_y) 
def hide_video_window():
    global screen_w, screen_h, window_name,window_x, window_y
    global geo_str, last_geo_str
    global vanish_x, vanish_y
    #cv2.moveWindow(window_name, int( (screen_w - window_w) * 0.97),-500) # Move it to invisible area
    #window_x = int( (screen_w - window_width) * 0.97)
    #window_y = -600
    #隱藏時，不更新 windows 的x,y 位置
    vanish_x = last_geo_x 
    vanish_y = last_geo_y
    #print("vanish:({},{})".format(vanish_x,vanish_y))
    x = int( (screen_w - window_width) * 0.97)
    y = screen_w+1600
    move_tk_window(x,y)

def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img
def image_transparent(image_rgba):
    newImage = []
    for item in image_rgba.getdata():
        if item[:3] == (255, 255, 255):
            newImage.append((255, 255, 255, 0))
        else:
            newImage.append(item)

    image_rgba.putdata(newImage)
    return image_rgba
    
def image_selfie_segmentation(image, stype="blur"):
    bg_image = None
    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = selfie_segmentation.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Draw selfie segmentation on the background image.
    # To improve segmentation around boundaries, consider applying a joint
    # bilateral filter to "results.segmentation_mask" with "image".
    condition = np.stack(
      (results.segmentation_mask,) * 3, axis=-1) > 0.15
    # The background can be customized.
    #   a) Load an image (with the same width and height of the input image) to
    #      be the background, e.g., bg_image = cv2.imread('/path/to/image/file')
    #   b) Blur the input image by applying image filtering, e.g.,
    #      bg_image = cv2.GaussianBlur(image,(55,55),0)
    BG_COLOR = (255, 255, 255) # gray
    
    if stype == "blur" :
        bg_image = cv2.GaussianBlur(image,(23,23),0)
        bg_image = increase_brightness(bg_image, value=20)
        output_image = np.where(condition, image, bg_image)
        output_image = increase_brightness(output_image, value=45)
    if bg_image is None:
        bg_image = np.zeros(image.shape, dtype=np.uint8)
        bg_image[:] = BG_COLOR
        output_image = np.where(condition, image, bg_image)       
    return output_image

def show_frame():
    global play_mode
    if play_mode == "Trans" or play_mode == "Normal" or play_mode == "H" and cap != None :
        success, img = cap.read()
        if not success :
            print ("not success")
            return
        img = cv2.flip(img, 1)
        #處理 opencv img 邏輯
        if (play_mode != "H"):
            img = image_selfie_segmentation(img,stype="blur") 
            img = image_selfie_segmentation(img,stype="") 
        #output_image = cv2.resize(output_image, (window_width, window_height)) 
        #
        #處理 tkinter GUI 邏輯
        cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)    
        img = PIL.Image.fromarray(cv2image)
        # 直接透過tk 設定背景色，略過轉換透明色
        #img = image_transparent(img)
        img = img.resize((window_width, window_height))
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
    lmain.after(1, show_frame)
        #move_window()
    
def keyboard_process(k):
    global window_width, window_height, screen_w, screen_h, window_name,window_x, window_y,play_mode
    global cap
    global last_geo_x, last_geo_y, vanish_x, vanish_y
    scale = 20
    move_x = int(screen_w / scale)
    move_y = int(screen_h / scale)
    if (k.event_type == "down") : 
        if k.name == "w" or k.name == "i" :
            y = last_geo_y - move_y
            move_tk_window(last_geo_x, y)
        if k.name == "s" or k.name == "k":
            y = last_geo_y + move_y
            move_tk_window(last_geo_x, y)
        if k.name == "d" or k.name == "l"  :
            x = last_geo_x + move_x
            move_tk_window(x, last_geo_y)
        if k.name == "a" or k.name == "j":
            x = last_geo_x - move_x  
            move_tk_window(x, last_geo_y)
    if (k.event_type == "up") :         
        if k.name == "h" :    
            if play_mode != "H" :      
                play_mode = "H"
                hide_video_window()  
                root.wm_attributes('-transparentcolor',"")
                root.overrideredirect(False)  
                 
                #不關閉Camera 因為啟動太慢
                #cap.release()
                #cap = None
                #記憶隱藏前的位置
                print ("change mode:{}".format(play_mode))
        if k.name == "t" :
            root.overrideredirect(True)    
            root.wm_attributes('-transparentcolor','white')  
            if play_mode == "H" :
                print("vanish:({},{})".format(vanish_x,vanish_y))
                move_tk_window(vanish_x, vanish_y)
            play_mode = "Trans"  
            print ("change mode:{}".format(play_mode))
        if k.name == "n" :
            root.overrideredirect(False)  
            root.wm_attributes('-transparentcolor','white') 
            if play_mode == "H" :
                print("vanish:({},{})".format(vanish_x,vanish_y))
                move_tk_window(vanish_x, vanish_y)
            play_mode = "Normal"
            print ("change mode:{}".format(play_mode))
        if k.name =="esc": 
            root.destroy()
        if k.name in hotkey_dict :
            loc = hotkey_dict[k.name]
            move_tk_window(int(loc[0]), int(loc[1]),animation=True)
def keyboard_monitor(type):
    keyboard.hook(keyboard_process)      
if __name__ == "__main__" :    
    
    #width, height = 800, 600
    play_mode = "Trans"
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1); 
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    #設定透明色
    root.wm_attributes('-transparentcolor','white')
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    show_frame()
    #監聽鍵盤
    keyboard_thread = Thread(target=keyboard_monitor,args=(0,))
    keyboard_thread.start()
    root.mainloop() 
    # For webcam input:
   
    cap.release()