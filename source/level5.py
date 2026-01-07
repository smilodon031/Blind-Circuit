import arcade
import random

class FireDispenser(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Initialize position
        self.center_x = x
        self.center_y = y
        
        sheet_path = "assets/sprites/obstacles/fire_dispenser.png"
        
        FRAME_WIDTH = 64
        FRAME_HEIGHT = 64
        
        # Load sprite sheet: 1 column x 5 rows = 5 frames total
        # Note: 'columns' refers to horizontal frames, 'count' is total frames
        # The sheet is vertical (1 column, 5 rows), so columns=1
        textures = arcade.load_spritesheet(
            sheet_path,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            1, # columns
            5  # count
        )
        
        self.frames = textures
        
        # Animation properties
        self.current_frame = self.frames[0]
        self.texture = self.current_frame
        
        self.animation_counter = 0
        self.animation_frame_duration = 6 # Update frame every 6 ticks (approx 0.1s at 60fps)
        
        self.cur_texture_index = 0
        
    def update_animation(self):
        self.animation_counter += 1
        
        if self.animation_counter >= self.animation_frame_duration:
            self.animation_counter = 0
            
            # Logic: 0 -> 1 -> 2 -> 3 -> 4, then loop 3 <-> 4
            if self.cur_texture_index < 3:
                self.cur_texture_index += 1
            else:
                if self.cur_texture_index == 3:
                    self.cur_texture_index = 4
                else:
                    self.cur_texture_index = 3
            
            self.current_frame = self.frames[self.cur_texture_index]
            self.texture = self.current_frame


class Level5Background:
    def __init__(self, car, screen_width, screen_height):
        self.car = car
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Track boundaries for progress calculation (vertical/y-axis)
        # Track starts at y=0 and ends at the finish line
        # Map is 200 tiles tall, each tile is 64px, scaled by 1.57
        self.track_start_y = 0
        # Calculate track end based on map height: 200 tiles * 64px * 1.57 scaling
        self.track_end_y = 200 * 64 * 1.57  # Approximately 20,096 pixels
        
        self.puddle_timer = 10
        self.speed_ramp_timer = 5
        self.view_bottom = 0
        self.map_path = "assets/maps/level5.tmx"
        self.broken_texture = arcade.load_texture('assets/sprites/obstacles/broken_texture.png')
        
        # Camera shake for obstacle hits
        self.shake_time = 0
        # Shake for hit_wall_rect (exposed for game.py to use)
        self.hit_wall_shake_time = 0
        # Current shake offsets (exposed for game.py to use)
        self.hit_wall_shake_offset_x = 0
        self.hit_wall_shake_offset_y = 0
        
        self.in_light = False

        # Load map
        self.tile_map = arcade.load_tilemap(self.map_path, scaling=1.57)
        
        # Extract the layers
        self.road_layer = self.tile_map.sprite_lists["Road"]
        self.object1_layer = self.tile_map.sprite_lists["Object1"]
        self.finish_line_layer = self.tile_map.sprite_lists["FinishLine"]
        self.puddles_layer = self.tile_map.sprite_lists["Puddles"]
        self.speed_ramp_layer = self.tile_map.sprite_lists["SpeedRamp"]
        
        # Fire Dispenser Layer
        # Manually create sprites to use custom class logic
        self.fire_dispenser_list = arcade.SpriteList()
        if "FireDispenser" in self.tile_map.sprite_lists:
             raw_dispensers = self.tile_map.sprite_lists["FireDispenser"]
             for raw in raw_dispensers:
                 dispenser = FireDispenser(raw.center_x, raw.center_y)
                 self.fire_dispenser_list.append(dispenser)

    def update(self, delta_time):
        # Scroll background based on car speed
        if not self.car.losing:
            self.view_bottom += self.car.speed

        # Collision with obstacles: replace with broken texture
        object1_list = arcade.check_for_collision_with_list(self.car, self.object1_layer)
        for obstacle in object1_list:
            if obstacle.texture != self.broken_texture:
                obstacle.texture = self.broken_texture
                self.car.lives -= 1
                self.car.life_just_lost = True
                self.shake_time = 0.3

        # Fire Dispenser collisions (Shake only)
        if arcade.check_for_collision_with_list(self.car, self.fire_dispenser_list):
             if not self.car.losing and self.car.lives > 0:
                 self.shake_time = 0.3

        # Puddles slow down the car
        puddles_list = arcade.check_for_collision_with_list(self.car, self.puddles_layer)
        if puddles_list:
            if self.puddle_timer > 0:
                self.car.speed = 1
                self.puddle_timer -= delta_time

        # Speed ramps boost the car
        speed_ramp_list = arcade.check_for_collision_with_list(self.car, self.speed_ramp_layer)
        if speed_ramp_list:
            if self.speed_ramp_timer > 0:
                self.car.speed += 4
                self.speed_ramp_timer -= delta_time

        # Trigger shake when car hits wall
        if self.car.hit_wall and self.hit_wall_shake_time <= 0:
            self.hit_wall_shake_time = 0.3

        # Check finish line collision
        finish_line_list = arcade.check_for_collision_with_list(self.car, self.finish_line_layer)
        if finish_line_list:
            if self.car.center_y > finish_line_list[0].center_y:
                self.car.race_won = True
                self.car.speed = 0

        # Scroll all layers to create forward movement illusion
        if not self.car.losing:
            scroll_layers = [
                self.road_layer, 
                self.object1_layer, 
                self.finish_line_layer, 
                self.puddles_layer, 
                self.speed_ramp_layer, 
                self.fire_dispenser_list
            ]
            for layer in scroll_layers:
                for sprite in layer:
                    sprite.center_y -= self.car.speed

        # Update animations
        for dispenser in self.fire_dispenser_list:
             dispenser.update_animation()

        # Update camera shake timer
        if self.shake_time > 0:
            self.shake_time -= delta_time
        # Update hit wall shake timer
        if self.hit_wall_shake_time > 0:
             self.hit_wall_shake_time -= delta_time

    def draw(self):
        # Calculate shake offsets for hit_wall_rect
        self.hit_wall_shake_offset_x = 0
        self.hit_wall_shake_offset_y = 0
        if self.hit_wall_shake_time > 0:
            self.hit_wall_shake_offset_x = random.uniform(-2, 2)
            self.hit_wall_shake_offset_y = random.uniform(-2, 2)

        # Draw the road layer
        self.road_layer.draw()
        self.object1_layer.draw()
        self.finish_line_layer.draw()
        self.puddles_layer.draw()
        self.speed_ramp_layer.draw()
        self.fire_dispenser_list.draw()
