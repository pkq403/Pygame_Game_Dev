import pygame as py
from pygame.locals import *
import os
import time
import random
import sys
import copy

"""
Tetris

Escrito por Pedro Castro
"""
# Colors
Color_black = (0, 0, 0)
Color_white = (255, 255, 255)
Color_green = (14, 162, 44) 
Color_red = (255, 28, 28)
Color_purple = (183, 14, 216)
Color_yellow = (162, 160, 14) 
Color_blue = (28, 130, 255)
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
            self.color = py.Color("aqua")
            
    def get_parts(self):
        return self.parts
    
    def fall(self, limit): # Baja 1 en ejeY
        floor = False
        for p in range(len(self.parts)):
            if limit[self.parts[p][0]][self.parts[p][1] + 1]: # si toca el suelo en ese punto
                #print("COLISION: pieza: ", self.parts[p][1] + 1, "suelo: ", limit[self.parts[p][0]])
                floor = True
                break
        # si ninguna pieza supera el limite
        # se bajan las piezas una unidad
        if not floor:
            for p in self.parts:
                p[1] += 1
        return floor
    
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
                # TODO: si una pieza se sale al girar moverla para recolocarla dentro del grid en lugar de
                # no permitirla girar
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
            self.parts = nparts
    
    def move(self, direc):
        if direc == 0: # mueve a derecha
            for i in self.parts:
                i[0] += 1
        if direc == 1: # mueve a derecha
            for i in self.parts:
                i[0] -= 1

class Cell():
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sum = CELLSIZE
    
    def paint(self, color, border = 0):
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


class Tetris():
    
    def __init__(self):
        self.curPiece = None # Piezas actuales (grid + saved)
        self.nextPiece = Piece(2)
        self.floor = [] 
        self.lenFloor = 0
        self.points = 0
        
        grid_o = Grid(GRID_WIDTH, GRID_HEIGHT, 300, 1)
        self.grid = []
        grid_o.map_grid(self.grid)
        
        self.timer = 0
        self.delay = 60
        
        self.limitFloor = [] # [*] Array de Booleanos segun si en una casilla hay un bloque (True)
        for i in range(NUMCELLSX):
            self.limitFloor.append([])
        for colum in self.limitFloor:
            for j in range(NUMCELLSY + 1):
                colum.append(False)
        for i in self.limitFloor:
            i[NUMCELLSY] = True
        
    def main(self):
        WIN.blit(BG, (0,0))
        
        run = True
        while run:
            if len(self.floor) != 0:
                self.recalcFloor()
            for e in py.event.get():
                if e.type == py.QUIT:
                    run = False
                if e.type == py.KEYDOWN:
                    self.move(e)
            WIN.blit(BG, (0,0))

            self.fall() # avanza la pieza cada cierto tiempo
            self.pieceGen() # genera las piezas
        
            self.paintPieces() # pinta las piezas
            self.paintFloor() # pinta el suelo
            self.paint_grid()
            
            py.display.flip()
            clock.tick(60)
        py.display.quit()
        py.quit()
        
    def deletePiece(self, isFloor):
        if isFloor and self.curPiece != None:
            self.floor.append([self.curPiece.get_parts(), self.curPiece.color])
            self.curPiece = None
            
    def recalcFloor(self):
        if self.lenFloor != 0 or len(self.floor) > self.lenFloor:
            lastPiece = self.floor[-1]
            for i in lastPiece[0]:
                self.limitFloor[i[0]][i[1]] = True # Pone esas posiciones como suelo
        
    def fall(self):
        if self.timer == self.delay:
            self.timer = 0
            self.deletePiece(self.curPiece.fall(self.limitFloor))
        self.timer += 1
            
    def pieceGen(self):
        if self.curPiece == None:
            self.curPiece = self.nextPiece
            self.nextPiece = Piece(random.randint(0, 4))
            
    def lateralCol(self, moved): # Return True si choca lateralmente con algun bloque
        for m in moved:
            if m[0] >= NUMCELLSX or m[0] < 0:
                return True
            elif self.limitFloor[m[0]][m[1]]:
                return True
        return False
    
    def move(self, event):
        if event.key == K_a: # mueve a izq
            moved = [[i[0] - 1, i[1]] for i in self.curPiece.parts]
            if not self.lateralCol(moved):
                self.curPiece.move(1)
        elif event.key == K_d: # mueve a der
            moved = [[i[0] + 1, i[1]] for i in self.curPiece.parts]
            if not self.lateralCol(moved):
                self.curPiece.move(0)
        elif event.key == K_w: # cambia la pieza por la guardada
            pass
        elif event.key == K_s: # baja 1 la pieza (eje y) /avanza mas rapido hacia el suelo/
            self.deletePiece(self.curPiece.fall(self.limitFloor))
        elif event.key == K_m: # gira 90 grad
            self.curPiece.turnRight()
        elif event.key == K_n: # gira 270 grad (90 en sentido antihorario)
            pass
        elif event.key == K_SPACE: # coloca la pieza instantaneamente
            pass
        
    def paintPieces(self):
        for i in self.curPiece.get_parts():
            print(i[0], i[1])
            self.grid[i[0]][i[1]].paint(self.curPiece.color)
    
    def paintFloor(self):
        for p in self.floor:
            for a in p[0]:
                self.grid[a[0]][a[1]].paint(p[1])
        
    def paint_grid(self):
        for x in self.grid:
            for y in x:
                y.paint(Color_black, 1)
    

if __name__=='__main__':
    te = Tetris()
    te.main()