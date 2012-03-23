import direct.directbase.DirectStart 
from panda3d.core import *
from panda3d.physx import PhysxManager
from panda3d.physx import PhysxEnums
from panda3d.physx import PhysxSceneDesc
from panda3d.physx import PhysxBodyDesc
from panda3d.physx import PhysxActorDesc
from panda3d.physx import PhysxBoxShapeDesc
from panda3d.physx import PhysxPlaneShapeDesc
from panda3d.physx import PhysxPointOnLineJointDesc

from skydome import SkyDome
from Car import Car
from keycontrol import KeyControl

class World:
    """ """
    
    def __init__(self):
        """ Constructs the World """
        self.sky = SkyDome( "Resources/Models/skydome.egg" )
        self.sky.sky.setScale( Vec3( 10,10,10))
        self.setupPhysX()
        self.addGround()
        self.setupLight()
        self.car = Car( self.physxScene )
        self.car.setSteer( -1.0 )
        taskMgr.add(self.simulate, 'PhysX Simulation')
        self.keyControl = KeyControl()
        #render.setShaderAuto() 
        
    def enablePhysxDebug(self):
        self.debugNP = render.attachNewNode(self.physxScene.getDebugGeomNode())
        self.debugNP.node().on()
        self.debugNP.node().visualizeWorldAxes(True)
        
    def setupPhysX(self):
        self.physx = PhysxManager.getGlobalPtr()
        sceneDesc = PhysxSceneDesc()
        sceneDesc.setGravity(Vec3(0, 0, -9.81))
        self.physxScene = self.physx.createScene(sceneDesc)
        mGround = self.physxScene.getMaterial(0)
        mGround.setRestitution(0.0)
        mGround.setStaticFriction(0.8)
        mGround.setDynamicFriction(0.8)
    
    def addGround(self):
        groundShape = PhysxPlaneShapeDesc()
        groundShape.setPlane( Vec3( 0, 0, 1 ), 0 );
        groundShape.setSkinWidth( 0.0 )
        groundActor = PhysxActorDesc();
        groundActor.setName( 'ground' )
        groundActor.addShape( groundShape )
        self.ground = self.physxScene.createActor( groundActor )
    
    def setupLight(self):
        ambient_source = AmbientLight('ambient')
        ambient_source.setColor(Vec4(0.082,0.133,0.255,1))
        ambient = render.attachNewNode(ambient_source.upcastToPandaNode())
        render.setLight( ambient )
        
        sun_source = DirectionalLight( 'sun' )
        sun_source.setColor( Vec4( 1, 0.96, 1, 1 ))
        sun_source.setScene( render )
        sun = render.attachNewNode( sun_source )
        sun.setHpr( 270, -45, 0 )
        render.setLight( sun )
        
    def simulate(self, task):
        dt = globalClock.getDt()
        self.physxScene.simulate(dt)
        self.physxScene.fetchResults()
        self.car.simulate(dt)
        self.keyControl.controlCar( self.car )
        base.cam.lookAt( self.car.chassis.getGlobalPos() )
        #print "num actors=" + str( self.physxScene.getNumActors() )
        return task.cont
    

#base.disableMouse()
base.cam.setPos(10, -25, 5)
base.cam.lookAt(0, 0, 0)

world = World()

run()
