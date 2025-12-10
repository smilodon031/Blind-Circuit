import arcade
from car import PlayerCar
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from track import ScrollingBackground

class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Blind Circuit")
        arcade.set_background_color(arcade.color.LIGHT_BLUE)

        # Initialize track and background - these will be set up in setup()
        self.background = None
        self.car = None
        self.player_list = None


    def setup(self):
        # Player
        self.car = PlayerCar(250, 400)

        # Make your own sprite list instead of Scene
        self.player_list = arcade.SpriteList()

        # Initialize the background with a simple track image or TMX map
        # For now, using what we have in the ScrollingBackground class
        map_path = "assets/maps/Level1.tmx"  # Use the same path as in track.py
        self.background = ScrollingBackground(map_path, self.car, self.width, self.height)

        # Add the car to the player list
        self.player_list.append(self.car)

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
