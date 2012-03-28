import pygame 
from direct.showbase.DirectObject import DirectObject 
from direct.showbase.MessengerGlobal import messenger 
from Car import Car

class JoystickHandler(DirectObject): 
    def __init__(self): 
        pygame.init() 
        
        count = pygame.joystick.get_count() 
        self.__joysticks = [] 
        for i in range(count): 
            js = pygame.joystick.Joystick(i) 
            js.init() 
            self.__joysticks.append(js) 

        taskMgr.add(self.__on_joystick_polling, 'Joystick Polling') 
        
    def destroy(self): 
        pygame.quit() 
        
    def get_joysticks(self): 
        return self.__joysticks 
        
    def get_count(self): 
        return len(self.__joysticks) 
        
    def __on_joystick_polling(self, task): 
        for ev in pygame.event.get(): 
        
            if ev.type is pygame.JOYBUTTONDOWN: 
                name = 'joystick%d-button%d' % (ev.joy, ev.button) 
                messenger.send(name) 
                print name
                
            elif ev.type is pygame.JOYBUTTONUP: 
                name = 'joystick%d-button%d-up' % (ev.joy, ev.button) 
                messenger.send(name) 
                
            elif ev.type is pygame.JOYAXISMOTION: 
                name = 'joystick%d-axis%d' % (ev.joy, ev.axis) 
                messenger.send(name, [ev.value]) 
                
            elif ev.type is pygame.JOYBALLMOTION: 
                name = 'joystick%d-ball%d' % (ev.joy, ev.hat) 
                messenger.send(name, [ev.rel]) 
                
            elif ev.type is pygame.JOYHATMOTION: 
                name = 'joystick%d-hat%d' % (ev.joy, ev.hat) 
                messenger.send(name, [ev.value]) 

        return task.cont 

class SteeringControl(JoystickHandler): 
    def __init__(self, car): 
        JoystickHandler.__init__(self) 

        self.car = car

        self.accept('joystick0-axis0', self.steer) 
        self.accept('joystick0-axis2', self.gas) 
        self.accept('joystick0-axis3', self.brake) 
        self.accept('joystick0-axis4', self.clutch) 
        self.accept('joystick0-button8', self.forward)
        self.accept('joystick0-button9', self.backward)

    def steer(self, value):
        #print "steer " + str(value)
        car.setSteer(value)

    def gas(self, value):
        #Change range from 1.0 - -1.0 (where 1 is lowest) to 0 - -1 (where 0 is lowest)
        valForCar = (value -1) / 2
        #Now change max value from -1 to 1 but keep 0 as min value
        valForCar = abs(valForCar)
        #print "gas " + str(valForCar)
        car.setMotorTorque(value)

    def brake(self, value):
        #Change range from 1.0 - -1.0 (where 1 is lowest) to 0 - -1 (where 0 is lowest)
        valForCar = (value -1) / 2
        #Now change max value from -1 to 1 but keep 0 as min value
        valForCar = abs(valForCar)
        #print "brake " + str(valForCar)
        car.setBrake(value)

    def clutch(self, value):
        #Change range from 1.0 - -1.0 (where 1 is lowest) to 0 - -1 (where 0 is lowest)
        valForCar = (value -1) / 2
        #Now change max value from -1 to 1 but keep 0 as min value
        valForCar = abs(valForCar)
        #print "clutch " + str(valForCar)
        car.setClutch(value)

    def forward(self):
        #print "forward"
        car.setReverse(False)

    def backward(self):
        #print "backward"
        car.setReverse(True)


