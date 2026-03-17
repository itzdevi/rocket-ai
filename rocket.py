import graphics

class Rocket:
    def __init__(self, mass, size):
        self.size = size
        self.position = [0, 0]
        self.rotation = [0, 0]
        self.velocity = [0, 0]
        self.angular_velocity = [0, 0]
        self.mass = mass
        self.net_force = [0, 0]
        self.net_torque = [0, 0]

    def tick(self, dt):
        self.__apply_gravity()
        self.__update_kinematics(dt)

        self.__handle_collisions()

    def draw(self, graphics: graphics.Graphics):
        graphics.draw_rect((0, 0), self.size, (255, 255, 255))

    def __apply_gravity(self):
        self.net_force[1] += 750 * self.mass

    def __update_kinematics(self, dt):
        self.velocity[0] += self.net_force[0] / self.mass * dt
        self.velocity[1] += self.net_force[1] / self.mass * dt
        self.position[0] += self.velocity[0] * dt
        self.position[1] -= self.velocity[1] * dt

        self.net_force[0] = 0
        self.net_force[1] = 0

    def __handle_collisions(self):
        lower_bound = self.position[1] - self.size[1] / 2
        if lower_bound <= 0:
            self.velocity[1] = 0
            self.position[1] = self.size[1] / 2