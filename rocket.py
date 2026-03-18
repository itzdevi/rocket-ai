import pygame
import graphics
import math
import action
import agent
import state
from constants import *
import random

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

    def reset_environment(self):
        # Simplified starting conditions for curriculum learning
        self.position = [random.uniform(200, 300), random.uniform(400, 500)]
        self.rotation = random.uniform(-30, 30)
        self.__velocity = [random.uniform(-10, 0), random.uniform(-10, 10)]
        self.__angular_velocity = random.uniform(-5, 5)
        self.__done = False
        self.__prev_dist = math.sqrt(self.position[0]**2 + self.position[1]**2)

    def get_state(self) -> state.State:
        return state.State(
            (-self.position[0] / 300, -self.position[1] / 600),
            math.radians(self.rotation) / math.pi,
            (self.__velocity[0] / 20, self.__velocity[1] / 40),
            math.radians(self.__angular_velocity) / math.pi,
            self.__currentAction.throttle,
            self.__currentAction.roll
        )
    
    def get_reward(self):
        current_dist = math.sqrt(self.position[0]**2 + self.position[1]**2)

        # 1. Potential-based reward shaping for distance (reward for getting closer)
        reward = (self.__prev_dist - current_dist) * 0.1

        # Update for next step
        self.__prev_dist = current_dist

        # 2. Continuous penalties
        # Penalty for not being upright
        reward -= 0.005 * (abs(self.rotation) / 180.0)
        # Penalty for high velocity near ground (to encourage soft landing)
        if self.position[1] < 200:
            speed = math.sqrt(self.__velocity[0]**2 + self.__velocity[1]**2)
            reward -= 0.005 * (speed / 40)
        
        # Penalty for fuel usage
        reward -= 0.001 * self.__currentAction.throttle

        # 3. Terminal rewards
        if self.__done:
            # Check for successful landing (stricter conditions)
            if abs(self.position[0]) < 50 and abs(self.position[1] - self.__size[1]/2) < 5 and abs(self.__velocity[1]) < 5 and abs(self.rotation) < 10:
                reward += 20.0  # Big reward for success
            else:
                reward -= 10.0  # Big penalty for any other termination (crash, out of bounds)
                
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
        # Check for out of bounds
        if abs(self.position[0]) > 800 or self.position[1] > 1500:
            self.__done = True
            return

        # Check for ground collision using rocket's corners for more realistic physics
        half_w = self.__size[0] / 2
        half_h = self.__size[1] / 2
        rad = math.radians(self.rotation)
        sin_rad = math.sin(rad)
        cos_rad = math.cos(rad)

        corners = [
            (-half_w, -half_h), (half_w, -half_h),
            (-half_w, half_h), (half_w, half_h)
        ]
        
        for corner in corners:
            # Rotate corner
            rotated_x = corner[0] * cos_rad - corner[1] * sin_rad
            rotated_y = corner[0] * sin_rad + corner[1] * cos_rad
            
            # Get world position of corner's y-coordinate
            world_y = self.position[1] - rotated_y

            if world_y <= 0:
                self.__done = True
                # Stop physics immediately on crash to get a clear terminal state
                self.__velocity = [0, 0]
                self.__angular_velocity = 0
                return

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