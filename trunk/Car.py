from pandac.PandaModules import * 

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
    return Vec3( float( node.getAttribute( 'x' ) ),
                 float( node.getAttribute( 'y' ) ),
                 float( node.getAttribute( 'z' ) ) )

def readPoint3( node ):
    return Point3( float( node.getAttribute( 'x' ) ),
                   float( node.getAttribute( 'y' ) ),
                   float( node.getAttribute( 'z' ) ) )

def toBool( string ):
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
        self.model.setPosQuat( self.shape.getGlobalPos(), self.shape.getGlobalQuat() )    # Inherit position from the WheelShape
        contact = PhysxWheelContactData()
        self.shape.getContact( contact )
        if contact.isValid():
            self.model.setY( self.model, self.shape.getRadius() - contact.getContactPosition() )
        else:
            self.model.setY( self.model, -self.shape.getSuspensionTravel() )
        self.tiremodel.setP( self.tiremodel.getP() + ( dt*self.shape.getAxleSpeed()*57.3 ) )
        self.model.setR( self.model, -self.shape.getSteerAngle() )
        

class Car:
    """ """
    
    def __init__( self, physxScene, xmlfile ):
        """ """
        #self.initChassis( physxScene );
        #self.initTires( physxScene )
        self.tires = []     # Holds the Car's tires
        self.steer = 0.0    # Represents current steering value
        self.initByXml( physxScene, xmlfile )
        
        
    def initByXml(self, physxScene, xmlfile):
        xmldoc = minidom.parse( xmlfile )
        carNode = xmldoc.getElementsByTagName( 'car' )[0]
        
        # Setup some global attributes for the car.
        self.type = carNode.getAttribute( 'type' )
        self.innerSteer = float( carNode.getAttribute( 'turn-angle-inside' ) )
        self.outerSteer = float( carNode.getAttribute( 'turn-angle-outside' ) )
        
        # Start initializing the chassis ...
        chassisNode = xmldoc.getElementsByTagName( 'chassis' )[0]
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
            
        
    def initChassis( self, physxScene ):
        shapeDesc = PhysxBoxShapeDesc();
        shapeDesc.setDimensions( Vec3( 0.9, 2.1, 0.4 ) )
        shapeDesc.setLocalPos( Point3( 0, 0, -0.3 ))
        shapeDesc2 = PhysxBoxShapeDesc()
        shapeDesc2.setDimensions( Vec3( 0.8, 1.15, 0.37 ))
        shapeDesc2.setLocalPos( Point3( 0, 1, 0.4 ))
        bodyDesc = PhysxBodyDesc()
        bodyDesc.setMass( 2000.0 )
        actorDesc = PhysxActorDesc()
        actorDesc.setBody( bodyDesc )
        actorDesc.setName( 'Chassis' )
        actorDesc.addShape( shapeDesc )
        actorDesc.addShape( shapeDesc2 )
        actorDesc.setGlobalPos( Point3( 0, 0, 2 ))
        self.chassis = physxScene.createActor( actorDesc );
        self.chassis.setCMassOffsetLocalPos( Point3( 0, -0.5, -0.6 ) )
        self.chassisModel = loader.loadModel( 'Resources/Models/Defender' )
        self.chassisModel.reparentTo( render )
        
    def initTires(self, physxScene):
        rubberDesc = PhysxMaterialDesc()
        rubberDesc.setRestitution(0.1)
        rubberDesc.setStaticFriction(1.2)
        rubberDesc.setDynamicFriction(0.1)
        mRubber = physxScene.createMaterial( rubberDesc )
        
        self.tires = []
        self.tires.append( Tire( physxScene, "flTire", Point3( 0.8, -1.4, -0.7 ), self.chassis, 180, mRubber ) );
        self.tires.append( Tire( physxScene, "frTire", Point3( -0.8, -1.4, -0.7 ), self.chassis, 0, mRubber ) );
        self.tires.append( Tire( physxScene, "rrTire", Point3( -0.8, 1.25, -0.7 ), self.chassis, 0, mRubber ) );
        self.tires.append( Tire( physxScene, "rlTire", Point3( 0.8, 1.25, -0.7 ), self.chassis, 180, mRubber ) );
        
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
        #self.tires[2].shape.setBrakeTorque( brake )
        #self.tires[3].shape.setBrakeTorque( brake )
        
    def setMotorTorque(self, torque):
        """ Sets the motor torque on the car.  The value ranges from 0.0 to 1.0, 1.0 being maximum torque"""
        if torque < 0.0:
            torque = 0.0
        elif torque > 1.0:
            torque = 1.0
        torque *= 100
        for tire in self.tires:
            if tire.torque:
                tire.shape.setMotorTorque( torque )
        #self.tires[0].shape.setMotorTorque( torque )
        #self.tires[1].shape.setMotorTorque( torque )
        #self.tires[2].shape.setMotorTorque( torque )
        #self.tires[3].shape.setMotorTorque( torque )
        
    def simulate(self,dt):
        self.chassisModel.setPosQuat( self.chassis.getGlobalPos(), self.chassis.getGlobalQuat() )
        for tire in self.tires:
            tire.simulate(dt);
            #matrix = tire.shape.getLocalMat()
            
            #tire.model.setMat( matrix )
            #print tire.shape.getName() + " axleSpd=" + str( tire.shape.getAxleSpeed() ) + " susp=" + str( tire.shape.getSuspensionTravel() )
            #tire.model.setPosQuat( tire.actor.getGlobalPos(), tire.actor.getGlobalQuat() )
        
        