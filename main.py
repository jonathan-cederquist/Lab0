import keyboard
import time
from solar_panel import SolarPanelSystem

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


## Create Solar Panel Object
myPanel = SolarPanelSystem("/dev/ttyS0", 128, 5.75)

# Create generators for FSM
myFoldGen = myPanel.foldFSM()
myTiltGen = myPanel.tiltFSM()

print("Welcome to the solar panel system demonstration.")
print("Press e to extend, r to retract, and number keys (2 digits) to tilt.")
print("Press x to exit the demonstration.")

key_pressed = None

key_Nums = []

## Turn on callback for particular keys only
keyboard.on_release_key('e', callback=onKeyPress)
keyboard.on_release_key('r', callback=onKeyPress)
keyboard.on_release_key('x', callback=onKeyPress)
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

period = 50000000 #Set period to 50 ms (in ns)
lastTime = time.perf_counter_ns()
nextTime = lastTime + period

while True:
    
    try:
        
        if time.perf_counter_ns() > nextTime:
            
            lastTime = time.perf_counter_ns()
            nextTime = lastTime + period
            
            #Run sunny folding state machine
            next(myFoldGen)
            
            #Run sunny tilting state machine
            next(myTiltGen)
            
            if key_pressed== 'e':
                myPanel.unfold()
                print("You have extended the rack")
                key_pressed=None
                
            elif key_pressed=='r':
                myPanel.fold()
                print("You have retracted the rack")
                key_pressed=None
                
            elif len(key_Nums) > 1:
                num = int(str(key_Nums.pop(0)) + str(key_Nums.pop(0)))
                
                # Set tilt angle to num
                myPanel.set_tilt_angle(num)
                print("You have tilted the rack ", num, " degrees")
                key_pressed=None
                
            elif key_pressed=='x':
                print("Goodbye!")
                break
                    
            
    except KeyboardInterrupt:
        break
    
keyboard.unhook_all()
