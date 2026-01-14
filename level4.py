import arcade
import random
from bot_ai import BotCar

class Level4Background:
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
        self.map_path = "assets/maps/level4.tmx"
        self.broken_texture = arcade.load_texture('assets/sprites/obstacles/broken_texture.png')
        
        # Camera shake for obstacle hits
        self.shake_time = 0
        # Shake for hit_wall_rect (exposed for game.py to use)
        self.hit_wall_shake_time = 0
        # Current shake offsets (exposed for game.py to use)
        self.hit_wall_shake_offset_x = 0
        self.hit_wall_shake_offset_y = 0

        self.in_light = False
        
        self.bot_list = arcade.SpriteList()
        # Lane centers: [115, 205, 295, 385]
        # Player spawns at lane 205, bot spawns at lane 115 (outer left)
        bot_x = 115
        bot_y = car.center_y - 20
        bot = BotCar(bot_x, bot_y, level_difficulty=4, car_target=car)
        self.bot_list.append(bot)
        assert car.center_x != bot.center_x, "Player and bot must spawn in different lanes"

        # Load map
        self.tile_map = arcade.load_tilemap(self.map_path, scaling=1.57)

        # Extract the layers
        self.road_layer = self.tile_map.sprite_lists["Road"]
        self.object1_layer = self.tile_map.sprite_lists["Object1"]
        self.finish_line_layer = self.tile_map.sprite_lists["FinishLine"]
        self.puddles_layer = self.tile_map.sprite_lists["Puddles"]
        self.speed_ramp_layer = self.tile_map.sprite_lists["SpeedRamp"]
        
        # Pass obstacles to bot
        for bot in self.bot_list:
            bot.set_context(
                obstacles=[self.object1_layer],
                puddles=[self.puddles_layer],
                ramps=[self.speed_ramp_layer]
            )
        

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

        for bot in self.bot_list:
            bot.update(delta_time)
            if not bot.exploding and not bot.race_finished:
                object1_bot_list = arcade.check_for_collision_with_list(bot, self.object1_layer)
                for obstacle in object1_bot_list:
                    if obstacle.texture != self.broken_texture:
                        bot.explode()
                
                finish_line_bot_list = arcade.check_for_collision_with_list(bot, self.finish_line_layer)
                if finish_line_bot_list:
                    finish = finish_line_bot_list[0]
                    if bot.center_y > finish.center_y and not bot.race_finished:
                        bot.race_finished = True
                        self.car.race_lost = True
                        self.car.losing = True

        # Scroll all layers to create forward movement illusion
        if not self.car.losing:
            scroll_layers = [self.road_layer, self.object1_layer, self.finish_line_layer, self.puddles_layer, self.speed_ramp_layer]
            for layer in scroll_layers:
                for sprite in layer:
                    sprite.center_y -= self.car.speed
            for bot in self.bot_list:
                if not bot.race_finished:
                    bot.center_y -= self.car.speed
        
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
        self.bot_list.draw()
