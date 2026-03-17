import pygame
import graphics
import rocket
import ground

ROCKET_MASS = 1000
ROCKET_SIZE = (70, 150)
FPS = 60

class App:
    def __init__(self):
        pygame.init()

        self.__graphics = graphics.Graphics((800, 600))
        self.__env = rocket.Rocket(ROCKET_MASS, ROCKET_SIZE)
        self.__ground = ground.Ground()
        self.__clock = pygame.time.Clock()
        self.__zoom = 1
        self.__running = True

        self.__env.position = [0, 7500]

    def is_running(self): return self.__running

    def tick(self):
        self.__handle_events()

        dt = self.__clock.tick(FPS) / 1000
        self.__env.tick(dt)

    def draw(self):
        self.__graphics.set_zoom(self.__zoom)
        self.__graphics.fill((135, 206, 235))

        self.__env.draw(self.__graphics)
        self.__ground.draw(self.__graphics, self.__env.position, self.__graphics.screen_size, self.__zoom)

        pygame.display.flip()

    def __handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
            if event.type == pygame.MOUSEWHEEL:
                self.__zoom += event.y * 0.03
                self.__zoom = min(5, max(0.04, self.__zoom))
