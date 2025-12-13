import arcade
import os


class ScrollingBackground:
    def __init__(self, map_path, car, screen_width, screen_height):
        self.car = car
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Initialize camera - check if Camera2D is available in this version
        try:
            self.camera = arcade.Camera2D()
        except AttributeError:
            # Fallback for older versions - might not have scrolling camera
            self.camera = None
        self.view_bottom = 0

        # Load map
        try:
            self.tile_map = arcade.load_tilemap(map_path, scaling=1.6)
        except Exception as e:
            print(f"Error loading tilemap from {map_path}: {e}")
            raise

        # Extract the road layer (supports multiple tile layer names)
        # Try common layer names
        self.road_layer = None
        for layer_name in ["Tile Layer 1", "road", "Road", "track", "Track"]:
            if layer_name in self.tile_map.sprite_lists:
                self.road_layer = self.tile_map.sprite_lists[layer_name]
                break
        
        # If no road layer found, use the first available sprite list
        if self.road_layer is None and len(self.tile_map.sprite_lists) > 0:
            self.road_layer = list(self.tile_map.sprite_lists.values())[0]

        # For a wider view, we could potentially scale the camera or adjust the view
        # Increase the horizontal view to make the map feel wider
        # Use zoom instead of modifying viewport directly to avoid compatibility issues
        if self.camera:
            # Instead of modifying viewport, use zoom to show a wider area
            # A zoom value < 1.0 means we see more of the scene (zoomed out)
            try:
                self.camera.zoom = 0.8  # Zoom out to show more horizontal space
            except AttributeError:
                # If zoom property doesn't exist, the camera will work normally
                pass
    
    def get_object_layers(self):
        """Get object layers from the tilemap."""
        if hasattr(self.tile_map, 'object_lists'):
            return self.tile_map.object_lists
        return {}
    
    def cleanup(self):
        """Clean up resources when switching levels."""
        # Clear the tile map reference
        self.tile_map = None
        self.road_layer = None

    def update(self):
        # Scroll the camera based on the car's speed (how fast it's moving forward)
        # The car stays fixed vertically, so we scroll the world instead
        if self.camera:
            screen_center_x = self.car.center_x
            # Move camera vertically based on car speed (simulates forward movement)
            screen_center_y = self.view_bottom + self.car.speed
            self.view_bottom = screen_center_y

            # Update camera position to follow the car's movement
            try:
                self.camera.position = (screen_center_x, screen_center_y)
            except AttributeError:
                # Some versions use center_x, center_y attributes directly
                self.camera.center_x = screen_center_x
                self.camera.center_y = screen_center_y
        else:
            # If no camera available, scroll the road sprites manually
            self.view_bottom += self.car.speed
            # Move all sprites in the road layer in the opposite direction to simulate scrolling
            for sprite in self.road_layer:
                sprite.center_y -= self.car.speed

    def draw(self):
        # Use the camera to draw the scrolling background if available
        if self.camera:
            # Use the camera if available
            self.camera.use()

        # Draw the road layer
        self.road_layer.draw()

        # Potentially draw with a modified view to make map appear wider
        # This approach depends on the camera implementation
