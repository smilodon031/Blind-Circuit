import arcade
from car import PlayerCar
from constants import SCREEN_HEIGHT, SCREEN_WIDTH

class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Blind Circuit")
        arcade.set_background_color(arcade.color.LIGHT_BLUE)

        self.car = PlayerCar(250, 400)   # spawn position
        self.scene = arcade.Scene()
        self.scene.add_sprite("Player", self.car)
        
    def setup(self):
        pass

    def on_draw(self):
        self.clear()
        self.scene.draw()

    def on_update(self, delta_time):
        self.car.update(SCREEN_WIDTH, SCREEN_HEIGHT)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.car.change_x = -self.car.speed
        elif key == arcade.key.RIGHT:
            self.car.change_x = self.car.speed
        elif key == arcade.key.UP:
            self.car.change_y = self.car.speed
        elif key == arcade.key.DOWN:
            self.car.change_y = -self.car.speed

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.car.change_x = 0
        elif key in (arcade.key.UP, arcade.key.DOWN):
            self.car.change_y = 0



def main():
    window = MyGame(400, 700)
    arcade.run()

if __name__ == "__main__":
    main()
