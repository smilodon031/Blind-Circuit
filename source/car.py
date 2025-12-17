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

        # Load the full sprite sheet as textures
        textures = arcade.load_spritesheet(
            sheet_path,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            4,
            16
        )

        # Rebuild into frames[row][col]
        self.frames = []
        index = 0
        for row in range(4):
            row_frames = []
            for col in range(4):
                row_frames.append(textures[index])
                index += 1
            self.frames.append(row_frames)


        # Initialize car properties
        self.speed = 0
        self.max_speed = 8  # Reduced from 10 to 6
        self.accel = 0.15  # Reduced acceleration to match lower max speed
        self.brake_power = 0.3  # Reduced brake power accordingly
        self.coast = 0.03  # Reduced coast rate
        self.turn_speed = 2.5  # Fixed turning speed for responsive control
        self.lives = 3
        self.hit_wall = False  # Add hit_wall property for game integration
        self.race_lost = False
        self.race_won = False
        self.losing = False  # Flag to indicate losing state (during explosion countdown)
        self.lose_timer = 0  # Countdown timer for explosion animation duration

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

            # Car must never move in reverse — if speed < 0, force it back to 0
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

        # Keep the car within screen boundaries and check for wall collisions
        if self.center_x < 70:
            self.center_x = 70
            self.hit_wall = True
            self.speed = 2
            self.wall_slowdown_timer = 20  # Slow down for 20 frames
        elif self.center_x > 430:
            self.center_x = 430
            self.hit_wall = True
            self.speed = 2
            self.wall_slowdown_timer = 20  # Slow down for 20 frames
        else:
            self.hit_wall = False
            # Decrement slowdown timer when not hitting walls
            if self.wall_slowdown_timer > 0:
                self.wall_slowdown_timer -= 1
                # When timer expires, return to normal speed
                if self.wall_slowdown_timer <= 0:
                    self.speed = min(self.speed, self.max_speed)

        # Update animation
        self.update_animation()

        # Call parent update to handle movement, but only horizontal
        super().update()

        # Prevent vertical movement - keep the car on the fixed horizontal plane
        # Vertical position is controlled by the game engine to maintain the illusion

    def update_animation(self):
        if self.exploding:
            # Handle explosion animation
            # ROW 3 — Explosion (Sequential): col 0 → start explosion, col 1 → medium, col 2 → more, col 3 → max
            self.explosion_counter += 1
            if self.explosion_counter >= self.explosion_frame_duration:
                self.explosion_counter = 0
                self.explosion_index += 1

                if self.explosion_index > 3:  # After the last explosion frame
                    self.destroyed = True
                    self.explosion_index = 3  # Stay on the last frame
                else:
                    self.current_frame = self.frames[3][self.explosion_index]
        else:
            # Determine animation row based on speed
            if abs(self.speed) < 3:
                row = 0  # ROW 0 — Normal Driving
            elif abs(self.speed) < 5:
                row = 1  # ROW 1 — Medium Flames
            else:
                row = 2  # ROW 2 — Extra Flames

            # Determine animation column based on direction
            if self.left_pressed:  # Turning left - not dependent on change_x
                # ROW 0: left=col1, ROW 1/2: left=col2
                col = 1 if row == 0 else 2
            elif self.right_pressed:  # Turning right - not dependent on change_x
                # ROW 0: right=col2, ROW 1/2: right=col3
                col = 2 if row == 0 else 3
            else:  # Going straight or braking
                if self.down_pressed:  # Braking (down arrow pressed)
                    # ROW 0: col 3 → brake
                    col = 3
                else:  # Going straight - alternate frames for rows 1 & 2, use single frame for row 0
                    if row == 0:
                        # ROW 0 — Normal Driving: col 0 → straight
                        col = 0
                    else:  # Row 1 & 2
                        # STRAIGHT ANIMATION IN ROWS 1 AND 2 - Toggle between col 0 and col 1
                        # Simple toggle that switches every animation_frame_duration
                        self.animation_counter += 1
                        if self.animation_counter >= self.animation_frame_duration:
                            self.animation_counter = 0

                        # Switch between frame 0 and 1 every animation_frame_duration / 2
                        if (self.animation_counter // (self.animation_frame_duration // 2)) % 2 == 0:
                            col = 0  # straight frame #1
                        else:
                            col = 1  # straight frame #2

            self.current_frame = self.frames[row][col]

        self.texture = self.current_frame

    def explode(self):
        """Trigger the explosion animation"""
        if not self.exploding:
            self.exploding = True
            self.explosion_index = 0
            self.explosion_counter = 0
            self.current_frame = self.frames[3][0]
            # Also trigger losing state if not already triggered
            if not self.losing:
                self.losing = True
                self.lose_timer = self.explosion_total_duration