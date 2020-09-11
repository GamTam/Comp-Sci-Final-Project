import random
import os
import pygame as pg

from Libraries import ptext

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
sansFont = "fonts/Comic Sans.ttf"
undertaleFont = "fonts/determinationMono.otf"

playerSpeed = 5
jumpHeight = 11
airTime = 3

white = (255, 255, 255)
black = (0, 0, 0)
darkGray = (50, 50, 50)
gray = (125, 125, 125)
red = (255, 0, 0)
green = (0, 225, 0)
purple = (255, 0, 255)
blue = (0, 0, 255)
yellow = (225, 225, 0)
lightBlue = (0, 155, 155)
sansEye = (132, 255, 242)

pg.display.set_icon(icon)
pg.mixer.init(44100, -16, 2, 64)
pg.init()
pg.display.set_caption(title)
screen = pg.display.set_mode((width, height), pg.DOUBLEBUF)

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
                  "board": pg.image.load("sprites/boardTextBox.png").convert_alpha(),
                  "undertale": pg.image.load("sprites/undertaleTextBox.png").convert_alpha()}

voidSprites = []

angle = 0
angledir = True
clock = pg.time.Clock()

updateRects = [pg.rect.Rect(0, 0, round(width / 2), round(height / 2)),
               pg.rect.Rect(round(width / 2), 0, round(width / 2), round(height / 2)),
               pg.rect.Rect(0, round(height / 2), round(width / 2), round(height / 2)),
               pg.rect.Rect(round(width / 2), round(height / 2), round(width / 2), round(height / 2)),
              ]

for i in range(len(os.listdir("sprites/the void/")) - 1):
    clock.tick(fps)
    voidSprites.append(pg.image.load("sprites/the void/{}.png".format(i + 1)).convert_alpha())

    for event in pg.event.get():
        keys = pg.key.get_pressed()
        if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
            pg.quit()

    if abs(angle) >= 30:
        angledir = not angledir

    if angledir:
        angle += 2
    else:
        angle -= 2

    star = pg.transform.rotate(talkAdvanceSprite, angle)
    starRect = star.get_rect()
    starRect.center = (width - 50, height - 50)

    screen.fill(black)

    screen.blit(star, starRect)

    pg.display.flip()

voidSpot = (width / 2, 100)

lightningSprites = []

for i in range(len(os.listdir("sprites/lightning/")) - 1):
    clock.tick(fps)
    lightningSprites.append(pg.image.load("sprites/lightning/{}.png".format(i + 1)).convert_alpha())

    for event in pg.event.get():
        keys = pg.key.get_pressed()
        if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
            pg.quit()

    if abs(angle) >= 30:
        angledir = not angledir

    if angledir:
        angle += 2
    else:
        angle -= 2

    star = pg.transform.rotate(talkAdvanceSprite, angle)
    starRect = star.get_rect()
    starRect.center = (width - 50, height - 50)

    screen.fill(black)

    screen.blit(star, starRect)

    pg.display.flip()

pg.event.clear()

pg.display.init()
pg.display.set_icon(icon)
pg.display.set_caption(title)


def randomNumber(max, min=1):
    return random.randint(min, max)


def nor(a, b):
    return not (a or b)


def luigiLevelFormula(game):
    exponent = 1.499
    baseXp = 8
    return round(baseXp * (game.follower.stats["level"] ** exponent))


def marioLevelFormula(game):
    exponent = 1.5
    baseXp = 7
    return round(baseXp * (game.player.stats["level"] ** exponent))
