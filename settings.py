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
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
lightBlue = (0, 155, 155)
sansEye = (132, 255, 242)

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

textboxSprites = {"dialogue": pg.image.load("sprites/textbox.png"),
                  "board": pg.image.load("sprites/boardTextBox.png")}


def randomNumber(max):
    return random.randint(1, max)


def nor(a, b):
    return not (a or b)
