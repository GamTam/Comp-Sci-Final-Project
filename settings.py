import pygame as pg
import math
from moviepy.editor import *

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

textboxSprites = {"dialogue": pg.image.load("sprites/textbox.png")}

fadeout = pg.image.load("sprites/fadeout.png").convert_alpha()
