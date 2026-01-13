import arcade
import random


class FireDispenser(arcade.Sprite):
    """Fire dispenser that animates when the player gets close."""
    
    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y

        # Load spritesheet (5 horizontal frames, each 64x64)
        self.textures = arcade.load_spritesheet(
            "assets/sprites/obstacles/fire_dispenser.png",
            sprite_width=64,
            sprite_height=64,
            columns=5,
            count=5
        )
        
        self.texture = self.textures[0]
        self.cur_texture_index = 0
        self.time_counter = 0.0
        self.animation_speed = 0.15
        self.is_activated = False
        self.is_stopped = False
        self.hit_box = [(-32, -32), (32, -32), (32, 32), (-32, 32)]

    def stop_animation(self):
        self.is_stopped = True

    def update_animation(self, delta_time, player_nearby):
        # Activate when player gets close
        if player_nearby and not self.is_activated:
            self.is_activated = True
            self.cur_texture_index = 1
            self.texture = self.textures[1]
        
        if not self.is_activated or self.is_stopped:
            return
        
        self.time_counter += delta_time
        if self.time_counter >= self.animation_speed:
            self.time_counter = 0
            
            # Loop between frames 3 and 4 at max fire
            if self.cur_texture_index >= 3:
                if self.cur_texture_index == 3:
                    self.cur_texture_index = 4
                else:
                    self.cur_texture_index = 3
            else:
                self.cur_texture_index += 1
            
            self.texture = self.textures[self.cur_texture_index]


class Level5Background:
    def __init__(self, car, screen_width, screen_height):
        self.car = car
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.track_start_y = 0
        self.track_end_y = 200 * 64 * 1.57

        self.puddle_timer = 10
        self.speed_ramp_timer = 5
        self.view_bottom = 0
        self.map_path = "assets/maps/level5.tmx"
        self.broken_texture = arcade.load_texture('assets/sprites/obstacles/broken_texture.png')
        
        self.shake_time = 0
        self.hit_wall_shake_time = 0
        self.hit_wall_shake_offset_x = 0
        self.hit_wall_shake_offset_y = 0

        self.in_light = False

        # Load map
        self.tile_map = arcade.load_tilemap(self.map_path, scaling=1.57)

        # Extract layers
        self.road_layer = self.tile_map.sprite_lists["Road"]
        self.object1_layer = self.tile_map.sprite_lists["Object1"]
        self.finish_line_layer = self.tile_map.sprite_lists["FinishLine"]
        self.puddles_layer = self.tile_map.sprite_lists["Puddles"]
        self.speed_ramp_layer = self.tile_map.sprite_lists["SpeedRamp"]

        # Load fire dispensers from Tiled map
        self.fire_dispenser_list = arcade.SpriteList()
        if "FireDispenser" in self.tile_map.sprite_lists:
            for raw in self.tile_map.sprite_lists["FireDispenser"]:
                dispenser = FireDispenser(raw.center_x or 0, raw.center_y or 0)
                dispenser.scale = 2.5
                self.fire_dispenser_list.append(dispenser)

    def update(self, delta_time):
        if not self.car.losing:
            self.view_bottom += self.car.speed

        # Collision with obstacles
        object1_list = arcade.check_for_collision_with_list(self.car, self.object1_layer)
        for obstacle in object1_list:
            if obstacle.texture != self.broken_texture:
                obstacle.texture = self.broken_texture
                self.car.lives -= 1
                self.car.life_just_lost = True
                self.shake_time = 0.3

        # Fire dispenser collision (shake and stop animation)
        fire_hits = arcade.check_for_collision_with_list(self.car, self.fire_dispenser_list)
        for dispenser in fire_hits:
            dispenser.stop_animation()
            self.shake_time = 0.3

        # Wall hit shake
        if self.car.hit_wall and self.hit_wall_shake_time <= 0:
            self.hit_wall_shake_time = 0.3
            
        # Finish line
        finish_line_list = arcade.check_for_collision_with_list(self.car, self.finish_line_layer)
        if finish_line_list:
            if self.car.center_y > finish_line_list[0].center_y:
                self.car.race_won = True
                self.car.speed = 0
        
        # Puddles slow down
        if arcade.check_for_collision_with_list(self.car, self.puddles_layer):
            if self.puddle_timer > 0:
                self.car.speed = 1
                self.puddle_timer -= delta_time
        
        # Speed ramps boost
        if arcade.check_for_collision_with_list(self.car, self.speed_ramp_layer):
            if self.speed_ramp_timer > 0:
                self.car.speed += 4
                self.speed_ramp_timer -= delta_time

        # Scroll all layers
        if not self.car.losing:
            scroll_layers = [self.road_layer, self.object1_layer, self.finish_line_layer, self.puddles_layer, self.speed_ramp_layer, self.fire_dispenser_list]
            for layer in scroll_layers:
                for sprite in layer:
                    sprite.center_y -= self.car.speed
        
        # Update shake timers
        if self.shake_time > 0:
            self.shake_time -= delta_time
        if self.hit_wall_shake_time > 0:
            self.hit_wall_shake_time -= delta_time

        # Update fire dispenser animations
        for dispenser in self.fire_dispenser_list:
            distance = abs(dispenser.center_x - self.car.center_x) + abs(dispenser.center_y - self.car.center_y)
            dispenser.update_animation(delta_time, distance < 300)

    def draw(self):
        self.hit_wall_shake_offset_x = 0
        self.hit_wall_shake_offset_y = 0
        if self.hit_wall_shake_time > 0:
            self.hit_wall_shake_offset_x = random.uniform(-2, 2)
            self.hit_wall_shake_offset_y = random.uniform(-2, 2)
        
        self.road_layer.draw()
        self.object1_layer.draw()
        self.finish_line_layer.draw()
        self.puddles_layer.draw()
        self.speed_ramp_layer.draw()
        self.fire_dispenser_list.draw()
