import random,time,math,sys,pygame.midi
try:import pygame
except ImportError:print"Please install Pygame.";sys.exit()
from pygame.locals import *

class spritesheet():
    def __init__(self, filename):
        try:self.sheet=pygame.image.load(filename).convert()
        except pygame.error, message:
            print 'Unable to load spritesheet image:', filename
            sys.exit(),message
    def image_at(self, rectangle, colorkey = None):
        rect=pygame.Rect(rectangle)
        image=pygame.Surface(rect.size).convert()
        image.blit(self.sheet,(0,0),rect)
        if colorkey!=None:
            if colorkey!=-1:
                colorkey=image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    def images_at(self, rects, colorkey = None):
        return [self.image_at(rect, colorkey) for rect in rects]

class bullet:
    def __init__(self,x,y,w,h,dps,weapon,colour,angle,speed):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.dps=dps
        self.weapon=weapon
        self.colour=colour
        self.angle=angle
        self.speed=speed
    def update(self):
        self.x+=math.cos(self.angle)*self.speed
        self.y+=math.sin(self.angle)*self.speed
class coin:
    def __init__(self,x,y,worth,img):
        self.x=x
        self.y=y
        self.worth=worth
        self.img=img
    def collide(self,plr):
        r=pygame.Rect(self.x,self.y,self.img.get_rect()[2],self.img.get_rect()[3])
        if r.colliderect(plr):
            midiout.set_instrument(118)
            midiout.note_on(random.randint(100,102),112)
            midiout.note_on(random.randint(70,75),112)
            plyr.score+=self.worth
            return True
        return False
        
class particle:
    def __init__(self,x,y,angle,speed,s,colour,life):
        self.x=x
        self.y=y
        self.angle=angle
        self.speed=speed
        self.s=s
        self.colour=colour
        self.life=life
    def update(self,ww,wh,Or,Ob):
        self.x+=math.cos(self.angle)*self.speed
        self.y+=math.sin(self.angle)*self.speed
        self.life-=1
        if self.x>ww+Or or self.x<0+Or or self.y>wh+Ob or self.y<0+Ob or self.life<=0:return True
        else:return False
     
class enemy:
    def __init__(self,x,y,health,speed,w,h,colour,name):
        self.x=x
        self.y=y
        self.health=health
        self.speed=speed
        self.w=w
        self.h=h
        self.colour=colour
        self.name=name
    def update(self):
        if self.health<=0:return True
        else:
            deltax=(plyr.x+plyr.w/2)-(self.x+self.w/2)
            deltay=(plyr.y+plyr.h/2)-(self.y+self.h/2)
            ab=(math.atan2(deltay,deltax))
            self.x+=math.cos(ab)*self.speed
            self.y+=math.sin(ab)*self.speed
            return False
    def collide(self):
        pr=pygame.Rect(plyr.x,plyr.y,plyr.w,plyr.h)
        er=pygame.Rect(self.x,self.y,self.w,self.h)
        if pr.colliderect(er):
            plyr.health-=random.randint(3,8)
            midiout.set_instrument(127)
            midiout.note_on(random.randint(60,65),80)
            rs=pygame.Rect((er[0]+er[2]-2,er[1]),(2,er[3]))
            ls=pygame.Rect((er[0],er[1]),(2,er[3]))
            tp=pygame.Rect((er[0],er[1]),(er[2],2))
            bt=pygame.Rect((er[0],er[1]+er[3]-2),(er[2],2))
            if pr.colliderect(rs):
                plyr.x+=self.speed+20
            elif pr.colliderect(ls):
                plyr.x-=self.speed+20
            if pr.colliderect(tp):
                plyr.y-=self.speed+20
            elif pr.colliderect(bt):
                plyr.y+=self.speed+20
class camera:
    def __init__(self,x,y,w,h,ww,wh,Or,Ob):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.ww=ww
        self.wh=wh
        self.Or=Or
        self.Ob=Ob
    def update(self):
        pr=pygame.Rect(plyr.x-self.Or,plyr.y-self.Ob,plyr.w,plyr.h)
        cr=pygame.Rect(self.x,self.y,self.w,self.h)
        if pr.colliderect(cr):
            rs=pygame.Rect((cr[0]+cr[2],cr[1]),(self.ww-cr[2],cr[3]))
            ls=pygame.Rect((0,cr[1]),(cr[0],cr[3]))
            tp=pygame.Rect((cr[0],0),(cr[2],cr[1]))
            bt=pygame.Rect((cr[0],cr[1]+cr[3]-2),(cr[2],self.wh-cr[1]))
            if (pr.colliderect(rs)):
                self.Or+=plyr.speed
            elif (pr.colliderect(ls)):
                self.Or-=plyr.speed
            if (pr.colliderect(tp)):
                self.Ob-=plyr.speed
            elif (pr.colliderect(bt)):        
                self.Ob+=plyr.speed
            return self.Or,self.Ob
        else:
            if pr[0]>self.x:self.Or+=plyr.speed*4
            elif pr[0]<self.x:self.Or-=plyr.speed*4
            if pr[1]>self.y:self.Ob+=plyr.speed*4
            elif pr[1]<self.y:self.Ob-=plyr.speed*4
            return self.Or,self.Ob
     
class player:
    def __init__(self,x,y,w,h,colour,speed,health):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.colour=colour
        self.speed=speed
        self.health=health
        self.score=0
        self.alive=True
    def update(self):
        global n
        if self.health<=0:
            n=""
            stats[2]+=1
            self.health=0
            self.alive=False
            for y in range(random.randint(10,20)):
                particles.append(particle(self.x,self.y,random.uniform(math.radians(0),math.radians(360)),pv,random.randint(3,4),(self.colour),random.randint(200,300)))
    def angle(self,mx,my,px,py):
        deltax=mx-px
        deltay=my-py
        ab=(math.atan2(deltay,deltax))
        return ab
    def aimerpos(self,px,py,angle):
        pa=[math.cos(angle)*20,math.sin(angle)*20]
        pa[0]+=px;pa[1]+=py
        return pa
    
class menu:
    def __init__(self,rects):
        self.rects=rects
        self.anim=[[0,0,False],[0,0,False],[0,0,False],[0,0,False]]
        self.active=False
    def update(self,tp,ww,wh,m):
        run=True
        paused=True
        for z in range(len(self.anim)):
            if False in self.anim[z]:
                if self.anim[z][0]>=self.rects[z][1][0] and self.anim[z][1]>=self.rects[z][1][1]:
                    self.anim[z][2]=True
                else:
                    if self.anim[z][0]<=self.rects[z][1][0]:
                        if tp>0:
                            self.anim[z][0]+=(self.rects[z][1][0]/((ww/wh)*50))
                    if self.anim[z][1]<self.rects[z][1][1]:
                        if tp>0:
                            self.anim[z][1]+=(self.rects[z][1][1]/((ww/wh)*50))
            else:
                for i in range(len(self.rects)):
                    b=pygame.Rect((self.rects[i][0][0],self.rects[i][0][1]),(self.rects[i][1][0],self.rects[i][1][1]))
                    if b.collidepoint(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]):
                        self.rects[i][2]=self.rects[i][4]
                        if m[0][1] and str(self.rects[i][5]).upper()=="EXIT GAME":
                            run=False
                        if m[0][1] and str(self.rects[i][5]).upper()=="RESUME GAME":
                            paused=False
                            break
                    else:
                        self.rects[i][2]=self.rects[i][3]
        return run,paused

class planet:
    def __init__(self,x,y,z,img):
        self.x=x
        self.y=y
        self.z=z
        self.zx=0
        self.zy=0
        self.img=img
    def update(self,Or,Ob,ww,wh):
        self.x+=.5
        if self.x>=10000:
            self.x=-10000
            self.y=random.randint(-10000,10000)
        self.zx=(self.x-Or-ww/2)*(self.z/1000.)
        self.zy=(self.y-Ob-wh/2)*(self.z/1000.)

class star:
    def __init__(self,x,y,w,h,colour,z):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.zx=0
        self.zy=0
        self.colour=colour
        self.z=z
    def update(self,Or,Ob,ww,wh):
        if self.x-outright not in range(0,windw) or self.y-outbottom not in range(0,windh):
            return True
        else:
            return False
  
def updateplanets():
    global planets
    temp=[]
    c=0
    for x in planets:
        x.update(outright,outbottom,windw,windh)
        temp.append([x.z,str(c)])
        c+=1
    temp.sort()
    templan=[]
    for x in temp:
        templan.append(planets[int(x[1])])
    planets=templan

def updatestars():
    global stars
    temp=[]
    dlt=[]
    c=0
    if len(stars)<20:
        stars.append(star(random.randint(outright,windw+outright),random.randint(outbottom,windh+outbottom),2,2,(255,255,255),0))
    for x in stars:
        if x.update(outright,outbottom,windw,windh):
            dlt.append(c)
        temp.append([x.z,str(c)])
        c+=1
    temp.sort()
    templan=[]
    for x in temp:
        templan.append(stars[int(x[1])])
    stars=templan
    tmp=[]
    for x in range(len(stars)):
        if x not in dlt:
            tmp.append(stars[x])
    stars=tmp

def updateproj():
    global projectiles
    for p in projectiles:
        p.update()
    if len(projectiles)>=100:projectiles.pop(0)

def updatecoins():
    global coins
    dlt=[]
    ct=[]
    for x in range(len(coins)):
        if coins[x][f].collide(pygame.Rect(plyr.x,plyr.y,plyr.w,plyr.h)):
            dlt.append(x)
    for x in range(len(coins)):
        if x not in dlt:
            ct.append(coins[x])
    coins=ct

def updateparticles():
    global particles
    dlt=[]
    tp=[]
    c=0
    for p in particles:
        d=p.update(windw,windh,outright,outbottom)
        if d:dlt.append(c)
        c+=1
    for x in range(len(particles)):
        if x not in dlt:
            tp.append(particles[x])
    particles=tp

def updateenemies():
    global enemies
    dlt=[]
    c=0
    te=[]
    for e in enemies:
        if e.update():
            stats[1]+=1
            midiout.set_instrument(127)
            midiout.note_on(random.randint(45,50),127)
            midiout.note_on(random.randint(45,50),127)
            midiout.note_on(random.randint(35,40),127)
            midiout.note_on(random.randint(35,40),127)
            dlt.append(c)
            for y in range(random.randint(10,20)):particles.append(particle(e.x,e.y,random.uniform(0,math.radians(360)),pv,random.randint(5,8),(random.randint(0,255),random.randint(0,255),random.randint(0,255)),random.randint(100,250)))
        c+=1
    for x in range(len(enemies)):
        if x not in dlt:
            te.append(enemies[x])
        else:
            if random.randint(1,2)>=1:
                temp=[]
                for z in range(len(co)):
                    temp.append(coin(enemies[x].x,enemies[x].y,random.randint(3,6),co[z]))
                coins.append(temp)
    enemies=te

def updatemenus():
    global menus,animatemenu
    for i in menus:
        if i.active:running,paused=i.update(tp,windw,windh,mouse)
    return running,paused

def detecthit():
    global enemies,projectiles,particles,dps
    dlt=[]
    c=0
    tp=[]
    for x in projectiles:
        a=pygame.Rect((x.x,x.y),(x.w,x.h))
        for e in enemies:
            b=pygame.Rect(e.x,e.y,e.w,e.h)
            if b.colliderect(a):
                midiout.set_instrument(118)
                midiout.note_on(random.randint(95,100),112)
                dlt.append(c)
                if x.weapon=="EXPLOSIVE SQUARE":
                    cols=[(250,120,0),(240,0,0),(255,255,0)]
                    for y in range(random.randint(10,20)):
                        particles.append(particle(x.x,x.y,random.uniform(0,math.radians(360)),pv,random.randint(3,4),cols[random.randint(0,len(cols)-1)],random.randint(100,200)))
                else:
                    for y in range(random.randint(1,2)):particles.append(particle(x.x,x.y,random.uniform(angle+math.radians(180),angle+math.radians(360)),pv,random.randint(3,4),(random.randint(0,255),random.randint(0,255),random.randint(0,255)),random.randint(100,150)))
                e.health-=random.uniform((x.dps),(x.dps+x.dps*2))
                sd=random.uniform(.94,.98)
                e.w,e.h=e.w*sd,e.h*sd
        c+=1
    for x in range(len(projectiles)):
        if x not in dlt:
            tp.append(projectiles[x])
    projectiles=tp

def collide():
    global enemies
    for enemy in enemies:
        enemy.collide()

def drawplayer():
    global blittedrect
    o=pygame.Surface((plyr.w,plyr.h))
    ot=pygame.Surface((windw,windh))
    o.fill((plyr.colour))
    ot.fill((0,0,0))
    o.set_colorkey((0, 0, 0))
    rp=pygame.Rect((0,0),(plyr.w,plyr.h))
    blittedrect=ot.blit(o,(plyr.x-outright,plyr.y-outbottom))
    oldcenter=blittedrect.center
    rotated=pygame.transform.rotate(o,math.degrees(angle)*-1)
    rotrect = rotated.get_rect()
    rotrect.center = oldcenter
    screen.blit(rotated, rotrect)
    pygame.draw.rect(screen,((255,0,0)),(((aimpos[0])-outright,(aimpos[1])-outbottom),(4,4)),1)

def drawplanets():
    global planets
    for x in planets:
        if x.x-outright+x.zx<windw and (x.x+x.img.get_rect()[2])-outright+x.zx>0 and x.y-outbottom+x.zy<windh and (x.y+x.img.get_rect()[3])-outbottom+x.zy>0:
            screen.blit(x.img,(x.x-outright+x.zx,x.y-outbottom+x.zy))

def drawstars():
    global starss
    for x in stars:
        pygame.draw.rect(screen,x.colour,(x.x-outright+x.zx,x.y-outbottom+x.zy,x.w,x.h))
 
def drawcoins():
    global coins
    for x in coins:
        screen.blit(x[f].img,(x[f].x-outright,x[f].y-outbottom))

def drawproj():
    global projectiles
    for i in projectiles:pygame.draw.rect(screen,(i.colour),((i.x-outright,i.y-outbottom),(i.w,i.h)),0)

def drawparticles():
    global particles
    for i in particles:
        if i.colour!="r":
            pygame.draw.rect(screen,(i.colour),((i.x-outright,i.y-outbottom),(i.s,i.s)),0)
        else:
            pygame.draw.rect(screen,(random.randint(0,255),random.randint(0,255),random.randint(0,255)),((i.x-outright,i.y-outbottom),(i.s,i.s)),0)

def drawenemies():
    global enemies
    for e in enemies:
        pygame.draw.rect(screen,(e.colour),((e.x-outright,e.y-outbottom),(e.w,e.h)),3)
        hp = smallest.render(("HP: "+str(math.ceil(e.health))), 5, (e.colour))
        t=hp.get_rect(center=(e.x+e.w/2-outright,e.y+e.h+20-outbottom))
        screen.blit(hp,(t[0],t[1]))
        if e.name!=None:
            name=smallest.render(str(e.name), 5, (255,255,255),(80,80,80))
            t=name.get_rect(center=(e.x+e.w/2-outright,e.y-20-outbottom))
            screen.blit(name,(t[0],t[1]))

def drawmenus():
    global menus
    for i in menus:
        if i.active:
            for x in range(len(i.rects)):
                ch=True
                if False in i.anim[x]:
                    ch=False
                if ch:
                    pdisp=menufont.render("PAUSED"+"."*(int(tp)/600)+"", 0, (255,255,255))
                    pr=pdisp.get_rect(center=(windw/2,windh/2))
                    screen.blit(pdisp,(pr[0],50))
                    for z in i.rects:
                        pygame.draw.rect(screen,(i.rects[x][2]),(i.rects[x][0],i.rects[x][1]),i.rects[x][6])
                        if i.rects[x][5]!=0:
                            button=menufont.render(i.rects[x][5], 0, (0,0,0))
                            t=button.get_rect(center=(i.rects[x][0][0]+(i.rects[x][1][0]/2),i.rects[x][0][1]+(i.rects[x][1][1]/2)))
                            screen.blit(button,(t[0],t[1]))
                else:
                    pygame.draw.rect(screen,(i.rects[x][2]),(i.rects[x][0],(i.anim[x][0],i.anim[x][1])),i.rects[x][6])

pygame.init()
time.sleep(0.2)
pygame.midi.init()

output_id = pygame.midi.get_default_output_id()
midiout = pygame.midi.Output(1,0)
midiout.set_instrument(2)
pitches=[24,26,28,29,31,33,35,\
         36,38,40,41,43,45,47,\
         48,50,52,53,55,57,59,\
         60,62,64,65,67,69,71,\
         72,74,76,77,79,81,83,\
         84,86,88,89,91,93,95]

statfile=open("bin/textfiles/stats.txt","r")
stats=[x for x in statfile.read().split("\n")]
for x in range(len(stats)):stats[x]=int(stats[x])
statfile.close()
scorefile=open("bin/textfiles/scores.txt","r")
scores=[[x.split("|")[0],x.split("|")[1]] for x in scorefile.read().split("\n")]
for x in range(len(scores)):scores[x][1]=int(scores[x][1])
scorefile.close()
tmp=[]
for x in range(len(scores)):tmp.append([scores[x][1],str(x)])
tmp.sort()
tmp2=[]
for x in range(len(tmp)):
    tmp2.append([scores[int(tmp[x][1])][0],tmp[x][0]])
scores=tmp2[::-1]
windw,windh=900,600
screen=pygame.display.set_mode((windw,windh),0,32)
maxres=pygame.display.list_modes()[0]
pygame.display.set_caption("SQUARES IN SPACE")
ico=pygame.image.load("bin/assets/Icon.png").convert_alpha()
pygame.display.set_icon(ico)
bg=pygame.image.load("bin/assets/background.png").convert_alpha()
bg=pygame.transform.scale(bg,(windw,windh))
title=pygame.image.load("bin/assets/Title.png").convert_alpha()
menufont=pygame.font.Font("bin/assets/pixelated.ttf", 30)
smaller=pygame.font.Font("bin/assets/pixelated.ttf", 25)
smallest=pygame.font.Font("bin/assets/pixelated.ttf", 15)
ppick=[]
for x in range(1,21):
    try:ppick.append(pygame.image.load("bin/assets/planet"+str(x)+".png").convert_alpha())
    except:pass
ss=spritesheet("bin/assets/coin.png")
rec=ss.sheet.get_rect()
points=[]
l,h=8,1
framew,frameh=rec[2]/l,rec[3]/h
for x in range(h):
    for y in range(l):
        points.append((y*framew,x*frameh,framew,frameh))
co=ss.images_at(points,colorkey=(0,0,0))
planets=[]
for x in range(20):
    planets.append(planet(random.randint(-10000,10000),random.randint(-10000,10000),random.randint(-920,-820),ppick[random.randint(0,len(ppick)-1)]))
projectiles=[]
particles=[]
coins=[]
stars=[]
enemies=[]
clock=pygame.time.Clock()
pls=windw/windh*2
mes=windw/windh*1.8
plsv=6
pv=1.5
tsl=0
tbs=200
tsls=0.
tbls=5000
pscreen=.2
tslh=2000
mtslc=2000
tslc=mtslc
outright,outbottom=0,0
keys=[[K_a,False,pls*-1],[K_d,False,pls],[K_w,False,pls*-1],[K_s,False,pls]]
mouse=[[1,False]]
plyr=player(windw/2,windh/2,20,20,(random.randint(1,255),random.randint(1,255),random.randint(1,255)),pls,100)
camerarect=[[(windw/2-((windw/2)*pscreen)),(windh/2-((windh/2)*pscreen))],[((windw/2)*pscreen)*2,((windh/2)*pscreen)*2]]
cam=camera(camerarect[0][0],camerarect[0][1],camerarect[1][0],camerarect[1][1],windw,windh,outright,outbottom)
animatemenu=[[0,0,False],[0,0,False],[0,0,False],[0,0,False]]
menus=[menu([[[windw/2-((windw/2)*.4),windh/2-((windh/2)*.6)],[((windw/2)*.4)*2,((windh/2)*.6)*2],[100,100,100],[100,100,100],[100,100,100],0,20],
           [[windw/2-((windw/2)*.4),windh/2-((windh/2)*.6)],[((windw/2)*.4)*2,((windh/2)*.6)*2],[150,150,150],[150,150,150],[150,150,150],0,0],
           [[windw/2-((windw/2)*.35),(((windh/2-((windh/2)*.6)+((windh/2)*.6)*2)))-((windh/2)*.1)*4],[((windw/2)*.35)*2,((windh/2)*.1)*2],[255,255,255],[255,255,255],[170,170,170],"EXIT GAME",0],
           [[windw/2-((windw/2)*.35),(windh/2-((windh/2)*.6))+((windh/2)*.1)*2],[((windw/2)*.35)*2,((windh/2)*.1)*2],[255,255,255],[255,255,255],[170,170,170],"RESUME GAME",0]])]
angle=math.radians(270.)
weapons=["SINGLE SQUARE","SPREAD SQUARE","MACHINE SQUARE","EXPLOSIVE SQUARE"]
n=""
cw=0
h=0
hh=0
songf=0
hlf=plyr.health
hl=plyr.health
frames=0
f=0
paused=False
running=True
mainmenu=True
option,high,stat,score=False,False,False,False
mute=False
clicked=False
full=False
while running:
    if not pygame.display.get_active() and not mainmenu and not score:
        paused=True
        menus[0].active=True
        menus[0].anim=[[0,0,False]for x in range(len(menus[0].rects))]
        tp=0
    for event in pygame.event.get():
        if score:
            keystate=pygame.key.get_pressed()
            shift=keystate[K_LSHIFT]
            if event.type==KEYDOWN:
                if event.key in range(97,123) and (shift):
                    n+=chr(event.key-32)
                elif event.key in range(97,123) or event.key==32:
                        n+=chr(event.key)
                elif event.key==K_BACKSPACE:
                    n=n[:-1]
                if event.key==K_RETURN:
                    scores.append([n,plyr.score])
                    tmp=[]
                    for x in range(len(scores)):tmp.append([scores[x][1],str(x)])
                    tmp.sort()
                    tmp2=[]
                    for x in range(len(tmp)):
                        tmp2.append([scores[int(tmp[x][1])][0],tmp[x][0]])
                    scores=tmp2[::-1]
                    keys=[[K_a,False,pls*-1],[K_d,False,pls],[K_w,False,pls*-1],[K_s,False,pls]]
                    mouse=[[1,False]]
                    score=False
                    mainmenu=True
                    n=""
                    plyr=player(windw/2,windh/2,20,20,(random.randint(1,255),random.randint(1,255),random.randint(1,255)),pls,100)
                    enemies=[]
                    outright,outbottom=0,0
                    cam=camera(camerarect[0][0],camerarect[0][1],camerarect[1][0],camerarect[1][1],windw,windh,outright,outbottom)
        if event.type==QUIT:
            running=False
        if mainmenu:
            if event.type == MOUSEBUTTONUP and event.button==1:
                clicked=True
        if event.type==KEYDOWN and not mainmenu and not score:
            for i in range(len(keys)):
                if event.key==keys[i][0]:
                    keys[i][1]=True
            if event.key==K_ESCAPE:
                if paused:paused=False;menus[0].active=False
                else:
                    paused=True;menus[0].active=True
                    menus[0].anim=[[0,0,False]for x in range(len(menus[0].rects))]
                    tp=0
            if event.key in range(49,len(weapons)+49):
                cw=event.key-49
                tslc=mtslc
                tbs=1000
                h=0
        if not mainmenu and not score:
            if event.type==KEYUP:
                for i in range(len(keys)):
                    if event.key==keys[i][0]:
                        keys[i][1]=False
            if event.type==MOUSEBUTTONDOWN:
                for i in range(len(mouse)):
                    if event.button==mouse[i][0]:
                        mouse[i][1]=True
            if event.type==MOUSEBUTTONUP:
                for i in range(len(mouse)):
                    if event.button==mouse[i][0]:
                        mouse[i][1]=False
        else:
            mouse[0][1]=False
    if not paused and not score:
        for i in range(len(keys)):
            if keys[i][1]:
                if i<2:
                    plyr.x+=keys[i][2]
                    movex=keys[i][2]
                elif i>=2:
                    plyr.y+=keys[i][2]
        
        if mouse[0][1] and tsl>=tbs:
            midiout.set_instrument(127)
            midiout.note_on(random.randint(65,68),70)
            stats[0]+=1
            if weapons[cw]=="SINGLE SQUARE":
                tbs=380
                dps=8
                projectiles.append(bullet(aimpos[0]-4/2,aimpos[1]-4/2,9,9,dps,weapons[cw],(random.randint(1,255),random.randint(1,255),random.randint(1,255)),angle,plsv))
            if weapons[cw]=="SPREAD SQUARE":
                tbs=500
                dps=3
                projectiles.append(bullet(aimpos[0]-4/2,aimpos[1]-4/2,5,5,dps,weapons[cw],(random.randint(1,255),random.randint(1,255),random.randint(1,255)),angle,plsv))
                projectiles.append(bullet(aimpos[0]-4/2,aimpos[1]-4/2,5,5,dps,weapons[cw],(random.randint(1,255),random.randint(1,255),random.randint(1,255)),angle-math.radians(random.randint(6,8)),plsv))
                projectiles.append(bullet(aimpos[0]-4/2,aimpos[1]-4/2,5,5,dps,weapons[cw],(random.randint(1,255),random.randint(1,255),random.randint(1,255)),angle+math.radians(random.randint(6,8)),plsv))
            if weapons[cw]=="MACHINE SQUARE":
                tbs=100
                dps=1.4
                projectiles.append(bullet(aimpos[0]-4/2,aimpos[1]-4/2,5,5,dps,weapons[cw],(random.randint(1,255),random.randint(1,255),random.randint(1,255)),angle,plsv))
            if weapons[cw]=="EXPLOSIVE SQUARE":
                tbs=2000
                dps=25.
                projectiles.append(bullet(aimpos[0]-4/2,aimpos[1]-4/2,11,11,dps,weapons[cw],(random.randint(1,255),random.randint(1,255),random.randint(1,255)),angle,0))
            tsl=0.
        if not mainmenu:angle=plyr.angle(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1],plyr.x+plyr.w/2-4/2-outright,plyr.y+plyr.h/2-4/2-outbottom)
        if plyr.alive:
            plyr.update()
            aimpos=plyr.aimerpos(plyr.x+plyr.w/2-4/2,plyr.y+plyr.h/2-4/2,angle)
        else:
            if not mainmenu:score=True
    if score:
        if random.randint(1,100)==2:                                                                                                    #Fireworks
            fx,fy=random.randint(outright,windw+outright),random.randint(outbottom,windh+outbottom)                                     #
            midiout.set_instrument(118)                                                                                                 #
            midiout.note_on(random.randint(100,105),127)                                                                                #
            midiout.note_on(random.randint(100,105),127)                                                                                #            
            midiout.set_instrument(127)                                                                                                 #
            midiout.note_on(random.randint(35,40),127)                                                                                  #
            midiout.note_on(random.randint(35,40),127)                                                                                  #                                                          
            c=(random.randint(2,255),random.randint(2,255),random.randint(2,255))                                                       #
            for y in range(random.randint(40,50)):                                                                                      #
                particles.append(particle(fx,fy,random.uniform(0,math.radians(360)),pv,random.randint(5,8),c,random.randint(100,250)))  #
    if not paused:
        updateplanets()
        updatestars()
        updateproj()
        updateparticles()
    if not paused and not score:
        if plyr.alive:
            detecthit()
            if not mainmenu:outright,outbottom=cam.update()
            updatecoins()
            if tsls>=tbls:
                if len(enemies)<10 and not mainmenu and not score:
                    enemies.append(enemy(random.randint(int(outright)-1000,windw+int(outright)+1000),random.randint(int(outbottom)-1000,windh+int(outbottom)+1000),100,mes+random.uniform(-.75,.5),random.randint(10,100),random.randint(10,100),(random.randint(1,255),random.randint(1,255),random.randint(1,255)),None))
                tsls=0.
                tbls=random.randint(1000,5000)
            if not mainmenu:
                updateenemies()
                collide()
            hl=plyr.health
            if hlf!=hl:
                hlf=hl
                tslh=2000
                hh=0
        if frames>=100:
            if f<len(co)-1:f+=1
            else:f=0
            frames=0
    if paused:running,paused=updatemenus()
    if songf>=380 and not mute:
        midiout.set_instrument(15)
        if not paused:
            note=pitches[random.randint(0,len(pitches)-1)]
            midiout.note_on(note,60)
            note=pitches[random.randint(0,len(pitches)-1)]
            midiout.note_on(note,60)
            note=pitches[random.randint(0,len(pitches)-1)]
            midiout.note_on(note,60)
        else:
            note=pitches[random.randint(0,len(pitches)-1)]
            midiout.note_on(note,40)
            note=pitches[random.randint(0,len(pitches)-1)]
            midiout.note_on(note,40)
            note=pitches[random.randint(0,len(pitches)-1)]
            midiout.note_on(note,40)
        songf=0
    screen.fill((0,0,0))
    drawstars()
    drawplanets()
    drawcoins()
    drawenemies()
    if plyr.alive and not mainmenu:drawplayer()
    drawproj()
    drawparticles()
    if tslc>0 and not mainmenu:
        wep=smallest.render(weapons[cw], 0, (150,150,150))
        cen=wep.get_rect(center=(blittedrect.center))
        if plyr.y-h>plyr.y-40:h+=.4
        screen.blit(wep,(cen[0],plyr.y-h-outbottom))
    if tslh>0 and not mainmenu:
        hel=smallest.render("HP:"+str(plyr.health), 0, (255,0,0))
        cen=hel.get_rect(center=(blittedrect.center))
        if plyr.y+hh<plyr.y+40:hh+=.4
        screen.blit(hel,(cen[0],plyr.y+hh-outbottom))
    if not mainmenu:
        scr=smaller.render("SCORE:"+str(plyr.score), 0, (255,255,0))
        screen.blit(scr,(0,windh-30))
    if mainmenu:
        screen.blit(title,(windw/2-title.get_rect()[2]/2,10))
        srec=pygame.Rect(windw/2-200,windh/2-40,400,80)
        orec=pygame.Rect(windw/2-200,windh/2-40+100,400,80)
        erec=pygame.Rect(windw/2-200,windh/2-40+200,400,80)
        highrec=pygame.Rect(windw/2-210,windh/2-90,200,40)
        statrec=pygame.Rect(windw/2+10,windh/2-90,200,40)
        if not option and not high and not stat:
            if not srec.collidepoint(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]):
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40,400,80))
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40,400,80),5)
            else:
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40,400,80))
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40,400,80),5)
                if clicked:mainmenu=False;stats[3]+=1;plyr=player(windw/2,windh/2,20,20,(random.randint(1,255),random.randint(1,255),random.randint(1,255)),pls,100)
            if not orec.collidepoint(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]):
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40+100,400,80))
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40+100,400,80),5)
            else:
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40+100,400,80))
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40+100,400,80),5)
                if clicked:option=True
            if not erec.collidepoint(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]):
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40+200,400,80))
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40+200,400,80),5)
            else:
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40+200,400,80))
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40+200,400,80),5)
                if clicked:running=False
            if not highrec.collidepoint(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]):
                pygame.draw.rect(screen,(100,100,100),(windw/2-210,windh/2-90,200,40))
                pygame.draw.rect(screen,(60,60,60),(windw/2-210,windh/2-90,200,40),5)
            else:
                pygame.draw.rect(screen,(60,60,60),(windw/2-210,windh/2-90,200,40))
                pygame.draw.rect(screen,(100,100,100),(windw/2-210,windh/2-90,200,40),5)
                if clicked:high=True
                
            if not statrec.collidepoint(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]):
                pygame.draw.rect(screen,(100,100,100),(windw/2+10,windh/2-90,200,40))
                pygame.draw.rect(screen,(60,60,60),(windw/2+10,windh/2-90,200,40),5)
            else:
                pygame.draw.rect(screen,(60,60,60),(windw/2+10,windh/2-90,200,40))
                pygame.draw.rect(screen,(100,100,100),(windw/2+10,windh/2-90,200,40),5)
                if clicked:stat=True
            clicked=False
        elif option:
            if not srec.collidepoint(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]):
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40,400,80))
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40,400,80),5)
            else:
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40,400,80))
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40,400,80),5)
                if clicked:
                    if windw!=maxres[0]:
                        full=True
                        windw,windh=maxres[0],maxres[1]
                        screen=pygame.display.set_mode((windw,windh),pygame.FULLSCREEN,32)
                    else:
                        full=False
                        windw,windh=800,600
                        screen=pygame.display.set_mode((windw,windh),0,32)
                    menus=[menu([[[windw/2-((windw/2)*.4),windh/2-((windh/2)*.6)],[((windw/2)*.4)*2,((windh/2)*.6)*2],[100,100,100],[100,100,100],[100,100,100],0,20],
                                 [[windw/2-((windw/2)*.4),windh/2-((windh/2)*.6)],[((windw/2)*.4)*2,((windh/2)*.6)*2],[150,150,150],[150,150,150],[150,150,150],0,0],
                                 [[windw/2-((windw/2)*.35),(((windh/2-((windh/2)*.6)+((windh/2)*.6)*2)))-((windh/2)*.1)*4],[((windw/2)*.35)*2,((windh/2)*.1)*2],[255,255,255],[255,255,255],[170,170,170],"EXIT GAME",0],
                                 [[windw/2-((windw/2)*.35),(windh/2-((windh/2)*.6))+((windh/2)*.1)*2],[((windw/2)*.35)*2,((windh/2)*.1)*2],[255,255,255],[255,255,255],[170,170,170],"RESUME GAME",0]])]
                    bg=pygame.transform.scale(bg,(windw,windh))
                    camerarect=[[(windw/2-((windw/2)*pscreen)),(windh/2-((windh/2)*pscreen))],[((windw/2)*pscreen)*2,((windh/2)*pscreen)*2]]
                    cam=camera(camerarect[0][0],camerarect[0][1],camerarect[1][0],camerarect[1][1],windw,windh,outright,outbottom)
            if not orec.collidepoint(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]):
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40+100,400,80))
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40+100,400,80),5)
            else:
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40+100,400,80))
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40+100,400,80),5)
                if clicked:
                    if mute:mute=False
                    else:mute=True
            if not erec.collidepoint(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]):
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40+200,400,80))
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40+200,400,80),5)
            else:
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40+200,400,80))
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40+200,400,80),5)
                if clicked:option=False
            clicked=False
        elif high:
            if not erec.collidepoint(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]):
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40+200,400,80))
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40+200,400,80),5)
            else:
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40+200,400,80))
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40+200,400,80),5)
                if clicked:high=False
            clicked=False
        elif stat:
            if not orec.collidepoint(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]):
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40+100,400,80))
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40+100,400,80),5)
            else:
                pygame.draw.rect(screen,(60,60,60),(windw/2-200,windh/2-40+100,400,80))
                pygame.draw.rect(screen,(100,100,100),(windw/2-200,windh/2-40+100,400,80),5)
                if clicked:stat=False
            clicked=False
        if not option and not high and not stat:
            play=menufont.render("PLAY!", 0, (255,255,255))
            options=menufont.render("OPTIONS", 0, (255,255,255))
            exitg=menufont.render("EXIT GAME", 0, (255,255,255))
            highscore=smaller.render("HIGHSCORES", 0, (255,255,255))
            statss=smaller.render("STATS", 0, (255,255,255))
            screen.blit(play,(windw/2-play.get_rect()[2]/2,windh/2-play.get_rect()[3]/2))
            screen.blit(options,(windw/2-options.get_rect()[2]/2,windh/2-options.get_rect()[3]/2+100))
            screen.blit(exitg,(windw/2-exitg.get_rect()[2]/2,windh/2-exitg.get_rect()[3]/2+200))
            screen.blit(highscore,(windw/2-204,windh/2-85))
            screen.blit(statss,(windw/2+60,windh/2-85))
        elif option:
            toggle=menufont.render("TOGGLE FULLSCREEN", 0, (255,255,255))
            mu=menufont.render("MUTE MUSIC: "+str(mute), 0, (255,255,255))
            back=menufont.render("BACK", 0, (255,255,255))
            screen.blit(toggle,(windw/2-toggle.get_rect()[2]/2,windh/2-toggle.get_rect()[3]/2))
            screen.blit(mu,(windw/2-mu.get_rect()[2]/2,windh/2-mu.get_rect()[3]/2+100))
            screen.blit(back,(windw/2-back.get_rect()[2]/2,windh/2-back.get_rect()[3]/2+200))
        elif high:
            back=menufont.render("BACK", 0, (255,255,255))
            players=[]
            c=0
            for i in scores:
                if full:
                    if c<15:
                        players.append(menufont.render(str(c+1)+". "+i[0]+" - "+str(i[1]), 0, (255,255,255)))
                else:
                    if c<8:
                        players.append(menufont.render(str(c+1)+". "+i[0]+" - "+str(i[1]), 0, (255,255,255)))
                c+=1
            back=menufont.render("BACK", 0, (255,255,255))
            screen.blit(back,(windw/2-back.get_rect()[2]/2,windh/2-back.get_rect()[3]/2+200))
            for i in range(len(players)):
                screen.blit(players[i],(windw/2-players[i].get_rect()[2]/2,i*30+200))
        elif stat:
            fired=menufont.render("SHOTS FIRED - "+str(stats[0]), 0, (255,255,255))
            killed=menufont.render("ENEMIES KILLED - "+str(stats[1]), 0, (255,255,255))
            deaths=menufont.render("DEATHS - "+str(stats[2]), 0, (255,255,255))
            plays=menufont.render("TIMES PLAYED - "+str(stats[3]), 0, (255,255,255))
            back=menufont.render("BACK", 0, (255,255,255))
            screen.blit(back,(windw/2-back.get_rect()[2]/2,windh/2-back.get_rect()[3]/2+100))
            screen.blit(fired,(windw/2-fired.get_rect()[2]/2,windh/2-110))
            screen.blit(killed,(windw/2-killed.get_rect()[2]/2,windh/2-70))
            screen.blit(deaths,(windw/2-deaths.get_rect()[2]/2,windh/2-30))
            screen.blit(plays,(windw/2-plays.get_rect()[2]/2,windh/2+10))
    if score:
        over=menufont.render("GAME OVER", 0, (255,255,255))
        name=menufont.render("ENTER YOUR NAME: "+n, 0, (255,255,255))
        scoredisp=menufont.render("SCORE: "+str(plyr.score), 0, (255,255,255))
        screen.blit(over,(windw/2-over.get_rect()[2]/2,windh/2-60))
        screen.blit(name,(windw/2-name.get_rect()[2]/2,windh/2))
        screen.blit(scoredisp,(windw/2-scoredisp.get_rect()[2]/2,windh/2+60))
    if paused:
        screen.blit(bg,(0,0))
        if tp>=2000:tp=0.
        else:tp+=mili
        drawmenus()
    pygame.display.update(pygame.Rect(0, 0, windw, windh))
    mili=clock.tick(200)
    tsl+=mili
    tsls+=mili
    tslh-=mili
    tslc-=mili
    frames+=mili
    if not mute:songf+=mili
pygame.quit()
pygame.midi.quit()
statfile=open("bin/textfiles/stats.txt","w")
for x in range(len(stats)):
    if x<len(stats)-1:statfile.write(str(stats[x])+"\n")
    else:statfile.write(str(stats[x]))
statfile.close()
scorefile=open("bin/textfiles/scores.txt","w")
for x in range(len(scores)):
    if x<len(scores)-1:scorefile.write(scores[x][0]+"|"+str(scores[x][1])+"\n")
    else:scorefile.write(scores[x][0]+"|"+str(scores[x][1]))
scorefile.close()
