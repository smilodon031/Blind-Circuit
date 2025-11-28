import arcade

class PlayerCar(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("assets/sprites/player/player_car.png", scale=2.0)
        self.center_x = x
        self.center_y = y
        self.speed = 5   # movement speed

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
