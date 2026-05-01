import pygame
import graphics
import math
import action
import agent
import state
from constants import *
import random
import numpy as np

class Rocket:
    def __init__(self):
        self.__image = pygame.image.load("./assets/rocket.png").convert_alpha()
        self.__size = self.__image.get_rect().size
        self.position = [0, 0]
        self.rotation = 0
        self.__velocity = [0, 0]
        self.__angular_velocity = 0
        self.__mass = ROCKET_MASS
        self.__net_force = [0, 0]
        self.__net_torque = 0
        self.__done = False
        self.__currentAction = action.Action(0, 0)
        self.__prev_dist = 0
        self.__step_count = 0

        self.__moment_of_inertia = (1/12) * self.__mass * ((self.__size[1]/2 / PIXELS_PER_METER)**2)

    def reset_environment(self):
        self.position[1] = random.randint(100, 500) * PIXELS_PER_METER
        # self.__velocity[1] = random.uniform(-1.3, 0.4) * PIXELS_PER_METER
        self.__velocity[1] = 0
        self.__done = False
        self.__step_count = 0
        self.__prev_dist = math.sqrt(self.position[0]**2 + self.position[1]**2)

    def get_state(self) -> state.State:
        # Use consistent normalization (Targeting -1 to 1)
        return state.State(
            (self.position[0] / (800 * PIXELS_PER_METER), # Screen width normalize
            self.position[1] / (1500 * PIXELS_PER_METER)), # Screen height normalize
            math.radians(self.rotation) / math.pi,
            (self.__velocity[0] / 50.0, # Expected max velocity
            self.__velocity[1] / 50.0),
            self.__angular_velocity / 10.0,
            self.__currentAction.throttle,
            self.__currentAction.roll
        )

    def get_reward(self):
        reward = 0

        st = self.get_state()

        # phase 1
        rew_phase1 = 0
        rew_phase1 += np.sign(st.velocity[1]) * 0.2

        reward += rew_phase1 * 1
        return reward


    def get_done(self) -> bool:
        return self.__done

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
        # self.__velocity[0] += self.__net_force[0] / self.__mass * dt
        self.__velocity[1] += self.__net_force[1] / self.__mass * dt
        # self.position[0] += self.__velocity[0] * PIXELS_PER_METER * dt
        self.position[1] -= self.__velocity[1] * PIXELS_PER_METER * dt

        # self.__angular_velocity += (self.__net_torque / self.__moment_of_inertia) * dt
        # self.rotation += self.__angular_velocity * dt

        self.__net_force[0] = 0
        self.__net_force[1] = 0
        self.__net_torque = 0

    def __handle_collisions(self):
        lower_bound = self.position[1] - self.__size[1] / 2
        if lower_bound <= 0:
            self.__velocity[0] = 0
            self.__velocity[1] = 0
            self.position[1] = self.__size[1] / 2
            self.__angular_velocity = 0
            self.__done = True

        self.__step_count += 1
        if self.__step_count >= 2000:
            self.__done = True

    def __apply_thrust(self, a: action.Action):
        a.roll = min(1, max(-1, a.roll))
        a.throttle = min(1, max(0, a.throttle))
        self.__currentAction = a

        gimbal_angle = a.roll * GIMBAL_ANGLE
        self.__net_torque += a.roll * REACTION_WHEEL_TORQUE

        rot_rad = math.radians(self.rotation + gimbal_angle)
        self.__net_force[0] += THRUST * math.sin(rot_rad) * a.throttle
        self.__net_force[1] -= THRUST * math.cos(rot_rad) * a.throttle
        self.__net_torque += (self.__size[1] / 2 * PIXELS_PER_METER) * THRUST * math.sin(math.radians(gimbal_angle)) * a.throttle