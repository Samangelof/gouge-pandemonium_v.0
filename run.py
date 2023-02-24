import arcade
from main import (
    GougeGame,
    SCREEN_WIDTH, 
    SCREEN_HEIGHT, 
    SCREEN_TITLE)

def main():
    window = GougeGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()




if __name__ == "__main__":
    main()