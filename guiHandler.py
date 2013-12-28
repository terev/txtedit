import pygame, Image
from pygame.locals import *
from Image import image

global font, fontHeight, imageList
imageList = {}

class guiManager:
    def __init__(self, images, items = {}):
        global imageList
        imageList = images
        self.items = items

    def update(self, mouse):
        for i in self.items:
            self.items[i].update(mouse)

    def draw(self, surface):
        for i in self.items:
            self.items[i].draw(surface)

    def addItem(self, item, guiId):
        self.items[guiId] = item

    def setFont(self, fontObj):
        global font, fontHeight
        font = fontObj
        fontHeight = font.size("I")[1]

class Control:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size

    #only virtual
    def update(self, mouse):
        pass

    #only virtual
    def draw(self, surface):
        pass

class DropDown(Control):
    def __init__(self, pos, size, items = [], selected = -1):
        Control.__init__(self, pos, size)
        self.items = items
        self.dropButton = Button([self.pos[0] + self.size[0], self.pos[1]], [self.size[1], self.size[1]], True, [0, 0, 0], imageList["DropDown"])
        self.dropOpen = False
        self.selected = selected
        self.lastSelected = self.selected
        
    def update(self, mouse):
        if self.lastSelected != self.selected:
            self.lastSelected = self.selected
            
        self.dropButton.update(mouse)
        if self.dropButton.activated:
            self.dropOpen = not self.dropOpen

        if self.dropOpen and mouse.clickRelease:
            for i in range(len(self.items)):
                if pygame.Rect(mouse.pos[0], mouse.pos[1], 1, 1).colliderect(pygame.Rect(self.pos[0] + 2, self.pos[1] + self.size[1] + i * fontHeight, self.size[0], fontHeight)):
                    self.selected = i
                    self.dropOpen = False
                    break

    def draw(self, surface):
        if self.selected != -1:
            txt = font.render(self.items[self.selected], 20, [0, 0, 0])
            surface.blit(txt, [self.pos[0] + 2, self.pos[1]])

        if self.dropOpen:
            pygame.draw.rect(surface, [0, 0, 0], [self.pos[0], self.pos[1] + self.size[1], self.size[0], fontHeight * len(self.items)], 2)
            for i in range(len(self.items)):
                txtSurf = font.render(self.items[i], 20, [0, 0, 0])
                surface.blit(txtSurf, [self.pos[0] + 2, self.pos[1] + self.size[1] + i * fontHeight])
            
        pygame.draw.rect(surface, [0, 0, 0], [self.pos[0], self.pos[1], self.size[0], self.size[1]], 2)
        self.dropButton.draw(surface)

    def newSelection(self):
        return self.lastSelected != self.selected
            
class Button(Control):
    def __init__(self, pos, size, doOffset = True, colour = [0, 0, 0], image = None):
        Control.__init__(self, pos, size)
        self.colour = colour
        self.clicked = False
        self.icon = image
        self.activated = False
        if doOffset:
            self.offset = 1
        else:
            self.offset = 0

    def update(self, mouse):
        self.clicked = False
        self.activated = False
        if pygame.Rect(mouse.pos[0], mouse.pos[1], 1, 1).colliderect(pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])):
            if mouse.clicked:
                self.clicked = True
            elif mouse.clickRelease:
                self.activated = True

    def draw(self, surface):
        if self.clicked:
            pygame.draw.rect(surface, self.colour, [self.pos[0] + self.offset, self.pos[1] - self.offset, self.size[0], self.size[1]], 2)
            if self.icon != None:
                surface.blit(self.icon.image, (self.pos[0] - self.icon.width / 2 + self.offset + self.size[0] / 2, self.pos[1] - self.icon.height / 2 - self.offset + self.size[1] / 2))
        else:
            pygame.draw.rect(surface, self.colour, [self.pos[0], self.pos[1], self.size[0], self.size[1]], 2)
            if self.icon != None:
                surface.blit(self.icon.image, (self.pos[0] - self.icon.width / 2 + self.size[0] / 2, self.pos[1] - self.icon.height / 2 + self.size[1] / 2))

class CheckBox(Control):
    def __init__(self, pos, size, state):
        Control.__init__(self, pos, size)
        self.buttonActivator = Button(pos, size, False)
        self.state = state

    def update(self, mouse):
        self.buttonActivator.update(mouse)
        if self.buttonActivator.activated:
            self.state = not self.state
            
    def draw(self, surface):
        self.buttonActivator.draw(surface)
        if self.state:
            pygame.draw.rect(surface, [0, 0, 0], [self.pos[0] + 4, self.pos[1] + 4, self.size[0] - 8, self.size[1] - 8], 0)
