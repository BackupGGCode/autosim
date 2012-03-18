
from panda3d.bullet import *
from pandac.PandaModules import * 

class Car:
    """ """
    
    def __init__(self, bulletWorld ):
        """ """
        #Chassis body
        shape = BulletBoxShape( Vec3( 0.7, 1.5, 0.5 ) )
        ts = TransformState.makePos( Point3( 0, 0, 0.5 ) )
        
        chassisNP = render.attachNewNode( BulletRigidBodyNode( 'Vehicle' ) )
        chassisNP.node().addShape(shape, ts)
        chassisNP.setPos( 0, 0, 5 )
        chassisNP.node().setMass( 800.0 )
        chassisNP.node().setDeactivationEnabled( False )
        
        bulletWorld.attachRigidBody( chassisNP.node() )
        
        # Chassis geometry
        loader.loadModel( 'Resources/Models/Defender.lwo' ).reparentTo( chassisNP )
        
        # Vehicle
        vehicle = BulletVehicle( bulletWorld, chassisNP.node() )
        vehicle.setCoordinateSystem( ZUp )
        bulletWorld.attachVehicle( vehicle )
        
        wheelNP = loader.loadModel( 'Resources/Models/Tire.lwo' )        
        wheel = vehicle.createWheel()
        wheel.setNode( wheelNP.node() )
        wheel.setChassisConnectionPointCs( Point3( 0.8, 1.1, 0.3 ) )
        wheel.setFrontWheel( True )
        
        wheel.setWheelDirectionCs(Vec3(0, 0, -1))
        wheel.setWheelAxleCs(Vec3(1, 0, 0))
        wheel.setWheelRadius(0.25)
        wheel.setMaxSuspensionTravelCm(40.0)
        
        wheel.setSuspensionStiffness(40.0)
        wheel.setWheelsDampingRelaxation(2.3)
        wheel.setWheelsDampingCompression(4.4)
        wheel.setFrictionSlip(100.0)
        wheel.setRollInfluence(0.1)
        
        # Steering info
        steering = 0.0            # degree
        steeringClamp = 45.0      # degree
        steeringIncrement = 120.0 # degree per second
        
        # Process input
        engineForce = 0.0
        brakeForce = 0.0
        
        #if inputState.isSet('forward'):
        #    engineForce = 1000.0
        #    brakeForce = 0.0
            
        #if inputState.isSet('reverse'):
        #    engineForce = 0.0
        #    brakeForce = 100.0
            
        #if inputState.isSet('turnLeft'):
        #    steering += dt * steeringIncrement
        #    steering = min(steering, steeringClamp)
            
        #if inputState.isSet('turnRight'):
        #    steering -= dt * steeringIncrement
        #    steering = max(steering, -steeringClamp)
            
        # Apply steering to front wheels
        #vehicle.setSteeringValue(steering, 0)
        #vehicle.setSteeringValue(steering, 1)
        
        # Apply engine and brake to rear wheels
        #vehicle.applyEngineForce(engineForce, 2)
        #vehicle.applyEngineForce(engineForce, 3)
        #vehicle.setBrake(brakeForce, 2)
        #vehicle.setBrake(brakeForce, 3)
