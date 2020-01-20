import pygame as pg
import xml.etree.ElementTree as ET
from settings import *

vec = pg.math.Vector2

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
                    self.map[name]['width'] = int(node.attrib.get('w'))
                    self.map[name]['height'] = int(node.attrib.get('h'))

    def get_image_rect(self, x, y, w, h):
        return self.spritesheet.subsurface(pg.Rect(x, y, w, h))

    def getImageName(self, name):
        rect = pg.Rect(self.map[name]['x'], self.map[name]['y'], self.map[name]['width'], self.map[name]['height'])
        return self.spritesheet.subsurface(rect)

class marioOverworld(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface((40, 40))
        self.image.fill(red)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos = vec(x, y)
        self.loadImages()

    def loadImages(self):
        pass

    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.pos.y -= playerSpeed
            if keys[pg.K_LSHIFT]:
                self.pos.y -= (playerSpeed * 2)
        if keys[pg.K_a]:
            self.pos.x -= playerSpeed
            if keys[pg.K_LSHIFT]:
                self.pos.x -= (playerSpeed * 2)
        if keys[pg.K_s]:
            self.pos.y += playerSpeed
            if keys[pg.K_LSHIFT]:
                self.pos.y += (playerSpeed * 2)
        if keys[pg.K_d]:
            self.pos.x += playerSpeed
            if keys[pg.K_LSHIFT]:
                self.pos.x += playerSpeed * 2

        self.rect.center = self.pos