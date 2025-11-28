import arcade
from game import MyGame

def main():
    window = MyGame(500,800)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
