import arcade
import random

class Drone(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        
        # Load the spritesheet
        self.textures = arcade.load_spritesheet(
            "assets/sprites/obstacles/drones.png",
            sprite_width=64,
            sprite_height=64,
            columns=2,
            count=2
        )
        self.texture = self.textures[0]
        self.cur_texture_index = 0
        self.time_counter = 0.0
        self.animation_speed = 0.1  # Fast animation speed
        
        # Scale the drone to match game style if needed, assuming 1.0 or similar to previous objects
        # Level 5 used scale 2.5 for fire dispensers, but standard tiles are scaled by 1.57 in background
        # Let's start with no extra scaling unless needed, but Tiled objects might need position adjustment
        # If these are tiles, they will be scaled by the map scaling (1.57). 
        # But wait, the user said "The drones layer is an object layer" in "3. Drones" section.
        # But I found it was a Tile Layer in the TMX (id=6 name="Drones"). 
        # However, usually we can treat tile layers as sprites.
        # Let's look at how Level 5 handled FireDispenser - it was an Object Group in the TMX?
        # In Level 6 TMX, "Drones" led to data, encoded as csv. So it IS a Tile Layer.
        # IF it is a tile layer, we load it as a SpriteList directly from the map.
        # BUT the user said "Each drone: Is a collidable obstacle... Drones must be animated."
        # The standard way to animate tiles in this engine seems to be replacing them with custom sprites
        # OR using animated tiles in Tiled.
        # The user's instructions "The drones layer is an object layer" might be a goal or a misunderstanding of the TMX.
        # Since I see it as a Tile Layer in the TMX, I should probably iterate over it and replace tiles with Drone sprites, 
        # OR just treat the loaded sprites as Drones if I can swap their texture.
        # Better approach: When loading the map, read the "Drones" layer. For each sprite in that layer, 
        # replace it with a Drone object instance at that position.
        
    def update_animation(self, delta_time: float = 1/60):
        self.time_counter += delta_time
        if self.time_counter >= self.animation_speed:
            self.time_counter = 0
            self.cur_texture_index += 1
            if self.cur_texture_index >= len(self.textures):
                self.cur_texture_index = 0
            self.texture = self.textures[self.cur_texture_index]

class Level6Background:
    def __init__(self, car, screen_width, screen_height):
        self.car = car
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Track boundaries for progress calculation
        self.track_start_y = 0
        self.track_end_y = 250 * 64 * 1.57  # Map is 250 tiles high

        self.puddle_timer = 10
        self.speed_ramp_timer = 5
        self.view_bottom = 0
        self.map_path = "assets/maps/level6.tmx"
        self.broken_texture = arcade.load_texture('assets/sprites/obstacles/broken_texture.png')
        
        # Camera shake
        self.shake_time = 0
        self.hit_wall_shake_time = 0
        self.hit_wall_shake_offset_x = 0
        self.hit_wall_shake_offset_y = 0

        self.in_light = False

        # Load map
        self.tile_map = arcade.load_tilemap(self.map_path, scaling=1.57)

        # Extract the layers
        self.road_layer = self.tile_map.sprite_lists["Road"]
        self.object1_layer = self.tile_map.sprite_lists["Object1"]
        self.finish_line_layer = self.tile_map.sprite_lists["FinishLine"]
        self.speed_ramp_layer = self.tile_map.sprite_lists["SpeedRamp"]
        self.light_layer = self.tile_map.sprite_lists["Light"]
        
        # Drones layer handling
        # Since Drones is a tile layer in the TMX, we load it, but we want animated Drones.
        # We will iterate through the loaded sprites, create Drone objects at their positions, 
        # and use those instead of the static tiles.
        self.drones_list = arcade.SpriteList()
        if "Drones" in self.tile_map.sprite_lists:
            # We use the loaded tiles to get positions
            raw_drones = self.tile_map.sprite_lists["Drones"]
            for tile in raw_drones:
                # Create a Drone at the tile's position
                drone = Drone(tile.center_x, tile.center_y)
                # Match the scaling of the map
                drone.scale = 1.57
                self.drones_list.append(drone)
        
        # Puddles might not exist in level 6, but good to check or handle if added later
        self.puddles_layer = self.tile_map.sprite_lists.get("Puddles", arcade.SpriteList())

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
        
        # Collision with Drones
        drones_hit = arcade.check_for_collision_with_list(self.car, self.drones_list)
        for drone in drones_hit:
            # We can use the same logic: turn it into broken texture or just standard hit
            # The prompt says: "Is a collidable obstacle. Causes the player to lose 1 life on collision"
            # It doesn't explicitly say to change texture, but "All layers behave exactly the same as previous level files" -> usually obstacles break.
            # However, Drones are animated. If we change texture to broken_texture, animation stops naturally (texture replaced).
            if drone.texture != self.broken_texture:
                drone.texture = self.broken_texture
                # Stop animating if broken? The update_animation might overwrite this next frame if we are not careful.
                # But Drone.update_animation sets self.texture. 
                # So we should probably remove it from animation list or handle it in Drone class.
                # Simpler approach matching Level 3 Fire logic: 
                # If we want to stop animation, we can add a property.
                # Or just let it happen.
                # Actually, if I change the texture here, the next update_animation will swap it back to the animation frame.
                # So I should probably remove it from the list or have a 'broken' state in Drone.
                # BUT, let's keep it simple. Level 3 fire sprites are decorations.
                # Let's modify Drone to handle broken state.
                # Wait, I cannot modify the Drone class easily if I didn't stick it in there.
                # I'll just remove the drone and replace it with a static broken sprite in a different list?
                # Or add 'broken' attribute to Drone.
                pass
            
            # Actually, let's stick to the simplest interpretation. 
            # If hit, lose life. The user said "Each drone: Is a collidable obstacle, Causes the player to lose 1 life".
            # It didn't explicitly say "Break into broken texture". 
            # BUT Level 3 obstacles do break.
            # Let's try to just register the hit.
            # To prevent multiple hits from same drone, we need to track it.
            # I will use the set texture method and check it, but I need to stop animation.
            
            # Let's add a 'broken' flag to Drone class dynamically or check texture?
            # If I stick to "All layers behave exactly the same", then yes, break it.
            
            if not getattr(drone, 'broken', False):
                drone.broken = True
                drone.texture = self.broken_texture
                self.car.lives -= 1
                self.car.life_just_lost = True
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
        if arcade.check_for_collision_with_list(self.car, self.puddles_layer):
            if self.puddle_timer > 0:
                self.car.speed = 1
                self.puddle_timer -= delta_time
        
        # Speed ramps boost the car
        if arcade.check_for_collision_with_list(self.car, self.speed_ramp_layer):
            if self.speed_ramp_timer > 0:
                self.car.speed += 4
                self.speed_ramp_timer -= delta_time
        
        # Light collision
        if arcade.check_for_collision_with_list(self.car, self.light_layer):
            self.in_light = True
        else:
            self.in_light = False

        # Scroll all layers to create forward movement illusion
        if not self.car.losing:
            scroll_layers = [self.road_layer, self.object1_layer, self.finish_line_layer, self.puddles_layer, self.speed_ramp_layer, self.light_layer, self.drones_list]
            for layer in scroll_layers:
                for sprite in layer:
                    sprite.center_y -= self.car.speed
        
        # Update camera shake timer
        if self.shake_time > 0:
            self.shake_time -= delta_time
        if self.hit_wall_shake_time > 0:
            self.hit_wall_shake_time -= delta_time
            
        # Update drone animations
        for drone in self.drones_list:
            if not getattr(drone, 'broken', False):
                drone.update_animation(delta_time)

    def draw(self):
        # Calculate shake offsets for hit_wall_rect
        self.hit_wall_shake_offset_x = 0
        self.hit_wall_shake_offset_y = 0
        if self.hit_wall_shake_time > 0:
            self.hit_wall_shake_offset_x = random.uniform(-2, 2)
            self.hit_wall_shake_offset_y = random.uniform(-2, 2)
        
        # Draw layers
        self.road_layer.draw()
        self.light_layer.draw()
        self.object1_layer.draw()
        self.finish_line_layer.draw()
        self.puddles_layer.draw()
        self.speed_ramp_layer.draw()
        self.drones_list.draw()
