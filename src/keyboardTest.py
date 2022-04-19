# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 21:48:14 2022

@author: Cederq
"""
import keyboard
import time

# Keyboard test module
def onKeyPress(key):
        ''' @brief Callback function to run when key is pressed.
            @param key The key that is pressed
        '''
        global key_pressed 
        key_pressed = key.name
        
        if key_pressed.isdecimal():
            global key_Nums
            key_Nums.append(int(key_pressed))

if __name__=="__main__":
    
    print("Welcome to the keyboard test. Only keys e, r, and number keys are available.")
    
    key_pressed = None
    
    key_Nums = []
    
    ## Turn on callback for particular keys only
    keyboard.on_release_key('e', callback=onKeyPress)
    keyboard.on_release_key('r', callback=onKeyPress)
    keyboard.on_release_key('t', callback=onKeyPress)
    keyboard.on_release_key('0', callback=onKeyPress)
    keyboard.on_release_key('1', callback=onKeyPress)
    keyboard.on_release_key('2', callback=onKeyPress)
    keyboard.on_release_key('3', callback=onKeyPress)
    keyboard.on_release_key('4', callback=onKeyPress)
    keyboard.on_release_key('5', callback=onKeyPress)
    keyboard.on_release_key('6', callback=onKeyPress)
    keyboard.on_release_key('7', callback=onKeyPress)
    keyboard.on_release_key('8', callback=onKeyPress)
    keyboard.on_release_key('9', callback=onKeyPress)
    
    while True:
        # period of 'state machine'
        time.sleep(0.05)
        
        
        #Run sunny folding state machine
        #Run sunny tilting state machine
        
        try:
            
            if key_pressed== 'e':
                #Issue command to extend rack (flip flag)
                print("You have extended the rack")
                key_pressed=None
                
            elif key_pressed=='r':
                #Issue command to retract the rack (flip flag)
                print("You have retracted the rack")
                key_pressed=None
                
            elif len(key_Nums) > 1:
                num = int(str(key_Nums.pop(0)) + str(key_Nums.pop(0)))
                
                # Set tilt angle to num
                print("You have tilted the rack ", num, " degrees")
                key_pressed=None
                
        
        except KeyboardInterrupt:
            break
        
    keyboard.unhook_all()