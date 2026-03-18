import agent
import pygame
import action

class ControllerAgent(agent.Agent):
    def __init__(self):
        pygame.joystick.init()
        self.__controller = pygame.joystick.Joystick(0)
        self.__controller.init()

    def get_action(self, state):
        throttle = (-self.__controller.get_axis(1) + 1) / 2
        roll = -self.__controller.get_axis(2)
        return action.Action(throttle, roll)