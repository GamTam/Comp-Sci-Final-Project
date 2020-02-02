import pygame as pg
import queue as Q
import xml.etree.ElementTree as ET
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


class Mario(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.stepSound = pg.mixer.Sound("sounds/coin.ogg")
        self.walking = False
        self.jumping = False
        self.jumpTimer = 0
        self.airTimer = 0
        self.facing = "right"
        self.colFace = "right"
        self.loadImages()
        self.image = self.standingFrames[0]
        self.shadow = self.shadowFrame
        self.lastUpdate = 0
        self.currentFrame = 0
        self.speed = playerSpeed
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)
        self.imgRect.center = (x, y - 35)
        self.vx, self.vy = 0, 0

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

        self.shadowFrame = sheet.getImageName("shadow.png")

    def wallCollisions(self, group, vx=0, vy=0):
        for wall in group:
            if pg.sprite.collide_rect(self, wall):
                if vx > 0:
                    self.rect.right = wall.rect.left
                    self.vx = 0
                if vx < 0:
                    self.rect.left = wall.rect.right
                    self.vx = 0
                if vy < 0:
                    self.rect.top = wall.rect.bottom
                    self.vy = 0
                if vy > 0:
                    self.rect.bottom = wall.rect.top
                    self.vy = 0

    def jump(self):
        if self.jumpTimer < jumpHeight and self.airTimer == 0:
            self.jumpTimer += 1.5
        elif self.jumpTimer >= jumpHeight:
            self.airTimer += 1
        if self.airTimer >= airTime and self.jumpTimer != 0:
            self.jumpTimer -= 1.5
        if self.jumpTimer <= 0 and self.airTimer != 0:
            self.jumping = False
        jumpOffset = self.jumpTimer * jumpHeight
        self.imgRect.bottom = (self.rect.bottom - 5) - jumpOffset

    def update(self):
        self.animate()
        keys = pg.key.get_pressed()
        self.vx, self.vy = 0, 0

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
        self.rect.y += self.vy
        self.wallCollisions(self.game.walls, 0, self.vy)

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

    def animate(self):
        now = pg.time.get_ticks()
        keys = pg.key.get_pressed()
        if not self.jumping:
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

        if self.walking and (self.currentFrame == 0 or self.currentFrame == 6) and now == self.lastUpdate:
            self.stepSound.stop()
            pg.mixer.Sound.play(self.stepSound)


class Luigi(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.stepSound = pg.mixer.Sound("sounds/coin.ogg")
        self.moveQueue = Q.Queue()
        self.game = game
        self.loadImages()
        self.facing = "right"
        self.lastUpdate = 0
        self.currentFrame = 0
        self.walking = False
        self.jumping = False
        self.jumpTimer = 0
        self.airTimer = 0
        self.image = self.standingFrames[0]
        self.shadow = self.shadowFrame
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)

    def jump(self):
        if self.jumpTimer < jumpHeight and self.airTimer == 0:
            self.jumpTimer += 1.5
        elif self.jumpTimer >= jumpHeight:
            self.airTimer += 1
        if self.airTimer >= airTime and self.jumpTimer != 0:
            self.jumpTimer -= 1.5
        if self.jumpTimer <= 0 and self.airTimer != 0:
            self.jumping = False
        jumpOffset = self.jumpTimer * jumpHeight
        self.imgRect.bottom = (self.rect.bottom - 5) - jumpOffset

    def update(self):
        self.animate()
        self.walking = self.game.player.walking
        if self.walking:
            self.moveQueue.put(self.game.player.rect.x)
            self.moveQueue.put(self.game.player.rect.y)
            self.moveQueue.put(self.game.player.facing)
            if self.moveQueue.qsize() > (fps / 2.5):
                self.rect.x = self.moveQueue.get()
                self.rect.y = self.moveQueue.get()
                self.facing = self.moveQueue.get()

        if not self.jumping:
            self.imgRect.bottom = self.rect.bottom - 5
            self.imgRect.centerx = self.rect.centerx
        else:
            self.jump()
            self.imgRect.centerx = self.rect.centerx

    def loadImages(self):
        sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")

        self.shadowFrame = sheet.getImageName("shadow.png")

        self.jumpingUpFrames = [sheet.getImageName("luigi_jumping_up_up.png"),
                                sheet.getImageName("luigi_jumping_up_down.png"),
                                sheet.getImageName("luigi_jumping_up_left.png"),
                                sheet.getImageName("luigi_jumping_up_right.png"),
                                sheet.getImageName("luigi_jumping_up_upleft.png"),
                                sheet.getImageName("luigi_jumping_up_upright.png"),
                                sheet.getImageName("luigi_jumping_up_downleft.png"),
                                sheet.getImageName("luigi_jumping_up_downright.png")]

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

    def animate(self):
        now = pg.time.get_ticks()
        if not self.jumping:
            if self.walking:
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
            if self.facing == "upright":
                center = self.imgRect.center
                self.image = self.jumpingUpFrames[5]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "upleft":
                center = self.imgRect.center
                self.image = self.jumpingUpFrames[4]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "downright":
                center = self.imgRect.center
                self.image = self.jumpingUpFrames[7]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "downleft":
                center = self.imgRect.center
                self.image = self.jumpingUpFrames[6]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "up":
                center = self.imgRect.center
                self.image = self.jumpingUpFrames[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "down":
                center = self.imgRect.center
                self.image = self.jumpingUpFrames[1]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "left":
                center = self.imgRect.center
                self.image = self.jumpingUpFrames[2]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "right":
                center = self.imgRect.center
                self.image = self.jumpingUpFrames[3]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center

        if self.walking and (self.currentFrame == 0 or self.currentFrame == 6) and now == self.lastUpdate:
            self.stepSound.stop()
            pg.mixer.Sound.play(self.stepSound)


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
