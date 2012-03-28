from panda3d.core import *
from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "framebuffer-multisample 1")
loadPrcFileData("", "prefer-parasite-buffer #f") 
loadPrcFileData("", "fullscreen 1 win-size 1440 900" )
import direct.directbase.DirectStart
from direct.showbase.Audio3DManager import Audio3DManager 
from direct.showbase.DirectObject import DirectObject

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
from speedometer import Speedometer
from stearingcontrol import SteeringControl

import sys

class World( DirectObject ):
    """ Dynamic world """
    
    def __init__(self):
        """ Constructs the World """
        self.sky = SkyDome( "Resources/Models/skydome.egg" )
        self.sky.sky.setScale( Vec3( 10,10,10))
        self.setupPhysX()
        self.setup3DAudio()
        
        self.car = Car( self.physxScene, self.audio3d, "defender.xml" )
        self.car.setActiveAudioProfile( 'outside' )
        
        self.setupLight()
        self.initTrack()
        taskMgr.add(self.simulate, 'PhysX Simulation')
        self.keyControl = KeyControl()
        self.steeringControl = SteeringControl( self.car )
        self.cameraControl = CameraControl( self.car )
        self.cameraControl.enableTowerCamera()
        self.speedometer = Speedometer();
        render.setShaderAuto() 
        self.accept( 'escape', sys.exit )
        #self.enablePhysxDebug()
        
    def initTrack(self):
        """ Loads the track model and the collision model for it. """
        kitchen = PhysxKitchen()
        
        trackCollision = loader.loadModel( "Resources/Models/TrackCollision.egg" )
        fenceCollision = loader.loadModel( "Resources/Models/FenceCollision.egg")
        self.track = loader.loadModel( "Resources/Models/Track.egg" )

        triMeshDesc = PhysxTriangleMeshDesc()
        triMeshDesc.setFromNodePath( trackCollision )
        triMesh = kitchen.cookTriangleMesh( triMeshDesc )
        triMeshShapeDesc = PhysxTriangleMeshShapeDesc()
        triMeshShapeDesc.setMesh( triMesh )
        
        triMeshDesc2 = PhysxTriangleMeshDesc()
        triMeshDesc2.setFromNodePath( fenceCollision )
        triMesh2 = kitchen.cookTriangleMesh( triMeshDesc2 )
        triMeshShapeDesc2 = PhysxTriangleMeshShapeDesc()
        triMeshShapeDesc2.setMesh( triMesh2 )
        
        actor = PhysxActorDesc()
        actor.setName( 'trackcollision' )
        actor.addShape( triMeshShapeDesc )
        actor.addShape( triMeshShapeDesc2 )
        self.physxtrack = self.physxScene.createActor( actor )
        
        self.track.reparentTo( render )
        loader.loadModel( "Resources/Models/Fence.egg" ).reparentTo( self.track )
        loader.loadModel( "Resources/Models/Rocks.egg" ).reparentTo( self.track )
        
        linfog = Fog( "Fog" )
        linfog.setColor( Vec4( 0.8, 0.85, 0.8, 1 ) )
        linfog.setExpDensity( 0.003 )
        self.track.attachNewNode(linfog)
        render.setFog(linfog)
        
    def enablePhysxDebug(self):
        """ Turns on physx visual debuggging """
        self.debugNP = render.attachNewNode(self.physxScene.getDebugGeomNode())
        self.debugNP.node().on()
        self.debugNP.node().visualizeWorldAxes(True)
        
    def setupPhysX(self):
        """ Sets up the physx world """
        self.physx = PhysxManager.getGlobalPtr()
        sceneDesc = PhysxSceneDesc()
        sceneDesc.setGravity(Vec3(0, 0, -9.81))
        self.physxScene = self.physx.createScene(sceneDesc)
        
        mGround = self.physxScene.getMaterial( 0 )
        mGround.setRestitution(0.0)
        mGround.setStaticFriction(0.8)
        mGround.setDynamicFriction(0.2)
        
    def setup3DAudio(self):
        """ Initializes the 3D audio manager """
        self.audio3d = Audio3DManager( base.sfxManagerList[0], base.cam )
    
    def setupLight(self):
        """ Sets up the scene lighting """
        ambient_source = AmbientLight('ambient')
        ambient_source.setColor(Vec4( 0.6, 0.65, 0.7, 1 ))
        ambient = render.attachNewNode(ambient_source.upcastToPandaNode())
        render.setLight( ambient )
        
        sun = render.attachNewNode( DirectionalLight( 'sun' ) )
        sun.node().setScene( render )
        render.setLight( sun )
        sun.reparentTo( self.car.chassisModel )
        sun.setH( -60 )
        sun.setP( -60 )
        sun.setPos( 0, 0, 10 )
        sun.node().getLens().setFov( 70 )
        sun.node().getLens().setNearFar( 1, 20 )
        sun.node().getLens().setFilmSize( 16, 16 )
        sun.node().setColor( Vec4( 1, 0.96, 1, 1 ))
        sun.node().setShadowCaster( True )
        self.sun = sun
        
        
    def simulate(self, task):
        """ Simulation loop, called every frame """
        dt = globalClock.getDt()
        self.physxScene.simulate(dt)
        self.physxScene.fetchResults()
        self.car.simulate(dt)
        self.keyControl.controlCar( self.car )
        self.cameraControl.simulate(dt)
        self.sun.setH( render, -60 )
        self.sun.setP( render, -60 )
        self.speedometer.updateSpeedometer( self.car.speed )
        return task.cont
    

#base.disableMouse()
base.cam.setPos(10, -25, 5)
base.cam.lookAt(0, 0, 0)
base.cam.node().getLens().setNear( 0.1 )
base.cam.node().getLens().setFov( 60 )
base.enableParticles()

render.setAntialias(AntialiasAttrib.MMultisample,1)

world = World()

run()
