from settings import *
from pytmx.util_pygame import load_pygame
from os.path import join, dirname, abspath

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Mycomon')

        self.import_assets()
        self.setup(self.tmx_maps['world'], 'house')

    def import_assets(self):
        base_path = dirname(dirname(abspath(__file__)))   # points to Game/
        map_path = join(base_path, 'data', 'maps', 'world.tmx')

        print("Loading map from:", map_path)  # debug
        self.tmx_maps = {'world': load_pygame(map_path)}

    def setup(self, tmx_map, player_start_pos):
        for x,y, surf in tmx_map.get_layer_by_name('Terrain').tiles():
            print(x,y, surf)

    def run(self):
        while True:
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # game logic
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()