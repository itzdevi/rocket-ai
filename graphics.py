import pygame

class Graphics:
    def __init__(self, screen_size):
        self.__screen_size = screen_size
        self.__surface = pygame.display.set_mode(screen_size)
        self.__zoom = 1

    def fill(self, color):
        self.__surface.fill(color)

    def draw_rect(self, view_position, size, color):
        rect = pygame.Rect(
            self.__screen_size[0] / 2 + view_position[0] - size[0] / 2 * self.__zoom,
            self.__screen_size[1] / 2 + view_position[1] - size[1] / 2 * self.__zoom,
            size[0] * self.__zoom,
            size[1] * self.__zoom
        )
        pygame.draw.rect(self.__surface, color, rect)

    def draw_rect_absolute(self, left, top, size, color):
        rect = pygame.Rect(left, top, size[0], size[1])
        pygame.draw.rect(self.__surface, color, rect)

    def draw_image(self, image:  pygame.Surface, view_position, size: None):
        if size is None:
            rect = image.get_rect()
            rect.center = (self.__screen_size[0] / 2 + view_position[0], self.__screen_size[1] / 2)
        else:
            rect = pygame.Rect(
                self.__screen_size[0] / 2 + view_position[0] - size[0] / 2 * self.__zoom,
                self.__screen_size[1] / 2 + view_position[1] - size[1] / 2 * self.__zoom,
                size[0] * self.__zoom,
                size[1] * self.__zoom
            )
        self.__surface.blit(image, rect)



    def set_zoom(self, zoom):
        self.__zoom = zoom