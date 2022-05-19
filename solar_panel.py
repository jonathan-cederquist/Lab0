import time
from math import pi as PI
from roboclaw_3 import Roboclaw

class SolarPanelSystem:
    
    S0_RETRACTED = 0
    S1_UNFOLDING = 1
    S2_EXTENDED  = 2
    S3_FOLDING   = 3
    S0_FLAT      = 0
    S1_TILTING   = 1
    S2_TILTED    = 2
    
    pinionPitchDia = 0.875   #[in]
    slideGearRatio = 21/36   #[Npinion/Nmotor]
    tiltGearRatio  = 24      #[TurnsWorm/TurnsGear]
    PPR            = 2774.64 #[Encoder pulses/rev]
    
    def __init__(self, rpiSerialPort, roboclawAddress, extendDist, currentPos=0, tiltAngle=0, unfoldFlag=False, dbg=False):
        '''!
        @brief Creates SolarPanelSystem object to control unfolding and tilting of solar panels
        @details Creates a roboclaw associated with the two motors used for controlling the
                 motion of unfolding and tilting.
        
        @param rpiSerialPort The location of the serial port connection on the raspberry pi
        @param roboclawAddress The address of the desired roboclaw
        @param extendDist The distance the rack extends for a full unfolding [in]
        @param currentPos The current extension position of the rack [in]
        @param tiltAngle The current angle the array is tilted at
        @param unfoldFlag A boolean flag used to tell the array when to unfold
        '''
        
        #Define Roboclaw serial com port, baudrate 38400
        self.rc = Roboclaw(rpiSerialPort,38400)
        self.no_error = self.rc.Open()
        
        #Debug flag
        self.dbgFlag = dbg
        
        #Define Roboclaw address
        self.address = roboclawAddress
        
        #Save extension distance
        self.extDistPulses = int((extendDist/(self.pinionPitchDia/2))*self.slideGearRatio*(self.PPR/(2*PI)))
        
        #Set current position of extension motor
        if self.no_error:
            self.rc.SetEncM1(self.address, int((currentPos/(self.pinionPitchDia/2))*self.slideGearRatio*(self.PPR/(2*PI))))
            
            if self.dbgFlag:
                print("M1 Enc:", self.rc.ReadEncM1(self.address)[1])
        
        #Save tilt angle
        self.tiltAngPulses = round(tiltAngle*self.tiltGearRatio*(self.PPR/360))
        
        #Set current position of tilt motor
        if self.no_error:
            self.rc.SetEncM2(self.address, self.tiltAngPulses)
            
            if self.dbgFlag:
                print("M2 Enc:", self.rc.ReadEncM2(self.address)[1])
            
        #Save unfold flag
        self.unfoldFlag = unfoldFlag
        
        #Set initial states to S0
        self.foldState = self.S0_RETRACTED
        self.tiltState = self.S0_FLAT
        
    def ready(self):
        '''!
        @brief Returns true if the serial port to the roboclaw opened correctly
        '''
        
        return not(self.no_error)
    
    def unfold(self):
        '''!
        @brief Changes unfoldFlag to tell panels to unfold
        '''
        
        self.unfoldFlag = True
        
    def fold(self):
        '''!
        @brief Changes unfoldFlag to tell panels to fold
        '''
        
        self.unfoldFlag = False
        
    def set_tilt_angle(self, newTiltAngle):
        '''!
        @brief Changes the desired tilt angle for the solar array
        @param newTiltAngle The new angle of tilt desired for the solar panels [deg]
        '''
        
        self.tiltAngPulses = round(newTiltAngle*self.tiltGearRatio*(self.PPR/360))
    
    def extend(self):
        '''!
        @brief Used to manually extend the solar array
        '''
        
        self.rc.SpeedAccelDeccelPositionM1(self.address, 2000, 300, 2000, self.extDistPulses, 1)
    
    def retract(self):
        '''!
        @brief Used to manually retract the solar array
        '''
        
        self.rc.SpeedAccelDeccelPositionM1(self.address, 2000, 300, 2000, 0, 1)
        
    def tilt(self, newTiltAng):
        '''!
        @brief Used to manually tilt the solar array to a desired angle
        @param newTiltAng The desired angle in degrees to tilt the solar array to
        '''
        
        self.tiltAngPulses = round(newTiltAng*self.tiltGearRatio*(self.PPR/360))
        self.rc.SpeedAccelDeccelPositionM2(self.address, 2000, 300, 2000, self.tiltAngPulses, 1)
        
    def foldFSM(self):
        '''!
        @brief Generator used to control the folding and unfolding of the solar array
        '''
        while True:
            
            if self.foldState==self.S0_RETRACTED:
                
                if self.unfoldFlag:
                    self.foldState = self.S1_UNFOLDING
                    self.rc.SpeedAccelDeccelPositionM1(self.address, 2000, 300, 2000, self.extDistPulses, 1)
                    
            elif self.foldState==self.S1_UNFOLDING:
                
                if self.rc.ReadCurrents(self.address)[1] > 200 or abs(self.rc.ReadEncM1(self.address)[1] - self.extDistPulses) < 7:
                    self.rc.ForwardM1(self.address, 0)
                    self.foldState = self.S2_EXTENDED
            
            elif self.foldState==self.S2_EXTENDED:
                
                if not(self.unfoldFlag):
                    self.foldState = self.S3_FOLDING
                    self.rc.SpeedAccelDeccelPositionM1(self.address, 2000, 300, 2000, 0, 1)
            
            elif self.foldState==self.S3_FOLDING:
                
                if self.rc.ReadCurrents(self.address)[1] > 200 or abs(self.rc.ReadEncM1(self.address)[1]) < 7:
                    self.rc.ForwardM1(self.address, 0)
                    self.foldState = self.S0_RETRACTED
            
            yield(self.foldState)
    
    def tiltFSM(self):
        '''!
        @brief Generator used to control the tilting of the solar array
        '''
        while True:
            
            if self.tiltState==self.S0_FLAT:
                
                if self.tiltAngPulses > 0:
                    self.tiltState = self.S1_TILTING
                    self.rc.SpeedAccelDeccelPositionM2(self.address, 2000, 300, 2000, self.tiltAngPulses, 1)
                    
            elif self.tiltState==self.S1_TILTING:
#                 
#                 if self.rc.ReadEncM2(self.address)[1] < 7:
#                     self.rc.ForwardM2(self.address, 0)
#                     self.tiltState = self.S0_FLAT
                    
                if self.rc.ReadCurrents(self.address)[2] > 200 or abs(self.rc.ReadEncM2(self.address)[1] - self.tiltAngPulses) < 7:
                    self.rc.ForwardM2(self.address, 0)
                    self.tiltState = self.S2_TILTED
            
            elif self.tiltState==self.S2_TILTED:
                
                if abs(self.rc.ReadEncM2(self.address)[1] - self.tiltAngPulses) > 7:
                    self.tiltState = self.S1_TILTING
                    self.rc.SpeedAccelDeccelPositionM2(self.address, 2000, 300, 2000, self.tiltAngPulses, 1)
            
            yield(self.tiltState)
            
if __name__=="__main__":
    
    Sunny = SolarPanelSystem("/dev/ttyS0", 128, 9.966, dbg=True)
    
    #Use keyboard module to control tilting/extension input?
    
    input("Press enter to extend the array:")
    
    Sunny.extend()
    
    time.sleep(20)
    
    Sunny.retract()
    
    Sunny.tilt(20)
    
    
    
    
        
        
