import pygame
from pygame.locals import *

class Mouse(object):
    def __init__(self):
        self.clickPos = (0, 0)
        self.clicked = False
        self.pos = (0, 0)
        self.clickRelease = False
        self.lastState = False
        self.buttons = [False] * 6
        self.lastClick = -1
        self.doubleClick = False
        self.lastpos = [[0, 0], [0, 0]]
        self.frame = 0

    def eventUpdate(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button in range(len(self.buttons)):
                self.buttons[event.button] = True
                    
        elif event.type == MOUSEBUTTONUP:
            if event.button in range(len(self.buttons)):
                self.buttons[event.button] = False
                    
    def update(self):
        self.pos = pygame.mouse.get_pos()
        
        self.lastState = self.clicked
        
        self.lastpos[1][0] = self.lastpos[0][0]
        self.lastpos[1][1] = self.lastpos[0][1]
        self.lastpos[0][0] = self.pos[0]
        self.lastpos[0][1] = self.pos[1]
        
        self.clicked = self.buttons[1]

        self.clickRelease = False
        self.doubleClick = False
        
        if not self.clicked and self.lastState:
            self.clickRelease = True
            self.lastState = False
            
        if self.clickRelease:
            if self.lastClick != -1:
                if (pygame.time.get_ticks() / 1000.) - self.lastClick <= 0.25:
                    self.doubleClick = True
                self.lastClick = -1
            else:
                self.lastClick = pygame.time.get_ticks() / 1000.0
        else:
            if self.lastClick != -1:
                if (pygame.time.get_ticks() / 1000.0) - self.lastClick > 0.25:
                    self.lastClick = -1
                
        if not self.lastState and self.clicked:
            self.clickPos = pygame.mouse.get_pos()
            
    def difPos(self):
        if self.pos[0] != self.clickPos[0] and self.pos[1] != self.clickPos[1]:
            return True
        return False
