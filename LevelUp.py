import pytweening as pt

from BlockContents import *


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


class MarioLevelUp(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.loadImages()
        self.image = self.spinningFrames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (200, 300)
        self.speed = 180
        self.lastUpdate = 0
        self.currentFrame = 0
        self.points = []
        self.bop = False
        self.counter = 0
        for i in range(self.speed + 1):
            self.points.append(pt.getPointOnLine(200, 300, width / 2 - 5,
                                                 385, (i / self.speed)))

    def loadImages(self):
        sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")

        self.spinningFrames = [sheet.getImageName("mario_spinning_1.png"),
                               sheet.getImageName("mario_spinning_2.png"),
                               sheet.getImageName("mario_spinning_3.png"),
                               sheet.getImageName("mario_spinning_4.png"),
                               sheet.getImageName("mario_spinning_5.png"),
                               sheet.getImageName("mario_spinning_6.png"),
                               sheet.getImageName("mario_spinning_7.png"),
                               sheet.getImageName("mario_spinning_8.png")]

        self.bopFrames = [sheet.getImageName("mario_levelup_1.png"),
                          sheet.getImageName("mario_levelup_2.png"),
                          sheet.getImageName("mario_levelup_3.png"),
                          sheet.getImageName("mario_levelup_4.png"),
                          sheet.getImageName("mario_levelup_5.png"),
                          sheet.getImageName("mario_levelup_6.png"),
                          sheet.getImageName("mario_levelup_7.png"),
                          sheet.getImageName("mario_levelup_8.png"),
                          sheet.getImageName("mario_levelup_9.png")]

    def update(self):
        self.animate()

        if self.counter < len(self.points) - 1:
            self.counter += 1
            self.rect.center = self.points[self.counter]

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.counter < len(self.points) - 1:
                if self.currentFrame < len(self.spinningFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.spinningFrames))
                else:
                    self.currentFrame = 0
                center = self.rect.center
                self.image = self.spinningFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center
            else:
                if self.currentFrame < len(self.bopFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.bopFrames))
                else:
                    self.currentFrame = 0
                bottom = self.rect.bottom
                centerx = self.rect.centerx
                self.image = self.bopFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                if self.currentFrame == 2:
                    self.rect.centerx = centerx + 3
                elif self.currentFrame == 3:
                    self.rect.centerx = centerx + 3
                elif self.currentFrame == 4:
                    self.rect.centerx = centerx + 1
                elif self.currentFrame == 5:
                    self.rect.centerx = centerx - 3
                elif self.currentFrame == 6:
                    self.rect.centerx = centerx - 3
                elif self.currentFrame == 7:
                    self.rect.centerx = centerx - 1
                else:
                    self.rect.centerx = centerx
                self.rect.bottom = bottom


class MarioLevelUpLeave(pg.sprite.Sprite):
    def __init__(self, pos=(200, 300)):
        pg.sprite.Sprite.__init__(self)
        self.loadImages()
        self.image = self.spinningFrames[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.speed = 180
        self.lastUpdate = 0
        self.currentFrame = 0
        self.points = []
        self.bop = False
        self.counter = 0
        for i in range(self.speed + 1):
            self.points.append(pt.getPointOnLine(self.rect.centerx, self.rect.centery, -870,
                                                 -470, (i / self.speed)))

    def loadImages(self):
        sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")

        self.spinningFrames = [sheet.getImageName("mario_spinning_1.png"),
                               sheet.getImageName("mario_spinning_2.png"),
                               sheet.getImageName("mario_spinning_3.png"),
                               sheet.getImageName("mario_spinning_4.png"),
                               sheet.getImageName("mario_spinning_5.png"),
                               sheet.getImageName("mario_spinning_6.png"),
                               sheet.getImageName("mario_spinning_7.png"),
                               sheet.getImageName("mario_spinning_8.png")]

        self.bopFrames = [sheet.getImageName("mario_levelup_1.png"),
                          sheet.getImageName("mario_levelup_2.png"),
                          sheet.getImageName("mario_levelup_3.png"),
                          sheet.getImageName("mario_levelup_4.png"),
                          sheet.getImageName("mario_levelup_5.png"),
                          sheet.getImageName("mario_levelup_6.png"),
                          sheet.getImageName("mario_levelup_7.png"),
                          sheet.getImageName("mario_levelup_8.png"),
                          sheet.getImageName("mario_levelup_9.png")]

    def update(self):
        self.animate()

        if self.counter < len(self.points) - 1:
            self.counter += 1
            self.rect.center = self.points[self.counter]

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.counter < len(self.points) - 1:
                if self.currentFrame < len(self.spinningFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.spinningFrames))
                else:
                    self.currentFrame = 0
                center = self.rect.center
                self.image = self.spinningFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class LuigiLevelUp(pg.sprite.Sprite):
    def __init__(self, mario=False):
        pg.sprite.Sprite.__init__(self)
        self.loadImages()
        self.image = self.spinningFrames[0]
        self.rect = self.image.get_rect()
        if not mario:
            self.rect.center = (200, 500)
        else:
            self.rect.center = (-870, 885)
        self.speed = 180
        self.lastUpdate = 0
        self.currentFrame = 0
        self.points = []
        self.bop = False
        self.counter = 0
        for i in range(self.speed + 1):
            self.points.append(pt.getPointOnLine(self.rect.centerx, self.rect.centery, width / 2 - 5,
                                                 385, (i / self.speed)))

    def loadImages(self):
        sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")

        self.spinningFrames = [sheet.getImageName("luigi_spinning_1.png"),
                               sheet.getImageName("luigi_spinning_2.png"),
                               sheet.getImageName("luigi_spinning_3.png"),
                               sheet.getImageName("luigi_spinning_4.png"),
                               sheet.getImageName("luigi_spinning_5.png"),
                               sheet.getImageName("luigi_spinning_6.png"),
                               sheet.getImageName("luigi_spinning_7.png"),
                               sheet.getImageName("luigi_spinning_8.png")]

        self.bopFrames = [sheet.getImageName("luigi_levelup_1.png"),
                          sheet.getImageName("luigi_levelup_2.png"),
                          sheet.getImageName("luigi_levelup_3.png"),
                          sheet.getImageName("luigi_levelup_4.png"),
                          sheet.getImageName("luigi_levelup_5.png"),
                          sheet.getImageName("luigi_levelup_6.png"),
                          sheet.getImageName("luigi_levelup_7.png"),
                          sheet.getImageName("luigi_levelup_8.png"),
                          sheet.getImageName("luigi_levelup_9.png"),
                          sheet.getImageName("luigi_levelup_10.png"),
                          sheet.getImageName("luigi_levelup_11.png"),
                          sheet.getImageName("luigi_levelup_12.png"),
                          sheet.getImageName("luigi_levelup_13.png"),
                          sheet.getImageName("luigi_levelup_14.png"),
                          sheet.getImageName("luigi_levelup_15.png"),
                          sheet.getImageName("luigi_levelup_16.png"),
                          sheet.getImageName("luigi_levelup_17.png"),
                          sheet.getImageName("luigi_levelup_18.png")]

    def update(self):
        self.animate()

        if self.counter < len(self.points) - 1:
            self.counter += 1
            self.rect.center = self.points[self.counter]

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.counter < len(self.points) - 1:
                if self.currentFrame < len(self.spinningFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.spinningFrames))
                else:
                    self.currentFrame = 0
                center = self.rect.center
                self.image = self.spinningFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center
            else:
                if self.currentFrame < len(self.bopFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.bopFrames))
                else:
                    self.currentFrame = 0
                bottom = self.rect.bottom
                centerx = self.rect.centerx
                self.image = self.bopFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom


class LuigiLevelUpLeave(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.loadImages()
        self.image = self.spinningFrames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (200, 500)
        self.speed = 180
        self.lastUpdate = 0
        self.currentFrame = 0
        self.points = []
        self.bop = False
        self.counter = 0
        for i in range(self.speed + 1):
            self.points.append(pt.getPointOnLine(self.rect.centerx, self.rect.centery, -870, 885, (i / self.speed)))

    def loadImages(self):
        sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")

        self.spinningFrames = [sheet.getImageName("luigi_spinning_1.png"),
                               sheet.getImageName("luigi_spinning_2.png"),
                               sheet.getImageName("luigi_spinning_3.png"),
                               sheet.getImageName("luigi_spinning_4.png"),
                               sheet.getImageName("luigi_spinning_5.png"),
                               sheet.getImageName("luigi_spinning_6.png"),
                               sheet.getImageName("luigi_spinning_7.png"),
                               sheet.getImageName("luigi_spinning_8.png")]

    def update(self):
        self.animate()

        if self.counter < len(self.points) - 1:
            self.counter += 1
            self.rect.center = self.points[self.counter]

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.counter < len(self.points) - 1:
                if self.currentFrame < len(self.spinningFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.spinningFrames))
                else:
                    self.currentFrame = 0
                center = self.rect.center
                self.image = self.spinningFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class MarioLevelUpUI(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.image.load("sprites/LevelUpMario.png").convert_alpha()
        self.rect = self.image.get_rect()

    def draw(self, added, add=True):
        self.game.screen.blit(self.image, self.rect)
        if not added:
            ptext.draw(str(self.game.player.stats["level"]), (324, 390), anchor=(0, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50)

            ptext.draw(str(self.game.player.stats["maxHP"]), (925, 275), anchor=(0, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50)
            if add:
                ptext.draw("+" + str(self.game.player.statGrowth["maxHP"]), (1200, 275), anchor=(1, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50)

            ptext.draw(str(self.game.player.stats["maxBP"]),
                       (925, 370), anchor=(0, 0.5), color=(253, 163, 5), gcolor=(253, 243, 31), fontname=superMario256,
                       owidth=0.7, surf=self.game.screen, fontsize=50)
            if add:
                ptext.draw("+" + str(self.game.player.statGrowth["maxBP"]), (1200, 370), anchor=(1, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50)

            ptext.draw(str(self.game.player.stats["pow"]),
                       (925, 465), anchor=(0, 0.5), color=(253, 163, 5), gcolor=(253, 243, 31), fontname=superMario256,
                       owidth=0.7, surf=self.game.screen, fontsize=50)
            if add:
                ptext.draw("+" + str(self.game.player.statGrowth["pow"]), (1200, 465), anchor=(1, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50)

            ptext.draw(str(self.game.player.stats["def"]),
                       (925, 560), anchor=(0, 0.5), color=(253, 163, 5), gcolor=(253, 243, 31), fontname=superMario256,
                       owidth=0.7, surf=self.game.screen, fontsize=50)
            if add:
                ptext.draw("+" + str(self.game.player.statGrowth["def"]), (1200, 560), anchor=(1, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50)
        else:
            ptext.draw(str(self.game.player.stats["level"] + 1), (324, 390), anchor=(0, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50)

            ptext.draw(str(self.game.player.stats["maxHP"] + self.game.player.statGrowth["maxHP"]), (925, 275), anchor=(0, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen,
                       fontsize=50)

            ptext.draw(str(self.game.player.stats["maxBP"] + self.game.player.statGrowth["maxBP"]),
                       (925, 370), anchor=(0, 0.5), color=(253, 163, 5), gcolor=(253, 243, 31),
                       fontname=superMario256,
                       owidth=0.7, surf=self.game.screen, fontsize=50)

            ptext.draw(str(self.game.player.stats["pow"] + self.game.player.statGrowth["pow"]),
                       (925, 465), anchor=(0, 0.5), color=(253, 163, 5), gcolor=(253, 243, 31),
                       fontname=superMario256,
                       owidth=0.7, surf=self.game.screen, fontsize=50)

            ptext.draw(str(self.game.player.stats["def"] + self.game.player.statGrowth["def"]),
                       (925, 560), anchor=(0, 0.5), color=(253, 163, 5), gcolor=(253, 243, 31),
                       fontname=superMario256,
                       owidth=0.7, surf=self.game.screen, fontsize=50)


class LuigiLevelUpUI(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.image.load("sprites/LevelUpLuigi.png").convert_alpha()
        self.rect = self.image.get_rect()

    def draw(self, added, add=True):
        self.game.screen.blit(self.image, self.rect)
        if not added:
            ptext.draw(str(self.game.follower.stats["level"]), (324, 390), anchor=(0, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50)

            ptext.draw(str(self.game.follower.stats["maxHP"]), (925, 275), anchor=(0, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50)
            if add:
                ptext.draw("+" + str(self.game.follower.statGrowth["maxHP"]), (1200, 275), anchor=(1, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50)

            ptext.draw(str(self.game.follower.stats["maxBP"]),
                       (925, 370), anchor=(0, 0.5), color=(253, 163, 5), gcolor=(253, 243, 31), fontname=superMario256,
                       owidth=0.7, surf=self.game.screen, fontsize=50)
            if add:
                ptext.draw("+" + str(self.game.follower.statGrowth["maxBP"]), (1200, 370), anchor=(1, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50)

            ptext.draw(str(self.game.follower.stats["pow"]),
                       (925, 465), anchor=(0, 0.5), color=(253, 163, 5), gcolor=(253, 243, 31), fontname=superMario256,
                       owidth=0.7, surf=self.game.screen, fontsize=50)
            if add:
                ptext.draw("+" + str(self.game.follower.statGrowth["pow"]), (1200, 465), anchor=(1, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50)

            ptext.draw(str(self.game.follower.stats["def"]),
                       (925, 560), anchor=(0, 0.5), color=(253, 163, 5), gcolor=(253, 243, 31), fontname=superMario256,
                       owidth=0.7, surf=self.game.screen, fontsize=50)
            if add:
                ptext.draw("+" + str(self.game.follower.statGrowth["def"]), (1200, 560), anchor=(1, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50)
        else:
            ptext.draw(str(self.game.follower.stats["level"] + 1), (324, 390), anchor=(0, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50)

            ptext.draw(str(self.game.follower.stats["maxHP"] + self.game.follower.statGrowth["maxHP"]), (925, 275), anchor=(0, 0.5), color=(253, 163, 5),
                       gcolor=(253, 243, 31), fontname=superMario256, owidth=0.7, surf=self.game.screen,
                       fontsize=50)

            ptext.draw(str(self.game.follower.stats["maxBP"] + self.game.follower.statGrowth["maxBP"]),
                       (925, 370), anchor=(0, 0.5), color=(253, 163, 5), gcolor=(253, 243, 31),
                       fontname=superMario256,
                       owidth=0.7, surf=self.game.screen, fontsize=50)

            ptext.draw(str(self.game.follower.stats["pow"] + self.game.follower.statGrowth["pow"]),
                       (925, 465), anchor=(0, 0.5), color=(253, 163, 5), gcolor=(253, 243, 31),
                       fontname=superMario256,
                       owidth=0.7, surf=self.game.screen, fontsize=50)

            ptext.draw(str(self.game.follower.stats["def"] + self.game.follower.statGrowth["def"]),
                       (925, 560), anchor=(0, 0.5), color=(253, 163, 5), gcolor=(253, 243, 31),
                       fontname=superMario256,
                       owidth=0.7, surf=self.game.screen, fontsize=50)
