import graphics

class TouchdownPoint:
    def draw(self, graphics: graphics.Graphics, rocket_position, zoom):
        graphics.draw_rect(
            (rocket_position[0] * zoom, rocket_position[1] * zoom),
            (400, 40),
            (255, 255, 255)
        )