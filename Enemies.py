from pygame.rect import RectType

from Overworld import *
from CutsceneObjects import *
from UI import *
from Settings import *
from statemachine import StateMachine, State
from math import sin, cos, pi, atan2


def get_angle(origin, destination):
    x_dist = destination[0] - origin[0]
    y_dist = destination[1] - origin[1]
    return atan2(-y_dist, x_dist) % (2 * pi)


def project(pos, angle, distance):
    return (pos[0] + (cos(angle) * distance),
            pos[1] - (sin(angle) * distance))


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


class GoombaODebug(pg.sprite.Sprite):
    def __init__(self, game, x, y, battle):
        pg.sprite.Sprite.__init__(self)
        self.newID = False
        self.game = game
        self.ID = -12
        self.game.sprites.append(self)
        self.game.enemies.append(self)
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
                    self.game.loadBattle(self.battle)

            hits = pg.sprite.collide_rect(self, self.game.follower)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self, self.game.followerCol)
                if hitsRound2:
                    self.game.despawnList.append(self.ID)
                    if len(self.game.despawnList) > 13:
                        self.game.despawnList.remove(self.game.despawnList[0])
                    self.game.loadBattle(self.battle)

            if self.game.player.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                    if hammerHitsRound2:
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)

            if self.game.follower.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                    if hammerHitsRound2:
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)

            for entity in self.game.entities:
                if self.rect.colliderect(entity.rect):
                    if type(entity).__name__ == "Lightning":
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)
                    if self.imgRect.colliderect(entity.imgRect):
                        if type(entity).__name__ == "Fireball":
                            self.game.despawnList.append(self.ID)
                            if len(self.game.despawnList) > 13:
                                self.game.despawnList.remove(self.game.despawnList[0])
                            self.game.loadBattle(self.battle)


class GoombaOverworld(StateMachine):
    idle = State("Idle", initial=True)
    moving = State("Moving")

    startWalking = idle.to(moving)
    giveUp = moving.to(idle)

    def init(self, game, x, y, battle, facing="down"):
        self.game = game
        self.game.sprites.append(self)
        self.game.enemies.append(self)
        self.loadImages()
        self.vx = 0
        self.vy = 0
        self.image = self.walkingFramesDown[0]
        self.currentFrame = random.randrange(len(self.walkingFramesDown))
        self.lastUpdate = 0
        self.facing = facing
        self.shadow = self.shadowFrame
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)
        self.alpha = 255
        self.speed = 2
        self.battle = battle
        self.newID = False
        self.id = -12

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
        if self.is_moving:
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
        else:
            if self.facing == "down":
                center = self.imgRect.center
                self.image = self.walkingFramesDown[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "up":
                center = self.imgRect.center
                self.image = self.walkingFramesUp[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "left":
                center = self.imgRect.center
                self.image = self.walkingFramesLeft[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "right":
                center = self.imgRect.center
                self.image = self.walkingFramesRight[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center

    def update(self):
        self.animate()

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
                    self.game.loadBattle(self.battle)

            hits = pg.sprite.collide_rect(self, self.game.follower)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self, self.game.followerCol)
                if hitsRound2:
                    self.game.despawnList.append(self.ID)
                    if len(self.game.despawnList) > 13:
                        self.game.despawnList.remove(self.game.despawnList[0])
                    self.game.loadBattle(self.battle)

            if self.game.player.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                    if hammerHitsRound2:
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)

            if self.game.follower.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                    if hammerHitsRound2:
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)

            for entity in self.game.entities:
                if self.rect.colliderect(entity.rect):
                    if type(entity).__name__ == "Lightning":
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)
                    if self.imgRect.colliderect(entity.imgRect):
                        if type(entity).__name__ == "Fireball":
                            self.game.despawnList.append(self.ID)
                            if len(self.game.despawnList) > 13:
                                self.game.despawnList.remove(self.game.despawnList[0])
                            self.game.loadBattle(self.battle)

        if self.is_idle:
            chance = random.randrange(0, 100)
            if chance == 0:
                dir = random.randrange(0, 4)
                if dir == 0:
                    self.facing = "up"
                    self.vy = -self.speed
                elif dir == 1:
                    self.facing = "down"
                    self.vy = self.speed
                elif dir == 2:
                    self.facing = "left"
                    self.vx = -self.speed
                else:
                    self.facing = "right"
                    self.vx = self.speed
                self.startWalking()
            else:
                self.vx, self.vy = 0, 0
        elif self.is_moving:
            self.rect.x += self.vx
            self.rect.y += self.vy

            for wall in self.game.walls:
                if pg.sprite.collide_rect(self, wall):
                    self.vx *= -1
                    self.vy *= -1
                    if self.facing == "up":
                        self.rect.top = wall.rect.bottom
                        self.rect.y += self.vy
                        self.facing = "down"
                    elif self.facing == "down":
                        self.rect.bottom = wall.rect.top
                        self.rect.y += self.vy
                        self.facing = "up"
                    elif self.facing == "left":
                        self.rect.left = wall.rect.right
                        self.rect.x += self.vx
                        self.facing = "right"
                    elif self.facing == "right":
                        self.rect.right = wall.rect.left
                        self.rect.x += self.vx
                        self.facing = "left"

            chance = random.randrange(0, 100)
            if chance == 0:
                self.giveUp()

        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx


class KoopaOverworld(StateMachine):
    idle = State("Idle", initial=True)
    moving = State("Moving")

    startWalking = idle.to(moving)
    giveUp = moving.to(idle)

    def init(self, game, x, y, battle, facing="down"):
        self.game = game
        self.game.sprites.append(self)
        self.game.enemies.append(self)
        self.loadImages()
        self.vx = 0
        self.vy = 0
        self.image = self.walkingFramesDown[0]
        self.currentFrame = random.randrange(len(self.walkingFramesDown))
        self.lastUpdate = 0
        self.facing = facing
        self.shadow = self.shadowFrame
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)
        self.alpha = 255
        self.speed = 2
        self.battle = battle
        self.newID = False
        self.id = -12

    def loadImages(self):
        sheet = spritesheet("sprites/koopa.png", "sprites/koopa.xml")

        self.walkingFramesUp = [sheet.getImageName("walking_up_1.png"),
                                sheet.getImageName("walking_up_2.png"),
                                sheet.getImageName("walking_up_3.png"),
                                sheet.getImageName("walking_up_4.png"),
                                sheet.getImageName("walking_up_5.png"),
                                sheet.getImageName("walking_up_6.png"),
                                sheet.getImageName("walking_up_7.png"),
                                sheet.getImageName("walking_up_8.png"),
                                sheet.getImageName("walking_up_9.png"),
                                sheet.getImageName("walking_up_10.png")]

        self.walkingFramesDown = [sheet.getImageName("walking_down_1.png"),
                                  sheet.getImageName("walking_down_2.png"),
                                  sheet.getImageName("walking_down_3.png"),
                                  sheet.getImageName("walking_down_4.png"),
                                  sheet.getImageName("walking_down_5.png"),
                                  sheet.getImageName("walking_down_6.png"),
                                  sheet.getImageName("walking_down_7.png"),
                                  sheet.getImageName("walking_down_8.png"),
                                  sheet.getImageName("walking_down_9.png"),
                                  sheet.getImageName("walking_down_10.png")]

        self.walkingFramesLeft = [sheet.getImageName("walking_left_1.png"),
                                  sheet.getImageName("walking_left_2.png"),
                                  sheet.getImageName("walking_left_3.png"),
                                  sheet.getImageName("walking_left_4.png"),
                                  sheet.getImageName("walking_left_5.png"),
                                  sheet.getImageName("walking_left_6.png"),
                                  sheet.getImageName("walking_left_7.png"),
                                  sheet.getImageName("walking_left_8.png"),
                                  sheet.getImageName("walking_left_9.png"),
                                  sheet.getImageName("walking_left_10.png")]

        self.walkingFramesRight = [sheet.getImageName("walking_right_1.png"),
                                   sheet.getImageName("walking_right_2.png"),
                                   sheet.getImageName("walking_right_3.png"),
                                   sheet.getImageName("walking_right_4.png"),
                                   sheet.getImageName("walking_right_5.png"),
                                   sheet.getImageName("walking_right_6.png"),
                                   sheet.getImageName("walking_right_7.png"),
                                   sheet.getImageName("walking_right_8.png"),
                                   sheet.getImageName("walking_right_9.png"),
                                   sheet.getImageName("walking_right_10.png")]

        self.shadowFrame = sheet.getImageName("shadow.png")

    def animate(self):
        now = pg.time.get_ticks()
        if self.is_moving:
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
        else:
            if self.facing == "down":
                center = self.imgRect.center
                self.image = self.walkingFramesDown[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "up":
                center = self.imgRect.center
                self.image = self.walkingFramesUp[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "left":
                center = self.imgRect.center
                self.image = self.walkingFramesLeft[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "right":
                center = self.imgRect.center
                self.image = self.walkingFramesRight[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center

    def update(self):
        self.animate()

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
                    self.game.loadBattle(self.battle)

            hits = pg.sprite.collide_rect(self, self.game.follower)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self, self.game.followerCol)
                if hitsRound2:
                    self.game.despawnList.append(self.ID)
                    if len(self.game.despawnList) > 13:
                        self.game.despawnList.remove(self.game.despawnList[0])
                    self.game.loadBattle(self.battle)

            if self.game.player.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                    if hammerHitsRound2:
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)

            if self.game.follower.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                    if hammerHitsRound2:
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)

            for entity in self.game.entities:
                if self.rect.colliderect(entity.rect):
                    if type(entity).__name__ == "Lightning":
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)
                    if self.imgRect.colliderect(entity.imgRect):
                        if type(entity).__name__ == "Fireball":
                            self.game.despawnList.append(self.ID)
                            if len(self.game.despawnList) > 13:
                                self.game.despawnList.remove(self.game.despawnList[0])
                            self.game.loadBattle(self.battle)

        if self.is_idle:
            chance = random.randrange(0, 100)
            if chance == 0:
                dir = random.randrange(0, 4)
                if dir == 0:
                    self.facing = "up"
                    self.vy = -self.speed
                elif dir == 1:
                    self.facing = "down"
                    self.vy = self.speed
                elif dir == 2:
                    self.facing = "left"
                    self.vx = -self.speed
                else:
                    self.facing = "right"
                    self.vx = self.speed
                self.startWalking()
            else:
                self.vx, self.vy = 0, 0
        elif self.is_moving:
            self.rect.x += self.vx
            self.rect.y += self.vy

            for wall in self.game.walls:
                if pg.sprite.collide_rect(self, wall):
                    self.vx *= -1
                    self.vy *= -1
                    if self.facing == "up":
                        self.rect.top = wall.rect.bottom
                        self.rect.y += self.vy
                        self.facing = "down"
                    elif self.facing == "down":
                        self.rect.bottom = wall.rect.top
                        self.rect.y += self.vy
                        self.facing = "up"
                    elif self.facing == "left":
                        self.rect.left = wall.rect.right
                        self.rect.x += self.vx
                        self.facing = "right"
                    elif self.facing == "right":
                        self.rect.right = wall.rect.left
                        self.rect.x += self.vx
                        self.facing = "left"

            chance = random.randrange(0, 100)
            if chance == 0:
                self.giveUp()

        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx


class SandoonOverworld(StateMachine):
    idle = State("Idle", initial=True)
    moving = State("Moving")
    toEyes = State("To Eyes")
    fromEyes = State("From Eyes")
    eyes = State("Eyes")

    startWalking = idle.to(moving)
    giveUp = moving.to(idle)
    goToEyes = idle.to(toEyes)
    reachEyes = toEyes.to(eyes)
    leaveEyes = eyes.to(fromEyes)
    finishEyes = fromEyes.to(idle)

    def init(self, game, x, y, battle, facing="down"):
        self.game = game
        self.game.sprites.append(self)
        self.game.enemies.append(self)
        self.loadImages()
        self.vx = 0
        self.vy = 0
        self.image = self.walkingFramesDown[0]
        self.currentFrame = random.randrange(len(self.walkingFramesDown))
        self.lastUpdate = 0
        self.facing = facing
        self.shadow = self.shadowFrames["Normal"]
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)
        self.alpha = 255
        self.speed = 2
        self.battle = battle
        self.newID = False
        self.id = -12

    def loadImages(self):
        sheet = spritesheet("sprites/sandoon overworld.png", "sprites/sandoon overworld.xml")

        self.walkingFramesUp = [sheet.getImageName("idle_up_1.png"),
                                sheet.getImageName("idle_up_2.png"),
                                sheet.getImageName("idle_up_3.png"),
                                sheet.getImageName("idle_up_4.png")]

        self.walkingFramesDown = [sheet.getImageName("idle_down_1.png"),
                                  sheet.getImageName("idle_down_2.png"),
                                  sheet.getImageName("idle_down_3.png"),
                                  sheet.getImageName("idle_down_4.png")]

        self.walkingFramesLeft = [sheet.getImageName("idle_left_1.png"),
                                  sheet.getImageName("idle_left_2.png"),
                                  sheet.getImageName("idle_left_3.png"),
                                  sheet.getImageName("idle_left_4.png")]

        self.walkingFramesRight = [sheet.getImageName("idle_right_1.png"),
                                   sheet.getImageName("idle_right_2.png"),
                                   sheet.getImageName("idle_right_3.png"),
                                   sheet.getImageName("idle_right_4.png")]

        self.toEyesFrames = [sheet.getImageName("to_eyes_1.png"),
                             sheet.getImageName("to_eyes_2.png"),
                             sheet.getImageName("to_eyes_3.png"),
                             sheet.getImageName("to_eyes_4.png"),
                             sheet.getImageName("to_eyes_5.png"),
                             sheet.getImageName("to_eyes_6.png"),
                             sheet.getImageName("to_eyes_7.png"),
                             sheet.getImageName("to_eyes_8.png"),
                             sheet.getImageName("to_eyes_9.png"),
                             sheet.getImageName("to_eyes_10.png"),
                             sheet.getImageName("to_eyes_11.png"),
                             sheet.getImageName("to_eyes_12.png"),
                             sheet.getImageName("to_eyes_13.png")]

        self.fromEyesFrames = [sheet.getImageName("from_eyes_1.png"),
                               sheet.getImageName("from_eyes_2.png"),
                               sheet.getImageName("from_eyes_3.png"),
                               sheet.getImageName("from_eyes_4.png"),
                               sheet.getImageName("from_eyes_5.png"),
                               sheet.getImageName("from_eyes_6.png"),
                               sheet.getImageName("from_eyes_7.png"),
                               sheet.getImageName("from_eyes_8.png"),
                               sheet.getImageName("from_eyes_9.png"),
                               sheet.getImageName("from_eyes_10.png"),
                               sheet.getImageName("from_eyes_11.png"),
                               sheet.getImageName("from_eyes_12.png")]

        self.eyeFrames = [sheet.getImageName("eyes_1.png"),
                          sheet.getImageName("eyes_2.png"),
                          sheet.getImageName("eyes_3.png"),
                          sheet.getImageName("eyes_4.png"),
                          sheet.getImageName("eyes_5.png"),
                          sheet.getImageName("eyes_6.png"),
                          sheet.getImageName("eyes_7.png"),
                          sheet.getImageName("eyes_8.png"),
                          sheet.getImageName("eyes_9.png"),
                          sheet.getImageName("eyes_10.png"),
                          sheet.getImageName("eyes_11.png"),
                          sheet.getImageName("eyes_12.png"),
                          sheet.getImageName("eyes_13.png"),
                          sheet.getImageName("eyes_14.png"),
                          sheet.getImageName("eyes_15.png"),
                          sheet.getImageName("eyes_16.png"),
                          sheet.getImageName("eyes_17.png")]

        self.shadowFrames = {"Normal": sheet.getImageName("shadow.png"), "Eyes": sheet.getImageName("eyeShadow.png")}

    def animate(self):
        now = pg.time.get_ticks()
        if self.is_toEyes:
            if now - self.lastUpdate > 60:
                if self.shadow != self.shadowFrames["Eyes"]:
                    self.shadow = self.shadowFrames["Eyes"]
                    bottom = self.rect.bottom
                    centerx = self.rect.centerx
                    self.rect = self.shadow.get_rect()
                    self.rect.centerx = centerx
                    self.rect.bottom = bottom
                self.lastUpdate = now
                if self.currentFrame < len(self.toEyesFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1) % (len(self.toEyesFrames))
                else:
                    self.reachEyes()
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                self.image = self.toEyesFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        elif self.is_eyes:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.eyeFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.eyeFrames))
                else:
                    self.currentFrame = 0
                center = self.imgRect.center
                self.image = self.eyeFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.is_fromEyes:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.fromEyesFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1) % (len(self.fromEyesFrames))
                else:
                    self.finishEyes()
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                self.image = self.fromEyesFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        else:
            if self.shadow != self.shadowFrames["Normal"]:
                self.shadow = self.shadowFrames["Normal"]
                bottom = self.rect.bottom
                centerx = self.rect.centerx
                self.rect = self.shadow.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom
            if self.facing == "down":
                if now - self.lastUpdate > 60:
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
                if now - self.lastUpdate > 60:
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
                if now - self.lastUpdate > 60:
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
                if now - self.lastUpdate > 60:
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
                    self.game.loadBattle(self.battle)

            hits = pg.sprite.collide_rect(self, self.game.follower)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self, self.game.followerCol)
                if hitsRound2:
                    self.game.despawnList.append(self.ID)
                    if len(self.game.despawnList) > 13:
                        self.game.despawnList.remove(self.game.despawnList[0])
                    self.game.loadBattle(self.battle)

            if self.game.player.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                    if hammerHitsRound2:
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)

            if self.game.follower.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                    if hammerHitsRound2:
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)

            for entity in self.game.entities:
                if self.rect.colliderect(entity.rect):
                    if type(entity).__name__ == "Lightning":
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)
                    if self.imgRect.colliderect(entity.imgRect):
                        if type(entity).__name__ == "Fireball":
                            self.game.despawnList.append(self.ID)
                            if len(self.game.despawnList) > 13:
                                self.game.despawnList.remove(self.game.despawnList[0])
                            self.game.loadBattle(self.battle)

        if self.is_idle:
            chance = random.randrange(0, 200)
            if chance == 0:
                dir = random.randrange(0, 4)
                if dir == 0:
                    self.facing = "up"
                    self.vy = -self.speed
                elif dir == 1:
                    self.facing = "down"
                    self.vy = self.speed
                elif dir == 2:
                    self.facing = "left"
                    self.vx = -self.speed
                else:
                    self.facing = "right"
                    self.vx = self.speed
                self.startWalking()
            else:
                self.vx, self.vy = 0, 0
                if chance == 1:
                    self.currentFrame = 0
                    self.goToEyes()
        elif self.is_eyes:
            chance = random.randrange(0, 300)
            if chance == 0:
                self.currentFrame = 0
                self.facing = "down"
                self.leaveEyes()
        elif self.is_moving:
            self.rect.x += self.vx
            self.rect.y += self.vy

            for wall in self.game.walls:
                if pg.sprite.collide_rect(self, wall):
                    self.vx *= -1
                    self.vy *= -1
                    if self.facing == "up":
                        self.rect.top = wall.rect.bottom
                        self.rect.y += self.vy
                        self.facing = "down"
                    elif self.facing == "down":
                        self.rect.bottom = wall.rect.top
                        self.rect.y += self.vy
                        self.facing = "up"
                    elif self.facing == "left":
                        self.rect.left = wall.rect.right
                        self.rect.x += self.vx
                        self.facing = "right"
                    elif self.facing == "right":
                        self.rect.right = wall.rect.left
                        self.rect.x += self.vx
                        self.facing = "left"

            chance = random.randrange(0, 100)
            if chance == 0:
                self.giveUp()

        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx


class AnubooOverworld(StateMachine):
    idle = State("Idle", initial=True)
    moving = State("Moving")
    charge = State("Charge")
    fire = State("Fire")

    startWalking = idle.to(moving)
    giveUp = moving.to(idle)
    toFireIdle = idle.to(charge)
    toFireMove = moving.to(charge)
    toFire = charge.to(fire)
    stopFire = fire.to(idle)

    def init(self, game, x, y, battle, facing="down"):
        self.game = game
        self.game.sprites.append(self)
        self.game.enemies.append(self)
        self.loadImages()
        self.vx = 0
        self.vy = 0
        self.image = self.walkingFramesDown[0]
        self.currentFrame = random.randrange(len(self.walkingFramesDown))
        self.lastUpdate = 0
        self.facing = facing
        self.shadow = self.shadowFrame
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)
        self.alpha = 255
        self.speed = 2
        self.battle = battle
        self.newID = False
        self.id = -12

    def loadImages(self):
        sheet = spritesheet("sprites/anuboo.png", "sprites/anuboo.xml")

        self.walkingFramesUp = [sheet.getImageName("up.png")]

        self.walkingFramesDown = [sheet.getImageName("down.png")]

        self.walkingFramesLeft = [sheet.getImageName("left.png")]

        self.walkingFramesRight = [sheet.getImageName("right.png")]

        self.chargingFramesUp = [sheet.getImageName("charge_up_1.png"),
                                 sheet.getImageName("charge_up_2.png"),
                                 sheet.getImageName("charge_up_3.png"),
                                 sheet.getImageName("charge_up_4.png"),
                                 sheet.getImageName("charge_up_5.png"),
                                 sheet.getImageName("charge_up_6.png"),
                                 sheet.getImageName("charge_up_7.png"),
                                 sheet.getImageName("charge_up_8.png")]

        self.chargingFramesDown = [sheet.getImageName("charge_down_1.png"),
                                   sheet.getImageName("charge_down_2.png"),
                                   sheet.getImageName("charge_down_3.png"),
                                   sheet.getImageName("charge_down_4.png"),
                                   sheet.getImageName("charge_down_5.png"),
                                   sheet.getImageName("charge_down_6.png"),
                                   sheet.getImageName("charge_down_7.png"),
                                   sheet.getImageName("charge_down_8.png")]

        self.chargingFramesLeft = [sheet.getImageName("charge_left_1.png"),
                                   sheet.getImageName("charge_left_2.png"),
                                   sheet.getImageName("charge_left_3.png"),
                                   sheet.getImageName("charge_left_4.png"),
                                   sheet.getImageName("charge_left_5.png"),
                                   sheet.getImageName("charge_left_6.png"),
                                   sheet.getImageName("charge_left_7.png"),
                                   sheet.getImageName("charge_left_8.png")]

        self.chargingFramesRight = [sheet.getImageName("charge_right_1.png"),
                                    sheet.getImageName("charge_right_2.png"),
                                    sheet.getImageName("charge_right_3.png"),
                                    sheet.getImageName("charge_right_4.png"),
                                    sheet.getImageName("charge_right_5.png"),
                                    sheet.getImageName("charge_right_6.png"),
                                    sheet.getImageName("charge_right_7.png"),
                                    sheet.getImageName("charge_right_8.png")]

        self.shadowFrame = sheet.getImageName("shadow.png")

    def animate(self):
        now = pg.time.get_ticks()
        if self.is_moving:
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
        elif self.is_charge or self.is_fire:
            if self.facing == "down":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.chargingFramesDown):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.chargingFramesDown))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.chargingFramesDown[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "up":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.chargingFramesUp):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.chargingFramesUp))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.chargingFramesUp[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "left":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.chargingFramesLeft):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.chargingFramesLeft))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.chargingFramesLeft[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "right":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.chargingFramesRight):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.chargingFramesRight))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.chargingFramesRight[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
        else:
            if self.facing == "down":
                center = self.imgRect.center
                self.image = self.walkingFramesDown[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "up":
                center = self.imgRect.center
                self.image = self.walkingFramesUp[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "left":
                center = self.imgRect.center
                self.image = self.walkingFramesLeft[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "right":
                center = self.imgRect.center
                self.image = self.walkingFramesRight[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center

    def update(self):
        self.animate()

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
                    self.game.loadBattle(self.battle)

            hits = pg.sprite.collide_rect(self, self.game.follower)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self, self.game.followerCol)
                if hitsRound2:
                    self.game.despawnList.append(self.ID)
                    if len(self.game.despawnList) > 13:
                        self.game.despawnList.remove(self.game.despawnList[0])
                    self.game.loadBattle(self.battle)

            if self.game.player.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                    if hammerHitsRound2:
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)

            if self.game.follower.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                    if hammerHitsRound2:
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)

            for entity in self.game.entities:
                if self.rect.colliderect(entity.rect):
                    if type(entity).__name__ == "Lightning":
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle)
                    if self.imgRect.colliderect(entity.imgRect):
                        if type(entity).__name__ == "Fireball":
                            self.game.despawnList.append(self.ID)
                            if len(self.game.despawnList) > 13:
                                self.game.despawnList.remove(self.game.despawnList[0])
                            self.game.loadBattle(self.battle)

        if self.is_idle:
            chance = random.randrange(0, 100)
            if chance == 0:
                dir = random.randrange(0, 4)
                if dir == 0:
                    self.facing = "up"
                    self.vy = -self.speed
                elif dir == 1:
                    self.facing = "down"
                    self.vy = self.speed
                elif dir == 2:
                    self.facing = "left"
                    self.vx = -self.speed
                else:
                    self.facing = "right"
                    self.vx = self.speed
                self.startWalking()
            else:
                self.vx, self.vy = 0, 0
        elif self.is_moving:
            self.rect.x += self.vx
            self.rect.y += self.vy

            for wall in self.game.walls:
                if pg.sprite.collide_rect(self, wall):
                    self.vx *= -1
                    self.vy *= -1
                    if self.facing == "up":
                        self.rect.top = wall.rect.bottom
                        self.rect.y += self.vy
                        self.facing = "down"
                    elif self.facing == "down":
                        self.rect.bottom = wall.rect.top
                        self.rect.y += self.vy
                        self.facing = "up"
                    elif self.facing == "left":
                        self.rect.left = wall.rect.right
                        self.rect.x += self.vx
                        self.facing = "right"
                    elif self.facing == "right":
                        self.rect.right = wall.rect.left
                        self.rect.x += self.vx
                        self.facing = "left"

            chance = random.randrange(0, 100)
            if chance == 0:
                self.giveUp()
        elif self.is_charge:
            chance = random.randrange(0, 100)
            if chance == 0:
                self.toFire()
        elif self.is_fire:
            AnubooLazerOverworld(self.game, self.rect.center, self.battle, self.id)
            self.stopFire()

        if self.game.leader == "mario":
            if self.facing == "left":
                if self.game.player.rect.right < self.rect.left:
                    if self.rect.bottom > self.game.player.rect.top and self.game.player.rect.bottom < self.rect.top:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()
            elif self.facing == "right":
                if self.game.player.rect.left > self.rect.right:
                    if self.rect.bottom > self.game.player.rect.top and self.game.player.rect.bottom < self.rect.top:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()
            elif self.facing == "top":
                if self.game.player.rect.bottom < self.rect.top:
                    if self.rect.left > self.game.player.rect.left and self.game.player.rect.right < self.rect.right:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()
            elif self.facing == "bottom":
                if self.game.player.rect.top > self.rect.bottom:
                    if self.rect.left > self.game.player.rect.left and self.game.player.rect.right < self.rect.right:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()
        elif self.game.leader == "luigi":
            if self.facing == "left":
                if self.game.follower.rect.right < self.rect.left:
                    if self.rect.bottom > self.game.follower.rect.top and self.game.follower.rect.bottom < self.rect.top:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()
            elif self.facing == "right":
                if self.game.follower.rect.left > self.rect.right:
                    if self.rect.bottom > self.game.follower.rect.top and self.game.follower.rect.bottom < self.rect.top:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()
            elif self.facing == "top":
                if self.game.follower.rect.bottom < self.rect.top:
                    if self.rect.left > self.game.follower.rect.left and self.game.follower.rect.right < self.rect.right:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()
            elif self.facing == "bottom":
                if self.game.follower.rect.top > self.rect.bottom:
                    if self.rect.left > self.game.follower.rect.left and self.game.follower.rect.right < self.rect.right:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()

        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx


class AnubooLazerOverworld(pg.sprite.Sprite):
    def __init__(self, game, pos, battle, id):
        self.game = game
        self.game.sprites.append(self)
        sheet = spritesheet("sprites/anuboo.png", "sprites/anuboo.xml")
        self.rect = pg.rect.Rect(pos, (0, 0))
        if self.game.leader == "mario":
            self.angle = get_angle(self.rect.center, self.game.player.rect.center)
            self.image = pg.transform.rotate(sheet.getImageName("lazer_vertical.png"), math.degrees(
                math.atan2(self.game.player.rect.centerx - self.rect.centerx,
                           self.game.player.rect.centery - self.rect.centery)))
        elif self.game.leader == "luigi":
            self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
            self.image = pg.transform.rotate(sheet.getImageName("lazer_vertical.png"), math.degrees(
                math.atan2(self.game.follower.rect.centerx - self.rect.centerx,
                           self.game.follower.rect.centery - self.rect.centery)))
        self.lastUpdate = 0
        self.imgRect = self.image.get_rect()
        self.shadow = self.image.copy()
        self.shadow.fill((0, 0, 0, 255), special_flags=pg.BLEND_RGBA_MIN)
        self.shadow.set_alpha(150)
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.id = id
        self.imgRect.centerx, self.imgRect.bottom = self.rect.centerx, self.rect.top - 25
        self.alpha = 255
        self.speed = 4
        self.battle = battle

    def update(self):
        self.rect.center = project(self.rect.center, self.angle, self.speed)
        self.imgRect.centerx, self.imgRect.bottom = self.rect.centerx, self.rect.top - 25
        for wall in self.game.walls:
            if wall.rect.colliderect(self.rect):
                self.game.sprites.remove(self)

        hits = pg.sprite.collide_rect(self, self.game.player)
        if hits:
            hitsRound2 = pg.sprite.collide_rect(self, self.game.playerCol)
            if hitsRound2:
                self.game.despawnList.append(self.id)
                if len(self.game.despawnList) > 13:
                    self.game.despawnList.remove(self.game.despawnList[0])
                self.game.loadBattle(self.battle)

        hits = pg.sprite.collide_rect(self, self.game.follower)
        if hits:
            hitsRound2 = pg.sprite.collide_rect(self, self.game.followerCol)
            if hitsRound2:
                self.game.despawnList.append(self.id)
                if len(self.game.despawnList) > 13:
                    self.game.despawnList.remove(self.game.despawnList[0])
                self.game.loadBattle(self.battle)


class MagiblotOverworldR(StateMachine):
    idle = State("Idle", initial=True)
    other = State("other")

    trans = idle.to(other)

    def init(self, game, x, y, battle):
        self.game = game
        self.game.enemies.append(self)
        self.game.sprites.append(self)

        self.loadImages()
        self.alpha = 255
        self.speed = 4
        self.lastUpdate = 0
        self.currentFrame = 0
        self.image = self.idleImages[0]
        self.imgRect = self.image.get_rect()
        self.rect = self.image.get_rect()
        self.hpSpeed = 0
        self.rect.center = (x, y)
        self.battle = battle
        self.newID = False
        self.id = -12

    def loadImages(self):
        sheet = spritesheet("sprites/magiblot-red.png", "sprites/magiblot-red.xml")

        self.idleImages = [sheet.getImageName("idle_1.png"),
                           sheet.getImageName("idle_2.png"),
                           sheet.getImageName("idle_3.png"),
                           sheet.getImageName("idle_4.png"),
                           sheet.getImageName("idle_5.png"),
                           sheet.getImageName("idle_6.png"),
                           sheet.getImageName("idle_7.png"),
                           sheet.getImageName("idle_8.png"),
                           sheet.getImageName("idle_9.png"),
                           sheet.getImageName("idle_10.png"),
                           sheet.getImageName("idle_11.png"),
                           sheet.getImageName("idle_12.png"),
                           sheet.getImageName("idle_13.png"),
                           sheet.getImageName("idle_14.png"),
                           sheet.getImageName("idle_15.png"),
                           sheet.getImageName("idle_16.png"),
                           sheet.getImageName("idle_17.png"),
                           sheet.getImageName("idle_18.png"),
                           sheet.getImageName("idle_19.png"),
                           sheet.getImageName("idle_20.png"),
                           sheet.getImageName("idle_21.png"),
                           sheet.getImageName("idle_22.png"),
                           sheet.getImageName("idle_23.png"),
                           sheet.getImageName("idle_24.png"),
                           sheet.getImageName("idle_25.png"),
                           sheet.getImageName("idle_26.png"),
                           sheet.getImageName("idle_27.png"),
                           sheet.getImageName("idle_28.png"),
                           sheet.getImageName("idle_29.png"),
                           sheet.getImageName("idle_30.png"),
                           sheet.getImageName("idle_31.png"),
                           sheet.getImageName("idle_32.png"),
                           sheet.getImageName("idle_33.png"),
                           sheet.getImageName("idle_34.png"),
                           sheet.getImageName("idle_35.png"),
                           sheet.getImageName("idle_36.png"),
                           sheet.getImageName("idle_37.png"),
                           sheet.getImageName("idle_38.png"),
                           sheet.getImageName("idle_39.png"),
                           sheet.getImageName("idle_40.png"),
                           sheet.getImageName("idle_41.png"),
                           sheet.getImageName("idle_42.png"),
                           sheet.getImageName("idle_43.png"),
                           sheet.getImageName("idle_44.png"),
                           sheet.getImageName("idle_45.png"),
                           sheet.getImageName("idle_46.png"),
                           sheet.getImageName("idle_47.png"),
                           sheet.getImageName("idle_48.png"),
                           sheet.getImageName("idle_49.png"),
                           sheet.getImageName("idle_50.png"),
                           sheet.getImageName("idle_51.png"),
                           sheet.getImageName("idle_52.png"),
                           sheet.getImageName("idle_53.png"),
                           sheet.getImageName("idle_54.png"),
                           sheet.getImageName("idle_55.png"),
                           sheet.getImageName("idle_56.png"),
                           sheet.getImageName("idle_57.png"),
                           sheet.getImageName("idle_58.png"),
                           sheet.getImageName("idle_59.png"),
                           sheet.getImageName("idle_60.png"),
                           sheet.getImageName("idle_61.png")]

    def update(self):
        self.animate()
        self.imgRect = self.rect

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
                    self.game.loadBattle(self.battle, stopMusic=False)

            hits = pg.sprite.collide_rect(self, self.game.follower)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self, self.game.followerCol)
                if hitsRound2:
                    self.game.despawnList.append(self.ID)
                    if len(self.game.despawnList) > 13:
                        self.game.despawnList.remove(self.game.despawnList[0])
                    self.game.loadBattle(self.battle, stopMusic=False)

            if self.game.player.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                    if hammerHitsRound2:
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle, stopMusic=False)

            if self.game.follower.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                    if hammerHitsRound2:
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle, stopMusic=False)

            for entity in self.game.entities:
                if self.rect.colliderect(entity.rect):
                    if type(entity).__name__ == "Lightning":
                        self.game.despawnList.append(self.ID)
                        if len(self.game.despawnList) > 13:
                            self.game.despawnList.remove(self.game.despawnList[0])
                        self.game.loadBattle(self.battle, stopMusic=False)
                    if self.imgRect.colliderect(entity.imgRect):
                        if type(entity).__name__ == "Fireball":
                            self.game.despawnList.append(self.ID)
                            if len(self.game.despawnList) > 13:
                                self.game.despawnList.remove(self.game.despawnList[0])
                            self.game.loadBattle(self.battle, stopMusic=False)

    def animate(self):
        if self.is_idle:
            if self.currentFrame < len(self.idleImages):
                self.currentFrame = (self.currentFrame + 1) % (len(self.idleImages))
            else:
                self.currentFrame = 0
            bottom = self.rect.bottom
            left = self.rect.left
            self.image = self.idleImages[self.currentFrame]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
            self.rect.left = left


class Goomba(pg.sprite.Sprite):
    def __init__(self, game, x, y, vx, vy, facing="down"):
        pg.sprite.Sprite.__init__(self)
        self.vx = vx
        self.vy = vy
        self.game = game
        self.hit = False
        self.hitTimer = 0
        self.going = True
        self.dead = False
        self.game.sprites.append(self)
        self.game.enemies.append(self)
        self.loadImages()
        self.image = self.walkingFramesDown[0]
        self.currentFrame = random.randrange(len(self.walkingFramesDown))
        self.lastUpdate = 0
        self.facing = facing
        self.shadow = self.shadowFrame
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)
        self.alpha = 255
        self.speed = 0
        self.mask = pg.mask.from_surface(self.image)
        self.textbox = None

        # Stats
        self.stats = {"maxHP": 4, "hp": 4, "pow": 10, "def": 5, "exp": 1, "coins": 3, "name": "Goomba"}
        self.rectHP = self.stats["hp"]

        self.description = []
        self.description.append("That's a Goomba!")
        self.description.append("These little guys will run\nback and forth across the screen\nand hope they hit you.")
        self.description.append("Max HP is " + str(self.stats["maxHP"]) + ",/p\nAttack is " + str(
            self.stats["pow"]) + ",/p\nDefence is " + str(self.stats["def"]) + ".")
        self.description.append('''The main motto of the Goomba is\n"March straight ahead into\nthe enemy's feet".''')
        self.description.append("Or,/5 at least that's what Bowser\nsays.")

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
        if self.going:
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

    def hpMath(self):
        if self.rectHP > self.stats["hp"] and self.speed == 0:
            self.speed = ((self.rectHP - self.stats["hp"]) / 30) * -1
        elif self.rectHP < self.stats["hp"] and self.speed == 0:
            self.speed = (self.stats["hp"] - self.rectHP) / 30

        if self.speed != 0:
            if self.rectHP > self.stats["hp"] and self.speed < 0:
                self.rectHP += self.speed
            elif self.rectHP < self.stats["hp"] and self.speed > 0:
                self.rectHP += self.speed
            else:
                self.rectHP = self.stats["hp"]
                self.speed = 0

    def update(self):
        self.animate()

        self.hpMath()

        if self.stats["hp"] <= 0:
            self.going = False
            self.alpha -= 10

        if self.alpha <= 0:
            self.game.battleCoins += self.stats["coins"]
            self.game.battleXp += self.stats["exp"]
            self.game.sprites.remove(self)
            self.game.enemies.remove(self)

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
            self.going = False
            if self.hitTimer > 20:
                self.going = True
                self.hit = False
                self.hitTimer = 0

        if self.game.player.stats["hp"] != 0:
            hits = pg.sprite.collide_rect(self.game.player, self)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                if keys[
                    pg.K_m] and self.game.player.going == "down" and self.game.player.rect.bottom <= self.imgRect.top + 50:
                    doubleDamageM = True
                if hitsRound2:
                    if self.game.player.going == "down" and self.game.player.jumping and self.stats["hp"] > 0:
                        if doubleDamageM:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (max(2 * (self.game.player.stats["pow"] - self.stats["def"]), 0)))
                            self.stats["hp"] -= (max(2 * (self.game.player.stats["pow"] - self.stats["def"]), 0))
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                        else:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (max(self.game.player.stats["pow"] - self.stats["def"], 0)))
                            self.stats["hp"] -= (max(self.game.player.stats["pow"] - self.stats["def"], 0))
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                        self.game.player.airTimer = 0
                    else:
                        if not self.game.player.hit and self.stats[
                            "hp"] > 0 and not self.hit and self.game.player.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.player.rect.left, self.game.player.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                            self.game.player.stats["hp"] -= (max(self.stats["pow"] - self.game.player.stats["def"], 1))
                            if self.game.player.stats["hp"] <= 0:
                                self.game.player.stats["hp"] = 0
                                self.game.player.currentFrame = 0
                            self.game.player.hitTime = pg.time.get_ticks()
                            self.game.playerHitSound.play()
                            self.game.player.canBeHit = False
                            self.game.player.hit = True

        if self.game.follower.stats["hp"] != 0:
            luigiHits = pg.sprite.collide_rect(self.game.follower, self)
            if luigiHits:
                hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                if keys[
                    pg.K_l] and self.game.follower.going == "down" and self.game.follower.rect.bottom <= self.imgRect.top + 50:
                    doubleDamageL = True
                if hitsRound2:
                    if self.game.follower.going == "down" and self.game.follower.jumping and self.stats["hp"] > 0:
                        if doubleDamageL:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 0)))
                            self.stats["hp"] -= (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 0))
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                        else:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (max(self.game.follower.stats["pow"] - self.stats["def"], 0)))
                            self.stats["hp"] -= (max(self.game.follower.stats["pow"] - self.stats["def"], 0))
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                        self.game.follower.airTimer = 0
                    else:
                        if not self.game.follower.hit and self.stats[
                            "hp"] > 0 and not self.hit and self.game.follower.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                            self.game.follower.stats["hp"] -= (
                                max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                            if self.game.follower.stats["hp"] <= 0:
                                self.game.follower.stats["hp"] = 0
                                self.game.follower.currentFrame = 0
                            self.game.follower.hitTime = pg.time.get_ticks()
                            self.game.playerHitSound.play()
                            self.game.follower.canBeHit = False
                            self.game.follower.hit = True

        if self.stats["hp"] != 0 and self.game.player.isHammer is not None:
            hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
            if hammerHits:
                hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                if hammerHitsRound2 and not self.hit and self.stats["hp"] > 0:
                    HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                               max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 0))
                    self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 0)
                    if self.stats["hp"] <= 0:
                        self.game.enemyDieSound.play()
                    self.game.enemyHitSound.play()
                    self.hit = True

        if self.stats["hp"] != 0 and self.game.follower.isHammer is not None:
            hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
            if hammerHits:
                hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                if hammerHitsRound2 and not self.hit and self.stats["hp"] > 0:
                    HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                               max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 0))
                    self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 0)
                    if self.stats["hp"] <= 0:
                        self.game.enemyDieSound.play()
                    self.game.enemyHitSound.play()
                    self.hit = True

        for entity in self.game.entities:
            if self.rect.colliderect(entity.rect) and not self.hit and self.stats["hp"] > 0:
                if type(entity).__name__ == "Lightning":
                    HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                               max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 0))
                    self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 0)
                    if self.stats["hp"] <= 0:
                        self.game.enemyDieSound.play()
                    self.game.enemyHitSound.play()
                    self.hit = True
                if self.imgRect.colliderect(entity.imgRect):
                    if type(entity).__name__ == "Fireball":
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 0))
                        self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 0)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        self.hit = True
                        entity.dead = True


class Koopa(StateMachine):
    idle = State("Idle", initial=True)
    toShell = State("To Shell")
    shell = State("Shell")
    leaveShell = State("Leave Shell")
    hit = State("Hit")

    goInside = idle.to(toShell)
    startSpin = toShell.to(shell)
    stopSpin = shell.to(leaveShell)
    standUp = leaveShell.to(idle)
    hitShell = hit.to(toShell)
    getHurt = idle.to(hit)
    getHurtShell = shell.to(hit)

    def init(self, game, pos):
        self.game = game
        self.game.enemies.append(self)
        self.game.sprites.append(self)

        self.loadImages()
        self.alpha = 255
        self.speed = 10
        self.lastUpdate = 0
        self.currentFrame = 0
        self.hitTimer = 0
        self.dead = False
        self.hit = False
        self.facing = "down"
        self.image = self.standingFrames["down"]
        self.imgRect = self.image.get_rect()
        self.shadow = self.shadowFrame
        self.rect = self.shadow.get_rect()
        self.hpSpeed = 0
        self.rect.center = pos
        self.imgRect.centerx = self.rect.centerx + 5
        self.imgRect.bottom = self.rect.centery + 10

        # Stats
        self.stats = {"maxHP": 10, "hp": 10, "pow": 12, "def": 7, "exp": 2, "coins": 3, "name": "Koopa"}
        self.rectHP = self.stats["hp"]

        self.description = ["That's a Koopa Troopa!",
                            "Koopas just stand there./p\nMenacingly.",
                            "After a while, they go into their\nshells and go after you.",
                            "While their in their shells, you\ncan't hit them.",
                            "Max HP is " + str(self.stats["maxHP"]) + ",/p\nAttack is " + str(
                                self.stats["pow"]) + ",/p\nDefence is " + str(self.stats["def"]) + ".",
                            "The Koopa Troop is Bowser's favorite\ncorps of the Bowser Baddies."]

    def loadImages(self):
        sheet = spritesheet("sprites/koopa.png", "sprites/koopa.xml")

        self.inShellFrames = [sheet.getImageName("inShell_1.png"),
                              sheet.getImageName("inShell_2.png"),
                              sheet.getImageName("inShell_3.png"),
                              sheet.getImageName("inShell_4.png"),
                              sheet.getImageName("inShell_5.png"),
                              sheet.getImageName("inShell_6.png"),
                              sheet.getImageName("inShell_7.png"),
                              sheet.getImageName("inShell_8.png")]

        self.toShellFramesUp = [sheet.getImageName("toShell_up_1.png"),
                                sheet.getImageName("toShell_up_2.png"),
                                sheet.getImageName("toShell_up_3.png"),
                                sheet.getImageName("toShell_up_4.png"),
                                sheet.getImageName("toShell_up_5.png")]

        self.toShellFramesDown = [sheet.getImageName("toShell_down_1.png"),
                                  sheet.getImageName("toShell_down_2.png"),
                                  sheet.getImageName("toShell_down_3.png"),
                                  sheet.getImageName("toShell_down_4.png"),
                                  sheet.getImageName("toShell_down_5.png")]

        self.toShellFramesLeft = [sheet.getImageName("toShell_left_1.png"),
                                  sheet.getImageName("toShell_left_2.png"),
                                  sheet.getImageName("toShell_left_3.png"),
                                  sheet.getImageName("toShell_left_4.png"),
                                  sheet.getImageName("toShell_left_5.png")]

        self.toShellFramesRight = [sheet.getImageName("toShell_right_1.png"),
                                   sheet.getImageName("toShell_right_2.png"),
                                   sheet.getImageName("toShell_right_3.png"),
                                   sheet.getImageName("toShell_right_4.png"),
                                   sheet.getImageName("toShell_right_5.png")]

        self.walkingFramesUp = [sheet.getImageName("walking_up_1.png"),
                                sheet.getImageName("walking_up_2.png"),
                                sheet.getImageName("walking_up_3.png"),
                                sheet.getImageName("walking_up_4.png"),
                                sheet.getImageName("walking_up_5.png"),
                                sheet.getImageName("walking_up_6.png"),
                                sheet.getImageName("walking_up_7.png"),
                                sheet.getImageName("walking_up_8.png"),
                                sheet.getImageName("walking_up_9.png"),
                                sheet.getImageName("walking_up_10.png")]

        self.walkingFramesDown = [sheet.getImageName("walking_down_1.png"),
                                  sheet.getImageName("walking_down_2.png"),
                                  sheet.getImageName("walking_down_3.png"),
                                  sheet.getImageName("walking_down_4.png"),
                                  sheet.getImageName("walking_down_5.png"),
                                  sheet.getImageName("walking_down_6.png"),
                                  sheet.getImageName("walking_down_7.png"),
                                  sheet.getImageName("walking_down_8.png"),
                                  sheet.getImageName("walking_down_9.png"),
                                  sheet.getImageName("walking_down_10.png")]

        self.walkingFramesLeft = [sheet.getImageName("walking_left_1.png"),
                                  sheet.getImageName("walking_left_2.png"),
                                  sheet.getImageName("walking_left_3.png"),
                                  sheet.getImageName("walking_left_4.png"),
                                  sheet.getImageName("walking_left_5.png"),
                                  sheet.getImageName("walking_left_6.png"),
                                  sheet.getImageName("walking_left_7.png"),
                                  sheet.getImageName("walking_left_8.png"),
                                  sheet.getImageName("walking_left_9.png"),
                                  sheet.getImageName("walking_left_10.png")]

        self.walkingFramesRight = [sheet.getImageName("walking_right_1.png"),
                                   sheet.getImageName("walking_right_2.png"),
                                   sheet.getImageName("walking_right_3.png"),
                                   sheet.getImageName("walking_right_4.png"),
                                   sheet.getImageName("walking_right_5.png"),
                                   sheet.getImageName("walking_right_6.png"),
                                   sheet.getImageName("walking_right_7.png"),
                                   sheet.getImageName("walking_right_8.png"),
                                   sheet.getImageName("walking_right_9.png"),
                                   sheet.getImageName("walking_right_10.png")]

        self.standingFrames = {"up": sheet.getImageName("standing_up.png"),
                               "down": sheet.getImageName("standing_down.png"),
                               "left": sheet.getImageName("standing_left.png"),
                               "right": sheet.getImageName("standing_right.png")
                               }

        self.shadowFrame = sheet.getImageName("shadow.png")

    def hpMath(self):
        if self.rectHP > self.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = ((self.rectHP - self.stats["hp"]) / 30) * -1
        elif self.rectHP < self.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = (self.stats["hp"] - self.rectHP) / 30

        if self.hpSpeed != 0:
            if self.rectHP + self.hpSpeed > self.stats["hp"] and self.hpSpeed < 0:
                self.rectHP += self.hpSpeed
            elif self.rectHP + self.hpSpeed < self.stats["hp"] and self.hpSpeed > 0:
                self.rectHP += self.hpSpeed
            else:
                self.rectHP = self.stats["hp"]
                self.hpSpeed = 0

    def update(self):
        self.animate()
        self.hpMath()

        if self.stats["hp"] > 0:
            if self.is_idle:
                chance = random.randrange(0, 200)
                self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
                if chance == 0:
                    if self.game.leader == "mario":
                        self.angle = get_angle(self.rect.center, self.game.player.rect.center)
                    else:
                        self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
                    self.currentFrame = 0
                    self.goInside()
            elif self.is_shell:
                self.rect.center = project(self.rect.center, self.angle, self.speed)
                for wall in self.game.walls:
                    if wall.rect.colliderect(self.rect):
                        if self.game.leader == "mario":
                            self.angle = get_angle(self.rect.center, self.game.player.rect.center)
                        elif self.game.leader == "luigi":
                            self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
                        self.rect.center = project(self.rect.center, self.angle, self.speed)
                chance = random.randrange(0, 200)
                if chance == 0:
                    choice = random.randrange(0, 4)
                    if choice == 0:
                        self.facing = "up"
                    elif choice == 1:
                        self.facing = "down"
                    elif choice == 2:
                        self.facing = "left"
                    elif choice == 3:
                        self.facing = "right"
                    self.currentFrame = len(self.toShellFramesDown) - 1
                    self.stopSpin()
            elif self.is_hit:
                self.hit = False
                self.hitShell()
            if self.hit:
                if self.is_idle:
                    self.getHurt()
                elif self.is_shell:
                    self.getHurtShell()

        keys = pg.key.get_pressed()
        doubleDamageM = False
        doubleDamageL = False

        if self.is_idle:
            if self.game.player.stats["hp"] != 0:
                hits = pg.sprite.collide_rect(self.game.player, self)
                if hits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                    if keys[
                        pg.K_m] and self.game.player.going == "down" and self.game.player.rect.bottom <= self.imgRect.top + 50:
                        doubleDamageM = True
                    if hitsRound2:
                        if self.game.player.going == "down" and self.game.player.jumping and self.stats["hp"] > 0:
                            if doubleDamageM:
                                HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                           (max(2 * (self.game.player.stats["pow"] - self.stats["def"]), 1)))
                                self.stats["hp"] -= (max(2 * (self.game.player.stats["pow"] - self.stats["def"]), 1))
                                if self.stats["hp"] <= 0:
                                    self.game.enemyDieSound.play()
                                self.game.enemyHitSound.play()
                                self.hit = True
                            else:
                                HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                           (max(self.game.player.stats["pow"] - self.stats["def"], 1)))
                                self.stats["hp"] -= (max(self.game.player.stats["pow"] - self.stats["def"], 1))
                                if self.stats["hp"] <= 0:
                                    self.game.enemyDieSound.play()
                                self.game.enemyHitSound.play()
                                self.hit = True
                            self.game.player.airTimer = 0
                        else:
                            if not self.game.player.hit and self.stats[
                                "hp"] > 0 and not self.hit and self.game.player.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.player.rect.left, self.game.player.rect.top - 2),
                                           (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                                self.game.player.stats["hp"] -= (
                                    max(self.stats["pow"] - self.game.player.stats["def"], 1))
                                if self.game.player.stats["hp"] <= 0:
                                    self.game.player.stats["hp"] = 0
                                    self.game.player.currentFrame = 0
                                self.game.player.hitTime = pg.time.get_ticks()
                                self.game.playerHitSound.play()
                                self.game.player.canBeHit = False
                                self.game.player.hit = True

            if self.game.follower.stats["hp"] != 0:
                luigiHits = pg.sprite.collide_rect(self.game.follower, self)
                if luigiHits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                    if keys[
                        pg.K_l] and self.game.follower.going == "down" and self.game.follower.rect.bottom <= self.imgRect.top + 50:
                        doubleDamageL = True
                    if hitsRound2:
                        if self.game.follower.going == "down" and self.game.follower.jumping and self.stats["hp"] > 0:
                            if doubleDamageL:
                                HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                           (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 1)))
                                self.stats["hp"] -= (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 1))
                                if self.stats["hp"] <= 0:
                                    self.game.enemyDieSound.play()
                                self.game.enemyHitSound.play()
                                self.hit = True
                            else:
                                HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                           (max(self.game.follower.stats["pow"] - self.stats["def"], 1)))
                                self.stats["hp"] -= (max(self.game.follower.stats["pow"] - self.stats["def"], 1))
                                if self.stats["hp"] <= 0:
                                    self.game.enemyDieSound.play()
                                self.game.enemyHitSound.play()
                                self.hit = True
                            self.game.follower.airTimer = 0
                        else:
                            if not self.game.follower.hit and self.stats[
                                "hp"] > 0 and not self.hit and self.game.follower.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                           (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                                self.game.follower.stats["hp"] -= (
                                    max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                                if self.game.follower.stats["hp"] <= 0:
                                    self.game.follower.stats["hp"] = 0
                                    self.game.follower.currentFrame = 0
                                self.game.follower.hitTime = pg.time.get_ticks()
                                self.game.playerHitSound.play()
                                self.game.follower.canBeHit = False
                                self.game.follower.hit = True

            if self.stats["hp"] != 0 and self.game.player.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                    if hammerHitsRound2 and not self.hit and self.stats["hp"] > 0:
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 0))
                        self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 0)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        self.hit = True

            if self.stats["hp"] != 0 and self.game.follower.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                    if hammerHitsRound2 and not self.hit and self.stats["hp"] > 0:
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1))
                        self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        self.hit = True

            for entity in self.game.entities:
                if self.rect.colliderect(entity.rect) and not self.hit and self.stats["hp"] > 0:
                    if type(entity).__name__ == "Lightning":
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 1))
                        self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 1)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        self.hit = True
                    if self.imgRect.colliderect(entity.imgRect):
                        if type(entity).__name__ == "Fireball":
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1))
                            self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1)
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                            entity.dead = True
        else:
            if self.game.player.stats["hp"] != 0:
                hits = pg.sprite.collide_rect(self.game.player, self)
                if hits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                    if hitsRound2:
                        if not self.game.player.hit and self.stats[
                            "hp"] > 0 and not self.hit and self.game.player.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.player.rect.left, self.game.player.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                            self.game.player.stats["hp"] -= (
                                max(self.stats["pow"] - self.game.player.stats["def"], 1))
                            if self.game.player.stats["hp"] <= 0:
                                self.game.player.stats["hp"] = 0
                                self.game.player.currentFrame = 0
                            self.game.player.hitTime = pg.time.get_ticks()
                            self.game.playerHitSound.play()
                            self.game.player.canBeHit = False
                            self.game.player.hit = True

            if self.game.follower.stats["hp"] > 0:
                luigiHits = pg.sprite.collide_rect(self.game.follower, self)
                if luigiHits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                    if keys[
                        pg.K_l] and self.game.follower.going == "down" and self.game.follower.rect.bottom <= self.imgRect.top + 50:
                        doubleDamageL = True
                    if hitsRound2:
                        if self.game.follower.stats["hp"] != 0:
                            if not self.game.follower.hit and self.stats[
                                "hp"] > 0 and not self.hit and self.game.follower.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                           (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                                self.game.follower.stats["hp"] -= (
                                    max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                                if self.game.follower.stats["hp"] <= 0:
                                    self.game.follower.stats["hp"] = 0
                                    self.game.follower.currentFrame = 0
                                self.game.follower.hitTime = pg.time.get_ticks()
                                self.game.playerHitSound.play()
                                self.game.follower.canBeHit = False
                                self.game.follower.hit = True

        if self.stats["hp"] <= 0:
            self.alpha -= 10

        if self.alpha <= 0:
            self.game.battleXp += self.stats["exp"]
            self.game.battleCoins += self.stats["coins"]
            self.game.sprites.remove(self)
            self.game.enemies.remove(self)

        self.imgRect.centerx = self.rect.centerx
        self.imgRect.bottom = self.rect.centery + 5

    def animate(self):
        now = pg.time.get_ticks()
        if self.is_toShell:
            if self.facing == "down":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.toShellFramesDown) - 1:
                        self.currentFrame = (self.currentFrame + 1) % (len(self.toShellFramesDown))
                    else:
                        self.startSpin()
                    center = self.imgRect.center
                    self.image = self.toShellFramesDown[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "up":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.toShellFramesUp) - 1:
                        self.currentFrame = (self.currentFrame + 1) % (len(self.toShellFramesUp))
                    else:
                        self.startSpin()
                    center = self.imgRect.center
                    self.image = self.toShellFramesUp[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "left":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.toShellFramesLeft) - 1:
                        self.currentFrame = (self.currentFrame + 1) % (len(self.toShellFramesLeft))
                    else:
                        self.startSpin()
                    center = self.imgRect.center
                    self.image = self.toShellFramesLeft[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "right":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.toShellFramesDown) - 1:
                        self.currentFrame = (self.currentFrame + 1) % (len(self.toShellFramesDown))
                    else:
                        self.startSpin()
                    center = self.imgRect.center
                    self.image = self.toShellFramesDown[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
        elif self.is_shell:
            if now - self.lastUpdate > 30:
                self.lastUpdate = now
                if self.currentFrame < len(self.inShellFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.inShellFrames))
                else:
                    self.currentFrame = 0
                center = self.imgRect.center
                self.image = self.inShellFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.is_leaveShell:
            if self.facing == "down":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame > 0:
                        self.currentFrame = (self.currentFrame - 1)
                    else:
                        self.standUp()
                    center = self.imgRect.center
                    self.image = self.toShellFramesDown[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "up":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame > 0:
                        self.currentFrame = (self.currentFrame - 1)
                    else:
                        self.standUp()
                    center = self.imgRect.center
                    self.image = self.toShellFramesUp[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "left":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame > 0:
                        self.currentFrame = (self.currentFrame - 1)
                    else:
                        self.standUp()
                    center = self.imgRect.center
                    self.image = self.toShellFramesLeft[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "right":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame > 0:
                        self.currentFrame = (self.currentFrame - 1)
                    else:
                        self.standUp()
                    center = self.imgRect.center
                    self.image = self.toShellFramesRight[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
        else:
            if self.facing == "down":
                center = self.imgRect.center
                self.image = self.walkingFramesDown[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "up":
                center = self.imgRect.center
                self.image = self.walkingFramesUp[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "left":
                center = self.imgRect.center
                self.image = self.walkingFramesLeft[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "right":
                center = self.imgRect.center
                self.image = self.walkingFramesRight[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center


class Sandoon(StateMachine):
    idle = State("Idle", initial=True)
    moving = State("Moving")
    toEyes = State("To Eyes")
    fromEyes = State("From Eyes")
    eyes = State("Eyes")

    startWalking = idle.to(moving)
    giveUp = moving.to(idle)
    goToEyes = idle.to(toEyes)
    reachEyes = toEyes.to(eyes)
    leaveEyes = eyes.to(fromEyes)
    finishEyes = fromEyes.to(idle)

    def init(self, game, x, y, facing="down"):
        self.game = game
        self.game.sprites.append(self)
        self.game.enemies.append(self)
        self.loadImages()
        self.vx = 0
        self.vy = 0
        self.image = self.walkingFramesDown[0]
        self.currentFrame = random.randrange(len(self.walkingFramesDown))
        self.lastUpdate = 0
        self.facing = facing
        self.shadow = self.shadowFrames["Normal"]
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)
        self.hit = False
        self.hitTimer = 0
        self.dead = False
        self.alpha = 255
        self.speed = 4
        self.hpSpeed = 0

        # Stats
        self.stats = {"maxHP": 30, "hp": 30, "pow": 30, "def": 23, "exp": 5, "coins": 7, "name": "Sandoon"}
        self.rectHP = self.stats["hp"]

        self.description = ["That's a Sandoon!",
                            "Sandoons just wander around, and\nlike to hide in the sand,/p where\nthey're invincible.",
                            "Max HP is " + str(self.stats["maxHP"]) + ",/p\nAttack is " + str(
                                self.stats["pow"]) + ",/p\nDefence is " + str(self.stats["def"]) + ".",
                            "Sandoons are native to Pi'illo Island.",
                            "How they made it here is beyond me."]

    def loadImages(self):
        sheet = spritesheet("sprites/sandoon overworld.png", "sprites/sandoon overworld.xml")

        self.walkingFramesUp = [sheet.getImageName("idle_up_1.png"),
                                sheet.getImageName("idle_up_2.png"),
                                sheet.getImageName("idle_up_3.png"),
                                sheet.getImageName("idle_up_4.png")]

        self.walkingFramesDown = [sheet.getImageName("idle_down_1.png"),
                                  sheet.getImageName("idle_down_2.png"),
                                  sheet.getImageName("idle_down_3.png"),
                                  sheet.getImageName("idle_down_4.png")]

        self.walkingFramesLeft = [sheet.getImageName("idle_left_1.png"),
                                  sheet.getImageName("idle_left_2.png"),
                                  sheet.getImageName("idle_left_3.png"),
                                  sheet.getImageName("idle_left_4.png")]

        self.walkingFramesRight = [sheet.getImageName("idle_right_1.png"),
                                   sheet.getImageName("idle_right_2.png"),
                                   sheet.getImageName("idle_right_3.png"),
                                   sheet.getImageName("idle_right_4.png")]

        self.toEyesFrames = [sheet.getImageName("to_eyes_1.png"),
                             sheet.getImageName("to_eyes_2.png"),
                             sheet.getImageName("to_eyes_3.png"),
                             sheet.getImageName("to_eyes_4.png"),
                             sheet.getImageName("to_eyes_5.png"),
                             sheet.getImageName("to_eyes_6.png"),
                             sheet.getImageName("to_eyes_7.png"),
                             sheet.getImageName("to_eyes_8.png"),
                             sheet.getImageName("to_eyes_9.png"),
                             sheet.getImageName("to_eyes_10.png"),
                             sheet.getImageName("to_eyes_11.png"),
                             sheet.getImageName("to_eyes_12.png"),
                             sheet.getImageName("to_eyes_13.png")]

        self.fromEyesFrames = [sheet.getImageName("from_eyes_1.png"),
                               sheet.getImageName("from_eyes_2.png"),
                               sheet.getImageName("from_eyes_3.png"),
                               sheet.getImageName("from_eyes_4.png"),
                               sheet.getImageName("from_eyes_5.png"),
                               sheet.getImageName("from_eyes_6.png"),
                               sheet.getImageName("from_eyes_7.png"),
                               sheet.getImageName("from_eyes_8.png"),
                               sheet.getImageName("from_eyes_9.png"),
                               sheet.getImageName("from_eyes_10.png"),
                               sheet.getImageName("from_eyes_11.png"),
                               sheet.getImageName("from_eyes_12.png")]

        self.eyeFrames = [sheet.getImageName("eyes_1.png"),
                          sheet.getImageName("eyes_2.png"),
                          sheet.getImageName("eyes_3.png"),
                          sheet.getImageName("eyes_4.png"),
                          sheet.getImageName("eyes_5.png"),
                          sheet.getImageName("eyes_6.png"),
                          sheet.getImageName("eyes_7.png"),
                          sheet.getImageName("eyes_8.png"),
                          sheet.getImageName("eyes_9.png"),
                          sheet.getImageName("eyes_10.png"),
                          sheet.getImageName("eyes_11.png"),
                          sheet.getImageName("eyes_12.png"),
                          sheet.getImageName("eyes_13.png"),
                          sheet.getImageName("eyes_14.png"),
                          sheet.getImageName("eyes_15.png"),
                          sheet.getImageName("eyes_16.png"),
                          sheet.getImageName("eyes_17.png")]

        self.shadowFrames = {"Normal": sheet.getImageName("shadow.png"), "Eyes": sheet.getImageName("eyeShadow.png")}

    def hpMath(self):
        if self.rectHP > self.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = ((self.rectHP - self.stats["hp"]) / 30) * -1
        elif self.rectHP < self.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = (self.stats["hp"] - self.rectHP) / 30

        if self.hpSpeed != 0:
            if self.rectHP + self.hpSpeed > self.stats["hp"] and self.hpSpeed < 0:
                self.rectHP += self.hpSpeed
            elif self.rectHP + self.hpSpeed < self.stats["hp"] and self.hpSpeed > 0:
                self.rectHP += self.hpSpeed
            else:
                self.rectHP = self.stats["hp"]
                self.hpSpeed = 0

    def animate(self):
        now = pg.time.get_ticks()
        if self.is_toEyes:
            if now - self.lastUpdate > 60:
                if self.shadow != self.shadowFrames["Eyes"]:
                    self.shadow = self.shadowFrames["Eyes"]
                    bottom = self.rect.bottom
                    centerx = self.rect.centerx
                    self.rect = self.shadow.get_rect()
                    self.rect.centerx = centerx
                    self.rect.bottom = bottom
                self.lastUpdate = now
                if self.currentFrame < len(self.toEyesFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1) % (len(self.toEyesFrames))
                else:
                    self.reachEyes()
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                self.image = self.toEyesFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        elif self.is_eyes:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.eyeFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.eyeFrames))
                else:
                    self.currentFrame = 0
                center = self.imgRect.center
                self.image = self.eyeFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.is_fromEyes:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.fromEyesFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1) % (len(self.fromEyesFrames))
                else:
                    self.finishEyes()
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                self.image = self.fromEyesFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        else:
            if self.shadow != self.shadowFrames["Normal"]:
                self.shadow = self.shadowFrames["Normal"]
                bottom = self.rect.bottom
                centerx = self.rect.centerx
                self.rect = self.shadow.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom
            if self.facing == "down":
                if now - self.lastUpdate > 60:
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
                if now - self.lastUpdate > 60:
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
                if now - self.lastUpdate > 60:
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
                if now - self.lastUpdate > 60:
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
        self.hpMath()
        self.animate()
        keys = pg.key.get_pressed()

        if not self.is_eyes:
            if self.game.player.stats["hp"] != 0:
                doubleDamageM = False
                hits = pg.sprite.collide_rect(self.game.player, self)
                if hits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                    if keys[
                        pg.K_m] and self.game.player.going == "down" and self.game.player.rect.bottom <= self.imgRect.top + 50:
                        doubleDamageM = True
                    if hitsRound2:
                        if self.game.player.going == "down" and self.game.player.jumping and self.stats["hp"] > 0:
                            if doubleDamageM:
                                HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                           (max(2 * (self.game.player.stats["pow"] - self.stats["def"]), 1)))
                                self.stats["hp"] -= (max(2 * (self.game.player.stats["pow"] - self.stats["def"]), 1))
                                if self.stats["hp"] <= 0:
                                    self.game.enemyDieSound.play()
                                self.game.enemyHitSound.play()
                                self.hit = True
                            else:
                                HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                           (max(self.game.player.stats["pow"] - self.stats["def"], 1)))
                                self.stats["hp"] -= (max(self.game.player.stats["pow"] - self.stats["def"], 1))
                                if self.stats["hp"] <= 0:
                                    self.game.enemyDieSound.play()
                                self.game.enemyHitSound.play()
                                self.hit = True
                            self.game.player.airTimer = 0
                        else:
                            if not self.game.player.hit and self.stats[
                                "hp"] > 0 and not self.hit and self.game.player.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.player.rect.left, self.game.player.rect.top - 2),
                                           (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                                self.game.player.stats["hp"] -= (
                                    max(self.stats["pow"] - self.game.player.stats["def"], 1))
                                if self.game.player.stats["hp"] <= 0:
                                    self.game.player.stats["hp"] = 0
                                    self.game.player.currentFrame = 0
                                self.game.player.hitTime = pg.time.get_ticks()
                                self.game.playerHitSound.play()
                                self.game.player.canBeHit = False
                                self.game.player.hit = True

            if self.game.follower.stats["hp"] != 0:
                luigiHits = pg.sprite.collide_rect(self.game.follower, self)
                if luigiHits:
                    doubleDamageL = False
                    hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                    if keys[
                        pg.K_l] and self.game.follower.going == "down" and self.game.follower.rect.bottom <= self.imgRect.top + 50:
                        doubleDamageL = True
                    if hitsRound2:
                        if self.game.follower.going == "down" and self.game.follower.jumping and self.stats["hp"] > 0:
                            if doubleDamageL:
                                HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                           (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 1)))
                                self.stats["hp"] -= (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 1))
                                if self.stats["hp"] <= 0:
                                    self.game.enemyDieSound.play()
                                self.game.enemyHitSound.play()
                                self.hit = True
                            else:
                                HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                           (max(self.game.follower.stats["pow"] - self.stats["def"], 1)))
                                self.stats["hp"] -= (max(self.game.follower.stats["pow"] - self.stats["def"], 1))
                                if self.stats["hp"] <= 0:
                                    self.game.enemyDieSound.play()
                                self.game.enemyHitSound.play()
                                self.hit = True
                            self.game.follower.airTimer = 0
                        else:
                            if not self.game.follower.hit and self.stats[
                                "hp"] > 0 and not self.hit and self.game.follower.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                           (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                                self.game.follower.stats["hp"] -= (
                                    max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                                if self.game.follower.stats["hp"] <= 0:
                                    self.game.follower.stats["hp"] = 0
                                    self.game.follower.currentFrame = 0
                                self.game.follower.hitTime = pg.time.get_ticks()
                                self.game.playerHitSound.play()
                                self.game.follower.canBeHit = False
                                self.game.follower.hit = True

            if self.stats["hp"] != 0 and self.game.player.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                    if hammerHitsRound2 and not self.hit and self.stats["hp"] > 0:
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1))
                        self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        self.hit = True

            if self.stats["hp"] != 0 and self.game.follower.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                    if hammerHitsRound2 and not self.hit and self.stats["hp"] > 0:
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1))
                        self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        self.hit = True

            for entity in self.game.entities:
                if self.rect.colliderect(entity.rect) and not self.hit and self.stats["hp"] > 0:
                    if type(entity).__name__ == "Lightning":
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 1))
                        self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 1)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        self.hit = True
                    if self.imgRect.colliderect(entity.imgRect):
                        if type(entity).__name__ == "Fireball":
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1))
                            self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1)
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                            entity.dead = True
        else:
            if self.game.player.stats["hp"] != 0:
                hits = pg.sprite.collide_rect(self.game.player, self)
                if hits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                    if hitsRound2:
                        if not self.game.player.hit and self.stats[
                            "hp"] > 0 and not self.hit and self.game.player.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.player.rect.left, self.game.player.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                            self.game.player.stats["hp"] -= (
                                max(self.stats["pow"] - self.game.player.stats["def"], 1))
                            if self.game.player.stats["hp"] <= 0:
                                self.game.player.stats["hp"] = 0
                                self.game.player.currentFrame = 0
                            self.game.player.hitTime = pg.time.get_ticks()
                            self.game.playerHitSound.play()
                            self.game.player.canBeHit = False
                            self.game.player.hit = True

            if self.game.follower.stats["hp"] > 0:
                luigiHits = pg.sprite.collide_rect(self.game.follower, self)
                if luigiHits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                    if keys[
                        pg.K_l] and self.game.follower.going == "down" and self.game.follower.rect.bottom <= self.imgRect.top + 50:
                        doubleDamageL = True
                    if hitsRound2:
                        if self.game.follower.stats["hp"] != 0:
                            if not self.game.follower.hit and self.stats[
                                "hp"] > 0 and not self.hit and self.game.follower.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                           (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                                self.game.follower.stats["hp"] -= (
                                    max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                                if self.game.follower.stats["hp"] <= 0:
                                    self.game.follower.stats["hp"] = 0
                                    self.game.follower.currentFrame = 0
                                self.game.follower.hitTime = pg.time.get_ticks()
                                self.game.playerHitSound.play()
                                self.game.follower.canBeHit = False
                                self.game.follower.hit = True

        if self.stats["hp"] > 0:
            if self.is_idle:
                chance = random.randrange(0, 200)
                if chance == 0 or chance == 1:
                    dir = random.randrange(0, 4)
                    if dir == 0:
                        self.facing = "up"
                        self.vy = -self.speed
                    elif dir == 1:
                        self.facing = "down"
                        self.vy = self.speed
                    elif dir == 2:
                        self.facing = "left"
                        self.vx = -self.speed
                    else:
                        self.facing = "right"
                        self.vx = self.speed
                    self.startWalking()
                else:
                    self.vx, self.vy = 0, 0
                    if chance == 2:
                        self.currentFrame = 0
                        self.goToEyes()
            elif self.is_eyes:
                chance = random.randrange(0, 200)
                if chance == 0:
                    self.currentFrame = 0
                    self.facing = "down"
                    self.leaveEyes()
            elif self.is_moving:
                self.rect.x += self.vx
                self.rect.y += self.vy

                for wall in self.game.walls:
                    if pg.sprite.collide_rect(self, wall):
                        self.vx *= -1
                        self.vy *= -1
                        if self.facing == "up":
                            self.rect.top = wall.rect.bottom
                            self.rect.y += self.vy
                            self.facing = "down"
                        elif self.facing == "down":
                            self.rect.bottom = wall.rect.top
                            self.rect.y += self.vy
                            self.facing = "up"
                        elif self.facing == "left":
                            self.rect.left = wall.rect.right
                            self.rect.x += self.vx
                            self.facing = "right"
                        elif self.facing == "right":
                            self.rect.right = wall.rect.left
                            self.rect.x += self.vx
                            self.facing = "left"

                chance = random.randrange(0, 300)
                if chance == 0:
                    self.giveUp()

        if self.hit:
            self.hitTimer += 1
            if self.hitTimer >= fps:
                self.hitTimer = 0
                self.hit = False

        if self.stats["hp"] <= 0:
            self.alpha -= 10

        if self.alpha <= 0:
            self.game.battleXp += self.stats["exp"]
            self.game.battleCoins += self.stats["coins"]
            self.game.sprites.remove(self)
            self.game.enemies.remove(self)

        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx


class Anuboo(StateMachine):
    idle = State("Idle", initial=True)
    moving = State("Moving")
    charge = State("Charge")
    fire = State("Fire")

    startWalking = idle.to(moving)
    giveUp = moving.to(idle)
    toFireIdle = idle.to(charge)
    toFireMove = moving.to(charge)
    toFire = charge.to(fire)
    stopFire = fire.to(idle)

    def init(self, game, x, y, facing="down"):
        self.game = game
        self.game.sprites.append(self)
        self.game.enemies.append(self)
        self.loadImages()
        self.vx = 0
        self.vy = 0
        self.image = self.walkingFramesDown[0]
        self.currentFrame = random.randrange(len(self.walkingFramesDown))
        self.lastUpdate = 0
        self.facing = facing
        self.shadow = self.shadowFrame
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = (x, y)
        self.alpha = 255
        self.speed = 2
        self.hpSpeed = 0
        self.hitTimer = 0
        self.dead = False
        self.hit = False

        # Stats
        self.stats = {"maxHP": 50, "hp": 50, "pow": 35, "def": 30, "exp": 7, "coins": 6, "name": "Anuboo"}
        self.rectHP = self.stats["hp"]

        self.description = ["That's an Anuboo!",
                            "Anuboos don't like it when you\nlook at them.",
                            "If you do, they'll shoot lasers\nat you!",
                            "Max HP is " + str(self.stats["maxHP"]) + ",/p\nAttack is " + str(
                                self.stats["pow"]) + ",/p\nDefence is " + str(self.stats["def"]) + ".",
                            "They way they just slide on the\nground is really unsettling..."]

    def loadImages(self):
        sheet = spritesheet("sprites/anuboo.png", "sprites/anuboo.xml")

        self.walkingFramesUp = [sheet.getImageName("up.png")]

        self.walkingFramesDown = [sheet.getImageName("down.png")]

        self.walkingFramesLeft = [sheet.getImageName("left.png")]

        self.walkingFramesRight = [sheet.getImageName("right.png")]

        self.chargingFramesUp = [sheet.getImageName("charge_up_1.png"),
                                 sheet.getImageName("charge_up_2.png"),
                                 sheet.getImageName("charge_up_3.png"),
                                 sheet.getImageName("charge_up_4.png"),
                                 sheet.getImageName("charge_up_5.png"),
                                 sheet.getImageName("charge_up_6.png"),
                                 sheet.getImageName("charge_up_7.png"),
                                 sheet.getImageName("charge_up_8.png")]

        self.chargingFramesDown = [sheet.getImageName("charge_down_1.png"),
                                   sheet.getImageName("charge_down_2.png"),
                                   sheet.getImageName("charge_down_3.png"),
                                   sheet.getImageName("charge_down_4.png"),
                                   sheet.getImageName("charge_down_5.png"),
                                   sheet.getImageName("charge_down_6.png"),
                                   sheet.getImageName("charge_down_7.png"),
                                   sheet.getImageName("charge_down_8.png")]

        self.chargingFramesLeft = [sheet.getImageName("charge_left_1.png"),
                                   sheet.getImageName("charge_left_2.png"),
                                   sheet.getImageName("charge_left_3.png"),
                                   sheet.getImageName("charge_left_4.png"),
                                   sheet.getImageName("charge_left_5.png"),
                                   sheet.getImageName("charge_left_6.png"),
                                   sheet.getImageName("charge_left_7.png"),
                                   sheet.getImageName("charge_left_8.png")]

        self.chargingFramesRight = [sheet.getImageName("charge_right_1.png"),
                                    sheet.getImageName("charge_right_2.png"),
                                    sheet.getImageName("charge_right_3.png"),
                                    sheet.getImageName("charge_right_4.png"),
                                    sheet.getImageName("charge_right_5.png"),
                                    sheet.getImageName("charge_right_6.png"),
                                    sheet.getImageName("charge_right_7.png"),
                                    sheet.getImageName("charge_right_8.png")]

        self.shadowFrame = sheet.getImageName("shadow.png")

    def hpMath(self):
        if self.rectHP > self.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = ((self.rectHP - self.stats["hp"]) / 30) * -1
        elif self.rectHP < self.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = (self.stats["hp"] - self.rectHP) / 30

        if self.hpSpeed != 0:
            if self.rectHP + self.hpSpeed > self.stats["hp"] and self.hpSpeed < 0:
                self.rectHP += self.hpSpeed
            elif self.rectHP + self.hpSpeed < self.stats["hp"] and self.hpSpeed > 0:
                self.rectHP += self.hpSpeed
            else:
                self.rectHP = self.stats["hp"]
                self.hpSpeed = 0

    def animate(self):
        now = pg.time.get_ticks()
        if self.is_moving:
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
        elif self.is_charge or self.is_fire:
            if self.facing == "down":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.chargingFramesDown):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.chargingFramesDown))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.chargingFramesDown[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "up":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.chargingFramesUp):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.chargingFramesUp))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.chargingFramesUp[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "left":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.chargingFramesLeft):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.chargingFramesLeft))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.chargingFramesLeft[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "right":
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.chargingFramesRight):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.chargingFramesRight))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.chargingFramesRight[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
        else:
            if self.facing == "down":
                center = self.imgRect.center
                self.image = self.walkingFramesDown[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "up":
                center = self.imgRect.center
                self.image = self.walkingFramesUp[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "left":
                center = self.imgRect.center
                self.image = self.walkingFramesLeft[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "right":
                center = self.imgRect.center
                self.image = self.walkingFramesRight[0]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center

    def update(self):
        self.animate()
        self.hpMath()
        keys = pg.key.get_pressed()

        if self.stats["hp"] > 0:
            if self.is_idle:
                chance = random.randrange(0, 100)
                if chance == 0:
                    dir = random.randrange(0, 4)
                    if dir == 0:
                        self.facing = "up"
                        self.vy = -self.speed
                    elif dir == 1:
                        self.facing = "down"
                        self.vy = self.speed
                    elif dir == 2:
                        self.facing = "left"
                        self.vx = -self.speed
                    else:
                        self.facing = "right"
                        self.vx = self.speed
                    self.startWalking()
                else:
                    self.vx, self.vy = 0, 0
            elif self.is_moving:
                self.rect.x += self.vx
                self.rect.y += self.vy

                for wall in self.game.walls:
                    if pg.sprite.collide_rect(self, wall):
                        self.vx *= -1
                        self.vy *= -1
                        if self.facing == "up":
                            self.rect.top = wall.rect.bottom
                            self.rect.y += self.vy
                            self.facing = "down"
                        elif self.facing == "down":
                            self.rect.bottom = wall.rect.top
                            self.rect.y += self.vy
                            self.facing = "up"
                        elif self.facing == "left":
                            self.rect.left = wall.rect.right
                            self.rect.x += self.vx
                            self.facing = "right"
                        elif self.facing == "right":
                            self.rect.right = wall.rect.left
                            self.rect.x += self.vx
                            self.facing = "left"

                chance = random.randrange(0, 100)
                if chance == 0:
                    self.giveUp()
            elif self.is_charge:
                chance = random.randrange(0, 100)
                if chance == 0:
                    self.toFire()
            elif self.is_fire:
                AnubooLazer(self.game, self.rect.center, self.stats)
                self.stopFire()

        if self.game.leader == "mario":
            if self.facing == "left":
                if self.game.player.rect.right < self.rect.left:
                    if self.rect.bottom > self.game.player.rect.top and self.game.player.rect.bottom < self.rect.top:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()
            elif self.facing == "right":
                if self.game.player.rect.left > self.rect.right:
                    if self.rect.bottom > self.game.player.rect.top and self.game.player.rect.bottom < self.rect.top:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()
            elif self.facing == "top":
                if self.game.player.rect.bottom < self.rect.top:
                    if self.rect.left > self.game.player.rect.left and self.game.player.rect.right < self.rect.right:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()
            elif self.facing == "bottom":
                if self.game.player.rect.top > self.rect.bottom:
                    if self.rect.left > self.game.player.rect.left and self.game.player.rect.right < self.rect.right:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()
        elif self.game.leader == "luigi":
            if self.facing == "left":
                if self.game.follower.rect.right < self.rect.left:
                    if self.rect.bottom > self.game.follower.rect.top and self.game.follower.rect.bottom < self.rect.top:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()
            elif self.facing == "right":
                if self.game.follower.rect.left > self.rect.right:
                    if self.rect.bottom > self.game.follower.rect.top and self.game.follower.rect.bottom < self.rect.top:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()
            elif self.facing == "top":
                if self.game.follower.rect.bottom < self.rect.top:
                    if self.rect.left > self.game.follower.rect.left and self.game.follower.rect.right < self.rect.right:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()
            elif self.facing == "bottom":
                if self.game.follower.rect.top > self.rect.bottom:
                    if self.rect.left > self.game.follower.rect.left and self.game.follower.rect.right < self.rect.right:
                        if self.is_idle:
                            self.toFireIdle()
                        elif self.is_moving:
                            self.toFireMove()

        if self.game.player.stats["hp"] != 0:
            doubleDamageM = False
            hits = pg.sprite.collide_rect(self.game.player, self)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                if keys[
                    pg.K_m] and self.game.player.going == "down" and self.game.player.rect.bottom <= self.imgRect.top + 50:
                    doubleDamageM = True
                if hitsRound2:
                    if self.game.player.going == "down" and self.game.player.jumping and self.stats["hp"] > 0:
                        if doubleDamageM:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (max(2 * (self.game.player.stats["pow"] - self.stats["def"]), 1)))
                            self.stats["hp"] -= (max(2 * (self.game.player.stats["pow"] - self.stats["def"]), 1))
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                        else:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (max(self.game.player.stats["pow"] - self.stats["def"], 1)))
                            self.stats["hp"] -= (max(self.game.player.stats["pow"] - self.stats["def"], 1))
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                        self.game.player.airTimer = 0
                    else:
                        if not self.game.player.hit and self.stats[
                            "hp"] > 0 and not self.hit and self.game.player.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.player.rect.left, self.game.player.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                            self.game.player.stats["hp"] -= (
                                max(self.stats["pow"] - self.game.player.stats["def"], 1))
                            if self.game.player.stats["hp"] <= 0:
                                self.game.player.stats["hp"] = 0
                                self.game.player.currentFrame = 0
                            self.game.player.hitTime = pg.time.get_ticks()
                            self.game.playerHitSound.play()
                            self.game.player.canBeHit = False
                            self.game.player.hit = True

        if self.game.follower.stats["hp"] != 0:
            luigiHits = pg.sprite.collide_rect(self.game.follower, self)
            if luigiHits:
                doubleDamageL = False
                hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                if keys[
                    pg.K_l] and self.game.follower.going == "down" and self.game.follower.rect.bottom <= self.imgRect.top + 50:
                    doubleDamageL = True
                if hitsRound2:
                    if self.game.follower.going == "down" and self.game.follower.jumping and self.stats["hp"] > 0:
                        if doubleDamageL:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 1)))
                            self.stats["hp"] -= (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 1))
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                        else:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (max(self.game.follower.stats["pow"] - self.stats["def"], 1)))
                            self.stats["hp"] -= (max(self.game.follower.stats["pow"] - self.stats["def"], 1))
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                        self.game.follower.airTimer = 0
                    else:
                        if not self.game.follower.hit and self.stats[
                            "hp"] > 0 and not self.hit and self.game.follower.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                            self.game.follower.stats["hp"] -= (
                                max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                            if self.game.follower.stats["hp"] <= 0:
                                self.game.follower.stats["hp"] = 0
                                self.game.follower.currentFrame = 0
                            self.game.follower.hitTime = pg.time.get_ticks()
                            self.game.playerHitSound.play()
                            self.game.follower.canBeHit = False
                            self.game.follower.hit = True

        if self.stats["hp"] != 0 and self.game.player.isHammer is not None:
            hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
            if hammerHits:
                hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                if hammerHitsRound2 and not self.hit and self.stats["hp"] > 0:
                    HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                               max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1))
                    self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1)
                    if self.stats["hp"] <= 0:
                        self.game.enemyDieSound.play()
                    self.game.enemyHitSound.play()
                    self.hit = True

        if self.stats["hp"] != 0 and self.game.follower.isHammer is not None:
            hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
            if hammerHits:
                hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                if hammerHitsRound2 and not self.hit and self.stats["hp"] > 0:
                    HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                               max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1))
                    self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1)
                    if self.stats["hp"] <= 0:
                        self.game.enemyDieSound.play()
                    self.game.enemyHitSound.play()
                    self.hit = True

        for entity in self.game.entities:
            if self.rect.colliderect(entity.rect) and not self.hit and self.stats["hp"] > 0:
                if type(entity).__name__ == "Lightning":
                    HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                               max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 1))
                    self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 1)
                    if self.stats["hp"] <= 0:
                        self.game.enemyDieSound.play()
                    self.game.enemyHitSound.play()
                    self.hit = True
                if self.imgRect.colliderect(entity.imgRect):
                    if type(entity).__name__ == "Fireball":
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1))
                        self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        self.hit = True
                        entity.dead = True

        if self.hit:
            self.hitTimer += 1
            if self.hitTimer >= fps:
                self.hitTimer = 0
                self.hit = False

        if self.stats["hp"] <= 0:
            self.alpha -= 10

        if self.alpha <= 0:
            self.game.battleXp += self.stats["exp"]
            self.game.battleCoins += self.stats["coins"]
            self.game.sprites.remove(self)
            self.game.enemies.remove(self)

        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx


class AnubooLazer(pg.sprite.Sprite):
    def __init__(self, game, pos, stats):
        self.game = game
        self.game.sprites.append(self)
        sheet = spritesheet("sprites/anuboo.png", "sprites/anuboo.xml")
        self.rect = pg.rect.Rect(pos, (0, 0))
        if self.game.leader == "mario":
            self.angle = get_angle(self.rect.center, self.game.player.rect.center)
            self.image = pg.transform.rotate(sheet.getImageName("lazer_vertical.png"), math.degrees(
                math.atan2(self.game.player.rect.centerx - self.rect.centerx,
                           self.game.player.rect.centery - self.rect.centery)))
        elif self.game.leader == "luigi":
            self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
            self.image = pg.transform.rotate(sheet.getImageName("lazer_vertical.png"), math.degrees(
                math.atan2(self.game.follower.rect.centerx - self.rect.centerx,
                           self.game.follower.rect.centery - self.rect.centery)))
        self.lastUpdate = 0
        self.imgRect = self.image.get_rect()
        self.shadow = self.image.copy()
        self.shadow.fill((0, 0, 0, 255), special_flags=pg.BLEND_RGBA_MIN)
        self.shadow.set_alpha(150)
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.imgRect.centerx, self.imgRect.bottom = self.rect.centerx, self.rect.top - 25
        self.alpha = 255
        self.speed = 5
        self.dead = False
        self.stats = stats

    def update(self):
        self.rect.center = project(self.rect.center, self.angle, self.speed)
        self.imgRect.centerx, self.imgRect.bottom = self.rect.centerx, self.rect.top - 25
        for wall in self.game.walls:
            if wall.rect.colliderect(self.rect):
                if self in self.game.sprites:
                    self.game.sprites.remove(self)

        if self.game.player.stats["hp"] != 0:
            hits = pg.sprite.collide_rect(self.game.player, self)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                if hitsRound2:
                    if not self.game.player.hit and self.stats[
                        "hp"] > 0 and self.game.player.canBeHit:
                        HitNumbers(self.game, self.game.room,
                                   (self.game.player.rect.left, self.game.player.rect.top - 2),
                                   (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                        self.game.player.stats["hp"] -= (
                            max(self.stats["pow"] - self.game.player.stats["def"], 1))
                        if self.game.player.stats["hp"] <= 0:
                            self.game.player.stats["hp"] = 0
                            self.game.player.currentFrame = 0
                        self.game.player.hitTime = pg.time.get_ticks()
                        self.game.playerHitSound.play()
                        self.game.player.canBeHit = False
                        self.game.player.hit = True

        if self.game.follower.stats["hp"] != 0:
            luigiHits = pg.sprite.collide_rect(self.game.follower, self)
            if luigiHits:
                hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                if hitsRound2:
                    if self.game.follower.stats["hp"] != 0:
                        if not self.game.follower.hit and self.stats[
                            "hp"] > 0 and self.game.follower.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                            self.game.follower.stats["hp"] -= (
                                max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                            if self.game.follower.stats["hp"] <= 0:
                                self.game.follower.stats["hp"] = 0
                                self.game.follower.currentFrame = 0
                            self.game.follower.hitTime = pg.time.get_ticks()
                            self.game.playerHitSound.play()
                            self.game.follower.canBeHit = False
                            self.game.follower.hit = True


class SpikySnifit(StateMachine):
    idle = State("Idle", initial=True)
    toFire = State("To Fire")
    fire = State("Fire")
    hit = State("Hit")

    charge = idle.to(toFire)
    startFire = toFire.to(fire)
    stopFire = fire.to(idle)
    getHurt = idle.to(hit)
    notHurt = hit.to(idle)

    def init(self, game, pos):
        self.game = game
        self.game.enemies.append(self)
        self.game.sprites.append(self)

        self.loadImages()
        self.alpha = 255
        self.speed = 10
        self.lastUpdate = 0
        self.currentFrame = 0
        self.cooldown = 60
        self.dead = False
        self.hit = False
        self.image = self.idleFrames[0]
        self.imgRect = self.image.get_rect()
        self.shadow = self.shadowFrame
        self.rect = self.shadow.get_rect()
        self.hpSpeed = 0
        self.rect.center = pos
        self.facing = "left"
        self.imgRect.left = self.rect.left
        self.imgRect.bottom = self.rect.bottom + 1

        # Stats
        self.stats = {"maxHP": 100, "hp": 100, "pow": 40, "def": 40, "exp": 13, "coins": 11, "name": "Spiky Snifit"}
        self.rectHP = self.stats["hp"]

        self.description = ["That's a Spiky Snifit!",
                            "Spiky Snifits stay put in the ground,/p\ndue to them being plants.",
                            "They do like to shoot spike balls at\nyou, though.",
                            "Max HP is " + str(self.stats["maxHP"]) + ",/p\nAttack is " + str(
                                self.stats["pow"]) + ",/p\nDefence is " + str(self.stats["def"]) + ".",
                            "Spiky Snifits aren't actually snifits!",
                            "They're a sub-species of pokey,\nbut the mask makes people\nconfuse them with snifits."]

    def loadImages(self):
        sheet = spritesheet("sprites/spiky snifit.png", "sprites/spiky snifit.xml")

        self.idleFrames = [sheet.getImageName("idle_1.png"),
                           sheet.getImageName("idle_2.png"),
                           sheet.getImageName("idle_3.png"),
                           sheet.getImageName("idle_4.png"),
                           sheet.getImageName("idle_5.png"),
                           sheet.getImageName("idle_6.png"),
                           sheet.getImageName("idle_7.png"),
                           sheet.getImageName("idle_8.png"),
                           sheet.getImageName("idle_9.png")]

        self.toShootFrames = [sheet.getImageName("to_shoot_1.png"),
                              sheet.getImageName("to_shoot_2.png"),
                              sheet.getImageName("to_shoot_3.png"),
                              sheet.getImageName("to_shoot_4.png"),
                              sheet.getImageName("to_shoot_5.png"),
                              sheet.getImageName("to_shoot_6.png"),
                              sheet.getImageName("to_shoot_7.png"),
                              sheet.getImageName("to_shoot_8.png"),
                              sheet.getImageName("to_shoot_9.png"),
                              sheet.getImageName("to_shoot_10.png"),
                              sheet.getImageName("to_shoot_11.png"),
                              sheet.getImageName("to_shoot_12.png"),
                              sheet.getImageName("to_shoot_13.png")]

        self.shootFrames = [sheet.getImageName("shoot_1.png"),
                            sheet.getImageName("shoot_2.png"),
                            sheet.getImageName("shoot_3.png"),
                            sheet.getImageName("shoot_4.png"),
                            sheet.getImageName("shoot_5.png")]

        self.hitFrame = sheet.getImageName("hit.png")

        self.shadowFrame = sheet.getImageName("shadow.png")

    def hpMath(self):
        if self.rectHP > self.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = ((self.rectHP - self.stats["hp"]) / 30) * -1
        elif self.rectHP < self.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = (self.stats["hp"] - self.rectHP) / 30

        if self.hpSpeed != 0:
            if self.rectHP + self.hpSpeed > self.stats["hp"] and self.hpSpeed < 0:
                self.rectHP += self.hpSpeed
            elif self.rectHP + self.hpSpeed < self.stats["hp"] and self.hpSpeed > 0:
                self.rectHP += self.hpSpeed
            else:
                self.rectHP = self.stats["hp"]
                self.hpSpeed = 0

    def update(self):
        self.animate()
        self.hpMath()

        if self.stats["hp"] > 0:
            if self.is_idle:
                chance = random.randrange(0, 200)
                if chance == 0:
                    self.currentFrame = 0

                    self.charge()
            if self.hit:
                if self.is_idle:
                    self.imgRect.centerx = self.rect.centerx
                    self.cooldown = 60
                    self.getHurt()

        keys = pg.key.get_pressed()
        doubleDamageM = False
        doubleDamageL = False

        if self.is_idle:
            if self.game.player.stats["hp"] != 0:
                hits = pg.sprite.collide_rect(self.game.player, self)
                if hits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                    if keys[
                        pg.K_m] and self.game.player.going == "down" and self.game.player.rect.bottom <= self.imgRect.top + 50:
                        doubleDamageM = True
                    if hitsRound2:
                        if self.game.player.going == "down" and self.game.player.jumping and self.stats["hp"] > 0:
                            if doubleDamageM:
                                HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                           (max(2 * (self.game.player.stats["pow"] - self.stats["def"]), 1)))
                                self.stats["hp"] -= (max(2 * (self.game.player.stats["pow"] - self.stats["def"]), 1))
                                if self.stats["hp"] <= 0:
                                    self.game.enemyDieSound.play()
                                self.game.enemyHitSound.play()
                                self.hit = True
                            else:
                                HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                           (max(self.game.player.stats["pow"] - self.stats["def"], 1)))
                                self.stats["hp"] -= (max(self.game.player.stats["pow"] - self.stats["def"], 1))
                                if self.stats["hp"] <= 0:
                                    self.game.enemyDieSound.play()
                                self.game.enemyHitSound.play()
                                self.hit = True
                            self.game.player.airTimer = 0
                        else:
                            if not self.game.player.hit and self.stats[
                                "hp"] > 0 and not self.hit and self.game.player.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.player.rect.left, self.game.player.rect.top - 2),
                                           (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                                self.game.player.stats["hp"] -= (
                                    max(self.stats["pow"] - self.game.player.stats["def"], 1))
                                if self.game.player.stats["hp"] <= 0:
                                    self.game.player.stats["hp"] = 0
                                    self.game.player.currentFrame = 0
                                self.game.player.hitTime = pg.time.get_ticks()
                                self.game.playerHitSound.play()
                                self.game.player.canBeHit = False
                                self.game.player.hit = True

            if self.game.follower.stats["hp"] != 0:
                luigiHits = pg.sprite.collide_rect(self.game.follower, self)
                if luigiHits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                    if keys[
                        pg.K_l] and self.game.follower.going == "down" and self.game.follower.rect.bottom <= self.imgRect.top + 50:
                        doubleDamageL = True
                    if hitsRound2:
                        if self.game.follower.going == "down" and self.game.follower.jumping and self.stats["hp"] > 0:
                            if doubleDamageL:
                                HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                           (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 1)))
                                self.stats["hp"] -= (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 1))
                                if self.stats["hp"] <= 0:
                                    self.game.enemyDieSound.play()
                                self.game.enemyHitSound.play()
                                self.hit = True
                            else:
                                HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                           (max(self.game.follower.stats["pow"] - self.stats["def"], 1)))
                                self.stats["hp"] -= (max(self.game.follower.stats["pow"] - self.stats["def"], 1))
                                if self.stats["hp"] <= 0:
                                    self.game.enemyDieSound.play()
                                self.game.enemyHitSound.play()
                                self.hit = True
                            self.game.follower.airTimer = 0
                        else:
                            if not self.game.follower.hit and self.stats[
                                "hp"] > 0 and not self.hit and self.game.follower.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                           (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                                self.game.follower.stats["hp"] -= (
                                    max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                                if self.game.follower.stats["hp"] <= 0:
                                    self.game.follower.stats["hp"] = 0
                                    self.game.follower.currentFrame = 0
                                self.game.follower.hitTime = pg.time.get_ticks()
                                self.game.playerHitSound.play()
                                self.game.follower.canBeHit = False
                                self.game.follower.hit = True

            if self.stats["hp"] != 0 and self.game.player.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                    if hammerHitsRound2 and not self.hit and self.stats["hp"] > 0:
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 0))
                        self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 0)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        self.hit = True

            if self.stats["hp"] != 0 and self.game.follower.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                    if hammerHitsRound2 and not self.hit and self.stats["hp"] > 0:
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1))
                        self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        self.hit = True

            for entity in self.game.entities:
                if self.rect.colliderect(entity.rect) and not self.hit and self.stats["hp"] > 0:
                    if type(entity).__name__ == "Lightning":
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 1))
                        self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 1)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        self.hit = True
                    if self.imgRect.colliderect(entity.imgRect):
                        if type(entity).__name__ == "Fireball":
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1))
                            self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1)
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                            entity.dead = True
        else:
            if self.game.player.stats["hp"] != 0:
                hits = pg.sprite.collide_rect(self.game.player, self)
                if hits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                    if hitsRound2:
                        if not self.game.player.hit and self.stats[
                            "hp"] > 0 and not self.hit and self.game.player.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.player.rect.left, self.game.player.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                            self.game.player.stats["hp"] -= (
                                max(self.stats["pow"] - self.game.player.stats["def"], 1))
                            if self.game.player.stats["hp"] <= 0:
                                self.game.player.stats["hp"] = 0
                                self.game.player.currentFrame = 0
                            self.game.player.hitTime = pg.time.get_ticks()
                            self.game.playerHitSound.play()
                            self.game.player.canBeHit = False
                            self.game.player.hit = True

            if self.game.follower.stats["hp"] > 0:
                luigiHits = pg.sprite.collide_rect(self.game.follower, self)
                if luigiHits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                    if hitsRound2:
                        if self.game.follower.stats["hp"] != 0:
                            if not self.game.follower.hit and self.stats[
                                "hp"] > 0 and not self.hit and self.game.follower.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                           (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                                self.game.follower.stats["hp"] -= (
                                    max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                                if self.game.follower.stats["hp"] <= 0:
                                    self.game.follower.stats["hp"] = 0
                                    self.game.follower.currentFrame = 0
                                self.game.follower.hitTime = pg.time.get_ticks()
                                self.game.playerHitSound.play()
                                self.game.follower.canBeHit = False
                                self.game.follower.hit = True

        if self.stats["hp"] <= 0:
            self.alpha -= 10

        if self.alpha <= 0:
            self.game.battleXp += self.stats["exp"]
            self.game.battleCoins += self.stats["coins"]
            self.game.sprites.remove(self)
            self.game.enemies.remove(self)

    def animate(self):
        now = pg.time.get_ticks()
        if self.is_idle:
            if now - self.lastUpdate > 45:
                self.lastUpdate = now
                if self.currentFrame < len(self.idleFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.idleFrames))
                else:
                    self.currentFrame = 0

                if self.game.leader == "mario":
                    if self.game.player.rect.centerx > self.rect.centerx:
                        right = self.imgRect.right
                        bottom = self.imgRect.bottom
                        self.image = pg.transform.flip(self.idleFrames[self.currentFrame], True, False)
                        self.facing = "left"
                        self.imgRect = self.image.get_rect()
                        self.imgRect.right = right
                        self.imgRect.bottom = bottom
                    else:
                        left = self.imgRect.left
                        bottom = self.imgRect.bottom
                        self.image = self.idleFrames[self.currentFrame]
                        self.facing = "right"
                        self.imgRect = self.image.get_rect()
                        self.imgRect.left = left
                        self.imgRect.bottom = bottom
                else:
                    if self.game.follower.rect.centerx > self.rect.centerx:
                        right = self.imgRect.right
                        bottom = self.imgRect.bottom
                        self.image = pg.transform.flip(self.idleFrames[self.currentFrame], True, False)
                        self.facing = "left"
                        self.imgRect = self.image.get_rect()
                        self.imgRect.right = right
                        self.imgRect.bottom = bottom
                    else:
                        left = self.imgRect.left
                        bottom = self.imgRect.bottom
                        self.image = self.idleFrames[self.currentFrame]
                        self.facing = "right"
                        self.imgRect = self.image.get_rect()
                        self.imgRect.left = left
                        self.imgRect.bottom = bottom
        elif self.is_toFire:
            if now - self.lastUpdate > 45:
                self.lastUpdate = now
                if self.currentFrame < len(self.toShootFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    SnifitBall(self.game, self.rect.center, self.stats)
                    self.currentFrame = 0
                    self.startFire()
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                if self.facing == "left":
                    self.image = pg.transform.flip(self.toShootFrames[self.currentFrame], True, False)
                else:
                    self.image = self.toShootFrames[self.currentFrame]
                    self.facing = "right"
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        elif self.is_fire:
            if now - self.lastUpdate > 45:
                self.lastUpdate = now
                if self.currentFrame < len(self.shootFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.currentFrame = 0
                    self.stopFire()
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                if self.game.leader == "mario":
                    if self.game.player.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.shootFrames[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.shootFrames[self.currentFrame]
                        self.facing = "right"
                else:
                    if self.game.follower.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.shootFrames[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.shootFrames[self.currentFrame]
                        self.facing = "right"
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        elif self.is_hit:
            print(self.cooldown)
            self.currentFrame = 0
            centerx = self.imgRect.centerx
            bottom = self.imgRect.bottom
            if self.facing == "left":
                self.image = pg.transform.flip(self.hitFrame, True, False)
            else:
                self.image = self.hitFrame
            self.imgRect = self.image.get_rect()
            self.imgRect.centerx = centerx
            self.imgRect.bottom = bottom
            if self.cooldown == 0:
                self.hit = False
                self.notHurt()
            else:
                self.cooldown -= 1


class SnifitBall(pg.sprite.Sprite):
    def __init__(self, game, pos, stats):
        self.game = game
        self.game.sprites.append(self)
        sheet = spritesheet("sprites/spiky snifit.png", "sprites/spiky snifit.xml")
        self.rect = pg.rect.Rect(pos, (0, 0))
        if self.game.leader == "mario":
            self.angle = get_angle(self.rect.center, self.game.player.rect.center)
            self.image = pg.transform.rotate(sheet.getImageName("ball.png"), math.degrees(
                math.atan2(self.game.player.rect.centerx - self.rect.centerx,
                           self.game.player.rect.centery - self.rect.centery)))
        elif self.game.leader == "luigi":
            self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
            self.image = pg.transform.rotate(sheet.getImageName("ball.png"), math.degrees(
                math.atan2(self.game.follower.rect.centerx - self.rect.centerx,
                           self.game.follower.rect.centery - self.rect.centery)))
        self.lastUpdate = 0
        self.imgRect = self.image.get_rect()
        self.shadow = sheet.getImageName("ballShadow.png")
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.offset = 20
        self.maxOffset = 50
        self.bounceSpeed = 5
        self.imgRect.centerx, self.imgRect.bottom = self.rect.centerx, self.rect.bottom - self.offset + 5
        self.alpha = 255
        self.speed = 8
        self.dead = False
        self.stats = stats

    def update(self):
        self.rect.center = project(self.rect.center, self.angle, self.speed)
        for wall in self.game.walls:
            if wall.rect.colliderect(self.rect):
                if self in self.game.sprites:
                    self.game.sprites.remove(self)

        if self.game.player.stats["hp"] != 0:
            hits = pg.sprite.collide_rect(self.game.player, self)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                if hitsRound2:
                    if not self.game.player.hit and self.stats[
                        "hp"] > 0 and self.game.player.canBeHit:
                        HitNumbers(self.game, self.game.room,
                                   (self.game.player.rect.left, self.game.player.rect.top - 2),
                                   (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                        self.game.player.stats["hp"] -= (
                            max(self.stats["pow"] - self.game.player.stats["def"], 1))
                        if self.game.player.stats["hp"] <= 0:
                            self.game.player.stats["hp"] = 0
                            self.game.player.currentFrame = 0
                        self.game.player.hitTime = pg.time.get_ticks()
                        self.game.playerHitSound.play()
                        self.game.player.canBeHit = False
                        self.game.player.hit = True

        if self.game.follower.stats["hp"] != 0:
            luigiHits = pg.sprite.collide_rect(self.game.follower, self)
            if luigiHits:
                hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                if hitsRound2:
                    if self.game.follower.stats["hp"] != 0:
                        if not self.game.follower.hit and self.stats[
                            "hp"] > 0 and self.game.follower.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                            self.game.follower.stats["hp"] -= (
                                max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                            if self.game.follower.stats["hp"] <= 0:
                                self.game.follower.stats["hp"] = 0
                                self.game.follower.currentFrame = 0
                            self.game.follower.hitTime = pg.time.get_ticks()
                            self.game.playerHitSound.play()
                            self.game.follower.canBeHit = False
                            self.game.follower.hit = True

        self.offset += self.bounceSpeed
        if self.offset >= self.maxOffset or self.offset <= 0:
            self.bounceSpeed *= -1

        self.imgRect.centerx = self.rect.centerx
        self.imgRect.bottom = self.rect.bottom - self.offset + 5


class LinebeckDebug(pg.sprite.Sprite):
    def __init__(self, game, start, hastexted=False):
        pg.sprite.Sprite.__init__(self, game.npcs)
        self.smoltext = []
        self.text = []
        self.game = game
        self.canTalk = True
        self.textbox = None
        self.game.sprites.append(self)
        sheet = spritesheet("sprites/enemies.png", "sprites/enemies.xml")
        self.image = pg.image.load("sprites/linebeck.png").convert_alpha()
        self.shadow = sheet.getImageName("shadow.png")
        self.rect = self.shadow.get_rect()
        self.imgRect = self.image.get_rect()
        self.rect.center = start
        self.type = "talk"
        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx
        self.canShop = False
        self.alpha = 255
        if not hastexted:
            self.counter = 0
        else:
            self.counter = 1
        self.text.append("Hello!")
        self.text.append("Would you two fine moustache\nfellows care to buy anything from\n<<Rthe mighty Linebeck>>?")
        self.text.append("Go on, take a look!")

    def update(self):
        if self.textbox is None:
            for event in self.game.event:
                if event.type == pg.KEYDOWN:
                    if self.game.leader == "mario":
                        if pg.sprite.collide_rect_ratio(1.1)(self,
                                                             self.game.player) and event.key == pg.K_m and self.game.player.canMove and self.game.follower.canMove:
                            if not self.game.player.jumping:
                                self.textbox = TextBox(self.game, self, self.text)
                                self.game.linebeckHasTexted = True
                                self.canShop = True
                                self.game.playsong = False
                                self.game.currentPoint += pg.mixer.music.get_pos()
                    elif self.game.leader == "luigi":
                        if pg.sprite.collide_rect_ratio(1.1)(self,
                                                             self.game.follower) and event.key == pg.K_l and self.game.player.canMove and self.game.follower.canMove:
                            if not self.game.follower.jumping:
                                self.textbox = TextBox(self.game, self, self.text)
                                self.game.linebeckHasTexted = True
                                self.canShop = True
                                self.game.playsong = False
                                self.game.currentPoint += pg.mixer.music.get_pos()
        elif self.textbox != "complete":
            pg.event.clear()
            self.game.playSong(6.402, 33.433, "linebeck's theme")
        else:
            if self.canShop:
                self.game.shop(
                    [["Mushroom", 5], ["Super Mushroom", 15], ["1-UP Mushroom", 10], ["1-UP Deluxe", 30], ["Syrup", 5],
                     ["Star Cand", 15]], '''self.playSong(6.402, 33.433,
                "linebeck's theme")''')
                self.canShop = False
                self.textbox = TextBox(self.game, self, ["Thank you for your shopping!"])
            else:
                self.textbox = None
                self.game.playsong = True


class CountBleckDebug(pg.sprite.Sprite):
    def __init__(self, game, pos):
        pg.sprite.Sprite.__init__(self, game.npcs)
        self.text = []
        self.type = "talk"
        self.game = game
        self.canTalk = True
        self.textbox = None
        self.alpha = 255
        self.currentFrame = 0
        self.lastUpdate = 0
        self.game.sprites.append(self)
        self.loadImages()
        self.image = self.sprites[0]
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.imgRect.bottom = self.rect.centery
        self.imgRect.left = self.rect.left - 10
        self.text.append("BLEH HEH HEH HEH!/p BLECK!")
        self.text.append("I see you've come at last!\nSo you really are the heroes\nof the Light Prognosticus!")
        self.text.append("But, it is too late./p All worlds\nwill soon be erased, by Count Bleck.")
        self.text.append("Come to grips with that now,\nfor you cannot stop me.")
        self.text.append("I suggest you make yourself\ncomfortable and enjoy this\none, final spectacle!")
        self.text.append("COUNT BLECK IS THE DELETER\nOF WORLDS! MY FATE IS WRITTEN\nIN THE <<RDARK PROGNOSTICUS>>!")
        self.text.append("ARE YOU PREPARED, HEROES?")
        self.text.append("OUR DUEL WILL BE WORTHY OF\nTHE LAST CLASH THE WORLDS WILL\nEVER SEE!")

    def loadImages(self):
        sheet = spritesheet("sprites/count bleck.png", "sprites/count bleck.xml")

        self.sprites = [sheet.getImageName("idle_1.png"),
                        sheet.getImageName("idle_2.png"),
                        sheet.getImageName("idle_3.png"),
                        sheet.getImageName("idle_4.png"),
                        sheet.getImageName("idle_5.png"),
                        sheet.getImageName("idle_6.png"),
                        sheet.getImageName("idle_7.png"),
                        sheet.getImageName("idle_8.png"),
                        sheet.getImageName("idle_9.png"),
                        sheet.getImageName("idle_10.png"),
                        sheet.getImageName("idle_11.png"),
                        sheet.getImageName("idle_12.png"),
                        sheet.getImageName("idle_13.png"),
                        sheet.getImageName("idle_14.png"),
                        sheet.getImageName("idle_15.png"),
                        sheet.getImageName("idle_16.png"),
                        sheet.getImageName("idle_17.png"),
                        sheet.getImageName("idle_18.png"),
                        sheet.getImageName("idle_19.png"),
                        sheet.getImageName("idle_20.png"),
                        sheet.getImageName("idle_21.png"),
                        sheet.getImageName("idle_22.png"),
                        sheet.getImageName("idle_23.png"),
                        sheet.getImageName("idle_24.png"),
                        sheet.getImageName("idle_25.png"),
                        sheet.getImageName("idle_26.png"),
                        sheet.getImageName("idle_27.png"),
                        sheet.getImageName("idle_28.png"),
                        sheet.getImageName("idle_29.png"),
                        sheet.getImageName("idle_30.png"),
                        sheet.getImageName("idle_31.png"),
                        sheet.getImageName("idle_32.png"),
                        sheet.getImageName("idle_33.png"),
                        sheet.getImageName("idle_34.png"),
                        sheet.getImageName("idle_35.png"),
                        sheet.getImageName("idle_36.png"),
                        sheet.getImageName("idle_37.png"),
                        sheet.getImageName("idle_38.png"),
                        sheet.getImageName("idle_39.png"),
                        sheet.getImageName("idle_40.png"),
                        sheet.getImageName("idle_41.png"),
                        sheet.getImageName("idle_42.png"),
                        sheet.getImageName("idle_43.png"),
                        sheet.getImageName("idle_44.png"),
                        sheet.getImageName("idle_45.png"),
                        sheet.getImageName("idle_46.png"),
                        sheet.getImageName("idle_47.png"),
                        sheet.getImageName("idle_48.png"),
                        sheet.getImageName("idle_49.png"),
                        sheet.getImageName("idle_50.png"),
                        sheet.getImageName("idle_51.png")]

        self.talking = [sheet.getImageName("talking_1.png"),
                        sheet.getImageName("talking_2.png"),
                        sheet.getImageName("talking_3.png"),
                        sheet.getImageName("talking_4.png"),
                        sheet.getImageName("talking_5.png"),
                        sheet.getImageName("talking_6.png")]

        self.shadow = sheet.getImageName("shadow.png")

    def update(self):
        self.animate()
        if self.textbox is None:
            keys = pg.key.get_pressed()
            if self.game.leader == "mario":
                if pg.sprite.collide_rect_ratio(1.1)(self, self.game.player) and keys[pg.K_m]:
                    if not self.game.player.jumping:
                        pg.mixer.music.fadeout(200)
                        self.game.playsong = False
                        self.game.firstLoop = True
                        self.textbox = TextBox(self.game, self, self.text, dir="down")
                        self.game.currentPoint += pg.mixer.music.get_pos()
            elif self.game.leader == "luigi":
                if pg.sprite.collide_rect_ratio(1.1)(self, self.game.follower) and keys[pg.K_l]:
                    if not self.game.follower.jumping:
                        pg.mixer.music.fadeout(200)
                        self.game.playsong = False
                        self.game.firstLoop = True
                        self.textbox = TextBox(self.game, self, self.text)
                        self.game.currentPoint += pg.mixer.music.get_pos()
        elif self.textbox != "complete":
            if not pg.mixer.music.get_busy() or self.textbox.rect.center == self.textbox.points[-1]:
                self.game.playSong(10.314, 32.016, "the evil count bleck")
            pg.event.clear()
        else:
            self.textbox = None
            self.game.loadBattle("self.loadMultiEnemyDebug()", currentPoint=False)

    def animate(self):
        now = pg.time.get_ticks()
        if self.textbox is None:
            if now - self.lastUpdate > 30:
                self.lastUpdate = now
                if self.currentFrame < len(self.sprites):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.sprites))
                else:
                    self.currentFrame = 0
                bottom = self.imgRect.bottom
                left = self.imgRect.left
                self.image = self.sprites[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.bottom = bottom
                self.imgRect.left = left
        elif self.textbox != "complete":
            if self.textbox.startAdvance:
                self.currentFrame = 23
            if self.textbox.talking:
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talking):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talking))
                    else:
                        self.currentFrame = 0
                    bottom = self.imgRect.bottom
                    left = self.imgRect.left
                    self.image = self.talking[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.left = left
            else:
                if now - self.lastUpdate > 30:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.sprites):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.sprites))
                    else:
                        self.currentFrame = 0
                    bottom = self.imgRect.bottom
                    left = self.imgRect.left
                    self.image = self.sprites[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.left = left


class TutorialBowser(StateMachine):
    idle = State("Idle", initial=True)
    goingToPlayer = State("Towards Player")
    punch = State("Punch")
    hit = State("hit")

    startWalking = idle.to(goingToPlayer)
    giveUp = goingToPlayer.to(idle)
    attack = goingToPlayer.to(punch)
    attackOver = punch.to(idle)
    instaPunch = idle.to(punch)
    idleHit = idle.to(hit)
    moveHit = goingToPlayer.to(hit)
    getUp = hit.to(goingToPlayer)

    def init(self, game, pos):
        self.game = game
        self.game.enemies.append(self)
        self.game.sprites.append(self)

        self.loadImages()
        self.cooldown = 0
        self.alpha = 255
        self.hitRange = 1.3
        self.speed = 2.5
        self.lastUpdate = 0
        self.currentFrame = 0
        self.hitTimer = 0
        self.dead = False
        self.facing = "right"
        self.image = self.idleImages[0]
        self.imgRect = self.image.get_rect()
        self.shadow = self.shadowFrame
        self.rect = self.shadow.get_rect()
        self.hpSpeed = 0
        self.rect.center = pos
        self.imgRect.centerx = self.rect.centerx + 5
        self.imgRect.bottom = self.rect.centery + 10

        # Stats
        self.stats = {"maxHP": 10, "hp": 10, "pow": 9, "def": 5, "exp": 3, "coins": 0, "name": "Bowser"}
        self.rectHP = 0

        self.description = []
        self.description.append("It's Bowser!")
        self.description.append("You know Bowser, right?/p\nHe kidnaps the princess every week?")
        self.description.append("Max HP is " + str(self.stats["maxHP"]) + ",/p\nAttack is " + str(
            self.stats["pow"]) + ",/p\nDefence is " + str(self.stats["def"]) + ".")
        self.description.append("Bowser has NEVER succeeded in\nkidnapping Princess Peach.")
        self.description.append("So make sure it stays that way and\nwin, Mario!")

    def loadImages(self):
        sheet = spritesheet("sprites/bowserBattle.png", "sprites/bowserBattle.xml")

        self.shadowFrame = sheet.getImageName("shadow.png")

        self.hitFrame = sheet.getImageName("hit.png")

        self.idleImages = [sheet.getImageName("idle_1.png"),
                           sheet.getImageName("idle_2.png"),
                           sheet.getImageName("idle_3.png"),
                           sheet.getImageName("idle_4.png"),
                           sheet.getImageName("idle_5.png"),
                           sheet.getImageName("idle_6.png"),
                           sheet.getImageName("idle_7.png"),
                           sheet.getImageName("idle_8.png"),
                           sheet.getImageName("idle_9.png"),
                           sheet.getImageName("idle_10.png"),
                           sheet.getImageName("idle_11.png"),
                           sheet.getImageName("idle_12.png"),
                           sheet.getImageName("idle_13.png"),
                           sheet.getImageName("idle_14.png"),
                           sheet.getImageName("idle_15.png"),
                           ]

        self.punchingFrames = [sheet.getImageName("punching_1.png"),
                               sheet.getImageName("punching_2.png"),
                               sheet.getImageName("punching_3.png"),
                               sheet.getImageName("punching_4.png"),
                               sheet.getImageName("punching_5.png"),
                               sheet.getImageName("punching_6.png"),
                               sheet.getImageName("punching_7.png"),
                               sheet.getImageName("punching_8.png"),
                               sheet.getImageName("punching_9.png"),
                               sheet.getImageName("punching_10.png"),
                               sheet.getImageName("punching_11.png"),
                               sheet.getImageName("punching_12.png"),
                               sheet.getImageName("punching_13.png"),
                               sheet.getImageName("punching_14.png"),
                               sheet.getImageName("punching_15.png"),
                               sheet.getImageName("punching_16.png"),
                               sheet.getImageName("punching_17.png"),
                               sheet.getImageName("punching_18.png"),
                               sheet.getImageName("punching_19.png")]

        self.walkingFrames = [sheet.getImageName("walking_1.png"),
                              sheet.getImageName("walking_2.png"),
                              sheet.getImageName("walking_3.png"),
                              sheet.getImageName("walking_4.png"),
                              sheet.getImageName("walking_5.png"),
                              sheet.getImageName("walking_6.png"),
                              sheet.getImageName("walking_7.png"),
                              sheet.getImageName("walking_8.png"),
                              sheet.getImageName("walking_9.png"),
                              sheet.getImageName("walking_10.png"),
                              sheet.getImageName("walking_11.png"),
                              sheet.getImageName("walking_12.png"),
                              sheet.getImageName("walking_13.png"),
                              sheet.getImageName("walking_14.png"),
                              sheet.getImageName("walking_15.png")]

    def hpMath(self):
        if self.rectHP > self.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = ((self.rectHP - self.stats["hp"]) / 30) * -1
        elif self.rectHP < self.stats["hp"] and self.hpSpeed == 0:
            if self.rectHP != 0:
                self.hpSpeed = (self.stats["hp"] - self.rectHP) / 30
            else:
                self.hpSpeed = (self.stats["hp"] - self.rectHP) / 180

        if self.hpSpeed != 0:
            if self.rectHP + self.hpSpeed > self.stats["hp"] and self.hpSpeed < 0:
                self.rectHP += self.hpSpeed
            elif self.rectHP + self.hpSpeed < self.stats["hp"] and self.hpSpeed > 0:
                self.rectHP += self.hpSpeed
            else:
                self.rectHP = self.stats["hp"]
                self.hpSpeed = 0

    def update(self):
        self.animate()
        self.hpMath()
        playerRect = self.rect.copy()
        playerRect.width = playerRect.width * self.hitRange

        if self.is_idle:
            if playerRect.colliderect(
                    self.game.player.rect) and self.cooldown == 0 and not self.game.player.jumping and not self.game.player.dead:
                self.currentFrame = 0
                self.game.bowserPunch.play()
                self.instaPunch()
            elif self.cooldown > 0:
                self.cooldown -= 1
            else:
                chance = random.randrange(0, 100)
                if chance == 0 and not self.game.player.dead:
                    self.startWalking()
        elif self.is_goingToPlayer:
            self.angle = get_angle(self.rect.center, self.game.player.rect.center)
            self.rect.center = project(self.rect.center, self.angle, self.speed)
            chance = random.randrange(0, 250)
            if chance == 0 or self.game.player.dead:
                self.giveUp()
            elif playerRect.colliderect(self.game.player.rect) and self.cooldown == 0 and not self.game.player.jumping:
                self.currentFrame = 0
                self.game.bowserPunch.play()
                self.attack()
            elif self.cooldown > 0:
                self.cooldown -= 1
        elif self.is_punch:
            if self.game.player.dead:
                self.attackOver()

        if self.cooldown > 0:
            self.cooldown -= 1

        if not self.is_punch:
            if self.game.player.stats["hp"] != 0:
                keys = pg.key.get_pressed()
                doubleDamageM = False
                hits = pg.sprite.collide_rect(self.game.player, self)
                if hits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                    if keys[
                        pg.K_m] and self.game.player.going == "down" and self.game.player.rect.bottom <= self.imgRect.top + 50:
                        doubleDamageM = True
                    if hitsRound2:
                        if self.game.player.going == "down" and self.game.player.jumping and self.stats[
                            "hp"] > 0 and not self.is_hit and not self.is_punch and self.cooldown == 0:
                            if doubleDamageM:
                                HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                           (2 * (self.game.player.stats["pow"] - self.stats["def"])))
                                self.stats["hp"] -= 2 * (self.game.player.stats["pow"] - self.stats["def"])
                                if self.stats["hp"] <= 0:
                                    self.game.enemyDieSound.play()
                                self.game.enemyHitSound.play()
                                if self.is_idle:
                                    self.idleHit()
                                elif self.is_goingToPlayer:
                                    self.moveHit()
                                self.cooldown = fps * 2
                            else:
                                HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                           (self.game.player.stats["pow"] - self.stats["def"]))
                                self.stats["hp"] -= (self.game.player.stats["pow"] - self.stats["def"])
                                if self.stats["hp"] <= 0:
                                    self.game.enemyDieSound.play()
                                self.game.enemyHitSound.play()
                                if self.is_idle:
                                    self.idleHit()
                                elif self.is_goingToPlayer:
                                    self.moveHit()
                                self.cooldown = fps * 2
                            self.game.player.airTimer = 0
                        else:
                            if not self.game.player.hit and self.stats[
                                "hp"] > 0 and not self.is_hit and self.game.player.canBeHit and self.game.player.stats[
                                "hp"] > self.stats["pow"] - self.game.player.stats["def"]:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.player.rect.left, self.game.player.rect.top - 2),
                                           (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                                self.game.player.stats["hp"] -= (
                                    max(self.stats["pow"] - self.game.player.stats["def"], 1))
                                if self.game.player.stats["hp"] <= 0:
                                    self.game.player.stats["hp"] = 0
                                    self.game.player.currentFrame = 0
                                self.game.player.hitTime = pg.time.get_ticks()
                                self.game.playerHitSound.play()
                                self.game.player.canBeHit = False
                                self.game.player.hit = True
        else:
            if self.game.player.stats["hp"] != 0:
                hits = self.imgRect.colliderect(self.game.playerCol.rect)
                if hits:
                    if self.rect.bottom > self.game.player.rect.centery > self.rect.top:
                        if not self.game.player.hit and self.stats["hp"] > 0 and self.game.player.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.player.rect.left, self.game.player.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                            self.game.player.stats["hp"] -= (max(self.stats["pow"] - self.game.player.stats["def"], 1))
                            if self.game.player.stats["hp"] <= 0:
                                self.game.player.stats["hp"] = 0
                                self.game.player.currentFrame = 0
                            self.game.player.hitTime = pg.time.get_ticks()
                            self.game.playerHitSound.play()
                            self.game.player.canBeHit = False
                            self.game.player.hit = True

        if self.stats["hp"] <= 0:
            self.cooldown = 10000
            self.alpha -= 10

        if self.alpha <= 0:
            self.game.battleXp += self.stats["exp"]
            self.game.sprites.remove(self)
            self.game.enemies.remove(self)

        if self.facing == "right":
            self.imgRect.centerx = self.rect.centerx + 5
            self.imgRect.bottom = self.rect.centery + 10
        else:
            self.imgRect.centerx = self.rect.centerx - 5
            self.imgRect.bottom = self.rect.centery + 10

    def animate(self):
        now = pg.time.get_ticks()
        if self.is_idle:
            if now - self.lastUpdate > 45:
                self.lastUpdate = now
                if self.currentFrame < len(self.idleImages):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.idleImages))
                else:
                    self.currentFrame = 0
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                if self.game.player.rect.centerx < self.rect.centerx:
                    self.image = pg.transform.flip(self.idleImages[self.currentFrame], True, False)
                    self.facing = "left"
                else:
                    self.image = self.idleImages[self.currentFrame]
                    self.facing = "right"
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        elif self.is_goingToPlayer:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.walkingFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingFrames))
                else:
                    self.currentFrame = 0
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                if self.game.player.rect.centerx < self.rect.centerx:
                    self.image = pg.transform.flip(self.walkingFrames[self.currentFrame], True, False)
                    self.facing = "left"
                else:
                    self.image = self.walkingFrames[self.currentFrame]
                    self.facing = "right"
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        elif self.is_punch:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.punchingFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1) % (len(self.punchingFrames))
                else:
                    self.cooldown = 10
                    self.attackOver()
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                if self.facing == "left":
                    self.image = pg.transform.flip(self.punchingFrames[self.currentFrame], True, False)
                else:
                    self.image = self.punchingFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        elif self.is_hit:
            self.currentFrame = 0
            centerx = self.imgRect.centerx
            bottom = self.imgRect.bottom
            if self.facing == "left":
                self.image = pg.transform.flip(self.hitFrame, True, False)
            else:
                self.image = self.hitFrame
            self.imgRect = self.image.get_rect()
            self.imgRect.centerx = centerx
            self.imgRect.bottom = bottom
            if self.cooldown == fps:
                self.getUp()
            else:
                self.cooldown -= 1


class Mammoshka(StateMachine):
    idle = State("Idle", initial=True)
    hit = State("hit")
    walking = State("Walking")
    jumping = State("Jumping")
    land = State("Land")
    charge = State("Charge")
    run = State("Run")

    idleHit = idle.to(hit)
    getUp = hit.to(idle)
    walkHit = walking.to(hit)
    startWalk = idle.to(walking)
    stopWalk = walking.to(idle)
    startCharge = idle.to(charge)
    go = charge.to(run)
    stop = run.to(idle)
    startJump = idle.to(jumping)
    stopJump = jumping.to(land)
    finishJump = land.to(idle)

    def init(self, game, pos):
        self.game = game
        self.game.enemies.append(self)
        self.game.sprites.append(self)
        self.offset = -15
        self.minOffset = -15
        self.maxOffset = 5000
        self.loadImages()
        self.cooldown = 0
        self.jumpTime = fps * 5
        self.alpha = 255
        self.hitRange = 1.3
        self.speed = 4
        self.lastUpdate = 0
        self.currentFrame = 0
        self.hitTimer = 0
        self.dead = False
        self.facing = "right"
        self.image = self.idleImages[0]
        self.imgRect = self.image.get_rect()
        self.shadow = self.shadowFrame
        self.rect = self.shadow.get_rect()
        self.hpSpeed = 0
        self.rect.center = pos
        self.imgRect.centerx = self.rect.centerx + 5
        self.imgRect.bottom = self.rect.centery + 10

        # Stats
        self.stats = {"maxHP": 150, "hp": 150, "pow": 25, "def": 15, "exp": 40, "coins": 100, "name": "Mammoshka"}
        self.rectHP = 0

        self.description = ["That's Mammoshka!",
                            "Mammoshka was sent here by\nFawful in order to beat us.",
                            "Max HP is " + str(self.stats["maxHP"]) + ",/p\nAttack is " + str(
                                self.stats["pow"]) + ",/p\nDefence is " + str(self.stats["def"]) + ".",
                            "I don't know where he got his\nhelmet from.",
                            "I wouldn't want to jump on it,\nthough.",
                            "Try using your hammers!"]

    def loadImages(self):
        sheet = spritesheet("sprites/Mammoshka Battle.png", "sprites/Mammoshka Battle.xml")

        self.shadowFrame = sheet.getImageName("shadow.png")

        self.hitFrame = sheet.getImageName("hit.png")

        self.idleImages = [sheet.getImageName("idle_1.png"),
                           sheet.getImageName("idle_2.png"),
                           sheet.getImageName("idle_3.png"),
                           sheet.getImageName("idle_4.png"),
                           sheet.getImageName("idle_5.png"),
                           sheet.getImageName("idle_6.png"),
                           sheet.getImageName("idle_7.png"),
                           sheet.getImageName("idle_8.png"),
                           sheet.getImageName("idle_9.png"),
                           sheet.getImageName("idle_10.png"),
                           sheet.getImageName("idle_11.png"),
                           sheet.getImageName("idle_12.png"),
                           sheet.getImageName("idle_13.png"),
                           sheet.getImageName("idle_14.png"),
                           sheet.getImageName("idle_15.png"),
                           sheet.getImageName("idle_16.png")
                           ]

        self.walkingImages = [sheet.getImageName("walking_1.png"),
                              sheet.getImageName("walking_2.png"),
                              sheet.getImageName("walking_3.png"),
                              sheet.getImageName("walking_4.png"),
                              sheet.getImageName("walking_5.png"),
                              sheet.getImageName("walking_6.png"),
                              sheet.getImageName("walking_7.png"),
                              sheet.getImageName("walking_8.png"),
                              sheet.getImageName("walking_9.png"),
                              sheet.getImageName("walking_10.png"),
                              sheet.getImageName("walking_11.png"),
                              sheet.getImageName("walking_12.png"),
                              sheet.getImageName("walking_13.png"),
                              sheet.getImageName("walking_14.png")]

        self.runImages = [sheet.getImageName("running_1.png"),
                          sheet.getImageName("running_2.png"),
                          sheet.getImageName("running_3.png"),
                          sheet.getImageName("running_4.png"),
                          sheet.getImageName("running_5.png"),
                          sheet.getImageName("running_6.png"),
                          sheet.getImageName("running_7.png"),
                          sheet.getImageName("running_8.png"),
                          sheet.getImageName("running_9.png"),
                          sheet.getImageName("running_10.png")]

        self.chargeImages = [sheet.getImageName("charging_1.png"),
                             sheet.getImageName("charging_2.png"),
                             sheet.getImageName("charging_3.png"),
                             sheet.getImageName("charging_4.png"),
                             sheet.getImageName("charging_5.png"),
                             sheet.getImageName("charging_6.png"),
                             sheet.getImageName("charging_7.png"),
                             sheet.getImageName("charging_8.png"),
                             sheet.getImageName("charging_9.png"),
                             sheet.getImageName("charging_10.png")]

        self.jumpingImages = [sheet.getImageName("jumping_1.png"),
                              sheet.getImageName("jumping_2.png"),
                              sheet.getImageName("jumping_3.png"),
                              sheet.getImageName("jumping_4.png")]

        self.landingImages = [sheet.getImageName("land_1.png"),
                              sheet.getImageName("land_2.png"),
                              sheet.getImageName("land_3.png"),
                              sheet.getImageName("land_4.png"),
                              sheet.getImageName("land_5.png"),
                              sheet.getImageName("land_6.png")]

    def hpMath(self):
        if self.rectHP > self.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = ((self.rectHP - self.stats["hp"]) / 30) * -1
        elif self.rectHP < self.stats["hp"] and self.hpSpeed == 0:
            if self.rectHP != 0:
                self.hpSpeed = (self.stats["hp"] - self.rectHP) / 30
            else:
                self.hpSpeed = (self.stats["hp"] - self.rectHP) / 180

        if self.hpSpeed != 0:
            if self.rectHP + self.hpSpeed > self.stats["hp"] and self.hpSpeed < 0:
                self.rectHP += self.hpSpeed
            elif self.rectHP + self.hpSpeed < self.stats["hp"] and self.hpSpeed > 0:
                self.rectHP += self.hpSpeed
            else:
                self.rectHP = self.stats["hp"]
                self.hpSpeed = 0

    def update(self):
        self.animate()
        self.hpMath()
        playerRect = self.rect.copy()
        playerRect.width = playerRect.width * self.hitRange

        if self.is_idle:
            chance = random.randrange(0, 200)
            if chance == 0 and self.cooldown <= 0:
                chance = random.randrange(0, 3)
                if chance == 0:
                    self.startWalk()
                elif chance == 1:
                    self.game.mammoshkaBounce.play()
                    self.startJump()
                    self.jumpTime = fps * 5
                elif chance == 2:
                    self.counter = 0
                    self.startCharge()
        elif self.is_walking:
            if self.game.leader == "mario":
                self.angle = get_angle(self.rect.center, self.game.player.rect.center)
            else:
                self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
            self.rect.center = project(self.rect.center, self.angle, self.speed)
            chance = random.randrange(0, 200)
            if chance == 0:
                self.stopWalk()
        elif self.is_jumping:
            if self.offset < self.maxOffset and self.jumpTime > 0:
                self.offset += 30
            else:
                if self.offset >= self.maxOffset:
                    if self.game.leader == "mario":
                        self.angle = get_angle(self.rect.center, self.game.player.rect.center)
                    else:
                        self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
                    self.rect.center = project(self.rect.center, self.angle, self.speed * 2)

                self.jumpTime -= 1
                if self.offset > self.minOffset:
                    if self.jumpTime <= 0:
                        self.offset -= 60
                else:
                    self.currentFrame = 0
                    self.stopJump()
        elif self.is_charge:
            self.counter += 1
            if self.counter >= fps * 5:
                if self.game.leader == "mario":
                    self.angle = get_angle(self.rect.center, self.game.player.rect.center)
                else:
                    self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
                self.counter = 0
                self.go()
        elif self.is_run:
            self.rect.center = project(self.rect.center, self.angle, self.speed * 5)
            for wall in self.game.walls:
                if wall.rect.colliderect(self.rect):
                    if self.is_run:
                        self.cooldown = fps
                        self.stop()
                        self.idleHit()

        if self.cooldown > 0:
            self.cooldown -= 1

        if self.game.player.stats["hp"] != 0:
            hits = pg.sprite.collide_rect(self.game.player, self)
            if hits:
                hitsRound2 = self.imgRect.colliderect(self.game.player.rect)
                if hitsRound2:
                    if not self.game.player.hit and self.stats[
                        "hp"] > 0 and not self.is_hit and self.game.player.canBeHit:
                        HitNumbers(self.game, self.game.room,
                                   (self.game.player.rect.left, self.game.player.rect.top - 2),
                                   (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                        self.game.player.stats["hp"] -= (
                            max(self.stats["pow"] - self.game.player.stats["def"], 1))
                        if self.game.player.stats["hp"] <= 0:
                            self.game.player.stats["hp"] = 0
                            self.game.player.currentFrame = 0
                        self.game.player.hitTime = pg.time.get_ticks()
                        self.game.playerHitSound.play()
                        self.game.player.canBeHit = False
                        self.game.player.hit = True

        if self.game.follower.stats["hp"] != 0:
            hits = pg.sprite.collide_rect(self.game.follower, self)
            if hits:
                hitsRound2 = self.imgRect.colliderect(self.game.follower.rect)
                if hitsRound2:
                    if not self.game.follower.hit and self.stats[
                        "hp"] > 0 and not self.is_hit and self.game.follower.canBeHit:
                        HitNumbers(self.game, self.game.room,
                                   (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                   (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                        self.game.follower.stats["hp"] -= (
                            max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                        if self.game.follower.stats["hp"] <= 0:
                            self.game.follower.stats["hp"] = 0
                            self.game.follower.currentFrame = 0
                        self.game.follower.hitTime = pg.time.get_ticks()
                        self.game.playerHitSound.play()
                        self.game.follower.canBeHit = False
                        self.game.follower.hit = True

        if self.is_idle or self.is_walking:
            if self.stats["hp"] != 0 and self.game.player.isHammer is not None and not self.is_run:
                hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                    if hammerHitsRound2 and not self.is_hit and self.stats["hp"] > 0:
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1))
                        self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        if self.is_idle:
                            self.idleHit()
                        elif self.is_walking:
                            self.walkHit()
                        self.cooldown = fps * 2.5

            if self.stats["hp"] != 0 and self.game.follower.isHammer is not None and not self.is_run:
                hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                    if hammerHitsRound2 and not self.is_hit and self.stats["hp"] > 0:
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1))
                        self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        if self.is_idle:
                            self.idleHit()
                        elif self.is_walking:
                            self.walkHit()
                        self.cooldown = fps * 2.5

        if self.stats["hp"] <= 0:
            self.cooldown = 10000
            self.alpha -= 10

        if self.alpha <= 0:
            self.game.battleXp += self.stats["exp"]
            self.game.battleCoins += self.stats["coins"]
            self.game.sprites.remove(self)
            self.game.enemies.remove(self)

        if self.facing == "right":
            self.imgRect.centerx = self.rect.centerx
            self.imgRect.bottom = self.rect.centery - self.offset
        else:
            self.imgRect.centerx = self.rect.centerx
            self.imgRect.bottom = self.rect.centery - self.offset

    def animate(self):
        now = pg.time.get_ticks()
        if self.is_idle:
            if now - self.lastUpdate > 45:
                self.lastUpdate = now
                if self.currentFrame < len(self.idleImages):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.idleImages))
                else:
                    self.currentFrame = 0
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                if self.game.leader == "mario":
                    if self.game.player.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.idleImages[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.idleImages[self.currentFrame]
                        self.facing = "right"
                else:
                    if self.game.follower.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.idleImages[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.idleImages[self.currentFrame]
                        self.facing = "right"
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        elif self.is_walking:
            if now - self.lastUpdate > 45:
                self.lastUpdate = now
                if self.currentFrame < len(self.walkingImages):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.walkingImages))
                else:
                    self.currentFrame = 0
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                if self.game.leader == "mario":
                    if self.game.player.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.walkingImages[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.walkingImages[self.currentFrame]
                        self.facing = "right"
                else:
                    if self.game.follower.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.walkingImages[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.walkingImages[self.currentFrame]
                        self.facing = "right"
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        elif self.is_charge:
            if now - self.lastUpdate > 45:
                self.lastUpdate = now
                if self.currentFrame < len(self.chargeImages):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.chargeImages))
                else:
                    self.currentFrame = 0
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                if self.game.leader == "mario":
                    if self.game.player.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.chargeImages[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.chargeImages[self.currentFrame]
                        self.facing = "right"
                else:
                    if self.game.follower.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.chargeImages[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.chargeImages[self.currentFrame]
                        self.facing = "right"
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        elif self.is_run:
            if now - self.lastUpdate > 45:
                self.lastUpdate = now
                if self.currentFrame < len(self.runImages):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.runImages))
                else:
                    self.currentFrame = 0
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                if self.facing == "left":
                    self.image = pg.transform.flip(self.runImages[self.currentFrame], True, False)
                else:
                    self.image = self.runImages[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        elif self.is_jumping:
            if now - self.lastUpdate > 45:
                self.lastUpdate = now
                if self.currentFrame < len(self.jumpingImages):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.jumpingImages))
                else:
                    self.currentFrame = 0
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                if self.facing == "left":
                    self.image = pg.transform.flip(self.jumpingImages[self.currentFrame], True, False)
                else:
                    self.image = self.jumpingImages[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        elif self.is_land:
            if now - self.lastUpdate > 45:
                self.lastUpdate = now
                if self.currentFrame < len(self.landingImages) - 1:
                    self.currentFrame = (self.currentFrame + 1) % (len(self.landingImages))
                else:
                    self.cooldown = 15
                    self.finishJump()
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                if self.facing == "left":
                    self.image = pg.transform.flip(self.landingImages[self.currentFrame], True, False)
                else:
                    self.image = self.landingImages[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        elif self.is_hit:
            self.currentFrame = 0
            centerx = self.imgRect.centerx
            bottom = self.imgRect.bottom
            if self.facing == "left":
                self.image = pg.transform.flip(self.hitFrame, True, False)
            else:
                self.image = self.hitFrame
            self.imgRect = self.image.get_rect()
            self.imgRect.centerx = centerx
            self.imgRect.bottom = bottom
            if self.cooldown == 0:
                self.getUp()
                chance = random.randrange(0, 3)
                if chance == 0:
                    self.startWalk()
                elif chance == 1:
                    self.game.mammoshkaBounce.play()
                    self.startJump()
                    self.jumpTime = fps * 5
                elif chance == 2:
                    self.counter = 0
                    self.startCharge()
            else:
                self.cooldown -= 1


class DarkFawful(StateMachine):
    idle = State("Idle", initial=True)
    walking = State("Walking")
    hit = State("hit")
    goUp = State("Go Up")
    endGoUp = State("End Go Up")
    startGoDown = State("Start Go Down")
    goDown = State("Go Down")
    fly = State("Fly")
    goToPortal = State("Go to portal")
    makePortalA = State("Make portal A")
    makePortalB = State("Make portal B")
    startFire = State("Start Fire")
    fire = State("fire")
    endFire = State("End Fire")
    toFlyAround = State("To Fly Around")
    flyAround = State("Fly Around")
    fromFlyAround = State("from fly around")

    startWalking = idle.to(walking)
    giveUp = walking.to(idle)
    startGoUp = idle.to(goUp)
    startEndGoUp = goUp.to(endGoUp)
    startFly = endGoUp.to(fly)
    endGoDown = goDown.to(idle)
    endFly = fly.to(startGoDown)
    beginGoDown = startGoDown.to(goDown)
    getHit = idle.to(hit)
    getUp = hit.to(idle)
    startGoToPortal = fly.to(goToPortal)
    beginPortalA = goToPortal.to(makePortalA)
    endPortalA = makePortalA.to(goToPortal)
    beginPortalB = goToPortal.to(makePortalB)
    endPortalB = makePortalB.to(startGoDown)
    enterGun = idle.to(startFire)
    beginFire = startFire.to(fire)
    exitGun = fire.to(endFire)
    asYouWere = endFire.to(idle)
    beginArialStrike = fly.to(toFlyAround)
    midArialStrike = toFlyAround.to(flyAround)
    endAreialStrike = flyAround.to(fromFlyAround)
    beginLanding = fromFlyAround.to(startGoDown)

    def init(self, game, pos):
        self.game = game
        self.game.enemies.append(self)
        self.game.sprites.append(self)

        self.loadImages()
        self.cooldown = 0
        self.alpha = 255
        self.hitRange = 1.3
        self.speed = 4
        self.lastUpdate = 0
        self.currentFrame = 0
        self.hitTimer = 0
        self.dead = False
        self.facing = "right"
        self.image = self.idleImages[0]
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.hpSpeed = 0
        self.offset = 0
        self.rect.center = pos
        self.imgRect.centerx = self.rect.centerx
        self.imgRect.bottom = self.rect.centery + 7 - self.offset
        self.portalA = None
        self.portalB = None

        # Stats
        self.stats = {"maxHP": 400, "hp": 400, "pow": 75, "def": 75, "exp": 200, "coins": 200, "name": "Dark Fawful"}
        self.rectHP = 0

        self.description = ["Fawful is there!",
                            "After Count Bleck gave him a power\nboost, he wants to take revenge on\nyou guys!",
                            "Max HP is " + str(self.stats["maxHP"]) + ",/p\nAttack is " + str(
                                self.stats["pow"]) + ",/p\nDefence is " + str(self.stats["def"]) + ".",
                            "The Beanbean kingdom is home to\nmany bean-themed creatures.",
                            "Fawful just happens to be one of\nthe more./9/6./9/6./p evil ones.",
                            "You can't even hit him while\nhe's flying!"]

    def loadImages(self):
        sheet = spritesheet("sprites/dark fawful.png", "sprites/dark fawful.xml")

        self.ballImage = sheet.getImageName("ball.png")

        self.ballShadow = sheet.getImageName("ballShadow.png")

        self.shadow = sheet.getImageName("shadow.png")

        self.hitFrame = sheet.getImageName("hit.png")

        self.idleImages = [sheet.getImageName("idle_1.png"),
                           sheet.getImageName("idle_2.png"),
                           sheet.getImageName("idle_3.png"),
                           sheet.getImageName("idle_4.png"),
                           sheet.getImageName("idle_5.png"),
                           sheet.getImageName("idle_6.png"),
                           sheet.getImageName("idle_7.png"),
                           sheet.getImageName("idle_8.png"),
                           sheet.getImageName("idle_9.png"),
                           sheet.getImageName("idle_10.png"),
                           sheet.getImageName("idle_11.png"),
                           sheet.getImageName("idle_12.png"),
                           sheet.getImageName("idle_13.png"),
                           sheet.getImageName("idle_14.png"),
                           sheet.getImageName("idle_15.png")]

        self.floatFrames = [sheet.getImageName("float_1.png"),
                            sheet.getImageName("float_2.png"),
                            sheet.getImageName("float_3.png"),
                            sheet.getImageName("float_4.png")]

        self.openCapeFrames = [sheet.getImageName("open_cape_1.png"),
                               sheet.getImageName("open_cape_2.png"),
                               sheet.getImageName("open_cape_3.png"),
                               sheet.getImageName("open_cape_4.png"),
                               sheet.getImageName("open_cape_5.png"),
                               sheet.getImageName("open_cape_6.png"),
                               sheet.getImageName("open_cape_7.png"),
                               sheet.getImageName("open_cape_8.png"),
                               sheet.getImageName("open_cape_9.png"),
                               sheet.getImageName("open_cape_10.png")]

        self.closeCapeFrames = [sheet.getImageName("close_cape_1.png"),
                                sheet.getImageName("close_cape_2.png"),
                                sheet.getImageName("close_cape_3.png"),
                                sheet.getImageName("close_cape_4.png"),
                                sheet.getImageName("close_cape_5.png"),
                                sheet.getImageName("close_cape_6.png")]

        self.flyFrames = [sheet.getImageName("fly_1.png"),
                          sheet.getImageName("fly_2.png"),
                          sheet.getImageName("fly_3.png"),
                          sheet.getImageName("fly_4.png"),
                          sheet.getImageName("fly_5.png")]

        self.spinFrames = [sheet.getImageName("spinning_1.png"),
                           sheet.getImageName("spinning_2.png"),
                           sheet.getImageName("spinning_3.png"),
                           sheet.getImageName("spinning_4.png"),
                           sheet.getImageName("spinning_5.png"),
                           sheet.getImageName("spinning_6.png"),
                           sheet.getImageName("spinning_7.png"),
                           sheet.getImageName("spinning_8.png")]

        self.leftPortalFrames = [sheet.getImageName("portal_left_1.png"),
                                 sheet.getImageName("portal_left_2.png"),
                                 sheet.getImageName("portal_left_3.png"),
                                 sheet.getImageName("portal_left_4.png"),
                                 sheet.getImageName("portal_left_5.png"),
                                 sheet.getImageName("portal_left_6.png"),
                                 sheet.getImageName("portal_left_7.png"),
                                 sheet.getImageName("portal_left_8.png"),
                                 sheet.getImageName("portal_left_9.png"),
                                 sheet.getImageName("portal_left_10.png"),
                                 sheet.getImageName("portal_left_11.png"),
                                 sheet.getImageName("portal_left_12.png"),
                                 sheet.getImageName("portal_left_13.png"),
                                 sheet.getImageName("portal_left_14.png")]

        self.rightPortalFrames = [sheet.getImageName("portal_right_1.png"),
                                  sheet.getImageName("portal_right_2.png"),
                                  sheet.getImageName("portal_right_3.png"),
                                  sheet.getImageName("portal_right_4.png"),
                                  sheet.getImageName("portal_right_5.png"),
                                  sheet.getImageName("portal_right_6.png"),
                                  sheet.getImageName("portal_right_7.png"),
                                  sheet.getImageName("portal_right_8.png"),
                                  sheet.getImageName("portal_right_9.png"),
                                  sheet.getImageName("portal_right_10.png"),
                                  sheet.getImageName("portal_right_11.png"),
                                  sheet.getImageName("portal_right_12.png"),
                                  sheet.getImageName("portal_right_13.png"),
                                  sheet.getImageName("portal_right_14.png")]

        self.enterGunFrames = [sheet.getImageName("enter_gun_1.png"),
                               sheet.getImageName("enter_gun_2.png"),
                               sheet.getImageName("enter_gun_3.png"),
                               sheet.getImageName("enter_gun_4.png"),
                               sheet.getImageName("enter_gun_5.png"),
                               sheet.getImageName("enter_gun_6.png"),
                               sheet.getImageName("enter_gun_7.png"),
                               sheet.getImageName("enter_gun_8.png"),
                               sheet.getImageName("enter_gun_9.png"),
                               sheet.getImageName("enter_gun_10.png"),
                               sheet.getImageName("enter_gun_11.png"),
                               sheet.getImageName("enter_gun_12.png")]

        self.fireGunFrames = [sheet.getImageName("fire_gun_1.png"),
                              sheet.getImageName("fire_gun_2.png"),
                              sheet.getImageName("fire_gun_3.png")]

        self.exitGunFrames = [sheet.getImageName("exit_gun_1.png"),
                              sheet.getImageName("exit_gun_2.png"),
                              sheet.getImageName("exit_gun_3.png"),
                              sheet.getImageName("exit_gun_4.png"),
                              sheet.getImageName("exit_gun_5.png"),
                              sheet.getImageName("exit_gun_6.png"),
                              sheet.getImageName("exit_gun_7.png"),
                              sheet.getImageName("exit_gun_8.png"),
                              sheet.getImageName("exit_gun_9.png"),
                              sheet.getImageName("exit_gun_10.png"),
                              sheet.getImageName("exit_gun_11.png"),
                              sheet.getImageName("exit_gun_12.png"),
                              sheet.getImageName("exit_gun_13.png"),
                              sheet.getImageName("exit_gun_14.png"),
                              sheet.getImageName("exit_gun_15.png"),
                              sheet.getImageName("exit_gun_16.png"),
                              sheet.getImageName("exit_gun_17.png"),
                              sheet.getImageName("exit_gun_18.png"),
                              sheet.getImageName("exit_gun_19.png"),
                              sheet.getImageName("exit_gun_20.png"),
                              sheet.getImageName("exit_gun_21.png"),
                              sheet.getImageName("exit_gun_22.png"),
                              sheet.getImageName("exit_gun_23.png"),
                              sheet.getImageName("exit_gun_24.png"),
                              sheet.getImageName("exit_gun_25.png")]

    def hpMath(self):
        if self.rectHP > self.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = ((self.rectHP - self.stats["hp"]) / 30) * -1
        elif self.rectHP < self.stats["hp"] and self.hpSpeed == 0:
            if self.rectHP != 0:
                self.hpSpeed = (self.stats["hp"] - self.rectHP) / 30
            else:
                self.hpSpeed = (self.stats["hp"] - self.rectHP) / 180

        if self.hpSpeed != 0:
            if self.rectHP + self.hpSpeed > self.stats["hp"] and self.hpSpeed < 0:
                self.rectHP += self.hpSpeed
            elif self.rectHP + self.hpSpeed < self.stats["hp"] and self.hpSpeed > 0:
                self.rectHP += self.hpSpeed
            else:
                self.rectHP = self.stats["hp"]
                self.hpSpeed = 0

    def update(self):
        self.animate()
        self.hpMath()

        if self.is_idle:
            self.offset = 0
            chance = random.randrange(0, 100)
            if chance == 0 and not self.game.player.dead and not self.game.follower.dead:
                choice = random.randrange(0, 3)
                if choice == 0:
                    self.startWalking()
                elif choice == 1:
                    self.startGoUp()
                elif choice == 2:
                    self.currentFrame = 0
                    self.enterGun()
        elif self.is_walking:
            self.offset = 10
            if self.game.leader == "mario":
                self.angle = get_angle(self.rect.center, self.game.player.rect.center)
            else:
                self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
            self.rect.center = project(self.rect.center, self.angle, self.speed)
            chance = random.randrange(0, 250)
            if chance == 0 or (self.game.player.dead or self.game.follower.dead):
                self.giveUp()
        elif self.is_goUp:
            if self.offset < 120:
                self.offset += 1
            else:
                self.currentFrame = 0
                self.startEndGoUp()
        elif self.is_goDown:
            if self.offset > 0:
                self.offset -= 1
            else:
                self.currentFrame = 0
                self.endGoDown()
        elif self.is_fire:
            self.offset = 0
            chance = random.randrange(0, 200)
            if chance == 0:
                self.exitGun()
        elif self.is_fly:
            chance = random.randrange(0, 100)
            if chance == 0 and not self.game.player.dead and not self.game.follower.dead:
                choose = random.randrange(0, 3)
                if self.portalA is None and self.portalB is None:
                    choose = 1
                if choose == 0:
                    self.currentFrame = 0
                    self.endFly()
                elif choose == 1:
                    if self.portalA in self.game.sprites:
                        self.game.sprites.remove(self.portalA)
                    if self.portalB in self.game.sprites:
                        self.game.sprites.remove(self.portalB)
                    self.portalA = None
                    self.portalB = None
                    self.angle = random.randrange(0, 360)
                    self.vx = project(self.rect.center, self.angle, self.speed)[0] - self.rect.centerx
                    self.vy = project(self.rect.center, self.angle, self.speed)[1] - self.rect.centery
                    self.cooldown = fps * 3
                    self.startGoToPortal()
                elif choose == 2:
                    self.currentFrame = 0
                    self.beginArialStrike()
        elif self.is_goToPortal:
            self.rect.centerx += self.vx
            self.rect.centery += self.vy
            self.cooldown -= 1
            for wall in self.game.walls:
                if self.rect.colliderect(wall.rect):
                    if self.game.leader == "mario":
                        self.angle = get_angle(self.rect.center, self.game.player.rect.center)
                    else:
                        self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
                    self.vx = project(self.rect.center, self.angle, self.speed)[0] - self.rect.centerx
                    self.vy = project(self.rect.center, self.angle, self.speed)[1] - self.rect.centery
                    self.rect.centerx += self.vx
                    self.rect.centery += self.vy
            if self.cooldown <= 0:
                if self.portalA is None:
                    self.currentFrame = 0
                    self.beginPortalA()
                    self.cooldown = fps * 10
                elif self.portalB is None:
                    self.currentFrame = 0
                    self.beginPortalB()
        elif self.is_toFlyAround:
            if self.offset > 20:
                self.offset -= 1

            if self.rect.centery > 0:
                self.rect.centery -= 5
            else:
                self.rect.centerx = random.randrange(0, self.game.map.width + 40)
                self.rect.centerx -= 40
                self.rect.centery = random.randrange(0, self.game.map.height + 100)
                self.rect.centery -= 100
                if self.game.leader == "mario":
                    self.angle = get_angle(self.rect.center, self.game.player.rect.center)
                else:
                    self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
                self.midArialStrike()
        elif self.is_flyAround:
            self.rect.center = project(self.rect.center, self.angle, self.speed * 10)

            edge = False
            if self.rect.x > self.game.map.width + 60:
                edge = True
            if self.rect.x < -60:
                edge = True
            if self.rect.y > self.game.map.height + 100:
                edge = True
            if self.rect.y < -100:
                edge = True

            if edge:
                if self.game.leader == "mario":
                    self.angle = get_angle(self.rect.center, self.game.player.rect.center)
                else:
                    self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
                chance = random.randrange(0, 5)
                if chance == 0:
                    self.endAreialStrike()
        elif self.is_fromFlyAround:
            self.angle = get_angle(self.rect.center, (1444, 1682))
            self.rect.center = project(self.rect.center, self.angle, self.speed)

            if abs(1444 - self.rect.centerx) < 50 and abs(1682 - self.rect.centery) < 50:
                self.beginLanding()

        if self.cooldown > 0:
            self.cooldown -= 1

        if self.is_idle or self.is_walking or self.is_fire:
            if self.game.player.stats["hp"] != 0:
                hits = pg.sprite.collide_rect(self.game.player, self)
                if hits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                    if hitsRound2:
                        if self.game.player.going == "down" and self.game.player.jumping and self.stats["hp"] > 0:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (max(2 * (self.game.player.stats["pow"] - self.stats["def"]), 1)))
                            self.stats["hp"] -= (max(2 * (self.game.player.stats["pow"] - self.stats["def"]), 1))
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            if self.is_walking:
                                self.giveUp()
                            if self.is_fire:
                                self.exitGun()
                                self.asYouWere()
                            if not self.is_hit: self.getHit()
                            self.cooldown = fps
                            self.game.player.airTimer = 0
                        else:
                            if not self.game.player.hit and self.stats[
                                "hp"] > 0 and not self.is_hit and self.game.player.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.player.rect.left, self.game.player.rect.top - 2),
                                           (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                                self.game.player.stats["hp"] -= (
                                    max(self.stats["pow"] - self.game.player.stats["def"], 1))
                                if self.game.player.stats["hp"] <= 0:
                                    self.game.player.stats["hp"] = 0
                                    self.game.player.currentFrame = 0
                                self.game.player.hitTime = pg.time.get_ticks()
                                self.game.playerHitSound.play()
                                self.game.player.canBeHit = False
                                self.game.player.hit = True

            if self.game.follower.stats["hp"] != 0:
                hits = pg.sprite.collide_rect(self.game.follower, self)
                if hits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                    if hitsRound2:
                        if self.game.player.going == "down" and self.game.player.jumping and self.stats["hp"] > 0:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                      (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 1)))
                            self.stats["hp"] -= (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 1))
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            if self.is_walking:
                                self.giveUp()
                            if self.is_fire:
                                self.exitGun()
                                self.asYouWere()
                            if not self.is_hit: self.getHit()
                            self.cooldown = fps
                            self.game.follower.airTimer = 0
                        else:
                            if not self.game.follower.hit and self.stats[
                                "hp"] > 0 and not self.is_hit and self.game.follower.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                           (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                                self.game.follower.stats["hp"] -= (
                                    max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                                if self.game.follower.stats["hp"] <= 0:
                                    self.game.follower.stats["hp"] = 0
                                    self.game.follower.currentFrame = 0
                                self.game.follower.hitTime = pg.time.get_ticks()
                                self.game.playerHitSound.play()
                                self.game.follower.canBeHit = False
                                self.game.follower.hit = True

            if self.stats["hp"] != 0 and self.game.player.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                    if hammerHitsRound2 and not self.is_hit and self.stats["hp"] > 0:
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 0))
                        self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 0)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        if self.is_walking:
                            self.giveUp()
                        if self.is_fire:
                            self.exitGun()
                            self.asYouWere()
                        if not self.is_hit: self.getHit()
                        self.cooldown = fps

            if self.stats["hp"] != 0 and self.game.follower.isHammer is not None:
                hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                    if hammerHitsRound2 and not self.is_hit and self.stats["hp"] > 0:
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1))
                        self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        if self.is_walking:
                            self.giveUp()
                        if self.is_fire:
                            self.exitGun()
                            self.asYouWere()
                        if not self.is_hit: self.getHit()
                        self.cooldown = fps

            for entity in self.game.entities:
                if self.rect.colliderect(entity.rect) and not self.is_hit and self.stats["hp"] > 0:
                    if type(entity).__name__ == "Lightning":
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 1))
                        self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 1)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        if self.is_walking:
                            self.giveUp()
                        if self.is_fire:
                            self.exitGun()
                            self.asYouWere()
                        if not self.is_hit: self.getHit()
                        self.cooldown = fps
                    if self.imgRect.colliderect(entity.imgRect):
                        if type(entity).__name__ == "Fireball":
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1))
                            self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1)
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            if self.is_walking:
                                self.giveUp()
                            if self.is_fire:
                                self.exitGun()
                                self.asYouWere()
                            if not self.is_hit: self.getHit()
                            self.cooldown = fps
                            entity.dead = True
        elif not self.is_hit:
            if self.game.player.stats["hp"] != 0:
                hits = self.imgRect.colliderect(self.game.playerCol.rect)
                if hits:
                    if self.rect.bottom > self.game.player.rect.centery > self.rect.top:
                        if not self.game.player.hit and self.stats["hp"] > 0 and self.game.player.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.player.rect.left, self.game.player.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                            self.game.player.stats["hp"] -= (max(self.stats["pow"] - self.game.player.stats["def"], 1))
                            if self.game.player.stats["hp"] <= 0:
                                self.game.player.stats["hp"] = 0
                                self.game.player.currentFrame = 0
                            self.game.player.hitTime = pg.time.get_ticks()
                            self.game.playerHitSound.play()
                            self.game.player.canBeHit = False
                            self.game.player.hit = True

            if self.game.follower.stats["hp"] != 0:
                hits = self.imgRect.colliderect(self.game.followerCol.rect)
                if hits:
                    if self.rect.bottom > self.game.follower.rect.centery > self.rect.top:
                        if not self.game.follower.hit and self.stats["hp"] > 0 and self.game.follower.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                            self.game.follower.stats["hp"] -= (
                                max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                            if self.game.follower.stats["hp"] <= 0:
                                self.game.follower.stats["hp"] = 0
                                self.game.follower.currentFrame = 0
                            self.game.follower.hitTime = pg.time.get_ticks()
                            self.game.playerHitSound.play()
                            self.game.follower.canBeHit = False
                            self.game.follower.hit = True

        if self.stats["hp"] <= 0:
            self.cooldown = 10000
            self.alpha -= 10

        if self.alpha <= 0:
            self.game.battleXp += self.stats["exp"]
            self.game.battleCoins += self.stats["coins"]
            self.game.sprites.remove(self)
            self.game.enemies.remove(self)

        self.imgRect.centerx = self.rect.centerx
        self.imgRect.bottom = self.rect.centery + 7 - self.offset

    def animate(self):
        now = pg.time.get_ticks()
        if self.is_idle:
            if now - self.lastUpdate > 45:
                self.lastUpdate = now
                if self.currentFrame < len(self.idleImages):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.idleImages))
                else:
                    self.currentFrame = 0
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                if self.game.leader == "mario":
                    if self.game.player.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.idleImages[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.idleImages[self.currentFrame]
                        self.facing = "right"
                else:
                    if self.game.follower.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.idleImages[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.idleImages[self.currentFrame]
                        self.facing = "right"
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
        elif self.is_walking:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.floatFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.floatFrames))
                else:
                    self.currentFrame = 0
                center = self.imgRect.center
                if self.game.leader == "mario":
                    if self.game.player.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.floatFrames[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.floatFrames[self.currentFrame]
                        self.facing = "right"
                else:
                    if self.game.follower.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.floatFrames[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.floatFrames[self.currentFrame]
                        self.facing = "right"
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.is_goUp or self.is_goDown:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.spinFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.spinFrames))
                else:
                    self.currentFrame = 0
                center = self.imgRect.center
                self.image = self.spinFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.is_endGoUp:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.openCapeFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.startFly()
                center = self.imgRect.center
                self.image = self.openCapeFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.is_startGoDown:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.closeCapeFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.beginGoDown()
                center = self.imgRect.center
                self.image = self.closeCapeFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.is_startFire:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.enterGunFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.beginFire()
                center = self.imgRect.center
                if self.game.leader == "mario":
                    if self.game.player.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.enterGunFrames[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.enterGunFrames[self.currentFrame]
                        self.facing = "right"
                else:
                    if self.game.follower.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.enterGunFrames[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.enterGunFrames[self.currentFrame]
                        self.facing = "right"
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.is_endFire:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.exitGunFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.asYouWere()
                center = self.imgRect.center
                if self.game.leader == "mario":
                    if self.game.player.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.exitGunFrames[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.exitGunFrames[self.currentFrame]
                        self.facing = "right"
                else:
                    if self.game.follower.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.exitGunFrames[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.exitGunFrames[self.currentFrame]
                        self.facing = "right"
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.is_fire:
            if now - self.lastUpdate > 150:
                self.lastUpdate = now
                if self.currentFrame < len(self.fireGunFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.fireGunFrames))
                else:
                    self.currentFrame = 0
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                if self.game.leader == "mario":
                    if self.game.player.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.fireGunFrames[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.fireGunFrames[self.currentFrame]
                        self.facing = "right"
                    self.imgRect = self.image.get_rect()
                    self.imgRect.centerx = centerx
                    self.imgRect.bottom = bottom
                else:
                    if self.game.follower.rect.centerx > self.rect.centerx:
                        self.image = pg.transform.flip(self.fireGunFrames[self.currentFrame], True, False)
                        self.facing = "left"
                    else:
                        self.image = self.fireGunFrames[self.currentFrame]
                        self.facing = "right"
                    self.imgRect = self.image.get_rect()
                    self.imgRect.centerx = centerx
                    self.imgRect.bottom = bottom
                if self.currentFrame == 1:
                    FawfulBullet(self.game, self.rect.center, self.stats, self.ballImage, self.ballShadow)
        elif self.is_makePortalA:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.leftPortalFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.portalA = FawfulPortal(self.game, (self.rect.centerx - 100, self.rect.centery), self.portalB)
                    self.angle = random.randrange(0, 360)
                    self.vx = project(self.rect.center, self.angle, self.speed)[0] - self.rect.centerx
                    self.vy = project(self.rect.center, self.angle, self.speed)[1] - self.rect.centery
                    self.endPortalA()
                center = self.imgRect.center
                self.image = self.leftPortalFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.is_makePortalB:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.rightPortalFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.endPortalB()
                    self.portalB = FawfulPortal(self.game, (self.rect.centerx + 100, self.rect.centery), self.portalA)
                    self.portalA.partner = self.portalB
                    self.currentFrame = 0
                center = self.imgRect.center
                self.image = self.rightPortalFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.is_fly or self.is_goToPortal or self.is_toFlyAround or self.is_flyAround or self.is_fromFlyAround:
            if now - self.lastUpdate > 60:
                self.lastUpdate = now
                if self.currentFrame < len(self.flyFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.flyFrames))
                else:
                    self.currentFrame = 0
                center = self.imgRect.center
                self.image = self.flyFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.is_hit:
            self.currentFrame = 0
            centerx = self.imgRect.centerx
            bottom = self.imgRect.bottom
            if self.facing == "left":
                self.image = pg.transform.flip(self.hitFrame, True, False)
            else:
                self.image = self.hitFrame
            self.imgRect = self.image.get_rect()
            self.imgRect.centerx = centerx
            self.imgRect.bottom = bottom
            if self.cooldown == 0:
                self.getUp()
                chance = random.randrange(0, 3)
                if chance == 0:
                    self.startWalking()
                elif chance == 1:
                    self.startGoUp()
                elif chance == 2:
                    self.enterGun()
            else:
                self.cooldown -= 1


class FawfulPortal(pg.sprite.Sprite):
    def __init__(self, game, pos, partner):
        self.game = game
        self.game.sprites.append(self)
        sheet = spritesheet("sprites/dark fawful.png", "sprites/dark fawful.xml")
        self.images = [sheet.getImageName("portal_1.png"),
                       sheet.getImageName("portal_2.png"),
                       sheet.getImageName("portal_3.png"),
                       sheet.getImageName("portal_4.png")]
        self.lastUpdate = 0
        self.image = self.images[0]
        self.imgRect = self.image.get_rect()
        self.shadow = sheet.getImageName("portalShadow.png")
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.hasTeleported = 0
        self.currentFrame = 0
        self.imgRect.centerx, self.imgRect.bottom = self.rect.centerx, self.rect.bottom - 5
        self.alpha = 255
        wallRect = self.rect.copy()
        wallRect.width += 50
        wallRect.height += 50
        for wall in self.game.walls:
            if wallRect.colliderect(wall.rect) and self in self.game.sprites:
                self.game.sprites.remove(self)
        self.dead = False
        self.partner = partner

    def update(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 60:
            self.lastUpdate = now
            if self.currentFrame < len(self.images):
                self.currentFrame = (self.currentFrame + 1) % (len(self.images))
            else:
                self.currentFrame = 0
            center = self.imgRect.center
            self.image = self.images[self.currentFrame]
            self.imgRect = self.image.get_rect()
            self.imgRect.center = center

        for sprite in self.game.sprites:
            if self.rect.colliderect(sprite.rect) and self.partner is not None and sprite is not self:
                if self.partner.hasTeleported == 0 and self.partner in self.game.sprites:
                    self.game.portalSound.play()
                    sprite.rect.center = self.partner.rect.center
                    self.hasTeleported = fps

        if self.hasTeleported > 0:
            self.hasTeleported -= 1


class FawfulBullet(pg.sprite.Sprite):
    def __init__(self, game, pos, stats, image, shadow):
        self.game = game
        self.game.sprites.append(self)
        self.image = image
        self.imgRect = self.image.get_rect()
        self.shadow = shadow
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.imgRect.centerx, self.imgRect.bottom = self.rect.centerx, self.rect.bottom - 10
        self.alpha = 255
        self.speed = 4.9
        self.dead = False
        self.stats = stats
        if self.game.leader == "mario":
            self.angle = get_angle(self.rect.center, self.game.player.rect.center)
        else:
            self.angle = get_angle(self.rect.center, self.game.follower.rect.center)

    def update(self):
        self.rect.center = project(self.rect.center, self.angle, self.speed)
        self.imgRect.centerx, self.imgRect.bottom = self.rect.centerx, self.rect.bottom - 10

        if self.game.player.stats["hp"] != 0:
            hits = self.imgRect.colliderect(self.game.playerCol.rect)
            if hits:
                if self.rect.bottom > self.game.player.rect.centery > self.rect.top:
                    if not self.game.player.hit and self.stats["hp"] > 0 and self.game.player.canBeHit:
                        HitNumbers(self.game, self.game.room,
                                   (self.game.player.rect.left, self.game.player.rect.top - 2),
                                   (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                        self.game.player.stats["hp"] -= (max(self.stats["pow"] - self.game.player.stats["def"], 1))
                        if self.game.player.stats["hp"] <= 0:
                            self.game.player.stats["hp"] = 0
                            self.game.player.currentFrame = 0
                        self.game.player.hitTime = pg.time.get_ticks()
                        self.game.playerHitSound.play()
                        self.game.player.canBeHit = False
                        self.game.player.hit = True

        if self.game.follower.stats["hp"] != 0:
            hits = self.imgRect.colliderect(self.game.followerCol.rect)
            if hits:
                if self.rect.bottom > self.game.follower.rect.centery > self.rect.top:
                    if not self.game.follower.hit and self.stats["hp"] > 0 and self.game.follower.canBeHit:
                        HitNumbers(self.game, self.game.room,
                                   (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                   (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                        self.game.follower.stats["hp"] -= (
                            max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                        if self.game.follower.stats["hp"] <= 0:
                            self.game.follower.stats["hp"] = 0
                            self.game.follower.currentFrame = 0
                        self.game.follower.hitTime = pg.time.get_ticks()
                        self.game.playerHitSound.play()
                        self.game.follower.canBeHit = False
                        self.game.follower.hit = True

        if self.rect.x > self.game.map.width + 60:
            self.game.sprites.remove(self)
        elif self.rect.x < -60:
            self.game.sprites.remove(self)
        elif self.rect.y > self.game.map.height + 100:
            self.game.sprites.remove(self)
        elif self.rect.y < -100:
            self.game.sprites.remove(self)


class MagiblotR(StateMachine):
    idle = State("Idle", initial=True)
    other = State("other")

    trans = idle.to(other)

    def init(self, game, pos):
        self.game = game
        self.game.enemies.append(self)
        self.game.sprites.append(self)

        self.loadImages()
        self.cooldown = 0
        self.alpha = 255
        self.hitRange = 1.3
        self.speed = 4
        self.lastUpdate = 0
        self.currentFrame = 0
        self.hitTimer = 0
        self.dead = False
        self.image = self.idleImages[0]
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.hpSpeed = 0
        self.rect.center = pos
        self.imgRect.centerx = self.rect.centerx + 3
        self.imgRect.bottom = self.rect.centery
        self.offset = 0

        # Stats
        self.stats = {"maxHP": 100, "hp": 100, "pow": 75, "def": 70, "exp": 100, "coins": 50, "name": "Red Magiblot"}
        self.rectHP = 0

        self.description = [
            "That's a Red Magiblot.",
            "I don't know how you managed to\nread this,/p this enemy isn't\nin the game.",
            "Are you hacking?",
            "Anyways, Max HP is " + str(self.stats["maxHP"]) + ",/p\nAttack is " + str(
                                self.stats["pow"]) + ",/p\nDefence is " + str(self.stats["def"]) + ".",
            "Um.../P it doesn't do anything.",
            "The devs weren't able to finish it in\ntime."]

    def hpMath(self):
        if self.rectHP > self.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = ((self.rectHP - self.stats["hp"]) / 30) * -1
        elif self.rectHP < self.stats["hp"] and self.hpSpeed == 0:
            if self.rectHP != 0:
                self.hpSpeed = (self.stats["hp"] - self.rectHP) / 30
            else:
                self.hpSpeed = (self.stats["hp"] - self.rectHP) / 180

        if self.hpSpeed != 0:
            if self.rectHP + self.hpSpeed > self.stats["hp"] and self.hpSpeed < 0:
                self.rectHP += self.hpSpeed
            elif self.rectHP + self.hpSpeed < self.stats["hp"] and self.hpSpeed > 0:
                self.rectHP += self.hpSpeed
            else:
                self.rectHP = self.stats["hp"]
                self.hpSpeed = 0

    def loadImages(self):
        sheet = spritesheet("sprites/magiblot-red.png", "sprites/magiblot-red.xml")

        self.idleImages = [sheet.getImageName("idle_1.png"),
                           sheet.getImageName("idle_2.png"),
                           sheet.getImageName("idle_3.png"),
                           sheet.getImageName("idle_4.png"),
                           sheet.getImageName("idle_5.png"),
                           sheet.getImageName("idle_6.png"),
                           sheet.getImageName("idle_7.png"),
                           sheet.getImageName("idle_8.png"),
                           sheet.getImageName("idle_9.png"),
                           sheet.getImageName("idle_10.png"),
                           sheet.getImageName("idle_11.png"),
                           sheet.getImageName("idle_12.png"),
                           sheet.getImageName("idle_13.png"),
                           sheet.getImageName("idle_14.png"),
                           sheet.getImageName("idle_15.png"),
                           sheet.getImageName("idle_16.png"),
                           sheet.getImageName("idle_17.png"),
                           sheet.getImageName("idle_18.png"),
                           sheet.getImageName("idle_19.png"),
                           sheet.getImageName("idle_20.png"),
                           sheet.getImageName("idle_21.png"),
                           sheet.getImageName("idle_22.png"),
                           sheet.getImageName("idle_23.png"),
                           sheet.getImageName("idle_24.png"),
                           sheet.getImageName("idle_25.png"),
                           sheet.getImageName("idle_26.png"),
                           sheet.getImageName("idle_27.png"),
                           sheet.getImageName("idle_28.png"),
                           sheet.getImageName("idle_29.png"),
                           sheet.getImageName("idle_30.png"),
                           sheet.getImageName("idle_31.png"),
                           sheet.getImageName("idle_32.png"),
                           sheet.getImageName("idle_33.png"),
                           sheet.getImageName("idle_34.png"),
                           sheet.getImageName("idle_35.png"),
                           sheet.getImageName("idle_36.png"),
                           sheet.getImageName("idle_37.png"),
                           sheet.getImageName("idle_38.png"),
                           sheet.getImageName("idle_39.png"),
                           sheet.getImageName("idle_40.png"),
                           sheet.getImageName("idle_41.png"),
                           sheet.getImageName("idle_42.png"),
                           sheet.getImageName("idle_43.png"),
                           sheet.getImageName("idle_44.png"),
                           sheet.getImageName("idle_45.png"),
                           sheet.getImageName("idle_46.png"),
                           sheet.getImageName("idle_47.png"),
                           sheet.getImageName("idle_48.png"),
                           sheet.getImageName("idle_49.png"),
                           sheet.getImageName("idle_50.png"),
                           sheet.getImageName("idle_51.png"),
                           sheet.getImageName("idle_52.png"),
                           sheet.getImageName("idle_53.png"),
                           sheet.getImageName("idle_54.png"),
                           sheet.getImageName("idle_55.png"),
                           sheet.getImageName("idle_56.png"),
                           sheet.getImageName("idle_57.png"),
                           sheet.getImageName("idle_58.png"),
                           sheet.getImageName("idle_59.png"),
                           sheet.getImageName("idle_60.png"),
                           sheet.getImageName("idle_61.png")]

        self.shadow = sheet.getImageName("shadow.png")

    def update(self):
        self.animate()

    def animate(self):
        if self.is_idle:
            if self.currentFrame < len(self.idleImages):
                self.currentFrame = (self.currentFrame + 1) % (len(self.idleImages))
            else:
                self.currentFrame = 0
            self.image = self.idleImages[self.currentFrame]
            self.imgRect = self.image.get_rect()

        self.imgRect.centerx = self.rect.centerx + 3
        self.imgRect.bottom = self.rect.centery


class CountBleckFight(StateMachine):
    idle = State("Idle", initial=True)
    walking = State("Towards Player")
    hit = State("hit")
    fire = State("fire")
    speed = State("Speed")

    startWalking = idle.to(walking)
    giveUp = walking.to(idle)
    getHit = idle.to(hit)
    getUp = hit.to(idle)
    toFire = idle.to(fire)
    fromFire = fire.to(idle)
    toSpeed = idle.to(speed)
    fromSpeed = speed.to(idle)

    def init(self, game, pos):
        self.game = game
        self.game.enemies.append(self)
        self.game.sprites.append(self)

        self.loadImages()
        self.cooldown = 0
        self.alpha = 255
        self.hitRange = 1.3
        self.speed = 4
        self.lastUpdate = 0
        self.currentFrame = 0
        self.hitTimer = 0
        self.dead = False
        self.image = self.idleImages[0]
        self.imgRect = self.image.get_rect()
        self.rect = self.shadow.get_rect()
        self.hpSpeed = 0
        self.rect.center = pos
        self.offset = 0
        self.imgRect.centerx = self.rect.centerx
        self.imgRect.bottom = self.rect.centery + 5 - self.offset
        self.hasCutscene = False

        # Stats
        self.stats = {"maxHP": 500, "hp": 500, "pow": 95, "def": 90, "exp": 0, "coins": 0, "name": "Count Bleck"}
        self.rectHP = 0

        self.description = [
            "That's Count Bleck.",
            "As you know, his main goal\nis to destroy all worlds\nwith the Void.",
            "Max HP is " + str(self.stats["maxHP"]) + ",/p\nAttack is " + str(
                self.stats["pow"]) + ",/p\nDefence is " + str(self.stats["def"]) + ".",
            "He's going to throw everything\nhe can at you.",
            "But you can beat him if you\ngive it your all!",
            "And you have to, or else\neverything we know will be\ngone..."]

    def loadImages(self):
        sheet = spritesheet("sprites/dark fawful.png", "sprites/dark fawful.xml")

        self.ballImage = sheet.getImageName("ball.png")

        self.ballShadow = sheet.getImageName("ballShadow.png")

        sheet = spritesheet("sprites/count bleck.png", "sprites/count bleck.xml")

        self.shadow = sheet.getImageName("shadow.png")

        self.hitFrame = sheet.getImageName("hit.png")

        self.idleImages = [sheet.getImageName("idle_1.png"),
                           sheet.getImageName("idle_2.png"),
                           sheet.getImageName("idle_3.png"),
                           sheet.getImageName("idle_4.png"),
                           sheet.getImageName("idle_5.png"),
                           sheet.getImageName("idle_6.png"),
                           sheet.getImageName("idle_7.png"),
                           sheet.getImageName("idle_8.png"),
                           sheet.getImageName("idle_9.png"),
                           sheet.getImageName("idle_10.png"),
                           sheet.getImageName("idle_11.png"),
                           sheet.getImageName("idle_12.png"),
                           sheet.getImageName("idle_13.png"),
                           sheet.getImageName("idle_14.png"),
                           sheet.getImageName("idle_15.png"),
                           sheet.getImageName("idle_16.png"),
                           sheet.getImageName("idle_17.png"),
                           sheet.getImageName("idle_18.png"),
                           sheet.getImageName("idle_19.png"),
                           sheet.getImageName("idle_20.png"),
                           sheet.getImageName("idle_21.png"),
                           sheet.getImageName("idle_22.png"),
                           sheet.getImageName("idle_23.png"),
                           sheet.getImageName("idle_24.png"),
                           sheet.getImageName("idle_25.png"),
                           sheet.getImageName("idle_26.png"),
                           sheet.getImageName("idle_27.png"),
                           sheet.getImageName("idle_28.png"),
                           sheet.getImageName("idle_29.png"),
                           sheet.getImageName("idle_30.png"),
                           sheet.getImageName("idle_31.png"),
                           sheet.getImageName("idle_32.png"),
                           sheet.getImageName("idle_33.png"),
                           sheet.getImageName("idle_34.png"),
                           sheet.getImageName("idle_35.png"),
                           sheet.getImageName("idle_36.png"),
                           sheet.getImageName("idle_37.png"),
                           sheet.getImageName("idle_38.png"),
                           sheet.getImageName("idle_39.png"),
                           sheet.getImageName("idle_40.png"),
                           sheet.getImageName("idle_41.png"),
                           sheet.getImageName("idle_42.png"),
                           sheet.getImageName("idle_43.png"),
                           sheet.getImageName("idle_44.png"),
                           sheet.getImageName("idle_45.png"),
                           sheet.getImageName("idle_46.png"),
                           sheet.getImageName("idle_47.png"),
                           sheet.getImageName("idle_48.png"),
                           sheet.getImageName("idle_49.png"),
                           sheet.getImageName("idle_50.png"),
                           sheet.getImageName("idle_51.png")]

        self.laughingFrames = [sheet.getImageName("to_laugh_1.png"),
                               sheet.getImageName("to_laugh_2.png"),
                               sheet.getImageName("to_laugh_3.png"),
                               sheet.getImageName("to_laugh_4.png"),
                               sheet.getImageName("to_laugh_5.png"),
                               sheet.getImageName("to_laugh_6.png"),
                               sheet.getImageName("laugh_1.png"),
                               sheet.getImageName("laugh_2.png"),
                               sheet.getImageName("laugh_3.png"),
                               sheet.getImageName("laugh_4.png"),
                               sheet.getImageName("laugh_5.png"),
                               sheet.getImageName("laugh_6.png"),
                               sheet.getImageName("laugh_7.png")]

        self.fireFrames = [sheet.getImageName("fire_1.png"),
                           sheet.getImageName("fire_2.png"),
                           sheet.getImageName("fire_3.png"),
                           sheet.getImageName("fire_4.png"),
                           sheet.getImageName("fire_5.png"),
                           sheet.getImageName("fire_6.png"),
                           sheet.getImageName("fire_7.png"),
                           sheet.getImageName("fire_8.png"),
                           sheet.getImageName("fire_9.png"),
                           sheet.getImageName("fire_10.png"),
                           sheet.getImageName("fire_11.png"),
                           sheet.getImageName("fire_12.png"),
                           sheet.getImageName("fire_13.png"),
                           sheet.getImageName("fire_14.png"),
                           sheet.getImageName("fire_15.png")]

    def hpMath(self):
        if self.rectHP > self.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = ((self.rectHP - self.stats["hp"]) / 30) * -1
        elif self.rectHP < self.stats["hp"] and self.hpSpeed == 0:
            if self.rectHP != 0:
                self.hpSpeed = (self.stats["hp"] - self.rectHP) / 30
            else:
                self.hpSpeed = (self.stats["hp"] - self.rectHP) / 180

        if self.hpSpeed != 0:
            if self.rectHP + self.hpSpeed > self.stats["hp"] and self.hpSpeed < 0:
                self.rectHP += self.hpSpeed
            elif self.rectHP + self.hpSpeed < self.stats["hp"] and self.hpSpeed > 0:
                self.rectHP += self.hpSpeed
            else:
                self.rectHP = self.stats["hp"]
                self.hpSpeed = 0

    def update(self):
        self.animate()
        self.hpMath()

        if self.stats["hp"] < 100 and not self.hasCutscene:
            self.description = [
                "Woah!",
                "There are so many copies of\nhim!",
                "But which one's the real\none...",
                "Only one way to find out!",
                "And you'd better hurry!/P\nWe're running out of time..."]

            self.stats = {"maxHP": 500, "hp": 500, "pow": 50, "def": 80, "exp": 100, "coins": 100,
                          "name": "Count Bleck"}

            LoadCutscene(self.game, self.game.player.rect, True, True, [
                ["self.setVar('self.bleck = BleckCutscene(self.game, self.game.bleck.rect.center)')",
                 "self.command('pg.mixer.music.fadeout(5000)')"],
                 ["""self.textBox(self.bleck, ["Bleh heh heh heh heh..."])"""],
                ["self.move(self.bleck, self.game.map.width / 2, self.game.map.height / 2, False, 120)",
                 "self.move(self.game.cameraRect, self.game.map.width / 2, self.game.map.height / 2, False, 120, 1)"
                 ],
                ["""self.textBox(self.bleck, [
                "Foolish heroes!",
                "You think that YOU are able to/nstop ME?",
                "WATCH AS I SUMMON MY ULTIMATE/nPOWER!"])""",
                 "self.command('self.game.cameraRect.update(self.bleck.rect, 5)')",
                 "self.setVar('self.game.bleck.rect.center = self.bleck.rect.center')"],
                ['''self.setVar("""self.game.battleSong = 'self.playSong(45.787, 57.6, "Count Bleck Battle Phase 2")'""")''',
                 'self.changeSong([45.787, 57.6, "Count Bleck Battle Phase 2"])',
                 "self.setVar('self.bleck.laughing = True')",
                 "self.setVar('self.bleck.currentFrame = 0')"],
                ["self.bleckCloneCreate()"],
                ["self.wait(3)"]
            ], id="Begin Phase 2")
            self.hasCutscene = True

        if self.is_idle:
            chance = random.randrange(0, 100)
            if chance == 0 and self.cooldown <= 0:
                choice = random.randrange(0, 3)
                self.cooldown = fps * 9
                if choice == 0:
                    self.startWalking()
                elif choice == 1:
                    self.currentFrame = 0
                    self.toFire()
                elif choice == 2:
                    if self.game.leader == "mario":
                        self.angle = get_angle(self.rect.center, self.game.player.rect.center)
                    else:
                        self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
                    self.toSpeed()
            elif self.cooldown > 0:
                self.cooldown -= 1
        elif self.is_walking:
            if self.game.leader == "mario":
                self.angle = get_angle(self.rect.center, self.game.player.rect.center)
            else:
                self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
            self.rect.center = project(self.rect.center, self.angle, self.speed)
            chance = random.randrange(0, 250)
            if chance == 0 or self.game.player.dead:
                self.giveUp()
        elif self.is_speed:
            for wall in self.game.walls:
                if self.rect.colliderect(wall.rect) and type(wall).__name__ == "Wall":
                    if self.game.leader == "mario":
                        self.angle = get_angle(self.rect.center, (random.randrange(self.game.player.rect.centerx - 40, self.game.player.rect.centerx + 40), (random.randrange(self.game.player.rect.centery - 40, self.game.player.rect.centery + 40))))
                    else:
                        self.angle = get_angle(self.rect.center, (random.randrange(self.game.follower.rect.centerx - 40, self.game.follower.rect.centerx + 40), (random.randrange(self.game.follower.rect.centery - 40, self.game.follower.rect.centery + 40))))
            self.rect.center = project(self.rect.center, self.angle, self.speed * 3)
            chance = random.randrange(0, 300)
            if 10 < chance < 15:
                for i in range(random.randrange(3, 8)):
                    ball = FawfulBullet(self.game, (random.randrange(self.rect.left - 100, self.rect.right + 100),
                                             random.randrange(self.rect.top - 100, self.rect.bottom + 100)), self.stats, self.ballImage, self.ballShadow)
                    ball.speed = 3
            if chance == 0 or self.game.player.dead:
                self.fromSpeed()

        if self.cooldown > 0:
            self.cooldown -= 1

        if self.is_idle or self.is_walking:
            if self.game.player.stats["hp"] != 0:
                hits = pg.sprite.collide_rect(self.game.player, self)
                if hits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                    if hitsRound2:
                        if self.game.player.going == "down" and self.game.player.jumping and self.stats["hp"] > 0:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (max(2 * (self.game.player.stats["pow"] - self.stats["def"]), 1)))
                            self.stats["hp"] -= (max(2 * (self.game.player.stats["pow"] - self.stats["def"]), 1))
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            if self.is_walking:
                                self.giveUp()
                            if not self.is_hit: self.getHit()
                            self.cooldown = fps
                            self.game.player.airTimer = 0
                        else:
                            if not self.game.player.hit and self.stats[
                                "hp"] > 0 and not self.is_hit and self.game.player.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.player.rect.left, self.game.player.rect.top - 2),
                                           (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                                self.game.player.stats["hp"] -= (
                                    max(self.stats["pow"] - self.game.player.stats["def"], 1))
                                if self.game.player.stats["hp"] <= 0:
                                    self.game.player.stats["hp"] = 0
                                    self.game.player.currentFrame = 0
                                self.game.player.hitTime = pg.time.get_ticks()
                                self.game.playerHitSound.play()
                                self.game.player.canBeHit = False
                                self.game.player.hit = True

            if self.game.follower.stats["hp"] != 0 and (self.is_idle or self.is_walking):
                hits = pg.sprite.collide_rect(self.game.follower, self)
                if hits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                    if hitsRound2:
                        if self.game.player.going == "down" and self.game.player.jumping and self.stats["hp"] > 0:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                      (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 1)))
                            self.stats["hp"] -= (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 1))
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            if self.is_walking:
                                self.giveUp()
                            if not self.is_hit: self.getHit()
                            self.cooldown = fps
                            self.game.follower.airTimer = 0
                        else:
                            if not self.game.follower.hit and self.stats[
                                "hp"] > 0 and not self.is_hit and self.game.follower.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                           (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                                self.game.follower.stats["hp"] -= (
                                    max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                                if self.game.follower.stats["hp"] <= 0:
                                    self.game.follower.stats["hp"] = 0
                                    self.game.follower.currentFrame = 0
                                self.game.follower.hitTime = pg.time.get_ticks()
                                self.game.playerHitSound.play()
                                self.game.follower.canBeHit = False
                                self.game.follower.hit = True

            if self.stats["hp"] != 0 and self.game.player.isHammer is not None and (self.is_idle or self.is_walking):
                hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                    if hammerHitsRound2 and not self.is_hit and self.stats["hp"] > 0:
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 0))
                        self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 0)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        if self.is_walking:
                            self.giveUp()
                        if not self.is_hit: self.getHit()
                        self.cooldown = fps

            if self.stats["hp"] != 0 and self.game.follower.isHammer is not None and (self.is_idle or self.is_walking):
                hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                    if hammerHitsRound2 and not self.is_hit and self.stats["hp"] > 0:
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1))
                        self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        if self.is_walking:
                            self.giveUp()
                        if not self.is_hit: self.getHit()
                        self.cooldown = fps

            for entity in self.game.entities:
                if self.rect.colliderect(entity.rect) and not self.is_hit and self.stats["hp"] > 0 and (self.is_idle or self.is_walking):
                    if type(entity).__name__ == "Lightning":
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 1))
                        self.stats["hp"] -= max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 1)
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        if self.is_walking:
                            self.giveUp()
                        if not self.is_hit: self.getHit()
                        self.cooldown = fps
                    if self.imgRect.colliderect(entity.imgRect) and (self.is_idle or self.is_walking):
                        if type(entity).__name__ == "Fireball":
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1))
                            self.stats["hp"] -= max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1)
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            if self.is_walking:
                                self.giveUp()
                            if not self.is_hit: self.getHit()
                            self.cooldown = fps
                            entity.dead = True

        elif not self.is_hit and not self.is_speed:
            if self.game.player.stats["hp"] != 0:
                hits = self.imgRect.colliderect(self.game.playerCol.rect)
                if hits:
                    if self.rect.bottom > self.game.player.rect.centery > self.rect.top:
                        if not self.game.player.hit and self.stats["hp"] > 0 and self.game.player.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.player.rect.left, self.game.player.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                            self.game.player.stats["hp"] -= (max(self.stats["pow"] - self.game.player.stats["def"], 1))
                            if self.game.player.stats["hp"] <= 0:
                                self.game.player.stats["hp"] = 0
                                self.game.player.currentFrame = 0
                            self.game.player.hitTime = pg.time.get_ticks()
                            self.game.playerHitSound.play()
                            self.game.player.canBeHit = False
                            self.game.player.hit = True

            if self.game.follower.stats["hp"] != 0:
                hits = self.imgRect.colliderect(self.game.followerCol.rect)
                if hits:
                    if self.rect.bottom > self.game.follower.rect.centery > self.rect.top:
                        if not self.game.follower.hit and self.stats["hp"] > 0 and self.game.follower.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                            self.game.follower.stats["hp"] -= (
                                max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                            if self.game.follower.stats["hp"] <= 0:
                                self.game.follower.stats["hp"] = 0
                                self.game.follower.currentFrame = 0
                            self.game.follower.hitTime = pg.time.get_ticks()
                            self.game.playerHitSound.play()
                            self.game.follower.canBeHit = False
                            self.game.follower.hit = True

        if self.stats["hp"] <= 0:
            self.cooldown = 10000
            self.alpha -= 10

        if self.alpha <= 0:
            self.game.battleXp += self.stats["exp"]
            self.game.sprites.remove(self)
            self.game.enemies.remove(self)

        self.imgRect.centerx = self.rect.centerx
        self.imgRect.bottom = self.rect.centery + 5 - self.offset

    def animate(self):
        now = pg.time.get_ticks()
        if self.is_idle or self.is_walking or self.is_speed:
            if now - self.lastUpdate > 30:
                self.lastUpdate = now
                if self.currentFrame < len(self.idleImages):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.idleImages))
                else:
                    self.currentFrame = 0
                bottom = self.imgRect.bottom
                left = self.imgRect.left
                self.image = self.idleImages[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.bottom = bottom
                self.imgRect.left = left
        elif self.is_fire:
            if now - self.lastUpdate > 30:
                self.lastUpdate = now
                if self.currentFrame < len(self.fireFrames) - 1:
                    self.currentFrame += 1
                else:
                    self.fromFire()
                if self.currentFrame == 9:
                    for i in range(random.randrange(5, 10)):
                        FawfulBullet(self.game, (random.randrange(self.rect.left - 100, self.rect.right + 100), random.randrange(self.rect.top - 100, self.rect.bottom + 100)), self.stats, self.ballImage, self.ballShadow)
                center = self.imgRect.center
                self.image = self.fireFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        elif self.is_hit:
            self.currentFrame = 0
            centerx = self.imgRect.centerx
            bottom = self.imgRect.bottom
            self.image = self.hitFrame
            self.imgRect = self.image.get_rect()
            self.imgRect.centerx = centerx
            self.imgRect.bottom = bottom
            if self.cooldown == 0:
                self.getUp()
                choice = random.randrange(0, 3)
                self.cooldown = fps * 9
                if choice == 0:
                    self.startWalking()
                elif choice == 1:
                    self.currentFrame = 0
                    self.toFire()
                elif choice == 2:
                    if self.game.leader == "mario":
                        self.angle = get_angle(self.rect.center, self.game.player.rect.center)
                    else:
                        self.angle = get_angle(self.rect.center, self.game.follower.rect.center)
                    self.toSpeed()
            else:
                self.cooldown -= 1


class Sans:
    def __init__(self, game, pos):
        self.game = game
        self.game.enemies.append(self)
        self.game.sprites.append(self)
        self.sansGameovers = self.game.sansGameovers

        self.loadImages()
        self.alpha = 255
        self.hitRange = 1.3
        self.speed = 2.5
        self.lastUpdate = 0
        self.currentFrame = 0
        self.hitTimer = 0
        self.dead = False
        self.anim = True
        self.hit = False
        self.currentHead = "default"
        self.currentBody = "default"
        self.headRect = self.head[self.currentHead].get_rect()
        self.bodyRect = self.body[self.currentBody].get_rect()
        self.legRect = self.legs.get_rect()
        self.rect = self.shadow.get_rect()
        self.hpSpeed = 0
        self.rect.center = pos
        self.legRect.centerx = self.rect.centerx
        self.legRect.bottom = self.rect.bottom - 2
        self.bodyRect.centerx = self.legRect.centerx - 2
        self.bodyRect.bottom = self.legRect.top + 7
        self.headRect.centerx = self.bodyRect.centerx + 2
        self.headRect.bottom = self.bodyRect.top + 10

        self.dodge = None
        self.dodged = False
        self.dodgeTimer = 0
        self.dodgeSpeed = 10

        self.eyeTimer = 0
        self.eyeLastUpdate = 0
        self.throwDir = None
        self.hasPlayedMagicSound = False
        self.throwPower = 20
        self.defaultThrowPower = 20

        self.bodyMovement = [0, -1, -1, -1, -1, 0, 0, 0, 1, 1, 1, 1]
        self.bodyMovementY = [0, 0, 1, 0, 0, -1, 0, 0, 0, 1, 0, 0, -1]
        self.headMovement = [0, 1, 1, 1, 0, -1, -1, 0, 1, 1, 1, 0, -1]

        img = CombineSprites([self.legs, self.body[self.currentBody], self.head[self.currentHead]], [self.legRect, self.bodyRect, self.headRect])
        self.image = img.image
        self.imgRect = img.rect

        # Stats
        self.stats = {"maxHP": 1, "hp": 1, "pow": 1, "def": 0, "exp": 400, "coins": 400, "name": "Sans"}
        self.rectHP = 0

        self.description = ["That's Sans./P\nFrom Undertale.",
                            "Sans is a funny skeleton with\nan enjoyment of bad puns.",
                            "He only fights people when they've\ncommitted genocide.../P\nor if you ask him,/p apparently.",
                            "Max HP is " + str(self.stats["maxHP"]) + ",/p\nAttack is " + str(
                            self.stats["pow"]) + ",/p\nDefence is " + str(self.stats["def"]) + ".",
                            "Something seems off about his\nstats.",
                            "No matter what,/p just keep\nattacking him.",
                            "...",
                            "Wait a minute...",
                            "It looks like he's disabled\nyour <<RBros. Attacks>>!",
                            "How'd he even do that?"]

        self.hitDialogue = [
            [
            ["self.command('self.game.cutsceneSprites.append(self.game.sans)')",
             '''self.setVar("""self.game.battleSong = 'self.playSong(17.057, 143.969, "megalovania")'""")''',
            "self.changeSong([17.057, 143.969, 'megalovania'])",
             "self.setVar('self.mario = marioCutscene(self.game, (self.game.player.rect.centerx, self.game.player.rect.centery))')",
             "self.setVar('self.luigi = luigiCutscene(self.game, (self.game.follower.rect.centerx, self.game.follower.rect.centery))')", 
             "self.move(self.game.cameraRect, self.game.sans.rect.centerx, self.game.sans.rect.centery, False, 60)"],
             ["""self.undertaleTextBox(self.game.sans, [
            "*/2 what?",
            "*/3 you think i'm just/n\a gonna stand there and/n\a take it?"
            ], sound="sans", font="sans", head="sans")""",
             """self.setVar('self.game.sans.currentHead = "look left smile"')""",
             """if self.textbox[0].page == 1: self.setVar('self.game.sans.currentHead = "wink"')""",
             """if self.textbox[0].page == 1: self.setVar('self.game.sans.currentBody = "shrug"')"""],
            ["""self.setVar('self.game.sans.currentFrame = 0')""",
             """self.setVar('self.game.sans.throwDir = "down"')""",
             """self.setVar('self.game.sans.currentHead = "default"')""",
             """self.setVar('self.game.sans.currentBody = "default"')"""]
            ]
            ]

        self.dialogueCounter = 0

    def loadImages(self):
        sheet = spritesheet("sprites/sansBattle.png", "sprites/sansBattle.xml")

        self.shadow = sheet.getImageName("shadow.png")

        self.head = {"default": sheet.getImageName("head default.png"),
                     "eyes closed": sheet.getImageName("head eyes closed.png"),
                     "no eyes": sheet.getImageName("head no eyes.png"),
                     "wink": sheet.getImageName("head wink.png"),
                     "look left smile": sheet.getImageName("head look left smile.png"),
                     "eye glow": [sheet.getImageName("head glow eye 1.png"),
                                  sheet.getImageName("head glow eye 2.png")]}

        self.body = {"default": sheet.getImageName("body default.png"),
                     "shrug": sheet.getImageName("body shrug.png"),
                     "throw down": [sheet.getImageName("throw_down_1.png"),
                                   sheet.getImageName("throw_down_2.png"),
                                   sheet.getImageName("throw_down_3.png"),
                                   sheet.getImageName("throw_down_4.png"),
                                   sheet.getImageName("throw_down_5.png")],
                     "throw up": [sheet.getImageName("throw_up_1.png"),
                                    sheet.getImageName("throw_up_2.png"),
                                    sheet.getImageName("throw_up_3.png"),
                                    sheet.getImageName("throw_up_4.png"),
                                    sheet.getImageName("throw_up_5.png")]
                     }

        self.legs = sheet.getImageName("legs.png")

        self.gasterBlasterSprites = [sheet.getImageName("GB_1.png"),
                                     sheet.getImageName("GB_2.png"),
                                     sheet.getImageName("GB_3.png"),
                                     sheet.getImageName("GB_4.png"),
                                     sheet.getImageName("GB_5.png"),
                                     sheet.getImageName("GB_6.png")]

    def hpMath(self):
        if self.rectHP > self.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = ((self.rectHP - self.stats["hp"]) / 30) * -1
        elif self.rectHP < self.stats["hp"] and self.hpSpeed == 0:
            if self.rectHP != 0:
                self.hpSpeed = (self.stats["hp"] - self.rectHP) / 30
            else:
                self.hpSpeed = (self.stats["hp"] - self.rectHP) / 180

        if self.hpSpeed != 0:
            if self.rectHP + self.hpSpeed > self.stats["hp"] and self.hpSpeed < 0:
                self.rectHP += self.hpSpeed
            elif self.rectHP + self.hpSpeed < self.stats["hp"] and self.hpSpeed > 0:
                self.rectHP += self.hpSpeed
            else:
                self.rectHP = self.stats["hp"]
                self.hpSpeed = 0

    def update(self):
        if self.game.player.stats["hp"] == 0 and self.game.follower.stats["hp"] == 0:
            self.game.sansGameovers = self.sansGameovers + 1
            self.game.follower.attackPieces[0][1] = 10
            self.game.player.attackPieces[0][1] = 10

        self.hpMath()

        LoadCutscene(self.game, self.game.player.rect, True, True, [
            ["self.command('self.game.cutsceneSprites.append(self.game.sans)')",
             """self.setVar('self.game.sans.currentHead = "eyes closed"')""",
             """self.setVar('self.game.player.attackPieces[0][1] = 0')""",
             "self.move(self.game.cameraRect, self.game.sans.rect.centerx, self.game.sans.rect.centery, False, 0)",
             "self.wait(3)",
             "self.command('self.game.birdNoise.play(-1)')"],
            ["""self.undertaleTextBox(self.game.sans, [
            "*/5 it's a beautiful day/n\a outside...",
            "* birds are singing.../p/n* flowers are blooming...",
            "* on days like these.../p/n* kids like you..."
            ], sound="sans", font="sans", head="sans")"""],
            ["self.setVar('self.room = self.game.room')",
             """self.setVar('self.game.room = "clique"')""",
             "self.command('Fadeout(self.game, 255)')",
             "self.command('self.game.birdNoise.stop()')",
             "self.command('self.game.click.play()')"],
            ["self.wait(0.5)",
             "self.setVar('self.game.sans.anim = False')",
             """self.setVar('self.game.sans.currentHead = "no eyes"')"""],
            ["""self.setVar('self.game.room = self.room')""",
             "self.command('self.game.click.play()')"],
            ["self.wait(1)"],
            ["""self.undertaleTextBox(self.game.sans, [
            "*/6/p S H O U L D  B E/n\a B U R N I N G  I N/n\a H E L L."
            ], sound="none", head="sans", speed=3)"""],
            ["self.setVar('self.game.sans.anim = True')",
             """self.setVar('self.game.sans.currentFrame = 0')""",
             """self.setVar('self.game.sans.throwDir = "down"')""",
             """self.setVar('self.game.sans.rectHP = 0')""",
             '''self.setVar("""self.game.battleSong = 'self.playSong(17.057, 143.969, "megalovania")'""")''']
        ], id="it's a beautiful day outside...")

        if self.dodge is not None:
            self.currentBody = "shrug"
            self.currentHead = "wink"

        if self.throwDir is not None:
            self.currentHead = "eye glow"
            self.currentBody = "throw down"
            if self.currentFrame == 0 and not self.hasPlayedMagicSound:
                self.game.sansMagicSound.play()
                self.hasPlayedMagicSound = True
            if self.currentFrame == len(self.body[self.currentBody]) - 1:
                if self.throwDir == "down":
                    self.game.player.flySpeedY = self.throwPower
                    self.game.follower.flySpeedY = self.throwPower
                elif self.throwDir == "up":
                    self.game.player.flySpeedY = -self.throwPower
                    self.game.follower.flySpeedY = -self.throwPower
                elif self.throwDir == "left":
                    self.game.player.flySpeedX = -self.throwPower
                    self.game.follower.flySpeedX = -self.throwPower
                elif self.throwDir == "right":
                    self.game.player.flySpeedX = self.throwPower
                    self.game.follower.flySpeedX = self.throwPower
                self.throwDir = None
                self.currentBody = "default"
                self.currentHead = "default"
        else:
            self.hasPlayedMagicSound = False

        if self.dodge == "right":
            if self.dodgeTimer < 30 and not self.dodged:
                self.dodgeTimer += 1
                if self.dodgeTimer < 15:
                    self.rect.y -= self.dodgeSpeed
            elif self.dodgeTimer > 0:
                self.dodged = True
                if self.dodgeTimer < 15:
                    self.rect.y += self.dodgeSpeed
                self.dodgeTimer -= 1
            else:
                self.dodged = False
                self.dodge = None
                self.currentBody = "default"
                self.currentHead = "default"
                try:
                    Cutscene(self.game, self.hitDialogue[self.dialogueCounter])
                except:
                    pass
                self.dialogueCounter += 1
        elif self.dodge == "left":
            if self.dodgeTimer < 30 and not self.dodged:
                self.dodgeTimer += 1
                if self.dodgeTimer < 15:
                    self.rect.y += self.dodgeSpeed
            elif self.dodgeTimer > 0:
                self.dodged = True
                if self.dodgeTimer < 15:
                    self.rect.y -= self.dodgeSpeed
                self.dodgeTimer -= 1
            else:
                self.dodged = False
                self.dodge = None
                self.currentBody = "default"
                self.currentHead = "default"
                try:
                    Cutscene(self.game, self.hitDialogue[self.dialogueCounter])
                except:
                    pass
                self.dialogueCounter += 1
        elif self.dodge == "down":
            if self.dodgeTimer < 30 and not self.dodged:
                self.dodgeTimer += 1
                if self.dodgeTimer < 15:
                    self.rect.x += self.dodgeSpeed
            elif self.dodgeTimer > 0:
                self.dodged = True
                if self.dodgeTimer < 15:
                    self.rect.x -= self.dodgeSpeed
                self.dodgeTimer -= 1
            else:
                self.dodged = False
                self.dodge = None
                self.currentBody = "default"
                self.currentHead = "default"
                try:
                    Cutscene(self.game, self.hitDialogue[self.dialogueCounter])
                except:
                    pass
                self.dialogueCounter += 1
        elif self.dodge == "up":
            if self.dodgeTimer < 30 and not self.dodged:
                self.dodgeTimer += 1
                if self.dodgeTimer < 15:
                    self.rect.x -= self.dodgeSpeed
            elif self.dodgeTimer > 0:
                self.dodged = True
                if self.dodgeTimer < 15:
                    self.rect.x += self.dodgeSpeed
                self.dodgeTimer -= 1
            else:
                self.dodged = False
                self.dodge = None
                self.currentBody = "default"
                self.currentHead = "default"
                try:
                    Cutscene(self.game, self.hitDialogue[self.dialogueCounter])
                except:
                    pass
                self.dialogueCounter += 1
        elif self.dodge == "downright":
            if self.dodgeTimer < 30 and not self.dodged:
                self.dodgeTimer += 1
                if self.dodgeTimer < 15:
                    self.rect.x += self.dodgeSpeed
                    self.rect.y -= self.dodgeSpeed
            elif self.dodgeTimer > 0:
                self.dodged = True
                if self.dodgeTimer < 15:
                    self.rect.x -= self.dodgeSpeed
                    self.rect.y += self.dodgeSpeed
                self.dodgeTimer -= 1
            else:
                self.dodged = False
                self.dodge = None
                self.currentBody = "default"
                self.currentHead = "default"
                try:
                    Cutscene(self.game, self.hitDialogue[self.dialogueCounter])
                except:
                    pass
                self.dialogueCounter += 1
        elif self.dodge == "downleft":
            if self.dodgeTimer < 30 and not self.dodged:
                self.dodgeTimer += 1
                if self.dodgeTimer < 15:
                    self.rect.x -= self.dodgeSpeed
                    self.rect.y -= self.dodgeSpeed
            elif self.dodgeTimer > 0:
                self.dodged = True
                if self.dodgeTimer < 15:
                    self.rect.x += self.dodgeSpeed
                    self.rect.y += self.dodgeSpeed
                self.dodgeTimer -= 1
            else:
                self.dodged = False
                self.dodge = None
                self.currentBody = "default"
                self.currentHead = "default"
                try:
                    Cutscene(self.game, self.hitDialogue[self.dialogueCounter])
                except:
                    pass
                self.dialogueCounter += 1
        elif self.dodge == "upleft":
            if self.dodgeTimer < 30 and not self.dodged:
                self.dodgeTimer += 1
                if self.dodgeTimer < 15:
                    self.rect.x -= self.dodgeSpeed
                    self.rect.y += self.dodgeSpeed
            elif self.dodgeTimer > 0:
                self.dodged = True
                if self.dodgeTimer < 15:
                    self.rect.x += self.dodgeSpeed
                    self.rect.y -= self.dodgeSpeed
                self.dodgeTimer -= 1
            else:
                self.dodged = False
                self.dodge = None
                self.currentBody = "default"
                self.currentHead = "default"
                try:
                    Cutscene(self.game, self.hitDialogue[self.dialogueCounter])
                except:
                    pass
                self.dialogueCounter += 1
        elif self.dodge == "upright":
            if self.dodgeTimer < 30 and not self.dodged:
                self.dodgeTimer += 1
                if self.dodgeTimer < 15:
                    self.rect.x += self.dodgeSpeed
                    self.rect.y += self.dodgeSpeed
            elif self.dodgeTimer > 0:
                self.dodged = True
                if self.dodgeTimer < 15:
                    self.rect.x -= self.dodgeSpeed
                    self.rect.y -= self.dodgeSpeed
                self.dodgeTimer -= 1
            else:
                self.dodged = False
                self.dodge = None
                self.currentBody = "default"
                self.currentHead = "default"
                try:
                    Cutscene(self.game, self.hitDialogue[self.dialogueCounter])
                except:
                    pass
                self.dialogueCounter += 1

        if self.stats["hp"] <= 0:
            self.cooldown = 10000
            self.alpha -= 10

        if self.alpha <= 0:
            self.game.battleXp += self.stats["exp"]
            self.game.battleCoins += self.stats["coins"]
            self.game.player.attackPieces[0][1] = 10
            self.game.sprites.remove(self)
            self.game.enemies.remove(self)

        if self.game.player.stats["hp"] != 0 and self.dodge is None:
            hits = pg.sprite.collide_rect(self.game.player, self)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self.game.playerCol, self)
                if hitsRound2:
                    if self.game.player.going == "down" and self.game.player.jumping and self.stats["hp"] > 0:
                        self.cooldown = fps
                        if self.dialogueCounter >= len(self.hitDialogue):
                            self.stats["hp"] -= 9999999999999
                            HitNumbers(self.game, self.game.room, (self.imgRect.centerx, self.imgRect.top), 9999999999999)
                        else:
                            self.dodge = self.game.player.facing
                    else:
                        if not self.game.player.hit and self.stats[
                            "hp"] > 0 and not self.hit and self.game.player.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.player.rect.left, self.game.player.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
                            self.game.player.stats["hp"] -= (
                                max(self.stats["pow"] - self.game.player.stats["def"], 1))
                            self.game.player.KR += 5
                            if self.game.player.stats["hp"] <= 0:
                                self.game.player.stats["hp"] = 0
                                self.game.player.currentFrame = 0
                                self.game.player.KR = 0
                            self.game.playerHitSound.play()

        if self.game.follower.stats["hp"] != 0 and self.dodge is None:
            hits = pg.sprite.collide_rect(self.game.follower, self)
            if hits:
                hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                if hitsRound2:
                    if self.game.follower.going == "down" and self.game.follower.jumping and self.stats["hp"] > 0:
                        if self.dialogueCounter >= len(self.hitDialogue):
                            self.stats["hp"] -= 9999999999999
                            HitNumbers(self.game, self.game.room, (self.imgRect.centerx, self.imgRect.top),
                                       9999999999999)
                        else:
                            self.dodge = self.game.follower.facing
                    else:
                        if not self.game.follower.hit and self.stats[
                            "hp"] > 0 and not self.hit and self.game.follower.canBeHit:
                            HitNumbers(self.game, self.game.room,
                                       (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                                       (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                            self.game.follower.stats["hp"] -= (
                                max(self.stats["pow"] - self.game.follower.stats["def"], 1))
                            self.game.follower.KR += 5
                            if self.game.follower.stats["hp"] <= 0:
                                self.game.follower.stats["hp"] = 0
                                self.game.follower.currentFrame = 0
                                self.game.follower.KR = 0
                            self.game.playerHitSound.play()

        if self.stats["hp"] != 0 and self.game.player.isHammer is not None and self.dodge is None:
            hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
            if hammerHits:
                hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                if hammerHitsRound2 and self.stats["hp"] > 0:
                    if self.dialogueCounter >= len(self.hitDialogue):
                        self.stats["hp"] -= 9999999999999
                        HitNumbers(self.game, self.game.room, (self.imgRect.centerx, self.imgRect.top), 9999999999999)
                    else:
                        self.dodge = self.game.player.facing

        if self.stats["hp"] != 0 and self.game.follower.isHammer is not None and self.dodge is None:
            hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
            if hammerHits:
                hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                if hammerHitsRound2 and self.stats["hp"] > 0:
                    if self.dialogueCounter >= len(self.hitDialogue):
                        self.stats["hp"] -= 1
                        HitNumbers(self.game, self.game.room, (self.imgRect.centerx, self.imgRect.top), 99999999999999999999999999)
                    else:
                        self.dodge = self.game.follower.facing

        for entity in self.game.entities:
            if self.rect.colliderect(entity.rect) and self.stats["hp"] > 0:
                if self.imgRect.colliderect(entity.imgRect):
                    if type(entity).__name__ == "Fireball":
                        entity.dead = True

        self.animate()

    def animate(self):
        now = pg.time.get_ticks()
        if self.currentHead == "eye glow":
            self.headRect = self.head[self.currentHead][self.currentFrame % 2].get_rect()
        else:
            self.headRect = self.head[self.currentHead].get_rect()

        if "throw" in self.currentBody:
            self.bodyRect = self.body[self.currentBody][self.currentFrame].get_rect()
        else:
            self.bodyRect = self.body[self.currentBody].get_rect()

        self.legRect = self.legs.get_rect()

        self.legRect.centerx = self.rect.centerx
        self.legRect.bottom = self.rect.centery + 2
        self.bodyRect.centerx = self.legRect.centerx - 2
        self.bodyRect.bottom = self.legRect.top + 7
        self.headRect.centerx = self.bodyRect.centerx + 2
        self.headRect.bottom = self.bodyRect.top + 10

        if now - self.eyeLastUpdate > 40:
            self.eyeLastUpdate = now
            self.eyeTimer += 1

        if now - self.lastUpdate > 50 and "throw" in self.currentBody:
            self.lastUpdate = now
            if self.currentFrame < len(self.currentBody) - 1:
                self.currentFrame += 1
        elif now - self.lastUpdate > 100 and self.anim:
            self.lastUpdate = now
            if self.currentFrame < len(self.bodyMovement):
                self.currentFrame = (self.currentFrame + 1) % (len(self.bodyMovement))
            else:
                self.currentFrame = 0

        self.bodyRect.x += self.bodyMovement[self.currentFrame]
        self.bodyRect.y += self.bodyMovementY[self.currentFrame]
        self.headRect.centerx = self.bodyRect.centerx + 2
        self.headRect.y += self.headMovement[self.currentFrame]

        if self.currentHead == "eye glow":
            head = self.head[self.currentHead][self.eyeTimer % 2]
        else:
            head = self.head[self.currentHead]

        if "throw" in self.currentBody:
            bod = self.body[self.currentBody][self.currentFrame]
            self.bodyRect = self.body[self.currentBody][self.currentFrame].get_rect()
            self.bodyRect.bottom = self.legRect.bottom
            self.bodyRect.centerx = self.legRect.centerx
            self.headRect.bottom = self.bodyRect.bottom - 80
            self.headRect.centerx = self.bodyRect.centerx - 2
        else:
            bod = self.body[self.currentBody]

        img = CombineSprites([self.legs, bod, head], [self.legRect, self.bodyRect, self.headRect])
        self.image = img.image
        self.imgRect = img.rect


class GasterBlaster(pg.sprite.Sprite):
    def __init__(self, game, pos, target, images, size, facing, speed=30, turnSpeed=30):
        self.points = []
        self.lastUpdate = 0
        self.pointCounter = 0
        self.laserDelay = 0
        self.game = game
        self.game.gasterBlasterArriveSound.play()
        self.dead = False
        self.laser = None
        self.offset = True
        self.manualDraw = True
        self.targetPos = target
        self.scale = size
        self.facing = facing.lower()
        self.pow = 1
        self.game.sprites.append(self)

        self.vel = 0
        self.speed = 2
        self.laserAlpha = 255
        self.sizeIncrease = True
        self.sizeIncreaseSpeed = 6

        self.sprites = images
        self.currentFrame = 0
        if self.facing == "down":
            self.angle = -90
            self.targetAngle = 0
        elif self.facing == "up":
            self.angle = 90
            self.targetAngle = 180
        elif self.facing == "left":
            self.angle = 180
            self.targetAngle = 270
        elif self.facing == "right":
            self.angle = 0
            self.targetAngle = 90
        self.rect = pg.rect.Rect(0, 0, 0, 0)
        self.rotate(self.angle)
        self.rect.center = pos
        self.alpha = 255

        self.turnSpeed = (self.targetAngle - self.angle) / turnSpeed

        for i in range(speed):
            self.points.append(
                pt.getPointOnLine(self.rect.centerx, self.rect.centery, target[0], target[1],
                                  (i / speed)))

    def rotate(self, angle):
        center = self.rect.center
        self.image = self.sprites[self.currentFrame]
        self.rect = self.image.get_rect()
        if self.scale < 1:
            self.image = pg.transform.scale(self.image,
                                        (round(self.rect.width * self.scale), self.rect.height))
        elif self.scale > 1:
            self.image = pg.transform.scale(self.image,
                                        (round(self.rect.width * self.scale), round(self.rect.height * self.scale)))
        self.rect = self.image.get_rect()
        self.image = pg.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        now = pg.time.get_ticks()
        if self.pointCounter < len(self.points) - 1:
            self.pointCounter += 1
        elif self.currentFrame < len(self.sprites) - 1 and self.laser is None:
            if self.laserDelay >= 15:
                if self.facing == "up" or self.facing == "down":
                    self.maxWidth = round(self.rect.width * 0.55)
                    self.laser = pg.rect.Rect(0, 0, 0, self.game.map.height * 2)
                elif self.facing == "left" or self.facing == "right":
                    self.maxWidth = round(self.rect.height * 0.55)
                    self.laser = pg.rect.Rect(0, 0, self.game.map.width * 2, 0)
                self.sizeIncreaseSpeed = round(self.maxWidth / self.sizeIncreaseSpeed)
            else:
                self.laserDelay += 1
        elif self.currentFrame < len(self.sprites) - 1 and self.laser is not None:
            if now - self.lastUpdate > 25:
                self.currentFrame += 1
                self.lastUpdate = now
                if self.currentFrame == 3:
                    self.game.gasterBlasterFireSound.play()
        else:
            if now - self.lastUpdate > 25:
                if self.currentFrame == 5:
                    self.currentFrame = 4
                else:
                    self.currentFrame = 5
                self.lastUpdate = now

        if self.angle < self.targetAngle:
            self.angle += self.turnSpeed
        else:
            self.angle = self.targetAngle

        self.rotate(self.angle)

        if self.laser is not None and self.currentFrame > len(self.sprites) - 3:
            self.vel += self.speed
            if not self.sizeIncrease: self.laserAlpha -= 2
            if self.facing == "up":
                self.rect.y += self.vel
                if self.sizeIncrease:
                    self.laser.width += self.sizeIncreaseSpeed
                    if self.laser.width >= self.maxWidth:
                        self.sizeIncrease = False
                elif self.laser.width >= 0:
                    self.laser.width -= round(self.sizeIncreaseSpeed * 0.2)

                if self.laser.width < 0:
                    self.game.sprites.remove(self)
                    self.laser.width = 0

                self.laser.midbottom = (self.rect.left, self.rect.top)
                self.laser.centerx += round(self.rect.width / 2)
                self.laser.bottom += round(self.rect.height * 0.45)
            elif self.facing == "down":
                self.rect.y -= self.vel

                if self.sizeIncrease:
                    self.laser.width += self.sizeIncreaseSpeed
                    if self.laser.width >= self.maxWidth:
                        self.sizeIncrease = False
                elif self.laser.width >= 0:
                    self.laser.width -= round(self.sizeIncreaseSpeed * 0.2)

                if self.laser.width < 0:
                    self.game.sprites.remove(self)
                    self.laser.width = 0

                self.laser.midtop = (self.rect.left, self.rect.bottom)
                self.laser.centerx += round(self.rect.width / 2)
                self.laser.top -= round(self.rect.height * 0.45)
            elif self.facing == "left":
                self.rect.x -= self.vel

                if self.sizeIncrease:
                    self.laser.height += self.sizeIncreaseSpeed
                    if self.laser.height >= self.maxWidth:
                        self.sizeIncrease = False
                elif self.laser.height >= 0:
                    self.laser.height -= round(self.sizeIncreaseSpeed * 0.2)

                if self.laser.height < 0:
                    self.game.sprites.remove(self)
                    self.laser.height = 0

                self.laser.right = self.rect.left + round(self.rect.width * 0.45)
                self.laser.centery = self.rect.top + round(self.rect.height / 2)
            elif self.facing == "right":
                self.rect.x += self.vel

                if self.sizeIncrease:
                    self.laser.height += self.sizeIncreaseSpeed
                    if self.laser.height >= self.maxWidth:
                        self.sizeIncrease = False
                elif self.laser.height >= 0:
                    self.laser.height -= round(self.sizeIncreaseSpeed * 0.2)

                if self.laser.height < 0:
                    self.game.sprites.remove(self)
                    self.laser.height = 0

                self.laser.left = self.rect.right - round(self.rect.width * 0.45)
                self.laser.centery = self.rect.top + round(self.rect.height / 2)

            self.laserSurf = pg.Surface((self.laser.width, self.laser.height))
            pg.draw.rect(self.laserSurf, white, pg.rect.Rect(0, 0, self.laser.width, self.laser.height))

            if self.game.player.stats["hp"] != 0 and self.laser.colliderect(self.game.player.rect) and self.laser.colliderect(self.game.player.imgRect):
                if not self.game.player.hit and self.game.player.canBeHit:
                    HitNumbers(self.game, self.game.room,
                               (self.game.player.rect.left, self.game.player.rect.top - 2),
                               (max(self.pow - self.game.player.stats["def"], 1)), "mario")
                    self.game.player.stats["hp"] -= (
                        max(self.pow - self.game.player.stats["def"], 1))
                    self.game.player.KR += 5
                    if self.game.player.stats["hp"] <= 0:
                        self.game.player.stats["hp"] = 0
                        self.game.player.currentFrame = 0
                        self.game.player.KR = 0
                    self.game.playerHitSound.play()

            if self.game.follower.stats["hp"] != 0 and self.laser.colliderect(self.game.follower.rect) and self.laser.colliderect(self.game.follower.imgRect):
                if not self.game.player.hit and self.game.follower.canBeHit:
                    HitNumbers(self.game, self.game.room,
                               (self.game.follower.rect.left, self.game.follower.rect.top - 2),
                               (max(self.pow - self.game.follower.stats["def"], 1)), "luigi")
                    self.game.follower.stats["hp"] -= (
                        max(self.pow - self.game.follower.stats["def"], 1))
                    self.game.follower.KR += 5
                    if self.game.follower.stats["hp"] <= 0:
                        self.game.follower.stats["hp"] = 0
                        self.game.follower.currentFrame = 0
                        self.game.follower.KR = 0
                    self.game.playerHitSound.play()
        else:
            self.rect.center = self.points[self.pointCounter]

    def draw(self):
        if self.laser is not None and self.currentFrame > len(self.sprites) - 3:
            self.game.blit_alpha(self.game.screen, self.laserSurf, self.game.camera.offset(self.laser), self.laserAlpha)
        self.game.blit_alpha(self.game.screen, self.image, self.game.camera.offset(self.rect), self.alpha)
