import collections as Q
import time
import pytweening as pt
from BlockContents import *
from UI import *
from LevelUp import *
from CutsceneObjects import *


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


class Fireball(pg.sprite.Sprite):
    def __init__(self, game, parent):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.game.fireballSound.play()
        self.dead = False
        self.parent = parent
        self.game.sprites.append(self)
        self.game.entities.append(self)
        self.alpha = 255
        self.currentFrame = 0
        self.offset = 20
        self.maxOffset = 50
        self.bounceSpeed = 5
        self.speed = 7
        self.vx = 0
        self.vy = 0

        if parent.facing == "left":
            self.vx = -self.speed
        elif parent.facing == "right":
            self.vx = self.speed
        elif parent.facing == "up":
            self.vy = -self.speed
        elif parent.facing == "down":
            self.vy = self.speed
        elif parent.facing == "upleft":
            self.vy = -self.speed
            self.vx = -self.speed
        elif parent.facing == "upright":
            self.vy = -self.speed
            self.vx = self.speed
        elif parent.facing == "downleft":
            self.vy = self.speed
            self.vx = -self.speed
        elif parent.facing == "downright":
            self.vy = self.speed
            self.vx = self.speed

        self.loadImages()
        self.image = self.images[0]
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = self.parent.rect.center
        self.imgRect.centerx, self.imgRect.centery = self.rect.centerx, self.rect.centery - self.offset

    def loadImages(self):
        sheet = spritesheet("sprites/fireball.png", "sprites/fireball.xml")

        self.images = [sheet.getImageName("1.png"),
                       sheet.getImageName("2.png"),
                       sheet.getImageName("3.png"),
                       sheet.getImageName("4.png"),
                       sheet.getImageName("5.png"),
                       sheet.getImageName("6.png"),
                       sheet.getImageName("7.png"),
                       sheet.getImageName("8.png"),
                       sheet.getImageName("9.png"),
                       sheet.getImageName("10.png"),
                       sheet.getImageName("11.png"),
                       sheet.getImageName("12.png"),
                       sheet.getImageName("13.png"),
                       sheet.getImageName("14.png"),
                       sheet.getImageName("15.png"),
                       sheet.getImageName("16.png"),
                       sheet.getImageName("17.png"),
                       sheet.getImageName("18.png"),
                       sheet.getImageName("19.png"),
                       sheet.getImageName("20.png"),
                       sheet.getImageName("21.png"),
                       sheet.getImageName("22.png"),
                       sheet.getImageName("23.png"),
                       sheet.getImageName("24.png"),
                       sheet.getImageName("25.png"),
                       sheet.getImageName("26.png"),
                       sheet.getImageName("27.png"),
                       sheet.getImageName("28.png"),
                       sheet.getImageName("29.png"),
                       sheet.getImageName("30.png")]

        self.shadow = sheet.getImageName("shadow.png")

    def update(self):
        if self.currentFrame < len(self.images) - 1:
            self.currentFrame = (self.currentFrame + 1) % (len(self.images))
        else:
            self.currentFrame = 0
        center = self.imgRect.center
        self.image = self.images[self.currentFrame]
        self.imgRect = self.image.get_rect()
        self.imgRect.center = center

        self.rect.x += self.vx
        self.rect.y += self.vy

        for wall in self.game.walls:
            if pg.sprite.collide_rect(self, wall):
                self.dead = True

        if self.rect.right < 0 or self.rect.left > self.game.map.width or self.rect.top > self.game.map.height + 100 or self.rect.bottom < 0:
                self.dead = True

        if self.dead:
            self.game.sprites.remove(self)
            self.game.entities.remove(self)
            self.game.fireballHitSound.play()
            self.parent.fireball = None
            self.parent.firing = False

        self.offset += self.bounceSpeed
        if self.offset >= self.maxOffset or self.offset <= 0:
            self.bounceSpeed *= -1

        self.imgRect.centerx = self.rect.centerx
        self.imgRect.bottom = self.rect.centery - self.offset + 10


class Lightning(pg.sprite.Sprite):
    def __init__(self, game, parent):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.dead = False
        self.playedThunderSound = False
        self.parent = parent
        self.game.sprites.append(self)
        self.game.entities.append(self)
        self.alpha = 255
        self.currentFrame = 0
        self.maxOffset = 50
        self.bounceSpeed = 5
        self.speed = 7
        self.vx = 0
        self.vy = 0

        if parent.facing == "left":
            self.vx = -self.speed
        elif parent.facing == "right":
            self.vx = self.speed
        elif parent.facing == "up":
            self.vy = -self.speed
        elif parent.facing == "down":
            self.vy = self.speed
        elif parent.facing == "upleft":
            self.vy = -self.speed
            self.vx = -self.speed
        elif parent.facing == "upright":
            self.vy = -self.speed
            self.vx = self.speed
        elif parent.facing == "downleft":
            self.vy = self.speed
            self.vx = -self.speed
        elif parent.facing == "downright":
            self.vy = self.speed
            self.vx = self.speed

        self.images = lightningSprites
        self.shadow = pg.image.load("sprites/lightning/shadow.png").convert_alpha()
        self.image = self.images[0]
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = self.parent.rect.center
        self.imgRect.centerx, self.imgRect.bottom = self.rect.centerx, self.rect.centery
        self.shootCounter = 0
        self.stop = False
        self.armed = False
        self.moveCounter = 0
        self.shooting = False

    def update(self):
        if self.shooting:
            if self.currentFrame < len(self.images) - 1:
                self.currentFrame = (self.currentFrame + 1) % (len(self.images))
            else:
                self.currentFrame = len(self.images) - 1
                self.dead = True
            center = self.imgRect.center
            self.image = self.images[self.currentFrame]
            self.imgRect = self.image.get_rect()
            self.imgRect.center = center

        if not self.shooting:
            if self.moveCounter <= fps * 5:
                self.rect.x += self.vx
                self.rect.y += self.vy
            elif self.moveCounter <= fps * 8:
                self.rect.x += self.vx / 2
                self.rect.y += self.vy / 2
            elif self.moveCounter <= fps * 10:
                self.rect.x += self.vx / 4
                self.rect.y += self.vy / 4
            else:
                self.armed = True
                self.moveCounter = fps * 10
        elif not self.playedThunderSound:
            self.game.thunderSound.play()
            self.playedThunderSound = True

        self.moveCounter += 1

        for wall in self.game.walls:
            if pg.sprite.collide_rect(self, wall):
                if self.rect.left < wall.rect.right or self.rect.right > wall.rect.left:
                    self.vx *= -1
                if self.rect.top < wall.rect.bottom or self.rect.bottom > wall.rect.top:
                    self.vy *= -1

                self.rect.x += self.vx
                self.rect.y += self.vy

        if self.armed:
            self.shootCounter += 1
            if self.shootCounter >= fps * 60:
                self.moveCounter = fps * 10
                self.shooting = True

        for enemy in self.game.enemies:
            if pg.sprite.collide_rect(self, enemy):
                self.shooting = True

        if self.rect.right < 0 or self.rect.left > self.game.map.width or self.rect.top > self.game.map.height + 100 or self.rect.bottom < 0:
                self.dead = True

        if self.dead:
            self.game.sprites.remove(self)
            self.game.entities.remove(self)
            self.parent.lightning = None
            self.parent.lightninging = False

        if self.shooting:
            self.imgRect.centerx = self.rect.centerx
            self.imgRect.bottom = self.rect.centery + 5
        else:
            self.imgRect.centerx = -1000
            self.imgRect.centery = -1000


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
        self.firing = False
        self.canMove = True
        self.canBeHit = True
        self.hitTime = 0
        self.ability = 0
        self.prevAbility = 12
        self.abilities = ["jump", "interact", "talk"]
        self.flySpeedX = 0
        self.flySpeedY = 0
        self.KR = 0
        self.KRTimer = 0
        self.alpha = 255
        self.stepSound = self.game.stoneSound
        self.walking = False
        self.jumping = False
        self.isHammer = None
        self.fireball = None
        self.jumpTimer = 0
        self.airTimer = 0
        self.facing = "right"
        self.going = "irrelevent"
        self.loadImages()
        self.image = self.standingFrames[0]
        self.shadow = self.shadowFrames["normal"]
        if self.game.area == "Castle Bleck":
            self.shadow.fill(gray, special_flags=pg.BLEND_ADD)
        self.lastUpdate = 0
        self.currentFrame = 0
        self.fireCounter = 0
        self.speed = playerSpeed
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)
        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.left = x
        self.vx, self.vy = 0, 0
        self.moveQueue = Q.deque()
        self.area = self.game.area

        self.stats = {"level": 1, "maxHP": 20, "maxBP": 10, "pow": 7, "def": 6, "hp": 20, "bp": 10, "exp": 0}
        self.statGrowth = {"maxHP": randomNumber(5), "maxBP": randomNumber(4), "pow": randomNumber(7),
                           "def": randomNumber(3)}
        self.attackPieces = [["Cavi Cape", 0], ["Teehee Valley", 0], ["Somnom Woods", 0],
                             ["Toad Town", 0]]
        self.brosAttacks = [["Red Shell", "self.redShell(enemies, song)",
                             pg.image.load("sprites/bros attacks/icons/redShellIcon.png").convert_alpha(), 100, 4]]

    def loadImages(self):
        sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")

        self.throwFrames = {"up": sheet.getImageName("mario_sans_throw_up.png"),
                            "down": sheet.getImageName("mario_sans_throw_down.png"),
                            "left": sheet.getImageName("mario_sans_throw_left.png"),
                            "right": sheet.getImageName("mario_sans_throw_right.png")}

        self.standingFrames = [sheet.getImageName("mario_standing_up.png"),
                               sheet.getImageName("mario_standing_down.png"),
                               sheet.getImageName("mario_standing_left.png"),
                               sheet.getImageName("mario_standing_right.png"),
                               sheet.getImageName("mario_standing_downright.png"),
                               sheet.getImageName("mario_standing_upright.png"),
                               sheet.getImageName("mario_standing_downleft.png"),
                               sheet.getImageName("mario_standing_upleft.png")]

        self.fireFrames = [sheet.getImageName("mario_fire_up.png"),
                               sheet.getImageName("mario_fire_down.png"),
                               sheet.getImageName("mario_fire_left.png"),
                               sheet.getImageName("mario_fire_right.png"),
                               sheet.getImageName("mario_fire_downright.png"),
                               sheet.getImageName("mario_fire_upright.png"),
                               sheet.getImageName("mario_fire_downleft.png"),
                               sheet.getImageName("mario_fire_upleft.png")]

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

    def wallCollisions(self, group, vx=0, vy=0, flySpeed=False):
        if not flySpeed:
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
        else:
            for wall in group:
                if pg.sprite.collide_rect(self, wall):
                    self.rect.x -= self.flySpeedX
                    self.rect.y -= self.flySpeedY
                    if self.flySpeedX != 0 or self.flySpeedY != 0:
                        self.game.cameraRect.cameraShake = 20
                        self.game.sansHitOnWallSound.play()
                    self.flySpeedX = 0
                    self.flySpeedY = 0

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
            self.airTimer = 0
            self.jumping = False
        jumpOffset = self.jumpTimer * jumpHeight
        self.imgRect.bottom = (self.rect.bottom - 5) - jumpOffset

    def hammer(self):
        self.canBeHit = True
        if self.alpha != 255:
            self.alpha = 255
        if self.isHammer is None:
            self.isHammer = Hammer(self.game, self)
        self.walking = False
        if self.currentFrame < len(self.hammerFramesLeft) - 1:
            pass
        else:
            self.currentFrame = 0
            self.hammering = False

    def fire(self):
        self.canBeHit = True
        if self.alpha != 255:
            self.alpha = 255
        if self.fireball is None:
            self.fireball = Fireball(self.game, self)
        self.walking = False

        self.fireCounter += 1

        if self.fireCounter >= fps / 2:
            self.fireCounter = 0
            self.firing = False

        if self.fireball not in self.game.entities:
            self.fireCounter = 0
            self.firing = False
            self.fireball = None

    def update(self):
        self.animate()

        if self.stats["hp"] < 0:
            self.stats["hp"] = 0
        if self.stats["hp"] == 0:
            self.KR = 0
            self.dead = True
            self.game.leader = "luigi"

        now = pg.time.get_ticks()
        keys = pg.key.get_pressed()
        self.vx, self.vy = 0, 0

        if self.game.leader == "mario":
            if not self.hammering:
                if not self.game.follower.hit and not self.game.follower.hammering and not self.firing and self.flySpeedY == 0 and self.flySpeedX == 0:
                    if not self.hit and self.canMove:
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
            if self.game.follower.dead:
                self.moveQueue.append(self.rect.x)
                self.moveQueue.append(self.rect.y)
                self.moveQueue.append(self.facing)
                if len(self.moveQueue) > 30:
                    self.moveQueue.popleft()
                    self.moveQueue.popleft()
                    self.moveQueue.popleft()
        elif self.game.leader == "luigi" and not self.dead:
            self.walking = self.game.follower.walking
            if not self.hit and not self.game.follower.hit and not self.game.follower.hammering and not self.hammering:
                if self.game.follower.walking or self.game.follower.vx != 0 or self.game.follower.vy != 0:
                    self.moveQueue.append(self.game.follower.rect.x)
                    self.moveQueue.append(self.game.follower.rect.y)
                    self.moveQueue.append(self.game.follower.facing)
                    if len(self.moveQueue) > 30:
                        self.rect.x = self.moveQueue.popleft()
                        self.rect.y = self.moveQueue.popleft()
                        self.facing = self.moveQueue.popleft()

        for event in self.game.event:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_m:
                    if self.abilities[self.ability] == "jump":
                        if not self.jumping and not self.hit and not self.dead and self.canMove:
                            self.jumping = True
                            self.jumpTimer = 1
                            self.airTimer = 0
                            self.game.jumpSound.play()
                    elif self.abilities[self.ability] == "hammer":
                        if not self.hammering and not self.hit and not self.dead and self.canMove:
                            self.hammering = True
                            self.currentFrame = 0
                    elif self.abilities[self.ability] == "fire":
                        if not self.firing and not self.hit and not self.dead and self.canMove:
                            self.firing = True
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

        if self.abilities[self.ability] == "fire":
            if self.game.leader == "luigi":
                self.ability = 0

        hits = pg.sprite.spritecollideany(self, self.game.npcs, pg.sprite.collide_rect_ratio(1.1))
        if hits and self.game.leader == "mario":
            if hits.canTalk:
                if hits.type == "talk":
                    if self.prevAbility == 12:
                        self.prevAbility = self.ability
                    self.ability = len(self.abilities) - 1
                elif hits.type == "interact":
                    if self.prevAbility == 12:
                        self.prevAbility = self.ability
                    self.ability = len(self.abilities) - 2
        else:
            if self.prevAbility != 12 or self.ability == len(self.abilities) - 2 or self.ability == len(self.abilities) - 1:
                if self.prevAbility != 12:
                    self.ability = self.prevAbility
                else:
                    self.ability = 0
                self.prevAbility = 12

        if self.hit:
            if self.hammering:
                self.hammering = False
            if self.firing:
                self.firing = False
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
        elif self.firing:
            self.fire()

        if self.game.follower.hammering:
            self.walking = False

        if self.KR > 0 and not self.dead:
            if self.KRTimer >= 15:
                self.KR -= 1
                self.stats["hp"] -= 1
                if self.stats["hp"] <= 0:
                    self.stats["hp"] = 1
                    self.KR = 0
                self.KRTimer = 0
            else:
                self.KRTimer += 1

        self.wallCollisions(self.game.walls, flySpeed=True)

        self.rect.x += self.flySpeedX
        self.rect.y += self.flySpeedY

        self.image = self.image.copy()

        if self.KR > 0:
            self.image.fill((91, 0, 155, 155), special_flags=pg.BLEND_RGB_MAX)

    def animate(self):
        now = pg.time.get_ticks()
        keys = pg.key.get_pressed()
        if self.canMove:
            if not self.dead and self.game.leader == "luigi":
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
                    if not self.hit and not self.game.follower.hit:
                        if self.walking or self.game.follower.vx != 0 or self.game.follower.vy != 0:
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
            elif not self.dead and self.game.leader == "mario":
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
                elif self.firing:
                    if self.facing == "up":
                        center = self.imgRect.center
                        self.image = self.fireFrames[0]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "down":
                        center = self.imgRect.center
                        self.image = self.fireFrames[1]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "left":
                        center = self.imgRect.center
                        self.image = self.fireFrames[2]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "right":
                        center = self.imgRect.center
                        self.image = self.fireFrames[3]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "downright":
                        center = self.imgRect.center
                        self.image = self.fireFrames[4]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "upright":
                        center = self.imgRect.center
                        self.image = self.fireFrames[5]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "downleft":
                        center = self.imgRect.center
                        self.image = self.fireFrames[6]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "upleft":
                        center = self.imgRect.center
                        self.image = self.fireFrames[7]
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
        elif self.dead:
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

        if self.flySpeedX != 0 or self.flySpeedY != 0:
            if self.flySpeedX < 0:
                center = self.imgRect.center
                self.image = self.throwFrames["left"]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
                self.facing = "right"
            elif self.flySpeedX > 0:
                center = self.imgRect.center
                self.image = self.throwFrames["right"]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
                self.facing = "left"
            elif self.flySpeedY > 0:
                center = self.imgRect.center
                self.image = self.throwFrames["down"]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
                self.facing = "up"
            elif self.flySpeedY < 0:
                center = self.imgRect.center
                self.image = self.throwFrames["up"]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
                self.facing = "down"

        if (self.walking or self.game.player.vx != 0 or self.game.player.vy != 0) and (
                self.currentFrame == 0 or self.currentFrame == 6) and now == self.lastUpdate:
            self.stepSound.stop()
            pg.mixer.Sound.play(self.stepSound)


class Luigi(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.stepSound = self.game.stoneSound
        self.moveQueue = Q.deque()
        self.hit = False
        self.dead = False
        self.canMove = True
        self.hammering = False
        self.isHammer = None
        self.flySpeedX = 0
        self.flySpeedY = 0
        self.hitTime = 0
        self.alpha = 255
        self.KR = 0
        self.KRTimer = 0
        self.ability = 0
        self.prevAbility = 12
        self.abilities = ["jump", "interact", "talk"]
        self.loadImages()
        self.facing = "right"
        self.lastUpdate = 0
        self.currentFrame = 1
        self.walking = False
        self.jumping = False
        self.canBeHit = True
        self.jumpTimer = 0
        self.airTimer = 0
        self.lightninging = False
        self.lightning = None
        self.lightningCounter = 0
        self.image = self.standingFrames[0]
        self.shadow = self.shadowFrames["normal"]
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)
        self.going = "irrelevent"
        self.area = self.game.area
        self.vx, self.vy = 0, 0
        if self.game.area == "Castle Bleck":
            self.shadow.fill(gray, special_flags=pg.BLEND_ADD)

        self.stats = {"level": 1, "maxHP": 23, "maxBP": 10, "pow": 6, "def": 8, "hp": 23, "bp": 10, "exp": 0}
        self.statGrowth = {"maxHP": randomNumber(9), "maxBP": randomNumber(7), "pow": randomNumber(3),
                           "def": randomNumber(5)}
        self.attackPieces = [["Cavi Cave", 0],
                             ["Guffawha Ruins", 0],
                             ["Somnom Ruins", 0],
                             ["Fawful's Castle", 0]]
        self.brosAttacks = [["Green Shell", "self.greenShell(enemies, song)",
                             pg.image.load("sprites/bros attacks/icons/greenShellIcon.png").convert_alpha(), 100, 4]]

    def hammer(self):
        self.canBeHit = True
        if self.alpha != 255:
            self.alpha = 255
        if self.isHammer == None:
            self.isHammer = Hammer(self.game, self)
        if self.currentFrame < len(self.hammerFramesLeft) - 1:
            pass
        else:
            self.currentFrame = 0
            self.hammering = False

    def lightningFire(self):
        self.canBeHit = True
        if self.alpha != 255:
            self.alpha = 255
        if self.lightning is None:
            self.lightning = Lightning(self.game, self)
        self.walking = False

        self.lightningCounter += 1

        if self.lightningCounter >= fps / 2:
            self.lightningCounter = 0
            self.lightninging = False

        if self.lightning not in self.game.entities:
            self.lightning = None
            self.lightninging = False
            self.lightningCounter = 0

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
            self.airTimer = 0
            self.jumping = False
        jumpOffset = self.jumpTimer * jumpHeight
        self.imgRect.bottom = (self.rect.bottom - 5) - jumpOffset

    def wallCollisions(self, group, vx=0, vy=0, flySpeed=False):
        if not flySpeed:
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
        else:
            for wall in group:
                if pg.sprite.collide_rect(self, wall):
                    self.rect.x -= self.flySpeedX
                    self.rect.y -= self.flySpeedY
                    if self.flySpeedX != 0 or self.flySpeedY != 0:
                        self.game.cameraRect.cameraShake = 20
                        self.game.sansHitOnWallSound.play()
                    self.flySpeedX = 0
                    self.flySpeedY = 0

    def update(self):
        if self.stats["hp"] < 0:
            self.stats["hp"] = 0
        if self.stats["hp"] == 0:
            self.KR = 0
            self.dead = True
            self.game.leader = "mario"
        self.animate()

        self.vx, self.vy = 0, 0

        now = pg.time.get_ticks()
        keys = pg.key.get_pressed()
        if self.game.leader == "mario" and not self.dead:
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
        elif self.game.leader == "luigi" and self.canMove and not self.hammering and not self.game.player.hammering and not self.lightninging and self.flySpeedY == 0 and self.flySpeedX == 0:
            if not self.hit and self.canMove:
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

            if self.game.player.dead:
                self.moveQueue.append(self.rect.x)
                self.moveQueue.append(self.rect.y)
                self.moveQueue.append(self.facing)
                if len(self.moveQueue) > 30:
                    self.moveQueue.popleft()
                    self.moveQueue.popleft()
                    self.moveQueue.popleft()

        if not self.hit and self.canMove and not self.dead:
            for event in self.game.event:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_l:
                        if self.abilities[self.ability] == "jump":
                            if not self.jumping and not self.hit and not self.dead and self.canMove:
                                self.jumping = True
                                self.jumpTimer = 1
                                self.airTimer = 0
                                self.game.jumpSound.play()
                        elif self.abilities[self.ability] == "hammer":
                            if not self.hammering and not self.hit and not self.dead and self.canMove:
                                self.hammering = True
                                self.currentFrame = 0
                        elif self.abilities[self.ability] == "thunder":
                            if not self.lightninging and not self.hit and not self.dead and self.canMove:
                                self.lightninging = True
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

        if self.abilities[self.ability] == "thunder":
            if self.game.leader == "mario":
                self.ability = 0

        hits = pg.sprite.spritecollideany(self, self.game.npcs, pg.sprite.collide_rect_ratio(1.1))
        if hits and self.game.leader == "luigi":
            if hits.canTalk:
                if hits.type == "talk":
                    if self.prevAbility == 12:
                        self.prevAbility = self.ability
                    self.ability = len(self.abilities) - 1
                elif hits.type == "interact":
                    if self.prevAbility == 12:
                        self.prevAbility = self.ability
                    self.ability = len(self.abilities) - 2
        else:
            if self.prevAbility != 12 or self.ability == len(self.abilities) - 2 or self.ability == len(self.abilities) - 1:
                if self.prevAbility != 12:
                    self.ability = self.prevAbility
                else:
                    self.ability = 0
                self.prevAbility = 12

        if not self.jumping:
            self.imgRect.bottom = self.rect.bottom - 5
            self.imgRect.centerx = self.rect.centerx
        else:
            self.jump()
            self.imgRect.centerx = self.rect.centerx

        if self.hammering:
            self.hammer()
        elif self.lightninging:
            self.lightningFire()

        if self.game.player.hammering:
            self.walking = False

        if self.KR > 0 and not self.dead:
            if self.KRTimer >= 15:
                self.KR -= 1
                self.stats["hp"] -= 1
                if self.stats["hp"] <= 0:
                    self.stats["hp"] = 1
                    self.KR = 0
                self.KRTimer = 0
            else:
                self.KRTimer += 1

        self.wallCollisions(self.game.walls, flySpeed=True)

        self.rect.x += self.flySpeedX
        self.rect.y += self.flySpeedY

        self.image = self.image.copy()

        if self.KR > 0:
            self.image.fill((91, 0, 155, 155), special_flags=pg.BLEND_RGB_MAX)

    def loadImages(self):
        sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")

        self.throwFrames = {"up": sheet.getImageName("luigi_sans_throw_up.png"),
                            "down": sheet.getImageName("luigi_sans_throw_down.png"),
                            "left": sheet.getImageName("luigi_sans_throw_left.png"),
                            "right": sheet.getImageName("luigi_sans_throw_right.png")}

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

        self.fireFrames = [sheet.getImageName("luigi_fire_up.png"),
                           sheet.getImageName("luigi_fire_down.png"),
                           sheet.getImageName("luigi_fire_left.png"),
                           sheet.getImageName("luigi_fire_right.png"),
                           sheet.getImageName("luigi_fire_downright.png"),
                           sheet.getImageName("luigi_fire_upright.png"),
                           sheet.getImageName("luigi_fire_downleft.png"),
                           sheet.getImageName("luigi_fire_upleft.png")]

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
        if self.canMove:
            if not self.dead and self.game.leader == "mario":
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
            elif not self.dead and self.game.leader == "luigi":
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
                elif self.lightninging:
                    if self.facing == "up":
                        center = self.imgRect.center
                        self.image = self.fireFrames[0]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "down":
                        center = self.imgRect.center
                        self.image = self.fireFrames[1]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "left":
                        center = self.imgRect.center
                        self.image = self.fireFrames[2]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "right":
                        center = self.imgRect.center
                        self.image = self.fireFrames[3]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "downright":
                        center = self.imgRect.center
                        self.image = self.fireFrames[4]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "upright":
                        center = self.imgRect.center
                        self.image = self.fireFrames[5]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "downleft":
                        center = self.imgRect.center
                        self.image = self.fireFrames[6]
                        self.imgRect = self.image.get_rect()
                        self.imgRect.center = center
                    if self.facing == "upleft":
                        center = self.imgRect.center
                        self.image = self.fireFrames[7]
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
        elif self.dead:
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

        if self.flySpeedX != 0 or self.flySpeedY != 0:
            if self.flySpeedX < 0:
                center = self.imgRect.center
                self.image = self.throwFrames["left"]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
                self.facing = "right"
            elif self.flySpeedX > 0:
                center = self.imgRect.center
                self.image = self.throwFrames["right"]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
                self.facing = "left"
            elif self.flySpeedY > 0:
                center = self.imgRect.center
                self.image = self.throwFrames["down"]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
                self.facing = "up"
            elif self.flySpeedY < 0:
                center = self.imgRect.center
                self.image = self.throwFrames["up"]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
                self.facing = "down"

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
            self.points.append(pt.getPointOnLine(self.rect.centerx, self.rect.centery, 200,
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
            elif self.image == self.spinningFrames[-1] and self.game.coinCollection.exp == 0:
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
            if self.newXP < self.game.battleXp - self.numSpeed or self.game.coinCollection.exp != 0:
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
            self.points.append(pt.getPointOnLine(self.rect.centerx, self.rect.centery, 200,
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
            elif self.image == self.spinningFrames[-1] and self.game.coinCollection.exp == 0:
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
            if self.newXP < self.game.battleXp - self.numSpeed or self.game.coinCollection.exp != 0:
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
    def __init__(self, game, pos, contents=None):
        pg.sprite.Sprite.__init__(self, game.blocks)
        if contents is None:
            contents = ["Coin(self.game, self)"]
        self.game = game
        self.game.sprites.append(self)
        self.ID = -17
        self.newID = False
        self.hit = False
        self.bopped = False
        self.empty = False
        self.contents = contents
        self.alpha = 255
        self.vy = 0
        self.dy = 0.065
        self.loadImages()
        self.rect = self.shadow.get_rect()
        if self.game.area == "Castle Bleck":
            self.shadow.fill(gray, special_flags=pg.BLEND_ADD)
        self.rect.center = pos
        self.image = self.blockSprite
        self.imgRect = self.image.get_rect()
        self.imgRect.centerx = self.rect.centerx
        self.imgRect.centery = self.rect.centery - 200
        self.contents = [content for content in self.contents if content != ""]
        if len(self.contents) == 0:
            self.contents = ["Coin(self.game, self)"]

    def loadImages(self):
        sheet = spritesheet("sprites/blocks.png", "sprites/blocks.xml")

        self.shadow = sheet.getImageName("shadow.png")

        self.blockSprite = sheet.getImageName("block.png")

        self.hitSprite = sheet.getImageName("empty block.png")

    def update(self):
        if not self.newID:
            if self.ID in self.game.hitBlockList:
                self.hit = True
                self.bopped = True
                self.contents = []
            self.newID = True

        if self.hit and self.bopped:
            if self.imgRect.centery < self.rect.centery - 190:
                self.imgRect.centery += 5
            elif len(self.contents) != 0:
                self.hit = False
                self.bopped = False
            else:
                self.image = self.hitSprite
        elif self.hit and not self.bopped:
            if self.imgRect.centery > self.rect.centery - 215:
                self.imgRect.centery -= 5
            else:
                self.bopped = True
        else:
            self.imgRect.y += round(self.vy)

        self.vy += self.dy
        if self.vy > 1 or self.vy < -1:
            self.dy *= -1

        hits = pg.sprite.collide_rect(self, self.game.player)
        if hits:
            rect = self.rect
            self.rect = self.imgRect
            hitsRound2 = pg.sprite.collide_rect(self, self.game.playerCol)
            self.rect = rect
            if hitsRound2 and self.game.player.going == "up":
                if len(self.contents) != 0 and not self.hit:
                    eval(self.contents[0])
                    self.contents.pop(0)
                self.game.player.airTimer = airTime
                self.hit = True
                self.game.blockHitSound.play()
                if self.ID not in self.game.hitBlockList:
                    self.game.hitBlockList.append(self.ID)

        hits = pg.sprite.collide_rect(self, self.game.follower)
        if hits:
            rect = self.rect
            self.rect = self.imgRect
            hitsRound2 = pg.sprite.collide_rect(self, self.game.followerCol)
            self.rect = rect
            if hitsRound2 and self.game.follower.going == "up":
                if len(self.contents) != 0 and not self.hit:
                    eval(self.contents[0])
                    self.contents.pop(0)
                self.game.follower.airTimer = airTime
                self.hit = True
                self.game.blockHitSound.play()
                if self.ID not in self.game.hitBlockList:
                    self.game.hitBlockList.append(self.ID)


class SaveBlock(pg.sprite.Sprite):
    def __init__(self, game, pos):
        pg.sprite.Sprite.__init__(self, game.blocks)
        self.game = game
        self.game.sprites.append(self)
        self.ID = -17
        self.newID = False
        self.hit = False
        self.bopped = False
        self.empty = False
        self.alpha = 255
        self.vy = 0
        self.dy = 0.065
        self.loadImages()
        self.rect = self.shadow.get_rect()
        if self.game.area == "Castle Bleck":
            self.shadow.fill(gray, special_flags=pg.BLEND_ADD)
        self.rect.center = pos
        self.image = self.blockSprite
        self.imgRect = self.image.get_rect()
        self.imgRect.centerx = self.rect.centerx
        self.imgRect.centery = self.rect.centery - 200
        self.up = True

    def loadImages(self):
        sheet = spritesheet("sprites/blocks.png", "sprites/blocks.xml")

        self.shadow = sheet.getImageName("shadow.png")

        self.blockSprite = sheet.getImageName("save block.png")

        self.hitSprite = sheet.getImageName("save block_hit.png")

    def update(self):
        if self.hit:
            if self.up:
                if self.imgRect.centery > self.rect.centery - 215:
                    self.imgRect.centery -= 5
                    bottom = self.imgRect.bottom
                    self.image = self.hitSprite
                    self.imgRect.bottom = bottom
                else:
                    self.up = False
            else:
                if self.imgRect.centery < self.rect.centery - 185:
                    self.imgRect.centery += 5
                    bottom = self.imgRect.bottom
                    self.image = self.blockSprite
                    self.imgRect.bottom = bottom
                else:
                    self.hit = False
                    self.dy = abs(self.dy)
                    self.vy = -0.99
                    self.game.save = True
        else:
            self.imgRect.y += round(self.vy)

        self.vy += self.dy
        if self.vy > 1 or self.vy < -1:
            self.dy *= -1

        hits = pg.sprite.collide_rect(self, self.game.player)
        if hits:
            rect = self.rect
            self.rect = self.imgRect
            hitsRound2 = pg.sprite.collide_rect(self, self.game.playerCol)
            self.rect = rect
            if hitsRound2 and self.game.player.going == "up":
                self.game.player.airTimer = airTime
                self.up = True
                self.hit = True
                self.game.blockHitSound.play()

        hits = pg.sprite.collide_rect(self, self.game.follower)
        if hits:
            rect = self.rect
            self.rect = self.imgRect
            hitsRound2 = pg.sprite.collide_rect(self, self.game.followerCol)
            self.rect = rect
            if hitsRound2 and self.game.follower.going == "up":
                self.game.follower.airTimer = airTime
                self.up = True
                self.hit = True
                self.game.blockHitSound.play()


class UndertaleSaveBlock(pg.sprite.Sprite):
    def __init__(self, game, pos):
        pg.sprite.Sprite.__init__(self, game.npcs, game.blocks)
        self.game = game
        self.game.sprites.append(self)
        self.ID = -17
        self.newID = False
        self.alpha = 255
        self.vy = 0
        self.dy = 0.065
        self.type = "interact"
        self.loadImages()
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.shadow = self.image
        self.imgRect = self.rect
        self.currentFrame = 0
        self.lastUpdate = 0
        self.textbox = None
        self.canTalk = True
        self.dead = False
        self.text = ["* (The fact that this place\n\a seems like its from\n\a somewhere else...)",
                     "* (It fills you with\n\a DETERMINATION.)"]

    def loadImages(self):
        sheet = spritesheet("sprites/blocks.png", "sprites/blocks.xml")

        self.images = [sheet.getImageName("undertale_save_1.png"),
                        sheet.getImageName("undertale_save_2.png")]

    def update(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 200:
            self.lastUpdate = now
            if self.currentFrame < len(self.images):
                self.currentFrame = (self.currentFrame + 1) % (len(self.images))
            else:
                self.currentFrame = 0
            center = self.imgRect.center
            self.image = self.images[self.currentFrame]
            self.imgRect = self.image.get_rect()
            self.imgRect.center = center

            self.shadow = self.images[1]
            center = self.rect.center
            self.rect = self.shadow.get_rect()
            self.rect.center = center
            if self.currentFrame == 1:
                self.shadow.set_alpha(255)
            else:
                self.shadow.set_alpha(0)

        if self.textbox is None:
            keys = pg.key.get_pressed()
            if self.game.leader == "mario":
                if pg.sprite.collide_rect_ratio(1.1)(self, self.game.player) and keys[pg.K_m]:
                    if not self.game.player.jumping:
                        pg.mixer.music.fadeout(200)
                        self.game.playsong = False
                        self.game.firstLoop = True
                        self.textbox = UndertaleTextBox(self.game, self, self.text)
                        self.game.currentPoint += pg.mixer.music.get_pos()
            elif self.game.leader == "luigi":
                if pg.sprite.collide_rect_ratio(1.1)(self, self.game.follower) and keys[pg.K_l]:
                    if not self.game.follower.jumping:
                        pg.mixer.music.fadeout(200)
                        self.game.playsong = False
                        self.game.firstLoop = True
                        self.textbox = UndertaleTextBox(self.game, self, self.text)
                        self.game.currentPoint += pg.mixer.music.get_pos()
        elif self.textbox == "complete":
            self.textbox = None
            self.game.save = True


class MarioBlock(pg.sprite.Sprite):
    def __init__(self, game, pos, contents=None):
        pg.sprite.Sprite.__init__(self, game.blocks)
        if contents is None:
            contents = ["Coin(self.game, self)"]
        self.game = game
        self.game.sprites.append(self)
        self.ID = -17
        self.newID = False
        self.hit = False
        self.bopped = False
        self.empty = False
        self.contents = contents
        self.alpha = 255
        self.vy = 0
        self.dy = 0.065
        self.loadImages()
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.image = self.blockSprite
        self.imgRect = self.image.get_rect()
        if self.game.area == "Castle Bleck":
            self.shadow.fill(gray, special_flags=pg.BLEND_ADD)
        self.imgRect.centerx = self.rect.centerx
        self.imgRect.centery = self.rect.centery - 200
        self.contents = [content for content in self.contents if content != ""]
        if len(self.contents) == 0:
            self.contents = ["Coin(self.game, self)"]

    def loadImages(self):
        sheet = spritesheet("sprites/blocks.png", "sprites/blocks.xml")

        self.shadow = sheet.getImageName("shadow.png")

        self.blockSprite = sheet.getImageName("mario block.png")

        self.hitSprite = sheet.getImageName("empty block.png")

    def update(self):
        if not self.newID:
            if self.ID in self.game.hitBlockList:
                self.hit = True
                self.bopped = True
                self.contents = []
            self.newID = True

        if self.hit and self.bopped:
            if self.imgRect.centery < self.rect.centery - 190:
                self.imgRect.centery += 5
            elif len(self.contents) != 0:
                self.hit = False
                self.bopped = False
            else:
                self.image = self.hitSprite
        elif self.hit and not self.bopped:
            if self.imgRect.centery > self.rect.centery - 215:
                self.imgRect.centery -= 5
            else:
                self.bopped = True
        else:
            self.imgRect.y += round(self.vy)

        self.vy += self.dy
        if self.vy > 1 or self.vy < -1:
            self.dy *= -1

        hits = pg.sprite.collide_rect(self, self.game.player)
        if hits:
            rect = self.rect
            self.rect = self.imgRect
            hitsRound2 = pg.sprite.collide_rect(self, self.game.playerCol)
            self.rect = rect
            if hitsRound2 and self.game.player.going == "up":
                if len(self.contents) != 0 and not self.hit:
                    eval(self.contents[0])
                    self.contents.pop(0)
                self.game.player.airTimer = airTime
                self.hit = True
                self.game.blockHitSound.play()
                self.game.hitBlockList.append(self.ID)

        hits = pg.sprite.collide_rect(self, self.game.follower)
        if hits:
            rect = self.rect
            self.rect = self.imgRect
            hitsRound2 = pg.sprite.collide_rect(self, self.game.followerCol)
            self.rect = rect
            if hitsRound2 and self.game.follower.going == "up":
                self.game.follower.airTimer = airTime
                self.hit = True
                self.game.blockHitSound.play()


class LuigiBlock(pg.sprite.Sprite):
    def __init__(self, game, pos, contents=None):
        pg.sprite.Sprite.__init__(self, game.blocks)
        if contents is None:
            contents = ["Coin(self.game, self)"]
        self.game = game
        self.game.sprites.append(self)
        self.ID = -17
        self.newID = False
        self.hit = False
        self.bopped = False
        self.empty = False
        self.contents = contents
        self.alpha = 255
        self.vy = 0
        self.dy = 0.065
        self.loadImages()
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.image = self.blockSprite
        self.imgRect = self.image.get_rect()
        if self.game.area == "Castle Bleck":
            self.shadow.fill(gray, special_flags=pg.BLEND_ADD)
        self.imgRect.centerx = self.rect.centerx
        self.imgRect.centery = self.rect.centery - 200
        self.contents = [content for content in self.contents if content != ""]
        if len(self.contents) == 0:
            self.contents = ["Coin(self.game, self)"]

    def loadImages(self):
        sheet = spritesheet("sprites/blocks.png", "sprites/blocks.xml")

        self.shadow = sheet.getImageName("shadow.png")

        self.blockSprite = sheet.getImageName("luigi block.png")

        self.hitSprite = sheet.getImageName("empty block.png")

    def update(self):
        if not self.newID:
            if self.ID in self.game.hitBlockList:
                self.hit = True
                self.bopped = True
                self.contents = []
            self.newID = True

        if self.hit and self.bopped:
            if self.imgRect.centery < self.rect.centery - 190:
                self.imgRect.centery += 5
            elif len(self.contents) != 0:
                self.hit = False
                self.bopped = False
            else:
                self.image = self.hitSprite
        elif self.hit and not self.bopped:
            if self.imgRect.centery > self.rect.centery - 215:
                self.imgRect.centery -= 5
            else:
                self.bopped = True
        else:
            self.imgRect.y += round(self.vy)

        self.vy += self.dy
        if self.vy > 1 or self.vy < -1:
            self.dy *= -1

        hits = pg.sprite.collide_rect(self, self.game.player)
        if hits:
            rect = self.rect
            self.rect = self.imgRect
            hitsRound2 = pg.sprite.collide_rect(self, self.game.playerCol)
            self.rect = rect
            if hitsRound2 and self.game.player.going == "up":
                self.game.player.airTimer = airTime
                self.hit = True
                self.game.blockHitSound.play()

        hits = pg.sprite.collide_rect(self, self.game.follower)
        if hits:
            rect = self.rect
            self.rect = self.imgRect
            hitsRound2 = pg.sprite.collide_rect(self, self.game.followerCol)
            self.rect = rect
            if hitsRound2 and self.game.follower.going == "up":
                if len(self.contents) != 0 and not self.hit:
                    eval(self.contents[0])
                    self.contents.pop(0)
                self.game.follower.airTimer = airTime
                self.hit = True
                self.game.blockHitSound.play()
                self.game.hitBlockList.append(self.ID)


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
    def __init__(self, game, parent, text, type="dialogue", dir=None, choice=False, sound="default", complete=False):
        pg.sprite.Sprite.__init__(self, game.ui, game.textboxes)
        self.speed = 20
        self.game = game
        self.choice = choice
        self.choosing = False
        self.talking = False
        self.game.player.hammering = False
        self.game.follower.hammering = False
        self.game.player.canMove = False
        self.game.follower.canMove = False
        self.parent = parent
        self.parent.textbox = self
        self.offset = False
        self.closing = False
        self.advancing = False
        self.big = False
        self.sound = sound
        self.type = type
        self.text = text.copy()
        for i in range(len(self.text)):
            self.text[i] = self.text[i].replace("/n", "\n")
            self.text[i] = self.text[i] + "\n\a"
        self.page = 0
        self.playSound = 10
        if complete:
            self.counter = self.speed - 1
            self.alpha = 255
            self.scale = 1
            self.currentCharacter = len(self.text[0])
        else:
            self.game.textBoxOpenSound.play()
            self.alpha = 0
            self.scale = 0
            self.currentCharacter = 1
            self.counter = 0
        self.points = []
        self.pause = 0
        self.angle = 0
        self.deathTimer = int(fps / 5)
        self.angleDir = True
        self.complete = False
        self.startAdvance = False
        self.advance = talkAdvanceSprite
        self.advanceRect = self.advance.get_rect()
        self.image = textboxSprites[type]
        self.rect = self.image.get_rect()
        self.maxRect = self.image.get_rect()
        self.rect.center = self.game.camera.offset(parent.imgRect).center
        self.advanceRect.center = (
            self.rect.right - self.advanceRect.width - 20, self.rect.bottom - self.advanceRect.width - 20)
        self.image = pg.transform.scale(textboxSprites[self.type],
                                        (int(self.maxRect.width * self.scale), int(self.maxRect.height * self.scale)))
        if self.type == "dialogue":
            self.textx = self.rect.left + 70
            self.texty = self.rect.top + 40
        if self.type == "board":
            self.textx = self.rect.left + 100
            self.texty = self.rect.top + 100
        if dir is None:
            if self.rect.centery >= height / 2:
                for i in range(self.speed + 1):
                    self.points.append(
                        pt.getPointOnLine(self.rect.centerx, self.rect.centery, width / 2, (self.rect.height / 2) + 20,
                                          (i / self.speed)))
            else:
                for i in range(self.speed + 1):
                    self.points.append(pt.getPointOnLine(self.rect.centerx, self.rect.centery, width / 2,
                                                         height - (self.rect.height / 2) - 20, (i / self.speed)))
        elif dir == "up":
            for i in range(self.speed + 1):
                self.points.append(
                    pt.getPointOnLine(self.rect.centerx, self.rect.centery, width / 2, (self.rect.height / 2) + 20,
                                      (i / self.speed)))
        elif dir == "down":
            for i in range(self.speed + 1):
                self.points.append(pt.getPointOnLine(self.rect.centerx, self.rect.centery, width / 2,
                                                     height - (self.rect.height / 2) - 20, (i / self.speed)))
        elif dir == "None":
            for i in range(self.speed + 1):
                self.points.append(pt.getPointOnLine(self.rect.centerx, self.rect.centery, width / 2,
                                                     height / 2, (i / self.speed)))

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
            elif self.deathTimer > 0:
                self.deathTimer -= 1
            else:
                self.game.player.canMove = True
                self.game.follower.canMove = True
                self.parent.textbox = "complete"
                self.complete = True
                self.kill()

        if not self.advancing:
            if self.type == "dialogue":
                self.textx = self.rect.left + 70
                self.texty = self.rect.top + 40
            if self.type == "board":
                self.textx = self.rect.left + 100
                self.texty = self.rect.top + 100
        else:
            self.texty -= 10
            if self.texty <= self.rect.top - 220:
                self.page += 1
                self.currentCharacter = 1
                self.advancing = False

        if self.text[self.page][0:2] == "/C" and self.choice and self.currentCharacter >= len(self.text[self.page]) - 1:
            self.choosing = True
        else:
            self.choosing = False

        if self.text[self.page][0:2] == "/B":
            self.big = True
        else:
            self.big = False

        if self.text[self.page][-4:-2] == "/S" and self.currentCharacter >= len(
                self.text[self.page]) - 4 and not self.pause:
            self.closing = True

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
        if self.type == "dialogue":
            self.advanceRect.right = self.rect.right - 50
            self.advanceRect.bottom = self.rect.bottom - 55
        elif self.type == "board":
            self.advanceRect.right = self.rect.right - 80
            self.advanceRect.bottom = self.rect.bottom - 100

    def draw(self):
        self.startAdvance = False
        keys = pg.key.get_pressed()
        character = self.text[self.page]

        if character[self.currentCharacter - 1] == "\n":
            self.currentCharacter += 1
        if character[self.currentCharacter - 1:self.currentCharacter + 1] == "<<":
            self.currentCharacter += 3
        if character[self.currentCharacter - 1:self.currentCharacter + 1] == ">>":
            self.currentCharacter += 2
        if character[self.currentCharacter - 1: self.currentCharacter + 1] == "/C":
            self.currentCharacter += 3
        if character[self.currentCharacter - 1: self.currentCharacter + 1] == "/B":
            self.currentCharacter += 3

        character = character[:self.currentCharacter]

        if self.currentCharacter < len(self.text[self.page]):
            if self.text[self.page][self.currentCharacter] == "/":
                if self.text[self.page][self.currentCharacter + 1] == "p":
                    self.pause = fps / 2
                if self.text[self.page][self.currentCharacter + 1] == "P":
                    self.pause = 60
                try:
                    if int(self.text[self.page][self.currentCharacter + 1]) % 1 == 0:
                        self.pause = int(self.text[self.page][self.currentCharacter + 1])
                except:
                    pass
                self.currentCharacter += 2

        character = character.replace("/p", "")
        character = character.replace("/P", "")
        character = character.replace("/1", "")
        character = character.replace("/2", "")
        character = character.replace("/3", "")
        character = character.replace("/4", "")
        character = character.replace("/5", "")
        character = character.replace("/6", "")
        character = character.replace("/7", "")
        character = character.replace("/8", "")
        character = character.replace("/9", "")

        completeText = False
        self.game.blit_alpha(self.game.screen, self.image, self.rect, self.alpha)
        if self.scale >= 1 and self.alpha >= 255:
            if not self.big:
                if self.type == "dialogue":
                    self.game.screen.set_clip((self.rect.left, self.rect.top + 30, 1000, 160))
                    ptext.draw(character, (self.textx, self.texty), lineheight=0.8, surf=self.game.screen,
                               fontname=dialogueFont, fontsize=35, color=black, background=(228, 229, 228))
                elif self.type == "board":
                    self.game.screen.set_clip((self.rect.left, self.rect.top + 61, 1000, 220))
                    ptext.draw(character, (self.textx, self.texty), lineheight=0.8, surf=self.game.screen,
                               fontname=dialogueFont, fontsize=35, color=black, background=(225, 223, 225))
            else:
                if self.type == "dialogue":
                    self.game.screen.set_clip((self.rect.left, self.rect.top + 30, 1000, 160))
                    ptext.draw(character, (self.rect.centerx - 2, self.texty + 20), lineheight=0.8,
                               surf=self.game.screen,
                               fontname=dialogueFont, fontsize=90, color=black, background=(228, 229, 228),
                               anchor=(0.5, 0))
                elif self.type == "board":
                    self.game.screen.set_clip((self.rect.left, self.rect.top + 61, 1000, 220))
                    ptext.draw(character, (self.rect.centerx - 2, self.texty + 20), lineheight=0.8,
                               surf=self.game.screen,
                               fontname=dialogueFont, fontsize=90, color=black, background=(225, 223, 225),
                               anchor=(0.5, 0))
            self.game.screen.set_clip(0, 0, width, height)
            if self.currentCharacter < len(self.text[self.page]) and not self.advancing:
                for event in self.game.event:
                    if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                        pg.quit()
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                            completeText = True
                            self.pause = 0
                if completeText:
                    self.currentCharacter = len(self.text[self.page])
            else:
                for event in self.game.event:
                    if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                        pg.quit()
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                            if self.page < len(self.text) - 1:
                                if not self.advancing: self.game.talkAdvanceSound.play()
                                self.advancing = True
                            else:
                                self.points = []
                                for i in range(self.speed + 1):
                                    self.points.append(
                                        pt.getPointOnLine(self.rect.centerx, self.rect.centery,
                                                          self.game.camera.offset(self.parent.imgRect).centerx,
                                                          self.game.camera.offset(self.parent.imgRect).centery,
                                                          (i / self.speed)))
                                self.counter = 0
                                self.game.textBoxCloseSound.stop()
                                self.game.textBoxCloseSound.play()
                                self.closing = True
            if self.pause <= 0:
                if self.currentCharacter < len(self.text[self.page]) and not completeText:
                    pitch = random.randrange(0, 3)
                    if self.playSound >= 1 and character[-1] != " " and self.sound == "default":
                        if pitch == 0:
                            self.game.talkSoundLow.play()
                        elif pitch == 1:
                            self.game.talkSoundMed.play()
                        elif pitch == 2:
                            self.game.talkSoundHigh.play()
                        self.playSound = 0
                    elif self.playSound >= 2 and character[-1] != " " and self.sound == "starlow":
                        if pitch == 0:
                            self.game.starlowTalkSoundLow.play()
                        elif pitch == 1:
                            self.game.starlowTalkSoundMed.play()
                        elif pitch == 2:
                            self.game.starlowTalkSoundHigh.play()
                        self.playSound = 0
                    elif self.playSound >= 3 and character[-1] != " " and self.sound == "fawful":
                        if pitch == 0:
                            self.game.fawfulTalkSoundLow.play()
                        elif pitch == 1:
                            self.game.fawfulTalkSoundMed.play()
                        elif pitch == 2:
                            self.game.fawfulTalkSoundHigh.play()
                        self.playSound = 0
                    else:
                        self.playSound += 1
                    self.currentCharacter += 1
                    self.talking = True

                    if self.currentCharacter >= len(self.text[self.page]) - 1:
                        self.startAdvance = True
                else:
                    self.talking = False
                    if not self.advancing:
                        self.playSound = 10
                        if not self.choosing:
                            self.game.screen.blit(self.advance, self.advanceRect.center)
            else:
                self.playSound = 10
                self.pause -= 1


class UndertaleTextBox(pg.sprite.Sprite):
    def __init__(self, game, parent, text, type="dialogue", head=None, sound="default", complete=False, font="default", speed=1):
        pg.sprite.Sprite.__init__(self, game.ui, game.textboxes)
        self.speed = speed
        self.game = game
        self.font = font
        self.head = head
        self.choosing = False
        self.talking = False
        self.game.player.hammering = False
        self.game.follower.hammering = False
        self.game.player.canMove = False
        self.game.follower.canMove = False
        self.parent = parent
        self.parent.textbox = self
        self.offset = False
        self.closing = False
        self.advancing = False
        self.big = False
        self.sound = sound
        self.type = type
        self.text = text.copy()
        if font == "default":
            self.font = undertaleFont
            self.fontsize = 37
            self.fontSpace = 1.2
        elif font == "sans":
            self.font = sansFont
            self.fontsize = 50
            self.fontSpace = 1
        for i in range(len(self.text)):
            self.text[i] = self.text[i].replace("/n", "\n")
            self.text[i] = self.text[i] + "\n\a"
        self.page = 0
        self.playSound = 10
        if complete:
            self.counter = self.speed - 1
            self.alpha = 255
            self.scale = 1
            self.currentCharacter = len(self.text[0])
        else:
            self.alpha = 0
            self.scale = 1
            self.currentCharacter = 1
        self.pause = 0
        self.deathTimer = int(0)
        self.angleDir = True
        self.complete = False
        self.image = textboxSprites["undertale"]
        self.rect = self.image.get_rect()
        self.rect.center = self.game.camera.offset(parent.imgRect).center
        if self.rect.centery >= height / 2:
            self.rect.center = (width / 2, (self.rect.height / 2) + 20)
        else:
            self.rect.center = (width / 2, height - (self.rect.height / 2) - 20)
        if self.type == "dialogue":
            self.textx = self.rect.left + 40
            self.texty = self.rect.top + 30
        if self.head == "sans":
            self.headSprites = [pg.image.load("sprites/sans heads/normal.png"),
                                pg.image.load("sprites/sans heads/look left.png"),
                                pg.image.load("sprites/sans heads/look left smile.png"),
                                pg.image.load("sprites/sans heads/wink.png"),
                                pg.image.load("sprites/sans heads/eyes half closed.png"),
                                pg.image.load("sprites/sans heads/eyes closed.png"),
                                pg.image.load("sprites/sans heads/no eyes.png")]

            self.headRect = self.headSprites[0].get_rect()
            self.headRect.left = self.rect.left + 40
            self.headRect.centery = self.rect.centery

        self.currentHead = 0

    def update(self):
        if self.alpha == 0:
            self.alpha = 255
        if not self.advancing:
            if self.head is None:
                self.textx = self.rect.left + 30
                self.texty = self.rect.top + 30
            else:
                self.textx = self.rect.left + 176
                self.texty = self.rect.top + 30
        else:
            self.page += 1
            self.currentCharacter = 1
            self.advancing = False

        if self.text[self.page][0:2] == "/B":
            self.big = True
        else:
            self.big = False

        if self.text[self.page][-4:-2] == "/S" and self.currentCharacter >= len(
                self.text[self.page]) - 4 and not self.pause:
            self.game.player.canMove = True
            self.game.follower.canMove = True
            self.parent.textbox = "complete"
            self.complete = True
            self.kill()

    def draw(self):
        self.startAdvance = False
        keys = pg.key.get_pressed()
        character = self.text[self.page]

        if character[self.currentCharacter - 1] == "\n":
            self.currentCharacter += 1
        if character[self.currentCharacter - 1:self.currentCharacter + 1] == "<<":
            self.currentCharacter += 3
        if character[self.currentCharacter - 1:self.currentCharacter + 1] == ">>":
            self.currentCharacter += 2
        if character[self.currentCharacter - 1: self.currentCharacter + 1] == "/C":
            self.currentCharacter += 3
        if character[self.currentCharacter - 1: self.currentCharacter + 1] == "/B":
            self.currentCharacter += 3

        character = character[:self.currentCharacter]

        if self.currentCharacter < len(self.text[self.page]):
            if self.text[self.page][self.currentCharacter] == "/":
                if self.text[self.page][self.currentCharacter + 1] == "p":
                    self.pause = fps / 2
                if self.text[self.page][self.currentCharacter + 1] == "P":
                    self.pause = 60
                try:
                    if int(self.text[self.page][self.currentCharacter + 1]) % 1 == 0:
                        self.currentHead = int(self.text[self.page][self.currentCharacter + 1])
                except:
                    pass
                self.currentCharacter += 2

        character = character.replace("/p", "")
        character = character.replace("/P", "")
        character = character.replace("/0", "")
        character = character.replace("/1", "")
        character = character.replace("/2", "")
        character = character.replace("/3", "")
        character = character.replace("/4", "")
        character = character.replace("/5", "")
        character = character.replace("/6", "")
        character = character.replace("/7", "")
        character = character.replace("/8", "")
        character = character.replace("/9", "")

        completeText = False
        self.game.blit_alpha(self.game.screen, self.image, self.rect, self.alpha)
        if self.scale >= 1 and self.alpha >= 255:
            if not self.big:
                self.game.screen.set_clip((self.rect.left, self.rect.top + 30, 1000, 160))
                ptext.draw(character, (self.textx, self.texty), surf=self.game.screen,
                           fontname=self.font, fontsize=self.fontsize, color=white, lineheight=self.fontSpace, background=(0, 0, 0), antialias=False)
            else:
                self.game.screen.set_clip((self.rect.left, self.rect.top + 30, 1000, 160))
                ptext.draw(character, (self.rect.centerx - 2, self.texty + 20), lineheight=self.fontSpace,
                           surf=self.game.screen,
                           fontname=self.font, fontsize=90, color=white, background=(0, 0, 0),
                           anchor=(0.5, 0), antialias=False)
            self.game.screen.set_clip(0, 0, width, height)
            if self.currentCharacter < len(self.text[self.page]) and not self.advancing:
                for event in self.game.event:
                    if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                        pg.quit()
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                            completeText = True
                            self.pause = 0
                if completeText:
                    self.currentCharacter = len(self.text[self.page])
            else:
                for event in self.game.event:
                    if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                        pg.quit()
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                            if self.page < len(self.text) - 1:
                                self.advancing = True
                            else:
                                self.counter = 0
                                self.game.player.canMove = True
                                self.game.follower.canMove = True
                                self.parent.textbox = "complete"
                                self.complete = True
                                self.kill()
            if self.pause <= 0:
                if self.currentCharacter < len(self.text[self.page]) and not completeText:
                    if character[-1] != " " and self.sound == "default":
                        self.game.undertaleTalkSound.play()
                        self.playSound = 0
                    if self.playSound >= 1 and self.sound == "sans":
                        self.game.sansTalkSound.play()
                        self.playSound = 0
                    else:
                        self.playSound += 1
                    self.currentCharacter += 1
                    self.pause = self.speed
                    self.talking = True

                    if self.currentCharacter >= len(self.text[self.page]) - 1:
                        self.startAdvance = True
                else:
                    self.talking = False
                    if not self.advancing:
                        self.playSound = 10
            else:
                if self.pause > 1:
                    self.playSound = 10
                self.pause -= 1
        if self.head is not None:
            self.game.blit_alpha(self.game.screen, self.headSprites[self.currentHead], self.headRect, self.alpha)


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
        self.currentCharacter = 1
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
        if character[self.currentCharacter - 1] == "\n":
            self.currentCharacter += 1
        character = character[:self.currentCharacter]
        self.game.blit_alpha(self.game.screen, self.image, self.game.camera.offset(self.rect), self.alpha)
        if self.scale >= 0.3:
            textx = self.game.camera.offset(self.rect).left + 10
            texty = self.game.camera.offset(self.rect).top + 10
            ptext.draw(character, (textx, texty), fontname=dialogueFont, fontsize=20,
                       lineheight=0.8, surf=self.game.screen)
            if self.currentCharacter < len(self.text[self.page]):
                self.currentCharacter += 2
                if self.currentCharacter > len(self.text[self.page]):
                    self.currentCharacter = len(self.text[self.page])


class RoomTransition:
    def __init__(self, game, initialRoom, room, size, pos, playerPos, width=None, height=None):
        self.game = game
        self.game.transistors.append(self)
        self.initialRoom = initialRoom
        self.room = room
        if width is None:
            self.rect = pg.rect.Rect(0, 0, size, size)
            self.rect.center = pos
        else:
            self.rect = pg.rect.Rect(pos[0], pos[1], width, height)
        self.playerPos = playerPos
        self.fadeout = None

    def update(self):
        if self.game.leader == "mario":
            if self.rect.colliderect(self.game.player.rect):
                if self.fadeout == None:
                    self.game.player.canMove = False
                    self.game.follower.canMove = False
                    self.game.player.walking = False
                    self.game.follower.walking = False
                    self.fadeout = Fadeout(self.game, 10)
        if self.game.leader == "luigi":
            if self.rect.colliderect(self.game.follower.rect):
                if self.fadeout == None:
                    self.game.player.canMove = False
                    self.game.follower.canMove = False
                    self.game.player.walking = False
                    self.game.follower.walking = False
                    self.fadeout = Fadeout(self.game, 10)

        if self.fadeout is not None:
            if self.fadeout.alpha >= 255:
                self.game.storeData["mario facing"] = self.game.player.facing
                self.game.storeData["luigi facing"] = self.game.follower.facing
                self.game.storeData["mario pos"] = self.playerPos
                self.game.storeData["luigi pos"] = self.playerPos
                self.game.storeData["mario stats"] = self.game.player.stats
                self.game.storeData["luigi stats"] = self.game.follower.stats
                self.game.storeData["mario abilities"] = self.game.player.abilities
                self.game.storeData["luigi abilities"] = self.game.follower.abilities
                self.game.storeData["mario current ability"] = self.game.player.ability
                self.game.storeData["luigi current ability"] = self.game.follower.ability
                self.game.storeData["mario attack pieces"] = self.game.player.attackPieces
                self.game.storeData["luigi attack pieces"] = self.game.follower.attackPieces
                self.game.storeData["move"] = Q.deque()
                self.game.player.canMove = True
                self.game.follower.canMove = True
                for sprite in self.game.sprites:
                    try:
                        sprite.loadImages()
                    except:
                        pass
                eval(self.room)

        if self.initialRoom != self.game.room:
            self.game.transistors.remove(self)


class Decoration(pg.sprite.Sprite):
    def __init__(self, game, image, pos):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.alpha = 255
        self.game.sprites.append(self)
        self.image = pg.image.load("sprites/decorations/" + image).convert_alpha()
        self.imgRect = self.image.get_rect()
        self.imgRect.center = pos
        self.rect = self.imgRect
        self.room = self.game.room

    def update(self):
        if self.room != self.game.room:
            self.game.sprites.remove(self)


class Void(pg.sprite.Sprite):
    def __init__(self, game, size):
        self.game = game
        self.game.void = self
        self.alpha = 255
        self.lastUpdate = 0
        self.currentFrame = 0
        self.speed = 0
        self.scale = size
        self.image = pg.transform.scale(voidSprites[self.currentFrame], (
        round(voidSprites[self.currentFrame].get_width() * self.scale),
        round(voidSprites[self.currentFrame].get_height() * self.scale)))
        self.rect = self.image.get_rect()
        self.rect.center = voidSpot

    def update(self, size):
        if self.scale > size and self.speed == 0:
            self.speed = (self.scale - size) / 180 * -1
        elif self.scale < size and self.speed == 0:
            self.speed = (size - self.scale) / 180

        self.speed = round(self.speed, 3)

        if self.speed != 0:
            if self.scale > size and self.speed < 0:
                self.scale += self.speed
            elif self.scale < size and self.speed > 0:
                self.scale += self.speed
            else:
                self.scale = size
                self.speed = 0

        now = pg.time.get_ticks()
        if now - self.lastUpdate > 30:
            self.lastUpdate = now
            if self.currentFrame < len(voidSprites):
                self.currentFrame = (self.currentFrame + 1) % (len(voidSprites))
            else:
                self.currentFrame = 0
            center = self.rect.center
            self.image = pg.transform.scale(voidSprites[self.currentFrame], (
                round(voidSprites[self.currentFrame].get_width() * abs(self.scale)),
                round(voidSprites[self.currentFrame].get_height() * abs(self.scale))))
            self.rect = self.image.get_rect()
            self.rect.center = center


class BroqueMonsieurShop(pg.sprite.Sprite):
    def __init__(self, game, pos, song):
        pg.sprite.Sprite.__init__(self, game.npcs)
        self.game = game
        self.canTalk = True
        self.textbox = None
        self.game.sprites.append(self)
        self.loadImages()
        self.facing = "down"
        self.talking = False
        self.image = self.idleFrames["down"][0]
        self.rect = self.shadow.get_rect()
        self.imgRect = self.image.get_rect()
        self.rect.center = pos
        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx
        self.canShop = False
        self.type = "talk"
        self.lastUpdate = 0
        self.currentFrame = 0
        self.alpha = 255
        self.shopContents = [["Mushroom", 5], ["Super Mushroom", 15], ["1-UP Mushroom", 10], ["1-UP Deluxe", 30],
                             ["Syrup", 5], ["Star Cand", 15]]
        self.song = song
        self.text = ["Bonjour, monsieur Red and Green!",
                     "I have shöp."]

    def loadImages(self):
        sheet = spritesheet("sprites/broque monsieur.png", "sprites/broque monsieur.xml")

        self.shadow = sheet.getImageName("shadow.png")

        self.idleFrames = {"up": [sheet.getImageName("standing_up_1.png"),
                                  sheet.getImageName("standing_up_2.png"),
                                  sheet.getImageName("standing_up_3.png"),
                                  sheet.getImageName("standing_up_4.png"),
                                  sheet.getImageName("standing_up_5.png"),
                                  sheet.getImageName("standing_up_6.png"),
                                  sheet.getImageName("standing_up_7.png"),
                                  sheet.getImageName("standing_up_8.png")],
                           "down": [sheet.getImageName("standing_down_1.png"),
                                    sheet.getImageName("standing_down_2.png"),
                                    sheet.getImageName("standing_down_3.png"),
                                    sheet.getImageName("standing_down_4.png"),
                                    sheet.getImageName("standing_down_5.png"),
                                    sheet.getImageName("standing_down_6.png"),
                                    sheet.getImageName("standing_down_7.png"),
                                    sheet.getImageName("standing_down_8.png")],
                           "left": [sheet.getImageName("standing_left_1.png"),
                                    sheet.getImageName("standing_left_2.png"),
                                    sheet.getImageName("standing_left_3.png"),
                                    sheet.getImageName("standing_left_4.png"),
                                    sheet.getImageName("standing_left_5.png"),
                                    sheet.getImageName("standing_left_6.png"),
                                    sheet.getImageName("standing_left_7.png"),
                                    sheet.getImageName("standing_left_8.png")],
                           "right": [sheet.getImageName("standing_right_1.png"),
                                     sheet.getImageName("standing_right_2.png"),
                                     sheet.getImageName("standing_right_3.png"),
                                     sheet.getImageName("standing_right_4.png"),
                                     sheet.getImageName("standing_right_5.png"),
                                     sheet.getImageName("standing_right_6.png"),
                                     sheet.getImageName("standing_right_7.png"),
                                     sheet.getImageName("standing_right_8.png")]
                           }

        self.talkingFrames = {"up": [sheet.getImageName("talking_up_1.png"),
                                     sheet.getImageName("talking_up_2.png"),
                                     sheet.getImageName("talking_up_3.png"),
                                     sheet.getImageName("talking_up_4.png"),
                                     sheet.getImageName("talking_up_5.png"),
                                     sheet.getImageName("talking_up_6.png"),
                                     sheet.getImageName("talking_up_7.png"),
                                     sheet.getImageName("talking_up_8.png")],
                              "down": [sheet.getImageName("talking_down_1.png"),
                                       sheet.getImageName("talking_down_2.png"),
                                       sheet.getImageName("talking_down_3.png"),
                                       sheet.getImageName("talking_down_4.png"),
                                       sheet.getImageName("talking_down_5.png"),
                                       sheet.getImageName("talking_down_6.png"),
                                       sheet.getImageName("talking_down_7.png"),
                                       sheet.getImageName("talking_down_8.png")],
                              "left": [sheet.getImageName("talking_left_1.png"),
                                       sheet.getImageName("talking_left_2.png"),
                                       sheet.getImageName("talking_left_3.png"),
                                       sheet.getImageName("talking_left_4.png"),
                                       sheet.getImageName("talking_left_5.png"),
                                       sheet.getImageName("talking_left_6.png"),
                                       sheet.getImageName("talking_left_7.png"),
                                       sheet.getImageName("talking_left_8.png")],
                              "right": [sheet.getImageName("talking_right_1.png"),
                                        sheet.getImageName("talking_right_2.png"),
                                        sheet.getImageName("talking_right_3.png"),
                                        sheet.getImageName("talking_right_4.png"),
                                        sheet.getImageName("talking_right_5.png"),
                                        sheet.getImageName("talking_right_6.png"),
                                        sheet.getImageName("talking_right_7.png"),
                                        sheet.getImageName("talking_right_8.png")]
                              }

    def update(self):
        self.animate()
        if self.textbox is None:
            for event in self.game.event:
                if event.type == pg.KEYDOWN:
                    if self.game.leader == "mario":
                        if pg.sprite.collide_rect_ratio(1.1)(self,
                                                             self.game.player) and event.key == pg.K_m and self.game.player.canMove and self.game.follower.canMove:
                            if not self.game.player.jumping:
                                if self.game.player.rect.top >= self.rect.bottom:
                                    self.facing = "down"
                                elif self.game.player.rect.bottom <= self.rect.top:
                                    self.facing = "up"
                                elif self.rect.right + self.game.player.rect.width > self.game.player.rect.right >= self.rect.left:
                                    self.facing = "left"
                                elif self.game.player.rect.left <= self.rect.right:
                                    self.facing = "right"
                                self.textbox = TextBox(self.game, self, self.text)
                                self.canShop = True
                    elif self.game.leader == "luigi":
                        if pg.sprite.collide_rect_ratio(1.1)(self,
                                                             self.game.follower) and event.key == pg.K_l and self.game.player.canMove and self.game.follower.canMove:
                            if not self.game.follower.jumping:
                                if self.game.follower.rect.top >= self.rect.bottom:
                                    self.facing = "down"
                                elif self.game.follower.rect.bottom <= self.rect.top:
                                    self.facing = "up"
                                elif self.rect.right + self.game.player.rect.width > self.game.follower.rect.right >= self.rect.left:
                                    self.facing = "left"
                                elif self.game.follower.rect.left <= self.rect.right:
                                    self.facing = "right"
                                self.textbox = TextBox(self.game, self, self.text)
                                self.canShop = True
        elif self.textbox != "complete":
            if self.textbox.talking:
                self.talking = True
            else:
                self.talking = False
        else:
            if self.shopContents is not None:
                if self.canShop:
                    self.game.shop(self.shopContents, self.song)
                    self.canShop = False
                    self.textbox = TextBox(self.game, self, ["Thank you for your shopping!"])
                else:
                    self.facing = "down"
                    self.textbox = None
            else:
                self.facing = "down"
                self.textbox = None

    def animate(self):
        now = pg.time.get_ticks()
        if not self.talking:
            if self.facing == "down":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.idleFrames["down"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.idleFrames["down"]))
                    else:
                        self.currentFrame = 0
                    centerx = self.imgRect.centerx
                    bottom = self.imgRect.bottom
                    self.image = self.idleFrames["down"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.centerx = centerx
                    self.imgRect.bottom = bottom
            elif self.facing == "up":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.idleFrames["up"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.idleFrames["up"]))
                    else:
                        self.currentFrame = 0
                    centerx = self.imgRect.centerx
                    bottom = self.imgRect.bottom
                    self.image = self.idleFrames["up"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.centerx = centerx
                    self.imgRect.bottom = bottom
            elif self.facing == "left":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.idleFrames["left"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.idleFrames["left"]))
                    else:
                        self.currentFrame = 0
                    centerx = self.imgRect.centerx
                    bottom = self.imgRect.bottom
                    self.image = self.idleFrames["left"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.centerx = centerx
                    self.imgRect.bottom = bottom
            elif self.facing == "right":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.idleFrames["right"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.idleFrames["right"]))
                    else:
                        self.currentFrame = 0
                    centerx = self.imgRect.centerx
                    bottom = self.imgRect.bottom
                    self.image = self.idleFrames["right"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.centerx = centerx
                    self.imgRect.bottom = bottom
        else:
            if self.facing == "down":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFrames["down"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFrames["down"]))
                    else:
                        self.currentFrame = 0
                    bottom = self.imgRect.bottom
                    centerx = self.imgRect.centerx
                    self.image = self.talkingFrames["down"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.centerx = centerx
            elif self.facing == "up":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFrames["up"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFrames["up"]))
                    else:
                        self.currentFrame = 0
                    bottom = self.imgRect.bottom
                    centerx = self.imgRect.centerx
                    self.image = self.talkingFrames["up"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.centerx = centerx
            elif self.facing == "left":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFrames["left"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFrames["left"]))
                    else:
                        self.currentFrame = 0
                    bottom = self.imgRect.bottom
                    centerx = self.imgRect.centerx
                    self.image = self.talkingFrames["left"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.centerx = centerx
            elif self.facing == "right":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFrames["right"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFrames["right"]))
                    else:
                        self.currentFrame = 0
                    bottom = self.imgRect.bottom
                    centerx = self.imgRect.centerx
                    self.image = self.talkingFrames["right"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.centerx = centerx


class FlipsideToSansRoom(pg.sprite.Sprite):
    def __init__(self, game, pos):
        pg.sprite.Sprite.__init__(self, game.npcs)
        self.game = game
        self.canTalk = True
        self.textbox = None
        self.game.sprites.append(self)
        self.loadImages()
        self.facing = "down"
        self.talking = False
        self.image = self.images[0]
        self.shadow = self.image
        self.rect = self.image.get_rect()
        self.imgRect = self.image.get_rect()
        self.rect.center = pos
        self.imgRect.bottom = self.rect.bottom
        self.imgRect.centerx = self.rect.centerx
        self.fade = None
        self.type = "interact"
        self.lastUpdate = 0
        self.currentFrame = 0
        self.select = 0
        self.alpha = 255
        self.options = [pg.rect.Rect(389, 390, 0, 0), pg.rect.Rect(773, 390, 0, 0)]
        self.cursor = None
        self.text = ["/CDo you want to go to another world?\n\a\n\a                 YES                        NO"]

    def loadImages(self):
        sheet = spritesheet("sprites/blocks.png", "sprites/blocks.xml")

        self.images = [sheet.getImageName("undertale_save_1.png"),
                       sheet.getImageName("undertale_save_2.png")]

    def update(self):
        self.animate()
        if self.textbox is None:
            for event in self.game.event:
                if event.type == pg.KEYDOWN:
                    if self.game.leader == "mario":
                        if pg.sprite.collide_rect_ratio(1.1)(self,
                                                             self.game.player) and event.key == pg.K_m and self.game.player.canMove and self.game.follower.canMove:
                            if not self.game.player.jumping:
                                if self.game.player.rect.top >= self.rect.bottom:
                                    self.facing = "down"
                                elif self.game.player.rect.bottom <= self.rect.top:
                                    self.facing = "up"
                                elif self.rect.right + self.game.player.rect.width > self.game.player.rect.right >= self.rect.left:
                                    self.facing = "left"
                                elif self.game.player.rect.left <= self.rect.right:
                                    self.facing = "right"
                                self.textbox = TextBox(self.game, self, self.text, type="board", dir="None", choice=True)
                    elif self.game.leader == "luigi":
                        if pg.sprite.collide_rect_ratio(1.1)(self,
                                                             self.game.follower) and event.key == pg.K_l and self.game.player.canMove and self.game.follower.canMove:
                            if not self.game.follower.jumping:
                                if self.game.follower.rect.top >= self.rect.bottom:
                                    self.facing = "down"
                                elif self.game.follower.rect.bottom <= self.rect.top:
                                    self.facing = "up"
                                elif self.rect.right + self.game.player.rect.width > self.game.follower.rect.right >= self.rect.left:
                                    self.facing = "left"
                                elif self.game.follower.rect.left <= self.rect.right:
                                    self.facing = "right"
                                self.textbox = TextBox(self.game, self, self.text, type="board", dir="None", choice=True)
        elif self.textbox != "complete":
            if self.textbox.talking:
                self.talking = True
            else:
                self.talking = False
            if self.textbox.choosing:
                if self.cursor is None:
                    self.cursor = Cursor(self.game, self.options[0])
                self.cursor.update(self.options[self.select], 60)

                for event in self.game.event:
                    if event.type == pg.KEYDOWN:
                        if (event.key == pg.K_a or event.key == pg.K_d) and self.cursor in self.game.cursors:
                            if self.select == 1:
                                self.select = 0
                            elif self.select == 0:
                                self.select = 1
                            self.game.abilityAdvanceSound.play()
                        if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                            self.cursor.kill()
                            self.game.menuChooseSound.play()
        else:
            self.facing = "down"
            self.textbox = None
            self.cursor = None
            if self.select == 0:
                self.fade = Fadeout(self.game, 5)
                pg.mixer.music.fadeout(3000)
                self.game.player.canMove = False
                self.game.follower.canMove = False

        if self.fade is not None:
            if self.fade.alpha >= 255:
                time.sleep(2)
                self.game.playtime += fps * 2
                self.game.storeData["mario facing"] = self.game.player.facing
                self.game.storeData["luigi facing"] = self.game.follower.facing
                self.game.storeData["mario pos"] = "beef"
                self.game.storeData["luigi pos"] = "beef"
                self.game.storeData["mario stats"] = self.game.player.stats
                self.game.storeData["luigi stats"] = self.game.follower.stats
                self.game.storeData["mario abilities"] = self.game.player.abilities
                self.game.storeData["luigi abilities"] = self.game.follower.abilities
                self.game.storeData["mario current ability"] = self.game.player.ability
                self.game.storeData["luigi current ability"] = self.game.follower.ability
                self.game.storeData["mario attack pieces"] = self.game.player.attackPieces
                self.game.storeData["luigi attack pieces"] = self.game.follower.attackPieces
                self.game.storeData["move"] = Q.deque()
                self.game.currentPoint = 0
                self.game.player.canMove = True
                self.game.follower.canMove = True
                self.game.loadSansRoom()

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 200:
            self.lastUpdate = now
            if self.currentFrame < len(self.images):
                self.currentFrame = (self.currentFrame + 1) % (len(self.images))
            else:
                self.currentFrame = 0
            center = self.imgRect.center
            self.image = self.images[self.currentFrame]
            self.imgRect = self.image.get_rect()
            self.imgRect.center = center

            self.shadow = self.images[1]
            center = self.rect.center
            self.rect = self.shadow.get_rect()
            self.rect.center = center
            if self.currentFrame == 1:
                self.shadow.set_alpha(255)
            else:
                self.shadow.set_alpha(0)


class ToadleyOverworld(pg.sprite.Sprite):
    def __init__(self, game, pos):
        pg.sprite.Sprite.__init__(self, game.npcs)
        self.game = game
        self.canTalk = True
        self.textbox = None
        self.game.sprites.append(self)
        self.loadImages()
        self.type = "talk"
        self.facing = "left"
        self.talking = False
        self.image = self.idleFrames["down"]
        self.rect = self.shadow.get_rect()
        self.imgRect = self.image.get_rect()
        self.rect.center = pos
        self.imgRect.bottom = self.rect.bottom - 2
        self.imgRect.centerx = self.rect.centerx
        self.canShop = False
        self.lastUpdate = 0
        self.currentFrame = 0
        self.alpha = 255
        self.text = ["What are you doing?",
                     "Go, save all worlds!"]

    def loadImages(self):
        sheet = spritesheet("sprites/toadley.png", "sprites/toadley.xml")

        self.shadow = sheet.getImageName("shadow.png")

        self.idleFrames = {"up": sheet.getImageName("standing_up.png"),
                           "down": sheet.getImageName("standing_down.png"),
                           "left": sheet.getImageName("standing_left.png"),
                           "right": sheet.getImageName("standing_right.png")
                           }

        self.talkingFrames = {"up": [sheet.getImageName("talking_up_1.png"),
                                     sheet.getImageName("talking_up_2.png"),
                                     sheet.getImageName("talking_up_3.png"),
                                     sheet.getImageName("talking_up_4.png"),
                                     sheet.getImageName("talking_up_5.png"),
                                     sheet.getImageName("talking_up_6.png")],
                              "down": [sheet.getImageName("talking_down_1.png"),
                                       sheet.getImageName("talking_down_2.png"),
                                       sheet.getImageName("talking_down_3.png"),
                                       sheet.getImageName("talking_down_4.png"),
                                       sheet.getImageName("talking_down_5.png"),
                                       sheet.getImageName("talking_down_6.png")],
                              "left": [sheet.getImageName("talking_left_1.png"),
                                       sheet.getImageName("talking_left_2.png"),
                                       sheet.getImageName("talking_left_3.png"),
                                       sheet.getImageName("talking_left_4.png"),
                                       sheet.getImageName("talking_left_5.png"),
                                       sheet.getImageName("talking_left_6.png")],
                              "right": [sheet.getImageName("talking_right_1.png"),
                                        sheet.getImageName("talking_right_2.png"),
                                        sheet.getImageName("talking_right_3.png"),
                                        sheet.getImageName("talking_right_4.png"),
                                        sheet.getImageName("talking_right_5.png"),
                                        sheet.getImageName("talking_right_6.png")]
                              }

    def update(self):
        self.animate()
        if self.textbox is None:
            for event in self.game.event:
                if event.type == pg.KEYDOWN:
                    if self.game.leader == "mario":
                        if pg.sprite.collide_rect_ratio(1.1)(self,
                                                             self.game.player) and event.key == pg.K_m and self.game.player.canMove and self.game.follower.canMove:
                            if not self.game.player.jumping:
                                if self.game.player.rect.top >= self.rect.bottom:
                                    self.facing = "down"
                                elif self.game.player.rect.bottom <= self.rect.top:
                                    self.facing = "up"
                                elif self.rect.right + self.game.player.rect.width > self.game.player.rect.right >= self.rect.left:
                                    self.facing = "left"
                                elif self.game.player.rect.left <= self.rect.right:
                                    self.facing = "right"
                                self.textbox = TextBox(self.game, self, self.text)
                    elif self.game.leader == "luigi":
                        if pg.sprite.collide_rect_ratio(1.1)(self,
                                                             self.game.follower) and event.key == pg.K_l and self.game.player.canMove and self.game.follower.canMove:
                            if not self.game.follower.jumping:
                                if self.game.follower.rect.top >= self.rect.bottom:
                                    self.facing = "down"
                                elif self.game.follower.rect.bottom <= self.rect.top:
                                    self.facing = "up"
                                elif self.rect.right + self.game.player.rect.width > self.game.follower.rect.right >= self.rect.left:
                                    self.facing = "left"
                                elif self.game.follower.rect.left <= self.rect.right:
                                    self.facing = "right"
                                self.textbox = TextBox(self.game, self, self.text)
        elif self.textbox != "complete":
            if self.textbox.talking:
                self.talking = True
            else:
                self.talking = False
        else:
            self.facing = "left"
            self.textbox = None

    def animate(self):
        now = pg.time.get_ticks()
        if not self.talking:
            if self.facing == "down":
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                self.image = self.idleFrames["down"]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
            elif self.facing == "up":
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                self.image = self.idleFrames["up"]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
            elif self.facing == "left":
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                self.image = self.idleFrames["left"]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
            elif self.facing == "right":
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                self.image = self.idleFrames["right"]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        else:
            if self.facing == "down":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFrames["down"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFrames["down"]))
                    else:
                        self.currentFrame = 0
                    bottom = self.imgRect.bottom
                    centerx = self.imgRect.centerx
                    self.image = self.talkingFrames["down"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.centerx = centerx
            elif self.facing == "up":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFrames["up"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFrames["up"]))
                    else:
                        self.currentFrame = 0
                    bottom = self.imgRect.bottom
                    centerx = self.imgRect.centerx
                    self.image = self.talkingFrames["up"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.centerx = centerx
            elif self.facing == "left":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFrames["left"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFrames["left"]))
                    else:
                        self.currentFrame = 0
                    bottom = self.imgRect.bottom
                    centerx = self.imgRect.centerx
                    self.image = self.talkingFrames["left"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.centerx = centerx
            elif self.facing == "right":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFrames["right"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFrames["right"]))
                    else:
                        self.currentFrame = 0
                    bottom = self.imgRect.bottom
                    centerx = self.imgRect.centerx
                    self.image = self.talkingFrames["right"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.centerx = centerx
