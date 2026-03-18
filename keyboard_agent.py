import agent
import action
import pygame

class KeyboardAgent(agent.Agent):
    def get_action(self, state):
        throttle = 0
        roll = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            throttle = 1
        if keys[pygame.K_a]:
            roll = 1
        if keys[pygame.K_d]:
            roll = -1
        return action.Action(throttle, roll)