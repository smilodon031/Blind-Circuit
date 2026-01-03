import arcade
import random

class FireSprite(arcade.Sprite):
    def __init__(self, parent_sprite):
        super().__init__()
        self.parent_sprite = parent_sprite
        
        # Load the spritesheet
        self.textures = arcade.load_spritesheet(
            "assets/sprites/obstacles/fire.png",
            sprite_width=64,
            sprite_height=64,
            columns=3,
            count=3
        )
        self.texture = self.textures[0]
        self.cur_texture_index = 0
        self.time_counter = 0.0
        self.animation_speed = 0.5
        
        # Set initial position
        self.center_x = self.parent_sprite.center_x
        self.center_y = self.parent_sprite.center_y + 10  # Vertical offset to be on top

    def update(self):
        # Follow the parent sprite
        self.center_x = self.parent_sprite.center_x
        self.center_y = self.parent_sprite.center_y + 10

    def update_animation(self, delta_time: float = 1/60):
        self.time_counter += delta_time
        if self.time_counter >= self.animation_speed:
            self.time_counter = 0
            self.cur_texture_index += 1
            if self.cur_texture_index >= len(self.textures):
                self.cur_texture_index = 0
            self.texture = self.textures[self.cur_texture_index]

class Level3Background:
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
        self.map_path = "assets/maps/Level3.tmx"
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
        self.broken_car_layer = self.tile_map.sprite_lists["BrokenCar"]
        self.puddles_layer = self.tile_map.sprite_lists["Puddles"]
        self.speed_ramp_layer = self.tile_map.sprite_lists["SpeedRamp"]
        
        # Initialize fire sprites for broken cars
        self.fire_list = arcade.SpriteList()
        for car in self.broken_car_layer:
            fire_sprite = FireSprite(car)
            self.fire_list.append(fire_sprite)
        

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
                self.car.life_just_lost = True  # Flag for sound system
                # Start camera shake for obstacle hit
                self.shake_time = 0.3
        
        broken_car_list = arcade.check_for_collision_with_list(self.car, self.broken_car_layer)          
        for obstacle in broken_car_list:
            if obstacle.texture != self.broken_texture:
                obstacle.texture = self.broken_texture
                self.car.lives -= 1
                self.car.life_just_lost = True  # Flag for sound system
                # Start camera shake for obstacle hit
                self.shake_time = 0.3

        # Trigger shake when car hits wall
        if self.car.hit_wall and self.hit_wall_shake_time <= 0:
            self.hit_wall_shake_time = 0.3
            
        # Check finish line collision
        finish_line_list = arcade.check_for_collision_with_list(self.car, self.finish_line_layer)
        if finish_line_list:
            finish = finish_line_list[0]
            if self.car.center_y > finish.center_y:
                self.car.race_won = True
                self.car.speed = 0
        
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

        # Scroll all layers to create forward movement illusion
        if not self.car.losing:
            scroll_layers = [self.road_layer, self.object1_layer, self.finish_line_layer, self.puddles_layer, self.speed_ramp_layer, self.broken_car_layer]
            for layer in scroll_layers:
                for sprite in layer:
                    sprite.center_y -= self.car.speed
        
        # Update camera shake timer
        if self.shake_time > 0:
            self.shake_time -= delta_time
        # Update hit wall shake timer
        if self.hit_wall_shake_time > 0:
            self.hit_wall_shake_time -= delta_time
            
        # Update fire animations
        self.fire_list.update()
        self.fire_list.update_animation(delta_time)

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
        self.broken_car_layer.draw()
        self.fire_list.draw()