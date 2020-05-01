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
        self.description.append("These little guys will run \nback and forth across the screen\nand hope they hit you.")
        self.description.append("Max HP is " + str(self.stats["maxHP"]) + ",/p\nAttack is " + str(
            self.stats["pow"]) + ",/p\nDefence is " + str(self.stats["def"]) + ".")
        self.description.append('''The main motto of the Goomba is\n"March straight ahead into\nthe enemy's feet".''')
        self.description.append("Or,/5 at least that's what Bowser \nsays.")

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
                    pg.K_m] and self.game.player.going == "down" and self.game.player.imgRect.bottom <= self.imgRect.top + 50:
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
                                       (self.game.player.imgRect.left, self.game.player.imgRect.top - 2),
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
                    pg.K_l] and self.game.follower.going == "down" and self.game.follower.imgRect.bottom <= self.imgRect.top + 50:
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
                                       (self.game.follower.imgRect.left, self.game.follower.imgRect.top - 2),
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
                            "Koopas wander around until you get\nclose to them, then they\ngo into their shells.",
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
            if self.rectHP > self.stats["hp"] and self.hpSpeed < 0:
                self.rectHP += self.hpSpeed
            elif self.rectHP < self.stats["hp"] and self.hpSpeed > 0:
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
                        pg.K_m] and self.game.player.going == "down" and self.game.player.imgRect.bottom <= self.imgRect.top + 50:
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
                                           (self.game.player.imgRect.left, self.game.player.imgRect.top - 2),
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
                        pg.K_l] and self.game.follower.going == "down" and self.game.follower.imgRect.bottom <= self.imgRect.top + 50:
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
                                           (self.game.follower.imgRect.left, self.game.follower.imgRect.top - 2),
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
                                       (self.game.player.imgRect.left, self.game.player.imgRect.top - 2),
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
                        pg.K_l] and self.game.follower.going == "down" and self.game.follower.imgRect.bottom <= self.imgRect.top + 50:
                        doubleDamageL = True
                    if hitsRound2:
                        if self.game.follower.stats["hp"] != 0:
                            if not self.game.follower.hit and self.stats[
                                "hp"] > 0 and not self.hit and self.game.follower.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.follower.imgRect.left, self.game.follower.imgRect.top - 2),
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
        self.rectHP = self.stats["hp"]

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
            self.hpSpeed = (self.stats["hp"] - self.rectHP) / 30

        if self.hpSpeed != 0:
            if self.rectHP > self.stats["hp"] and self.hpSpeed < 0:
                self.rectHP += self.hpSpeed
            elif self.rectHP < self.stats["hp"] and self.hpSpeed > 0:
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
                        pg.K_m] and self.game.player.going == "down" and self.game.player.imgRect.bottom <= self.imgRect.top + 50:
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
                                "hp"] > 0 and not self.is_hit and self.game.player.canBeHit:
                                HitNumbers(self.game, self.game.room,
                                           (self.game.player.imgRect.left, self.game.player.imgRect.top - 2),
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
                                       (self.game.player.imgRect.left, self.game.player.imgRect.top - 2),
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
        self.rectHP = self.stats["hp"]

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
            self.hpSpeed = (self.stats["hp"] - self.rectHP) / 30

        if self.hpSpeed != 0:
            if self.rectHP > self.stats["hp"] and self.hpSpeed < 0:
                self.rectHP += self.hpSpeed
            elif self.rectHP < self.stats["hp"] and self.hpSpeed > 0:
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
                hitsRound2 = self.imgRect.colliderect(self.game.player.imgRect)
                if hitsRound2:
                    if not self.game.player.hit and self.stats[
                        "hp"] > 0 and not self.is_hit and self.game.player.canBeHit:
                        HitNumbers(self.game, self.game.room,
                                   (self.game.player.imgRect.left, self.game.player.imgRect.top - 2),
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
                hitsRound2 = self.imgRect.colliderect(self.game.follower.imgRect)
                if hitsRound2:
                    if not self.game.follower.hit and self.stats[
                        "hp"] > 0 and not self.is_hit and self.game.follower.canBeHit:
                        HitNumbers(self.game, self.game.room,
                                   (self.game.follower.imgRect.left, self.game.follower.imgRect.top - 2),
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
