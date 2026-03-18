import numpy as np

class State:
    def __init__(self, position: list[float, float], rotation: float, velocity: list[float, float], angular_velocity: float):
        self.position = position
        self.rotation = rotation
        self.velocity = velocity
        self.angular_velocity = angular_velocity

    def __call__(self):
        return np.array([
            self.position[0],
            self.position[1],
            self.rotation,
            self.velocity[0],
            self.velocity[1],
            self.angular_velocity
        ], dtype=np.float32)