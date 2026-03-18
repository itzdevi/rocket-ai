import pygame
import graphics

class Rocket:
    def __init__(self, mass):
        self.__image = pygame.image.load("./assets/rocket.png").convert_alpha()
        self.__size = self.__image.get_rect().size
        self.position = [0, 0]
        self.rotation = 0
        self.__velocity = [0, 0]
        self.__angular_velocity = 0
        self.__mass = mass
        self.__net_force = [0, 0]
        self.__net_torque = 0


    def tick(self, dt):
        self.__apply_gravity()
        self.__update_kinematics(dt)

        self.__handle_collisions()

    def draw(self, graphics: graphics.Graphics):
        graphics.draw_image(self.__image, (0, 0), self.rotation)

    def __apply_gravity(self):
        self.__net_force[1] += 750 * self.__mass

    def __update_kinematics(self, dt):
        self.__velocity[0] += self.__net_force[0] / self.__mass * dt
        self.__velocity[1] += self.__net_force[1] / self.__mass * dt
        self.position[0] += self.__velocity[0] * dt
        self.position[1] -= self.__velocity[1] * dt

        self.__net_force[0] = 0
        self.__net_force[1] = 0

    def __handle_collisions(self):
        lower_bound = self.position[1] - self.__size[1] / 2
        if lower_bound <= 0:
            self.__velocity[1] = 0
            self.position[1] = self.__size[1] / 2