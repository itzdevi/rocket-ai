import graphics

class Ground:
    def draw(self, graphics: graphics.Graphics, rocket_position, screen_size, zoom):
        graphics.draw_rect_absolute(
            0,
            screen_size[1] / 2 + rocket_position[1] * zoom,
            (
                screen_size[0],
                screen_size[1] / 2 + rocket_position[1] * zoom
            ),
            (85, 82, 83)
        )