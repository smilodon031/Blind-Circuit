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
        self.wall_slowdown_timer = 0  # Timer to maintain slow speed after wall hit

    def update(self, delta_time=0, SCREEN_WIDTH=None, SCREEN_HEIGHT=None):
        # Only allow horizontal movement; car never moves vertically
        self.center_x += self.change_x
        # self.center_y += self.change_y  # Disabled - car stays fixed vertically

        # Keep the car within screen boundaries and check for wall collisions
        if self.center_x < 100:
            self.center_x = 100
            print("Hit Left wall")
            self.hit_wall = True
            self.speed = 2
            self.wall_slowdown_timer = 20  # Slow down for 20 frames
        elif self.center_x > 400:
            self.center_x = 400
            print("Hit Right wall")
            self.hit_wall = True
            self.speed = 2
            self.wall_slowdown_timer = 20  # Slow down for 20 frames
        else: 
            self.hit_wall = False
            # Decrement slowdown timer when not hitting walls
            if self.wall_slowdown_timer > 0:
                self.wall_slowdown_timer -= 1
                self.speed = 2
            else:
                self.speed = 5    