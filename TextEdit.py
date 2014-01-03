import pygame, re, os, json
from pygame.locals import *
from mouseHandler import *
from keyboardHandler import *
from guiHandler import *
from imageStruct import *

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
        global syntaxDtb, right

        lineWidth = fontDtb.bodyFont.styles["regular"].size(line)[0]
        if lineWidth > right:
            right = lineWidth
        del lineWidth
        
        indeces = []
        keysIn = []
        
        exprC = ["",""]
        exprC[0] = "".join(["\\"+x for x in syntaxDtb.active.comt[0]])
        exprC[1] = "".join(["\\"+x for x in syntaxDtb.active.comt[1]])
        
        commentExpr = exprC[0] + "+.*"

        for match in re.finditer(commentExpr, line):

            if match.span()[0] == 0 or (line[match.span()[0] - 1] != "'" and line[match.span()[0] - 1] != '"'):
                indeces.append([match.span()[0]])
                keysIn.append(match.group())

        special = re.findall(r"\"+.*?(?=\")\"", line) + re.findall(r"\'+.*?(?=\')\'", line) + re.findall(r"[0-9]+\.?[0-9]*", line)
        for i in range(len(special)):
            cur = []
            padded = padWord(special[i])
            for match in re.finditer(padded, line):
                cur.append(match.span()[0])
            indeces.append(cur)
            keysIn.append(special[i])

        found = re.findall(r"[a-zA-Z_]+", line) + re.findall(r"[=!+/*-]+", line)

        final = []
        if len(found) > 0:
            for l in range(len(found)):
                if syntaxDtb.isKeyword(found[l]) and found[l] not in keysIn:
                    keysIn.append(found[l])
                    indeces.append(findAllKeys(found[l], line, padWord(found[l])))

        if len(indeces) == 0:
            return [[False, line]]
        
        else:
            final = []
            string = ""
            k = 0
            while k < len(line):
                added = False
                for j in range(len(indeces)):
                    if k in indeces[j]:
                        added = True
                        if string != "":
                            final.append([False, string])
                        final.append([True, keysIn[j] , syntaxDtb.active.wordColour(keysIn[j])])
                        string = ""
                        k += len(keysIn[j])
                        break
                    
                if not added and k < len(line):
                    string += line[k]
                    k += 1
            
            if string != "":
                 final.append([False, string])
        return final

    def longestLine(self):
        longest = 0
        lHold = ""
        for line in self.lines:
            if len(line) > longest:
                longest = len(line)
                lHold = line
        return lHold

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
        fontDtb.adjustScale()

    def parsedSize(self, position):
        charX = 0
        x = position[0]
        y = position[1]
        width = 0
        i = 0
        while i < len(self.parsed[y]):
            if charX + len(self.parsed[y][i][1]) > x:
                if self.parsed[y][i][0]:
                    style = themeDtb.active.groups[self.parsed[y][i][2]].settings["style"]
                    partSize = fontDtb.bodyFont.styles[style].size(self.parsed[y][i][1][:x - charX])[0]
                else:
                    style = themeDtb.active.groups["def"].settings["style"]
                    partSize = fontDtb.bodyFont.styles[style].size(self.parsed[y][i][1][:x - charX])[0]
                return width + partSize
            else:
                if self.parsed[y][i][0]:
                    style = themeDtb.active.groups[self.parsed[y][i][2]].settings["style"]
                    partSize = fontDtb.bodyFont.styles[style].size(self.parsed[y][i][1])[0]
                else:
                    style = themeDtb.active.groups["def"].settings["style"]
                    partSize = fontDtb.bodyFont.styles[style].size(self.parsed[y][i][1])[0]
                width += partSize
                charX += len(self.parsed[y][i][1])
            i += 1
        style = themeDtb.active.groups["def"].settings["style"]
        return width
        
        
    def drawFile(self):
        sideBuff = 0
        buff = 0
        if drawLineN:
            buff = 5
            sideBuff = fontDtb.bodyFont.styles["regular"].size(str(len(self.parsed)))[0] + 4

        #Screen scope range
        scope = range(vCursor / fontDtb.bodyFont.height, ((vCursor + windh) / fontDtb.bodyFont.height) \
                      if ((vCursor + windh) / fontDtb.bodyFont.height) < len(self.parsed) else len(self.parsed))
        for i in scope:
            x = 0
            if drawLineN:
                x += sideBuff + buff

            for w in range(len(self.parsed[i])):
                
                if self.parsed[i][w][0]:
                    style = themeDtb.active.groups[self.parsed[i][w][2]].settings["style"]
                    surface = fontDtb.bodyFont.styles[style].render(self.parsed[i][w][1], 100, themeDtb.active.groups[self.parsed[i][w][2]].settings["colour"])
                    screen.blit(surface, [x - hCursor, i * fontDtb.bodyFont.height - vCursor + top])
                    x += fontDtb.bodyFont.styles[style].size(self.parsed[i][w][1])[0]
                else:
                    style = themeDtb.active.groups["def"].settings["style"]
                    surface = fontDtb.bodyFont.styles[style].render(self.parsed[i][w][1], 100, themeDtb.active.groups["def"].settings["colour"])
                    screen.blit(surface, [x - hCursor, i * fontDtb.bodyFont.height - vCursor + top])
                    x += fontDtb.bodyFont.styles[style].size(self.parsed[i][w][1])[0]
                
                
        if on:
            temp = 0
            if drawLineN:
                temp = 4
            for i in range(len(textCursors)):
                if textCursors[i].pos[1] in scope:
                    x = textCursors[i].pos[0]
                    y = textCursors[i].pos[1]
                    pygame.draw.rect(screen, themeDtb.active.settings["cursorColour"], [self.parsedSize([x, y]) + sideBuff + temp - hCursor, \
                                                         textCursors[i].pos[1] * fontDtb.bodyFont.height + 2 + top - vCursor, 2, fontDtb.bodyFont.height - 4], 0)
        if drawLineN:
            pygame.draw.rect(screen, themeDtb.active.settings["background"], [0, top, sideBuff, windh], 0)
            pygame.draw.line(screen, themeDtb.active.groups["def"].settings["colour"], [sideBuff, 0], [sideBuff, windh], 1)
            for i in scope:
                lineN = fontDtb.bodyFont.styles["regular"].render(str(i + 1).rjust(len(str(len(self.parsed)))), 20, themeDtb.active.groups["def"].settings["colour"])
                screen.blit(lineN, [2, i * fontDtb.bodyFont.height - vCursor + top])

    def add(self, string, pos):
        self.lines[pos[1]] = strInsert(string, self.lines[pos[1]], pos[0])
        self.updateLine(pos[1])

    def addLine(self, pos):
        cut = self.lines[pos[1]][pos[0]:]
        self.lines[pos[1]] = self.lines[pos[1]][:pos[0]]
        self.lines.insert(pos[1] + 1, cut)
        self.parsed.insert(pos[1] + 1, self.parseLine(cut))
        self.updateLine(pos[1])

    def remove(self, startX, startY, endX, endY):
        if startY == endY:
            self.lines[startY] = self.lines[startY][:startX] + self.lines[startY][endX:]
            self.updateLine(startY)
        else:
            self.lines = self.lines[:startY] + [self.lines[startY][:startX]] + ([self.lines[endY][endX:]] + self.lines[endY + 1:])
            
            for i in range(startY + 1, endY):
                self.parsed.pop(startY + 1)
                
            self.mergeLines(startY, startY + 1)
                
            self.updateLine(startY)
            if startY < len(self.lines) - 1:
                self.updateLine(startY + 1)

    def delete(self, pos):
        self.lines[pos[1]] = self.lines[pos[1]][:pos[0]] + self.lines[pos[1]][pos[0] + 1:]
        self.updateLine(pos[1])

    def backspace(self, pos):
        self.lines[pos[1]] =  self.lines[pos[1]][:pos[0] - 1] + self.lines[pos[1]][pos[0]:]
        self.updateLine(pos[1])
        
    
class keyGroup:
    def __init__(self, colour, words):
        self.colour = colour
        self.words = words
    
class highlight:
    def __init__(self, name, path, extenstions):
        self.name = name
        self.path = path
        self.groups = []
        self.comt = ["", ""]
        self.autoExt = extenstions
        self.getData()
        
    def getData(self):
        try:
            config = open(self.path, "r")
        except:
            warn("Cannot open " + self.path)
            return
        contents = []
        
        line = config.readline().rstrip("\n")
        cmntSplit = line.split("|")[-1].split(",")
        
        while line:
            line = config.readline().rstrip("\n")
            contents.append(line)
        config.close()
        
        self.comt[0] = cmntSplit[0]
        self.comt[1] = cmntSplit[1]
        
        knownColours = []
        cur = 0
        contents = "".join(contents)
        parsed = re.findall(r'([A-Za-z][^{}]*)', contents)
        parts = []
        curpart = []
        for i in range(0, len(parsed), 2):
            parts.append([re.findall(r"\w+", parsed[i])[0], re.findall(r"[a-zA-Z0-9_=!+/*-]+", parsed[i + 1])])
            
        for i in range(len(parts)):
            if parts[i][0] not in knownColours:
                knownColours.append(parts[i][0])
                self.groups.append(keyGroup(parts[i][0], parts[i][1]))
            else:
                for word in parts[i][1]:
                    self.groups[knownColours.index(parts[i][0])].words.append(word)

    def wordColour(self, word):
        if isNum(word):
            return "num"
        
        if (word[0] == "'" or word[0] == '"') and\
           (word[-1] == "'" or word[-1] == '"'):
            return "str"
        if word.find(self.comt[0]) == 0:
            return "cmt"
        
        for i in range(len(self.groups)):
            if self.groups[i].words.count(word) > 0:
                return self.groups[i].colour
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

class fontObj:
    def __init__(self):
        pass

class fontDatabase:
    extensions = ["fon", "ttf"]
    def __init__(self, path, fontSize):
        self.path = path
        self.bodySize = fontSize
        self.guiSize = 18
        try:
            self.fonts = os.listdir(self.path)
        except:
            warn("Acess Denied to " + self.path)
            return
        
        self.active = 2
        self.bodyFont = None
        #self.guiFont = self.loadFont(self.fonts[0], self.guiSize)

    def loadFont(self, name, size):
        newFont = fontObj()
        fontManifest = open(self.path + "/" + name + "/manifest.man")
        fontData = json.load(fontManifest)
        fontManifest.close()

        newFont.name = fontData["fontName"]
        newFont.styles = {}
        
        newFont.styles["regular"] = pygame.font.Font(self.path + "/" + name + "/" + fontData["styles"]["regular"], size)
        newFont.styles["bold"] = pygame.font.Font(self.path + "/" + name + "/" + fontData["styles"]["bold"], size)
        newFont.styles["italic"] = pygame.font.Font(self.path + "/" + name + "/" + fontData["styles"]["italic"], size)
        newFont.styles["boldItalic"] = pygame.font.Font(self.path + "/" + name + "/" + fontData["styles"]["boldItalic"], size)

        newFont.height = newFont.styles["regular"].size("I")[1]

        return newFont

    def setActiveByName(self, path, size):
        global bottom, right
        self.bodySize = size
        self.bodyFont = self.loadFont(path, self.bodySize)
        if len(files) != 0:
            bottom = len(files[openFile].lines) * self.bodyFont.height
            right = self.bodyFont.styles["regular"].size(files[openFile].longestLine())[0]
            scale = self.bodyFont.height * 3

    def adjustScale(self, size = None):
        global bottom, right, scale
        if size == None:
            size = self.bodySize
        self.bodySize = size
        self.updateFont()
        bottom = len(files[openFile].lines) * self.bodyFont.height
        right = self.bodyFont.styles["regular"].size(files[openFile].longestLine())[0]
        scale = self.bodyFont.height * 3

    def updateFont(self):
        self.bodyFont = self.loadFont(themeDtb.active.settings["bodyFont"], self.bodySize)   
        
class group:
    def __init__(self):
        pass

class theme:
    def __init__(self):
        pass

class themeDatabase:
    def __init__(self, paths, name = "default"):
        self.themeNames = []
        self.nameList = []
        for path in paths:
            self.themeNames.append([path] + os.listdir(path))
            names = os.listdir(path)
            for i in range(len(names)):
                self.nameList += [names[i].split(".")[0]]
        self.pathIndex = [1, 0]
        self.defaultTheme = self.loadTheme("user/themes/prop/default")
        self.active = None
        self.setActiveByName(name)
    
    def setActiveByName(self, name):
        nameIndex = self.getPathIndex(name)
        if nameIndex != None:
            self.active = self.loadTheme(self.themeNames[nameIndex[0]][0] + "/" + self.themeNames[nameIndex[0]][nameIndex[1]])
            self.pathIndex[0] = nameIndex[0]
            self.pathIndex[1] = nameIndex[1]
            fontDtb.setActiveByName(self.active.settings["bodyFont"], 18)

    def getPathIndex(self, name):
        pathName = addExtension(name, "tme")
        if pathName != None:
            for i in range(len(self.themeNames)):
                if self.themeNames[i].count(pathName) > 0:
                    return [i, self.themeNames[i].index(pathName)]
            return -1

    def indexOfName(self, name):
        pathName = addExtension(name, "tme")
        if pathName != None:
            count = 0
            for i in range(len(self.themeNames)):
                if self.themeNames[i].count(pathName) > 0:
                    return count + self.themeNames[i].index(pathName) - 1
                count += len(self.themeNames[i]) - 1

    def loadTheme(self, path):
        
        newTheme = theme()
        path = addExtension(path, "tme")
        themeFile = open(path)
        themeData = json.load(themeFile)
        themeFile.close()
        newTheme.name = themeData["name"]

        newTheme.settings = {}
        for setting in themeData["settings"][0]:
            newTheme.settings[setting] = themeData["settings"][0][setting]

        if path.split("/")[-1] != "default.tme":
            for setting in self.defaultTheme.settings:
                if setting not in newTheme.settings:
                    newTheme.settings[setting] = self.defaultTheme.settings[setting]

        newTheme.groups = {}
        for i in range(1, len(themeData["settings"])):
            newGroup = group()
            name = themeData["settings"][i]["group"]
            newGroup.settings = {}
            for setting in themeData["settings"][i]["settings"]:
                newGroup.settings[setting] = themeData["settings"][i]["settings"][setting]

            if path.split("/")[-1] != "default.tme":
                for setting in self.defaultTheme.groups[name].settings:
                    if setting not in newGroup.settings:
                        newGroup.settings[setting] = self.defaultTheme.groups[name].settings[setting]
                
            newTheme.groups[name] = newGroup   
        return newTheme

class textCursor:
    def __init__(self, pos, index = -1):
        self.pos = pos
        if index == -1:
            self.index = len(textCursors)
        else:
            self.index = index
            
    def update(self):
        global vCursor, files, initialClick, bottom
        
        if keyboard.keys[K_RIGHT]:
            if initialClick[0] != -1 and not keyboard.modifiers[1]:
                initialClick[0] = -1
                initialClick[1] = -1

            elif initialClick[0] == -1 and keyboard.modifiers[1]:
                initialClick[0] = self.pos[0]
                initialClick[1] = self.pos[1]
                
            if self.pos[0] < len(files[openFile].lines[self.pos[1]]):
                self.pos[0] += 1
            elif self.pos[1] < len(files[openFile].lines) - 1:
                self.pos[1] += 1
                self.pos[0] = 0
                
        elif keyboard.keys[K_LEFT]:
            if initialClick[0] != -1 and not keyboard.modifiers[1]:
                initialClick[0] = -1
                initialClick[1] = -1

            elif initialClick[0] == -1 and keyboard.modifiers[1]:
                initialClick[0] = self.pos[0]
                initialClick[1] = self.pos[1]
                
            if self.pos[0] > 0:
                self.pos[0] -= 1
            elif self.pos[1] > 0:
                self.pos[1] -= 1
                self.pos[0] = len(files[openFile].lines[self.pos[1]])

        if keyboard.keys[K_UP]:
            if initialClick[0] != -1 and not keyboard.modifiers[1]:
                initialClick[0] = -1
                initialClick[1] = -1

            elif initialClick[0] == -1 and keyboard.modifiers[1]:
                initialClick[0] = self.pos[0]
                initialClick[1] = self.pos[1]
                
            if self.pos[1] > 0:

                if self.pos[0] > len(files[openFile].lines[self.pos[1]]) - 1:
                    self.pos[0] = len(files[openFile].lines[self.pos[1]])
                    
                if self.pos[1] * fontDtb.bodyFont.height < vCursor:
                        vCursor = self.pos[1] * fontDtb.bodyFont.height - windh / 2
                elif (self.pos[1] - 1) * fontDtb.bodyFont.height < vCursor:
                    vCursor -= fontDtb.bodyFont.height
                    
                self.pos[1] -= 1

            
        elif keyboard.keys[K_DOWN]:
            if initialClick[0] != -1 and not keyboard.modifiers[1]:
                initialClick[0] = -1
                initialClick[1] = -1

            elif initialClick[0] == -1 and keyboard.modifiers[1]:
                initialClick[0] = self.pos[0]
                initialClick[1] = self.pos[1]
                
            if self.pos[1] < len(files[openFile].lines) - 1:
                
                if self.pos[0] > len(files[openFile].lines[self.pos[1]]) - 1:
                    self.pos[0] = len(files[openFile].lines[self.pos[1]])
                self.pos[1] += 1
                    
            if self.pos[1] * fontDtb.bodyFont.height > vCursor + windh:
                vCursor = self.pos[1] * fontDtb.bodyFont.height - windh / 2
            elif (self.pos[1] + 3) * fontDtb.bodyFont.height > vCursor + windh:
                vCursor += fontDtb.bodyFont.height
                
        
        #add string to cur line in place
        if keyboard.string != "":
            initialClick = [-1, -1]
            files[openFile].add(keyboard.string, self.pos)
            self.pos[0] += len(keyboard.string)

        #shift line in cursor place by tab width amount
        elif keyboard.keys[K_TAB]:
            initialClick = [-1, -1]
            files[openFile].addToLine(" " * tabWidth, self.pos)
            self.pos[0] += tabWidth

        #cut line in cursor place and move to new line
        elif keyboard.keys[K_RETURN]:
            initialClick = [-1, -1]
            files[openFile].addLine(self.pos)

            #shift cursor pos down a line and to the start
            self.pos[1] += 1
            self.pos[0] = 0
            bottom = len(files[openFile].lines) * fontDtb.bodyFont.height

        #remove chars in front cursor
        elif keyboard.keys[K_DELETE]:
            if isSelection:
                files[openFile].remove(startX, startY, endX, endY)
                
                self.pos = [startX, startY]
                initialClick = [-1, -1]
            else:
                #delete chars on same line
                if self.pos[0] < len(files[openFile].lines[self.pos[1]]):
                    files[openFile].delete(self.pos)

                #merge line below onto current line
                elif self.pos[1] < len(files[openFile].lines) - 1:
                    files[openFile].mergeLines(self.pos[1], self.pos[1] + 1)
                    files[openFile].updateLine(self.pos[1])

        #delete chars before cursor
        elif keyboard.keys[K_BACKSPACE]:
            
            if isSelection:
                files[openFile].remove(startX, startY, endX, endY)
                
                self.pos = [startX, startY]
                initialClick = [-1, -1]
            else:
                #delete chars on cur line
                if self.pos[0] > 0:
                    files[openFile].backspace(self.pos)
                    
                    self.pos[0] -= 1

                #merge cur line onto line above
                elif self.pos[1] > 0:
                    
                    self.pos[0] = len(files[openFile].lines[self.pos[1] - 1])
                    files[openFile].mergeLines(self.pos[1] - 1, self.pos[1])
                    if self.pos[1] < len(files[openFile].lines) - 1:
                        files[openFile].updateLine(self.pos[1])
                    self.pos[1] -= 1
                initialClick = [-1, -1]

def warn(string):
    print "warn -", string

def findAllKeys(string, text, regex):
    matches = []
    for match in re.finditer(regex , text):
        if not inString(text, match.span()):
            if not strIsAlpha(string):
                matches.append(match.span()[0])
                
            elif match.span()[1] < len(text):
                if match.span()[0] == 0 and not isAlpha(text[match.span()[1]]):
                    matches.append(match.span()[0])
                elif not isAlpha(text[match.span()[0] - 1]) and not isAlpha(text[match.span()[1]]):
                    matches.append(match.span()[0])
                    
            elif isAlpha(text[match.span()[0]]) and not isAlpha(text[match.span()[0] - 1]):
                matches.append(match.span()[0])

            elif match.span()[0] == 0 and match.span()[1] == len(text):
                matches.append(match.span()[0])

    return matches

def loadImages(path):
    extWhitelist = ["jpg", "png"]
    images = {}
    try:
        imgList = os.listdir(path)
    except:
        warn("Access Denied to " + path)

    for i in range(len(imgList)):
        name = imgList[i].split(".")[0]
        ext = imgList[i].split(".")[-1]
        if name not in images and ext in extWhitelist:
            images[name] = img(pygame.image.load(path + "/" + imgList[i]).convert_alpha())

    return images

def isAlpha(char):
    return ord(char) in range(97, 123) or\
           ord(char) in range(65, 91)

def strIsAlpha(string):
    for c in string:
        if not isAlpha(c):
            return False
    return True

def isNum(string):
    if string[0] == "-" and len(string) == 1:
        return False
    
    if string.count(".") > 1:
        return False

    return not False in [True if ord(x) in range(48, 58) or x in ('-', '.') else False for x in string]

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

def padWord(word):
    spans = []
    padded = ""
    for match in re.finditer("\W", word):
        spans.append(match.span()[0])
    for j in range(len(word)):
        if j in spans:
            padded += "\\" + word[j]
        else:
            padded += word[j]

    return padded

def addExtension(name, extension):
    if name.count(".") > 1:
        return None
    elif name.count(".") == 1:
        if name.split(".")[-1] == extension:
            return name
        else:
            return None
    else:
        return name + "." + extension
    
global colours, syntaxDtb, fontDtb, screen, vCursor, hCursor, drawLineN, bgColour, lineColour,\
       cursorColour, selectionColour, bottom, top, right, openFile, scale, tabWidth, \
       textCursors, openFile, dtb, startY, endY, startX, endX, isSelection

#initialize pygame
pygame.init()

#window width and height
windw, windh = 1900, 980

#screen flush colour
bgColour = [255, 255, 255]

#line highlight colour
lineColour = [240, 240, 240]

#cursor colour
cursorColour = [0, 0, 0]

#selection foreground
selectionColour = [180, 180, 180]

#Top and bottom boundaries, top variable
top, bottom = 30, 0

#right boundary
right = 0

#spaces in a tab
tabWidth = 4

#Cursor blink on and off intervals
onInterval = 500
offInterval = 400

#selection boundaries
startY, endY, startX, endX = 0, 0, 0, 0

#is there a selection bool
isSelection = False

#vertical and horizontal scroll pos
vCursor = 0
hCursor = 0

#Draw line numbers bool
drawLineN = True

screen = pygame.display.set_mode([windw, windh], pygame.RESIZABLE)

#open file index
openFile = 0

files = []

syntaxDtb = syntaxDatabase("manifest.txt")
fontDtb = fontDatabase("assets/fonts", 20)
themeDtb = themeDatabase(["user/themes/custom", "user/themes/prop"], "dark")

files.append(File("files/textEdit.py"))
fontDtb.adjustScale()


guiComponents = guiManager(loadImages("assets/images/GUI"))

#initializing mouse and keyboard
mouse = Mouse()
keyboard = Keyboard()

textCursors = []
textCursors.append(textCursor([0, 0]))
initialClick = [-1, -1]


scale = 100
pygame.key.set_repeat(250, 30)
clock = pygame.time.Clock()

guiComponents.setFont(pygame.font.SysFont("Courier", 15))
guiComponents.addItem(DropDown([windw - 300, 0], [200, 26], ["hi"], 0), "fontSelector")
guiComponents.addItem(DropDown([windw - 600, 0], [200, 26], ["hi"], 0), "themeSelector")
guiComponents.addItem(CheckBox([20, 0], [20, 20], drawLineN), "lnToggle")

time = 0
on = True
style = themeDtb.active.groups["def"].settings["style"]

run = True
while run:
    time += clock.get_time()
    mouse.lastState = mouse.clicked
    for i in range(len(keyboard.keys)):
        keyboard.last[i] = keyboard.keys[i]
        keyboard.keys[i] = False
        
    for event in pygame.event.get():
        if event.type == VIDEORESIZE:
            windw, windh = event.size
            
            #you are actually supposed to do this
            screen = pygame.display.set_mode([windw, windh], pygame.RESIZABLE)
            
        if event.type == QUIT:
            run = False

        if event.type == MOUSEBUTTONUP:
            mouse.eventUpdate(event)
            
        if event.type == MOUSEBUTTONDOWN:
            mouse.eventUpdate(event)
            
        if event.type == KEYDOWN:
            if event.key not in keyboard.blackList and len(event.unicode) > 0:
                if ord(event.unicode) in range(32, 127):
                    keyboard.keys[ord(event.unicode)] = True
            else:
                keyboard.keys[event.key] = True

            if event.key in keyboard.modifiersK:
                keyboard.modifiers[keyboard.modifiersK.index(event.key)] = True
                
        if event.type == KEYUP:
            if event.key in keyboard.modifiersK:
                keyboard.modifiers[keyboard.modifiersK.index(event.key)] = False
    
        if mouse.buttons[4]:
            if keyboard.modifiers[0]:
                fontDtb.adjustScale(fontDtb.bodySize + 2)
                vCursor += fontDtb.bodyFont.height
                
            elif  vCursor > 0:
                vCursor -= scale
                
        elif mouse.buttons[5]:
            if keyboard.modifiers[0]:
                if fontDtb.bodySize - 2  > 2:
                    fontDtb.adjustScale(fontDtb.bodySize - 2)
                    vCursor -= fontDtb.bodyFont.height
                
            elif vCursor + windh < bottom + top:
                vCursor += scale

    if mouse.buttons[2]:
        if vCursor >= 0 and vCursor + windh <= bottom + top:
            vCursor += (mouse.lastpos[1][1] - mouse.lastpos[0][1]) * 4

        if hCursor >= 0 and hCursor + windw <= right:
            hCursor += (mouse.lastpos[1][0] - mouse.lastpos[0][0])

    if vCursor < 0:
        vCursor = 0
    elif vCursor + windh > bottom + top and bottom - windh >= 0:
        vCursor = bottom - windh + top

    if hCursor < 0:
        hCursor = 0
    elif hCursor + windw > right and right > windw:
        hCursor = right - windw
        
    mouse.update()
    keyboard.buildString()
    if on:
        if time >= onInterval:
            on = not on
            time = 0
    else:
        if time >= offInterval:
            on = not on
            time = 0
            
    if mouse.clicked and mouse.pos[1] > top:
        xPos = hCursor
        yPos = (mouse.pos[1] + vCursor - top) / fontDtb.bodyFont.height
        nLines = len(files[openFile].lines)
        if yPos > nLines - 1:
            yPos = nLines - 1
            
        nChars = len(files[openFile].lines[yPos])
        #-4 hard coded value to align cursor better
        charX = -4
        
        if drawLineN:
            charX = fontDtb.bodyFont.styles["regular"].size(str(nLines))[0]
        sliceMetrics = []
        for i in range(len(files[openFile].parsed[yPos])):
            if files[openFile].parsed[yPos][i][0]:
                style = themeDtb.active.groups[files[openFile].parsed[yPos][i][2]].settings["style"]
                sliceMetrics += fontDtb.bodyFont.styles[style].metrics(files[openFile].parsed[yPos][i][1])
            else:
                style = themeDtb.active.groups["def"].settings["style"]
                sliceMetrics += fontDtb.bodyFont.styles[style].metrics(files[openFile].parsed[yPos][i][1])
        #sliceMetrics = fontDtb.bodyFont.styles["regular"].metrics(files[openFile].lines[yPos])
        mouseRect = pygame.Rect(mouse.pos[0] + hCursor, mouse.pos[1] + vCursor - top, 1, 1)
        if drawLineN and mouseRect.x < fontDtb.bodyFont.styles["regular"].size(str(len(files[openFile].lines)))[0] + 9:
            mouseRect.x = fontDtb.bodyFont.styles["regular"].size(str(len(files[openFile].lines)))[0] + 9
        picked = False
        for i in range(nChars):
            if mouseRect.colliderect(pygame.Rect(charX, yPos * fontDtb.bodyFont.height, sliceMetrics[i][4], fontDtb.bodyFont.height)):
                xPos = i
                picked = True
                break
            charX += sliceMetrics[i][4]
            
        if not picked and xPos == 0 and i == nChars - 1:
            xPos = nChars

        if not mouse.lastState:
            initialClick[0] = xPos
            initialClick[1] = yPos
            
        textCursors[0].pos[0] = xPos
        textCursors[0].pos[1] = yPos

    #Get the selection boundaries - on calculated once now
    if initialClick[0] != -1 and ((initialClick[0] != textCursors[0].pos[0] and\
                                   initialClick[1] == textCursors[0].pos[1]) or initialClick[1] != textCursors[0].pos[1]):
        isSelection = True
        endY = max(textCursors[0].pos[1], initialClick[1])
        startY = min(textCursors[0].pos[1], initialClick[1])
        
        if startY == endY:
            startX = min(textCursors[0].pos[0], initialClick[0])
            endX = max(textCursors[0].pos[0], initialClick[0])
        elif startY == textCursors[0].pos[1]:
            startX = textCursors[0].pos[0]
            endX = initialClick[0]
        else:
            startX = initialClick[0]
            endX = textCursors[0].pos[0]
    else:
        isSelection = False
    
    for i in range(len(textCursors)):
        textCursors[i].update()
    
    guiComponents.update(mouse)
        
    drawLineN = guiComponents.items["lnToggle"].state
    if guiComponents.items["fontSelector"].newSelection() and guiComponents.items["fontSelector"].selected != -1:
        pass
        #fontDtb.active = guiComponents.items["fontSelector"].selected
        #fontDtb.adjustScale(0)

    if guiComponents.items["themeSelector"].newSelection() and guiComponents.items["themeSelector"].selected != -1:
        themeDtb.setActiveByName(guiComponents.items["themeSelector"].items[guiComponents.items["themeSelector"].selected])

    screen.fill(themeDtb.active.settings["background"])
    

    if isSelection:
        for i in range(startY, endY + 1):
            lineWidth = 0
            actualX = -hCursor
            actualY = fontDtb.bodyFont.height * i + top - vCursor
            if drawLineN:
                actualX += fontDtb.bodyFont.styles["regular"].size(str(len(files[openFile].lines)))[0] + 9
                
            if i == startY and i == endY:
                
                actualX += files[openFile].parsedSize([startX, i])
                #fontDtb.bodyFont.styles["regular"].size(files[openFile].lines[i][:startX])[0]
                
                lineWidth = files[openFile].parsedSize([endX, i]) - files[openFile].parsedSize([startX, i])
                #fontDtb.bodyFont.styles["regular"].size(files[openFile].lines[i][startX:endX])[0]
            elif i == startY:
                actualX += files[openFile].parsedSize([startX, i])
                #fontDtb.bodyFont.styles["regular"].size(files[openFile].lines[i][:startX])[0]
                lineWidth = windw - actualX
            elif i == endY:
                lineWidth = files[openFile].parsedSize([endX, i])
                #fontDtb.bodyFont.styles["regular"].size(files[openFile].lines[i][:endX])[0]
            else:
                lineWidth = windw

            pygame.draw.rect(screen, themeDtb.active.settings["selections"], (actualX, fontDtb.bodyFont.height * i - vCursor + top, lineWidth, fontDtb.bodyFont.height), 0)
    else:
        for j in range(len(textCursors)):
            pygame.draw.rect(screen, themeDtb.active.settings["lineHighlight"], [0, textCursors[j].pos[1] * fontDtb.bodyFont.height - vCursor + top, windw - 5, fontDtb.bodyFont.height], 0)

    files[openFile].drawFile()
        
    #Draw top bar
    pygame.draw.rect(screen, themeDtb.active.settings["background"], [0, 0, windw, top], 0)
    
    #Draw all gui items
    guiComponents.draw(screen)
        
    pygame.display.flip()
    clock.tick()
pygame.quit()
