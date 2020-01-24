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
                    self.map[name]['w'] = int(node.attrib.get('w'))
                    self.map[name]['h'] = int(node.attrib.get('h'))

    def get_image_rect(self, x, y, w, h):
        return self.spritesheet.subsurface(pg.Rect(x, y, w, h))

    def getImageName(self, name):
        rect = pg.Rect(self.map[name]['x'], self.map[name]['y'], self.map[name]['w'], self.map[name]['h'])
        return self.spritesheet.subsurface(rect)


class marioOverworld(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.walking = False
        self.facing = "up"
        self.loadImages()
        # self.image = pg.Surface((40, 40))
        self.image = self.standingFrames[0]
        # self.image.fill(red)
        self.lastUpdate = 0
        self.currentFrame = 0
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos = vec(x, y)

    def loadImages(self):
        sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")

        self.standingFrames = [sheet.getImageName("mario-luigi/mario_standing_up.png"),
                               sheet.getImageName("mario-luigi/mario_standing_down.png"),
                               sheet.getImageName("mario-luigi/mario_standing_left.png"),
                               sheet.getImageName("mario-luigi/mario_standing_right.png"),
                               sheet.getImageName("mario-luigi/mario_standing_downright.png"),
                               sheet.getImageName("mario-luigi/mario_standing_upright.png"),
                               sheet.getImageName("mario-luigi/mario_standing_downleft.png"),
                               sheet.getImageName("mario-luigi/mario_standing_upleft.png")]

        self.walkingFramesUp = [sheet.getImageName("mario-luigi/mario_walking_up_1.png"),
                                sheet.getImageName("mario-luigi/mario_walking_up_2.png"),
                                sheet.getImageName("mario-luigi/mario_walking_up_3.png"),
                                sheet.getImageName("mario-luigi/mario_walking_up_4.png"),
                                sheet.getImageName("mario-luigi/mario_walking_up_5.png"),
                                sheet.getImageName("mario-luigi/mario_walking_up_6.png"),
                                sheet.getImageName("mario-luigi/mario_walking_up_7.png"),
                                sheet.getImageName("mario-luigi/mario_walking_up_8.png"),
                                sheet.getImageName("mario-luigi/mario_walking_up_9.png"),
                                sheet.getImageName("mario-luigi/mario_walking_up_10.png"),
                                sheet.getImageName("mario-luigi/mario_walking_up_11.png"),
                                sheet.getImageName("mario-luigi/mario_walking_up_12.png")]

        self.walkingFramesUpright = [sheet.getImageName("mario-luigi/mario_walking_upright_1.png"),
                                     sheet.getImageName("mario-luigi/mario_walking_upright_2.png"),
                                     sheet.getImageName("mario-luigi/mario_walking_upright_3.png"),
                                     sheet.getImageName("mario-luigi/mario_walking_upright_4.png"),
                                     sheet.getImageName("mario-luigi/mario_walking_upright_5.png"),
                                     sheet.getImageName("mario-luigi/mario_walking_upright_6.png"),
                                     sheet.getImageName("mario-luigi/mario_walking_upright_7.png"),
                                     sheet.getImageName("mario-luigi/mario_walking_upright_8.png"),
                                     sheet.getImageName("mario-luigi/mario_walking_upright_9.png"),
                                     sheet.getImageName("mario-luigi/mario_walking_upright_10.png"),
                                     sheet.getImageName("mario-luigi/mario_walking_upright_11.png"),
                                     sheet.getImageName("mario-luigi/mario_walking_upright_12.png")]

        self.walkingFramesRight = [sheet.getImageName("mario-luigi/mario_walking_right_1.png"),
                                   sheet.getImageName("mario-luigi/mario_walking_right_2.png"),
                                   sheet.getImageName("mario-luigi/mario_walking_right_3.png"),
                                   sheet.getImageName("mario-luigi/mario_walking_right_4.png"),
                                   sheet.getImageName("mario-luigi/mario_walking_right_5.png"),
                                   sheet.getImageName("mario-luigi/mario_walking_right_6.png"),
                                   sheet.getImageName("mario-luigi/mario_walking_right_7.png"),
                                   sheet.getImageName("mario-luigi/mario_walking_right_8.png"),
                                   sheet.getImageName("mario-luigi/mario_walking_right_9.png"),
                                   sheet.getImageName("mario-luigi/mario_walking_right_10.png"),
                                   sheet.getImageName("mario-luigi/mario_walking_right_11.png"),
                                   sheet.getImageName("mario-luigi/mario_walking_right_12.png")]

        self.walkingFramesDownright = [sheet.getImageName("mario-luigi/mario_walking_downright_1.png"),
                                       sheet.getImageName("mario-luigi/mario_walking_downright_2.png"),
                                       sheet.getImageName("mario-luigi/mario_walking_downright_3.png"),
                                       sheet.getImageName("mario-luigi/mario_walking_downright_4.png"),
                                       sheet.getImageName("mario-luigi/mario_walking_downright_5.png"),
                                       sheet.getImageName("mario-luigi/mario_walking_downright_6.png"),
                                       sheet.getImageName("mario-luigi/mario_walking_downright_7.png"),
                                       sheet.getImageName("mario-luigi/mario_walking_downright_8.png"),
                                       sheet.getImageName("mario-luigi/mario_walking_downright_9.png"),
                                       sheet.getImageName("mario-luigi/mario_walking_downright_10.png"),
                                       sheet.getImageName("mario-luigi/mario_walking_downright_11.png"),
                                       sheet.getImageName("mario-luigi/mario_walking_downright_12.png")]

        self.walkingFramesDown = [sheet.getImageName("mario-luigi/mario_walking_down_1.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_down_2.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_down_3.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_down_4.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_down_5.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_down_6.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_down_7.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_down_8.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_down_9.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_down_10.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_down_11.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_down_12.png")]

        self.walkingFramesDownleft = [sheet.getImageName("mario-luigi/mario_walking_downleft_1.png"),
                                      sheet.getImageName("mario-luigi/mario_walking_downleft_2.png"),
                                      sheet.getImageName("mario-luigi/mario_walking_downleft_3.png"),
                                      sheet.getImageName("mario-luigi/mario_walking_downleft_4.png"),
                                      sheet.getImageName("mario-luigi/mario_walking_downleft_5.png"),
                                      sheet.getImageName("mario-luigi/mario_walking_downleft_6.png"),
                                      sheet.getImageName("mario-luigi/mario_walking_downleft_7.png"),
                                      sheet.getImageName("mario-luigi/mario_walking_downleft_8.png"),
                                      sheet.getImageName("mario-luigi/mario_walking_downleft_9.png"),
                                      sheet.getImageName("mario-luigi/mario_walking_downleft_10.png"),
                                      sheet.getImageName("mario-luigi/mario_walking_downleft_11.png"),
                                      sheet.getImageName("mario-luigi/mario_walking_downleft_12.png")]

        self.walkingFramesLeft = [sheet.getImageName("mario-luigi/mario_walking_left_1.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_left_2.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_left_3.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_left_4.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_left_5.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_left_6.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_left_7.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_left_8.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_left_9.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_left_10.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_left_11.png"),
                                  sheet.getImageName("mario-luigi/mario_walking_left_12.png")]

        self.walkingFramesUpleft = [sheet.getImageName("mario-luigi/mario_walking_upleft_1.png"),
                                    sheet.getImageName("mario-luigi/mario_walking_upleft_2.png"),
                                    sheet.getImageName("mario-luigi/mario_walking_upleft_3.png"),
                                    sheet.getImageName("mario-luigi/mario_walking_upleft_4.png"),
                                    sheet.getImageName("mario-luigi/mario_walking_upleft_5.png"),
                                    sheet.getImageName("mario-luigi/mario_walking_upleft_6.png"),
                                    sheet.getImageName("mario-luigi/mario_walking_upleft_7.png"),
                                    sheet.getImageName("mario-luigi/mario_walking_upleft_8.png"),
                                    sheet.getImageName("mario-luigi/mario_walking_upleft_9.png"),
                                    sheet.getImageName("mario-luigi/mario_walking_upleft_10.png"),
                                    sheet.getImageName("mario-luigi/mario_walking_upleft_11.png"),
                                    sheet.getImageName("mario-luigi/mario_walking_upleft_12.png")]

    def update(self):
        self.animate()
        keys = pg.key.get_pressed()
        if keys[pg.K_w] and keys[pg.K_d]:
            self.facing = "upright"
            self.pos.y -= playerSpeed / 2
            self.pos.x += playerSpeed
        if keys[pg.K_w] and keys[pg.K_a]:
            self.facing = "upleft"
            self.pos.y -= playerSpeed
            self.pos.x -= playerSpeed
        elif keys[pg.K_s] and keys[pg.K_d]:
            self.facing = "downright"
            self.pos.y += playerSpeed
            self.pos.x += playerSpeed
        elif keys[pg.K_s] and keys[pg.K_a]:
            self.facing = "downleft"
            self.pos.y += playerSpeed
            self.pos.x -= playerSpeed
        elif keys[pg.K_w]:
            self.facing = "up"
            self.pos.y -= playerSpeed
        elif keys[pg.K_a]:
            self.facing = "left"
            self.pos.x -= playerSpeed
        elif keys[pg.K_s]:
            self.facing = "down"
            self.pos.y += playerSpeed
        elif keys[pg.K_d]:
            self.facing = "right"
            self.pos.x += playerSpeed

        self.rect.center = self.pos

    def animate(self):
        now = pg.time.get_ticks()
        keys = pg.key.get_pressed()
        if keys[pg.K_w] and keys[pg.K_d]:
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.walkingFramesUpright):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesUpright))
                else:
                    self.currentFrame = 0
                center = self.rect.center
                self.image = self.walkingFramesUpright[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center
        if keys[pg.K_w] and keys[pg.K_a]:
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.walkingFramesUpleft):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesUpleft))
                else:
                    self.currentFrame = 0
                center = self.rect.center
                self.image = self.walkingFramesUpleft[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center
        elif keys[pg.K_s] and keys[pg.K_d]:
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.walkingFramesDownright):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesDownright))
                else:
                    self.currentFrame = 0
                center = self.rect.center
                self.image = self.walkingFramesDownright[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center
        elif keys[pg.K_s] and keys[pg.K_a]:
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.walkingFramesDownleft):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesDownleft))
                else:
                    self.currentFrame = 0
                center = self.rect.center
                self.image = self.walkingFramesDownleft[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center
        elif keys[pg.K_w]:
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.walkingFramesUp):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesUp))
                else:
                    self.currentFrame = 0
                center = self.rect.center
                self.image = self.walkingFramesUp[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center
        elif keys[pg.K_a]:
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.walkingFramesLeft):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesLeft))
                else:
                    self.currentFrame = 0
                center = self.rect.center
                self.image = self.walkingFramesLeft[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center
        elif keys[pg.K_s]:
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.walkingFramesDown):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesDown))
                else:
                    self.currentFrame = 0
                center = self.rect.center
                self.image = self.walkingFramesDown[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center
        elif keys[pg.K_d]:
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.walkingFramesRight):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesRight))
                else:
                    self.currentFrame = 0
                center = self.rect.center
                self.image = self.walkingFramesRight[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center
        else:
            if self.facing == "up":
                center = self.rect.center
                self.image = self.standingFrames[0]
                self.rect = self.image.get_rect()
                self.rect.center = center
            if self.facing == "down":
                center = self.rect.center
                self.image = self.standingFrames[1]
                self.rect = self.image.get_rect()
                self.rect.center = center
            if self.facing == "left":
                center = self.rect.center
                self.image = self.standingFrames[2]
                self.rect = self.image.get_rect()
                self.rect.center = center
            if self.facing == "right":
                center = self.rect.center
                self.image = self.standingFrames[3]
                self.rect = self.image.get_rect()
                self.rect.center = center
            if self.facing == "downright":
                center = self.rect.center
                self.image = self.standingFrames[4]
                self.rect = self.image.get_rect()
                self.rect.center = center
            if self.facing == "upright":
                center = self.rect.center
                self.image = self.standingFrames[5]
                self.rect = self.image.get_rect()
                self.rect.center = center
            if self.facing == "downleft":
                center = self.rect.center
                self.image = self.standingFrames[6]
                self.rect = self.image.get_rect()
                self.rect.center = center
            if self.facing == "upleft":
                center = self.rect.center
                self.image = self.standingFrames[7]
                self.rect = self.image.get_rect()
                self.rect.center = center

            self.currentFrame = 0
