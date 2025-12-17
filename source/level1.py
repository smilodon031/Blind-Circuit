import arcade

class Level1Background:
    def __init__(self, car, screen_width, screen_height):
        self.car = car
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.puddle_timer = 10
        self.speed_ramp_timer = 5
        self.view_bottom = 0
        self.map_path = "assets/maps/Level1.tmx"

        # Load map
        self.tile_map = arcade.load_tilemap(self.map_path, scaling=1.57)

        # Extract the layers
        self.road_layer = self.tile_map.sprite_lists["Road"]
        self.object1_layer = self.tile_map.sprite_lists["Object1"]
        self.finish_line_layer = self.tile_map.sprite_lists["FinishLine"]
        self.puddles_layer = self.tile_map.sprite_lists["Puddles"]
        self.speed_ramp_layer = self.tile_map.sprite_lists["SpeedRamp"]
        

    def update(self, delta_time):
        # Freeze background scrolling during losing state
        if not self.car.losing:
            self.view_bottom += self.car.speed

        object1_list = arcade.check_for_collision_with_list(self.car, self.object1_layer)          
        for object in object1_list:
            object.remove_from_sprite_lists()
            self.car.lives -= 1
            
        finish_line_list = arcade.check_for_collision_with_list(self.car, self.finish_line_layer)
        if finish_line_list:
            finish = finish_line_list[0]
            if self.car.center_y > finish.center_y:
                self.car.race_won = True
                self.car.speed = 0
        puddles_list = arcade.check_for_collision_with_list(self.car, self.puddles_layer)
        if puddles_list:
            if self.puddle_timer > 0:
                self.car.speed = 1
                self.puddle_timer -= delta_time
        speed_ramp_list = arcade.check_for_collision_with_list(self.car, self.speed_ramp_layer)
        if speed_ramp_list:
            if self.speed_ramp_timer > 0:
                self.car.speed += 4
                self.speed_ramp_timer -= delta_time

        
    
        # Freeze scrolling during losing state
        if not self.car.losing:
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
        self.speed_ramp_layer.draw()