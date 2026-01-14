import arcade
from game import MyGame
from constants import SCREEN_HEIGHT, SCREEN_WIDTH



def main():
    # Only window creation and initial setup happens here
    # All game logic is contained within the MyGame class in game.py
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
 