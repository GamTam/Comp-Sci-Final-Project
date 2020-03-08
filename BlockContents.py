import xml.etree.ElementTree as ET
import random
from Settings import *


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


class Coin(pg.sprite.Sprite):
    def __init__(self, game, block):
        self.game = game
        self.block = block
        pg.sprite.Sprite.__init__(self)
        self.game.sprites.append(self)
        sheet = spritesheet("sprites/blocks.png", "sprites/blocks.xml")
        self.images = [sheet.getImageName("coin_1.png"),
                       sheet.getImageName("coin_2.png"),
                       sheet.getImageName("coin_3.png"),
                       sheet.getImageName("coin_4.png"),
                       sheet.getImageName("coin_5.png"),
                       sheet.getImageName("coin_6.png"),
                       sheet.getImageName("coin_7.png"),
                       sheet.getImageName("coin_8.png")]
        self.rect = self.block.rect
        self.image = self.images[random.randrange(0,8)]
        self.imgRect = self.image.get_rect()
        self.imgRect.center = self.block.imgRect.center
        self.lastUpdate = 0
        self.currentFrame = 0
        self.alpha = 255
        self.counter = 0
        self.game.coinSound.play()

    def update(self):
        now = pg.time.get_ticks()

        if self.counter < fps / 4:
            self.counter += 1
        else:
            self.game.coins += 1
            self.game.sprites.remove(self)

        if self.counter < fps / 4:
            self.imgRect.y -= 10

        if now - self.lastUpdate > 20:
            self.lastUpdate = now
            if self.currentFrame < len(self.images):
                self.currentFrame = (self.currentFrame + 1) % (len(self.images))
            else:
                self.currentFrame = 0
            center = self.imgRect.center
            self.image = self.images[self.currentFrame]
            self.imgRect = self.image.get_rect()
            self.imgRect.center = center
