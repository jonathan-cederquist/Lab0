import time
from solar_panel import SolarPanelSystem

## Create Solar Panel Object
myPanel = SolarPanelSystem("/dev/ttyS0", 128, 5.75)

# Create generators for FSM
myFoldGen = myPanel.foldFSM()
#myTiltGen = myPanel.tiltFSM()

print("Welcome to the solar panel folding cycles test.")
print("This program starts a counter and continually unfolds and folds the solar array.")
print("Press Ctrl-C to exit the test at any time.")

period = 50000000 #Set period to 50 ms (in ns)
lastTime = time.perf_counter_ns()
nextTime = lastTime + period
cycleCounter = 0
unfoldFlag = True
errorMsg = ''

while True:
    
    try:
        
        if time.perf_counter_ns() > nextTime:
            
            lastTime = time.perf_counter_ns()
            nextTime = lastTime + period
            
            #Run sunny folding state machine
            state = next(myFoldGen)
            
            #Run sunny tilting state machine
            #next(myTiltGen)
            
            #If panel should be unfolding, check unfolding states
            if unfoldFlag:
                
                #If retracted, issue command to unfold
                if state==0:
                    myPanel.unfold()
                
                #If already unfolding, let it chill
                elif state==1:
                    pass
                
                #If finished unfolding (extended), flip flag
                elif state==2:
                    unfoldFlag = False
            #If panel should be folding, check folding states
            else:
                
                #If extended, issue command to fold
                if state==2:
                    myPanel.fold()
                
                #If already folding, let it chill
                elif state==3:
                    pass
                
                #If finished folding (retracted), flip flag and increase counter
                elif state==0:
                    unfoldFlag = True
                    cycleCounter += 1
            
            if cycleCounter > 500:
                errorMsg = 'No error. 500 cycles completed.'
                break
            
    except KeyboardInterrupt:
        errorMsg = 'Keyboard interrupt'
        break
    
print('The test has stopped. The reason for stoppage was:')
print(errorMsg)
print(cycleCounter, 'cycles were completed.')

