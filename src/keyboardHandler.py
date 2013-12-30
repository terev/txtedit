from pygame.locals import *

class Keyboard:
    def __init__(self):
        self.keys = [False] * 320
        self.last = [False] * 320
        self.modifiersK = [K_LCTRL, K_LSHIFT]
        self.modifiers = [False] * 2
        self.whiteList = [x for x in range(32, 127)]
        self.blackList = [K_RETURN, K_BACKSPACE, K_TAB]
        self.string = ""

    def buildString(self):
        self.string = ""
        for i in range(32, 255):
            if self.keys[i]:
                if i in self.whiteList:
                    self.string += chr(i)
        
    def pressRelease(self, key):
        return self.last[key] and not self.keys[key]

    def newPress(self, key):
        return not self.last[key] and self.keys[key]
