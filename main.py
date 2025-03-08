import pygame

from constants import *
from game import Game

if __name__ == "__main__":
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    game = Game(win, fenmate2[-2])
    game.run()
    pygame.quit()

"""
TODO: 
make board object less heavy, maybe piece functions outside object. maybe i'm dumb
reduce the number of moves for minmax
improve bot agrresivity when it has advantage
replace board with bitboard
allow promotion
"""
