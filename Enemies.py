import xml.etree.ElementTree as ET
import pygame as pg
from UI import *
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


class GoombaO(pg.sprite.Sprite):
    def __init__(self, game, x, y, battle="THBEM"):
        self.groups = game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.newID = False
        self.game = game
        self.ID = -12
        self.game.sprites.append(self)
        self.alpha = 255
        sheet = spritesheet("sprites/enemies.png", "sprites/enemies.xml")
        self.image = sheet.getImageName("goomba_walking_down_1.png")
        self.shadow = sheet.getImageName("shadow.png")
        self.rect = self.shadow.get_rect()
        self.imgRect = self.image.get_rect()
        self.battle = battle
        self.rect.center = (x, y)
        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx

    def update(self):
        if not self.newID:
            if self.ID in self.game.despawnList:
                self.game.sprites.remove(self)
            self.newID = True
        if self in self.game.sprites:
            hits = pg.sprite.collide_rect(self, self.game.player)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self, self.game.playerCol)
                if hitsRound2:
                    self.game.despawnList.append(self.ID)
                    if len(self.game.despawnList) > 13:
                        self.game.despawnList.remove(self.game.despawnList[0])
                    print(self.game.despawnList)
                    self.game.loadBattle(self.battle)

            hits = pg.sprite.collide_rect(self, self.game.follower)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self, self.game.followerCol)
                if hitsRound2:
                    self.game.despawnList.append(self.ID)
                    if len(self.game.despawnList) > 13:
                        self.game.despawnList.remove(self.game.despawnList[0])
                    print(self.game.despawnList)
                    self.game.loadBattle(self.battle)


class Goomba(pg.sprite.Sprite):
    def __init__(self, game, x, y, vx, vy, facing="down"):
        self.groups = game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.vx = vx
        self.vy = vy
        self.game = game
        self.hit = False
        self.hitTimer = 0
        self.going = True
        self.dead = False
        self.game.sprites.append(self)
        self.loadImages()
        self.image = self.walkingFramesDown[0]
        self.currentFrame = 0
        self.lastUpdate = 0
        self.facing = facing
        self.shadow = self.shadowFrame
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)
        self.alpha = 255
        self.mask = pg.mask.from_surface(self.image)

        # Stats
        self.stats = {"maxHP": 4, "hp": 4, "pow": 2, "def": 0, "exp": 2}

    def loadImages(self):
        sheet = spritesheet("sprites/enemies.png", "sprites/enemies.xml")

        self.walkingFramesUp = [sheet.getImageName("goomba_walking_up_1.png"),
                                sheet.getImageName("goomba_walking_up_2.png"),
                                sheet.getImageName("goomba_walking_up_3.png"),
                                sheet.getImageName("goomba_walking_up_4.png"),
                                sheet.getImageName("goomba_walking_up_5.png"),
                                sheet.getImageName("goomba_walking_up_6.png"),
                                sheet.getImageName("goomba_walking_up_7.png"),
                                sheet.getImageName("goomba_walking_up_8.png")]

        self.walkingFramesDown = [sheet.getImageName("goomba_walking_down_1.png"),
                                  sheet.getImageName("goomba_walking_down_2.png"),
                                  sheet.getImageName("goomba_walking_down_3.png"),
                                  sheet.getImageName("goomba_walking_down_4.png"),
                                  sheet.getImageName("goomba_walking_down_5.png"),
                                  sheet.getImageName("goomba_walking_down_6.png"),
                                  sheet.getImageName("goomba_walking_down_7.png"),
                                  sheet.getImageName("goomba_walking_down_8.png")]

        self.walkingFramesLeft = [sheet.getImageName("goomba_walking_left_1.png"),
                                  sheet.getImageName("goomba_walking_left_2.png"),
                                  sheet.getImageName("goomba_walking_left_3.png"),
                                  sheet.getImageName("goomba_walking_left_4.png"),
                                  sheet.getImageName("goomba_walking_left_5.png"),
                                  sheet.getImageName("goomba_walking_left_6.png"),
                                  sheet.getImageName("goomba_walking_left_7.png"),
                                  sheet.getImageName("goomba_walking_left_8.png")]

        self.walkingFramesRight = [sheet.getImageName("goomba_walking_right_1.png"),
                                   sheet.getImageName("goomba_walking_right_2.png"),
                                   sheet.getImageName("goomba_walking_right_3.png"),
                                   sheet.getImageName("goomba_walking_right_4.png"),
                                   sheet.getImageName("goomba_walking_right_5.png"),
                                   sheet.getImageName("goomba_walking_right_6.png"),
                                   sheet.getImageName("goomba_walking_right_7.png"),
                                   sheet.getImageName("goomba_walking_right_8.png")]

        self.shadowFrame = sheet.getImageName("shadow.png")

    def animate(self):
        now = pg.time.get_ticks()
        if self.facing == "down":
            if now - self.lastUpdate > 30:
                self.lastUpdate = now
                if self.currentFrame < len(self.walkingFramesDown):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesDown))
                else:
                    self.currentFrame = 0
                center = self.imgRect.center
                self.image = self.walkingFramesDown[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.facing == "up":
            if now - self.lastUpdate > 30:
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
            if now - self.lastUpdate > 30:
                self.lastUpdate = now
                if self.currentFrame < len(self.walkingFramesLeft):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesLeft))
                else:
                    self.currentFrame = 0
                center = self.imgRect.center
                self.image = self.walkingFramesLeft[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.facing == "right":
            if now - self.lastUpdate > 30:
                self.lastUpdate = now
                if self.currentFrame < len(self.walkingFramesRight):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFramesRight))
                else:
                    self.currentFrame = 0
                center = self.imgRect.center
                self.image = self.walkingFramesRight[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center

    def update(self):
        self.animate()
        if self.stats["hp"] <= 0:
            self.going = False
            self.alpha -= 10

        if self.alpha <= 0:
            self.game.sprites.remove(self)
            self.kill()

        for wall in self.game.walls:
            if pg.sprite.collide_rect(self, wall):
                if self.facing == "up":
                    self.rect.top = wall.rect.bottom
                    self.rect.y -= self.vy
                    self.facing = "down"
                elif self.facing == "down":
                    self.rect.bottom = wall.rect.top
                    self.rect.y += self.vy
                    self.facing = "up"
                elif self.facing == "left":
                    self.rect.left = wall.rect.right
                    self.rect.x -= self.vx
                    self.facing = "right"
                elif self.facing == "right":
                    self.rect.right = wall.rect.left
                    self.rect.x += self.vx
                    self.facing = "left"

        if self.going:
            if self.facing == "down":
                self.rect.y += self.vy
            elif self.facing == "up":
                self.rect.y -= self.vy
            elif self.facing == "left":
                self.rect.x -= self.vx
            elif self.facing == "right":
                self.rect.x += self.vx

        if self.rect.x > self.game.map.width + 60:
            self.rect.x = -60
        if self.rect.x < -60:
            self.rect.x = self.game.map.width + 60
        if self.rect.y > self.game.map.height + 100:
            self.rect.y = -100
        if self.rect.y < -100:
            self.rect.y = self.game.map.height + 100

        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx

        keys = pg.key.get_pressed()
        doubleDamageM = False
        doubleDamageL = False

        if self.hit:
            self.hitTimer += 1
            if self.hitTimer > 5:
                self.hit = False
                self.hitTimer = 0

        if self.game.player.stats["hp"] != 0:
            hits = pg.sprite.collide_rect(self.game.player, self)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                if keys[pg.K_m] and self.game.player.going == "down" and self.game.player.imgRect.bottom <= self.imgRect.top + 50:
                    doubleDamageM = True
                if hitsRound2:
                    if self.game.player.going == "down" and self.game.player.jumping and self.stats["hp"] > 0:
                        if doubleDamageM:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (2 * (self.game.player.stats["pow"] - self.stats["def"])))
                            self.stats["hp"] -= 2 * (self.game.player.stats["pow"] - self.stats["def"])
                            self.hit = True
                        else:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (self.game.player.stats["pow"] - self.stats["def"]))
                            self.stats["hp"] -= (self.game.player.stats["pow"] - self.stats["def"])
                            self.hit = True
                        self.game.player.airTimer = 0
                    else:
                        if not self.game.player.hit and self.stats["hp"] > 0 and not self.hit:
                            HitNumbers(self.game, self.game.room, (self.game.player.imgRect.left, self.game.player.imgRect.top - 2),(max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                            self.game.player.stats["hp"] -= (max(self.stats["pow"] - self.game.player.stats["def"], 1))
                            if self.game.player.stats["hp"] <= 0:
                                self.game.player.stats["hp"] = 0
                                self.game.player.currentFrame = 0
                            self.game.player.hitTime = pg.time.get_ticks()
                            self.game.player.hit = True

        if self.game.follower.stats["hp"] != 0:
            luigiHits = pg.sprite.collide_rect(self.game.follower, self)
            if luigiHits:
                hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                if keys[
                    pg.K_l] and self.game.follower.going == "down" and self.game.follower.imgRect.bottom <= self.imgRect.top + 50:
                    doubleDamageL = True
                if hitsRound2:
                    if self.game.follower.going == "down" and self.game.follower.jumping and self.stats["hp"] > 0:
                        if doubleDamageL:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (2 * (self.game.follower.stats["pow"] - self.stats["def"])))
                            self.stats["hp"] -= 2 * (self.game.follower.stats["pow"] - self.stats["def"])
                            self.hit = True
                        else:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (self.game.follower.stats["pow"] - self.stats["def"]))
                            self.stats["hp"] -= (self.game.follower.stats["pow"] - self.stats["def"])
                            self.hit = True
                        self.game.follower.airTimer = 0
                    else:
                        if not self.game.follower.hit and self.stats["hp"] > 0 and not self.hit:
                            HitNumbers(self.game, self.game.room, (self.game.follower.imgRect.left, self.game.follower.imgRect.top - 2), (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                            self.game.follower.stats["hp"] -= (max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                            if self.game.follower.stats["hp"] <= 0:
                                self.game.follower.stats["hp"] = 0
                                self.game.follower.currentFrame = 0
                            self.game.follower.hitTime = pg.time.get_ticks()
                            self.game.follower.hit = True
