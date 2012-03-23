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


class Tire:
    """ Represents a tire on a car, and the suspension """
    
    def __init__( self, physxScene, name, pos, carActor, hdg, material ):
        self.model = render.attachNewNode( name + "nodeBase" )
        self.tiremodel = loader.loadModel( "Resources/Models/Tire" )
        self.tiremodel.setR( hdg )
        self.initialH = hdg
        self.tiremodel.reparentTo( self.model )
        self.model.reparentTo( render )
        self.createWheelShapeTire( physxScene, name, pos, carActor, material )
        
    def createWheelShapeTire( self, physxScene, name, pos, carActor, material ):
        """ Creates a raycast tire using Wheel Shapes which are a simple way of creating physx tires. """
        wheelDesc = PhysxWheelShapeDesc()
        wheelDesc.setRadius( 0.4 )
        #wheelDesc.setWidth( 0.2 )
        #wheelDesc.setWheelApproximation( 10 )
        wheelDesc.setLocalPos( pos )
        wheelDesc.setMaterial( material )
        springDesc = PhysxSpringDesc()
        springDesc.setSpring( 8000 )
        springDesc.setDamper( 500 )
        #springDesc.setTargetValue( 0.2 )
        wheelDesc.setSuspensionTravel( 0.2 )
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
    
    def __init__( self, physxScene ):
        """ """
        self.initChassis( physxScene );
        self.initTires( physxScene )
        self.steer = 0.0
        
    def initChassis( self, physxScene ):
        shapeDesc = PhysxBoxShapeDesc();
        shapeDesc.setDimensions( Vec3( 0.9, 2.1, 0.4 ) )
        shapeDesc.setLocalPos( Point3( 0, 0, -0.3 ))
        shapeDesc2 = PhysxBoxShapeDesc()
        shapeDesc2.setDimensions( Vec3( 0.8, 1.15, 0.37 ))
        shapeDesc2.setLocalPos( Point3( 0, 1, 0.4 ))
        bodyDesc = PhysxBodyDesc()
        #mat = Mat4.translateMat( Vec3( 0, 1.6, -0.6 ) )
        bodyDesc.setMass( 2000.0 )
        #bodyDesc.setMassLocalMat( mat )
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
        outerMax = 32
        innerMax = 37
        if steer < 0:
            self.tires[0].shape.setSteerAngle( innerMax * steer )
            self.tires[1].shape.setSteerAngle( outerMax * steer )
        else:
            self.tires[0].shape.setSteerAngle( outerMax * steer )
            self.tires[1].shape.setSteerAngle( innerMax * steer )
        
    def setBrake(self, brake):
        """ Sets the brake force on the car.  The value ranges from 0.0 to 1.0, 1.0 being maximum brake applied """
        if brake < 0.0:
            brake = 0.0
        elif brake > 1.0:
            brake = 1.0
        brake *= 1000
        self.tires[2].shape.setBrakeTorque( brake )
        self.tires[3].shape.setBrakeTorque( brake )
        
    def setMotorTorque(self, torque):
        """ Sets the motor torque on the car.  The value ranges from 0.0 to 1.0, 1.0 being maximum torque"""
        if torque < 0.0:
            torque = 0.0
        elif torque > 1.0:
            torque = 1.0
        torque *= 100
        self.tires[0].shape.setMotorTorque( torque )
        self.tires[1].shape.setMotorTorque( torque )
        self.tires[2].shape.setMotorTorque( torque )
        self.tires[3].shape.setMotorTorque( torque )
        
    def simulate(self,dt):
        self.chassisModel.setPosQuat( self.chassis.getGlobalPos(), self.chassis.getGlobalQuat() )
        for tire in self.tires:
            tire.simulate(dt);
            #matrix = tire.shape.getLocalMat()
            
            #tire.model.setMat( matrix )
            #print tire.shape.getName() + " axleSpd=" + str( tire.shape.getAxleSpeed() ) + " susp=" + str( tire.shape.getSuspensionTravel() )
            #tire.model.setPosQuat( tire.actor.getGlobalPos(), tire.actor.getGlobalQuat() )
        