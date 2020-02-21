import queue as Q
import math
import ptext
import random
import xml.etree.ElementTree as ET
import pygame as pg
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
        self.canMove = True
        self.hitTime = 0
        self.alpha = 255
        self.stepSound = pg.mixer.Sound("sounds/coin.ogg")
        self.walking = False
        self.jumping = False
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

        self.stats = {"level": 1, "maxHP": 10, "maxBP": 5, "pow": 2, "def": 0, "stache": 3, "hp": 10, "bp": 5}

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

    def update(self):
        self.animate()
        if self.stats["hp"] < 0:
            self.stats["hp"] = 0
        if self.stats["hp"] == 0:
            self.dead = True

        now = pg.time.get_ticks()
        keys = pg.key.get_pressed()
        self.vx, self.vy = 0, 0

        if not self.dead and self.canMove:
            if not self.hit and not self.game.follower.hit:
                if keys[pg.K_w]:
                    self.vy = -playerSpeed
                if keys[pg.K_a]:
                    self.vx = -playerSpeed
                if keys[pg.K_s]:
                    self.vy = playerSpeed
                if keys[pg.K_d]:
                    self.vx = playerSpeed
                if keys[pg.K_m] or keys[pg.K_SPACE]:
                    if not self.jumping and not self.hit and not self.dead and self.canMove:
                        self.jumping = True
                        self.jumpTimer = 1
                        self.airTimer = 0
                        self.game.jumpSound.play()

        if self.hit:
            if now - self.hitTime > 250:
                self.hit = False

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

        if self.walking and (self.currentFrame == 0 or self.currentFrame == 6) and now == self.lastUpdate:
            self.stepSound.stop()
            pg.mixer.Sound.play(self.stepSound)


class Luigi(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.stepSound = pg.mixer.Sound("sounds/coin.ogg")
        self.moveQueue = Q.Queue()
        self.hit = False
        self.dead = False
        self.canMove = True
        self.hitTime = 0
        self.alpha = 255
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
        self.shadow = self.shadowFrames["normal"]
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)
        self.going = "irrelevent"
        self.vx, self.vy = 0, 0

        self.stats = {"level": 1, "maxHP": 13, "maxBP": 5, "pow": 1, "def": 0, "stache": 3, "hp": 13, "bp": 5}

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
                    self.moveQueue.put(self.game.player.rect.x)
                    self.moveQueue.put(self.game.player.rect.y)
                    self.moveQueue.put(self.game.player.facing)
                    if self.moveQueue.qsize() > 30:
                        self.rect.x = self.moveQueue.get()
                        self.rect.y = self.moveQueue.get()
                        self.facing = self.moveQueue.get()
        elif not self.dead and self.game.player.dead and self.canMove:
            self.moveQueue = Q.Queue()
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

        if not self.hit:
            if keys[pg.K_l] or keys[pg.K_SPACE]:
                if not self.jumping and not self.hit and not self.dead and self.canMove:
                    self.jumping = True
                    self.jumpTimer = 1
                    self.airTimer = 0
                    self.game.jumpSound.play()

        if self.hit:
            if now - self.hitTime > 250:
                self.hit = False

        if not self.jumping:
            self.imgRect.bottom = self.rect.bottom - 5
            self.imgRect.centerx = self.rect.centerx
        else:
            self.jump()
            self.imgRect.centerx = self.rect.centerx

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


class GoombaT(pg.sprite.Sprite):
    def __init__(self, game, start):
        pg.sprite.Sprite.__init__(self)
        self.text = []
        self.game = game
        self.textbox = None
        self.game.sprites.append(self)
        sheet = spritesheet("sprites/enemies.png", "sprites/enemies.xml")
        self.image = sheet.getImageName("goomba_walking_down_1.png")
        self.shadow = sheet.getImageName("shadow.png")
        self.rect = self.shadow.get_rect()
        self.imgRect = self.image.get_rect()
        self.rect.center = start
        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx
        self.alpha = 255
        self.counter = 0
        self.text.append("It's a beautiful day outside.\nBirds are singing...\nFlowers are blooming...\n\a")
        self.text.append("On days like these...\nKids like you...\n\a")
        self.text.append("SHOULD BE BURNING IN HELL\n\a")

    def update(self):
        if self.game.textbox is None:
            keys = pg.key.get_pressed()
            if pg.sprite.collide_rect(self, self.game.player) and (keys[pg.K_m] or keys[pg.K_l] or keys[pg.K_SPACE]):
                self.game.textbox = TextBox(self.game, self, self.text)
        else:
            pg.event.clear()


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
        self.scale = 0
        self.counter = 0
        self.alpha = 0
        self.type = type
        self.text = text
        self.page = 0
        self.playSound = 0
        self.currentCharacter = 0
        self.points = []
        self.image = textboxSprites[type]
        self.rect = self.image.get_rect()
        self.maxRect = self.image.get_rect()
        self.rect.center = self.game.camera.offset(parent.rect).center
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
                self.game.textbox = None
                self.kill()

        self.rect.center = self.points[self.counter]
        center = self.rect.center
        self.image = pg.transform.scale(textboxSprites[self.type],
                                        (int(self.maxRect.width * self.scale), int(self.maxRect.height * self.scale)))
        self.rect = self.image.get_rect()
        self.rect.center = center

    def draw(self):
        character = self.text[self.page]
        character = character[0: self.currentCharacter]
        completeText = False
        self.game.blit_alpha(self.game.screen, self.image, self.rect, self.alpha)
        if self.scale >= 1:
            ptext.draw(character, (self.rect.left + 20, self.rect.top + 30), fontname=dialogueFont, color=black, fontsize=40, lineheight=0.75)
            if self.currentCharacter < len(self.text[self.page]):
                for event in pg.event.get():
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                            completeText = True
                if completeText:
                    self.currentCharacter = len(self.text[self.page])
                else:
                    if self.playSound == 1:
                        pitch = random.randrange(0, 3)
                        if pitch == 0:
                            self.game.talkSoundLow.play()
                        elif pitch == 1:
                            self.game.talkSoundMed.play()
                        else:
                            self.game.talkSoundHigh.play()
                        self.playSound = 0
                    else:
                        self.playSound += 1
                    self.currentCharacter += 1
            else:
                for event in pg.event.get():
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                            if self.page < len(self.text) - 1:
                                self.currentCharacter = 0
                                self.page += 1
                            else:
                                self.points = []
                                for i in range(self.speed + 1):
                                    self.points.append(
                                        pt.getPointOnLine(self.rect.centerx, self.rect.centery, self.game.camera.offset(self.parent.imgRect).centerx,
                                                          self.game.camera.offset(self.parent.imgRect).centery,
                                                          (i / self.speed)))
                                self.counter = 0
                                self.game.textBoxCloseSound.play()
                                self.closing = True

