from pandac.PandaModules import * 

from panda3d.physx import PhysxActorDesc
from panda3d.physx import PhysxBodyDesc
from panda3d.physx import PhysxBoxShapeDesc
from panda3d.physx import PhysxD6JointDesc
from panda3d.physx import PhysxJointLimitSoftDesc
from panda3d.physx import PhysxJointDriveDesc
from panda3d.physx import PhysxSpringDesc 
from panda3d.physx import PhysxWheelShapeDesc


class Tire:
    """ """
    
    def __init__( self, physxScene, name, pos, carActor, hdg ):
        suspension = 0.2
        radius = 0.4
        heightModifier = (suspension + radius )/suspension;
        
        wheelDesc = PhysxWheelShapeDesc()
        wheelDesc.setRadius( 0.4 )
        wheelDesc.setLocalPos( pos )
        #wheelDesc.setInverseWheelMass( 0.1 )
        #wheelDesc.setSkinWidth( 0.5 )
        
        springDesc = PhysxSpringDesc()
        springDesc.setSpring( 10000 )
        springDesc.setDamper( 1000 )
        springDesc.setTargetValue( 0.2 )
        wheelDesc.setSuspensionTravel( 0.1 )
        wheelDesc.setSuspension( springDesc )
        
        self.model = loader.loadModel( "Resources/Models/Tire" )
        #self.model.reparentTo( render )
        #self.model.setH( hdg )
        self.shape = carActor.createShape( wheelDesc )
        #self.shape.setMotorTorque( 100 )
        self.steer = 0.0
        
        #actorDesc = PhysxActorDesc()
        #actorDesc.setName( name+"Actor" )
        #actorDesc.addShape( self.shape )
        #self.actor = physxScene.createActor( actorDesc )
        
class Car:
    """ """
    
    def __init__( self, physxScene ):
        """ """
        self.initChassis( physxScene );
        self.initTires( physxScene )
        
    def initChassis(self, physxScene):
        shapeDesc = PhysxBoxShapeDesc();
        shapeDesc.setDimensions( Vec3( 0.9, 2.1, 0.4 ) )
        shapeDesc.setLocalPos( Point3( 0, 0, -0.3 ))
        shapeDesc.setMass( 2200 )
        shapeDesc2 = PhysxBoxShapeDesc()
        shapeDesc2.setDimensions( Vec3( 0.8, 1.15, 0.37 ))
        shapeDesc2.setLocalPos( Point3( 0, 1, 0.4 ))
        shapeDesc2.setMass( 100 )
        bodyDesc = PhysxBodyDesc()
        bodyDesc.setMass( 2000.0 )
        actorDesc = PhysxActorDesc()
        actorDesc.setBody( bodyDesc )
        actorDesc.setName( 'Chassis' )
        actorDesc.addShape( shapeDesc )
        actorDesc.addShape( shapeDesc2 )
        actorDesc.setGlobalPos( Point3( 0, 0, 2 ))
        self.chassis = physxScene.createActor( actorDesc );
        self.chassisModel = loader.loadModel( 'Resources/Models/Defender' )
        self.chassisModel.reparentTo( render )
        
    def initTires(self, physxScene):
        self.tires = []
        self.tires.append( Tire( physxScene, "flTire", Point3( 0.8, -1.4, -0.7 ), self.chassis, 180 ) );
        self.tires.append( Tire( physxScene, "frTire", Point3( -0.8, -1.4, -0.7 ), self.chassis, 0 ) );
        self.tires.append( Tire( physxScene, "rrTire", Point3( -0.8, 1.25, -0.7 ), self.chassis, 0 ) );
        self.tires.append( Tire( physxScene, "rlTire", Point3( 0.8, 1.25, -0.7 ), self.chassis, 180 ) );
        self.tires[0].model.reparentTo( self.chassisModel )
        self.tires[1].model.reparentTo( self.chassisModel )
        self.tires[2].model.reparentTo( self.chassisModel )
        self.tires[3].model.reparentTo( self.chassisModel )
        
    def setSteer(self, steer):
        """ Set the car's steering value. The value ranges from -1.0 - 1.0, 0.0 being a neutral position """
        if steer < -1.0:
            steer = -1.0
        elif steer > 1.0:
            steer = 1.0
        self.steer = steer
        steer *= 45
        self.tires[0].shape.setSteerAngle( steer )
        self.tires[1].shape.setSteerAngle( steer )
        
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
        
    def simulate(self ):
        self.chassisModel.setPosQuat( self.chassis.getGlobalPos(), self.chassis.getGlobalQuat() )
        for tire in self.tires:
            matrix = tire.shape.getLocalMat()
            tire.model.setMat( matrix )
            #tire.model.setPosQuat( tire.actor.getGlobalPos(), tire.actor.getGlobalQuat() )
        