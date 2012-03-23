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
        
        self.debugNP = render.attachNewNode(self.physxScene.getDebugGeomNode())
        self.debugNP.node().on()
        self.debugNP.node().visualizeWorldAxes(True)
        
        self.keyControl = KeyControl()
        #render.setShaderAuto() 
        
    def setupPhysX(self):
        self.physx = PhysxManager.getGlobalPtr()
        sceneDesc = PhysxSceneDesc()
        sceneDesc.setGravity(Vec3(0, 0, -9.81))
        self.physxScene = self.physx.createScene(sceneDesc)
        m0 = self.physxScene.getMaterial(0)
        m0.setRestitution(0.1)
        m0.setStaticFriction(0.3)
        m0.setDynamicFriction(0.3)
    
    def addGround(self):
        groundShape = PhysxPlaneShapeDesc()
        groundShape.setPlane( Vec3( 0, 0, 1 ), 0 );
        groundActor = PhysxActorDesc();
        groundActor.setName( 'ground' )
        groundActor.addShape( groundShape )
        self.ground = self.physxScene.createActor( groundActor )
    
    def setupLight(self):
        self.light = render.attachNewNode(DirectionalLight("Spot")) 
        self.light.node().setScene(render) 
        self.light.node().setShadowCaster(True) 
        render.setLight(self.light) 
        
    def simulate(self, task):
        dt = globalClock.getDt()
        self.physxScene.simulate(dt)
        self.physxScene.fetchResults()
        self.car.simulate()
        self.keyControl.controlCar( self.car )
        base.cam.lookAt( self.car.chassis.getGlobalPos() )
        #print "num actors=" + str( self.physxScene.getNumActors() )
        return task.cont
    

#base.disableMouse()
base.cam.setPos(10, -25, 5)
base.cam.lookAt(0, 0, 0)

world = World()

run()
