import pygame, re, os
from pygame.locals import *

class File:
    def __init__(self, path):
        self.path = path
        self.ext = ""
        self.lines = []
        self.parsed = []
        self.loadFile()
        
    def loadFile(self):
        global syntaxDtb
        
        self.ext = self.path.split("/")[-1].split(".")[-1]
        auto = syntaxDtb.isExt(self.ext)
        if auto != -1:
            syntaxDtb.active = syntaxDtb.configs[auto]
        try:
            thisFile = open(self.path, "r")
        except:
            warn("Cannot open " + self.path)
            return
        
        for line in thisFile:
            self.lines.append(line.rstrip("\n"))
        thisFile.close()
        
        for i in self.lines:
            self.parsed.append(self.parseLine(i))
            
    def parseLine(self, line):
        global syntaxDtb
        found = re.findall(r"\b(\w+\b)", line)
        if len(found) > 0:
            keysIn = []
            indeces = []
            final = []

            for l in range(len(found)):
                if found[l] != "":
                    if syntaxDtb.isKeyword(found[l])and found[l] not in keysIn:
                        keysIn.append(found[l])
                        indeces.append(findAll(found[l], line))

            if len(keysIn) == 0:
                return [[False, line]]
            
            else:
                fixed = line
                for l in range(len(keysIn)):
                    fixed = "".join(fixed.split(keysIn[l]))
                final = []
                string = ""
                k = 0
                while k < len(line):
                    added = False
                    for j in range(len(indeces)):
                        if k in indeces[j]:
                            if string != "":
                                final.append([False, string])
                            final.append([True, keysIn[j], syntaxDtb.active.wordColor(keysIn[j])])
                            string = ""
                            k += len(keysIn[j])
                            break
                        
                    if k < len(line):
                        string += line[k]
                    k += 1
                
                if string != "":
                     final.append([False, string])
            return final
            
        else:
            return [[False, line]]

    def updateLine(self, lineNum):
        parsed = self.parseLine(self.lines[lineNum])
        self.parsed[lineNum] = parsed[:]

    def mergeLines(self, dest, src):
        self.parsed[dest] += self.parsed[src]
        self.lines[dest] += self.lines[src]
        
        del self.parsed[src]
        del self.lines[src]
        for i in range(dest, len(self.lines)):
            self.updateLine(i)
        fontDtb.adjustScale(0)
        
        
    def drawFile(self):
        buff = 5
        largest = fontDtb.selected.size(str(len(self.parsed)))[0] + 4
        pygame.draw.rect(screen, [200, 200, 200], [0, top, largest, windh], 0)

        #Screen scope range
        scope = range(cursor / fontDtb.height, ((cursor + windh) / fontDtb.height) \
                      if ((cursor + windh) / fontDtb.height) < len(self.parsed) else len(self.parsed))
        
        for i in scope:
            x = 0
            lineN = fontDtb.selected.render(str(i + 1).rjust(len(str(len(self.parsed)))), 20, [0, 0, 0])
            screen.blit(lineN, [x + 2, i * fontDtb.height - cursor + top])
            x += largest + buff
             
            for w in range(len(self.parsed[i])):
                if self.parsed[i][w][0]:
                    surface = fontDtb.selected.render(self.parsed[i][w][1], 100, colors[self.parsed[i][w][2]])
                else:
                    surface = fontDtb.selected.render(self.parsed[i][w][1], 100, colors["def"])
                screen.blit(surface, [x, i * fontDtb.height - cursor + top])
                x += fontDtb.selected.size(self.parsed[i][w][1])[0]
                
        if on:
            for i in range(len(textCursors)):
                if textCursors[i].pos[1] in scope:
                    cursSlice = self.lines[textCursors[i].pos[1]][:textCursors[i].pos[0]]
                    pygame.draw.rect(screen, [0, 0, 0], [fontDtb.selected.size(cursSlice)[0] + largest + 4, \
                                                         textCursors[i].pos[1] * fontDtb.height + 2 + top - cursor, 2, fontDtb.height - 4], 0)
        
class keyGroup:
    def __init__(self, color, words):
        self.color = color
        self.words = words
    

class highlight:
    def __init__(self, name, path, extenstions):
        self.name = name
        self.path = path
        self.groups = []
        self.autoExt = extenstions
        self.getData()
        
    def getData(self):
        try:
            config = open(self.path, "r")
        except:
            warn("Cannot open " + self.path)
            return
        
        contents = config.read()
        config.close()
        contents = " ".join(contents.split("\n"))
        knownColors = []
        cur = 0
        parsed = re.findall(r'([A-Za-z][^{}]*)', contents)
        parts = []
        curpart = []
        for i in range(0, len(parsed), 2):
            parts.append([re.findall(r"\w+", parsed[i])[0], re.findall(r"\w+", parsed[i + 1])])
            
        for i in range(len(parts)):
            if parts[i][0] not in knownColors:
                knownColors.append(parts[i][0])
                self.groups.append(keyGroup(parts[i][0], parts[i][1]))
            else:
                for word in parts[i][1]:
                    self.groups[knownColors.index(parts[i][0])].words.append(word)

    def wordColor(self, word):
        for i in range(len(self.groups)):
            if self.groups[i].words.count(word) > 0:
                return self.groups[i].color
        return -1

class syntaxDatabase:
    def __init__(self, path):
        self.configs = []
        self.path = path
        if self.getConfigs() == -1:
            del self
            return
        self.active = None

    def getConfigs(self):
        try:
            cList = open(self.path, "r")
        except:
            warn("Cannot open " + self.path)
            return -1
        contents = cList.read()
        cList.close()
        
        for part in contents.split("\n"):
            parts = part.split(" ")
            self.configs.append(highlight(parts[0], parts[1], parts[2:] if len(parts) > 2 else ""))
            
    def isKeyword(self, word):
        for group in self.active.groups:
            if word in group.words:
                return True
        return False

    def isExt(self, extension):
        for i in range(len(self.configs)):
            if extension in self.configs[i].autoExt:
                return i
        return -1

class fontDatabase:
    def __init__(self, path, fontSize):
        self.path = path
        self.fontSize = fontSize
        self.fonts = []
        self.loadFonts()
        self.active = 0
        self.selected = self.fonts[self.active]
        self.height = self.selected.get_linesize()
        
    def loadFonts(self):
        global fontSize
        try:
            fList = os.listdir(self.path)
        except:
            warn("Acess Denied to " + self.path)
            return
        for i in range(len(fList)):
            self.fonts.append(pygame.font.Font(self.path + "/" + fList[i], self.fontSize))

    def adjustScale(self, size):
        global bottom, scale
        del self.fonts[:]
        self.fonts = []
        self.fontSize += size
        self.loadFonts()
        self.selected = self.fonts[self.active]
        self.height = self.selected.get_linesize()
        bottom = len(files[openFile].lines) * self.height
        scale = self.height * 5
        
    def updateFont(self):
        self.selected = self.fonts[self.active]

class textCursor:
    def __init__(self, pos):
        self.pos = pos
        self.index = len(textCursors)

    def update(self):
        if keyboard.keys[K_RIGHT]:
            if self.pos[0] < len(files[openFile].lines[self.pos[1]]):
                self.pos[0] += 1
                
        elif keyboard.keys[K_LEFT]:
            if self.pos[0] > 0:
                self.pos[0] -= 1
                
        if keyboard.keys[K_UP]:
            if self.pos[1] > 0:
                self.pos[1] -= 1
                if self.pos[0] > len(files[openFile].lines[self.pos[1]]) - 1:
                    self.pos[0] = len(files[openFile].lines[self.pos[1]])
            
        elif keyboard.keys[K_DOWN]:
            if self.pos[1] < len(files[openFile].lines):
                self.pos[1] += 1
                if self.pos[0] > len(files[openFile].lines[self.pos[1]]) - 1:
                    self.pos[0] = len(files[openFile].lines[self.pos[1]])
                    
        if keyboard.string != "":
            for i in range(self.index):
                if textCursors[i].pos[1] == self.pos[1]:
                    self.pos[0] += 1
            files[openFile].lines[self.pos[1]] = strInsert(keyboard.string, files[openFile].lines[self.pos[1]], self.pos[0])
            self.pos[0] += 1
            
            files[openFile].updateLine(self.pos[1])
            
        if keyboard.keys[K_TAB]:
            for i in range(self.index):
                if textCursors[i].pos[1] == self.pos[1]:
                    self.pos[0] += tabWidth
            files[openFile].lines[self.pos[1]] =  strInsert(" " * tabWidth, files[openFile].lines[self.pos[1]], self.pos[0])
            self.pos[0] += tabWidth
            files[openFile].updateLine(self.pos[1])
             
        elif keyboard.keys[K_RETURN]:
            cut = files[openFile].lines[self.pos[1]][self.pos[0]:]
            files[openFile].lines[self.pos[1]] = files[openFile].lines[self.pos[1]][:self.pos[0]]
            files[openFile].lines.insert(self.pos[1] + 1, cut)
            files[openFile].parsed.insert(self.pos[1] + 1, files[openFile].parseLine(cut))
            files[openFile].updateLine(self.pos[1])
            self.pos[0] = 0
            self.pos[1] += 1
            
        elif keyboard.keys[K_BACKSPACE]:
            if self.pos[0] > 0:
                for i in range(self.index):
                    if textCursors[i].pos[1] == self.pos[1]:
                        self.pos[0] -= 1
                files[openFile].lines[self.pos[1]] =  files[openFile].lines[self.pos[1]][:self.pos[0] - 1] +\
                                                       files[openFile].lines[self.pos[1]][self.pos[0]:]
                self.pos[0] -= 1
                files[openFile].updateLine(self.pos[1])
                
            elif self.pos[1] > 0:
                
                self.pos[0] = len(files[openFile].lines[self.pos[1] - 1])
                files[openFile].mergeLines(self.pos[1] - 1, self.pos[1])
                self.pos[1] -= 1
                
class Mouse:
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
        
    def update(self):
        global clock
        
        self.pos = pygame.mouse.get_pos()
        
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

class Keyboard:
    def __init__(self):
        self.keys = [False] * 320
        self.last = [False] * 320
        self.modifiersK = [K_LCTRL, K_LSHIFT]
        self.modifiers = [False] * 2
        self.keymap = [")", "!", "@", "#", "$", "%", "^", "&", "*", "("]
        self.string = ""

    def update(self):
        self.buildString()

    def buildString(self):
        self.string = ""
        for i in range(ord("a"), ord("z") + 1):
            if keyboard.keys[i]:
                if keyboard.modifiers[1]:
                    self.string += chr(i - 32)
                else:
                    self.string += chr(i)

        for i in range(32, 48):
            if i != 45 and keyboard.keys[i]:
                self.string += chr(i)

        for i in range(48, 58):
            if keyboard.keys[i]:
                if keyboard.modifiers[1]:
                    self.string += keyboard.keymap[i - 48]
                else:
                    self.string += chr(i)

        if keyboard.keys[K_MINUS]:
            if keyboard.modifiers[1]:
                self.string += "_"
            else:
                self.string += "-"

        elif keyboard.keys[K_EQUALS]:
            if keyboard.modifiers[1]:
                self.string += "="
            else:
                self.string += "+"
        
    def pressRelease(self, key):
        return self.last[key] and not self.keys[key]

    def newPress(self, key):
        return not self.last[key] and self.keys[key]  
            
def warn(string):
    print "warn -", string

def findAll(string, text):
    matches = []
    for match in re.finditer(r"\b" + string + "" , text):
        if not inString(text, match.span()):
            if match.span()[1] < len(text):
                if match.span()[0] == 0 and not isAlpha(text[match.span()[1]]):
                    matches.append(match.span()[0])
                elif not isAlpha(text[match.span()[0] - 1]) and not isAlpha(text[match.span()[1]]):
                    matches.append(match.span()[0])
            elif not isAlpha(text[match.span()[0] - 1]):
                matches.append(match.span()[0])

            elif match.span()[0] == 0 and match.span()[1] == len(text):
                matches.append(match.span()[0])

    return matches

def isAlpha(char):
    return ord(char) in range(ord("a"), ord("z") + 1) or\
           ord(char) in range(ord("A"), ord("Z") + 1)

def inString(text, span):
    left = False
    for i in range(span[0], -1, -1):
        if text[i] == '"':
            left = True
            break
        
    if not left:
        return False
    
    right = True
    for i in range(span[1], len(text)):
        if text[i] == '"':
            right = True
            break

    return right and left

def strInsert(part, string, index):
    return string[:index] + part + string[index:]


global colors, syntaxDtb, fontDtb, screen, cursor, bottom, top, openFile, scale, tabWidth, textCursors
pygame.init()
windw, windh = 1900, 980
screen = pygame.display.set_mode([windw, windh])
colors = {}
colors["blue"] = [0, 0, 255]
colors["red"] = [255, 0, 0]
colors["orange"] = [255, 165, 0]
colors["purple"] = [160, 3, 240]
colors["def"] = [0, 0, 0]
syntaxDtb = syntaxDatabase("manifest.txt")
fontDtb = fontDatabase("assets/fonts", 18)

files = [File("files/textEdit.py"),File("files/test.py"),
         File("files/highlightTest.py"),File("files/SquaresInSpace.py")]

openFile = 0
cursor = 0
mse = Mouse()
keyboard = Keyboard()
textCursors = []
textCursors.append(textCursor([0, 0]))
run = True
top = 0
fontDtb.adjustScale(0)
scale = 100
pygame.key.set_repeat(250, 30)
clock = pygame.time.Clock()

#spaces in a tab
tabWidth = 4

#Cursor blink on and off intervals
onInterval = 500
offInterval = 400

time = 0
on = True
while run:
    time += clock.get_time()
    mse.lastState = mse.clicked
    for i in range(len(keyboard.keys)):
        keyboard.last[i] = keyboard.keys[i]
        keyboard.keys[i] = False
        
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False

        if event.type == KEYDOWN:
            if event.key in range(len(keyboard.keys)):
                keyboard.keys[event.key] = True
                
            for i in range(len(keyboard.modifiersK)):
                if event.key == keyboard.modifiersK[i]:
                    keyboard.modifiers[i] = True
            
        if event.type == KEYUP:
            if event.key in range(len(keyboard.keys)):
                keyboard.keys[event.key] = False
                
            for i in range(len(keyboard.modifiersK)):
                if event.key == keyboard.modifiersK[i]:
                    keyboard.modifiers[i] = False
                
        if event.type == MOUSEBUTTONDOWN:
            if event.button in range(len(mse.buttons)):
                mse.buttons[event.button] = True

        elif event.type == MOUSEBUTTONUP:
            if event.button in range(len(mse.buttons)):
                mse.buttons[event.button] = False
                    
        if mse.buttons[4]:
            if keyboard.modifiers[0]:
                fontDtb.adjustScale(2)
                
            elif  cursor > 0:
                cursor -= scale
                
        elif mse.buttons[5]:
            if keyboard.modifiers[0]:
                if fontDtb.fontSize - 2  > 0:
                    fontDtb.adjustScale(-2)
                
            elif cursor + windh < bottom + top:
                cursor += scale

    if mse.buttons[2]:
        if cursor >= 0 and cursor + windh <= bottom + top:
            cursor += (mse.lastpos[1][1] - mse.lastpos[0][1]) * 4

    if cursor < 0:
        cursor = 0
    elif cursor + windh > bottom + top and bottom - windh >= 0:
        cursor = bottom - windh
        
    keyboard.update()
    mse.update()
    if on:
        if time >= onInterval:
            on = not on
            time = 0
    else:
        if time >= offInterval:
            on = not on
            time = 0
            
    if mse.clicked and not mse.lastState:
        xPos = 0
        yPos = (mse.pos[1] + cursor) / fontDtb.height
        nLines = len(files[openFile].lines)
        if yPos > nLines - 1:
            yPos = nLines - 1
            
        nChars = len(files[openFile].lines[yPos])
        charX = fontDtb.selected.size(str(nLines))[0]
        sliceMetrics = fontDtb.selected.metrics(files[openFile].lines[yPos])
        picked = False
        for i in range(nChars):
            
            if pygame.Rect(mse.pos[0], mse.pos[1] + cursor, 1, 1).colliderect(pygame.Rect(charX, yPos * fontDtb.height, sliceMetrics[i][4], fontDtb.height)):
                xPos = i
                picked = True
                break
            charX += sliceMetrics[i][4]
            
        if not picked and xPos == 0 and i == nChars - 1:
            xPos = nChars

        if keyboard.modifiers[0]:
            #Sort greatest to least y pos
            textCursors.append(textCursor([xPos, yPos]))
            temp = []
            for i in range(len(textCursors)):
                temp.append([textCursors[i].pos[1], str(i)])
            temp.sort()
            temp = temp[::-1]
            sort = []
            for i in range(len(temp)):
                sort.append(textCursors[int(temp[i][1])])
            textCursors = []
            for i in range(len(sort)):
                textCursors.append(textCursor(sort[i].pos))
                
        else:
            if len(textCursors) > 0:
                for i in range(len(textCursors) - 1, 0, -1):
                    textCursors.pop(i)
                    i -= 1
            textCursors[0].pos[0] = xPos
            textCursors[0].pos[1] = yPos
    
    for i in range(len(textCursors)):
        textCursors[i].update()
        
##    if keyboard.pressRelease(K_LEFT):
##        if openFile > 0:
##            openFile -= 1
##        else:
##            openFile = len(files) - 1
##        bottom = len(files[openFile].parsed) * fontDtb.height
##
##    if keyboard.pressRelease(K_RIGHT):
##        if openFile < len(files) - 1:
##            openFile += 1
##        else:
##            openFile = 0
##        bottom = len(files[openFile].parsed) * fontDtb.height
    screen.fill([255, 255, 255])
    files[openFile].drawFile()
    pygame.display.update()
    clock.tick()
pygame.quit()
