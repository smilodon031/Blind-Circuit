import arcade
from car import PlayerCar
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from track import ScrollingBackground
from obstacle import Obstacle

class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Blind Circuit")
        arcade.set_background_color(arcade.color.LIGHT_BLUE)

        # Level management
        self.current_level = 1
        self.max_levels = 5
        
        # Manual map paths for each level
        # Set the path for each level here (relative to project root or absolute path)
        self.level_maps = {
            1: "assets/maps/Level1.tmx",
            2: "assets/maps/level2.tmx",
            3: "assets/maps/level3.tmx",
            4: "assets/maps/level4.tmx",
            5: "assets/maps/level5.tmx",
        }
        
        # Initialize track and background - these will be set up in setup()
        self.background = None
        self.car = None
        self.player_list = None
        self.obstacle_list = None
        self.finish_line = None
        
        # Store player properties that persist across levels
        self.player_lives = 3
        self.player_score = 0


    def setup(self):
        # Load level 1 initially
        self.load_level(1)

    def load_level(self, level_number):
        """Load a level by number."""
        self.current_level = level_number
        
        # Clean up old level
        if self.background:
            self.background.cleanup()
        
        # Clear obstacles
        if self.obstacle_list:
            self.obstacle_list.clear()
        else:
            self.obstacle_list = arcade.SpriteList()
        
        # Get map path from manual level maps
        if level_number in self.level_maps:
            map_path = self.level_maps[level_number]
            print(f"Loading level {level_number} from: {map_path}")
        else:
            print(f"Warning: Level {level_number} not found in level_maps")
            return
        
        # Create player if needed
        if self.car is None:
            self.car = PlayerCar(250, 400)
            self.car.lives = self.player_lives
        
        # Load the map
        try:
            self.background = ScrollingBackground(map_path, self.car, self.width, self.height)
        except Exception as e:
            print(f"Error loading map from {map_path}: {e}")
            return
        self.background.view_bottom = 0
        
        # Reset finish line
        self.finish_line = None
        
        # Create player list if needed
        if self.player_list is None:
            self.player_list = arcade.SpriteList()
            self.player_list.append(self.car)
        
        # Load objects from map
        self._load_object_layers()
        
        # Default player position if no start found
        if not hasattr(self, '_player_start_loaded'):
            self.car.center_x = 250
            self.car.center_y = 400

    def _load_object_layers(self):
        """loads objects from Tiled."""
        if not self.background or not self.background.tile_map:
            return

        layers = self.background.get_object_layers()
        self._player_start_loaded = False

        for layer_name, objects in layers.items():
            # Make sure objects is always a list
            if not isinstance(objects, list):
                objects = [objects]

            for obj in objects:
                name = ""
                if hasattr(obj, "name") and obj.name:
                    name = obj.name.lower()
                
                type_ = ""
                if hasattr(obj, "type") and obj.type:
                    type_ = obj.type.lower()

                x = obj.x * 2.0
                y = obj.y * 2.0
                width = (obj.width if hasattr(obj, "width") else 32) * 2.0
                height = (obj.height if hasattr(obj, "height") else 32) * 2.0

                # PLAYER START
                if "start" in layer_name.lower() or "start" in name or type_ == "player_start":
                    self.car.center_x = x
                    self.car.center_y = y
                    self._player_start_loaded = True

                # FINISH LINE
                elif "finish" in layer_name.lower() or "finish" in name or type_ == "finish":
                    finish = arcade.Sprite()
                    finish.center_x = x
                    finish.center_y = y
                    finish.width = width
                    finish.height = height
                    self.finish_line = finish

                # OBSTACLES
                elif "obstacle" in layer_name.lower() or "obstacle" in name or type_ == "obstacle":
                    obstacle = Obstacle(x, y, width=width, height=height)
                    self.obstacle_list.append(obstacle)

    def go_to_next_level(self):
        """Switch to the next level."""
        if self.car:
            self.player_lives = self.car.lives
        
        if self.current_level >= self.max_levels:
            print("All levels completed!")
            return
        
        self.load_level(self.current_level + 1)
        
        if self.car:
            self.car.speed = 0
            self.car.destroyed = False
            self.car.exploding = False
            self.car.hit_wall = False

    def on_draw(self):
        self.clear()
        if self.background:
            self.background.draw()
        if self.player_list:
            self.player_list.draw()
        if self.obstacle_list:
            self.obstacle_list.draw()

        # Draw "Hit wall!" text if car hit a wall (based on slowdown timer)
        if self.car and self.car.hit_wall:
            arcade.draw_text("Hit wall!", self.width//2, self.height//2, arcade.color.WHITE, 80, anchor_x="center", anchor_y="center", bold=True)
        
        # Draw level info (optional)
        arcade.draw_text(f"Level {self.current_level}", 10, self.height - 30, arcade.color.WHITE, 20)

    def on_update(self, delta_time):
        if self.background:
            self.background.update()
        if self.player_list:
            self.player_list.update()
        if self.obstacle_list:
            self.obstacle_list.update()
        
        # Check for finish line
        if self.car and self.finish_line and not self.car.destroyed and self.background:
            view_y = self.background.view_bottom
            if view_y >= self.finish_line.center_y:
                car_left = self.car.center_x - self.car.width / 2
                car_right = self.car.center_x + self.car.width / 2
                finish_left = self.finish_line.center_x - self.finish_line.width / 2
                finish_right = self.finish_line.center_x + self.finish_line.width / 2
                if not (car_right < finish_left or car_left > finish_right):
                    self.go_to_next_level()

    def on_key_press(self, key, modifiers):
        if not self.car:
            return
        if key == arcade.key.LEFT:
            self.car.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.car.right_pressed = True
        elif key == arcade.key.UP:
            self.car.up_pressed = True
        elif key == arcade.key.DOWN:
            self.car.down_pressed = True

    def on_key_release(self, key, modifiers):
        if not self.car:
            return
        if key == arcade.key.LEFT:
            self.car.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.car.right_pressed = False
        elif key == arcade.key.UP:
            self.car.up_pressed = False
        elif key == arcade.key.DOWN:
            self.car.down_pressed = False
