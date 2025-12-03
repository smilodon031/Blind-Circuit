import arcade
from car import PlayerCar
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from track import ScrollingBackground

class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Blind Circuit")
        arcade.set_background_color(arcade.color.LIGHT_BLUE)
        # Player
        self.car = PlayerCar(250, 400)

        # Background
        self.background = ScrollingBackground(
            "assets/maps/road.png",
            self.car,
            width,
            height
        )

        # Make your own sprite list instead of Scene
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.car)

        
    def setup(self):
        pass

    def on_draw(self):
        self.clear()
        self.background.draw()
        self.player_list.draw()

        
        # Draw "Hit wall!" text if car hit a wall (based on slowdown timer)
        if self.car.hit_wall:
            arcade.draw_text("Hit wall!", self.width//2, self.height//2, arcade.color.WHITE, 80, anchor_x="center", anchor_y="center", bold=True)

    def on_update(self, delta_time):
        self.background.update()
        self.player_list.update()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.car.change_x = -self.car.speed
        elif key == arcade.key.RIGHT:
            self.car.change_x = self.car.speed
        elif key == arcade.key.UP:
            self.car.change_y = self.car.speed
        elif key == arcade.key.DOWN:
            self.car.change_y = -self.car.speed

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.car.change_x = 0
        elif key in (arcade.key.UP, arcade.key.DOWN):
            self.car.change_y = 0
