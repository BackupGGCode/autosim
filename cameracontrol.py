from direct.showbase.DirectObject import DirectObject

from panda3d.core import *

key_map = (('1',['1',1]),('1-up',['1',0]),
           ('2',['2',1]),('2-up',['2',0]),
           ('3',['3',1]),('3-up',['3',0]))

class CameraControl(DirectObject):
    """ Controls the camera / view angle of the audiosim """
    
    def __init__(self, car):
        """ """
        self.accept( '1', self.enableTowerCamera )
        self.accept( '2', self.enableInsideCamera )
        self.accept( '3', self.enableBehindCamera )
        self.trackCar = False
        self.car = car

    def enableTowerCamera(self ):
        """ """
        base.cam.reparentTo( render )
        base.cam.setPos(10, -25, 5)
        self.trackCar = True
        base.cam.lookAt( self.car.chassis.getGlobalPos() )
        self.car.setCurrentAudioProfile( 'outside' )
        
    def enableInsideCamera(self ):
        """ """
        np = self.car.chassisModel.find( "**/camera-inside" )
        self.trackCar = False
        if np is not None:
            base.cam.setPos( Point3( 0,0,0 ))
            base.cam.setHpr( Vec3( 0,0,0 ))
            base.cam.reparentTo( np )
            self.car.setCurrentAudioProfile( 'inside' )
        
    def enableBehindCamera(self ):
        """ """
        np = self.car.chassisModel.find( "**/camera-behind" )
        self.trackCar = False
        if np is not None:
            base.cam.setPos( Point3( 0,0,0 ))
            base.cam.setHpr( Vec3( 0,0,0 ))
            base.cam.reparentTo( np )
            self.car.setCurrentAudioProfile( 'outside' )
        
    def simulate(self, dt):
        """ """
        if self.trackCar:
            base.cam.lookAt( self.car.chassis.getGlobalPos() )
        
    #def set_keystate(self, key, state):
        #self.keystate[key] = state