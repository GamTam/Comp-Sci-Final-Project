import xml.etree.ElementTree as ET
import pygame as pg
from settings import *


class spritesheet:
    def __init__(self, img_file, data_file=None):
        self.spritesheet = pg.image.load(img_file).convert_alpha()
        if data_file:
            tree = ET.parse(data_file)
            self.map = {}
            for node in tree.iter():
                if node.attrib.get('n'):
                    name = node.attrib.get('n')
                    self.map[name] = {}
                    self.map[name]['x'] = int(node.attrib.get('x'))
                    self.map[name]['y'] = int(node.attrib.get('y'))
                    self.map[name]['w'] = int(node.attrib.get('w'))
                    self.map[name]['h'] = int(node.attrib.get('h'))

    def get_image_rect(self, x, y, w, h):
        return self.spritesheet.subsurface(pg.Rect(x, y, w, h))

    def getImageName(self, name):
        rect = pg.Rect(self.map[name]['x'], self.map[name]['y'], self.map[name]['w'], self.map[name]['h'])
        return self.spritesheet.subsurface(rect)


class MarioUI(pg.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.ui
        pg.sprite.Sprite.__init__(self, self.groups)
        sheet = spritesheet("sprites/ui.png", "sprites/ui.xml")
        self.game = game
        self.numbers = [sheet.getImageName("0_hp.png"),
                        sheet.getImageName("1_hp.png"),
                        sheet.getImageName("2_hp.png"),
                        sheet.getImageName("3_hp.png"),
                        sheet.getImageName("4_hp.png"),
                        sheet.getImageName("5_hp.png"),
                        sheet.getImageName("6_hp.png"),
                        sheet.getImageName("7_hp.png"),
                        sheet.getImageName("8_hp.png"),
                        sheet.getImageName("9_hp.png")]
        self.sprites = [pg.image.load("sprites/MarioUI.png")]
        self.image = self.sprites[0]
        self.rect = self.image.get_rect()
        self.rect.left = 0
        self.rect.top = 0

    def update(self):
        self.hp = [int(i) for i in str(self.game.player.stats["hp"])]

        if len(self.hp) == 1:
            if self.hp[0] == 0:
                self.numberImg = self.numbers[0]
            elif self.hp[0] == 1:
                self.numberImg = self.numbers[1]
            elif self.hp[0] == 2:
                self.numberImg = self.numbers[2]
            elif self.hp[0] == 3:
                self.numberImg = self.numbers[3]
            elif self.hp[0] == 4:
                self.numberImg = self.numbers[4]
            elif self.hp[0] == 5:
                self.numberImg = self.numbers[5]
            elif self.hp[0] == 6:
                self.numberImg = self.numbers[6]
            elif self.hp[0] == 7:
                self.numberImg = self.numbers[7]
            elif self.hp[0] == 8:
                self.numberImg = self.numbers[8]
            elif self.hp[0] == 9:
                self.numberImg = self.numbers[9]

            self.numberRect = self.numberImg.get_rect()
            self.numberRect.right = self.rect.right - 70
            self.numberRect.centery = self.rect.bottom - 25
        elif len(self.hp) == 2:
            if self.hp[0] == 0:
                self.numberImg1 = self.numbers[0]
            elif self.hp[0] == 1:
                self.numberImg1 = self.numbers[1]
            elif self.hp[0] == 2:
                self.numberImg1 = self.numbers[2]
            elif self.hp[0] == 3:
                self.numberImg1 = self.numbers[3]
            elif self.hp[0] == 4:
                self.numberImg1 = self.numbers[4]
            elif self.hp[0] == 5:
                self.numberImg1 = self.numbers[5]
            elif self.hp[0] == 6:
                self.numberImg1 = self.numbers[6]
            elif self.hp[0] == 7:
                self.numberImg1 = self.numbers[7]
            elif self.hp[0] == 8:
                self.numberImg1 = self.numbers[8]
            elif self.hp[0] == 9:
                self.numberImg1 = self.numbers[9]

            if self.hp[1] == 0:
                self.numberImg2 = self.numbers[0]
            elif self.hp[1] == 1:
                self.numberImg2 = self.numbers[1]
            elif self.hp[1] == 2:
                self.numberImg2 = self.numbers[2]
            elif self.hp[1] == 3:
                self.numberImg2 = self.numbers[3]
            elif self.hp[1] == 4:
                self.numberImg2 = self.numbers[4]
            elif self.hp[1] == 5:
                self.numberImg2 = self.numbers[5]
            elif self.hp[1] == 6:
                self.numberImg2 = self.numbers[6]
            elif self.hp[1] == 7:
                self.numberImg2 = self.numbers[7]
            elif self.hp[1] == 8:
                self.numberImg2 = self.numbers[8]
            elif self.hp[1] == 9:
                self.numberImg2 = self.numbers[9]

            self.numberRect1 = self.numberImg1.get_rect()
            self.numberRect2 = self.numberImg2.get_rect()

            self.numberRect2.centery = self.rect.bottom - 25
            self.numberRect2.right = self.rect.right - 70
            self.numberRect1.centery = self.rect.bottom - 25
            self.numberRect1.right = self.numberRect2.left
        elif len(self.hp) == 3:
            if self.hp[0] == 0:
                self.numberImg1 = self.numbers[0]
            elif self.hp[0] == 1:
                self.numberImg1 = self.numbers[1]
            elif self.hp[0] == 2:
                self.numberImg1 = self.numbers[2]
            elif self.hp[0] == 3:
                self.numberImg1 = self.numbers[3]
            elif self.hp[0] == 4:
                self.numberImg1 = self.numbers[4]
            elif self.hp[0] == 5:
                self.numberImg1 = self.numbers[5]
            elif self.hp[0] == 6:
                self.numberImg1 = self.numbers[6]
            elif self.hp[0] == 7:
                self.numberImg1 = self.numbers[7]
            elif self.hp[0] == 8:
                self.numberImg1 = self.numbers[8]
            elif self.hp[0] == 9:
                self.numberImg1 = self.numbers[9]

            if self.hp[1] == 0:
                self.numberImg2 = self.numbers[0]
            elif self.hp[1] == 1:
                self.numberImg2 = self.numbers[1]
            elif self.hp[1] == 2:
                self.numberImg2 = self.numbers[2]
            elif self.hp[1] == 3:
                self.numberImg2 = self.numbers[3]
            elif self.hp[1] == 4:
                self.numberImg2 = self.numbers[4]
            elif self.hp[1] == 5:
                self.numberImg2 = self.numbers[5]
            elif self.hp[1] == 6:
                self.numberImg2 = self.numbers[6]
            elif self.hp[1] == 7:
                self.numberImg2 = self.numbers[7]
            elif self.hp[1] == 8:
                self.numberImg2 = self.numbers[8]
            elif self.hp[1] == 9:
                self.numberImg2 = self.numbers[9]

            if self.hp[2] == 0:
                self.numberImg3 = self.numbers[0]
            elif self.hp[2] == 1:
                self.numberImg3 = self.numbers[1]
            elif self.hp[2] == 2:
                self.numberImg3 = self.numbers[2]
            elif self.hp[2] == 3:
                self.numberImg3 = self.numbers[3]
            elif self.hp[2] == 4:
                self.numberImg3 = self.numbers[4]
            elif self.hp[2] == 5:
                self.numberImg3 = self.numbers[5]
            elif self.hp[2] == 6:
                self.numberImg3 = self.numbers[6]
            elif self.hp[2] == 7:
                self.numberImg3 = self.numbers[7]
            elif self.hp[2] == 8:
                self.numberImg3 = self.numbers[8]
            elif self.hp[2] == 9:
                self.numberImg3 = self.numbers[9]

            self.numberRect1 = self.numberImg1.get_rect()
            self.numberRect2 = self.numberImg2.get_rect()
            self.numberRect3 = self.numberImg3.get_rect()

            self.numberRect3.centery = self.rect.bottom - 25
            self.numberRect3.right = self.rect.right - 70
            self.numberRect2.right = self.numberRect3.left
            self.numberRect2.centery = self.rect.bottom - 25
            self.numberRect1.centery = self.rect.bottom - 25
            self.numberRect1.right = self.numberRect2.left




    def draw(self):
        self.game.screen.blit(self.image, self.rect)
        if len(self.hp) == 1:
            self.game.screen.blit(self.numberImg, self.numberRect)
        elif len(self.hp) == 2:
            self.game.screen.blit(self.numberImg1, self.numberRect1)
            self.game.screen.blit(self.numberImg2, self.numberRect2)
        elif len(self.hp) == 3:
            self.game.screen.blit(self.numberImg1, self.numberRect1)
            self.game.screen.blit(self.numberImg2, self.numberRect2)
            self.game.screen.blit(self.numberImg3, self.numberRect3)


class LuigiUI(pg.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.ui
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        sheet = spritesheet("sprites/ui.png", "sprites/ui.xml")
        self.numbers = [sheet.getImageName("0_hp.png"),
                        sheet.getImageName("1_hp.png"),
                        sheet.getImageName("2_hp.png"),
                        sheet.getImageName("3_hp.png"),
                        sheet.getImageName("4_hp.png"),
                        sheet.getImageName("5_hp.png"),
                        sheet.getImageName("6_hp.png"),
                        sheet.getImageName("7_hp.png"),
                        sheet.getImageName("8_hp.png"),
                        sheet.getImageName("9_hp.png")]
        self.sprites = [pg.image.load("sprites/LuigiUI.png")]
        self.image = self.sprites[0]
        self.rect = self.image.get_rect()
        self.rect.right = width
        self.rect.top = 0

    def update(self):
        self.hp = [int(i) for i in str(self.game.follower.stats["hp"])]

        if len(self.hp) == 1:
            if self.hp[0] == 0:
                self.numberImg = self.numbers[0]
            elif self.hp[0] == 1:
                self.numberImg = self.numbers[1]
            elif self.hp[0] == 2:
                self.numberImg = self.numbers[2]
            elif self.hp[0] == 3:
                self.numberImg = self.numbers[3]
            elif self.hp[0] == 4:
                self.numberImg = self.numbers[4]
            elif self.hp[0] == 5:
                self.numberImg = self.numbers[5]
            elif self.hp[0] == 6:
                self.numberImg = self.numbers[6]
            elif self.hp[0] == 7:
                self.numberImg = self.numbers[7]
            elif self.hp[0] == 8:
                self.numberImg = self.numbers[8]
            elif self.hp[0] == 9:
                self.numberImg = self.numbers[9]

            self.numberRect = self.numberImg.get_rect()
            self.numberRect.right = self.rect.right - 50
            self.numberRect.centery = self.rect.bottom - 25
        elif len(self.hp) == 2:
            if self.hp[0] == 0:
                self.numberImg1 = self.numbers[0]
            elif self.hp[0] == 1:
                self.numberImg1 = self.numbers[1]
            elif self.hp[0] == 2:
                self.numberImg1 = self.numbers[2]
            elif self.hp[0] == 3:
                self.numberImg1 = self.numbers[3]
            elif self.hp[0] == 4:
                self.numberImg1 = self.numbers[4]
            elif self.hp[0] == 5:
                self.numberImg1 = self.numbers[5]
            elif self.hp[0] == 6:
                self.numberImg1 = self.numbers[6]
            elif self.hp[0] == 7:
                self.numberImg1 = self.numbers[7]
            elif self.hp[0] == 8:
                self.numberImg1 = self.numbers[8]
            elif self.hp[0] == 9:
                self.numberImg1 = self.numbers[9]

            if self.hp[1] == 0:
                self.numberImg2 = self.numbers[0]
            elif self.hp[1] == 1:
                self.numberImg2 = self.numbers[1]
            elif self.hp[1] == 2:
                self.numberImg2 = self.numbers[2]
            elif self.hp[1] == 3:
                self.numberImg2 = self.numbers[3]
            elif self.hp[1] == 4:
                self.numberImg2 = self.numbers[4]
            elif self.hp[1] == 5:
                self.numberImg2 = self.numbers[5]
            elif self.hp[1] == 6:
                self.numberImg2 = self.numbers[6]
            elif self.hp[1] == 7:
                self.numberImg2 = self.numbers[7]
            elif self.hp[1] == 8:
                self.numberImg2 = self.numbers[8]
            elif self.hp[1] == 9:
                self.numberImg2 = self.numbers[9]

            self.numberRect1 = self.numberImg1.get_rect()
            self.numberRect2 = self.numberImg2.get_rect()

            self.numberRect2.centery = self.rect.bottom - 25
            self.numberRect2.right = self.rect.right - 50
            self.numberRect1.centery = self.rect.bottom - 25
            self.numberRect1.right = self.numberRect2.left
        elif len(self.hp) == 3:
            if self.hp[0] == 0:
                self.numberImg1 = self.numbers[0]
            elif self.hp[0] == 1:
                self.numberImg1 = self.numbers[1]
            elif self.hp[0] == 2:
                self.numberImg1 = self.numbers[2]
            elif self.hp[0] == 3:
                self.numberImg1 = self.numbers[3]
            elif self.hp[0] == 4:
                self.numberImg1 = self.numbers[4]
            elif self.hp[0] == 5:
                self.numberImg1 = self.numbers[5]
            elif self.hp[0] == 6:
                self.numberImg1 = self.numbers[6]
            elif self.hp[0] == 7:
                self.numberImg1 = self.numbers[7]
            elif self.hp[0] == 8:
                self.numberImg1 = self.numbers[8]
            elif self.hp[0] == 9:
                self.numberImg1 = self.numbers[9]

            if self.hp[1] == 0:
                self.numberImg2 = self.numbers[0]
            elif self.hp[1] == 1:
                self.numberImg2 = self.numbers[1]
            elif self.hp[1] == 2:
                self.numberImg2 = self.numbers[2]
            elif self.hp[1] == 3:
                self.numberImg2 = self.numbers[3]
            elif self.hp[1] == 4:
                self.numberImg2 = self.numbers[4]
            elif self.hp[1] == 5:
                self.numberImg2 = self.numbers[5]
            elif self.hp[1] == 6:
                self.numberImg2 = self.numbers[6]
            elif self.hp[1] == 7:
                self.numberImg2 = self.numbers[7]
            elif self.hp[1] == 8:
                self.numberImg2 = self.numbers[8]
            elif self.hp[1] == 9:
                self.numberImg2 = self.numbers[9]

            if self.hp[2] == 0:
                self.numberImg3 = self.numbers[0]
            elif self.hp[2] == 1:
                self.numberImg3 = self.numbers[1]
            elif self.hp[2] == 2:
                self.numberImg3 = self.numbers[2]
            elif self.hp[2] == 3:
                self.numberImg3 = self.numbers[3]
            elif self.hp[2] == 4:
                self.numberImg3 = self.numbers[4]
            elif self.hp[2] == 5:
                self.numberImg3 = self.numbers[5]
            elif self.hp[2] == 6:
                self.numberImg3 = self.numbers[6]
            elif self.hp[2] == 7:
                self.numberImg3 = self.numbers[7]
            elif self.hp[2] == 8:
                self.numberImg3 = self.numbers[8]
            elif self.hp[2] == 9:
                self.numberImg3 = self.numbers[9]

            self.numberRect1 = self.numberImg1.get_rect()
            self.numberRect2 = self.numberImg2.get_rect()
            self.numberRect3 = self.numberImg3.get_rect()

            self.numberRect3.centery = self.rect.bottom - 25
            self.numberRect3.right = self.rect.right - 50
            self.numberRect2.right = self.numberRect3.left
            self.numberRect2.centery = self.rect.bottom - 25
            self.numberRect1.centery = self.rect.bottom - 25
            self.numberRect1.right = self.numberRect2.left

    def draw(self):
        self.game.screen.blit(self.image, self.rect)
        if len(self.hp) == 1:
            self.game.screen.blit(self.numberImg, self.numberRect)
        elif len(self.hp) == 2:
            self.game.screen.blit(self.numberImg1, self.numberRect1)
            self.game.screen.blit(self.numberImg2, self.numberRect2)
        elif len(self.hp) == 3:
            self.game.screen.blit(self.numberImg1, self.numberRect1)
            self.game.screen.blit(self.numberImg2, self.numberRect2)
            self.game.screen.blit(self.numberImg3, self.numberRect3)


class HitNumbers(pg.sprite.Sprite):
    def __init__(self, game, room, pos, number, type="normal"):
        self.groups = game.ui
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.offset = True
        sheet = spritesheet("sprites/ui.png", "sprites/ui.xml")
        self.numbers = [sheet.getImageName("0.png"),
                        sheet.getImageName("1.png"),
                        sheet.getImageName("2.png"),
                        sheet.getImageName("3.png"),
                        sheet.getImageName("4.png"),
                        sheet.getImageName("5.png"),
                        sheet.getImageName("6.png"),
                        sheet.getImageName("7.png"),
                        sheet.getImageName("8.png"),
                        sheet.getImageName("9.png")]
        self.alpha = 255
        if type == "normal":
            self.base = sheet.getImageName("hit.png")
        elif type == "mario":
            self.base = sheet.getImageName("hit_mario.png")
        elif type == "luigi":
            self.base = sheet.getImageName("hit_luigi.png")
        self.counter = 0
        self.room = room
        self.image = self.base
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.number = [int(i) for i in str(number)]
        if len(self.number) == 1:
            if self.number[0] == 0:
                self.numberImg = self.numbers[0]
            elif self.number[0] == 1:
                self.numberImg = self.numbers[1]
            elif self.number[0] == 2:
                self.numberImg = self.numbers[2]
            elif self.number[0] == 3:
                self.numberImg = self.numbers[3]
            elif self.number[0] == 4:
                self.numberImg = self.numbers[4]
            elif self.number[0] == 5:
                self.numberImg = self.numbers[5]
            elif self.number[0] == 6:
                self.numberImg = self.numbers[6]
            elif self.number[0] == 7:
                self.numberImg = self.numbers[7]
            elif self.number[0] == 8:
                self.numberImg = self.numbers[8]
            elif self.number[0] == 9:
                self.numberImg = self.numbers[9]

            self.numberRect = self.numberImg.get_rect()
            self.numberRect.center = self.rect.center
        elif len(self.number) == 2:
            if self.number[0] == 0:
                self.numberImg1 = self.numbers[0]
            elif self.number[0] == 1:
                self.numberImg1 = self.numbers[1]
            elif self.number[0] == 2:
                self.numberImg1 = self.numbers[2]
            elif self.number[0] == 3:
                self.numberImg1 = self.numbers[3]
            elif self.number[0] == 4:
                self.numberImg1 = self.numbers[4]
            elif self.number[0] == 5:
                self.numberImg1 = self.numbers[5]
            elif self.number[0] == 6:
                self.numberImg1 = self.numbers[6]
            elif self.number[0] == 7:
                self.numberImg1 = self.numbers[7]
            elif self.number[0] == 8:
                self.numberImg1 = self.numbers[8]
            elif self.number[0] == 9:
                self.numberImg1 = self.numbers[9]

            if self.number[1] == 0:
                self.numberImg2 = self.numbers[0]
            elif self.number[1] == 1:
                self.numberImg2 = self.numbers[1]
            elif self.number[1] == 2:
                self.numberImg2 = self.numbers[2]
            elif self.number[1] == 3:
                self.numberImg2 = self.numbers[3]
            elif self.number[1] == 4:
                self.numberImg2 = self.numbers[4]
            elif self.number[1] == 5:
                self.numberImg2 = self.numbers[5]
            elif self.number[1] == 6:
                self.numberImg2 = self.numbers[6]
            elif self.number[1] == 7:
                self.numberImg2 = self.numbers[7]
            elif self.number[1] == 8:
                self.numberImg2 = self.numbers[8]
            elif self.number[1] == 9:
                self.numberImg2 = self.numbers[9]

            self.numberRect1 = self.numberImg1.get_rect()
            self.numberRect2 = self.numberImg2.get_rect()

            self.numberRect1.centery = self.rect.centery
            self.numberRect1.right = self.rect.centerx + 1
            self.numberRect2.centery = self.rect.centery
            self.numberRect2.left = self.rect.centerx - 1
        elif len(self.number) == 3:
            if self.number[0] == 0:
                self.numberImg1 = self.numbers[0]
            elif self.number[0] == 1:
                self.numberImg1 = self.numbers[1]
            elif self.number[0] == 2:
                self.numberImg1 = self.numbers[2]
            elif self.number[0] == 3:
                self.numberImg1 = self.numbers[3]
            elif self.number[0] == 4:
                self.numberImg1 = self.numbers[4]
            elif self.number[0] == 5:
                self.numberImg1 = self.numbers[5]
            elif self.number[0] == 6:
                self.numberImg1 = self.numbers[6]
            elif self.number[0] == 7:
                self.numberImg1 = self.numbers[7]
            elif self.number[0] == 8:
                self.numberImg1 = self.numbers[8]
            elif self.number[0] == 9:
                self.numberImg1 = self.numbers[9]

            if self.number[1] == 0:
                self.numberImg2 = self.numbers[0]
            elif self.number[1] == 1:
                self.numberImg2 = self.numbers[1]
            elif self.number[1] == 2:
                self.numberImg2 = self.numbers[2]
            elif self.number[1] == 3:
                self.numberImg2 = self.numbers[3]
            elif self.number[1] == 4:
                self.numberImg2 = self.numbers[4]
            elif self.number[1] == 5:
                self.numberImg2 = self.numbers[5]
            elif self.number[1] == 6:
                self.numberImg2 = self.numbers[6]
            elif self.number[1] == 7:
                self.numberImg2 = self.numbers[7]
            elif self.number[1] == 8:
                self.numberImg2 = self.numbers[8]
            elif self.number[1] == 9:
                self.numberImg2 = self.numbers[9]

            if self.number[2] == 0:
                self.numberImg3 = self.numbers[0]
            elif self.number[2] == 1:
                self.numberImg3 = self.numbers[1]
            elif self.number[2] == 2:
                self.numberImg3 = self.numbers[2]
            elif self.number[2] == 3:
                self.numberImg3 = self.numbers[3]
            elif self.number[2] == 4:
                self.numberImg3 = self.numbers[4]
            elif self.number[2] == 5:
                self.numberImg3 = self.numbers[5]
            elif self.number[2] == 6:
                self.numberImg3 = self.numbers[6]
            elif self.number[2] == 7:
                self.numberImg3 = self.numbers[7]
            elif self.number[2] == 8:
                self.numberImg3 = self.numbers[8]
            elif self.number[2] == 9:
                self.numberImg3 = self.numbers[9]

            self.numberRect1 = self.numberImg1.get_rect()
            self.numberRect2 = self.numberImg2.get_rect()
            self.numberRect3 = self.numberImg3.get_rect()

            self.numberRect1.centery = self.rect.centery
            self.numberRect1.right = self.rect.centerx - (self.numberRect2.width / 2) + 2
            self.numberRect2.center = self.rect.center
            self.numberRect3.centery = self.rect.centery
            self.numberRect3.left = self.rect.centerx + (self.numberRect2.width / 2) - 2

    def draw(self):
        self.game.blit_alpha(self.game.screen, self.image, self.game.camera.offset(self.rect), self.alpha)
        if len(self.number) == 1:
            self.game.blit_alpha(self.game.screen, self.numberImg, self.game.camera.offset(self.numberRect), self.alpha)
        elif len(self.number) == 2:
            self.game.blit_alpha(self.game.screen, self.numberImg1, self.game.camera.offset(self.numberRect1), self.alpha)
            self.game.blit_alpha(self.game.screen, self.numberImg2, self.game.camera.offset(self.numberRect2), self.alpha)
        elif len(self.number) == 3:
            self.game.blit_alpha(self.game.screen, self.numberImg1, self.game.camera.offset(self.numberRect1), self.alpha)
            self.game.blit_alpha(self.game.screen, self.numberImg2, self.game.camera.offset(self.numberRect2), self.alpha)
            self.game.blit_alpha(self.game.screen, self.numberImg3, self.game.camera.offset(self.numberRect3), self.alpha)

    def update(self):
        self.counter += 1

        if self.counter >= fps:
            self.alpha -= 10
            if self.alpha <= 0:
                self.kill()

        if self.game.room != self.room:
            self.kill()