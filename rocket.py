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

        self.__moment_of_inertia = (1/12) * self.__mass * ((self.__size[1] / PIXELS_PER_METER) ** 2)

    def reset_environment(self):
        self.position[0] = random.randint(-300, 300) * PIXELS_PER_METER
        self.position[1] = random.randint(100, 500) * PIXELS_PER_METER
        self.__velocity[1] = random.uniform(0, 0.8) * PIXELS_PER_METER
        self.rotation = random.randint(-50, 50)
        self.__done = False
        self.__step_count = 0
        self.__prev_dist = math.sqrt(self.position[0]**2 + self.position[1]**2)

    def get_state(self) -> state.State:
        return state.State(
            (self.position[0] / (800 * PIXELS_PER_METER), # Screen width normalize
            self.position[1] / (1500 * PIXELS_PER_METER)), # Screen height normalize
            math.radians(self.__get_rotation_wrapped()),
            (self.__velocity[0] / 50.0, # Expected max velocity
            self.__velocity[1] / 50.0),
            self.__angular_velocity / 10.0,
            self.__currentAction.throttle,
            self.__currentAction.roll
        )

    def get_reward(self):
        reward = 0

        st = self.get_state()
        vert_vel = st.velocity[1]
        alt = st.distance_from_touchdown[1]
        rot = st.rotation
        ang_vel = st.angular_velocity
        lateral_vel = st.velocity[0]
        lateral_dist = st.distance_from_touchdown[0]


        # phase 1
        rew_phase1 = 0
        if vert_vel < 0:
            rew_phase1 = -15
        elif vert_vel > 0.4:
            rew_phase1 = 0.4
        else:
            rew_phase1 = 5

        # reward += rew_phase1

        # phase 2
        if vert_vel < -0.7 or alt > 0.5:
            self.__done = True
            return -1000

        rew_phase2 = 0
        descent_speed = 0.3
        vert_vel_error_descent = descent_speed - vert_vel
        rew_phase2 += 6 * np.exp(-2 * abs(vert_vel_error_descent)) - 1
        reward = 0.3 * rew_phase1 + rew_phase2

        # phase 2.5
        # rew_phase2_5 = 6 * np.exp(-3 * abs(ang_vel))

        # phase 3
        rew_phase3 = 6 * np.exp(-3 * abs(rot))
        rew_phase3 -= 4 * ang_vel**2

        # phase 4
        rew_phase4 = np.sign(lateral_vel) * -np.sign(lateral_dist) * 5
        if rew_phase4 == 0:
            rew_phase4 = -3
        if abs(lateral_dist) < 0.04:
            rew_phase4 = 10

        reward += rew_phase1 * 0.1 + rew_phase2 * 0.4 + rew_phase3 * 0.3 + rew_phase4
        return reward


    def get_done(self) -> bool:
        return self.__done

    def tick(self, dt, agent: agent.Agent):
        self.__apply_gravity()
        self.__apply_thrust(agent.get_action(self.get_state()))
        self.__update_kinematics(dt)

        self.__handle_collisions()

    def draw(self, graphics: graphics.Graphics):
        graphics.draw_image(self.__image, (0, 0), self.rotation, True, self.__image.get_rect().size)

    def __apply_gravity(self):
        self.__net_force[1] += GRAVITY * self.__mass

    def __get_rotation_wrapped(self):
        x = (self.rotation + 180) % 360
        return x - 180

    def __update_kinematics(self, dt):
        self.__velocity[0] += self.__net_force[0] / self.__mass * dt
        self.__velocity[1] += self.__net_force[1] / self.__mass * dt
        self.position[0] += self.__velocity[0] * PIXELS_PER_METER * dt
        self.position[1] -= self.__velocity[1] * PIXELS_PER_METER * dt

        self.__angular_velocity += (self.__net_torque / self.__moment_of_inertia) * dt
        self.rotation += math.degrees(self.__angular_velocity) * dt

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
        self.__net_torque += (self.__size[1] / 2 / PIXELS_PER_METER) * THRUST * math.sin(math.radians(gimbal_angle)) * a.throttle
