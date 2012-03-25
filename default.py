import direct.directbase.DirectStart
from direct.showbase.Audio3DManager import Audio3DManager 
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from panda3d.physx import PhysxManager
from panda3d.physx import PhysxEnums
from panda3d.physx import PhysxSceneDesc
from panda3d.physx import PhysxBodyDesc
from panda3d.physx import PhysxActorDesc
from panda3d.physx import PhysxBoxShapeDesc
from panda3d.physx import PhysxPlaneShapeDesc
from panda3d.physx import PhysxPointOnLineJointDesc
from panda3d.physx import PhysxTriangleMeshDesc
from panda3d.physx import PhysxTriangleMesh
from panda3d.physx import PhysxTriangleMeshShape
from panda3d.physx import PhysxTriangleMeshShapeDesc
from panda3d.physx import PhysxKitchen

from skydome import SkyDome
from Car import Car
from keycontrol import KeyControl
from cameracontrol import CameraControl

class World( DirectObject ):
    """ """
    
    def __init__(self):
        """ Constructs the World """
        self.sky = SkyDome( "Resources/Models/skydome.egg" )
        self.sky.sky.setScale( Vec3( 10,10,10))
        self.setupPhysX()
        self.setup3DAudio()
        #self.addGround()
        self.setupLight()
        #self.car = Car( self.physxScene )
        self.car = Car( self.physxScene, self.audio3d, "defender.xml" )
        #self.car.setSteer( -1.0 )
        self.car.setActiveAudioProfile( 'outside' )
        self.initTrack()
        taskMgr.add(self.simulate, 'PhysX Simulation')
        self.keyControl = KeyControl()
        self.cameraControl = CameraControl( self.car )
        render.setShaderAuto() 
        #self.enablePhysxDebug()
        
    def initTrack(self):
        kitchen = PhysxKitchen()
        triMeshDesc = PhysxTriangleMeshDesc()
        self.trackCollision = loader.loadModel( "Resources/Models/TrackCollision.egg" )
        self.track = loader.loadModel( "Resources/Models/Track.egg" )
        #self.trackCollision.setScale( Vec3( 0.5, 0.5, 0.5 ) )
        triMeshDesc.setFromNodePath( self.trackCollision )
        triMesh = kitchen.cookTriangleMesh( triMeshDesc )
        triMeshShapeDesc = PhysxTriangleMeshShapeDesc()
        triMeshShapeDesc.setMesh( triMesh )
        actor = PhysxActorDesc()
        actor.setName( 'trackcollision' )
        actor.addShape( triMeshShapeDesc )
        self.physxtrack = self.physxScene.createActor( actor )
        self.track.reparentTo( render ) # todo: replace with nice model
        
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
        
    def setup3DAudio(self):
        self.audio3d = Audio3DManager( base.sfxManagerList[0], base.cam )
        #self.audio3d.setSoundVelocityAuto(#sound)
    
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
        sun.setHpr( 200, -45, 0 )
        render.setLight( sun )
        
    def simulate(self, task):
        dt = globalClock.getDt()
        self.physxScene.simulate(dt)
        self.physxScene.fetchResults()
        self.car.simulate(dt)
        self.keyControl.controlCar( self.car )
        #base.cam.lookAt( self.car.chassis.getGlobalPos() )
        self.cameraControl.simulate(dt)
        #print "num actors=" + str( self.physxScene.getNumActors() )
        return task.cont
    

#base.disableMouse()
base.cam.setPos(10, -25, 5)
base.cam.lookAt(0, 0, 0)
base.cam.node().getLens().setNear( 0.1 )
base.cam.node().getLens().setFov( 60 )

world = World()

run()
