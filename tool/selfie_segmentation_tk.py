'''
Created on 2021年7月14日

@author: Hsiao-Chien Tsai(蔡効謙)
'''
import cv2
import mediapipe as mp
import numpy as np
import keyboard
from threading import Thread

mp_drawing = mp.solutions.drawing_utils
mp_selfie_segmentation = mp.solutions.selfie_segmentation
selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=0) 

import PIL
from PIL import Image,ImageTk
from tkinter import *

window_width = 640
widow_height = 480
play_mode = "N"

root = Tk()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
root.bind('<Escape>', lambda e: root.quit())
root.title("AI CAM")
appHeight = 140
padding = 8
left_padding = 300

window_x = screen_w-window_width-30
window_y = screen_h- widow_height -60
geo_str = str(window_width) + "x" + str(widow_height) + "+"+ str(window_x) +"+" + str(window_y)
#geo_str = str(window_width) + "x" + str(widow_height) + "+"+ str(screen_width-window_width-30) +"+" + str(screen_height - widow_height -60)
print (geo_str)
root.geometry(geo_str)
lmain = Label(root,background='white',borderwidth = 0, highlightthickness = 0)
lmain.pack()

#
#cap = None
def move_tk_window(x,y):
    geo_str = str(window_width) + "x" + str(widow_height) + "+"+ str(x) +"+" + str(y)    
    root.geometry(geo_str)
def show_video_window():   
    
    global screen_w, screen_h, window_name,window_x, window_y
    #cv2.moveWindow(window_name, int( (screen_w - window_w) * 0.97),-40)  # Move it to (40,30)  
    #window_x = int((screen_w - window_width) * 0.97)
    #window_y = 20t
    window_x = screen_w-window_width-30
    window_y = screen_h- widow_height -60
    move_tk_window(window_x,window_y) 
def hide_video_window():
    global screen_w, screen_h, window_name,window_x, window_y
    #cv2.moveWindow(window_name, int( (screen_w - window_w) * 0.97),-500) # Move it to invisible area
    window_x = int( (screen_w - window_width) * 0.97)
    window_y = -600
    move_tk_window(window_x,window_y)

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
    if play_mode == "N" or play_mode == "T" or play_mode == "H" and cap != None :
        success, img = cap.read()
        if not success :
            print ("not success")
            return
        img = cv2.flip(img, 1)
        #處理 opencv img 邏輯
        if (play_mode != "H"):
            img = image_selfie_segmentation(img,stype="blur") 
            img = image_selfie_segmentation(img,stype="") 
        #output_image = cv2.resize(output_image, (window_width, widow_height)) 
        #
        #處理 tkinter GUI 邏輯
        cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)    
        img = PIL.Image.fromarray(cv2image)
        # 直接透過tk 設定背景色，略過轉換透明色
        #img = image_transparent(img)
        img = img.resize((window_width, widow_height))
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
    lmain.after(1, show_frame)
        #move_window()
    
def keyboard_process(k):
    global window_width, window_height, screen_w, screen_h, window_name,window_x, window_y,play_mode
    global cap
    scale = 20
    move_x = int(screen_w / scale)
    move_y = int(screen_h / scale)
    if (k.event_type == "down") :
        if k.name == "w" or k.name == "i" :
            window_y -= move_y
        if k.name == "s" or k.name == "k":
            window_y += move_y
        if k.name == "d" or k.name == "l"  :
            window_x += move_x
        if k.name == "a" or k.name == "j":
            window_x -= move_x  
        move_tk_window(window_x, window_y)
        if k.name == "h" :            
            play_mode = "H"
            root.overrideredirect(False)
            hide_video_window()
            root.wm_attributes('-transparentcolorh',"")            
            #不關閉Camera 因為啟動太慢
            #cap.release()
            #cap = None
            print ("change mode:{}".format(play_mode))
        if k.name == "n" :
            
            play_mode = "N"
            root.overrideredirect(True)    
            root.wm_attributes('-transparentcolor','white')        
            show_video_window()
            #if cap == None:
            #    cap = cv2.VideoCapture(0)
            print ("change mode:{}".format(play_mode))
        if k.name == "t" :
            play_mode = "T"
            root.overrideredirect(False)  
            root.wm_attributes('-transparentcolor','white')   
            #show_frame()          
            show_video_window()    
            
            print ("change mode:{}".format(play_mode))
def keyboard_monitor(type):
    keyboard.hook(keyboard_process)      
if __name__ == "__main__" :    
    
    #width, height = 800, 600
    play_mode = "N"
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1); 
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    
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