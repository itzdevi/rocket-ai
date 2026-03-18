import numpy as np

class State:
    def __init__(self, distance_from_touchdown: list[float, float], rotation: float, velocity: list[float, float], angular_velocity: float, throttle: float, roll: float):
        self.distance_from_touchdown = distance_from_touchdown
        self.rotation = rotation
        self.velocity = velocity
        self.angular_velocity = angular_velocity
        self.throttle = throttle
        self.roll = roll

    def __call__(self):
        return np.array([
            self.distance_from_touchdown[0],
            self.distance_from_touchdown[1],
            self.rotation,
            self.velocity[0],
            self.velocity[1],
            self.angular_velocity,
            self.throttle,
            self.roll
        ], dtype=np.float32)