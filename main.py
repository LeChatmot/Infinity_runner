from re import A
from socket import socket
from kandinsky import display
import time
import pygame as pg
import numpy as np
from numba import njit

"""

methode njit : ~30 fps <== choisi avec un resolution a 4

methode opti numpy : ~20 fps

methode opti numpy + njit : ERROR

place :

1 :             4 : 

2 :             5 : 

3 :             6 : 

"""

class Car(pg.sprite.Sprite):

    def __init__(self,file_menu,sprite_back,Right,Left,size):
        super().__init__()

        self.velocity = 0

        self.image_menu = pg.image.load(file_menu).convert()
        self.back = pg.image.load(sprite_back).convert()
        self.rect = (self.back.get_width()*size,self.back.get_height()*size)
        self.back = pg.transform.scale(self.back,self.rect)

        self.img_R = pg.image.load(Right).convert_alpha()
        self.img_R = pg.transform.scale(self.img_R,self.rect)

        self.img_L = pg.image.load(Left).convert_alpha()
        self.img_L = pg.transform.scale(self.img_L,self.rect)

        self.sprite = self.back.copy()
        
def connection(socket,host,Nom_partie):
    port = 15555

    try:
        socket.connect((host, port))
        #connect

        #creation envoie
        data = Nom_partie
        data = data.encode("utf8")

        #envoie
        socket.sendall(data)

    except ConnectionRefusedError:
        print("connection échouée")

    finally:
        socket.close()



def menu(player):
    pg.init()
    
    color_list = []
    
    bg = pg.image.load('sprites/Sky.png')

    screen = pg.display.set_mode((bg.get_width(),bg.get_height()))

    font = pg.font.Font(None,40)

    button = pg.image.load("sprites/button.png")
    button = pg.transform.scale(button,(button.get_width()*4,button.get_height()*4))
    button_clicked = False
    
    arrowR = pg.image.load("sprites/arrowR.png")
    arrowR = pg.transform.scale(arrowR,(arrowR.get_width()*4,arrowR.get_height()*4))
    arrowR.set_colorkey((255,255,255))
    arrowR_pressed = False
    
    arrowL = pg.image.load("sprites/arrowL.png")
    arrowL = pg.transform.scale(arrowL,(arrowL.get_width()*4,arrowL.get_height()*4))
    arrowL.set_colorkey((255,255,255))
    arrowL_pressed = False

    text = font.render("Infinit Racer",1,(0,0,0))

    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.blit(bg,(0,0))

        screen.blit(button,((bg.get_width()/2-(button.get_width()/2),bg.get_height()/2-(button.get_height()/2))))
        
        screen.blit(arrowR,(((bg.get_width()/4)*3)-(arrowR.get_width()/2),(bg.get_height()/4)*3-(arrowR.get_height()/2)))
        
        screen.blit(arrowL,((bg.get_width()/4)-(arrowL.get_width()/2),((bg.get_height()/4)*3)-(arrowL.get_height()/2)))

        screen.blit(text,(bg.get_width()/2-(text.get_width()/2),bg.get_height()/4-(text.get_height()/2)))

        pos =  pg.mouse.get_pos()

        button_rect = button.get_rect()
        button_rect.topleft = ((bg.get_width()/2-(button.get_width()/2),bg.get_height()/2-(button.get_height()/2)))

        if button_rect.collidepoint(pos):
            if pg.mouse.get_pressed()[0] == 1 and button_clicked == False:
                button_clicked = True
                pg.quit()
                main(player)

        if pg.mouse.get_pressed()[0] == 0:
            button_clicked = False

        pg.display.update()

    pg.quit()



def main(player):
    f = time.monotonic()

    pg.init()
    screen = pg.display.set_mode((0,0),pg.FULLSCREEN)
    running = True
    clock = pg.time.Clock()

    pg.mouse.set_visible(False)

    resolution = 3
    size_map = 35

    maxcoo = 54
    minicoo = 1

    nbcases = 55

    rotate_speed = 0.002
    move_speed = 0.008

    hres = int(screen.get_width()/resolution) #horizontal resolution
    halfvres = int((screen.get_height()/resolution)/2) # vertical resolution /2

    mod = hres/60
    posx, posy, rot = 51,39.3,-1.57

    sky = pg.image.load('sprites/fond.png')
    #tableau 3d de couleur de l'image
    sky = pg.surfarray.array3d(pg.transform.scale(sky,(360,halfvres*2)))
    #tableau 3d de couleur de l'image
    floor = pg.surfarray.array3d(pg.image.load('sprites/Circuit.png'))

    map = pg.image.load('sprites/Circuit.png')
    map = pg.transform.scale(map,(map.get_width()/nbcases*size_map,map.get_height()/nbcases*size_map))
    rec_map = (map.get_width(),map.get_height())

    icon = pg.image.load("sprites/icon.png")

    font = pg.font.Font(None,200)

    shade = 0.4 + 0.6*(np.linspace(0, halfvres, halfvres)/halfvres)
    shade = np.dstack((shade, shade, shade))

    frame = np.ones([hres, halfvres*2, 3])

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        frame = new_frame(posx,posy,rot,frame,sky,floor,shade,hres,halfvres,mod,nbcases)

        surface = pg.surfarray.make_surface(frame*255)
        surface = pg.transform.scale(surface, (screen.get_width(),screen.get_height()))

        fps = int(clock.get_fps())

        score = int((time.monotonic()-f)//0.8)
        
        texte = font.render("score : "+str(score),1,(0,0,0))

        #hotbar
        pg.display.set_caption("Infinit Racer / fps: "+str(fps))
        pg.display.set_icon(icon)
        #screen
        screen.blit(surface, (0,0))
        screen.blit(map,(0,0))
        screen.blit(texte,(screen.get_width()-texte.get_width(),0))
        
        size_carree = 4
        
        pg.draw.rect(screen,(0,255,0),((((posx)*rec_map[0])-size_carree//2)//nbcases,(((posy)*rec_map[1])-size_carree//2)//nbcases,size_carree,size_carree))
        
        player.sprite.set_colorkey((255,255,255))

        screen.blit(player.sprite,(int(screen.get_width()/2-(player.sprite.get_width()/2)),int(screen.get_height()/4)*3-(player.sprite.get_height()/4)))
        pg.display.update()

        posx,posy,rot = movement(posx,posy,rot,pg.key.get_pressed(), clock.tick(),maxcoo,minicoo,rotate_speed,move_speed,player)

def movement(posx,posy,rot,keys,et,max,mini,rotate,speed,player):
    #mouvement de caméra
    if (keys[pg.K_UP] or keys[ord('z')]) and posx + np.cos(rot)*speed*et <=max and posx + np.cos(rot)*speed*et >=mini and posy + np.sin(rot)*speed*et <=max and posy + np.sin(rot)*speed*et >=mini:
        posx, posy = posx + np.cos(rot)*speed*et, posy + np.sin(rot)*speed*et
        player.sprite = player.back.copy()

    if (keys[pg.K_DOWN] or keys[ord('s')]) and posx - np.cos(rot)*speed*et <=max and posx - np.cos(rot)*speed*et >=mini and posy - np.sin(rot)*speed*et <=max and posy - np.sin(rot)*speed*et >=mini:
        posx, posy = posx - np.cos(rot)*speed*et, posy - np.sin(rot)*speed*et
        player.sprite = player.back.copy()

    if keys[pg.K_LEFT] or keys[ord('q')]:
        rot -= rotate*et
        player.sprite = player.img_L.copy()

    if keys[pg.K_RIGHT] or keys[ord('d')]:
        rot += rotate*et
        player.sprite = player.img_R.copy()

    if keys[ord('p')]:
        print(str(posx)+" "+str(posy)+" "+str(rot))
    return posx,posy,rot

@njit()
def new_frame(posx,posy,rot,frame,sky,floor,shade,hres,halfvres,mod,max):
    #boucle sur la resolution
    for i in range(hres):
            rot_i = rot + np.deg2rad(i/mod - 30)
            sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i/mod - 30))
            frame[i][:] = sky[int(np.rad2deg(rot_i)%359)][:]/255
            for j in range(halfvres):
                n = (halfvres/(halfvres-j))/cos2
                x,y = posx + cos*n, posy + sin*n
                xx,yy = int(x/max%1*600),int(y/max%1*600)

                shade = 0.4 + 0.8*(1-j/halfvres)

                frame[i][halfvres*2-1-j] = shade*floor[xx][yy]/255

    return frame

if __name__ == '__main__':
    player = Car("sprites/BlueCar.png","sprites/BlueCarBack.png","sprites/BlueCarRight.png","sprites/BlueCarLeft.png",20)
    menu(player)
    pg.quit()
    exit()