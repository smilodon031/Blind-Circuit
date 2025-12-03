import arcade

class ScrollingBackground:
    def __init__(self, image_path, car, screen_width, screen_height):
        self.car = car
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Load the texture once
        self.texture = arcade.load_texture(image_path)

        # --- Create two background sprites ---
        self.bg_1 = arcade.Sprite(image_path)
        self.bg_2 = arcade.Sprite(image_path)

        # Scale background to screen width
        scale = screen_width / self.bg_1.width
        self.bg_1.scale = scale
        self.bg_2.scale = scale

        # Position them
        self.bg_1.center_x = screen_width // 2 + 25
        self.bg_2.center_x = screen_width // 2 + 25

        # One at bottom, one directly above
        self.bg_1.center_y = self.bg_1.height // 2
        self.bg_2.center_y = self.bg_1.center_y + self.bg_1.height

        # Put in a SpriteList for easy drawing
        self.background_list = arcade.SpriteList()
        self.background_list.append(self.bg_1)
        self.background_list.append(self.bg_2)

    def update(self):
        # Scroll relative to car movement exactly like your old code
        scroll_amount = self.car.change_y

        self.bg_1.center_y -= scroll_amount
        self.bg_2.center_y -= scroll_amount

        # Wrap when an image moves off screen
        if self.bg_1.center_y <= -self.bg_1.height // 2:
            self.bg_1.center_y = self.bg_2.center_y + self.bg_2.height

        if self.bg_2.center_y <= -self.bg_2.height // 2:
            self.bg_2.center_y = self.bg_1.center_y + self.bg_1.height

    def draw(self):
        self.background_list.draw()
