import arcade
from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class PlayerCar(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("assets/sprites/player/player_car.png", scale=2.0)
        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.speed = 5
        self.max_speed = 10
        self.acceleration = 0.2
        self.hit_wall = False

    def update(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Keep the car within screen boundaries and check for wall collisions
        if self.center_x < 50:
            self.center_x = 50
            print("Hit Left wall")
            self.hit_wall = True
            self.speed = 2
        elif self.center_x > 450:
            self.center_x = 450
            print("Hit Right wall")
            self.hit_wall = True
            self.speed = 2
        else: 
            self.hit_wall = False
            self.speed = 5    
    def on_draw(self):
        arcade.start_render()
        if self.hit_wall:
            arcade.draw_text("Hit wall!", self.width//2, self.height//2, arcade.color.WHITE, 80, anchor_x = "center", anchor_y = "center",  bold=True)
