import arcade
import random
from car import PlayerCar
import constants
from level1 import Level1Background

# Game state constants
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
        # FIXED: Load start screen sprite once during init, not every frame in on_draw
        self.start_screen_sprite = arcade.Sprite(
            "assets/sprites/player/start_screen.png",
            scale=1
        )
        self.start_screen_sprite.center_x = width // 2
        self.start_screen_sprite.center_y = height // 2
        # Load hit wall texture for shake effect
        self.hit_wall_rect = arcade.load_texture("assets/sprites/player/hit_wall.png")
        # Load custom font for all text
        arcade.load_font("assets/font/Pixelify_Sans/static/PixelifySans-Regular.ttf")
        self.font_name = "Pixelify Sans"


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
        # Reset viewport to normal state at start of each frame
        arcade.set_viewport(0, self.width, 0, self.height)

        if self.state == STATE_START:
            # FIXED: Sprite is now loaded once in __init__, just draw it here
            self.start_screen_sprite.draw()

        elif self.state == STATE_PLAYING:
            # Camera shake effect for obstacle hits
            if self.background.shake_time > 0:
                shake_x = random.uniform(-5, 5)
                shake_y = random.uniform(-5, 5)
                arcade.set_viewport(-shake_x, self.width - shake_x, -shake_y, self.height - shake_y)
            
            self.background.draw()
            self.player_list.draw()
            
            # Draw hit wall rectangle with shake effect (shake managed by level1.py)
            if self.car.hit_wall:
                arcade.draw_texture_rectangle(
                    constants.SCREEN_WIDTH//2 + self.background.hit_wall_shake_offset_x,
                    constants.SCREEN_HEIGHT//2 + self.background.hit_wall_shake_offset_y,
                    500, 800, self.hit_wall_rect
                )
            
            # Reset viewport
            arcade.set_viewport(0, self.width, 0, self.height)

        elif self.state == STATE_WIN:
            arcade.draw_text(
                "YOU WIN!",
                self.width//2,
                self.height//2 + 40,
                arcade.color.GREEN,
                50,
                anchor_x="center",
                font_name=self.font_name,
            )
            arcade.draw_text(
                "Press N for Next Level",
                self.width//2,
                self.height//2,
                arcade.color.WHITE,
                25,
                anchor_x="center",
                font_name=self.font_name,
            )

        elif self.state == STATE_LOSE:
            arcade.draw_text(
                "GAME OVER",
                self.width//2,
                self.height//2 + 40,
                arcade.color.RED,
                50,
                anchor_x="center",
                font_name=self.font_name,
            )
            arcade.draw_text(
                "Press R to Retry",
                self.width//2,
                self.height//2,
                arcade.color.WHITE,
                25,
                anchor_x="center",
                font_name=self.font_name,
            )


    def on_update(self, delta_time):
        self.background.update(delta_time)
        self.player_list.update()

        # Check win/lose conditions
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
                    self.level_index = 0  # Loop back to first level
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

