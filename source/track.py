import arcade


class ScrollingBackground:
    def __init__(self, map_path, car, screen_width, screen_height):
        self.car = car
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.cooldown = 0
        self.puddle_timer = 5
        self.view_bottom = 0

        # Load map
        self.tile_map = arcade.load_tilemap(map_path, scaling=1.57)

        # Extract the layers
        self.road_layer = self.tile_map.sprite_lists["Road"]
        self.object1_layer = self.tile_map.sprite_lists["Object1"]
        self.finish_line_layer = self.tile_map.sprite_lists["FinishLine"]
        self.puddles_layer = self.tile_map.sprite_lists["Puddles"]
        self.speed_ramp_layer = self.tile_map.sprite_lists["SpeedRamp"]
        

    def update(self, delta_time):
        if self.cooldown > 0:
            self.cooldown -= 1
        else:
            self.view_bottom += self.car.speed

            if arcade.check_for_collision_with_list(self.car, self.object1_layer):
                self.car.lives -= 1
                self.car.center_y -= self.car.speed * 0.2
                self.cooldown = 5
            if arcade.check_for_collision_with_list(self.car, self.finish_line_layer):
                self.car.center_x = self.car.last_checkpoint_x
                self.car.center_y = self.car.last_checkpoint_y
            if arcade.check_for_collision_with_list(self.car, self.puddles_layer):
                if self.puddle_timer > 0:
                    self.car.speed = 1
                    self.puddle_timer -= delta_time
            if arcade.check_for_collision_with_list(self.car, self.speed_ramp_layer):
                self.car.speed += 3
        
        
        scroll_layers = [self.road_layer, self.object1_layer, self.finish_line_layer, self.puddles_layer, self.speed_ramp_layer]
        # Move all sprites in the road layer in the opposite direction to simulate scrolling
        for layer in scroll_layers:
            for sprite in layer:
                sprite.center_y -= self.car.speed


    def draw(self):
        # Draw the road layer
        self.road_layer.draw()
        self.object1_layer.draw()
        self.finish_line_layer.draw()
        self.puddles_layer.draw()

        # Potentially draw with a modified view to make map appear wider
        # This approach depends on the camera implementation
