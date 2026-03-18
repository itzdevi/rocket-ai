import pygame
import graphics
import math
import action
import agent
import state

THRUST = 20000
GIMBAL_ANGLE = 7
REACTION_WHEEL_TORQUE = 850964.4444
GRAVITY = 10
PIXELS_PER_METER = 6

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

    def get_state(self) -> state.State:
        return state.State(
            self.position,
            self.rotation,
            self.__velocity,
            self.__angular_velocity
        )

    def tick(self, dt, agent: agent.Agent):
        self.__apply_gravity()
        self.__apply_thrust(agent.get_action(self.get_state()))
        self.__update_kinematics(dt)

        self.__handle_collisions()

    def draw(self, graphics: graphics.Graphics):
        graphics.draw_image(self.__image, (0, 0), self.rotation)

    def __apply_gravity(self):
        self.__net_force[1] += GRAVITY * self.__mass

    def __update_kinematics(self, dt):
        self.__velocity[0] += self.__net_force[0] / self.__mass * dt
        self.__velocity[1] += self.__net_force[1] / self.__mass * dt
        self.position[0] += self.__velocity[0] * PIXELS_PER_METER * dt
        self.position[1] -= self.__velocity[1] * PIXELS_PER_METER * dt

        moment_of_inertia = (1/12) * self.__mass * ((self.__size[1]/2 / PIXELS_PER_METER)**2)
        self.__angular_velocity += (self.__net_torque / moment_of_inertia) * dt
        self.rotation += self.__angular_velocity * dt

        self.__net_force[0] = 0
        self.__net_force[1] = 0
        self.__net_torque = 0

    def __handle_collisions(self):
        lower_bound = self.position[1] - self.__size[1] / 2
        if lower_bound <= 0:
            self.__velocity[0] = 0
            self.__velocity[1] = 0
            self.__angular_velocity = 0
            self.position[1] = self.__size[1] / 2

    def __apply_thrust(self, a: action.Action):
        gimbal_angle = a.roll * GIMBAL_ANGLE
        self.__net_torque += a.roll * REACTION_WHEEL_TORQUE

        rot_rad = math.radians(self.rotation + gimbal_angle)
        self.__net_force[0] += THRUST * math.sin(rot_rad) * a.throttle
        self.__net_force[1] -= THRUST * math.cos(rot_rad) * a.throttle
        self.__net_torque += (self.__size[1] / 2 * PIXELS_PER_METER) * THRUST * math.sin(math.radians(gimbal_angle)) * a.throttle