import pygame

import constants
import graphics

class Earth:
    def __init__(self):
        self.__image = pygame.image.load("./assets/earth.png").convert_alpha()
        self.__size = self.__image.get_rect().size
        
    def draw(self, graphics: graphics.Graphics, zoom):
        graphics.draw_image(self.__image, (-120, -180), 0 , False, (self.__size[0] / 16, self.__size[1] / 16))