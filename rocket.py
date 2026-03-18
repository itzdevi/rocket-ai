import graphics

class Rocket:
    def __init__(self, __mass, size):
        self.__size = size
        self.__position = [0, 0]
        self.__rotation = [0, 0]
        self.__velocity = [0, 0]
        self.__angular_velocity = [0, 0]
        self.mass = __mass
        self.__net_force = [0, 0]
        self.__net_torque = [0, 0]

    def tick(self, dt):
        self.__apply_gravity()
        self.__update_kinematics(dt)

        self.__handle_collisions()

    def draw(self, graphics: graphics.Graphics):
        graphics.draw_rect((0, 0), self.__size, (255, 255, 255))

    def __apply_gravity(self):
        self.__net_force[1] += 750 * self.mass

    def __update_kinematics(self, dt):
        self.__velocity[0] += self.__net_force[0] / self.mass * dt
        self.__velocity[1] += self.__net_force[1] / self.mass * dt
        self.__position[0] += self.__velocity[0] * dt
        self.__position[1] -= self.__velocity[1] * dt

        self.__net_force[0] = 0
        self.__net_force[1] = 0

    def __handle_collisions(self):
        lower_bound = self.__position[1] - self.__size[1] / 2
        if lower_bound <= 0:
            self.__velocity[1] = 0
            self.__position[1] = self.__size[1] / 2