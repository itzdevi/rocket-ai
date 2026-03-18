import pygame
from copy import copy

class Graphics:
    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.__surface = pygame.display.set_mode(screen_size)
        self.__zoom = 1

    def fill(self, color):
        self.__surface.fill(color)

    def draw_rect(self, view_position, size, color):
        rect = pygame.Rect(
            self.screen_size[0] / 2 + view_position[0] - size[0] / 2 * self.__zoom,
            self.screen_size[1] / 2 + view_position[1] - size[1] / 2 * self.__zoom,
            size[0] * self.__zoom,
            size[1] * self.__zoom
        )
        pygame.draw.rect(self.__surface, color, rect)

    def draw_rect_absolute(self, left, top, size, color):
        rect = pygame.Rect(left, top, size[0], size[1])
        pygame.draw.rect(self.__surface, color, rect)

    def draw_image(self, image:  pygame.Surface, view_position, rotation, size=None):
        image_cpy = copy(image)

        if size:
            image_cpy = pygame.transform.scale(image_cpy, size)

        rect = image_cpy.get_rect()
        rect.size = rect.size[0] * self.__zoom, rect.size[1] * self.__zoom
        rect.left = self.screen_size[0] / 2 + view_position[0] - rect.width / 2
        rect.top = self.screen_size[1] / 2 + view_position[1] - rect.height / 2
        image_cpy = pygame.transform.scale(image_cpy, rect.size)

        image_cpy = pygame.transform.rotate(image_cpy, rotation)
        rect = image_cpy.get_rect(center=rect.center)

        self.__surface.blit(image_cpy, rect)



    def set_zoom(self, zoom):
        self.__zoom = zoom