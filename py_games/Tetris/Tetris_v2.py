# -*- coding: utf-8 -*-
"""
Tetris v2
CONTROLADO POR CONTROL GESTUAL
Escrito por Pedro Castro
"""

import pygame as py
from pygame.locals import *
import os
import time
import random
import sys
import copy


# Colors
Color_black = (0, 0, 0)
Color_white = (255, 255, 255)
Color_green = (14, 162, 44) 
Color_red = (255, 28, 28)
Color_purple = (183, 14, 216)
Color_yellow = (162, 160, 14) 
Color_blue = py.Color("aqua")
Color_darkBlue = (8,22,155)
Color_orange = (255,181,30)

# CONSTANTES
WIDTH, HEIGHT = 800, 600
py.init()

clock = py.time.Clock()

# First game settings
WIN = py.display.set_mode((WIDTH, HEIGHT))
py.display.set_caption("Tetris")

# IMAGES
BG = py.transform.scale(py.image.load(os.path.join("assets", "bg_tetris.png")), (WIDTH, HEIGHT))

# GRID SETTING
GRID_WIDTH = 305
GRID_HEIGHT = 570
CELLSIZE = 35
NUMCELLSX = GRID_WIDTH // CELLSIZE # numero de celdas en x
NUMCELLSY = GRID_HEIGHT // CELLSIZE # numero de celdas en y
FALL_START_X = NUMCELLSX // 2 - 1 
FALL_START_Y = 0
START = (FALL_START_X, FALL_START_Y)

class Cell():
    
    def __init__(self, x, y, floor = False):
        self.x = x
        self.y = y
        self.sum = CELLSIZE
        self.floor = floor
        self.color = Color_black
    
    def paint(self, color, border = 0):
        if color == None:
            color = self.color
        py.draw.rect(WIN, color, (self.x, self.y, self.sum, self.sum), border)
        
class Grid():
    
    def __init__(self, width, height, offsetx, offsety):
        self.w = width
        self.h = height
        self.num_cells_x = NUMCELLSX
        self.num_cells_y = NUMCELLSY
        self.offsetx = offsetx
        self.offsety = offsety
        
    def map_grid(self, grid):
        for i in range(self.num_cells_x):
            grid.append([])
        for x in range(self.num_cells_x):
            for y in range(self.num_cells_y):
                grid[x].append(Cell((x * CELLSIZE) + self.offsetx, (y * CELLSIZE) + self.offsety))
        for x in range(self.num_cells_x):
            grid[x].append(Cell(None, None, True))


# GLOBAL GRID
grid_o = Grid(GRID_WIDTH, GRID_HEIGHT, 300, 1)
grid = []
grid_o.map_grid(grid)

# Clases auxiliares 
'''
conjunto de celdas
'''
class Piece():
    def __init__(self, ind):
        self.ind = ind # 0 -> cuadrado, 1 -> L, 2 -> L (invertida), 3 -> T, 4 -> |
        self.parts = []
        self.color = Color_black
        if ind == 0: # cuadrado
            self.parts = [[START[0], START[1]], [START[0] + 1, START[1]],[START[0], START[1] + 1],[START[0] + 1, START[1] + 1]]
            self.color = Color_yellow
            
        elif ind == 1: # L
            self.parts = [[START[0], START[1] + 2],[START[0], START[1]],[START[0], START[1] + 1],[START[0] + 1, START[1]  + 2]]
            self.color = Color_orange
        
        elif ind == 2: # L invertida
            self.parts = [[START[0], START[1] + 2],[START[0], START[1]],[START[0], START[1] + 1],[START[0] - 1, START[1] + 2]]
            self.color = Color_darkBlue
        
        elif ind == 3: # T
            self.parts = [[START[0], START[1]],[START[0] - 1, START[1]],[START[0] + 1, START[1]],[START[0], START[1] + 1]]
            self.color = Color_purple
        
        elif ind == 4: # |
            self.parts = [[START[0], START[1] + 2], [START[0], START[1]], [START[0], START[1] + 1], [START[0], START[1] + 3]]
            self.color = Color_blue
            
    def get_parts(self):
        return self.parts
    
    def fall(self): # Baja 1 en ejeY
        floor = False
        for p in self.parts:
            if grid[p[0]][p[1] + 1].floor: # si toca el suelo en ese punto
                floor = True
                break
        # si ninguna pieza supera el limite
        # se bajan las piezas una unidad
        if not floor:
            for p in self.parts:
                p[1] += 1
        else:
            self.colision() # la pieza colisiona con el suelo y se convierte en parte del suelo
        
        return floor
            
    '''
    Convierte la pieza actual en suelo (Pone esas casillas en el grid a suelo) 
    y set la pieza actual a None
    '''
    def colision(self):
        for p in self.parts:
            grid[p[0]][p[1]].floor = True
            grid[p[0]][p[1]].color = self.color
    
    def turnRight(self): # gira 90 grads a la derecha
        if self.ind != 0:
            giro = True
            nparts = self.parts
            ox = nparts[0][0]
            oy = nparts[0][1]
            offset = [0,0]
            for p in nparts[1:]:
                a = p[0]
                p[0] = ox + (oy - p[1])
                p[1] = oy + (a - ox)
                if p[0] >= NUMCELLSX:
                    resta = NUMCELLSX - p[0] - 1
                    if resta < offset[0]:
                        offset[0] = resta
                if p[0] < 0:
                    if abs(p[0]) > offset[0]:
                        offset[0] = abs(p[0])
                if p[1] >= NUMCELLSY:
                    resta = NUMCELLSY - p[1] - 1
                    if resta < offset[1]:
                        offset[1] = resta
            for i in nparts:
                i[0] += offset[0]
                i[1] += offset[1]
            # Comprueba que no haya suelo en ninguna de esas posiciones
            # TODO: bug se gira dentro del suelo
            for p in nparts:
                if grid[p[0]][p[1]].floor:
                    print("cancel giro")
                    return False
            
            self.parts = nparts
            return True
    
    def move(self, direc):
        moved = None
        if direc == 0:
            moved = [[i[0] + 1, i[1]] for i in self.parts]
        if direc == 1:
            moved = [[i[0] - 1, i[1]] for i in self.parts]
        for m in moved:
            if m[0] >= NUMCELLSX or m[0] < 0:
                return False
            elif grid[m[0]][m[1]].floor:
                return False
        self.parts = copy.deepcopy(moved)
        return True



class Tetris():
    
    def __init__(self):
        self.curPiece = None
        self.pieceQ = []
        self.pieceQGen() # cola de piezas
        self.points = 0
        
        self.timer = 0
        self.delay = 60
    
    def pieceQGen(self):
        if len(self.pieceQ) == 4:
            return
        # si la cola esta vacia la rellena con 4 piezas aleatorias
        if not self.pieceQ:
            for i in range(4):
                self.pieceQ.append(Piece(random.randint(0,4)))
            return
        # si no anhade una pieza aleatoria al final de la cola
        self.pieceQ.append(Piece(random.randint(0,4)))
    
    def updateCurPiece(self):
        if self.curPiece == None:
            self.curPiece = self.pieceQ.pop()
        
    def fall(self):
        if self.timer == self.delay:
            self.timer = 0
            return self.curPiece.fall()
        self.timer += 1
        return False
    
    '''
    comprueba si hay que borrar alguna linea
    En caso de que haya lineas que borrar las elimina
    '''
    def check_remove(self):
        delete_rows = []
        for y in range(len(NUMCELLSY)):
            row = True
            for x in range(len(NUMCELLSX)):
                if grid[x][y].floor == False:
                    row = False
            if row == True: 
                delete_rows.append(y)
        
        # HERE: deberia haber un metodo que hiciera una animacion rapida sobre las lineas eliminadas 
        
        # Set that rows to false
        for y in delete_rows:
            for x in range(len(NUMCELLSX)):
                grid[x][y].floor = False
        
        
        
    '''
    bucle principal del juego 
    '''
    def main(self):
        WIN.blit(BG, (0,0))
        run = True
        while run:
            
            for e in py.event.get():
                if e.type == py.QUIT:
                    run = False
                if e.type == py.KEYDOWN:
                    self.move(e)
            WIN.blit(BG, (0,0))
            self.pieceQGen()
            self.updateCurPiece()
            if self.fall(): # caida de la pieza
                self.curPiece = None                
            
            #self.check_remove() # Elimina lineas y baja las lineas de arriba del suelo
            
            if self.curPiece != None:
                self.paintPieces() # pinta las piezas
                
            Tetris.paintFloor() # pinta el suelo
            Tetris.paint_grid_table()
            py.display.flip()
            clock.tick(60)
            
        py.display.quit()
        py.quit()
     
    
    def move(self, event):
        if event.key == K_a: # mueve a izq
            self.curPiece.move(1)
        elif event.key == K_d: # mueve a der
            self.curPiece.move(0)
        elif event.key == K_w: # gira 90 grad
            self.curPiece.turnRight()
        elif event.key == K_s: # baja 1 la pieza (eje y) /avanza mas rapido hacia el suelo/
            if self.curPiece.fall():
                self.curPiece = None
        elif event.key == K_m: # cambia la pieza por la guardada
            pass
        elif event.key == K_n: # gira 270 grad (90 en sentido antihorario)
            pass
        elif event.key == K_SPACE: # coloca la pieza instantaneamente
            pass
        
    def paintPieces(self):
        for i in self.curPiece.get_parts():
            grid[i[0]][i[1]].paint(self.curPiece.color)
    def paintFloor():
        for x in range(NUMCELLSX):
            for y in range(NUMCELLSY):
                if grid[x][y].floor == True:
                    grid[x][y].paint(None)
                    
    def paint_grid_table():
        for x in range(NUMCELLSX):
            for y in range(NUMCELLSY):
                grid[x][y].paint(Color_black, 1)


if __name__=='__main__':
    te = Tetris()
    te.main()

