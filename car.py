import arcade
from constants import SCREEN_HEIGHT, SCREEN_WIDTH

class PlayerCar(arcade.Sprite):
    def __init__(self, x, y):
        # Initialize with the default sprite
        super().__init__("assets/sprites/player/player_car.png", scale=2.0)

        # Initialize position
        self.center_x = x
        self.center_y = y


        sheet_path = "assets/sprites/player/player_animations.png"

        FRAME_WIDTH = 44
        FRAME_HEIGHT = 80

        # Load sprite sheet: 4 rows x 4 cols = 16 frames total
        textures = arcade.load_spritesheet(
            sheet_path,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            4,
            16
        )

        # Organize frames into 2D array [row][col] for easy access
        self.frames = []
        index = 0
        for row in range(4):
            row_frames = []
            for col in range(4):
                row_frames.append(textures[index])
                index += 1
            self.frames.append(row_frames)


        # Car physics properties
        self.speed = 0
        self.max_speed = 8
        self.accel = 0.05
        self.brake_power = 0.3
        self.coast = 0.03
        self.turn_speed = 2.5  # Fixed turning speed for responsive control
        self.lives = 3
        self.hit_wall = False
        self.race_lost = False
        self.race_won = False
        self.losing = False  # During explosion countdown
        self.lose_timer = 0

        # Input tracking properties
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Scale the car to make it more visible
        self.scale = 3.0  # Increase the scale to make the car larger

        # Animation properties
        self.current_frame = self.frames[0][0]  # Default to normal straight frame (row 0, col 0 - straight)
        self.texture = self.current_frame  # Set initial texture
        self.exploding = False
        self.explosion_index = 0
        self.explosion_counter = 0
        self.explosion_frame_duration = 10  # Update explosion frame every 10 updates
        self.explosion_over = False
        # Calculate total explosion animation duration (4 frames * 10 updates per frame)
        self.explosion_total_duration = 5 * self.explosion_frame_duration
        self.animation_counter = 0
        self.animation_frame_duration = 8  # Change frame every 8 updates for animation

        # Additional properties for wall collision handling
        self.wall_slowdown_timer = 0  # Timer to maintain slow speed after wall hit
        self.acceleration = 0.2
        # Initialize the destroyed attribute that was referenced but not defined
        self.destroyed = False
        # Speed row for sound system (0=low, 1=mid, 2=high)
        self.speed_row = 0

        # Flag to track when a life was just lost (for sound system)
        self.life_just_lost = False

    def current_speed(self):
        """Returns current speed as an integer 0-8 for dashboard indexing"""
        return max(0, min(8, int(round(self.speed))))

    def update(self, delta_time=1/60):
        # Check if player has lost all lives and trigger losing state
        if self.lives <= 0 and not self.losing and not self.explosion_over:
            self.losing = True
            self.exploding = True
            self.race_lost = True
            self.lose_timer = self.explosion_total_duration
            self.speed = 0
            # Clear all input flags to freeze movement
            self.left_pressed = False
            self.right_pressed = False
            self.up_pressed = False
            self.down_pressed = False

        # Handle countdown timer during losing state
        if self.losing:
            self.lose_timer -= 1
            if self.lose_timer <= 0:
                self.explosion_over = True
                self.losing = False

        # Handle input-based movement (only if not losing)
        if self.losing:
            # Freeze movement during losing state
            self.speed = 0
            self.change_x = 0
            self.change_y = 0
        else:
            # Handle input-based movement
            if self.up_pressed:
                self.speed += self.accel
            elif self.down_pressed:
                self.speed -= self.brake_power
            else:
                # Coasting when no input
                if self.speed > 0:
                    self.speed = max(0, self.speed - self.coast)
                elif self.speed < 0:
                    self.speed = min(0, self.speed + self.coast)

            # Clamp speed to max
            self.speed = max(-self.max_speed, min(self.speed, self.max_speed))

            # Prevent reverse movement
            if self.speed < 0:
                self.speed = 0

            # Calculate movement based on direction input (only horizontal movement)
            # Use fixed turn_speed for responsive, controlled turning
            self.change_x = 0
            if self.left_pressed:
                self.change_x = -self.turn_speed  # Move left at fixed turning speed
            elif self.right_pressed:
                self.change_x = self.turn_speed   # Move right at fixed turning speed

            # The car should NOT move vertically - only horizontal movement
            # The vertical movement is handled by the scrolling background
            self.change_y = 0

            # Only allow horizontal movement; car never moves vertically
            self.center_x += self.change_x
            # self.center_y += self.change_y  # Disabled - car stays fixed vertically

        # Wall collision: constrain to track boundaries and apply slowdown penalty
        if self.center_x < 70:
            self.center_x = 70
            self.hit_wall = True
            self.speed = 2
            self.wall_slowdown_timer = 20
        elif self.center_x > 430:
            self.center_x = 430
            self.hit_wall = True
            self.speed = 2
            self.wall_slowdown_timer = 20
        else:
            self.hit_wall = False
            # Gradually restore normal speed after wall hit
            if self.wall_slowdown_timer > 0:
                self.wall_slowdown_timer -= 1
                if self.wall_slowdown_timer <= 0:
                    self.speed = min(self.speed, self.max_speed)

        # Update animation
        self.update_animation()

        # Apply movement (horizontal only - vertical handled by background scrolling)
        super().update()

    def update_animation(self):
        if self.exploding:
            # Explosion animation: row 3, sequential frames
            self.explosion_counter += 1
            if self.explosion_counter >= self.explosion_frame_duration:
                self.explosion_counter = 0
                self.explosion_index += 1

                if self.explosion_index > 3:
                    self.destroyed = True
                    self.explosion_index = 3  # Hold on last frame
                else:
                    self.current_frame = self.frames[3][self.explosion_index]
        else:
            # Select row based on speed (0=normal, 1=medium flames, 2=extra flames)
            if abs(self.speed) < 3:
                row = 0
            elif abs(self.speed) < 7:
                row = 1
            else:
                row = 2

            # Store speed row so sound system can use it
            self.speed_row = row

            # Select column based on direction/action
            if self.left_pressed:
                col = 1 if row == 0 else 2
            elif self.right_pressed:
                col = 2 if row == 0 else 3
            else:
                if self.down_pressed:
                    col = 3  # Braking
                else:
                    if row == 0:
                        col = 0  # Straight
                    else:
                        # Animate straight movement for rows 1 & 2
                        self.animation_counter += 1
                        if self.animation_counter >= self.animation_frame_duration:
                            self.animation_counter = 0

                        # Toggle between frames 0 and 1
                        if (self.animation_counter // (self.animation_frame_duration // 2)) % 2 == 0:
                            col = 0
                        else:
                            col = 1

            self.current_frame = self.frames[row][col]

        self.texture = self.current_frame

    def explode(self):
        """Trigger explosion animation and losing state"""
        if not self.exploding:
            self.exploding = True
            self.explosion_index = 0
            self.explosion_counter = 0
            self.current_frame = self.frames[3][0]
            if not self.losing:
                self.losing = True
                self.lose_timer = self.explosion_total_duration