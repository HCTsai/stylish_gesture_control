'''
Created on 2022年5月10日

@author: Hsiao-Chien Tsai(蔡効謙)
'''

import os
import numpy as np
def get_user_hotkey(user_hotkey_file) :
    hotkey_dict = {}
    if not os.path.exists(user_hotkey_file) :
        print ("user hot_key file not found")
        return hotkey_dict  
    with open(user_hotkey_file,"r",encoding="utf-8") as f:
        hotkeys = [l.replace("\n","") for l in f.readlines() if not l.startswith("#")]
        for hotkey in hotkeys :
            h = hotkey.split(",")
            hotkey_dict[h[0]] = h[1:]
    return hotkey_dict

def list_to_file(list_name,file_name):
    with open(file_name,"w",encoding="utf-8") as of:
        for r in list_name :
            of.write(str(r) + "\n")
            
    with open ("hist.txt","w",encoding="utf-8") as of :
        hist, bins=np.histogram(np.array(list_name),bins=np.linspace(0,1280,128))
        for i, h in enumerate(hist) : 
            of.write(str(h) +"\t" + str(bins[i])  + "\n")