import pygame as pg
import random
from Libraries import ptext
import math
from moviepy.editor import *

ptext.DEFAULT_COLOR = "black"
ptext.DEFAULT_COLOR_TAG = {
    ">>": None,
    "<<R": (255, 0, 0),
    "<<B": (0, 0, 255),
    "<<G": (0, 225, 0),
    "/C": None,
    "/B": None,
    "/S": None
}

width = 1280
height = 720

icon = pg.image.load("sprites/icon.png")

fps = 60
title = "Super Mario & Luigi"
dialogueFont = 'fonts/PMF.otf'
superMario256 = "fonts/SuperMario256.ttf"
expNumbers = "fonts/expnumbers.ttf"

playerSpeed = 5
jumpHeight = 11
airTime = 3

white = (255, 255, 255)
black = (0, 0, 0)
darkGray = (50, 50, 50)
red = (255, 0, 0)
green = (0, 225, 0)
purple = (255, 0, 255)
blue = (0, 0, 255)
yellow = (225, 225, 0)
lightBlue = (0, 155, 155)
sansEye = (132, 255, 242)

pg.display.set_icon(icon)
pg.mixer.pre_init(44100, -16, 2, 2048)
pg.init()
pg.display.set_caption(title)
screen = pg.display.set_mode((width, height))

battleTransitionSprites = [pg.image.load("sprites/battle intro/battle_transition_1.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_2.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_3.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_4.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_5.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_6.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_7.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_8.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_9.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_10.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_11.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_12.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_13.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_14.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_15.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_16.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_17.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_18.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_19.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_20.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_21.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_22.png").convert_alpha(),
                           pg.image.load("sprites/battle intro/battle_transition_23.png").convert_alpha()]

talkAdvanceSprite = pg.image.load("sprites/textboxadvance.png").convert_alpha()
mushroomSprite = pg.image.load("sprites/item icons/mushroom.png").convert_alpha()
oneUpSprite = pg.image.load("sprites/item icons/1-UP.png").convert_alpha()
NutSprite = pg.image.load("sprites/item icons/Nut.png").convert_alpha()
syrupSprite = pg.image.load("sprites/item icons/syrup.png").convert_alpha()
candySprite = pg.image.load("sprites/item icons/star candy.png").convert_alpha()
hpSprite = pg.image.load("sprites/item icons/hpIcon.png").convert_alpha()
bpSprite = pg.image.load("sprites/item icons/bpIcon.png").convert_alpha()
powSprite = pg.image.load("sprites/item icons/powIcon.png").convert_alpha()
defSprite = pg.image.load("sprites/item icons/defIcon.png").convert_alpha()

textboxSprites = {"dialogue": pg.image.load("sprites/textbox.png").convert_alpha(),
                  "board": pg.image.load("sprites/boardTextBox.png").convert_alpha()}

voidSprites = [pg.image.load("sprites/the void/1.png").convert_alpha(),
               pg.image.load("sprites/the void/2.png").convert_alpha(),
               pg.image.load("sprites/the void/3.png").convert_alpha(),
               pg.image.load("sprites/the void/4.png").convert_alpha(),
               pg.image.load("sprites/the void/5.png").convert_alpha(),
               pg.image.load("sprites/the void/6.png").convert_alpha(),
               pg.image.load("sprites/the void/7.png").convert_alpha(),
               pg.image.load("sprites/the void/8.png").convert_alpha(),
               pg.image.load("sprites/the void/9.png").convert_alpha(),
               pg.image.load("sprites/the void/10.png").convert_alpha(),
               pg.image.load("sprites/the void/11.png").convert_alpha(),
               pg.image.load("sprites/the void/12.png").convert_alpha(),
               pg.image.load("sprites/the void/13.png").convert_alpha(),
               pg.image.load("sprites/the void/14.png").convert_alpha(),
               pg.image.load("sprites/the void/15.png").convert_alpha(),
               pg.image.load("sprites/the void/16.png").convert_alpha(),
               pg.image.load("sprites/the void/17.png").convert_alpha(),
               pg.image.load("sprites/the void/18.png").convert_alpha(),
               pg.image.load("sprites/the void/19.png").convert_alpha(),
               pg.image.load("sprites/the void/20.png").convert_alpha(),
               pg.image.load("sprites/the void/21.png").convert_alpha(),
               pg.image.load("sprites/the void/22.png").convert_alpha(),
               pg.image.load("sprites/the void/23.png").convert_alpha(),
               pg.image.load("sprites/the void/24.png").convert_alpha(),
               pg.image.load("sprites/the void/25.png").convert_alpha(),
               pg.image.load("sprites/the void/26.png").convert_alpha(),
               pg.image.load("sprites/the void/27.png").convert_alpha(),
               pg.image.load("sprites/the void/28.png").convert_alpha(),
               pg.image.load("sprites/the void/29.png").convert_alpha(),
               pg.image.load("sprites/the void/30.png").convert_alpha(),
               pg.image.load("sprites/the void/31.png").convert_alpha(),
               pg.image.load("sprites/the void/32.png").convert_alpha(),
               pg.image.load("sprites/the void/33.png").convert_alpha(),
               pg.image.load("sprites/the void/34.png").convert_alpha(),
               pg.image.load("sprites/the void/35.png").convert_alpha(),
               pg.image.load("sprites/the void/36.png").convert_alpha(),
               pg.image.load("sprites/the void/37.png").convert_alpha(),
               pg.image.load("sprites/the void/38.png").convert_alpha(),
               pg.image.load("sprites/the void/39.png").convert_alpha(),
               pg.image.load("sprites/the void/40.png").convert_alpha(),
               pg.image.load("sprites/the void/41.png").convert_alpha(),
               pg.image.load("sprites/the void/42.png").convert_alpha(),
               pg.image.load("sprites/the void/43.png").convert_alpha(),
               pg.image.load("sprites/the void/44.png").convert_alpha(),
               pg.image.load("sprites/the void/45.png").convert_alpha(),
               pg.image.load("sprites/the void/46.png").convert_alpha(),
               pg.image.load("sprites/the void/47.png").convert_alpha(),
               pg.image.load("sprites/the void/48.png").convert_alpha(),
               pg.image.load("sprites/the void/49.png").convert_alpha(),
               pg.image.load("sprites/the void/50.png").convert_alpha(),
               pg.image.load("sprites/the void/51.png").convert_alpha(),
               pg.image.load("sprites/the void/52.png").convert_alpha(),
               pg.image.load("sprites/the void/53.png").convert_alpha(),
               pg.image.load("sprites/the void/54.png").convert_alpha(),
               pg.image.load("sprites/the void/55.png").convert_alpha(),
               pg.image.load("sprites/the void/56.png").convert_alpha(),
               pg.image.load("sprites/the void/57.png").convert_alpha(),
               pg.image.load("sprites/the void/58.png").convert_alpha(),
               pg.image.load("sprites/the void/59.png").convert_alpha(),
               pg.image.load("sprites/the void/60.png").convert_alpha(),
               pg.image.load("sprites/the void/61.png").convert_alpha(),
               pg.image.load("sprites/the void/62.png").convert_alpha(),
               pg.image.load("sprites/the void/63.png").convert_alpha(),
               pg.image.load("sprites/the void/64.png").convert_alpha(),
               pg.image.load("sprites/the void/65.png").convert_alpha(),
               pg.image.load("sprites/the void/66.png").convert_alpha(),
               pg.image.load("sprites/the void/67.png").convert_alpha(),
               pg.image.load("sprites/the void/68.png").convert_alpha(),
               pg.image.load("sprites/the void/69.png").convert_alpha(),
               pg.image.load("sprites/the void/70.png").convert_alpha(),
               pg.image.load("sprites/the void/71.png").convert_alpha(),
               pg.image.load("sprites/the void/72.png").convert_alpha(),
               pg.image.load("sprites/the void/73.png").convert_alpha(),
               pg.image.load("sprites/the void/74.png").convert_alpha(),
               pg.image.load("sprites/the void/75.png").convert_alpha(),
               pg.image.load("sprites/the void/76.png").convert_alpha(),
               pg.image.load("sprites/the void/77.png").convert_alpha(),
               pg.image.load("sprites/the void/78.png").convert_alpha(),
               pg.image.load("sprites/the void/79.png").convert_alpha(),
               pg.image.load("sprites/the void/80.png").convert_alpha(),
               pg.image.load("sprites/the void/81.png").convert_alpha(),
               pg.image.load("sprites/the void/82.png").convert_alpha(),
               pg.image.load("sprites/the void/83.png").convert_alpha(),
               pg.image.load("sprites/the void/84.png").convert_alpha(),
               pg.image.load("sprites/the void/85.png").convert_alpha(),
               pg.image.load("sprites/the void/86.png").convert_alpha(),
               pg.image.load("sprites/the void/87.png").convert_alpha(),
               pg.image.load("sprites/the void/88.png").convert_alpha(),
               pg.image.load("sprites/the void/89.png").convert_alpha(),
               pg.image.load("sprites/the void/90.png").convert_alpha(),
               pg.image.load("sprites/the void/91.png").convert_alpha(),
               pg.image.load("sprites/the void/92.png").convert_alpha(),
               pg.image.load("sprites/the void/93.png").convert_alpha(),
               pg.image.load("sprites/the void/94.png").convert_alpha(),
               pg.image.load("sprites/the void/95.png").convert_alpha(),
               pg.image.load("sprites/the void/96.png").convert_alpha(),
               pg.image.load("sprites/the void/97.png").convert_alpha(),
               pg.image.load("sprites/the void/98.png").convert_alpha(),
               pg.image.load("sprites/the void/99.png").convert_alpha(),
               pg.image.load("sprites/the void/100.png").convert_alpha(),
               pg.image.load("sprites/the void/101.png").convert_alpha(),
               pg.image.load("sprites/the void/102.png").convert_alpha(),
               pg.image.load("sprites/the void/103.png").convert_alpha(),
               pg.image.load("sprites/the void/104.png").convert_alpha(),
               pg.image.load("sprites/the void/105.png").convert_alpha(),
               pg.image.load("sprites/the void/106.png").convert_alpha(),
               pg.image.load("sprites/the void/107.png").convert_alpha(),
               pg.image.load("sprites/the void/108.png").convert_alpha(),
               pg.image.load("sprites/the void/109.png").convert_alpha(),
               pg.image.load("sprites/the void/110.png").convert_alpha(),
               pg.image.load("sprites/the void/111.png").convert_alpha(),
               pg.image.load("sprites/the void/112.png").convert_alpha(),
               pg.image.load("sprites/the void/113.png").convert_alpha(),
               pg.image.load("sprites/the void/114.png").convert_alpha(),
               pg.image.load("sprites/the void/115.png").convert_alpha(),
               pg.image.load("sprites/the void/116.png").convert_alpha(),
               pg.image.load("sprites/the void/117.png").convert_alpha(),
               pg.image.load("sprites/the void/118.png").convert_alpha(),
               pg.image.load("sprites/the void/119.png").convert_alpha(),
               pg.image.load("sprites/the void/120.png").convert_alpha(),
               pg.image.load("sprites/the void/121.png").convert_alpha(),
               pg.image.load("sprites/the void/122.png").convert_alpha(),
               pg.image.load("sprites/the void/123.png").convert_alpha(),
               pg.image.load("sprites/the void/124.png").convert_alpha(),
               pg.image.load("sprites/the void/125.png").convert_alpha(),
               pg.image.load("sprites/the void/126.png").convert_alpha(),
               pg.image.load("sprites/the void/127.png").convert_alpha(),
               pg.image.load("sprites/the void/128.png").convert_alpha(),
               pg.image.load("sprites/the void/129.png").convert_alpha(),
               pg.image.load("sprites/the void/130.png").convert_alpha(),
               pg.image.load("sprites/the void/131.png").convert_alpha(),
               pg.image.load("sprites/the void/132.png").convert_alpha(),
               pg.image.load("sprites/the void/133.png").convert_alpha(),
               pg.image.load("sprites/the void/134.png").convert_alpha(),
               pg.image.load("sprites/the void/135.png").convert_alpha(),
               pg.image.load("sprites/the void/136.png").convert_alpha(),
               pg.image.load("sprites/the void/137.png").convert_alpha(),
               pg.image.load("sprites/the void/138.png").convert_alpha(),
               pg.image.load("sprites/the void/139.png").convert_alpha(),
               pg.image.load("sprites/the void/140.png").convert_alpha(),
               pg.image.load("sprites/the void/141.png").convert_alpha(),
               pg.image.load("sprites/the void/142.png").convert_alpha(),
               pg.image.load("sprites/the void/143.png").convert_alpha(),
               pg.image.load("sprites/the void/144.png").convert_alpha(),
               pg.image.load("sprites/the void/145.png").convert_alpha(),
               pg.image.load("sprites/the void/146.png").convert_alpha(),
               pg.image.load("sprites/the void/147.png").convert_alpha(),
               pg.image.load("sprites/the void/148.png").convert_alpha(),
               pg.image.load("sprites/the void/149.png").convert_alpha(),
               pg.image.load("sprites/the void/150.png").convert_alpha(),
               pg.image.load("sprites/the void/151.png").convert_alpha(),
               pg.image.load("sprites/the void/152.png").convert_alpha(),
               pg.image.load("sprites/the void/153.png").convert_alpha(),
               pg.image.load("sprites/the void/154.png").convert_alpha(),
               pg.image.load("sprites/the void/155.png").convert_alpha(),
               pg.image.load("sprites/the void/156.png").convert_alpha(),
               pg.image.load("sprites/the void/157.png").convert_alpha(),
               pg.image.load("sprites/the void/158.png").convert_alpha(),
               pg.image.load("sprites/the void/159.png").convert_alpha(),
               pg.image.load("sprites/the void/160.png").convert_alpha(),
               pg.image.load("sprites/the void/161.png").convert_alpha(),
               pg.image.load("sprites/the void/162.png").convert_alpha(),
               pg.image.load("sprites/the void/163.png").convert_alpha(),
               pg.image.load("sprites/the void/164.png").convert_alpha(),
               pg.image.load("sprites/the void/165.png").convert_alpha(),
               pg.image.load("sprites/the void/166.png").convert_alpha(),
               pg.image.load("sprites/the void/167.png").convert_alpha(),
               pg.image.load("sprites/the void/168.png").convert_alpha(),
               pg.image.load("sprites/the void/169.png").convert_alpha(),
               pg.image.load("sprites/the void/170.png").convert_alpha(),
               pg.image.load("sprites/the void/171.png").convert_alpha(),
               pg.image.load("sprites/the void/172.png").convert_alpha(),
               pg.image.load("sprites/the void/173.png").convert_alpha(),
               pg.image.load("sprites/the void/174.png").convert_alpha(),
               pg.image.load("sprites/the void/175.png").convert_alpha(),
               pg.image.load("sprites/the void/176.png").convert_alpha(),
               pg.image.load("sprites/the void/177.png").convert_alpha(),
               pg.image.load("sprites/the void/178.png").convert_alpha(),
               pg.image.load("sprites/the void/179.png").convert_alpha(),
               pg.image.load("sprites/the void/180.png").convert_alpha(),
               pg.image.load("sprites/the void/181.png").convert_alpha(),
               pg.image.load("sprites/the void/182.png").convert_alpha(),
               pg.image.load("sprites/the void/183.png").convert_alpha(),
               pg.image.load("sprites/the void/184.png").convert_alpha(),
               pg.image.load("sprites/the void/185.png").convert_alpha(),
               pg.image.load("sprites/the void/186.png").convert_alpha(),
               pg.image.load("sprites/the void/187.png").convert_alpha(),
               pg.image.load("sprites/the void/188.png").convert_alpha(),
               pg.image.load("sprites/the void/189.png").convert_alpha(),
               pg.image.load("sprites/the void/190.png").convert_alpha(),
               pg.image.load("sprites/the void/191.png").convert_alpha(),
               pg.image.load("sprites/the void/192.png").convert_alpha(),
               pg.image.load("sprites/the void/193.png").convert_alpha(),
               pg.image.load("sprites/the void/194.png").convert_alpha(),
               pg.image.load("sprites/the void/195.png").convert_alpha(),
               pg.image.load("sprites/the void/196.png").convert_alpha(),
               pg.image.load("sprites/the void/197.png").convert_alpha(),
               pg.image.load("sprites/the void/198.png").convert_alpha(),
               pg.image.load("sprites/the void/199.png").convert_alpha(),
               pg.image.load("sprites/the void/200.png").convert_alpha(),
               pg.image.load("sprites/the void/201.png").convert_alpha(),
               pg.image.load("sprites/the void/202.png").convert_alpha(),
               pg.image.load("sprites/the void/203.png").convert_alpha(),
               pg.image.load("sprites/the void/204.png").convert_alpha(),
               pg.image.load("sprites/the void/205.png").convert_alpha(),
               pg.image.load("sprites/the void/206.png").convert_alpha(),
               pg.image.load("sprites/the void/207.png").convert_alpha(),
               pg.image.load("sprites/the void/208.png").convert_alpha(),
               pg.image.load("sprites/the void/209.png").convert_alpha(),
               pg.image.load("sprites/the void/210.png").convert_alpha(),
               pg.image.load("sprites/the void/211.png").convert_alpha(),
               pg.image.load("sprites/the void/212.png").convert_alpha(),
               pg.image.load("sprites/the void/213.png").convert_alpha(),
               pg.image.load("sprites/the void/214.png").convert_alpha(),
               pg.image.load("sprites/the void/215.png").convert_alpha(),
               pg.image.load("sprites/the void/216.png").convert_alpha(),
               pg.image.load("sprites/the void/217.png").convert_alpha(),
               pg.image.load("sprites/the void/218.png").convert_alpha(),
               pg.image.load("sprites/the void/219.png").convert_alpha(),
               pg.image.load("sprites/the void/220.png").convert_alpha(),
               pg.image.load("sprites/the void/221.png").convert_alpha(),
               pg.image.load("sprites/the void/222.png").convert_alpha(),
               pg.image.load("sprites/the void/223.png").convert_alpha(),
               pg.image.load("sprites/the void/224.png").convert_alpha(),
               pg.image.load("sprites/the void/225.png").convert_alpha(),
               pg.image.load("sprites/the void/226.png").convert_alpha(),
               pg.image.load("sprites/the void/227.png").convert_alpha(),
               pg.image.load("sprites/the void/228.png").convert_alpha(),
               pg.image.load("sprites/the void/229.png").convert_alpha(),
               pg.image.load("sprites/the void/230.png").convert_alpha(),
               pg.image.load("sprites/the void/231.png").convert_alpha(),
               pg.image.load("sprites/the void/232.png").convert_alpha(),
               pg.image.load("sprites/the void/233.png").convert_alpha(),
               pg.image.load("sprites/the void/234.png").convert_alpha(),
               pg.image.load("sprites/the void/235.png").convert_alpha(),
               pg.image.load("sprites/the void/236.png").convert_alpha(),
               pg.image.load("sprites/the void/237.png").convert_alpha(),
               pg.image.load("sprites/the void/238.png").convert_alpha(),
               pg.image.load("sprites/the void/239.png").convert_alpha()]

pg.event.clear()


def randomNumber(max):
    return random.randint(1, max)


def nor(a, b):
    return not (a or b)
