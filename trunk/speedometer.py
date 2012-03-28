from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib

class Speedometer(DirectObject):

    def __init__(self):
        self.initSpeedometer()

    def initSpeedometer(self):
        """Initialize display of the Speedometer."""

        #Load image of the speedometer on the screen.
        ppp = ( -1, 0, -0.7 )
        self.spdm = OnscreenImage(image = 'Resources/Images/speedometer.png', scale=0.25, pos = ppp )
        self.spdm.setTransparency(TransparencyAttrib.MAlpha) #Enable Transparency

        #Load image of the speedometer's pointer on the screen.
        self.pointer = OnscreenImage(image = 'Resources/Images/needle.png', scale=0.25, pos = ppp )
        self.pointer.setTransparency(TransparencyAttrib.MAlpha) #Enable Transparency
        self.updateSpeedometer(0)

    def updateSpeedometer(self, speed):
        """Update indicator of speed on the speedometer, i.e, angle of the pointer.
            - mainPlayerSpeed: Current speed of the player.
            - maxSpeed: maxSpeed of the player."""

        #Set range of the movement of the pointer, according to the image of the speedometer.
        minAngle, maxAngle = 0 , 270
        maxSpeed = 280
                
        #Calculate the new current angle of the pointer.
        currentAngle = (speed - 46) * maxAngle / maxSpeed

        #Set new rotation to the pointer.
        self.pointer.setR(currentAngle)
