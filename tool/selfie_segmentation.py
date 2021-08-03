'''
Created on 2021年7月14日

@author: Hsiao-Chien Tsai(蔡効謙)
'''
import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_selfie_segmentation = mp.solutions.selfie_segmentation

selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=0) 
def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img
BG_COLOR = (255, 255, 255) # gray
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
    if stype == "blur" :
        bg_image = cv2.GaussianBlur(image,(13,13),0)
        #bg_image = increase_brightness(bg_image, value=10)
        output_image = np.where(condition, image, bg_image)
        output_image = increase_brightness(output_image, value=20)
    if bg_image is None:
        bg_image = np.zeros(image.shape, dtype=np.uint8)
        bg_image[:] = BG_COLOR
        output_image = np.where(condition, image, bg_image)
        output_image = increase_brightness(output_image, value=20)       
    return output_image
if __name__ == "__main__" :     
    # For webcam input:
    BG_COLOR = (255, 255, 255) # gray
    cap = cv2.VideoCapture(0)
   
    bg_image = None
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue
        image = cv2.flip(image, 1)
        output_image = image_selfie_segmentation(image,stype="blur") 
        output_image = image_selfie_segmentation(output_image,stype="") 
        cv2.imshow('Selfie Segmentation', output_image)
        if cv2.waitKey(5) & 0xFF == 27:
            break
    cap.release()