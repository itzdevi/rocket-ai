import pygame
import graphics
import rocket
import ground
import touchdown_point
import agent

from constants import *

class App:
    def __init__(self, agent: agent.Agent):
        pygame.init()

        self.__agent = agent
        self.__graphics = graphics.Graphics((800, 600))
        self.env = rocket.Rocket()
        self.__ground = ground.Ground()
        self.__touchdown_point = touchdown_point.TouchdownPoint()
        self.__clock = pygame.time.Clock()
        self.__zoom = 1
        self.__running = True

        self.env.reset_environment()

    def is_running(self): return self.__running

    def tick(self):
        self.__handle_events()

        dt = self.__clock.tick(FPS) / 1000 * TIME_MULTIPLIER_FACTOR
        self.env.tick(dt, self.__agent)

        if self.env.get_done():
            self.env.reset_environment()

    def draw(self):
        self.__graphics.set_zoom(self.__zoom)
        self.__graphics.fill((0, 0, 0))

        self.__ground.draw(self.__graphics, self.env.position, self.__graphics.screen_size, self.__zoom)
        self.__touchdown_point.draw(self.__graphics, self.env.position, self.__zoom)
        self.env.draw(self.__graphics)

        pygame.display.flip()

    def __handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
            if event.type == pygame.MOUSEWHEEL:
                self.__zoom += event.y * 0.03
                self.__zoom = min(5, max(0.04, self.__zoom))
