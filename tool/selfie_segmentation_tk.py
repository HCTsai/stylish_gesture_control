'''
Created on 2021年7月14日

@author: Hsiao-Chien Tsai(蔡効謙)
'''
import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_selfie_segmentation = mp.solutions.selfie_segmentation
selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1) 

import PIL
from PIL import Image,ImageTk
from tkinter import *

window_width = 640
widow_height = 480
play_mode = "N"

root = Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.bind('<Escape>', lambda e: root.quit())
appHeight = 140
padding = 8
left_padding = 300
geo_str = str(window_width) + "x" + str(widow_height) + "+"+ str(screen_width-window_width-30) +"+" + str(screen_height - widow_height -60)
print (geo_str)
root.geometry(geo_str)
lmain = Label(root,background='white',borderwidth = 0, highlightthickness = 0)
lmain.pack()

count = 0

def move_window():
    global count
    geo_str = str(window_width) + "x" + str(widow_height) + "+"+ str(count%screen_width) +"+" + str(screen_height - widow_height -30)
    print (geo_str)
    root.geometry(geo_str)
    count +=20
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
    
def image_selfie_segmentation(image):
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
    #bg_image = cv2.GaussianBlur(image,(23,23),0)
    #bg_image = increase_brightness(bg_image, value=10)
    if bg_image is None:
        bg_image = np.zeros(image.shape, dtype=np.uint8)
        bg_image[:] = BG_COLOR
    output_image = np.where(condition, image, bg_image)
    output_image = increase_brightness(output_image, value=35)
    return output_image

def show_frame():
    
    if play_mode == "N" :
        success, img = cap.read()
        if not success :
            return
        img = cv2.flip(img, 1)
        #處理 opencv img 邏輯
        output_image = image_selfie_segmentation(img) 
        #output_image = cv2.resize(output_image, (window_width, widow_height)) 
        #
        #處理 tkinter GUI 邏輯
        cv2image = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGBA)    
        img = PIL.Image.fromarray(cv2image)
        # 直接透過tk 設定背景色
        #img = image_transparent(img)
        img = img.resize((window_width, widow_height))
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        lmain.after(1, show_frame)
        #move_window()
    
    
if __name__ == "__main__" :    
    
    #width, height = 800, 600
    play_mode = "N"
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1); 
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    show_frame()
    root.wm_attributes('-transparentcolor','white')
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    
    root.mainloop() 
    # For webcam input:
   
    cap.release()