import pygame
import sys
import os
import random
import time


class Tile:
    def __init__(self, row, col, xPos, yPos, tile_w):
        self.isBomb = False
        self.num_bombs_adj = 0

        self.row = row
        self.col = col

        self.xPos = xPos
        self.yPos = yPos

        self.tile_w = tile_w

        self.visible = False
        self.isFlagged = False

        self.bomb_img = pygame.transform.scale(pygame.image.load(os.path.abspath("res/images/bomb.png")),
                                               (tile_w, tile_w))
        self.cell_img = pygame.transform.scale(pygame.image.load(os.path.abspath("res/images/cell.png")),
                                               (tile_w, tile_w))
        self.flag_img = pygame.transform.scale(pygame.image.load(os.path.abspath("res/images/flag.png")),
                                               (tile_w, tile_w))

        self.text_colours = {1: (0, 0, 255), 2: (0, 153, 0), 3: (255, 0, 0), 4: (0, 0, 102), 5: (51, 0, 25),
                             6: (32, 32, 32)}

    def render(self, display):

        if self.visible:
            pygame.draw.rect(display, (185, 185, 185), (self.xPos, self.yPos, self.tile_w, self.tile_w))
            if self.num_bombs_adj > 0:
                self.msgToScreen(str(self.num_bombs_adj), display, self.text_colours[self.num_bombs_adj],
                                 int(self.tile_w * .75), None, True,
                                 self.xPos + self.tile_w // 2 - int(self.tile_w * .2),
                                 self.yPos + self.tile_w // 2 - int(self.tile_w * .2))
            if self.isBomb:
                display.blit(self.bomb_img, (self.xPos, self.yPos))
        elif self.isFlagged:
            display.blit(self.flag_img, (self.xPos, self.yPos))
        else:
            display.blit(self.cell_img, (self.xPos, self.yPos))

    def msgToScreen(self, msg, display, color, fontSize, font, isBold, xPos, yPos):
        font = pygame.font.SysFont(font, fontSize, bold=isBold)
        screen_text = font.render(msg, True, color)
        display.blit(screen_text, [xPos, yPos])


class Game:
    def __init__(self, numTiles, numBombs):
        pygame.init()
        self.tile_width = 50
        self.dimensions = (self.tile_width * numTiles, self.tile_width * numTiles)
        self.display = pygame.display.set_mode(self.dimensions)
        self.clock = pygame.time.Clock()

        self.running = True
        self.fps = 10

        self.num_bombs = self.flags_left = numBombs

        self.tile_grid = []

        self.start_time = 0

        self.rows = int(self.dimensions[0] / self.tile_width)
        self.cols = int(self.dimensions[1] / self.tile_width)

        pygame.display.set_caption(
            "Minesweeper: " + str(self.rows) + "x" + str(self.cols) + " " + str(self.num_bombs) + " Bombs")

    def run(self):
        self.set_up()
        self.start_time = time.time()
        while self.running:
            self.event_handler()

            self.update()
            self.render()

            self.clock.tick(self.fps)

    def update(self):
        pass

    def render(self):

        self.render_tiles()
        '''for x in self.tile_grid:
            for j in x:
                if j.isBomb:
                    pygame.draw.rect(self.display, (255, 0, 0), (j.xPos, j.yPos, self.tile_width, self.tile_width))'''
        self.draw_grid()

        pygame.display.update()

    def render_tiles(self):
        for row in self.tile_grid:
            for tile in row:
                tile.render(self.display)

    def generate_tiles(self):
        tile_grid = [[Tile(x, y, x * self.tile_width,
                           y * self.tile_width,
                           self.tile_width) for x in range(int(self.dimensions[0] / self.tile_width))] for y in
                     range(int(self.dimensions[1] / self.tile_width))]

        for i in range(self.num_bombs):
            while True:
                x = random.randrange(self.rows)
                y = random.randrange(self.cols)
                if not tile_grid[y][x].isBomb:
                    tile_grid[y][x].isBomb = True
                    break

        for x in range(self.rows):
            for y in range(self.cols):
                if not tile_grid[y][x].isBomb:
                    for (dx, dy) in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                        if self.inbounds(x + dx, y + dy):
                            if tile_grid[y + dy][x + dx].isBomb:
                                tile_grid[y][x].num_bombs_adj += 1
                else:
                    tile_grid[y][x].num_bombs_adj = -1
        return tile_grid

    def draw_grid(self):
        for x in range(self.rows):
            pygame.draw.line(self.display, (0, 0, 0), (x * self.tile_width, 0),
                             (x * self.tile_width, self.dimensions[1]))
        for y in range(self.cols):
            pygame.draw.line(self.display, (0, 0, 0), (0, y * self.tile_width),
                             (self.dimensions[0], y * self.tile_width))

    def set_up(self):
        sTime = time.time()
        self.tile_grid = self.generate_tiles()
        print("Generated Cells in %.2f seconds" % (time.time() - sTime))

    def inbounds(self, x, y):
        if x >= 0 and x < self.rows and y >= 0 and y < self.cols:
            return True
        return False

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mX, mY = pygame.mouse.get_pos()
                indexs = (mX // self.tile_width, mY // self.tile_width)
                if event.button == 1 and not self.tile_grid[indexs[1]][indexs[0]].isFlagged:

                    self.flood_fill(indexs[0], indexs[1])
                    if self.tile_grid[indexs[1]][indexs[0]].isBomb:
                        self.reveal_tiles()
                        pygame.display.set_caption("Game Over! Press 'r' to Reset")
                        print(time.time() - self.start_time)
                elif event.button == 3:

                    if self.flags_left >= 0:
                        if self.flags_left == 0:
                            self.tile_grid[indexs[1]][indexs[0]].isFlagged = False
                        else:
                            self.tile_grid[indexs[1]][indexs[0]].isFlagged = not self.tile_grid[indexs[1]][
                                indexs[0]].isFlagged

                    if self.flags_left > 0:
                        if not self.tile_grid[indexs[1]][indexs[0]].isFlagged:
                            self.flags_left += 1
                        else:
                            self.flags_left -= 1

                        pygame.display.set_caption(
                            "Minesweeper: " + str(self.rows) + "x" + str(self.cols) + " " + str(
                                self.flags_left) + " Bombs Left")

                    x = 0
                    for row in self.tile_grid:
                        for tile in row:
                            if tile.isBomb and tile.isFlagged:
                                x += 1
                    if x == self.num_bombs:
                        # WIN CASE
                        print("U win")

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()

    def display_adj_tiles(self, mx, my):
        self.tile_grid[my // self.tile_width][mx // self.tile_width].visible = True

    def flood_fill(self, x, y):
        if not self.inbounds(x, y):
            return
        tile = self.tile_grid[y][x]
        if tile.isBomb or tile.visible or tile.isFlagged:
            return

        tile.visible = True

        if tile.num_bombs_adj > 0:
            return

        for (dx, dy) in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            self.flood_fill(x + dx, y + dy)

    def reveal_tiles(self):
        for row in self.tile_grid:
            for tile in row:
                if tile.isFlagged:
                    tile.isFlagged = False
                if tile.isBomb:
                    tile.visible = True

    def reset(self):
        self.tile_grid = self.generate_tiles()
        self.flags_left = self.num_bombs
        pygame.display.set_caption(
            "Minesweeper: " + str(self.rows) + "x" + str(self.cols) + " " + str(self.num_bombs) + " Bombs")


game = Game(int(input("Dimension of board: ")), int(input("Number of bombs: ")))
game.run()
