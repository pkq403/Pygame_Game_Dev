import pygame as py
from pygame.locals import *
import os
import time
import random
import sys

"""
Snake Game

Escrito por Pedro Castro
"""
# Colors
Color_black = (0, 0, 0)
Color_white = (255, 255, 255)
Color_green = (14, 162, 44) 
Color_red = (255, 28, 28)

class Cell():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sumX = tam_celda
        self.sumY = tam_celda
        
py.init()

clock = py.time.Clock()
WIDTH, HEIGHT = 600, 600

# First game settings
WIN = py.display.set_mode((WIDTH, HEIGHT))
py.display.set_caption("Snake Game")

tam_celda = 20 # Habra celdas de 10 x 10
num_cells = WIDTH//tam_celda


def map_grid(grid):
    for i in range(num_cells):
        grid.append([])
    for x in range(num_cells):
        for y in range(num_cells):
            grid[x].append(Cell(x * tam_celda, y * tam_celda))
            
            
grid = []
map_grid(grid)


class SnakeGame():
    def __init__(self):
        self.head = [2,4]
        self.snake = [grid[self.head[0]][self.head[1]], grid[1][4], grid[0][4]]
        
        self.apples = []
        self.eaten_apples = 0
        
        self.lose = False
        self.delay = 150 # 150 / 30 = 5 s de delay
        self.timer = 0
        
        
    def main(self):
        run = True
        while run:
            for e in py.event.get():
                if e.type == py.QUIT:
                    run = False
                if e.type == py.KEYDOWN:
                    self.move_snake(e)
            if not self.lose:
                self.fruit_gen()
                self.bg_paint()
                self.paint_snake()
                self.paint_fruit()
            else:
                self.paintLose()
                
            py.display.flip()
            clock.tick(30)
        py.display.quit()
        py.quit()
        
    def paintLose(self):
        mode_font = py.font.SysFont('ebrima',35)
        WIN.blit(mode_font.render('DERROTA', True, Color_white), (220, 250))
        
    def bg_paint(self):
        py.draw.rect(WIN, Color_black, (0,0, WIDTH, HEIGHT))
        mode_font = py.font.SysFont('Arial',25)
        WIN.blit(mode_font.render('Comidas: ' + str(self.eaten_apples), True, Color_white), (50, 550))
        
    def move_snake(self, event):
        if event.key == K_w:
            if self.head[1] > 0:
                self.head[1] -= 1
        if event.key == K_s:
            if self.head[1] < (num_cells - 1):
                self.head[1] += 1
        if event.key == K_a:
            if self.head[0] > 0:
                self.head[0] -= 1
        if event.key == K_d:
            if self.head[0] < (num_cells - 1):
                self.head[0] += 1
        new_head = grid[self.head[0]][self.head[1]]
        if new_head in self.apples:
            self.snake.insert(0, new_head)
            self.apples.remove(new_head)
            self.eaten_apples += 1
        elif new_head in self.snake:
            # Derrota
            self.lose = True
        else:
            for i in range(len(self.snake) -1, 0, -1):
                self.snake[i] = self.snake[i-1]
            self.snake[0] = new_head
    
    def paint_snake(self):
        for n in self.snake:
            py.draw.rect(WIN, Color_green, (n.x, n.y, n.sumX, n.sumY))
    def paint_fruit(self):
        for a in self.apples:
            py.draw.rect(WIN, Color_red, (a.x, a.y, tam_celda, tam_celda))
    def fruit_gen(self):
        if self.timer == self.delay:
            new_apple = grid[random.randint(0,num_cells-1)][random.randint(0,num_cells-1)]
            if new_apple not in self.snake and new_apple not in self.apples:
                self.apples.append(new_apple)
            self.timer = 0
        self.timer += 1
            
            
if __name__=='__main__':
    sg = SnakeGame()
    sg.main()