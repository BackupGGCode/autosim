from direct.showbase.DirectObject import DirectObject
from math import fabs

key_map = (('arrow_left',['left',1]),('arrow_left-up',['left',0]),
           ('arrow_right',['right',1]),('arrow_right-up',['right',0]),
           ('arrow_up',['up',1]),('arrow_up-up',['up',0]),
           ('arrow_down',['down',1]),('arrow_down-up',['down',0]),
           ('r',['r',1]),('r-up',['r',0]))
           
class KeyControl( DirectObject ):
    """ A class for controlling a vehicle with the arrow keys.  To be replaced with a more
    sophisticated Steering Wheel control object. """
    
    def __init__(self, car):
        self.keystate = {'down':0, 'up':0, 'left':0, 'right':0, 'r':0 }
        self.car = car
        for key in key_map:
            self.accept( key[0], self.set_keystate, key[1] )
            
    def set_keystate(self, key, state):
        self.keystate[key] = state
        
    def simulate(self, dt):
        if self.keystate['down'] is 1:
            self.car.setBrake( 1.0 )
        else:
            self.car.setBrake( 0.0 )
            
        if self.keystate['up'] is 1:
            self.car.setMotorTorque( 1.0 )
        else:
            self.car.setMotorTorque( 0.0 )
            
        if self.keystate['r'] is 1:
            self.keystate['r'] = 0  # toggle immediately
            self.car.setReverse( not car.reverse )
            
        steerFactor = 0.05;    
        steerTarget = 0;
        if self.keystate['left'] is 1:
            steerTarget -= 1
        elif self.keystate['right'] is 1:
            steerTarget += 1
        else:
            steerTarget = 0
        dir = steerTarget - self.car.steer
        if dir != 0:
            dir = fabs( dir ) / dir
        self.car.setSteer( self.car.steer + ( steerFactor * dir ) )
        
#    def controlCar(self, car):
#       if self.keystate['down'] is 1:
#            car.setBrake( 1.0 )
#        else:
#            car.setBrake( 0.0 )
#            
#        if self.keystate['up'] is 1:
#            car.setMotorTorque( 1.0 )
#        else:
#            car.setMotorTorque( 0.0 )
#            
#        if self.keystate['r'] is 1:
#            self.keystate['r'] = 0  # toggle immediately
#            car.setReverse( not car.reverse )
#        
#        steerFactor = 0.05;    
#        steerTarget = 0;
#       if self.keystate['left'] is 1:
#            steerTarget -= 1
#        elif self.keystate['right'] is 1:
#
#            steerTarget += 1
#        else:
#            steerTarget = 0
#        dir = steerTarget - car.steer
#        if dir != 0:
#            dir = fabs( dir ) / dir
#        car.setSteer( car.steer + ( steerFactor * dir ) )
#        