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
        # Light overlay texture (loaded in setup)
        self.light_texture = None
        
        # Level timer tracking
        self.level_time = 0.0
        self.level_finished = False
        # Track cumulative speed for average calculation (speed * time)
        self.cumulative_speed_time = 0.0
        
        # Button press state for visual feedback
        self.level1_pressed = False
        self.level2_pressed = False
        self.level3_pressed = False
        self.level4_pressed = False
        self.level5_pressed = False
        # Button transition delay timer
        self.button_transition_timer = 0.0
        self.pending_level_index = None

        # Sound playback flags to prevent repeated sounds
        self.crash_sound_played = False
        self.life_lost_sound_played = False
        self.win_sound_played = False
        self.loss_sound_played = False

        # Track previous hit_wall state to detect wall collision events
        self.previous_hit_wall = False
        
        # Engine sound system
        self.engine_start = arcade.load_sound("assets/sounds/player/start_engine.wav")
        self.engine_low = arcade.load_sound("assets/sounds/player/low_speed.wav")
        self.engine_mid = arcade.load_sound("assets/sounds/player/mid_speed.wav")
        self.engine_high = arcade.load_sound("assets/sounds/player/high_speed.wav")
        
        self.engine_player = None
        self.current_engine_row = None
        self.engine_started = False


    def setup(self):
        # Player - create fresh car each time
        self.car = PlayerCar(250, 400)
        
        self.win_sound = arcade.load_sound("assets/sounds/player/win.wav")
        self.loss_sound = arcade.load_sound("assets/sounds/player/loss.wav")
        self.crash_sound = arcade.load_sound("assets/sounds/player/crash.wav")
        self.button_sound = arcade.load_sound("assets/sounds/player/button.wav")
        self.life_lost_sound = arcade.load_sound("assets/sounds/player/life_lost.wav")
    
        # Reset car state to ensure it's ready
        self.car.race_won = False
        self.car.race_lost = False
        self.car.losing = False
        self.car.explosion_over = False
        self.car.exploding = False
        self.car.destroyed = False
        self.car.lives = 3
        self.car.speed = 0
        self.car.hit_wall = False
        self.car.left_pressed = False
        self.car.right_pressed = False
        self.car.up_pressed = False
        self.car.down_pressed = False
        self.car.life_just_lost = False

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
        # Load light overlay texture
        self.light_texture = arcade.load_texture("assets/sprites/obstacles/light.png")
        
        # Initialize display speed to match car's initial speed
        self.display_speed = 0.0
        
        # Reset level timer and finished state
        self.level_time = 0.0
        self.level_finished = False
        # Reset cumulative speed tracking for average calculation
        self.cumulative_speed_time = 0.0
        
        # Reset button transition timer
        self.button_transition_timer = 0.0
        self.pending_level_index = None
        
        # Reset engine state for each level
        self.engine_started = False
        self.current_engine_row = None

        # Reset sound flags for each level
        self.crash_sound_played = False
        self.life_lost_sound_played = False
        self.win_sound_played = False
        self.loss_sound_played = False
        self.previous_hit_wall = False

        if self.engine_player:
            self.engine_player.pause()
            self.engine_player = None

        level_class = constants.LEVEL_CLASSES[self.level_index]
        self.background = level_class(self.car, self.width, self.height)

    def update_engine_sound(self, delta_time):
        """Update engine sounds based on car speed"""
        if not self.car:
            return

        # Play start engine sound once when car first moves
        if self.car.speed != 0 and not self.engine_started:
            arcade.play_sound(self.engine_start, volume=0.05)
            self.engine_started = True

        # Get speed row from car (already calculated in update_animation)
        row = self.car.speed_row

        # Only switch sound if speed row changed
        if row == self.current_engine_row:
            return

        # Stop current engine sound if playing
        if self.engine_player:
            self.engine_player.pause()

        # Play appropriate engine sound based on speed row
        if row == 0:
            self.engine_player = arcade.play_sound(self.engine_low, volume=0.05, looping=True)
        elif row == 1:
            self.engine_player = arcade.play_sound(self.engine_mid, volume=0.05, looping=True)
        else:
            self.engine_player = arcade.play_sound(self.engine_high, volume=0.05, looping=True)

        self.current_engine_row = row

    def on_draw(self):
        self.clear()
        # Reset viewport to normal state at start of each frame
        arcade.set_viewport(0, self.width, 0, self.height)

        if self.state == STATE_START:
            # FIXED: Sprite is now loaded once in __init__, just draw it here
            self.start_screen_sprite.draw()
            
            # Draw level selection buttons
            # Level 1 button - use pressed color if clicked
            level1_button_x = self.width // 2 - 80
            level1_button_y = self.height // 2 - 100
            level1_button_width = 120
            level1_button_height = 50
            # Change button color based on press state
            level1_color = arcade.color.DARK_GRAY if self.level1_pressed else arcade.color.GRAY
            arcade.draw_rectangle_filled(
                level1_button_x,
                level1_button_y,
                level1_button_width,
                level1_button_height,
                level1_color
            )
            arcade.draw_rectangle_outline(
                level1_button_x,
                level1_button_y,
                level1_button_width,
                level1_button_height,
                arcade.color.WHITE,
                2
            )
            arcade.draw_text(
                "Level 1",
                level1_button_x,
                level1_button_y,
                arcade.color.WHITE,
                20,
                anchor_x="center",
                anchor_y="center",
                font_name=self.font_name,
            )
            
            # Level 2 button - use pressed color if clicked
            level2_button_x = self.width // 2 + 80
            level2_button_y = self.height // 2 - 100
            level2_button_width = 120
            level2_button_height = 50
            # Change button color based on press state
            level2_color = arcade.color.DARK_GRAY if self.level2_pressed else arcade.color.GRAY
            arcade.draw_rectangle_filled(
                level2_button_x,
                level2_button_y,
                level2_button_width,
                level2_button_height,
                level2_color
            )
            arcade.draw_rectangle_outline(
                level2_button_x,
                level2_button_y,
                level2_button_width,
                level2_button_height,
                arcade.color.WHITE,
                2
            )
            arcade.draw_text(
                "Level 2",
                level2_button_x,
                level2_button_y,
                arcade.color.WHITE,
                20,
                anchor_x="center",
                anchor_y="center",
                font_name=self.font_name,
            )

            # Level 3 button - use pressed color if clicked
            level3_button_x = self.width // 2 - 80
            level3_button_y = self.height // 2 - 180
            level3_button_width = 120
            level3_button_height = 50
            # Change button color based on press state
            level3_color = arcade.color.DARK_GRAY if self.level3_pressed else arcade.color.GRAY
            arcade.draw_rectangle_filled(
                level3_button_x,
                level3_button_y,
                level3_button_width,
                level3_button_height,
                level3_color
            )
            arcade.draw_rectangle_outline(
                level3_button_x,
                level3_button_y,
                level3_button_width,
                level3_button_height,
                arcade.color.WHITE,
                2
            )
            arcade.draw_text(
                "Level 3",
                level3_button_x,
                level3_button_y,
                arcade.color.WHITE,
                20,
                anchor_x="center",
                anchor_y="center",
                font_name=self.font_name,
            )

            # Level 4 button - use pressed color if clicked
            level4_button_x = self.width // 2 + 80
            level4_button_y = self.height // 2 - 180
            level4_button_width = 120
            level4_button_height = 50
            # Change button color based on press state
            level4_color = arcade.color.DARK_GRAY if self.level4_pressed else arcade.color.GRAY
            arcade.draw_rectangle_filled(
                level4_button_x,
                level4_button_y,
                level4_button_width,
                level4_button_height,
                level4_color
            )
            arcade.draw_rectangle_outline(
                level4_button_x,
                level4_button_y,
                level4_button_width,
                level4_button_height,
                arcade.color.WHITE,
                2
            )
            arcade.draw_text(
                "Level 4",
                level4_button_x,
                level4_button_y,
                arcade.color.WHITE,
                20,
                anchor_x="center",
                anchor_y="center",
                font_name=self.font_name,
            )

            # Level 5 button (center bottom)
            level5_button_x = self.width // 2 - 80
            level5_button_y = self.height // 2 - 260
            level5_button_width = 120
            level5_button_height = 50
            # Change button color based on press state
            level5_color = arcade.color.DARK_GRAY if self.level5_pressed else arcade.color.GRAY
            arcade.draw_rectangle_filled(
                level5_button_x,
                level5_button_y,
                level5_button_width,
                level5_button_height,
                level5_color
            )
            arcade.draw_rectangle_outline(
                level5_button_x,
                level5_button_y,
                level5_button_width,
                level5_button_height,
                arcade.color.WHITE,
                2
            )
            arcade.draw_text(
                "Level 5",
                level5_button_x,
                level5_button_y,
                arcade.color.WHITE,
                20,
                anchor_x="center",
                anchor_y="center",
                font_name=self.font_name,
            )

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
            
            # Draw light overlay if player is in light area (for Level 2)
            if self.background.in_light and self.light_texture:
                arcade.draw_texture_rectangle(
                    self.width // 2,
                    self.height // 2,
                    self.width,
                    self.height,
                    self.light_texture
                )
            
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
                bar_x = 60  # Left side of dashboard
                bar_y = 15  # Middle area of dashboard
                bar_width = 60
                bar_height = 10
                
                # Draw percentage text just above the progress bar
                percentage = int(progress * 100)
                arcade.draw_text(
                    f"{percentage}%",
                    bar_x + 50,
                    bar_y- 5,  # Just above the bar
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
            
            # Draw time on dashboard (near bottom center)
            minutes = int(self.level_time // 60)
            seconds = int(self.level_time % 60)
            time_text = f"Time: {minutes:02d}:{seconds:02d}"
            arcade.draw_text(
                time_text,
                30,
                40,
                arcade.color.WHITE,
                14,
                font_name=self.font_name,
            )

        elif self.state == STATE_WIN:
            # Draw big "W" for win
            arcade.draw_text(
                "W",
                self.width // 2,
                self.height // 2 + 120,
                arcade.color.GREEN,
                160,
                anchor_x="center",
                font_name=self.font_name,
            )
            
            # Draw time taken
            minutes = int(self.level_time // 60)
            seconds = int(self.level_time % 60)
            arcade.draw_text(
                f"Time Taken: {minutes:02d}:{seconds:02d}",
                self.width // 2,
                self.height // 2 + 20,
                arcade.color.WHITE,
                28,
                anchor_x="center",
                font_name=self.font_name,
            )
            
            # Draw average speed (calculate from cumulative speed over time)
            if self.level_time > 0:
                average_speed = (self.cumulative_speed_time / self.level_time) * 30
            else:
                average_speed = 0
            arcade.draw_text(
                f"Average Speed: {int(average_speed)} Km/hr",
                self.width // 2,
                self.height // 2 - 20,
                arcade.color.WHITE,
                28,
                anchor_x="center",
                font_name=self.font_name,
            )
            
            # Draw next level instruction
            arcade.draw_text(
                "Press N for Next Level",
                self.width // 2,
                self.height // 2 - 80,
                arcade.color.WHITE,
                20,
                anchor_x="center",
                font_name=self.font_name,
            )

        elif self.state == STATE_LOSE:
            # Draw big "L" for lose
            arcade.draw_text(
                "L",
                self.width // 2,
                self.height // 2 + 120,
                arcade.color.RED,
                160,
                anchor_x="center",
                font_name=self.font_name,
            )
            
            # Draw crash message
            arcade.draw_text(
                "You Crashed!",
                self.width // 2,
                self.height // 2 + 20,
                arcade.color.WHITE,
                28,
                anchor_x="center",
                font_name=self.font_name,
            )
            
            # Draw retry instruction
            arcade.draw_text(
                "Press R to Retry",
                self.width // 2,
                self.height // 2 - 60,
                arcade.color.WHITE,
                20,
                anchor_x="center",
                font_name=self.font_name,
            )


    def on_update(self, delta_time):
        # Handle button transition delay
        if self.state == STATE_START and self.button_transition_timer > 0:
            self.button_transition_timer -= delta_time
            if self.button_transition_timer <= 0 and self.pending_level_index is not None:
                # Timer finished, now transition to the level
                self.level_index = self.pending_level_index
                self.state = STATE_PLAYING
                self.setup()
                # Reset button states
                self.level1_pressed = False
                self.level2_pressed = False
                self.level3_pressed = False
                self.level4_pressed = False
                self.level5_pressed = False
                self.pending_level_index = None
                return  # Skip other updates during transition
        
        self.background.update(delta_time)
        self.player_list.update()
        
        # Update smoothed display speed for HUD
        if self.car:
            actual_speed = self.car.speed
            # Smooth the display speed: display_speed += (actual_speed - display_speed) * 0.1
            self.display_speed += (actual_speed - self.display_speed) * 0.1
        
        # Update level timer if playing and level not finished
        if self.state == STATE_PLAYING and not self.level_finished:
            self.level_time += delta_time
            # Track cumulative speed for average calculation
            if self.car:
                self.cumulative_speed_time += self.car.speed * delta_time
            # Update engine sounds during gameplay
            self.update_engine_sound(delta_time)

        # Check for wall collision sound (only once per collision)
        if self.car.hit_wall and not self.previous_hit_wall and not self.crash_sound_played:
            arcade.play_sound(self.crash_sound, volume=0.7)
            self.crash_sound_played = True
        elif not self.car.hit_wall:
            self.crash_sound_played = False  # Reset flag when not hitting wall

        # Update previous hit_wall state
        self.previous_hit_wall = self.car.hit_wall

        # Check for life lost sound (only once per life loss)
        if self.car.life_just_lost and not self.life_lost_sound_played:
            arcade.play_sound(self.life_lost_sound, volume=0.75)
            self.life_lost_sound_played = True
            self.car.life_just_lost = False  # Reset the flag

        # Reset life lost sound flag when not losing life
        if not self.car.life_just_lost:
            self.life_lost_sound_played = False

        # Check win/lose conditions
        if self.car.race_won and not self.level_finished:
            self.level_finished = True
            self.state = STATE_WIN
            # Play win sound once
            if not self.win_sound_played:
                arcade.play_sound(self.win_sound, volume=0.8)
                self.win_sound_played = True
            # Stop engine sound on win
            if self.engine_player:
                self.engine_player.pause()
                self.engine_player = None
                self.current_engine_row = None
        
        if self.car.explosion_over and not self.level_finished:
            self.level_finished = True
            self.state = STATE_LOSE
            # Play loss sound once
            if not self.loss_sound_played:
                arcade.play_sound(self.loss_sound, volume=0.8)
                self.loss_sound_played = True
            # Stop engine sound on lose
            if self.engine_player:
                self.engine_player.pause()
                self.engine_player = None
                self.current_engine_row = None

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse clicks for level selection"""
        if self.state == STATE_START and button == arcade.MOUSE_BUTTON_LEFT:
            # Reset button press states
            self.level1_pressed = False
            self.level2_pressed = False
            self.level3_pressed = False
            self.level4_pressed = False
            self.level5_pressed = False
            
            # Level 1 button (left side)
            level1_button_x = self.width // 2 - 80
            level1_button_y = self.height // 2 - 100
            level1_button_width = 120
            level1_button_height = 50
            
            if (level1_button_x - level1_button_width // 2 <= x <= level1_button_x + level1_button_width // 2 and
                level1_button_y - level1_button_height // 2 <= y <= level1_button_y + level1_button_height // 2):
                # If Level 1 clicked - show visual feedback first
                self.level1_pressed = True
                arcade.play_sound(self.button_sound, volume=0.35)
                self.pending_level_index = 0
                self.button_transition_timer = 0.15  # 0.15 second delay to show feedback
                return
            
            # Level 2 button (right side)
            level2_button_x = self.width // 2 + 80
            level2_button_y = self.height // 2 - 100
            level2_button_width = 120
            level2_button_height = 50
            
            if (level2_button_x - level2_button_width // 2 <= x <= level2_button_x + level2_button_width // 2 and
                level2_button_y - level2_button_height // 2 <= y <= level2_button_y + level2_button_height // 2):
                # If Level 2 clicked - show visual feedback first
                self.level2_pressed = True
                arcade.play_sound(self.button_sound, volume=0.35)
                self.pending_level_index = 1
                self.button_transition_timer = 0.15  # 0.15 second delay to show feedback
                return
            
            # Level 3 button (center bottom)
            level3_button_x = self.width // 2 - 80
            level3_button_y = self.height // 2 - 160
            level3_button_width = 120
            level3_button_height = 50
            
            if (level3_button_x - level3_button_width // 2 <= x <= level3_button_x + level3_button_width // 2 and
                level3_button_y - level3_button_height // 2 <= y <= level3_button_y + level3_button_height // 2):
                # If Level 3 clicked - show visual feedback first
                self.level3_pressed = True
                arcade.play_sound(self.button_sound, volume=0.35)
                self.pending_level_index = 2
                self.button_transition_timer = 0.15  # 0.15 second delay to show feedback
                return

            # Level 4 button (right bottom)
            level4_button_x = self.width // 2 + 80
            level4_button_y = self.height // 2 - 180
            level4_button_width = 120
            level4_button_height = 50
            
            if (level4_button_x - level4_button_width // 2 <= x <= level4_button_x + level4_button_width // 2 and
                level4_button_y - level4_button_height // 2 <= y <= level4_button_y + level4_button_height // 2):
                # If Level 4 clicked - show visual feedback first
                self.level4_pressed = True
                arcade.play_sound(self.button_sound, volume=0.35)
                self.pending_level_index = 3
                self.button_transition_timer = 0.15  # 0.15 second delay to show feedback
                return

            # Level 5 button (center bottom row 3)
            # Must match drawing position: self.width // 2 - 80 (user customized)
            level5_button_x = self.width // 2 - 80
            level5_button_y = self.height // 2 - 260
            level5_button_width = 120
            level5_button_height = 50
            
            if (level5_button_x - level5_button_width // 2 <= x <= level5_button_x + level5_button_width // 2 and
                level5_button_y - level5_button_height // 2 <= y <= level5_button_y + level5_button_height // 2):
                # If Level 5 clicked - show visual feedback first
                self.level5_pressed = True
                arcade.play_sound(self.button_sound, volume=0.35)
                self.pending_level_index = 4
                self.button_transition_timer = 0.15  # 0.15 second delay to show feedback
                return

    def on_mouse_release(self, x, y, button, modifiers):
        """Reset button press states when mouse is released"""
        self.level1_pressed = False
        self.level2_pressed = False
        self.level3_pressed = False
        self.level4_pressed = False
        self.level5_pressed = False

    def on_key_press(self, key, modifiers):

        if self.state == STATE_START:
            # Default to Level 1 if any key is pressed (for backward compatibility)
            self.level_index = 0
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
        if self.state == STATE_PLAYING and self.car and not self.car.losing:
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
        if not self.car or self.car.losing:
            return

        if key == arcade.key.LEFT:
            self.car.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.car.right_pressed = False
        elif key == arcade.key.UP:
            self.car.up_pressed = False
        elif key == arcade.key.DOWN:
            self.car.down_pressed = False

