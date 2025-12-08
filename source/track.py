import arcade
import os

class ScrollingBackground:
    def __init__(self, tmx_map_path, car, screen_width, screen_height):
        self.car = car
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Convert relative path to absolute path based on project root
        if not os.path.isabs(tmx_map_path):
            # Assume path is relative to project root (parent of source directory)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            tmx_map_path = os.path.join(project_root, tmx_map_path)

        # Make sure the file exists
        if not os.path.exists(tmx_map_path):
            print(f"Warning: Tiled map file not found at: {tmx_map_path}")

        # Load the Tiled map
        self.tile_map = arcade.load_tilemap(tmx_map_path)

        # The tilemap object has sprite_lists for each layer
        if self.tile_map:
            # Get the sprite lists for the tilemap layers
            self.background_list = arcade.SpriteList()

            # Iterate through the sprite lists in the tilemap
            for layer_name in self.tile_map.sprite_lists:
                layer_sprite_list = self.tile_map.sprite_lists[layer_name]

                # Add all sprites from this layer to our background list
                for sprite in layer_sprite_list:
                    self.background_list.append(sprite)

            # Calculate map dimensions based on tiles
            self.map_width = self.tile_map.width * self.tile_map.tile_width
            self.map_height = self.tile_map.height * self.tile_map.tile_height
        else:
            self.map_width = screen_width
            self.map_height = screen_height
            self.background_list = arcade.SpriteList()

        # Initialize camera offset
        self.offset_x = 0
        self.offset_y = 0

    def update(self):
        # Scroll based on car's speed (negative because we're scrolling the map backwards)
        # Multiply by a factor to make scrolling more noticeable
        scroll_amount = self.car.speed * 2.0  # Increased scroll factor for more visible movement

        # Update the Y offset to create scrolling effect based on car's speed
        self.offset_y += scroll_amount

        # Keep the offset within bounds of the map
        max_offset_y = max(0, self.map_height - self.screen_height)
        if self.offset_y > max_offset_y:
            self.offset_y = max_offset_y
        if self.offset_y < 0:
            self.offset_y = 0

    def draw(self):
        # Create a temporary sprite list with adjusted positions
        temp_sprite_list = arcade.SpriteList()

        for sprite in self.background_list:
            # Create a copy of the sprite with adjusted position
            temp_sprite = arcade.Sprite()
            temp_sprite.texture = sprite.texture
            temp_sprite.scale = sprite.scale
            temp_sprite.alpha = sprite.alpha  # Preserve transparency

            # For a racing game, only adjust vertical scrolling based on the car's forward motion
            # The horizontal position should stay fixed to the original world position
            temp_sprite.center_x = sprite.center_x  # Keep original horizontal position
            temp_sprite.center_y = (sprite.center_y - self.offset_y) - (self.car.center_y - self.screen_height // 4)

            temp_sprite_list.append(temp_sprite)

        # Draw all sprites with adjusted positions
        temp_sprite_list.draw()