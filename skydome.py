from pandac.PandaModules import * 
from direct.task import Task # To use Tasks

class SkyDome:
    """ 
    A very simple skydome object.  
    Sets up a skydome that attaches itself as a direct child of the camera.  Requests to be drawn
    first (by requesting render bin 0) and disables all depth testing and sorting to have as little
    impact as possible on the rendering """ 
    
    def __init__( self, filePath ):
        """ Initializes the object.  
        The filePath argument represents the model to load for the sky geometry. """
        self.sky = loader.loadModel( filePath )
        self.sky.setDepthWrite( False )
        self.sky.setDepthTest( False )
        self.sky.setBin( 'background', 0 )
        self.sky.setEffect(CompassEffect.make(render))
        self.sky.setLightOff() 
        self.sky.reparentTo( base.camera )

