import arcade
import random
from constants import BOT_DIFFICULTY

class BotCar(arcade.Sprite):
    def __init__(self, x, y, level_difficulty=1, car_target=None):
        super().__init__()
        
        # Difficulty settings
        # retrieves stats based on level, defaulting to level 1 if invalid
        self.stats = BOT_DIFFICULTY.get(level_difficulty, BOT_DIFFICULTY[1])
        
        # Target to follow (usually the player)
        self.target = car_target
        
        # Environmental awareness (lists of sprites)
        self.obstacles = []     # Deadly obstacles (walls, objects)
        self.puddles = []       # Slowdown zones
        self.ramps = []         # Speed boost zones
        self.drones = []        # Moving obstacles (if any)
        
        # Position
        self.center_x = x
        self.center_y = y
        self.scale = 3.0
        
        # Physics
        self.base_speed = self.stats["max_speed"]
        self.current_speed = self.base_speed
        self.lanes = [115, 205, 295, 385]
        self.target_lane_x = x
        self.is_changing_lane = False
        
        # AI State
        self.active = False     # Bot starts inactive until player moves
        self.reaction_timer = 0.0
        self.stuck_timer = 0.0  # Tracks how long bot is stuck behind an object/player
        self.slowing_down = False
        
        # Animation setup
        sheet_path = "assets/sprites/bots/bot_animations.png"
        FRAME_WIDTH = 44
        FRAME_HEIGHT = 80
        textures = arcade.load_spritesheet(sheet_path, FRAME_WIDTH, FRAME_HEIGHT, 4, 16)
        
        self.frames = []
        index = 0
        for row in range(4):
            row_frames = []
            for col in range(4):
                row_frames.append(textures[index])
                index += 1
            self.frames.append(row_frames)
            
        self.current_frame = self.frames[0][0]
        self.texture = self.current_frame
        self.animation_counter = 0
        self.animation_frame_duration = 8 # Update speed for animations
        self.speed_row = 1
        self.lean_state = 0
        
        # Status flags
        self.exploding = False
        self.explosion_index = 0
        self.explosion_counter = 0
        self.explosion_frame_duration = 10
        self.destroyed = False
        self.collision_damaged = False
        self.race_finished = False
        self.hit_wall = False
        
        # Timers
        self.spawn_time = 0.0
        self.wall_contact_timer = 0.0
        self.collision_cooldown = 0.0 # Timer to prevent constant collision speed penalties

    def set_context(self, obstacles=None, puddles=None, ramps=None, drones=None):
        """Pass various sprite lists for the bot to be aware of."""
        if obstacles:
            self.obstacles = obstacles if isinstance(obstacles, list) else [obstacles]
        if puddles:
            self.puddles = puddles if isinstance(puddles, list) else [puddles]
        if ramps:
            self.ramps = ramps if isinstance(ramps, list) else [ramps]
        if drones:
            self.drones = drones if isinstance(drones, list) else [drones]

    def update(self, delta_time=1/60):
        if self.destroyed:
            return

        # Activation Logic: Strict wait for start
        # Bot remains completely frozen until player starts moving
        if not self.active:
            if self.target and self.target.speed > 0:
                self.active = True
                self.spawn_time = 0.0
                self.wall_contact_timer = 0.0
                self.collision_cooldown = 0.0
            else:
                return

        self.spawn_time += delta_time
        if self.collision_cooldown > 0:
            self.collision_cooldown -= delta_time

        if self.exploding:
            self._update_explosion()
            return

        # AI Decision Making
        self.reaction_timer -= delta_time
        if self.reaction_timer <= 0:
            self._make_decision()
            # Randomize next decision time slightly
            self.reaction_timer = self.stats["reaction_time"] * random.uniform(0.8, 1.2)
        
        # Reset stuck timer if moving efficiently
        if self.target:
            x_diff = abs(self.center_x - self.target.center_x)
            y_diff = self.target.center_y - self.center_y
            # If stuck behind player or just stuck in general
            if x_diff < 50 and 0 < y_diff < 300:
                self.stuck_timer += delta_time
            else:
                self.stuck_timer = 0.0
            
        # Lateral Movement Physics
        dist_x = self.target_lane_x - self.center_x
        move_speed = 3.0
        
        # Buffer Zone Enforcement (Continuous)
        # Even during lane change, if we get too close to player, steer away
        if self.target:
            lateral_dist = self.center_x - self.target.center_x
            # Check for 70px buffer zone
            if abs(lateral_dist) < 70 and abs(self.center_y - self.target.center_y) < 100:
                # Too close! Nudge away
                if lateral_dist > 0:
                    self.center_x += 1 # Push right
                    if self.target_lane_x < self.center_x + 20: 
                        self.target_lane_x = min(430, self.center_x + 50)
                else:
                    self.center_x -= 1 # Push left
                    if self.target_lane_x > self.center_x - 20:
                        self.target_lane_x = max(70, self.center_x - 50)

        if abs(dist_x) > 2:
            if dist_x > 0:
                self.center_x += move_speed
                self._update_lean(right=True)
            else:
                self.center_x -= move_speed
                self._update_lean(left=True)
        else:
            self._update_lean(straight=True)
            self.is_changing_lane = False

        # Wall boundaries
        if self.center_x < 70:
            self.center_x = 70
            self.hit_wall = True
        elif self.center_x > 430:
            self.center_x = 430
            self.hit_wall = True
        else:
            self.hit_wall = False
        
        # Wall contact timer (only count if NOT in grace period)
        if self.hit_wall and self.spawn_time >= 10.0:
            self.wall_contact_timer += delta_time
            if self.wall_contact_timer >= 5.0:
                self.explode(force=True)
        else:
            self.wall_contact_timer = 0.0

        # Vertical Movement
        current_max_speed = self.base_speed
        
        # Simple interaction checks
        all_ramps = []
        for r_list in self.ramps:
            if isinstance(r_list, arcade.SpriteList):
                all_ramps.extend(r_list)
            else:
                all_ramps.append(r_list)
                
        all_puddles = []
        for p_list in self.puddles:
            if isinstance(p_list, arcade.SpriteList):
                all_puddles.extend(p_list)
            else:
                all_puddles.append(p_list)
        
        
        # Correct approach for lists
        hit_ramp = False
        for ramp in all_ramps:
            if arcade.check_for_collision(self, ramp):
                hit_ramp = True
                break
        
        hit_puddle = False
        for puddle in all_puddles:
            if arcade.check_for_collision(self, puddle):
                hit_puddle = True
                break
                
        if hit_ramp:
            current_max_speed += 2.0  # Boost
        if hit_puddle:
            current_max_speed *= 0.6  # Slow down
        if self.slowing_down:
            current_max_speed *= 0.5  # Brake for obstacles

        # Apply current speed (with smoothing)
        if self.current_speed < current_max_speed:
            self.current_speed += 0.1
        elif self.current_speed > current_max_speed:
            self.current_speed -= 0.1
            
            # Move vertically relative to player (simulated)
        if self.target:
            y_diff = self.target.center_y - self.center_y
            
            # Chase logic relative to scrolling
            # The game scrolls at player speed. If we are faster, we move up. Slower, down.
            # But the logic here is center_y based.
            
            # We want to move at (our_speed - player_speed) relative to screen?
            # No, 'center_y' is world coordinate. Logic:
            # self.center_y += self.current_speed (but converted to pixels)
            # The level.update scrolls everything down by player.speed.
            # So here we just move up by *our* speed.
            
            speed_pixel_per_frame = self.current_speed * delta_time * 60 # Scale factor
            self.center_y += speed_pixel_per_frame

        self._check_collisions()
        self._update_animation()

    def _make_decision(self):
        if not self.target:
            return

        awareness = self.stats.get("awareness_distance", 200)
        
        # Gather all hazards
        hazards = []
        for obj in self.obstacles:
            if isinstance(obj, arcade.SpriteList):
                hazards.extend(obj)
            else:
                hazards.append(obj)
        for obj in self.drones:
            if isinstance(obj, arcade.SpriteList):
                hazards.extend(obj)
            else:
                hazards.append(obj)
        for obj in self.puddles:
            if isinstance(obj, arcade.SpriteList):
                hazards.extend(obj)
            else:
                hazards.append(obj)
                
        # Player is a soft hazard (buffer zone)
        # We handle player separately for "Avoidance" vs "Panic"

        imminent_crash = False
        nearest_dist = float('inf')

        # Detect hazards ahead
        for obs in hazards:
            if obs.center_y > self.center_y and obs.center_y < self.center_y + awareness:
                # Check lane overlap
                if abs(obs.center_x - self.center_x) < 50:
                    dist = obs.center_y - self.center_y
                    if dist < nearest_dist:
                        nearest_dist = dist
                        imminent_crash = True
        
        # Check player buffer separately
        player_too_close = False
        if self.target:
             if self.center_y < self.target.center_y + 100 and self.center_y > self.target.center_y - 100:
                 if abs(self.center_x - self.target.center_x) < 80:
                     player_too_close = True

        self.slowing_down = False
        
        if imminent_crash or player_too_close:
            avoidance_strength = self.stats.get("avoidance_strength", 0.5)
            panic_chance = self.stats.get("panic_chance", 0.1)
            
            # Decide: Avoid or Panic
            if random.random() < avoidance_strength or player_too_close: # Always try to avoid player
                # Smart Avoidance: Find safest lane
                current_lane = min(self.lanes, key=lambda l: abs(l - self.center_x))
                other_lanes = [l for l in self.lanes if l != current_lane]
                safe_lanes = []
                
                for lane in other_lanes:
                    is_safe = True
                    for obs in hazards:
                         if obs.center_y > self.center_y and obs.center_y < self.center_y + awareness:
                             if abs(obs.center_x - lane) < 50:
                                 is_safe = False
                                 break
                    # Also check player buffer for this lane
                    if self.target and abs(lane - self.target.center_x) < 80 and abs(self.center_y - self.target.center_y) < 200:
                        is_safe = False
                        
                    if is_safe:
                        safe_lanes.append(lane)
                
                if safe_lanes:
                    self.target_lane_x = random.choice(safe_lanes)
                    self.is_changing_lane = True
                else:
                    # No safe lane? Slow down!
                    self.slowing_down = True
            elif random.random() < panic_chance:
                # Panic: Random move
                self.target_lane_x = random.choice(self.lanes)
                self.is_changing_lane = True
        else:
            # No imminent crash, normal behavior
            target_x = self.target.center_x
            
            # Use follow_accuracy to determine if we track player lane or drift
            if random.random() > self.stats["follow_accuracy"]:
                offset = random.choice([-60, 60])
                target_x += offset
            
            # Logic: If behind player, try to overtake? Or execute lane changes for variety?
            if self.stuck_timer > 2.0:
                if random.random() < self.stats["lane_change_chance"]:
                    self.target_lane_x = random.choice(self.lanes)
                    self.is_changing_lane = True
                    self.stuck_timer = 0.0
                else:
                    self.target_lane_x = target_x
            elif not self.is_changing_lane:
                self.target_lane_x = target_x
                
        self.target_lane_x = max(70, min(430, self.target_lane_x))

    def _update_lean(self, left=False, right=False, straight=False):
        self.lean_state = 0
        if left:
            self.lean_state = 1
        if right:
            self.lean_state = 2

    def _update_animation(self):
        speed_abs = abs(self.current_speed if hasattr(self, 'current_speed') else self.base_speed)
        
        # Select frame row based on speed
        if speed_abs < 3:
            row = 0
        elif speed_abs < 7:
            row = 1
        else:
            row = 2
        
        self.speed_row = row
        
        if self.lean_state == 1:
            col = 1 if row == 0 else 2
        elif self.lean_state == 2:
            col = 2 if row == 0 else 3
        else:
            if row == 0:
                col = 0
            else:
                self.animation_counter += 1
                if self.animation_counter >= self.animation_frame_duration:
                    self.animation_counter = 0
                
                if (self.animation_counter // (self.animation_frame_duration // 2)) % 2 == 0:
                    col = 0
                else:
                    col = 1
                
        self.current_frame = self.frames[row][col]
        self.texture = self.current_frame

    def _check_collisions(self):
        if not self.target:
            return
        
        # "rubbing is racing" - Check player collision
        if arcade.check_for_collision(self, self.target):
            # Only apply penalty if cooldown is ready
            if self.collision_cooldown <= 0:
                # Penalty for hitting another car: Slow down
                self.current_speed *= 0.8
                # Also slow down player slightly if possible to simulate contact friction
                if hasattr(self.target, 'speed'):
                    self.target.speed *= 0.9 # Small drag
                
                # Set cooldown to prevent instant grinding halt
                self.collision_cooldown = 1.0
            
            # Push apart slightly logic handled in lateral movement (Buffer Zone Enforcement)
            
    def explode(self, force=False, damage_player=False):
        if self.exploding:
            return
            
        # Check grace period (unless forced)
        if not force and self.spawn_time < 10.0:
            return
            
        self.exploding = True
        self.active = False # Stop AI decisions
        
        # Note: We no longer damage player on regular bot death.
        # Only if specific logic demanded it, but user requested collision-based speed adjustment instead.
        # So this parameter is largely unused now, but kept for compatibility.
        if damage_player and not self.collision_damaged and self.target and self.spawn_time >= 10.0:
            # Optional: Could still hurt player on massive T-Bone, but for now strict compliance to "Speed Adjustment"
            pass
              
    def _update_explosion(self):
        self.explosion_counter += 1
        if self.explosion_counter >= self.explosion_frame_duration:
            self.explosion_counter = 0
            self.explosion_index += 1
            
            if self.explosion_index > 3:
                self.explosion_index = 3
                self.current_frame = self.frames[3][3]
                self.texture = self.current_frame
            else:
                self.current_frame = self.frames[3][self.explosion_index]
                self.texture = self.current_frame
