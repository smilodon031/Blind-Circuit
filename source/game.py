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
        arcade.set_background_color(arcade.color.BLACK)

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
        
        # Dashboard textures will be loaded in setup()
        self.dashboard_textures = None
        # Smoothed speed value for HUD display
        self.display_speed = 0.0
        # Heart texture for lives display (loaded in setup)
        self.heart_texture = None
        # Skull texture for when out of lives (loaded in setup)
        self.skull_texture = None


    def setup(self):
        # Player
        self.car = PlayerCar(250, 400)

        # Make your own sprite list instead of Scene
        self.player_list = arcade.SpriteList()

        # Add the car to the player list
        self.player_list.append(self.car)

        # Load dashboard sprite sheet (2 columns, 5 rows = 10 frames, but we use frames 0-8)
        dashboard_path = "assets/sprites/player/dashboard.png"
        self.dashboard_textures = arcade.load_spritesheet(
            dashboard_path,
            sprite_width=500,
            sprite_height=200,
            columns=2,
            count=10
        )
        
        # Load heart texture for lives display (32x32 pixels)
        self.heart_texture = arcade.load_texture("assets/sprites/player/heart.png")
        # Load skull texture for when out of lives
        self.skull_texture = arcade.load_texture("assets/sprites/player/skull.png")
        
        # Initialize display speed to match car's initial speed
        self.display_speed = 0.0

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
                    502, 802, self.hit_wall_rect
                )
            
            # Reset viewport before drawing HUD elements (HUD should be in screen space)
            arcade.set_viewport(0, self.width, 0, self.height)
            
            # Draw dashboard HUD at bottom center of screen
            if self.dashboard_textures:
                speed_index = max(0, min(8, int(round(self.display_speed))))
                dashboard_texture = self.dashboard_textures[speed_index]
                arcade.draw_texture_rectangle(
                    self.width // 2,
                    100,
                    500,
                    200,
                    dashboard_texture
                )
            
            # Draw speed text (updates in increments of 10, positioned lower)
            speed_kmh = self.display_speed * 30.0
            # Round to nearest 10
            speed_rounded = int(round(speed_kmh / 10)) * 10
            speed_text = f"{speed_rounded}Km/hr"
            arcade.draw_text(
                speed_text,
                self.width // 2,
                50,  # Lowered by 50 pixels from 190
                arcade.color.WHITE,
                20,  # Reduced from 48
                anchor_x="center",
                font_name=self.font_name,
            )
            
            # Calculate track progress (using vertical/y-axis progress from level)
            if self.car and self.background:
                track_start_y = self.background.track_start_y
                track_end_y = self.background.track_end_y
                # Use view_bottom which tracks vertical scroll progress
                current_progress = self.background.view_bottom
                progress = (current_progress - track_start_y) / (track_end_y - track_start_y)
                progress = max(0.0, min(1.0, progress))  # Clamp between 0.0 and 1.0
                
                # Draw progress bar in left circular area of dashboard
                bar_x = 70  # Left side of dashboard
                bar_y = 15  # Middle area of dashboard
                bar_width = 80
                bar_height = 20
                
                # Draw percentage text just above the progress bar
                percentage = int(progress * 100)
                arcade.draw_text(
                    f"{percentage}%",
                    bar_x,
                    bar_y + 25,  # Just above the bar
                    arcade.color.WHITE,
                    14,
                    anchor_x="center",
                    font_name=self.font_name,
                )
                
                # Background bar (dark gray) - centered at bar_x, bar_y
                arcade.draw_rectangle_filled(
                    bar_x, bar_y,
                    bar_width, bar_height,
                    arcade.color.DARK_GRAY
                )
                
                # Foreground bar (white, scaled by progress)
                if progress > 0:
                    # Calculate left edge of filled portion
                    filled_width = bar_width * progress
                    filled_x = bar_x - bar_width // 2 + filled_width // 2
                    arcade.draw_rectangle_filled(
                        filled_x, bar_y,
                        filled_width, bar_height,
                        arcade.color.WHITE
                    )
            
            # Draw position tracker (placeholder)
            arcade.draw_text(
                "Position: 1",
                self.width - 20,  # Top-right area
                15,  # Just above dashboard
                arcade.color.WHITE,
                15,
                anchor_x="right",
                font_name=self.font_name,
            )
            
            # Draw Lives HUD on right side of dashboard
            if self.car and self.heart_texture:
                lives_x = self.width - 120  # Right side of dashboard area
                lives_y = 45  # Aligned with dashboard HUD
                
                # Draw "Lives: " label
                arcade.draw_text(
                    "Lives:",
                    lives_x,
                    lives_y,
                    arcade.color.WHITE,
                    10,
                    anchor_x="left",
                    font_name=self.font_name,
                )
                
                # If out of lives, draw skull icon instead of hearts
                if self.car.lives <= 0 and self.skull_texture:
                    skull_x = lives_x + 50  # Start after "Lives: " text
                    skull_size = 25
                    arcade.draw_texture_rectangle(
                        skull_x,
                        lives_y + 3,
                        skull_size,
                        skull_size,
                        self.skull_texture
                    )
                else:
                    # Draw heart icons (25x25 each, 30px spacing)
                    heart_size = 20
                    heart_spacing = 20
                    start_x = lives_x + 50  # Start after "Lives: " text
                    
                    for i in range(self.car.lives):
                        heart_x = start_x + (i * heart_spacing)
                        arcade.draw_texture_rectangle(
                            heart_x,
                            lives_y + 3,
                            heart_size,
                            heart_size,
                            self.heart_texture
                        )

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
        
        # Update smoothed display speed for HUD
        if self.car:
            actual_speed = self.car.speed
            # Smooth the display speed: display_speed += (actual_speed - display_speed) * 0.1
            self.display_speed += (actual_speed - self.display_speed) * 0.1

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

