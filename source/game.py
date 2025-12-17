import arcade
from car import PlayerCar
import constants
from level1 import Level1Background

STATE_START = 0
STATE_PLAYING = 1
STATE_WIN = 2
STATE_LOSE = 3

class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Blind Circuit")
        arcade.set_background_color(arcade.color.LIGHT_BLUE)

        # Initialize track and background - these will be set up in setup()
        self.background = None
        self.car = None
        self.player_list = None
        self.current_level = 1
        self.state = STATE_START
        self.level_index = 0  # starts at first level


    def setup(self):
        # Player
        self.car = PlayerCar(250, 400)

        # Make your own sprite list instead of Scene
        self.player_list = arcade.SpriteList()

        # Add the car to the player list
        self.player_list.append(self.car)


        level_class = constants.LEVEL_CLASSES[self.level_index]
        self.background = level_class(self.car, self.width, self.height)

    def on_draw(self):
        self.clear()

        if self.state == STATE_START:
            arcade.draw_text(
                "BLIND CIRCUIT",
                self.width//2,
                self.height//2 + 80,
                arcade.color.WHITE,
                60,
                anchor_x="center"
            )
            arcade.draw_text(
                "PRESS ANY KEY TO START",
                self.width//2,
                self.height//2,
                arcade.color.WHITE,
                30,
                anchor_x="center"
            )

        elif self.state == STATE_PLAYING:
            self.background.draw()
            self.player_list.draw()

        elif self.state == STATE_WIN:
            arcade.draw_text(
                "YOU WIN!",
                self.width//2,
                self.height//2 + 40,
                arcade.color.GREEN,
                50,
                anchor_x="center"
            )
            arcade.draw_text(
                "Press N for Next Level",
                self.width//2,
                self.height//2,
                arcade.color.WHITE,
                25,
                anchor_x="center"
            )

        elif self.state == STATE_LOSE:
            arcade.draw_text(
                "GAME OVER",
                self.width//2,
                self.height//2 + 40,
                arcade.color.RED,
                50,
                anchor_x="center"
            )
            arcade.draw_text(
                "Press R to Retry",
                self.width//2,
                self.height//2,
                arcade.color.WHITE,
                25,
                anchor_x="center"
            )


        # Draw "Hit wall!" text if car hit a wall (based on slowdown timer)
        if self.car.hit_wall:
            arcade.draw_text("Hit wall!", self.width//2, self.height//2, arcade.color.WHITE, 80, anchor_x="center", anchor_y="center", bold=True)

    def on_update(self, delta_time):
        self.background.update(delta_time)
        self.player_list.update()
        
        if self.car.explosion_over:
            self.state = STATE_LOSE
        if self.car.race_won:
            self.state = STATE_WIN

    def on_key_press(self, key, modifiers):

        if self.state == STATE_START:
            self.state = STATE_PLAYING
            self.setup()
            return

        if self.state == STATE_WIN:
            if key == arcade.key.N:
                self.level_index += 1
                if self.level_index >= len(constants.LEVEL_CLASSES):
                    self.level_index = 0  # Loop back or handle final screen
                self.state = STATE_PLAYING
                self.setup()
            return

        if self.state == STATE_LOSE:
            if key == arcade.key.R:
                self.state = STATE_PLAYING
                self.setup()
            return

        # Only allow car movement when playing and not in losing state
        if self.state == STATE_PLAYING and not self.car.losing:
            if key == arcade.key.LEFT:
                self.car.left_pressed = True
            elif key == arcade.key.RIGHT:
                self.car.right_pressed = True
            elif key == arcade.key.UP:
                self.car.up_pressed = True
            elif key == arcade.key.DOWN:
                self.car.down_pressed = True

    def on_key_release(self, key, modifiers):
        if self.state != STATE_PLAYING:
            return
        
        # Ignore key releases during losing state
        if self.car.losing:
            return

        if key == arcade.key.LEFT:
            self.car.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.car.right_pressed = False
        elif key == arcade.key.UP:
            self.car.up_pressed = False
        elif key == arcade.key.DOWN:
            self.car.down_pressed = False

