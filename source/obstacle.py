import arcade


class Obstacle(arcade.Sprite):
    """Simple obstacle sprite."""
    def __init__(self, x, y, width=32, height=32):
        super().__init__()
        texture = arcade.make_soft_square_texture(32, arcade.color.RED, outer_alpha=255)
        self.texture = texture
        self.scale = 1.0
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height

