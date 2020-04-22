import xml.etree.ElementTree as ET

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
        self.image = self.images[random.randrange(0, 8)]
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


class Other(pg.sprite.Sprite):
    def __init__(self, game, block, item, amount=1):
        self.game = game
        self.block = block
        pg.sprite.Sprite.__init__(self, game.blockContents)
        self.game.sprites.append(self)
        self.item = item
        self.amount = amount
        sheet = spritesheet("sprites/blocks.png", "sprites/blocks.xml")
        self.images = {"Mushroom": sheet.getImageName("Mushroom.png"),
                       "1-UP": sheet.getImageName("1-UP.png"),
                       "Nut": sheet.getImageName("Nut.png"),
                       "Syrup": sheet.getImageName("Syrup.png"),
                       "Star Candy": sheet.getImageName("Star Candy.png"),
                       "Attack Piece": sheet.getImageName("Attack Piece.png")}
        if "1-UP" in self.item:
            self.image = self.images["1-UP"]
        elif "Mushroom" in self.item:
            self.image = self.images["Mushroom"]
        elif "Nut" in self.item:
            self.image = self.images["Nut"]
        elif "Syrup" in self.item:
            self.image = self.images["Syrup"]
        elif "Star Cand" in self.item:
            self.image = self.images["Star Candy"]
        elif "Attack Piece" in self.item:
            self.image = self.images["Attack Piece"]
        self.rect = self.block.rect
        self.imgRect = self.image.get_rect()
        self.imgRect.center = self.block.imgRect.center
        self.alpha = 255
        self.counter = 0
        self.game.itemFromBlockSound.play()
        self.messageImage = pg.image.load("sprites/ui/enemySelectionFullScreen.png").convert_alpha()
        self.messageImage = pg.transform.flip(self.messageImage, False, True)
        self.messageRect = self.messageImage.get_rect()
        self.messageRect.bottom = height
        for item in self.game.items:
            if item[0] == self.item:
                if item[1] < 0:
                    item[1] = 0
                item[1] += amount

        for item in self.game.player.attackPieces:
            if item[0] in self.item:
                item[1] += amount
                self.playerItem = item

        for item in self.game.follower.attackPieces:
            if item[0] in self.item:
                item[1] += amount
                self.playerItem = item

    def update(self):
        if self.counter < fps:
            self.counter += 1
        else:
            self.kill()
            self.game.sprites.remove(self)

        if self.counter < fps / 8:
            self.imgRect.y -= 10

    def draw(self):
        self.game.screen.blit(self.messageImage, self.messageRect)
        if self.item == "Star Cand":
            if self.amount > 1:
                ptext.draw(self.item + "ies X" + str(self.amount), (width / 2, height - 46), fontname=dialogueFont, owidth=1, anchor=(0.5, 0.5), surf=self.game.screen, fontsize=50, color=white)
            else:
                ptext.draw(self.item + "y", (width / 2, height - 46), fontname=dialogueFont, owidth=1, anchor=(0.5, 0.5), surf=self.game.screen, fontsize=50, color=white)
        elif "Attack Piece" not in self.item:
            if self.amount > 1:
                ptext.draw(self.item + "s X" + str(self.amount), (width / 2, height - 46), fontname=dialogueFont, owidth=1, anchor=(0.5, 0.5), surf=self.game.screen, fontsize=50, color=white)
            else:
                ptext.draw(self.item, (width / 2, height - 46), fontname=dialogueFont, owidth=1, anchor=(0.5, 0.5), surf=self.game.screen, fontsize=50, color=white)
        else:
            if self.amount > 1:
                ptext.draw(self.item + "s X" + str(self.amount)+ " (" + str(10 - int(self.playerItem[1])) + " left)", (width / 2, height - 46), fontname=dialogueFont, owidth=1,
                           anchor=(0.5, 0.5), surf=self.game.screen, fontsize=50, color=white)
            else:
                ptext.draw(self.item + " (" + str(10 - int(self.playerItem[1])) + " left)", (width / 2, height - 46), fontname=dialogueFont, owidth=1, anchor=(0.5, 0.5),
                           surf=self.game.screen, fontsize=50, color=white)

