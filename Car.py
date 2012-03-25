from pandac.PandaModules import * 
from direct.showbase import Audio3DManager

from panda3d.physx import PhysxActorDesc
from panda3d.physx import PhysxBodyDesc
from panda3d.physx import PhysxBoxShapeDesc
from panda3d.physx import PhysxD6JointDesc
from panda3d.physx import PhysxJointLimitSoftDesc
from panda3d.physx import PhysxJointDriveDesc
from panda3d.physx import PhysxMaterialDesc
from panda3d.physx import PhysxSpringDesc 
from panda3d.physx import PhysxWheelShapeDesc
from panda3d.physx import PhysxWheelContactData

from xml.dom import minidom

def readVec3( node ):
    """ An XML helper routine to parse a Vec3 from a node """
    return Vec3( float( node.getAttribute( 'x' ) ),
                 float( node.getAttribute( 'y' ) ),
                 float( node.getAttribute( 'z' ) ) )

def readPoint3( node ):
    """ An XML helper routine to parse a Point3 from a node """
    return Point3( float( node.getAttribute( 'x' ) ),
                   float( node.getAttribute( 'y' ) ),
                   float( node.getAttribute( 'z' ) ) )

def toBool( string ):
    """ An helper routine that returns True if the supplied string equals 'true', otherwise False """
    return string == 'true'

class Tire:
    """ Represents a tire on a car, and the suspension """
    
    def __init__( self, physxScene, name, pos, carActor, hdg, material, radius, spring, damper, targetValue ):
        self.model = render.attachNewNode( name + "nodeBase" )
        self.tiremodel = loader.loadModel( "Resources/Models/Tire" )
        self.tiremodel.setR( hdg )
        self.initialH = hdg
        self.tiremodel.reparentTo( self.model )
        self.model.reparentTo( render )
        self.createWheelShapeTire( physxScene, name, pos, carActor, material, radius, spring, damper, targetValue )
        self.steerable = True
        self.torque = True
        self.brake = True

        
    def createWheelShapeTire( self, physxScene, name, pos, carActor, material, radius, spring, damper, targetValue ):
        """ Creates a raycast tire using Wheel Shapes which are a simple way of creating physx tires. """
        wheelDesc = PhysxWheelShapeDesc()
        wheelDesc.setRadius( radius )
        wheelDesc.setLocalPos( pos )
        wheelDesc.setMaterial( material )
        springDesc = PhysxSpringDesc()
        springDesc.setSpring( spring )
        springDesc.setDamper( damper )
        springDesc.setTargetValue( targetValue )
        wheelDesc.setSuspensionTravel( 0.1 )
        wheelDesc.setSuspension( springDesc )
        self.shape = carActor.createShape( wheelDesc )


    def simulate(self, dt ):
        """ Simulates the tire, places the visual model according to the physical model """
        self.model.setPosQuat( self.shape.getGlobalPos(), self.shape.getGlobalQuat() )    # Inherit position from the WheelShape
        contact = PhysxWheelContactData()
        self.shape.getContact( contact )
        if contact.isValid():
            self.model.setY( self.model, self.shape.getRadius() - contact.getContactPosition() )
        else:
            self.model.setY( self.model, -self.shape.getSuspensionTravel() )
        self.tiremodel.setP( self.tiremodel.getP() + ( dt*self.shape.getAxleSpeed()*57.3 ) )
        self.model.setR( self.model, -self.shape.getSteerAngle() )
    
        
class AudioProfile:
    """ An audio profile stores the audio files used by the Car for the current view point.
    The main reason for the audio profile is that the audio varies wether the user is inside
    the car or outside. """
    
    def __init__( self, profileNode, audio3d, car ):
        self.name = profileNode.getAttribute( 'name' )
        self.sounds = []
        self.active = False
        self.engineIdle = self.loadSoundNode( audio3d, car, profileNode, 'engine-idle' )
        self.engineStart = self.loadSoundNode( audio3d, car, profileNode, 'engine-start' )
        self.roadSound = self.loadSoundNode( audio3d, car, profileNode, 'road-sound' )
        self.car = car
    
    def loadSoundNode( self, audio3d, car, parentNode, nodeName ):
        soundNode = parentNode.getElementsByTagName( nodeName )[0]
        sound = audio3d.loadSfx( soundNode.getAttribute( 'file' ) )
        audio3d.attachSoundToObject( sound, car.chassisModel )
        audio3d.setSoundVelocityAuto( sound )
        sound.setLoop( toBool( soundNode.getAttribute( 'loop' ) ) )
        self.sounds.append( sound )
        return sound
    
    def setEngineRunning( self, running ):
        if running:
            self.engineIdle.play()
        else:
            self.engineIdle.stop()
    
    def setActive( self, active ):
        self.active = active
        if self.active == False:
            for sound in self.sounds:
                sound.stop()
        else:
            for sound in self.sounds:
                if sound.getLoop():
                    sound.play()
                
    def simulate( self, dt ):
        self.roadSound.setVolume( min( self.car.speed / 15, 3.0 ) )
        self.engineIdle.setPlayRate( max( 1.0, self.car.torque / 75 ))
    
    #def simulate(self, dt ):

class Car:
    """ """
    
    def __init__( self, physxScene, audio3d, xmlfile ):
        """ """
        self.tires = []         # Holds the Car's tires
        self.audioProfiles = [] # Holds the Car's audio profiles
        self.steer = 0.0        # Represents current steering value
        self.engineTorque = 0.0 # Represents the engine torque
        self.initByXml( physxScene, audio3d, xmlfile )
        self.speed = 0.0        # The car's speed.
        self.torque = 0.0
        self.brake = 0.0
        self.currentAudioProfile = None
        
    def setCurrentAudioProfile(self, name ):
        newActive = None
        if self.currentAudioProfile is not None:
            self.currentAudioProfile.setActive( False )
            
        for profile in self.audioProfiles:
            if profile.name == name:
                newActive = profile
        if newActive is not None:
            newActive.setActive( True )
            self.currentAudioProfile = newActive
        
    def initByXml(self, physxScene, audio3d, xmlfile):
        """ Initializes the Car from an XML file """
        xmldoc = minidom.parse( xmlfile )
        carNode = xmldoc.getElementsByTagName( 'car' )[0]
        
        # Setup some global attributes for the car.
        self.type = carNode.getAttribute( 'type' )
        self.innerSteer = float( carNode.getAttribute( 'turn-angle-inside' ) )
        self.outerSteer = float( carNode.getAttribute( 'turn-angle-outside' ) )
        self.initChassisByXml( physxScene, carNode )
        self.initTyresByXml( physxScene, carNode )
        self.initAudioByXml( audio3d, carNode )
        self.initCameraByXml( carNode )
        
    def initChassisByXml(self, physxScene, carNode):
        """ Loads chassis configuraiton from an xml file and applies to the car """
        # Start initializing the chassis ...
        chassisNode = carNode.getElementsByTagName( 'chassis' )[0]
        bodyNode = chassisNode.getElementsByTagName( 'body' )[0]
        
        bodyDesc = PhysxBodyDesc()
        bodyDesc.setMass( float( bodyNode.getAttribute( 'mass' ) ) )
        
        actorDesc = PhysxActorDesc()
        actorDesc.setName( 'Chassis' )
        actorDesc.setBody( bodyDesc )
        actorDesc.setGlobalPos( readPoint3( chassisNode.getElementsByTagName( 'global-pos' )[0] ) )
        
        boxShapeNodes = bodyNode.getElementsByTagName( 'boxshape' )
        for boxNode in boxShapeNodes:
            shapeDesc = PhysxBoxShapeDesc()
            shapeDesc.setDimensions( readVec3( boxNode.getElementsByTagName('dimensions')[0] ) )
            shapeDesc.setLocalPos( readPoint3( boxNode.getElementsByTagName('local-pos')[0] ) )
            actorDesc.addShape( shapeDesc )
            
        self.chassis = physxScene.createActor( actorDesc )
        self.chassis.setCMassOffsetLocalPos( readPoint3( chassisNode.getElementsByTagName( 'center-of-mass' )[0] ) )
        self.chassisModel = loader.loadModel( chassisNode.getAttribute( 'model' ))
        self.chassisModel.reparentTo( render )
    
    def initTyresByXml( self, physxScene, carNode ):
        """ Loads tire configuraiton from an xml file and applies to the car """
        rubberDesc = PhysxMaterialDesc()
        rubberDesc.setRestitution(0.1)
        rubberDesc.setStaticFriction(1.2)
        rubberDesc.setDynamicFriction(0.1)
        mRubber = physxScene.createMaterial( rubberDesc )
        # Start loading the tires ...
        tireNodes = carNode.getElementsByTagName( 'tire' )
        for tireNode in tireNodes:
            springNode = tireNode.getElementsByTagName( 'spring' )[0]
            pos = readPoint3( tireNode.getElementsByTagName( 'local-pos' )[0] )
            tire = Tire( physxScene, tireNode.getAttribute( 'name' ), pos, self.chassis, 
                         int( tireNode.getAttribute( 'rotation' ) ),  mRubber, 
                         float( tireNode.getAttribute( 'radius' ) ), 
                         float( springNode.getAttribute( 'spring' ) ),
                         float( springNode.getAttribute( 'damper' ) ),
                         float( springNode.getAttribute( 'target-value' ) ) )
            self.tires.append( tire )
            tire.steerable = toBool( tireNode.getAttribute( 'steerable' ))


    def initAudioByXml( self, audio3d, carNode ):
        """ Loads audio information from an xml file and applies it to the car """
        audioNode = carNode.getElementsByTagName( 'audio' )[0]
        profileNodes = audioNode.getElementsByTagName( 'profile' )
        for profileNode in profileNodes:
            profile = AudioProfile( profileNode, audio3d, self )
            self.audioProfiles.append( profile )
            
    def initCameraByXml( self, carNode ):
        cameraNodes = carNode.getElementsByTagName('camera')
        for cameraNode in cameraNodes:
            np = self.chassisModel.attachNewNode( "camera-" + cameraNode.getAttribute( 'name' ) )
            np.setPos( readPoint3( cameraNode.getElementsByTagName('pos')[0] ) )
            np.setHpr( readVec3( cameraNode.getElementsByTagName( 'hpr' )[0]))
            
    def setActiveAudioProfile(self, name):
        for profile in self.audioProfiles:
            if profile.name == name:
                profile.setEngineRunning( True )
            else:
                profile.setEngineRunning( False )
        
    def setSteer(self, steer):
        """ Set the car's steering value. The value ranges from -1.0 - 1.0, 0.0 being a neutral position """
        if steer < -1.0:
            steer = -1.0
        elif steer > 1.0:
            steer = 1.0
        self.steer = steer
        for tire in self.tires:
            if tire.steerable:
                if ( steer < 0.0 and tire.model.getX() > 0.0 ) or ( steer > 0.0 and tire.model.getX() < 0.0 ):
                    tire.shape.setSteerAngle( self.innerSteer * steer )
                else:
                    tire.shape.setSteerAngle( self.outerSteer * steer )
        
    def setBrake(self, brake):
        """ Sets the brake force on the car.  The value ranges from 0.0 to 1.0, 1.0 being maximum brake applied """
        if brake < 0.0:
            brake = 0.0
        elif brake > 1.0:
            brake = 1.0
        brake *= 1000
        for tire in self.tires:
            if tire.brake:
                tire.shape.setBrakeTorque( brake )
        
    def setMotorTorque(self, torque):
        """ Sets the motor torque on the car.  The value ranges from 0.0 to 1.0, 1.0 being maximum torque"""
        if torque < 0.0:
            torque = 0.0
        elif torque > 1.0:
            torque = 1.0
        torque *= 100
        dTorque = 2
        if self.torque < torque:
            self.torque += dTorque
        elif self.torque > torque:
            self.torque -= dTorque
             
        for tire in self.tires:
            if tire.torque:
                tire.shape.setMotorTorque( self.torque )
        
        
    def simulate(self,dt):
        self.chassisModel.setPosQuat( self.chassis.getGlobalPos(), self.chassis.getGlobalQuat() )
        for tire in self.tires:
            tire.simulate(dt);
        self.speed = self.chassis.getLinearVelocity().length()
        if self.currentAudioProfile is not None:
            self.currentAudioProfile.simulate( dt )
        #print "speed=" + str( ( self.speed * 60.0 *60.0 ) / 1000.0 ) 
            
        
        