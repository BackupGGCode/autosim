import direct.directbase.DirectStart 
from panda3d.core import Vec3
from panda3d.bullet import *

from Car import Car

class World:
    """ """
    
    def __init__(self):
        """ Constructs the World """
        self.setupBullet()
        self.addGround()
        
    def setupBullet(self):
        self.bulletWorld = BulletWorld()
        self.bulletWorld.setGravity( Vec3( 0, 0, -9.81 ) )
    
    def addGround(self):        
        shape = BulletPlaneShape(Vec3(0, 0, 1), 1)
        node = BulletRigidBodyNode( 'Ground' )
        node.addShape(shape)
        np = render.attachNewNode(node)
        np.setPos(0, 0, -2)
        self.bulletWorld.attachRigidBody(node)    

base.disableMouse()
base.cam.setPos(0, -15, 0)
base.cam.lookAt(0, 0, 0)

world = World()
car = Car( world.bulletWorld )

def update( task ):
    dt = globalClock.getDt()
    world.bulletWorld.doPhysics( dt, 10, 1.0/180.0 )
    return task.cont

taskMgr.add( update, 'update' )

run()
