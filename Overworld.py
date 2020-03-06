import collections as Q
from Libraries import ptext
import random
import xml.etree.ElementTree as ET
import pytweening as pt
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


class HammerCollisionMario(pg.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.collision.append(self)
        self.rect = pg.rect.Rect(-100, 100, 0, 0)


class HammerCollisionLuigi(pg.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.collision.append(self)
        self.rect = pg.rect.Rect(-100, 100, 0, 0)


class Hammer(pg.sprite.Sprite):
    def __init__(self, game, parent):
        pg.sprite.Sprite.__init__(self)
        self.alpha = 255
        self.lastUpdate = 0
        self.currentFrame = 0
        self.counter = 0
        self.game = game
        self.game.hammerSwingSound.play()
        self.hasPlayedHit = False
        self.dead = False
        self.parent = parent
        self.game.sprites.append(self)
        self.loadImages()
        self.image = self.leftFrames[0]
        self.imgRect = self.image.get_rect()
        self.imgRect.bottom = self.parent.imgRect.top
        self.imgRect.centerx = self.parent.imgRect.centerx
        self.rect = pg.rect.Rect(0, 0, 50, 25)
        if self.parent.facing == "up":
            self.rect.centerx = self.parent.rect.centerx
            self.rect.centery = self.parent.rect.centery - 30
        elif self.parent.facing == "down":
            self.rect.centerx = self.parent.rect.centerx
            self.rect.centery = self.parent.rect.centery + 30
        elif self.parent.facing == "left":
            self.rect.centerx = self.parent.rect.centerx - 55
            self.rect.centery = self.parent.rect.centery
        elif self.parent.facing == "right":
            self.rect.centerx = self.parent.rect.centerx + 55
            self.rect.centery = self.parent.rect.centery
        elif self.parent.facing == "upleft":
            self.rect.centerx = self.parent.rect.centerx - 25
            self.rect.centery = self.parent.rect.centery - 30
        elif self.parent.facing == "upright":
            self.rect.centerx = self.parent.rect.centerx + 35
            self.rect.centery = self.parent.rect.centery - 30
        elif self.parent.facing == "downleft":
            self.rect.centerx = self.parent.rect.centerx - 35
            self.rect.centery = self.parent.rect.centery + 25
        elif self.parent.facing == "downright":
            self.rect.centerx = self.parent.rect.centerx + 35
            self.rect.centery = self.parent.rect.centery + 25

        self.points = []
        for i in range(2 + 1):
            self.points.append(pt.getPointOnLine(self.imgRect.centerx, self.imgRect.centery, self.rect.centerx,
                                                 self.rect.top, (i / 2)))

    def loadImages(self):
        sheet = spritesheet("sprites/hammer.png", "sprites/hammer.xml")

        self.upFrames = [sheet.getImageName("up_1.png"),
                         sheet.getImageName("up_2.png"),
                         sheet.getImageName("up_3.png"),
                         sheet.getImageName("up_4.png"),
                         sheet.getImageName("up_5.png")]

        self.downFrames = [sheet.getImageName("down_1.png"),
                           sheet.getImageName("down_2.png"),
                           sheet.getImageName("down_3.png"),
                           sheet.getImageName("down_4.png"),
                           sheet.getImageName("down_5.png")]

        self.leftFrames = [sheet.getImageName("left_1.png"),
                           sheet.getImageName("left_2.png"),
                           sheet.getImageName("left_3.png"),
                           sheet.getImageName("left_4.png"),
                           sheet.getImageName("left_5.png")]

        self.rightFrames = [sheet.getImageName("right_1.png"),
                            sheet.getImageName("right_2.png"),
                            sheet.getImageName("right_3.png"),
                            sheet.getImageName("right_4.png"),
                            sheet.getImageName("right_5.png")]

        self.downleftFrames = [sheet.getImageName("downleft_1.png"),
                               sheet.getImageName("downleft_2.png"),
                               sheet.getImageName("downleft_3.png"),
                               sheet.getImageName("downleft_4.png"),
                               sheet.getImageName("downleft_5.png")]

        self.downrightFrames = [sheet.getImageName("downright_1.png"),
                                sheet.getImageName("downright_2.png"),
                                sheet.getImageName("downright_3.png"),
                                sheet.getImageName("downright_4.png"),
                                sheet.getImageName("downright_5.png")]

        self.upleftFrames = [sheet.getImageName("upleft_1.png"),
                             sheet.getImageName("upleft_2.png"),
                             sheet.getImageName("upleft_3.png"),
                             sheet.getImageName("upleft_4.png"),
                             sheet.getImageName("upleft_5.png")]

        self.uprightFrames = [sheet.getImageName("upright_1.png"),
                              sheet.getImageName("upright_2.png"),
                              sheet.getImageName("upright_3.png"),
                              sheet.getImageName("upright_4.png"),
                              sheet.getImageName("upright_5.png")]

    def update(self):
        self.animate()
        if self.parent == self.game.player:
            self.game.playerHammer.rect = self.imgRect
        else:
            self.game.followerHammer.rect = self.imgRect

        if self.counter < len(self.points) - 1 and self.currentFrame > 2:
            self.counter += 1
        elif not self.hasPlayedHit and self.currentFrame > 2:
            self.game.hammerHitSound.play()
            self.hasPlayedHit = True

        self.imgRect.center = self.points[self.counter]
        if not self.parent.hammering or self.parent.hit:
            self.parent.isHammer = None
            self.game.sprites.remove(self)
            if self.parent == self.game.player:
                self.game.playerHammer.rect = pg.rect.Rect(-100, 100, 0, 0)
            else:
                self.game.followerHammer.rect = pg.rect.Rect(-100, 100, 0, 0)

    def animate(self):
        now = pg.time.get_ticks()
        if self.parent.facing == "up":
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.upFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.currentFrame = 4
                center = self.imgRect.center
                self.image = self.upFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.parent.facing == "down":
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.upFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.currentFrame = 4
                center = self.imgRect.center
                self.image = self.downFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.parent.facing == "left":
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.upFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.currentFrame = 4
                center = self.imgRect.center
                self.image = self.leftFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.parent.facing == "right":
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.upFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.currentFrame = 4
                center = self.imgRect.center
                self.image = self.rightFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.parent.facing == "upleft":
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.upFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.currentFrame = 4
                center = self.imgRect.center
                self.image = self.upleftFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.parent.facing == "upright":
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.upFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.currentFrame = 4
                center = self.imgRect.center
                self.image = self.uprightFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.parent.facing == "downleft":
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.upFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.currentFrame = 4
                center = self.imgRect.center
                self.image = self.downleftFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.parent.facing == "downright":
            if now - self.lastUpdate > 25:
                self.lastUpdate = now
                if self.currentFrame < len(self.upFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.currentFrame = 4
                center = self.imgRect.center
                self.image = self.downrightFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center


class MarioCollision(pg.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.collision.append(self)
        self.rect = self.game.player.imgRect
        self.rect.center = self.game.player.imgRect.center

    def update(self):
        self.rect = self.game.player.imgRect
        self.rect.center = self.game.player.imgRect.center


class LuigiCollision(pg.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.collision.append(self)
        self.rect = self.game.follower.imgRect
        self.rect.center = self.game.follower.imgRect.center

    def update(self):
        self.rect = self.game.follower.imgRect
        self.rect.center = self.game.follower.imgRect.center


class Mario(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.hit = False
        self.dead = False
        self.hammering = False
        self.canMove = True
        self.canBeHit = True
        self.hitTime = 0
        self.ability = 0
        self.prevAbility = 12
        self.abilities = ["jump", "interact", "talk"]
        self.alpha = 255
        self.stepSound = pg.mixer.Sound("sounds/coin.ogg")
        self.walking = False
        self.jumping = False
        self.isHammer = None
        self.jumpTimer = 0
        self.airTimer = 0
        self.facing = "right"
        self.going = "irrelevent"
        self.loadImages()
        self.image = self.standingFrames[0]
        self.shadow = self.shadowFrames["normal"]
        self.lastUpdate = 0
        self.currentFrame = 0
        self.speed = playerSpeed
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)
        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.left = x
        self.vx, self.vy = 0, 0

        self.stats = {"level": 1, "maxHP": 10, "maxBP": 5, "pow": 2, "def": 0, "stache": 3, "hp": 10, "bp": 5, "exp": 0}

    def loadImages(self):
        sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")

        self.standingFrames = [sheet.getImageName("mario_standing_up.png"),
                               sheet.getImageName("mario_standing_down.png"),
                               sheet.getImageName("mario_standing_left.png"),
                               sheet.getImageName("mario_standing_right.png"),
                               sheet.getImageName("mario_standing_downright.png"),
                               sheet.getImageName("mario_standing_upright.png"),
                               sheet.getImageName("mario_standing_downleft.png"),
                               sheet.getImageName("mario_standing_upleft.png")]

        self.walkingFramesUp = [sheet.getImageName("mario_walking_up_1.png"),
                                sheet.getImageName("mario_walking_up_2.png"),
                                sheet.getImageName("mario_walking_up_3.png"),
                                sheet.getImageName("mario_walking_up_4.png"),
                                sheet.getImageName("mario_walking_up_5.png"),
                                sheet.getImageName("mario_walking_up_6.png"),
                                sheet.getImageName("mario_walking_up_7.png"),
                                sheet.getImageName("mario_walking_up_8.png"),
                                sheet.getImageName("mario_walking_up_9.png"),
                                sheet.getImageName("mario_walking_up_10.png"),
                                sheet.getImageName("mario_walking_up_11.png"),
                                sheet.getImageName("mario_walking_up_12.png")]

        self.walkingFramesUpright = [sheet.getImageName("mario_walking_upright_1.png"),
                                     sheet.getImageName("mario_walking_upright_2.png"),
                                     sheet.getImageName("mario_walking_upright_3.png"),
                                     sheet.getImageName("mario_walking_upright_4.png"),
                                     sheet.getImageName("mario_walking_upright_5.png"),
                                     sheet.getImageName("mario_walking_upright_6.png"),
                                     sheet.getImageName("mario_walking_upright_7.png"),
                                     sheet.getImageName("mario_walking_upright_8.png"),
                                     sheet.getImageName("mario_walking_upright_9.png"),
                                     sheet.getImageName("mario_walking_upright_10.png"),
                                     sheet.getImageName("mario_walking_upright_11.png"),
                                     sheet.getImageName("mario_walking_upright_12.png")]

        self.walkingFramesRight = [sheet.getImageName("mario_walking_right_1.png"),
                                   sheet.getImageName("mario_walking_right_2.png"),
                                   sheet.getImageName("mario_walking_right_3.png"),
                                   sheet.getImageName("mario_walking_right_4.png"),
                                   sheet.getImageName("mario_walking_right_5.png"),
                                   sheet.getImageName("mario_walking_right_6.png"),
                                   sheet.getImageName("mario_walking_right_7.png"),
                                   sheet.getImageName("mario_walking_right_8.png"),
                                   sheet.getImageName("mario_walking_right_9.png"),
                                   sheet.getImageName("mario_walking_right_10.png"),
                                   sheet.getImageName("mario_walking_right_11.png"),
                                   sheet.getImageName("mario_walking_right_12.png")]

        self.walkingFramesDownright = [sheet.getImageName("mario_walking_downright_1.png"),
                                       sheet.getImageName("mario_walking_downright_2.png"),
                                       sheet.getImageName("mario_walking_downright_3.png"),
                                       sheet.getImageName("mario_walking_downright_4.png"),
                                       sheet.getImageName("mario_walking_downright_5.png"),
                                       sheet.getImageName("mario_walking_downright_6.png"),
                                       sheet.getImageName("mario_walking_downright_7.png"),
                                       sheet.getImageName("mario_walking_downright_8.png"),
                                       sheet.getImageName("mario_walking_downright_9.png"),
                                       sheet.getImageName("mario_walking_downright_10.png"),
                                       sheet.getImageName("mario_walking_downright_11.png"),
                                       sheet.getImageName("mario_walking_downright_12.png")]

        self.walkingFramesDown = [sheet.getImageName("mario_walking_down_1.png"),
                                  sheet.getImageName("mario_walking_down_2.png"),
                                  sheet.getImageName("mario_walking_down_3.png"),
                                  sheet.getImageName("mario_walking_down_4.png"),
                                  sheet.getImageName("mario_walking_down_5.png"),
                                  sheet.getImageName("mario_walking_down_6.png"),
                                  sheet.getImageName("mario_walking_down_7.png"),
                                  sheet.getImageName("mario_walking_down_8.png"),
                                  sheet.getImageName("mario_walking_down_9.png"),
                                  sheet.getImageName("mario_walking_down_10.png"),
                                  sheet.getImageName("mario_walking_down_11.png"),
                                  sheet.getImageName("mario_walking_down_12.png")]

        self.walkingFramesDownleft = [sheet.getImageName("mario_walking_downleft_1.png"),
                                      sheet.getImageName("mario_walking_downleft_2.png"),
                                      sheet.getImageName("mario_walking_downleft_3.png"),
                                      sheet.getImageName("mario_walking_downleft_4.png"),
                                      sheet.getImageName("mario_walking_downleft_5.png"),
                                      sheet.getImageName("mario_walking_downleft_6.png"),
                                      sheet.getImageName("mario_walking_downleft_7.png"),
                                      sheet.getImageName("mario_walking_downleft_8.png"),
                                      sheet.getImageName("mario_walking_downleft_9.png"),
                                      sheet.getImageName("mario_walking_downleft_10.png"),
                                      sheet.getImageName("mario_walking_downleft_11.png"),
                                      sheet.getImageName("mario_walking_downleft_12.png")]

        self.walkingFramesLeft = [sheet.getImageName("mario_walking_left_1.png"),
                                  sheet.getImageName("mario_walking_left_2.png"),
                                  sheet.getImageName("mario_walking_left_3.png"),
                                  sheet.getImageName("mario_walking_left_4.png"),
                                  sheet.getImageName("mario_walking_left_5.png"),
                                  sheet.getImageName("mario_walking_left_6.png"),
                                  sheet.getImageName("mario_walking_left_7.png"),
                                  sheet.getImageName("mario_walking_left_8.png"),
                                  sheet.getImageName("mario_walking_left_9.png"),
                                  sheet.getImageName("mario_walking_left_10.png"),
                                  sheet.getImageName("mario_walking_left_11.png"),
                                  sheet.getImageName("mario_walking_left_12.png")]

        self.walkingFramesUpleft = [sheet.getImageName("mario_walking_upleft_1.png"),
                                    sheet.getImageName("mario_walking_upleft_2.png"),
                                    sheet.getImageName("mario_walking_upleft_3.png"),
                                    sheet.getImageName("mario_walking_upleft_4.png"),
                                    sheet.getImageName("mario_walking_upleft_5.png"),
                                    sheet.getImageName("mario_walking_upleft_6.png"),
                                    sheet.getImageName("mario_walking_upleft_7.png"),
                                    sheet.getImageName("mario_walking_upleft_8.png"),
                                    sheet.getImageName("mario_walking_upleft_9.png"),
                                    sheet.getImageName("mario_walking_upleft_10.png"),
                                    sheet.getImageName("mario_walking_upleft_11.png"),
                                    sheet.getImageName("mario_walking_upleft_12.png")]

        self.jumpingUpFrames = [sheet.getImageName("mario_jumping_up_up.png"),
                                sheet.getImageName("mario_jumping_up_down.png"),
                                sheet.getImageName("mario_jumping_up_left.png"),
                                sheet.getImageName("mario_jumping_up_right.png"),
                                sheet.getImageName("mario_jumping_up_upleft.png"),
                                sheet.getImageName("mario_jumping_up_upright.png"),
                                sheet.getImageName("mario_jumping_up_downleft.png"),
                                sheet.getImageName("mario_jumping_up_downright.png")]

        self.jumpingDownFrames = [sheet.getImageName("mario_jumping_down_up.png"),
                                  sheet.getImageName("mario_jumping_down_down.png"),
                                  sheet.getImageName("mario_jumping_down_left.png"),
                                  sheet.getImageName("mario_jumping_down_right.png"),
                                  sheet.getImageName("mario_jumping_down_upleft.png"),
                                  sheet.getImageName("mario_jumping_down_upright.png"),
                                  sheet.getImageName("mario_jumping_down_downleft.png"),
                                  sheet.getImageName("mario_jumping_down_downright.png")]

        self.deadFramesRight = [sheet.getImageName("mario_dead_right_1.png"),
                                sheet.getImageName("mario_dead_right_2.png"),
                                sheet.getImageName("mario_dead_right_3.png"),
                                sheet.getImageName("mario_dead_right_4.png"), ]

        self.deadFramesLeft = [sheet.getImageName("mario_dead_left_1.png"),
                               sheet.getImageName("mario_dead_left_2.png"),
                               sheet.getImageName("mario_dead_left_3.png"),
                               sheet.getImageName("mario_dead_left_4.png"), ]

        self.deadFramesUp = [sheet.getImageName("mario_dead_up_1.png"),
                             sheet.getImageName("mario_dead_up_2.png"),
                             sheet.getImageName("mario_dead_up_3.png"),
                             sheet.getImageName("mario_dead_up_4.png")]

        self.deadFramesDown = [sheet.getImageName("mario_dead_down_1.png"),
                               sheet.getImageName("mario_dead_down_2.png"),
                               sheet.getImageName("mario_dead_down_3.png"),
                               sheet.getImageName("mario_dead_down_4.png")]

        self.hammerFramesUp = [sheet.getImageName("mario_hammering_up_1.png"),
                               sheet.getImageName("mario_hammering_up_2.png"),
                               sheet.getImageName("mario_hammering_up_3.png"),
                               sheet.getImageName("mario_hammering_up_4.png"),
                               sheet.getImageName("mario_hammering_up_5.png"),
                               sheet.getImageName("mario_hammering_up_6.png"),
                               sheet.getImageName("mario_hammering_up_7.png"),
                               sheet.getImageName("mario_hammering_up_8.png"),
                               sheet.getImageName("mario_hammering_up_9.png"),
                               sheet.getImageName("mario_hammering_up_10.png"),
                               sheet.getImageName("mario_hammering_up_11.png"),
                               sheet.getImageName("mario_hammering_up_12.png"),
                               sheet.getImageName("mario_hammering_up_13.png")]

        self.hammerFramesDown = [sheet.getImageName("mario_hammering_down_1.png"),
                                 sheet.getImageName("mario_hammering_down_2.png"),
                                 sheet.getImageName("mario_hammering_down_3.png"),
                                 sheet.getImageName("mario_hammering_down_4.png"),
                                 sheet.getImageName("mario_hammering_down_5.png"),
                                 sheet.getImageName("mario_hammering_down_6.png"),
                                 sheet.getImageName("mario_hammering_down_7.png"),
                                 sheet.getImageName("mario_hammering_down_8.png"),
                                 sheet.getImageName("mario_hammering_down_9.png"),
                                 sheet.getImageName("mario_hammering_down_10.png"),
                                 sheet.getImageName("mario_hammering_down_11.png"),
                                 sheet.getImageName("mario_hammering_down_12.png"),
                                 sheet.getImageName("mario_hammering_down_13.png")]

        self.hammerFramesLeft = [sheet.getImageName("mario_hammering_left_1.png"),
                                 sheet.getImageName("mario_hammering_left_2.png"),
                                 sheet.getImageName("mario_hammering_left_3.png"),
                                 sheet.getImageName("mario_hammering_left_4.png"),
                                 sheet.getImageName("mario_hammering_left_5.png"),
                                 sheet.getImageName("mario_hammering_left_6.png"),
                                 sheet.getImageName("mario_hammering_left_7.png"),
                                 sheet.getImageName("mario_hammering_left_8.png"),
                                 sheet.getImageName("mario_hammering_left_9.png"),
                                 sheet.getImageName("mario_hammering_left_10.png"),
                                 sheet.getImageName("mario_hammering_left_11.png"),
                                 sheet.getImageName("mario_hammering_left_12.png"),
                                 sheet.getImageName("mario_hammering_left_13.png")]

        self.hammerFramesRight = [sheet.getImageName("mario_hammering_right_1.png"),
                                  sheet.getImageName("mario_hammering_right_2.png"),
                                  sheet.getImageName("mario_hammering_right_3.png"),
                                  sheet.getImageName("mario_hammering_right_4.png"),
                                  sheet.getImageName("mario_hammering_right_5.png"),
                                  sheet.getImageName("mario_hammering_right_6.png"),
                                  sheet.getImageName("mario_hammering_right_7.png"),
                                  sheet.getImageName("mario_hammering_right_8.png"),
                                  sheet.getImageName("mario_hammering_right_9.png"),
                                  sheet.getImageName("mario_hammering_right_10.png"),
                                  sheet.getImageName("mario_hammering_right_11.png"),
                                  sheet.getImageName("mario_hammering_right_12.png"),
                                  sheet.getImageName("mario_hammering_right_13.png")]

        self.hammerFramesUpleft = [sheet.getImageName("mario_hammering_upleft_1.png"),
                                   sheet.getImageName("mario_hammering_upleft_2.png"),
                                   sheet.getImageName("mario_hammering_upleft_3.png"),
                                   sheet.getImageName("mario_hammering_upleft_4.png"),
                                   sheet.getImageName("mario_hammering_upleft_5.png"),
                                   sheet.getImageName("mario_hammering_upleft_6.png"),
                                   sheet.getImageName("mario_hammering_upleft_7.png"),
                                   sheet.getImageName("mario_hammering_upleft_8.png"),
                                   sheet.getImageName("mario_hammering_upleft_9.png"),
                                   sheet.getImageName("mario_hammering_upleft_10.png"),
                                   sheet.getImageName("mario_hammering_upleft_11.png"),
                                   sheet.getImageName("mario_hammering_upleft_12.png"),
                                   sheet.getImageName("mario_hammering_upleft_13.png")]

        self.hammerFramesUpright = [sheet.getImageName("mario_hammering_upright_1.png"),
                                    sheet.getImageName("mario_hammering_upright_2.png"),
                                    sheet.getImageName("mario_hammering_upright_3.png"),
                                    sheet.getImageName("mario_hammering_upright_4.png"),
                                    sheet.getImageName("mario_hammering_upright_5.png"),
                                    sheet.getImageName("mario_hammering_upright_6.png"),
                                    sheet.getImageName("mario_hammering_upright_7.png"),
                                    sheet.getImageName("mario_hammering_upright_8.png"),
                                    sheet.getImageName("mario_hammering_upright_9.png"),
                                    sheet.getImageName("mario_hammering_upright_10.png"),
                                    sheet.getImageName("mario_hammering_upright_11.png"),
                                    sheet.getImageName("mario_hammering_upright_12.png"),
                                    sheet.getImageName("mario_hammering_upright_13.png")]

        self.hammerFramesDownleft = [sheet.getImageName("mario_hammering_downleft_1.png"),
                                     sheet.getImageName("mario_hammering_downleft_2.png"),
                                     sheet.getImageName("mario_hammering_downleft_3.png"),
                                     sheet.getImageName("mario_hammering_downleft_4.png"),
                                     sheet.getImageName("mario_hammering_downleft_5.png"),
                                     sheet.getImageName("mario_hammering_downleft_6.png"),
                                     sheet.getImageName("mario_hammering_downleft_7.png"),
                                     sheet.getImageName("mario_hammering_downleft_8.png"),
                                     sheet.getImageName("mario_hammering_downleft_9.png"),
                                     sheet.getImageName("mario_hammering_downleft_10.png"),
                                     sheet.getImageName("mario_hammering_downleft_11.png"),
                                     sheet.getImageName("mario_hammering_downleft_12.png"),
                                     sheet.getImageName("mario_hammering_downleft_13.png")]

        self.hammerFramesDownright = [sheet.getImageName("mario_hammering_downright_1.png"),
                                      sheet.getImageName("mario_hammering_downright_2.png"),
                                      sheet.getImageName("mario_hammering_downright_3.png"),
                                      sheet.getImageName("mario_hammering_downright_4.png"),
                                      sheet.getImageName("mario_hammering_downright_5.png"),
                                      sheet.getImageName("mario_hammering_downright_6.png"),
                                      sheet.getImageName("mario_hammering_downright_7.png"),
                                      sheet.getImageName("mario_hammering_downright_8.png"),
                                      sheet.getImageName("mario_hammering_downright_9.png"),
                                      sheet.getImageName("mario_hammering_downright_10.png"),
                                      sheet.getImageName("mario_hammering_downright_11.png"),
                                      sheet.getImageName("mario_hammering_downright_12.png"),
                                      sheet.getImageName("mario_hammering_downright_13.png")]

        self.hitFrames = {"up": sheet.getImageName("mario_hit_up.png"),
                          "down": sheet.getImageName("mario_hit_down.png"),
                          "left": sheet.getImageName("mario_hit_left.png"),
                          "right": sheet.getImageName("mario_hit_right.png"),
                          "downright": sheet.getImageName("mario_hit_downright.png"),
                          "upright": sheet.getImageName("mario_hit_upright.png"),
                          "downleft": sheet.getImageName("mario_hit_downleft.png"),
                          "upleft": sheet.getImageName("mario_hit_upleft.png")}

        self.shadowFrames = {"normal": sheet.getImageName("shadow.png"),
                             "dead horizontal": sheet.getImageName("dead_shadow_horizontal.png"),
                             "dead vertical": sheet.getImageName("dead_shadow_vertical.png")}

    def wallCollisions(self, group, vx=0, vy=0):
        for wall in group:
            if pg.sprite.collide_rect(self, wall):
                if vx > 0:
                    self.rect.right = wall.rect.left
                    self.vx = 0
                    self.walking = False
                if vx < 0:
                    self.rect.left = wall.rect.right
                    self.vx = 0
                    self.walking = False
                if vy < 0:
                    self.rect.top = wall.rect.bottom
                    self.vy = 0
                    self.walking = False
                if vy > 0:
                    self.rect.bottom = wall.rect.top
                    self.vy = 0
                    self.walking = False

    def jump(self):
        if self.jumpTimer < jumpHeight and self.airTimer == 0:
            self.jumpTimer += 0.9
            self.going = "up"
        elif self.jumpTimer >= jumpHeight:
            self.airTimer += 1
        if self.airTimer >= airTime and self.jumpTimer != 0:
            self.jumpTimer -= 0.9
            self.going = "down"
        if self.jumpTimer <= 0 and self.airTimer != 0:
            self.jumping = False
        jumpOffset = self.jumpTimer * jumpHeight
        self.imgRect.bottom = (self.rect.bottom - 5) - jumpOffset

    def hammer(self):
        if self.isHammer == None:
            self.isHammer = Hammer(self.game, self)
        self.walking = False
        if self.currentFrame < len(self.hammerFramesLeft) - 1:
            pass
        else:
            self.currentFrame = 0
            self.hammering = False

    def update(self):
        self.animate()

        if self.stats["hp"] < 0:
            self.stats["hp"] = 0
        if self.stats["hp"] == 0:
            self.dead = True

        now = pg.time.get_ticks()
        keys = pg.key.get_pressed()
        self.vx, self.vy = 0, 0

        hits = pg.sprite.spritecollideany(self, self.game.npcs, pg.sprite.collide_rect_ratio(1.1))

        if not self.dead and self.canMove and not self.hammering:
            if not self.hit and not self.game.follower.hit and not self.game.follower.hammering:
                if self.jumping and not hits:
                    if keys[pg.K_w]:
                        self.vy = -playerSpeed
                    if keys[pg.K_a]:
                        self.vx = -playerSpeed
                    if keys[pg.K_s]:
                        self.vy = playerSpeed
                    if keys[pg.K_d]:
                        self.vx = playerSpeed
                elif not self.jumping:
                    if keys[pg.K_w]:
                        self.vy = -playerSpeed
                    if keys[pg.K_a]:
                        self.vx = -playerSpeed
                    if keys[pg.K_s]:
                        self.vy = playerSpeed
                    if keys[pg.K_d]:
                        self.vx = playerSpeed
                else:
                    self.walking = False
                for event in self.game.event:
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_m:
                            if self.ability == 0:
                                if not self.jumping and not self.hit and not self.dead and self.canMove:
                                    self.jumping = True
                                    self.jumpTimer = 1
                                    self.airTimer = 0
                                    self.game.jumpSound.play()
                            elif self.ability == 1:
                                if not self.hammering and not self.hit and not self.dead and self.canMove:
                                    self.hammering = True
                                    self.currentFrame = 0
                        if event.key == pg.K_SPACE:
                            if not self.jumping and not self.hit and not self.dead and self.canMove:
                                self.jumping = True
                                self.jumpTimer = 1
                                self.airTimer = 0
                                self.game.jumpSound.play()
                        if event.key == pg.K_LSHIFT:
                            if len(self.abilities) > 3:
                                self.game.abilityAdvanceSound.play()
                            self.ability = (self.ability + 1) % (len(self.abilities) - 2)
                            print(self.abilities[self.ability])
                        if event.key == pg.K_h:
                            if len(self.abilities) == 3:
                                self.abilities = ["jump", "hammer", "interact", "talk"]
                            else:
                                self.abilities = ["jump", "interact", "talk"]

        hits = pg.sprite.spritecollideany(self, self.game.npcs, pg.sprite.collide_rect_ratio(1.1))
        if hits:
            if hits.canTalk:
                if self.prevAbility == 12:
                    self.prevAbility = self.ability
                self.ability = len(self.abilities) - 1
        else:
            if self.prevAbility != 12:
                self.ability = self.prevAbility
                self.prevAbility = 12

        if self.hit:
            if self.hammering:
                self.hammering = False
            if now - self.hitTime > 250:
                self.hit = False

        if not self.canBeHit and not self.dead:
            if now % 2 == 0 and not self.hit:
                self.alpha = 0
            else:
                self.alpha = 255
            if now - self.hitTime > 1000:
                self.alpha = 255
                self.canBeHit = True

        self.rect.x += self.vx
        self.wallCollisions(self.game.walls, self.vx)
        if not self.jumping:
            self.wallCollisions(self.game.npcs, self.vx)
        self.rect.y += self.vy
        self.wallCollisions(self.game.walls, 0, self.vy)
        if not self.jumping:
            self.wallCollisions(self.game.npcs, 0, self.vy)

        if self.rect.x > self.game.map.width + 60:
            self.rect.x = -60
        if self.rect.x < -60:
            self.rect.x = self.game.map.width + 60
        if self.rect.y > self.game.map.height + 100:
            self.rect.y = -100
        if self.rect.y < -100:
            self.rect.y = self.game.map.height + 100

        if not self.jumping:
            self.imgRect.bottom = self.rect.bottom - 5
            self.imgRect.centerx = self.rect.centerx
        else:
            self.jump()
            self.imgRect.centerx = self.rect.centerx
        if self.hammering:
            self.hammer()

        if self.game.follower.hammering:
            self.walking = False

    def animate(self):
        now = pg.time.get_ticks()
        keys = pg.key.get_pressed()
        if self.canMove:
            if not self.dead:
                if self.hit:
                    self.walking = False
                    if self.facing == "up":
                        center = self.imgRect.center
                        self.image = self.hitFrames["up"]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    elif self.facing == "down":
                        center = self.imgRect.center
                        self.image = self.hitFrames["down"]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    elif self.facing == "left":
                        center = self.imgRect.center
                        self.image = self.hitFrames["left"]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    elif self.facing == "right":
                        center = self.imgRect.center
                        self.image = self.hitFrames["right"]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    elif self.facing == "downleft":
                        center = self.imgRect.center
                        self.image = self.hitFrames["downleft"]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    elif self.facing == "downright":
                        center = self.imgRect.center
                        self.image = self.hitFrames["downright"]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    elif self.facing == "upleft":
                        center = self.imgRect.center
                        self.image = self.hitFrames["upleft"]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    elif self.facing == "upright":
                        center = self.imgRect.center
                        self.image = self.hitFrames["upright"]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.hammering:
                    if self.facing == "left":
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.hammerFramesLeft) + 1:
                                self.currentFrame = (self.currentFrame + 1)
                            center = self.imgRect.center
                            self.image = self.hammerFramesLeft[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                    elif self.facing == "right":
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.hammerFramesLeft) + 1:
                                self.currentFrame = (self.currentFrame + 1)
                            center = self.imgRect.center
                            self.image = self.hammerFramesRight[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                    elif self.facing == "up":
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.hammerFramesLeft) + 1:
                                self.currentFrame = (self.currentFrame + 1)
                            center = self.imgRect.center
                            self.image = self.hammerFramesUp[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                    elif self.facing == "down":
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.hammerFramesLeft) + 1:
                                self.currentFrame = (self.currentFrame + 1)
                            center = self.imgRect.center
                            self.image = self.hammerFramesDown[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                    elif self.facing == "upleft":
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.hammerFramesLeft) + 1:
                                self.currentFrame = (self.currentFrame + 1)
                            center = self.imgRect.center
                            self.image = self.hammerFramesUpleft[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                    elif self.facing == "upright":
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.hammerFramesLeft) + 1:
                                self.currentFrame = (self.currentFrame + 1)
                            center = self.imgRect.center
                            self.image = self.hammerFramesUpright[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                    elif self.facing == "downleft":
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.hammerFramesLeft) + 1:
                                self.currentFrame = (self.currentFrame + 1)
                            center = self.imgRect.center
                            self.image = self.hammerFramesDownleft[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                    elif self.facing == "downright":
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.hammerFramesLeft) + 1:
                                self.currentFrame = (self.currentFrame + 1)
                            center = self.imgRect.center
                            self.image = self.hammerFramesDownright[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                elif not self.jumping:
                    if keys[pg.K_w] and keys[pg.K_d]:
                        self.facing = "upright"
                        self.walking = True
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.walkingFramesUpright):
                                self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesUpright))
                            else:
                                self.currentFrame = 0
                            center = self.imgRect.center
                            self.image = self.walkingFramesUpright[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                    elif keys[pg.K_w] and keys[pg.K_a]:
                        self.facing = "upleft"
                        self.walking = True
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.walkingFramesUpleft):
                                self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesUpleft))
                            else:
                                self.currentFrame = 0
                            center = self.imgRect.center
                            self.image = self.walkingFramesUpleft[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                    elif keys[pg.K_s] and keys[pg.K_d]:
                        self.facing = "downright"
                        self.walking = True
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.walkingFramesDownright):
                                self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesDownright))
                            else:
                                self.currentFrame = 0
                            center = self.imgRect.center
                            self.image = self.walkingFramesDownright[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                    elif keys[pg.K_s] and keys[pg.K_a]:
                        self.facing = "downleft"
                        self.walking = True
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.walkingFramesDownleft):
                                self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesDownleft))
                            else:
                                self.currentFrame = 0
                            center = self.imgRect.center
                            self.image = self.walkingFramesDownleft[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                    elif keys[pg.K_w]:
                        self.facing = "up"
                        self.walking = True
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.walkingFramesUp):
                                self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesUp))
                            else:
                                self.currentFrame = 0
                            center = self.imgRect.center
                            self.image = self.walkingFramesUp[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                    elif keys[pg.K_a]:
                        self.facing = "left"
                        self.walking = True
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.walkingFramesLeft):
                                self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesLeft))
                            else:
                                self.currentFrame = 0
                            center = self.imgRect.center
                            self.image = self.walkingFramesLeft[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                    elif keys[pg.K_s]:
                        self.facing = "down"
                        self.walking = True
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.walkingFramesDown):
                                self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesDown))
                            else:
                                self.currentFrame = 0
                            center = self.imgRect.center
                            self.image = self.walkingFramesDown[self.currentFrame]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                    elif keys[pg.K_d]:
                        self.facing = "right"
                        self.walking = True
                        if now - self.lastUpdate > 25:
                            self.lastUpdate = now
                            if self.currentFrame < len(self.walkingFramesRight):
                                self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesRight))
                            else:
                                self.currentFrame = 0
                        center = self.imgRect.center
                        self.image = self.walkingFramesRight[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    else:
                        if self.facing == "up":
                            center = self.imgRect.center
                            self.image = self.standingFrames[0]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        if self.facing == "down":
                            center = self.imgRect.center
                            self.image = self.standingFrames[1]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        if self.facing == "left":
                            center = self.imgRect.center
                            self.image = self.standingFrames[2]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        if self.facing == "right":
                            center = self.imgRect.center
                            self.image = self.standingFrames[3]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        if self.facing == "downright":
                            center = self.imgRect.center
                            self.image = self.standingFrames[4]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        if self.facing == "upright":
                            center = self.imgRect.center
                            self.image = self.standingFrames[5]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        if self.facing == "downleft":
                            center = self.imgRect.center
                            self.image = self.standingFrames[6]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        if self.facing == "upleft":
                            center = self.imgRect.center
                            self.image = self.standingFrames[7]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center

                        self.currentFrame = 0
                        self.walking = False
                else:
                    if self.going == "up":
                        if keys[pg.K_w] and keys[pg.K_d]:
                            self.facing = "upright"
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[5]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif keys[pg.K_w] and keys[pg.K_a]:
                            self.facing = "upleft"
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[4]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif keys[pg.K_s] and keys[pg.K_d]:
                            self.facing = "downright"
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[7]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif keys[pg.K_s] and keys[pg.K_a]:
                            self.facing = "downleft"
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[6]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif keys[pg.K_w]:
                            self.facing = "up"
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[0]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif keys[pg.K_s]:
                            self.facing = "down"
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[1]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif keys[pg.K_a]:
                            self.facing = "left"
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[2]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif keys[pg.K_d]:
                            self.facing = "right"
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[3]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif self.facing == "upright":
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[5]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                        elif self.facing == "upleft":
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[4]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                        elif self.facing == "downright":
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[7]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                        elif self.facing == "downleft":
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[6]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                        elif self.facing == "up":
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[0]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                        elif self.facing == "down":
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[1]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                        elif self.facing == "left":
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[2]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                        elif self.facing == "right":
                            center = self.imgRect.center
                            self.image = self.jumpingUpFrames[3]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                    else:
                        if keys[pg.K_w] and keys[pg.K_d]:
                            self.facing = "upright"
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[5]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif keys[pg.K_w] and keys[pg.K_a]:
                            self.facing = "upleft"
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[4]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif keys[pg.K_s] and keys[pg.K_d]:
                            self.facing = "downright"
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[7]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif keys[pg.K_s] and keys[pg.K_a]:
                            self.facing = "downleft"
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[6]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif keys[pg.K_w]:
                            self.facing = "up"
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[0]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif keys[pg.K_s]:
                            self.facing = "down"
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[1]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif keys[pg.K_a]:
                            self.facing = "left"
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[2]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif keys[pg.K_d]:
                            self.facing = "right"
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[3]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = True
                        elif self.facing == "upright":
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[5]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                        elif self.facing == "upleft":
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[4]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                        elif self.facing == "downright":
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[7]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                        elif self.facing == "downleft":
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[6]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                        elif self.facing == "up":
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[0]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                        elif self.facing == "down":
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[1]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                        elif self.facing == "left":
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[2]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
                        elif self.facing == "right":
                            center = self.imgRect.center
                            self.image = self.jumpingDownFrames[3]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                            self.walking = False
            else:
                if self.facing == "right":
                    if now - self.lastUpdate > 100:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.deadFramesRight) - 1:
                            self.currentFrame = (self.currentFrame + 1)
                        else:
                            center = self.rect.center
                            self.shadow = self.shadowFrames["dead horizontal"]
                            self.rect = self.shadow.get_rect()
                            self.rect.center = center
                        bottom = self.imgRect.bottom
                        left = self.imgRect.left
                        self.image = self.deadFramesRight[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.bottom = bottom
                        self.imgRect.left = left
                elif self.facing == "left":
                    if now - self.lastUpdate > 100:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.deadFramesLeft) - 1:
                            self.currentFrame = (self.currentFrame + 1)
                        else:
                            center = self.rect.center
                            self.shadow = self.shadowFrames["dead horizontal"]
                            self.rect = self.shadow.get_rect()
                            self.rect.center = center
                        bottom = self.imgRect.bottom
                        left = self.imgRect.left
                        self.image = self.deadFramesLeft[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.bottom = bottom
                        self.imgRect.left = left
                elif self.facing == "up":
                    if now - self.lastUpdate > 100:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.deadFramesUp) - 1:
                            self.currentFrame = (self.currentFrame + 1)
                        else:
                            center = self.rect.center
                            self.shadow = self.shadowFrames["dead vertical"]
                            self.rect = self.shadow.get_rect()
                            self.rect.center = center
                        bottom = self.imgRect.bottom
                        left = self.imgRect.left
                        self.image = self.deadFramesUp[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.bottom = bottom
                        self.imgRect.left = left
                elif self.facing == "down":
                    if now - self.lastUpdate > 100:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.deadFramesDown) - 1:
                            self.currentFrame = (self.currentFrame + 1)
                        else:
                            center = self.rect.center
                            self.shadow = self.shadowFrames["dead vertical"]
                            self.rect = self.shadow.get_rect()
                            self.rect.center = center
                        bottom = self.imgRect.bottom
                        left = self.imgRect.left
                        self.image = self.deadFramesDown[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.bottom = bottom
                        self.imgRect.left = left
                elif self.facing == "downleft":
                    if now - self.lastUpdate > 100:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.deadFramesDown) - 1:
                            self.currentFrame = (self.currentFrame + 1)
                        else:
                            center = self.rect.center
                            self.shadow = self.shadowFrames["dead vertical"]
                            self.rect = self.shadow.get_rect()
                            self.rect.center = center
                        bottom = self.imgRect.bottom
                        left = self.imgRect.left
                        self.image = self.deadFramesDown[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.bottom = bottom
                        self.imgRect.left = left
                elif self.facing == "downright":
                    if now - self.lastUpdate > 100:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.deadFramesDown) - 1:
                            self.currentFrame = (self.currentFrame + 1)
                        else:
                            center = self.rect.center
                            self.shadow = self.shadowFrames["dead vertical"]
                            self.rect = self.shadow.get_rect()
                            self.rect.center = center
                        bottom = self.imgRect.bottom
                        left = self.imgRect.left
                        self.image = self.deadFramesDown[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.bottom = bottom
                        self.imgRect.left = left
                elif self.facing == "upleft":
                    if now - self.lastUpdate > 100:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.deadFramesUp) - 1:
                            self.currentFrame = (self.currentFrame + 1)
                        else:
                            center = self.rect.center
                            self.shadow = self.shadowFrames["dead vertical"]
                            self.rect = self.shadow.get_rect()
                            self.rect.center = center
                        bottom = self.imgRect.bottom
                        left = self.imgRect.left
                        self.image = self.deadFramesUp[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.bottom = bottom
                        self.imgRect.left = left
                elif self.facing == "upright":
                    if now - self.lastUpdate > 100:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.deadFramesUp) - 1:
                            self.currentFrame = (self.currentFrame + 1)
                        else:
                            center = self.rect.center
                            self.shadow = self.shadowFrames["dead vertical"]
                            self.rect = self.shadow.get_rect()
                            self.rect.center = center
                        bottom = self.imgRect.bottom
                        left = self.imgRect.left
                        self.image = self.deadFramesUp[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.bottom = bottom
                        self.imgRect.left = left
        else:
            if self.facing == "up":
                center = self.imgRect.center
                self.image = self.standingFrames[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            if self.facing == "down":
                center = self.imgRect.center
                self.image = self.standingFrames[1]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            if self.facing == "left":
                center = self.imgRect.center
                self.image = self.standingFrames[2]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            if self.facing == "right":
                center = self.imgRect.center
                self.image = self.standingFrames[3]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            if self.facing == "downright":
                center = self.imgRect.center
                self.image = self.standingFrames[4]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            if self.facing == "upright":
                center = self.imgRect.center
                self.image = self.standingFrames[5]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            if self.facing == "downleft":
                center = self.imgRect.center
                self.image = self.standingFrames[6]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            if self.facing == "upleft":
                center = self.imgRect.center
                self.image = self.standingFrames[7]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            self.currentFrame = 11

        if self.walking and (self.currentFrame == 0 or self.currentFrame == 6) and now == self.lastUpdate:
            self.stepSound.stop()
            pg.mixer.Sound.play(self.stepSound)


class Luigi(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.stepSound = pg.mixer.Sound("sounds/coin.ogg")
        self.moveQueue = Q.deque()
        self.hit = False
        self.dead = False
        self.canMove = True
        self.hammering = False
        self.isHammer = None
        self.hitTime = 0
        self.alpha = 255
        self.ability = 0
        self.prevAbility = 12
        self.abilities = ["jump", "interact", "talk"]
        self.game = game
        self.loadImages()
        self.facing = "right"
        self.lastUpdate = 0
        self.currentFrame = 0
        self.walking = False
        self.jumping = False
        self.canBeHit = True
        self.jumpTimer = 0
        self.airTimer = 0
        self.image = self.standingFrames[0]
        self.shadow = self.shadowFrames["normal"]
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)
        self.going = "irrelevent"
        self.vx, self.vy = 0, 0

        self.stats = {"level": 1, "maxHP": 13, "maxBP": 5, "pow": 1, "def": 0, "stache": 3, "hp": 13, "bp": 5, "exp": 0}

    def hammer(self):
        if self.isHammer == None:
            self.isHammer = Hammer(self.game, self)
        self.walking = False
        if self.currentFrame < len(self.hammerFramesLeft) - 1:
            pass
        else:
            self.currentFrame = 0
            self.hammering = False

    def jump(self):
        if self.jumpTimer < jumpHeight and self.airTimer == 0:
            self.jumpTimer += 0.9
            self.going = "up"
        elif self.jumpTimer >= jumpHeight:
            self.airTimer += 1
        if self.airTimer >= airTime and self.jumpTimer != 0:
            self.jumpTimer -= 0.9
            self.going = "down"
        if self.jumpTimer <= 0 and self.airTimer != 0:
            self.jumping = False
        jumpOffset = self.jumpTimer * jumpHeight
        self.imgRect.bottom = (self.rect.bottom - 5) - jumpOffset

    def wallCollisions(self, group, vx=0, vy=0):
        for wall in group:
            if pg.sprite.collide_rect(self, wall):
                if vx > 0:
                    self.rect.right = wall.rect.left
                    self.vx = 0
                    self.walking = False
                if vx < 0:
                    self.rect.left = wall.rect.right
                    self.vx = 0
                    self.walking = False
                if vy < 0:
                    self.rect.top = wall.rect.bottom
                    self.vy = 0
                    self.walking = False
                if vy > 0:
                    self.rect.bottom = wall.rect.top
                    self.vy = 0
                    self.walking = False

    def update(self):
        if self.stats["hp"] < 0:
            self.stats["hp"] = 0
        if self.stats["hp"] == 0:
            self.dead = True
        self.animate()

        now = pg.time.get_ticks()
        keys = pg.key.get_pressed()
        if not self.dead and not self.game.player.dead:
            self.walking = self.game.player.walking
            if not self.hit and not self.game.player.hit:
                if self.walking or self.game.player.vx != 0 or self.game.player.vy != 0:
                    self.moveQueue.append(self.game.player.rect.x)
                    self.moveQueue.append(self.game.player.rect.y)
                    self.moveQueue.append(self.game.player.facing)
                    if len(self.moveQueue) > 30:
                        self.rect.x = self.moveQueue.popleft()
                        self.rect.y = self.moveQueue.popleft()
                        self.facing = self.moveQueue.popleft()
        elif not self.dead and self.game.player.dead and self.canMove and not self.hammering:
            self.moveQueue = Q.deque()
            self.vx, self.vy = 0, 0
            if not self.hit:
                if keys[pg.K_w]:
                    self.vy = -playerSpeed
                if keys[pg.K_a]:
                    self.vx = -playerSpeed
                if keys[pg.K_s]:
                    self.vy = playerSpeed
                if keys[pg.K_d]:
                    self.vx = playerSpeed

            self.rect.x += self.vx
            self.wallCollisions(self.game.walls, self.vx)
            self.wallCollisions(self.game.npcs, self.vx)
            self.rect.y += self.vy
            self.wallCollisions(self.game.walls, 0, self.vy)
            self.wallCollisions(self.game.npcs, 0, self.vy)

            if self.rect.x > self.game.map.width + 60:
                self.rect.x = -60
            if self.rect.x < -60:
                self.rect.x = self.game.map.width + 60
            if self.rect.y > self.game.map.height + 100:
                self.rect.y = -100
            if self.rect.y < -100:
                self.rect.y = self.game.map.height + 100

        if not self.hit and self.canMove:
            for event in self.game.event:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_l:
                        if self.ability == 0:
                            if not self.jumping and not self.hit and not self.dead and self.canMove:
                                self.jumping = True
                                self.jumpTimer = 1
                                self.airTimer = 0
                                self.game.jumpSound.play()
                        elif self.ability == 1:
                            if not self.hammering and not self.hit and not self.dead and self.canMove:
                                self.hammering = True
                                self.currentFrame = 0
                    if event.key == pg.K_SPACE:
                        if not self.jumping and not self.hit and not self.dead and self.canMove:
                            self.jumping = True
                            self.jumpTimer = 1
                            self.airTimer = 0
                            self.game.jumpSound.play()
                    if event.key == pg.K_RSHIFT:
                        if len(self.abilities) > 3:
                            self.game.abilityAdvanceSound.play()
                        self.ability = (self.ability + 1) % (len(self.abilities) - 2)
                        print(self.abilities[self.ability])
                    if event.key == pg.K_h:
                        if len(self.abilities) == 3:
                            self.abilities = ["jump", "hammer", "interact", "talk"]
                        else:
                            self.abilities = ["jump", "interact", "talk"]

        if self.hit:
            self.canBeHit = False
            if self.hammering:
                self.hammering = False
            if now - self.hitTime > 250:
                self.hit = False

        if not self.canBeHit and not self.dead:
            if now % 2 == 0 and not self.hit:
                self.alpha = 0
            else:
                self.alpha = 255
            if now - self.hitTime > 1000:
                self.alpha = 255
                self.canBeHit = True

        if not self.jumping:
            self.imgRect.bottom = self.rect.bottom - 5
            self.imgRect.centerx = self.rect.centerx
        else:
            self.jump()
            self.imgRect.centerx = self.rect.centerx
        if self.hammering:
            self.hammer()

    def loadImages(self):
        sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")

        self.shadowFrames = {"normal": sheet.getImageName("shadow.png"),
                             "dead horizontal": sheet.getImageName("dead_shadow_horizontal.png"),
                             "dead vertical": sheet.getImageName("dead_shadow_vertical.png")}

        self.jumpingUpFrames = [sheet.getImageName("luigi_jumping_up_up.png"),
                                sheet.getImageName("luigi_jumping_up_down.png"),
                                sheet.getImageName("luigi_jumping_up_left.png"),
                                sheet.getImageName("luigi_jumping_up_right.png"),
                                sheet.getImageName("luigi_jumping_up_upleft.png"),
                                sheet.getImageName("luigi_jumping_up_upright.png"),
                                sheet.getImageName("luigi_jumping_up_downleft.png"),
                                sheet.getImageName("luigi_jumping_up_downright.png")]

        self.jumpingDownFrames = [sheet.getImageName("luigi_jumping_down_up.png"),
                                  sheet.getImageName("luigi_jumping_down_down.png"),
                                  sheet.getImageName("luigi_jumping_down_left.png"),
                                  sheet.getImageName("luigi_jumping_down_right.png"),
                                  sheet.getImageName("luigi_jumping_down_upleft.png"),
                                  sheet.getImageName("luigi_jumping_down_upright.png"),
                                  sheet.getImageName("luigi_jumping_down_downleft.png"),
                                  sheet.getImageName("luigi_jumping_down_downright.png")]

        self.standingFrames = [sheet.getImageName("luigi_standing_up.png"),
                               sheet.getImageName("luigi_standing_down.png"),
                               sheet.getImageName("luigi_standing_left.png"),
                               sheet.getImageName("luigi_standing_right.png"),
                               sheet.getImageName("luigi_standing_downright.png"),
                               sheet.getImageName("luigi_standing_upright.png"),
                               sheet.getImageName("luigi_standing_downleft.png"),
                               sheet.getImageName("luigi_standing_upleft.png")]

        self.walkingFramesUp = [sheet.getImageName("luigi_walking_up_1.png"),
                                sheet.getImageName("luigi_walking_up_2.png"),
                                sheet.getImageName("luigi_walking_up_3.png"),
                                sheet.getImageName("luigi_walking_up_4.png"),
                                sheet.getImageName("luigi_walking_up_5.png"),
                                sheet.getImageName("luigi_walking_up_6.png"),
                                sheet.getImageName("luigi_walking_up_7.png"),
                                sheet.getImageName("luigi_walking_up_8.png"),
                                sheet.getImageName("luigi_walking_up_9.png"),
                                sheet.getImageName("luigi_walking_up_10.png"),
                                sheet.getImageName("luigi_walking_up_11.png"),
                                sheet.getImageName("luigi_walking_up_12.png")]

        self.walkingFramesUpright = [sheet.getImageName("luigi_walking_upright_1.png"),
                                     sheet.getImageName("luigi_walking_upright_2.png"),
                                     sheet.getImageName("luigi_walking_upright_3.png"),
                                     sheet.getImageName("luigi_walking_upright_4.png"),
                                     sheet.getImageName("luigi_walking_upright_5.png"),
                                     sheet.getImageName("luigi_walking_upright_6.png"),
                                     sheet.getImageName("luigi_walking_upright_7.png"),
                                     sheet.getImageName("luigi_walking_upright_8.png"),
                                     sheet.getImageName("luigi_walking_upright_9.png"),
                                     sheet.getImageName("luigi_walking_upright_10.png"),
                                     sheet.getImageName("luigi_walking_upright_11.png"),
                                     sheet.getImageName("luigi_walking_upright_12.png")]

        self.walkingFramesRight = [sheet.getImageName("luigi_walking_right_1.png"),
                                   sheet.getImageName("luigi_walking_right_2.png"),
                                   sheet.getImageName("luigi_walking_right_3.png"),
                                   sheet.getImageName("luigi_walking_right_4.png"),
                                   sheet.getImageName("luigi_walking_right_5.png"),
                                   sheet.getImageName("luigi_walking_right_6.png"),
                                   sheet.getImageName("luigi_walking_right_7.png"),
                                   sheet.getImageName("luigi_walking_right_8.png"),
                                   sheet.getImageName("luigi_walking_right_9.png"),
                                   sheet.getImageName("luigi_walking_right_10.png"),
                                   sheet.getImageName("luigi_walking_right_11.png"),
                                   sheet.getImageName("luigi_walking_right_12.png")]

        self.walkingFramesDownright = [sheet.getImageName("luigi_walking_downright_1.png"),
                                       sheet.getImageName("luigi_walking_downright_2.png"),
                                       sheet.getImageName("luigi_walking_downright_3.png"),
                                       sheet.getImageName("luigi_walking_downright_4.png"),
                                       sheet.getImageName("luigi_walking_downright_5.png"),
                                       sheet.getImageName("luigi_walking_downright_6.png"),
                                       sheet.getImageName("luigi_walking_downright_7.png"),
                                       sheet.getImageName("luigi_walking_downright_8.png"),
                                       sheet.getImageName("luigi_walking_downright_9.png"),
                                       sheet.getImageName("luigi_walking_downright_10.png"),
                                       sheet.getImageName("luigi_walking_downright_11.png"),
                                       sheet.getImageName("luigi_walking_downright_12.png")]

        self.walkingFramesDown = [sheet.getImageName("luigi_walking_down_1.png"),
                                  sheet.getImageName("luigi_walking_down_2.png"),
                                  sheet.getImageName("luigi_walking_down_3.png"),
                                  sheet.getImageName("luigi_walking_down_4.png"),
                                  sheet.getImageName("luigi_walking_down_5.png"),
                                  sheet.getImageName("luigi_walking_down_6.png"),
                                  sheet.getImageName("luigi_walking_down_7.png"),
                                  sheet.getImageName("luigi_walking_down_8.png"),
                                  sheet.getImageName("luigi_walking_down_9.png"),
                                  sheet.getImageName("luigi_walking_down_10.png"),
                                  sheet.getImageName("luigi_walking_down_11.png"),
                                  sheet.getImageName("luigi_walking_down_12.png")]

        self.walkingFramesDownleft = [sheet.getImageName("luigi_walking_downleft_1.png"),
                                      sheet.getImageName("luigi_walking_downleft_2.png"),
                                      sheet.getImageName("luigi_walking_downleft_3.png"),
                                      sheet.getImageName("luigi_walking_downleft_4.png"),
                                      sheet.getImageName("luigi_walking_downleft_5.png"),
                                      sheet.getImageName("luigi_walking_downleft_6.png"),
                                      sheet.getImageName("luigi_walking_downleft_7.png"),
                                      sheet.getImageName("luigi_walking_downleft_8.png"),
                                      sheet.getImageName("luigi_walking_downleft_9.png"),
                                      sheet.getImageName("luigi_walking_downleft_10.png"),
                                      sheet.getImageName("luigi_walking_downleft_11.png"),
                                      sheet.getImageName("luigi_walking_downleft_12.png")]

        self.walkingFramesLeft = [sheet.getImageName("luigi_walking_left_1.png"),
                                  sheet.getImageName("luigi_walking_left_2.png"),
                                  sheet.getImageName("luigi_walking_left_3.png"),
                                  sheet.getImageName("luigi_walking_left_4.png"),
                                  sheet.getImageName("luigi_walking_left_5.png"),
                                  sheet.getImageName("luigi_walking_left_6.png"),
                                  sheet.getImageName("luigi_walking_left_7.png"),
                                  sheet.getImageName("luigi_walking_left_8.png"),
                                  sheet.getImageName("luigi_walking_left_9.png"),
                                  sheet.getImageName("luigi_walking_left_10.png"),
                                  sheet.getImageName("luigi_walking_left_11.png"),
                                  sheet.getImageName("luigi_walking_left_12.png")]

        self.walkingFramesUpleft = [sheet.getImageName("luigi_walking_upleft_1.png"),
                                    sheet.getImageName("luigi_walking_upleft_2.png"),
                                    sheet.getImageName("luigi_walking_upleft_3.png"),
                                    sheet.getImageName("luigi_walking_upleft_4.png"),
                                    sheet.getImageName("luigi_walking_upleft_5.png"),
                                    sheet.getImageName("luigi_walking_upleft_6.png"),
                                    sheet.getImageName("luigi_walking_upleft_7.png"),
                                    sheet.getImageName("luigi_walking_upleft_8.png"),
                                    sheet.getImageName("luigi_walking_upleft_9.png"),
                                    sheet.getImageName("luigi_walking_upleft_10.png"),
                                    sheet.getImageName("luigi_walking_upleft_11.png"),
                                    sheet.getImageName("luigi_walking_upleft_12.png")]

        self.deadFramesRight = [sheet.getImageName("luigi_dead_right_1.png"),
                                sheet.getImageName("luigi_dead_right_2.png"),
                                sheet.getImageName("luigi_dead_right_3.png"),
                                sheet.getImageName("luigi_dead_right_4.png"), ]

        self.deadFramesLeft = [sheet.getImageName("luigi_dead_left_1.png"),
                               sheet.getImageName("luigi_dead_left_2.png"),
                               sheet.getImageName("luigi_dead_left_3.png"),
                               sheet.getImageName("luigi_dead_left_4.png"), ]

        self.deadFramesUp = [sheet.getImageName("luigi_dead_up_1.png"),
                             sheet.getImageName("luigi_dead_up_2.png"),
                             sheet.getImageName("luigi_dead_up_3.png"),
                             sheet.getImageName("luigi_dead_up_4.png")]

        self.deadFramesDown = [sheet.getImageName("luigi_dead_down_1.png"),
                               sheet.getImageName("luigi_dead_down_2.png"),
                               sheet.getImageName("luigi_dead_down_3.png"),
                               sheet.getImageName("luigi_dead_down_4.png")]

        self.hammerFramesUp = [sheet.getImageName("luigi_hammering_up_1.png"),
                               sheet.getImageName("luigi_hammering_up_2.png"),
                               sheet.getImageName("luigi_hammering_up_3.png"),
                               sheet.getImageName("luigi_hammering_up_4.png"),
                               sheet.getImageName("luigi_hammering_up_5.png"),
                               sheet.getImageName("luigi_hammering_up_6.png"),
                               sheet.getImageName("luigi_hammering_up_7.png"),
                               sheet.getImageName("luigi_hammering_up_8.png"),
                               sheet.getImageName("luigi_hammering_up_9.png"),
                               sheet.getImageName("luigi_hammering_up_10.png"),
                               sheet.getImageName("luigi_hammering_up_11.png"),
                               sheet.getImageName("luigi_hammering_up_12.png"),
                               sheet.getImageName("luigi_hammering_up_13.png")]

        self.hammerFramesDown = [sheet.getImageName("luigi_hammering_down_1.png"),
                                 sheet.getImageName("luigi_hammering_down_2.png"),
                                 sheet.getImageName("luigi_hammering_down_3.png"),
                                 sheet.getImageName("luigi_hammering_down_4.png"),
                                 sheet.getImageName("luigi_hammering_down_5.png"),
                                 sheet.getImageName("luigi_hammering_down_6.png"),
                                 sheet.getImageName("luigi_hammering_down_7.png"),
                                 sheet.getImageName("luigi_hammering_down_8.png"),
                                 sheet.getImageName("luigi_hammering_down_9.png"),
                                 sheet.getImageName("luigi_hammering_down_10.png"),
                                 sheet.getImageName("luigi_hammering_down_11.png"),
                                 sheet.getImageName("luigi_hammering_down_12.png"),
                                 sheet.getImageName("luigi_hammering_down_13.png")]

        self.hammerFramesLeft = [sheet.getImageName("luigi_hammering_left_1.png"),
                                 sheet.getImageName("luigi_hammering_left_2.png"),
                                 sheet.getImageName("luigi_hammering_left_3.png"),
                                 sheet.getImageName("luigi_hammering_left_4.png"),
                                 sheet.getImageName("luigi_hammering_left_5.png"),
                                 sheet.getImageName("luigi_hammering_left_6.png"),
                                 sheet.getImageName("luigi_hammering_left_7.png"),
                                 sheet.getImageName("luigi_hammering_left_8.png"),
                                 sheet.getImageName("luigi_hammering_left_9.png"),
                                 sheet.getImageName("luigi_hammering_left_10.png"),
                                 sheet.getImageName("luigi_hammering_left_11.png"),
                                 sheet.getImageName("luigi_hammering_left_12.png"),
                                 sheet.getImageName("luigi_hammering_left_13.png")]

        self.hammerFramesRight = [sheet.getImageName("luigi_hammering_right_1.png"),
                                  sheet.getImageName("luigi_hammering_right_2.png"),
                                  sheet.getImageName("luigi_hammering_right_3.png"),
                                  sheet.getImageName("luigi_hammering_right_4.png"),
                                  sheet.getImageName("luigi_hammering_right_5.png"),
                                  sheet.getImageName("luigi_hammering_right_6.png"),
                                  sheet.getImageName("luigi_hammering_right_7.png"),
                                  sheet.getImageName("luigi_hammering_right_8.png"),
                                  sheet.getImageName("luigi_hammering_right_9.png"),
                                  sheet.getImageName("luigi_hammering_right_10.png"),
                                  sheet.getImageName("luigi_hammering_right_11.png"),
                                  sheet.getImageName("luigi_hammering_right_12.png"),
                                  sheet.getImageName("luigi_hammering_right_13.png")]

        self.hammerFramesUpleft = [sheet.getImageName("luigi_hammering_upleft_1.png"),
                                   sheet.getImageName("luigi_hammering_upleft_2.png"),
                                   sheet.getImageName("luigi_hammering_upleft_3.png"),
                                   sheet.getImageName("luigi_hammering_upleft_4.png"),
                                   sheet.getImageName("luigi_hammering_upleft_5.png"),
                                   sheet.getImageName("luigi_hammering_upleft_6.png"),
                                   sheet.getImageName("luigi_hammering_upleft_7.png"),
                                   sheet.getImageName("luigi_hammering_upleft_8.png"),
                                   sheet.getImageName("luigi_hammering_upleft_9.png"),
                                   sheet.getImageName("luigi_hammering_upleft_10.png"),
                                   sheet.getImageName("luigi_hammering_upleft_11.png"),
                                   sheet.getImageName("luigi_hammering_upleft_12.png"),
                                   sheet.getImageName("luigi_hammering_upleft_13.png")]

        self.hammerFramesUpright = [sheet.getImageName("luigi_hammering_upright_1.png"),
                                    sheet.getImageName("luigi_hammering_upright_2.png"),
                                    sheet.getImageName("luigi_hammering_upright_3.png"),
                                    sheet.getImageName("luigi_hammering_upright_4.png"),
                                    sheet.getImageName("luigi_hammering_upright_5.png"),
                                    sheet.getImageName("luigi_hammering_upright_6.png"),
                                    sheet.getImageName("luigi_hammering_upright_7.png"),
                                    sheet.getImageName("luigi_hammering_upright_8.png"),
                                    sheet.getImageName("luigi_hammering_upright_9.png"),
                                    sheet.getImageName("luigi_hammering_upright_10.png"),
                                    sheet.getImageName("luigi_hammering_upright_11.png"),
                                    sheet.getImageName("luigi_hammering_upright_12.png"),
                                    sheet.getImageName("luigi_hammering_upright_13.png")]

        self.hammerFramesDownleft = [sheet.getImageName("luigi_hammering_downleft_1.png"),
                                     sheet.getImageName("luigi_hammering_downleft_2.png"),
                                     sheet.getImageName("luigi_hammering_downleft_3.png"),
                                     sheet.getImageName("luigi_hammering_downleft_4.png"),
                                     sheet.getImageName("luigi_hammering_downleft_5.png"),
                                     sheet.getImageName("luigi_hammering_downleft_6.png"),
                                     sheet.getImageName("luigi_hammering_downleft_7.png"),
                                     sheet.getImageName("luigi_hammering_downleft_8.png"),
                                     sheet.getImageName("luigi_hammering_downleft_9.png"),
                                     sheet.getImageName("luigi_hammering_downleft_10.png"),
                                     sheet.getImageName("luigi_hammering_downleft_11.png"),
                                     sheet.getImageName("luigi_hammering_downleft_12.png"),
                                     sheet.getImageName("luigi_hammering_downleft_13.png")]

        self.hammerFramesDownright = [sheet.getImageName("luigi_hammering_downright_1.png"),
                                      sheet.getImageName("luigi_hammering_downright_2.png"),
                                      sheet.getImageName("luigi_hammering_downright_3.png"),
                                      sheet.getImageName("luigi_hammering_downright_4.png"),
                                      sheet.getImageName("luigi_hammering_downright_5.png"),
                                      sheet.getImageName("luigi_hammering_downright_6.png"),
                                      sheet.getImageName("luigi_hammering_downright_7.png"),
                                      sheet.getImageName("luigi_hammering_downright_8.png"),
                                      sheet.getImageName("luigi_hammering_downright_9.png"),
                                      sheet.getImageName("luigi_hammering_downright_10.png"),
                                      sheet.getImageName("luigi_hammering_downright_11.png"),
                                      sheet.getImageName("luigi_hammering_downright_12.png"),
                                      sheet.getImageName("luigi_hammering_downright_13.png")]

        self.hitFrames = {"up": sheet.getImageName("luigi_hit_up.png"),
                          "down": sheet.getImageName("luigi_hit_down.png"),
                          "left": sheet.getImageName("luigi_hit_left.png"),
                          "right": sheet.getImageName("luigi_hit_right.png"),
                          "downright": sheet.getImageName("luigi_hit_downright.png"),
                          "upright": sheet.getImageName("luigi_hit_upright.png"),
                          "downleft": sheet.getImageName("luigi_hit_downleft.png"),
                          "upleft": sheet.getImageName("luigi_hit_upleft.png")}

    def animate(self):
        now = pg.time.get_ticks()
        keys = pg.key.get_pressed()
        if not self.dead and not self.game.player.dead:
            if self.hit:
                if self.facing == "up":
                    center = self.imgRect.center
                    self.image = self.hitFrames["up"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                elif self.facing == "down":
                    center = self.imgRect.center
                    self.image = self.hitFrames["down"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                elif self.facing == "left":
                    center = self.imgRect.center
                    self.image = self.hitFrames["left"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                elif self.facing == "right":
                    center = self.imgRect.center
                    self.image = self.hitFrames["right"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                elif self.facing == "downleft":
                    center = self.imgRect.center
                    self.image = self.hitFrames["downleft"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                elif self.facing == "downright":
                    center = self.imgRect.center
                    self.image = self.hitFrames["downright"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                elif self.facing == "upleft":
                    center = self.imgRect.center
                    self.image = self.hitFrames["upleft"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                elif self.facing == "upright":
                    center = self.imgRect.center
                    self.image = self.hitFrames["upright"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.hammering:
                if self.facing == "left":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesLeft[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.facing == "right":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesRight[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.facing == "up":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesUp[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.facing == "down":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesDown[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.facing == "upleft":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesUpleft[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.facing == "upright":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesUpright[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.facing == "downleft":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesDownleft[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.facing == "downright":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesDownright[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
            elif not self.jumping:
                if not self.hit and not self.game.player.hit:
                    if self.walking or self.game.player.vx != 0 or self.game.player.vy != 0:
                        if self.facing == "upright":
                            if now - self.lastUpdate > 25:
                                self.lastUpdate = now
                                if self.currentFrame < len(self.walkingFramesUpright):
                                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesUpright))
                                else:
                                    self.currentFrame = 0
                                center = self.imgRect.center
                                self.image = self.walkingFramesUpright[self.currentFrame]
                                self.imgRect = self.image.get_rect()
                                self.imgRect.center = center
                        elif self.facing == "upleft":
                            if now - self.lastUpdate > 25:
                                self.lastUpdate = now
                                if self.currentFrame < len(self.walkingFramesUpleft):
                                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesUpleft))
                                else:
                                    self.currentFrame = 0
                                center = self.imgRect.center
                                self.image = self.walkingFramesUpleft[self.currentFrame]
                                self.imgRect = self.image.get_rect()
                                self.imgRect.center = center
                        elif self.facing == "downright":
                            if now - self.lastUpdate > 25:
                                self.lastUpdate = now
                                if self.currentFrame < len(self.walkingFramesDownright):
                                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesDownright))
                                else:
                                    self.currentFrame = 0
                                center = self.imgRect.center
                                self.image = self.walkingFramesDownright[self.currentFrame]
                                self.imgRect = self.image.get_rect()
                                self.imgRect.center = center
                        elif self.facing == "downleft":
                            if now - self.lastUpdate > 25:
                                self.lastUpdate = now
                                if self.currentFrame < len(self.walkingFramesDownleft):
                                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesDownleft))
                                else:
                                    self.currentFrame = 0
                                center = self.imgRect.center
                                self.image = self.walkingFramesDownleft[self.currentFrame]
                                self.imgRect = self.image.get_rect()
                                self.imgRect.center = center
                        elif self.facing == "up":
                            if now - self.lastUpdate > 25:
                                self.lastUpdate = now
                                if self.currentFrame < len(self.walkingFramesUp):
                                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesUp))
                                else:
                                    self.currentFrame = 0
                                center = self.imgRect.center
                                self.image = self.walkingFramesUp[self.currentFrame]
                                self.imgRect = self.image.get_rect()
                                self.imgRect.center = center
                        elif self.facing == "left":
                            if now - self.lastUpdate > 25:
                                self.lastUpdate = now
                                if self.currentFrame < len(self.walkingFramesLeft):
                                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesLeft))
                                else:
                                    self.currentFrame = 0
                                center = self.imgRect.center
                                self.image = self.walkingFramesLeft[self.currentFrame]
                                self.imgRect = self.image.get_rect()
                                self.imgRect.center = center
                        elif self.facing == "down":
                            if now - self.lastUpdate > 25:
                                self.lastUpdate = now
                                if self.currentFrame < len(self.walkingFramesDown):
                                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesDown))
                                else:
                                    self.currentFrame = 0
                                center = self.imgRect.center
                                self.image = self.walkingFramesDown[self.currentFrame]
                                self.imgRect = self.image.get_rect()
                                self.imgRect.center = center
                        elif self.facing == "right":
                            if now - self.lastUpdate > 25:
                                self.lastUpdate = now
                                if self.currentFrame < len(self.walkingFramesRight):
                                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesRight))
                                else:
                                    self.currentFrame = 0
                                center = self.imgRect.center
                                self.image = self.walkingFramesRight[self.currentFrame]
                                self.imgRect = self.image.get_rect()
                                self.imgRect.center = center
                    else:
                        if self.facing == "up":
                            center = self.imgRect.center
                            self.image = self.standingFrames[0]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        if self.facing == "down":
                            center = self.imgRect.center
                            self.image = self.standingFrames[1]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        if self.facing == "left":
                            center = self.imgRect.center
                            self.image = self.standingFrames[2]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        if self.facing == "right":
                            center = self.imgRect.center
                            self.image = self.standingFrames[3]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        if self.facing == "downright":
                            center = self.imgRect.center
                            self.image = self.standingFrames[4]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        if self.facing == "upright":
                            center = self.imgRect.center
                            self.image = self.standingFrames[5]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        if self.facing == "downleft":
                            center = self.imgRect.center
                            self.image = self.standingFrames[6]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        if self.facing == "upleft":
                            center = self.imgRect.center
                            self.image = self.standingFrames[7]
                            self.imgRect = self.image.get_rect()
                            self.imgRect.center = center
                        self.currentFrame = 11
            else:
                if self.going == "up":
                    if keys[pg.K_w] and keys[pg.K_d]:
                        self.facing = "upright"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[5]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_w] and keys[pg.K_a]:
                        self.facing = "upleft"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[4]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_s] and keys[pg.K_d]:
                        self.facing = "downright"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[7]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_s] and keys[pg.K_a]:
                        self.facing = "downleft"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[6]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_w]:
                        self.facing = "up"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[0]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_s]:
                        self.facing = "down"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[1]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_a]:
                        self.facing = "left"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[2]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_d]:
                        self.facing = "right"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[3]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif self.facing == "upright":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[5]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "upleft":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[4]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "downright":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[7]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "downleft":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[6]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "up":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[0]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "down":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[1]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "left":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[2]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "right":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[3]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                else:
                    if keys[pg.K_w] and keys[pg.K_d]:
                        self.facing = "upright"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[5]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_w] and keys[pg.K_a]:
                        self.facing = "upleft"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[4]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_s] and keys[pg.K_d]:
                        self.facing = "downright"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[7]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_s] and keys[pg.K_a]:
                        self.facing = "downleft"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[6]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_w]:
                        self.facing = "up"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[0]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_s]:
                        self.facing = "down"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[1]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_a]:
                        self.facing = "left"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[2]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_d]:
                        self.facing = "right"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[3]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif self.facing == "upright":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[5]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "upleft":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[4]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "downright":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[7]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "downleft":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[6]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "up":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[0]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "down":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[1]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "left":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[2]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "right":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[3]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
        elif not self.dead and self.game.player.dead:
            if self.hit:
                self.walking = False
                if self.facing == "up":
                    center = self.imgRect.center
                    self.image = self.hitFrames["up"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                elif self.facing == "down":
                    center = self.imgRect.center
                    self.image = self.hitFrames["down"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                elif self.facing == "left":
                    center = self.imgRect.center
                    self.image = self.hitFrames["left"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                elif self.facing == "right":
                    center = self.imgRect.center
                    self.image = self.hitFrames["right"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                elif self.facing == "downleft":
                    center = self.imgRect.center
                    self.image = self.hitFrames["downleft"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                elif self.facing == "downright":
                    center = self.imgRect.center
                    self.image = self.hitFrames["downright"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                elif self.facing == "upleft":
                    center = self.imgRect.center
                    self.image = self.hitFrames["upleft"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                elif self.facing == "upright":
                    center = self.imgRect.center
                    self.image = self.hitFrames["upright"]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.hammering:
                if self.facing == "left":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesLeft[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.facing == "right":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesRight[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.facing == "up":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesUp[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.facing == "down":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesDown[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.facing == "upleft":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesUpleft[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.facing == "upright":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesUpright[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.facing == "downleft":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesDownleft[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif self.facing == "downright":
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.hammerFramesLeft) + 1:
                            self.currentFrame = (self.currentFrame + 1)
                        center = self.imgRect.center
                        self.image = self.hammerFramesDownright[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
            elif not self.jumping:
                if keys[pg.K_w] and keys[pg.K_d]:
                    self.facing = "upright"
                    self.walking = True
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.walkingFramesUpright):
                            self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesUpright))
                        else:
                            self.currentFrame = 0
                        center = self.imgRect.center
                        self.image = self.walkingFramesUpright[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif keys[pg.K_w] and keys[pg.K_a]:
                    self.facing = "upleft"
                    self.walking = True
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.walkingFramesUpleft):
                            self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesUpleft))
                        else:
                            self.currentFrame = 0
                        center = self.imgRect.center
                        self.image = self.walkingFramesUpleft[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif keys[pg.K_s] and keys[pg.K_d]:
                    self.facing = "downright"
                    self.walking = True
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.walkingFramesDownright):
                            self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesDownright))
                        else:
                            self.currentFrame = 0
                        center = self.imgRect.center
                        self.image = self.walkingFramesDownright[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif keys[pg.K_s] and keys[pg.K_a]:
                    self.facing = "downleft"
                    self.walking = True
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.walkingFramesDownleft):
                            self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesDownleft))
                        else:
                            self.currentFrame = 0
                        center = self.imgRect.center
                        self.image = self.walkingFramesDownleft[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif keys[pg.K_w]:
                    self.facing = "up"
                    self.walking = True
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.walkingFramesUp):
                            self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesUp))
                        else:
                            self.currentFrame = 0
                        center = self.imgRect.center
                        self.image = self.walkingFramesUp[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif keys[pg.K_a]:
                    self.facing = "left"
                    self.walking = True
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.walkingFramesLeft):
                            self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesLeft))
                        else:
                            self.currentFrame = 0
                        center = self.imgRect.center
                        self.image = self.walkingFramesLeft[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif keys[pg.K_s]:
                    self.facing = "down"
                    self.walking = True
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.walkingFramesDown):
                            self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesDown))
                        else:
                            self.currentFrame = 0
                        center = self.imgRect.center
                        self.image = self.walkingFramesDown[self.currentFrame]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                elif keys[pg.K_d]:
                    self.facing = "right"
                    self.walking = True
                    if now - self.lastUpdate > 25:
                        self.lastUpdate = now
                        if self.currentFrame < len(self.walkingFramesRight):
                            self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesRight))
                        else:
                            self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.walkingFramesRight[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
                else:
                    if self.facing == "up":
                        center = self.imgRect.center
                        self.image = self.standingFrames[0]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "down":
                        center = self.imgRect.center
                        self.image = self.standingFrames[1]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "left":
                        center = self.imgRect.center
                        self.image = self.standingFrames[2]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "right":
                        center = self.imgRect.center
                        self.image = self.standingFrames[3]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "downright":
                        center = self.imgRect.center
                        self.image = self.standingFrames[4]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "upright":
                        center = self.imgRect.center
                        self.image = self.standingFrames[5]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "downleft":
                        center = self.imgRect.center
                        self.image = self.standingFrames[6]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "upleft":
                        center = self.imgRect.center
                        self.image = self.standingFrames[7]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center

                    self.currentFrame = 0
                    self.walking = False
            else:
                if self.going == "up":
                    if keys[pg.K_w] and keys[pg.K_d]:
                        self.facing = "upright"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[5]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_w] and keys[pg.K_a]:
                        self.facing = "upleft"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[4]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_s] and keys[pg.K_d]:
                        self.facing = "downright"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[7]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_s] and keys[pg.K_a]:
                        self.facing = "downleft"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[6]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_w]:
                        self.facing = "up"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[0]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_s]:
                        self.facing = "down"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[1]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_a]:
                        self.facing = "left"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[2]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_d]:
                        self.facing = "right"
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[3]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif self.facing == "upright":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[5]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "upleft":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[4]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "downright":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[7]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "downleft":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[6]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "up":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[0]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "down":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[1]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "left":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[2]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "right":
                        center = self.imgRect.center
                        self.image = self.jumpingUpFrames[3]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                else:
                    if keys[pg.K_w] and keys[pg.K_d]:
                        self.facing = "upright"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[5]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_w] and keys[pg.K_a]:
                        self.facing = "upleft"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[4]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_s] and keys[pg.K_d]:
                        self.facing = "downright"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[7]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_s] and keys[pg.K_a]:
                        self.facing = "downleft"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[6]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_w]:
                        self.facing = "up"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[0]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_s]:
                        self.facing = "down"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[1]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_a]:
                        self.facing = "left"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[2]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif keys[pg.K_d]:
                        self.facing = "right"
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[3]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = True
                    elif self.facing == "upright":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[5]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "upleft":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[4]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "downright":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[7]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "downleft":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[6]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "up":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[0]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "down":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[1]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "left":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[2]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
                    elif self.facing == "right":
                        center = self.imgRect.center
                        self.image = self.jumpingDownFrames[3]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                        self.walking = False
        else:
            if self.facing == "right":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.deadFramesRight) - 1:
                        self.currentFrame = (self.currentFrame + 1)
                    else:
                        center = self.rect.center
                        self.shadow = self.shadowFrames["dead horizontal"]
                        self.rect = self.shadow.get_rect()
                        self.rect.center = center
                    bottom = self.imgRect.bottom
                    left = self.imgRect.left
                    self.image = self.deadFramesRight[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.left = left
            elif self.facing == "left":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.deadFramesLeft) - 1:
                        self.currentFrame = (self.currentFrame + 1)
                    else:
                        center = self.rect.center
                        self.shadow = self.shadowFrames["dead horizontal"]
                        self.rect = self.shadow.get_rect()
                        self.rect.center = center
                    bottom = self.imgRect.bottom
                    left = self.imgRect.left
                    self.image = self.deadFramesLeft[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.left = left
            elif self.facing == "up":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.deadFramesUp) - 1:
                        self.currentFrame = (self.currentFrame + 1)
                    else:
                        center = self.rect.center
                        self.shadow = self.shadowFrames["dead vertical"]
                        self.rect = self.shadow.get_rect()
                        self.rect.center = center
                    bottom = self.imgRect.bottom
                    left = self.imgRect.left
                    self.image = self.deadFramesUp[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.left = left
            elif self.facing == "down":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.deadFramesDown) - 1:
                        self.currentFrame = (self.currentFrame + 1)
                    else:
                        center = self.rect.center
                        self.shadow = self.shadowFrames["dead vertical"]
                        self.rect = self.shadow.get_rect()
                        self.rect.center = center
                    bottom = self.imgRect.bottom
                    left = self.imgRect.left
                    self.image = self.deadFramesDown[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.left = left
            elif self.facing == "downleft":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.deadFramesDown) - 1:
                        self.currentFrame = (self.currentFrame + 1)
                    else:
                        center = self.rect.center
                        self.shadow = self.shadowFrames["dead vertical"]
                        self.rect = self.shadow.get_rect()
                        self.rect.center = center
                    bottom = self.imgRect.bottom
                    left = self.imgRect.left
                    self.image = self.deadFramesDown[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.left = left
            elif self.facing == "downright":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.deadFramesDown) - 1:
                        self.currentFrame = (self.currentFrame + 1)
                    else:
                        center = self.rect.center
                        self.shadow = self.shadowFrames["dead vertical"]
                        self.rect = self.shadow.get_rect()
                        self.rect.center = center
                    bottom = self.imgRect.bottom
                    left = self.imgRect.left
                    self.image = self.deadFramesDown[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.left = left
            elif self.facing == "upleft":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.deadFramesUp) - 1:
                        self.currentFrame = (self.currentFrame + 1)
                    else:
                        center = self.rect.center
                        self.shadow = self.shadowFrames["dead vertical"]
                        self.rect = self.shadow.get_rect()
                        self.rect.center = center
                    bottom = self.imgRect.bottom
                    left = self.imgRect.left
                    self.image = self.deadFramesUp[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.left = left
            elif self.facing == "upright":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.deadFramesUp) - 1:
                        self.currentFrame = (self.currentFrame + 1)
                    else:
                        center = self.rect.center
                        self.shadow = self.shadowFrames["dead vertical"]
                        self.rect = self.shadow.get_rect()
                        self.rect.center = center
                    bottom = self.imgRect.bottom
                    left = self.imgRect.left
                    self.image = self.deadFramesUp[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.left = left

        if (self.walking or self.game.player.vx != 0 or self.game.player.vy != 0) and (
                self.currentFrame == 0 or self.currentFrame == 6) and now == self.lastUpdate:
            self.stepSound.stop()
            pg.mixer.Sound.play(self.stepSound)


class MarioBattleComplete(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.alpha = 255
        self.speed = 120
        self.xp = self.game.player.stats["exp"]
        self.numSpeed = self.game.battleXp / 45
        self.counter = 0
        self.currentFrame = 0
        self.lastUpdate = 0
        self.dead = False
        self.pose = False
        self.newXP = 0
        self.points = []
        self.loadImages()
        self.image = self.spinningFrames[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = self.game.player.imgRect.bottom
        self.rect.centerx = self.game.player.imgRect.centerx
        self.game.sprites.remove(self.game.player)
        for i in range(self.speed + 1):
            self.points.append(pt.getPointOnLine(self.rect.centerx, self.rect.centery, 400,
                                                 300, (i / self.speed)))

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

        self.poseFrames = [sheet.getImageName("mario_winpose_1.png"),
                           sheet.getImageName("mario_winpose_2.png"),
                           sheet.getImageName("mario_winpose_3.png"), ]

    def update(self):
        self.animate()
        if self.counter < len(self.points) - 1:
            self.counter += 1
        else:
            if self.newXP < self.game.battleXp - self.numSpeed:
                self.game.player.stats["exp"] += self.numSpeed
                self.newXP += self.numSpeed
            elif self.image == self.spinningFrames[-1]:
                self.game.player.stats["exp"] = self.xp + self.game.battleXp
                self.currentFrame = 0
                self.pose = True
            else:
                self.game.player.stats["exp"] = self.xp + self.game.battleXp

        self.rect.center = self.points[self.counter]

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.newXP < self.game.battleXp - self.numSpeed:
                if self.currentFrame < len(self.spinningFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.spinningFrames))
                else:
                    self.currentFrame = 0
                center = self.rect.center
                self.image = self.spinningFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center
            else:
                if self.currentFrame < len(self.spinningFrames) and not self.pose:
                    if self.currentFrame < len(self.spinningFrames) - 1:
                        self.currentFrame = (self.currentFrame + 1)
                    center = self.rect.center
                    self.image = self.spinningFrames[self.currentFrame]
                    self.rect = self.image.get_rect()
                    self.rect.center = center
                else:
                    if self.currentFrame < len(self.poseFrames) - 1:
                        self.currentFrame = (self.currentFrame + 1)
                        center = self.rect.center
                        self.image = self.poseFrames[self.currentFrame]
                        self.rect = self.image.get_rect()
                        self.rect.center = center


class LuigiBattleComplete(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.alpha = 255
        self.speed = 120
        self.counter = 0
        self.xp = self.game.follower.stats["exp"]
        self.numSpeed = self.game.battleXp / 45
        self.currentFrame = 0
        self.lastUpdate = 0
        self.dead = False
        self.pose = False
        self.newXP = 0
        self.points = []
        self.loadImages()
        self.image = self.spinningFrames[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = self.game.follower.imgRect.bottom
        self.rect.centerx = self.game.follower.imgRect.centerx
        self.game.sprites.remove(self.game.follower)
        for i in range(self.speed + 1):
            self.points.append(pt.getPointOnLine(self.rect.centerx, self.rect.centery, 400,
                                                 500, (i / self.speed)))

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

        self.poseFrames = [sheet.getImageName("luigi_winpose_1.png"),
                           sheet.getImageName("luigi_winpose_2.png"),
                           sheet.getImageName("luigi_winpose_3.png"), ]

    def update(self):
        self.animate()
        if self.counter < len(self.points) - 1:
            self.counter += 1
        else:
            if self.newXP < self.game.battleXp - self.numSpeed:
                self.game.follower.stats["exp"] += self.numSpeed
                self.newXP += self.numSpeed
            elif self.image == self.spinningFrames[-1]:
                self.game.follower.stats["exp"] = self.xp + self.game.battleXp
                self.currentFrame = 0
                self.pose = True
            else:
                self.game.follower.stats["exp"] = self.xp + self.game.battleXp

        self.rect.center = self.points[self.counter]

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.newXP < self.game.battleXp - self.numSpeed:
                if self.currentFrame < len(self.spinningFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.spinningFrames))
                else:
                    self.currentFrame = 0
                center = self.rect.center
                self.image = self.spinningFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center
            else:
                if self.currentFrame < len(self.spinningFrames) and not self.pose:
                    if self.currentFrame < len(self.spinningFrames) - 1:
                        self.currentFrame = (self.currentFrame + 1)
                    center = self.rect.center
                    self.image = self.spinningFrames[self.currentFrame]
                    self.rect = self.image.get_rect()
                    self.rect.center = center
                else:
                    if self.currentFrame < len(self.poseFrames) - 1:
                        self.currentFrame = (self.currentFrame + 1)
                        center = self.rect.center
                        self.image = self.poseFrames[self.currentFrame]
                        self.rect = self.image.get_rect()
                        self.rect.center = center


class Block(pg.sprite.Sprite):
    def __init__(self, game, pos):
        pg.sprite.Sprite.__init__(self, game.blocks)
        self.game = game
        self.game.sprites.append(self)
        self.ID = -17
        self.newID = False
        self.hit = False
        self.alpha = 255
        self.vy = 0
        self.dy = 0.065
        self.loadImages()
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.image = self.blockSprite
        self.imgRect = self.image.get_rect()
        self.imgRect.centerx = self.rect.centerx
        self.imgRect.centery = self.rect.centery - 200

    def loadImages(self):
        sheet = spritesheet("sprites/blocks.png", "sprites/blocks.xml")

        self.shadow = sheet.getImageName("shadow.png")

        self.blockSprite = sheet.getImageName("block.png")

        self.hitSprite = sheet.getImageName("empty block.png")

    def update(self):
        if not self.newID:
            if self.ID in self.game.hitBlockList:
                self.hit = True
            self.newID = True
        if self.hit:
            self.image = self.hitSprite
        else:
            self.vy += self.dy
            if self.vy > 1 or self.vy < -1:
                self.dy *= -1
            self.imgRect.y += round(self.vy)

        hits = pg.sprite.collide_rect(self, self.game.player)
        if hits:
            rect = self.rect
            self.rect = self.imgRect
            hitsRound2 = pg.sprite.collide_rect(self, self.game.playerCol)
            self.rect = rect
            if hitsRound2:
                self.game.hitBlockList.append(self.ID)
                self.game.player.airTimer = airTime
                self.hit = True

        hits = pg.sprite.collide_rect(self, self.game.follower)
        if hits:
            rect = self.rect
            self.rect = self.imgRect
            hitsRound2 = pg.sprite.collide_rect(self, self.game.followerCol)
            self.rect = rect
            if hitsRound2:
                self.game.hitBlockList.append(self.ID)
                self.game.follower.airTimer = airTime
                self.hit = True


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((w, h))
        self.image.fill(sansEye)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class BattleTransition(pg.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.effects
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.offset = False
        self.loadImages()
        self.lastUpdate = 0
        self.currentFrame = -1
        self.alpha = 255
        self.room = self.game.room
        self.image = self.sprites[0]
        self.rect = self.image.get_rect()
        self.rect.center = (width / 2, height / 2)

    def loadImages(self):
        self.sprites = battleTransitionSprites

    def update(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 60:
            self.lastUpdate = now
            if self.currentFrame < len(self.sprites) - 1:
                self.currentFrame = (self.currentFrame + 1)
            center = self.rect.center
            self.image = self.sprites[self.currentFrame]
            self.rect = self.image.get_rect()
            self.rect.center = center

        if self.currentFrame == len(self.sprites) - 1 and self.room != self.game.room:
            self.alpha -= 20

        if self.alpha <= 0:
            self.kill()


class TextBox(pg.sprite.Sprite):
    def __init__(self, game, parent, text, type="dialogue"):
        pg.sprite.Sprite.__init__(self, game.ui)
        self.speed = 20
        self.game = game
        self.game.textBoxOpenSound.play()
        self.game.player.canMove = False
        self.game.follower.canMove = False
        self.parent = parent
        self.offset = False
        self.closing = False
        self.advancing = False
        self.scale = 0
        self.counter = 0
        self.alpha = 0
        self.type = type
        self.text = text.copy()
        for i in range(len(self.text)):
            self.text[i] = self.text[i] + "\n\a"
        self.page = 0
        self.playSound = 0
        self.currentCharacter = 0
        self.points = []
        self.pause = 0
        self.pTimes = 0
        self.PTimes = 0
        self.numTimes = 0
        self.angle = 0
        self.angleDir = True
        self.advance = talkAdvanceSprite
        self.advanceRect = self.advance.get_rect()
        self.image = textboxSprites[type]
        self.rect = self.image.get_rect()
        self.maxRect = self.image.get_rect()
        self.rect.center = self.game.camera.offset(parent.rect).center
        self.advanceRect.center = (
        self.rect.right - self.advanceRect.width - 20, self.rect.bottom - self.advanceRect.width - 20)
        self.image = pg.transform.scale(textboxSprites[self.type],
                                        (int(self.maxRect.width * self.scale), int(self.maxRect.height * self.scale)))
        if self.rect.y > height / 2:
            for i in range(self.speed + 1):
                self.points.append(
                    pt.getPointOnLine(self.rect.centerx, self.rect.centery, width / 2, (self.rect.height / 2) + 20,
                                      (i / self.speed)))
        else:
            for i in range(self.speed + 1):
                self.points.append(pt.getPointOnLine(self.rect.centerx, self.rect.centery, width / 2,
                                                     height - (self.rect.height / 2) - 20, (i / self.speed)))

    def update(self):
        if not self.closing:
            if self.scale <= 1:
                self.scale += 0.05
            if self.alpha < 255:
                self.alpha += 10
            if self.counter < len(self.points) - 1:
                self.counter += 1
        else:
            if self.scale > 0:
                self.scale -= 0.05
            if self.alpha > 0:
                self.alpha -= 10
            if self.counter < len(self.points) - 1:
                self.counter += 1
            else:
                self.game.player.canMove = True
                self.game.follower.canMove = True
                self.parent.textbox = "complete"
                self.kill()

        if not self.advancing:
            if self.type == "dialogue":
                self.textx = self.rect.left + 70
                self.texty = self.rect.top + 40
        else:
            self.texty -= 10
            if self.texty <= self.rect.top - 220:
                self.page += 1
                self.currentCharacter = 0
                self.advancing = False

        self.rect.center = self.points[self.counter]
        center = self.rect.center
        self.image = pg.transform.scale(textboxSprites[self.type],
                                        (int(self.maxRect.width * self.scale), int(self.maxRect.height * self.scale)))
        self.rect = self.image.get_rect()
        self.rect.center = center

        if abs(self.angle) >= 30:
            self.angleDir = not self.angleDir
        if self.angleDir:
            self.angle += 2
        else:
            self.angle -= 2
        self.advance = pg.transform.rotate(talkAdvanceSprite, self.angle)
        self.advanceRect = self.advance.get_rect()
        self.advanceRect.right = self.rect.right - 50
        self.advanceRect.bottom = self.rect.bottom - 55

    def draw(self):
        keys = pg.key.get_pressed()
        character = self.text[self.page]
        character = character[:self.currentCharacter]
        if self.currentCharacter < len(self.text[self.page]):
            if self.text[self.page][self.currentCharacter] == "/":
                if self.text[self.page][self.currentCharacter + 1] == "p":
                    self.pTimes += 1
                    self.text[self.page] = self.text[self.page].replace("/p", "", self.pTimes)
                    self.pause = fps / 2
                if self.text[self.page][self.currentCharacter + 1] == "P":
                    self.PTimes += 1
                    self.text[self.page] = self.text[self.page].replace("/P", "", self.PTimes)
                    self.pause = 60
                try:
                    if int(self.text[self.page][self.currentCharacter + 1]) % 1 == 0:
                        self.numTimes += 1
                        self.pause = int(self.text[self.page][self.currentCharacter + 1])
                        self.text[self.page] = self.text[self.page].replace("/1", "", self.numTimes)
                        self.text[self.page] = self.text[self.page].replace("/2", "", self.numTimes)
                        self.text[self.page] = self.text[self.page].replace("/3", "", self.numTimes)
                        self.text[self.page] = self.text[self.page].replace("/4", "", self.numTimes)
                        self.text[self.page] = self.text[self.page].replace("/5", "", self.numTimes)
                        self.text[self.page] = self.text[self.page].replace("/6", "", self.numTimes)
                        self.text[self.page] = self.text[self.page].replace("/7", "", self.numTimes)
                        self.text[self.page] = self.text[self.page].replace("/8", "", self.numTimes)
                        self.text[self.page] = self.text[self.page].replace("/9", "", self.numTimes)
                except:
                    pass
        completeText = False
        self.game.blit_alpha(self.game.screen, self.image, self.rect, self.alpha)
        if self.scale >= 1:
            text, pos = ptext.draw(character, (self.textx, self.texty), fontname=dialogueFont, color=black, fontsize=35,
                                   lineheight=0.8, surf=None)
            self.game.screen.set_clip((self.rect.left, self.rect.top + 30, 1000, 250))
            self.game.screen.blit(text, pos)
            self.game.screen.set_clip(None)
            if self.pause <= 0:
                if self.currentCharacter < len(self.text[self.page]):
                    for event in self.game.event:
                        if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                            pg.quit()
                        if event.type == pg.KEYDOWN:
                            if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                                completeText = True
                    if completeText:
                        self.text[self.page] = self.text[self.page].replace("/P", "")
                        self.text[self.page] = self.text[self.page].replace("/p", "")
                        self.text[self.page] = self.text[self.page].replace("/1", "")
                        self.text[self.page] = self.text[self.page].replace("/2", "")
                        self.text[self.page] = self.text[self.page].replace("/3", "")
                        self.text[self.page] = self.text[self.page].replace("/4", "")
                        self.text[self.page] = self.text[self.page].replace("/5", "")
                        self.text[self.page] = self.text[self.page].replace("/6", "")
                        self.text[self.page] = self.text[self.page].replace("/7", "")
                        self.text[self.page] = self.text[self.page].replace("/8", "")
                        self.text[self.page] = self.text[self.page].replace("/9", "")
                        self.currentCharacter = len(self.text[self.page])
                    else:
                        if self.playSound == 1:
                            pitch = random.randrange(0, 3)
                            if pitch == 0:
                                self.game.talkSoundLow.play()
                            elif pitch == 1:
                                self.game.talkSoundMed.play()
                            elif pitch == 2:
                                self.game.talkSoundHigh.play()
                            self.playSound = 0
                        else:
                            self.playSound += 1
                        self.currentCharacter += 1
                else:
                    for event in self.game.event:
                        if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                            pg.quit()
                        if event.type == pg.KEYDOWN:
                            if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                                if self.page < len(self.text) - 1:
                                    if not self.advancing: self.game.talkAdvanceSound.play()
                                    self.advancing = True
                                    self.pTimes = 0
                                    self.PTimes = 0
                                    self.numTimes = 0
                                else:
                                    self.points = []
                                    for i in range(self.speed + 1):
                                        self.points.append(
                                            pt.getPointOnLine(self.rect.centerx, self.rect.centery,
                                                              self.game.camera.offset(self.parent.imgRect).centerx,
                                                              self.game.camera.offset(self.parent.imgRect).centery,
                                                              (i / self.speed)))
                                    self.counter = 0
                                    self.game.textBoxCloseSound.play()
                                    self.closing = True
                    if not self.advancing:
                        self.game.screen.blit(self.advance, self.advanceRect.center)
            else:
                self.pause -= 1


class MiniTextbox(pg.sprite.Sprite):
    def __init__(self, game, parent, text, pos):
        pg.sprite.Sprite.__init__(self, game.ui)
        self.speed = 20
        self.game = game
        self.parent = parent
        self.parent.textbox = self
        self.offset = True
        self.closing = False
        self.advancing = False
        self.scale = 0
        self.counter = 0
        self.alpha = 0
        self.text = text.copy()
        for i in range(len(self.text)):
            self.text[i] = self.text[i] + "\n\a"
        self.page = 0
        self.currentCharacter = 0
        self.points = []
        self.pause = 0
        self.pTimes = 0
        self.PTimes = 0
        self.numTimes = 0
        self.angle = 0
        self.image = textboxSprites["dialogue"]
        self.rect = self.image.get_rect()
        self.maxRect = self.image.get_rect()
        self.rect.center = pos
        self.image = pg.transform.scale(textboxSprites["dialogue"],
                                        (int(self.maxRect.width * self.scale), int(self.maxRect.height * self.scale)))

    def update(self):
        if not self.closing:
            if self.scale <= 0.3:
                self.scale += 0.02
            if self.alpha < 255:
                self.alpha += 10
        else:
            if self.scale > 0:
                self.scale -= 0.02
            if self.alpha > 0:
                self.alpha -= 10
            else:
                self.parent.textbox = None
                self.kill()

        center = self.rect.center
        self.image = pg.transform.scale(textboxSprites["dialogue"],
                                        (int(self.maxRect.width * self.scale), int(self.maxRect.height * self.scale)))
        self.rect = self.image.get_rect()
        self.rect.center = center

    def draw(self):
        character = self.text[self.page]
        character = character[:self.currentCharacter]
        self.game.blit_alpha(self.game.screen, self.image, self.game.camera.offset(self.rect), self.alpha)
        if self.scale >= 0.3:
            textx = self.game.camera.offset(self.rect).left + 10
            texty = self.game.camera.offset(self.rect).top + 10
            ptext.draw(character, (textx, texty), fontname=dialogueFont, color=black, fontsize=20,
                       lineheight=0.8, surf=self.game.screen)
            if self.currentCharacter < len(self.text[self.page]):
                self.currentCharacter += 2
                if self.currentCharacter > len(self.text[self.page]):
                    self.currentCharacter = len(self.text[self.page])
