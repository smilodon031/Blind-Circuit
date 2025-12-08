import arcade
from car import PlayerCar
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from track import ScrollingBackground

class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Blind Circuit")
        arcade.set_background_color(arcade.color.LIGHT_BLUE)

        # Player - position car at a fixed Y position near bottom of screen for visual consistency
        self.car = PlayerCar(width // 2, height // 4)  # Car stays near the bottom of the screen

        # Background
        self.background = ScrollingBackground(
            "assets/maps/prototype_map.tmx",
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
        # Only update the background (track scrolls based on car's speed)
        self.background.update()

        # Update car for horizontal movement only (no vertical movement)
        self.car.update()

        # Keep car's Y position fixed to maintain the illusion that it's not moving vertically
        # The track movement creates the illusion of forward movement
        self.car.center_y = self.height // 4

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.car.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.car.right_pressed = True
        elif key == arcade.key.UP:
            self.car.up_pressed = True
        elif key == arcade.key.DOWN:
            self.car.down_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.car.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.car.right_pressed = False
        elif key == arcade.key.UP:
            self.car.up_pressed = False
        elif key == arcade.key.DOWN:
            self.car.down_pressed = False
