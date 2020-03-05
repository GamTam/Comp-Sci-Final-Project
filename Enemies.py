from Overworld import *
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
    def __init__(self, game, x, y, battle):
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

    def update(self):
        self.animate()
        if self.stats["hp"] <= 0:
            self.going = False
            self.alpha -= 10

        if self.alpha <= 0:
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
                                       (2 * (self.game.player.stats["pow"] - self.stats["def"])))
                            self.stats["hp"] -= 2 * (self.game.player.stats["pow"] - self.stats["def"])
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                        else:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (self.game.player.stats["pow"] - self.stats["def"]))
                            self.stats["hp"] -= (self.game.player.stats["pow"] - self.stats["def"])
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                        self.game.player.airTimer = 0
                    else:
                        if not self.game.player.hit and self.stats["hp"] > 0 and not self.hit and self.game.player.canBeHit:
                            HitNumbers(self.game, self.game.room, (self.game.player.imgRect.left, self.game.player.imgRect.top - 2),(max(self.stats["pow"] - self.game.player.stats["def"], 1)), "mario")
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
                                       (2 * (self.game.follower.stats["pow"] - self.stats["def"])))
                            self.stats["hp"] -= 2 * (self.game.follower.stats["pow"] - self.stats["def"])
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                        else:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       (self.game.follower.stats["pow"] - self.stats["def"]))
                            self.stats["hp"] -= (self.game.follower.stats["pow"] - self.stats["def"])
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            self.hit = True
                        self.game.follower.airTimer = 0
                    else:
                        if not self.game.follower.hit and self.stats["hp"] > 0 and not self.hit and self.game.follower.canBeHit:
                            HitNumbers(self.game, self.game.room, (self.game.follower.imgRect.left, self.game.follower.imgRect.top - 2), (max(self.stats["pow"] - self.game.follower.stats["def"], 1)), "luigi")
                            self.game.follower.stats["hp"] -= (max(self.stats["pow"] - self.game.follower.stats["def"], 1))
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
                if hammerHitsRound2 and not self.hit:
                    HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                               round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5))
                    self.stats["hp"] -= round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5)
                    if self.stats["hp"] <= 0:
                        self.game.enemyDieSound.play()
                    self.game.enemyHitSound.play()
                    self.hit = True

        if self.stats["hp"] != 0 and self.game.follower.isHammer is not None:
            hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
            if hammerHits:
                hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                if hammerHitsRound2 and not self.hit:
                    HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                               round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5))
                    self.stats["hp"] -= round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5)
                    if self.stats["hp"] <= 0:
                        self.game.enemyDieSound.play()
                    self.game.enemyHitSound.play()
                    self.hit = True


class GoombaKing(pg.sprite.Sprite):
    def __init__(self, game, start):
        pg.sprite.Sprite.__init__(self, game.npcs)
        self.text = []
        self.game = game
        self.textbox = None
        self.canTalk = True
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
        self.text.append("WHO DARES DISTURB THE GREAT \nGOOMBA KING?")
        self.text.append("Oh./p It's you.")
        self.text.append(
            "I have heard about all of your feats\nof strength, and I am telling you\nthat no one is stronger than me!")
        self.text.append("So,/5/5/5 MARIO!/p LUIGI!/p\nLet the battle of the century.../P\nBEGIN!")

    def update(self):
        if self.textbox is None:
            keys = pg.key.get_pressed()
            if pg.sprite.collide_rect_ratio(1.1)(self, self.game.player) and keys[pg.K_m]:
                if not self.game.player.jumping:
                    self.textbox = TextBox(self.game, self, self.text)
        elif self.textbox != "complete":
            pg.event.clear()
        else:
            self.textbox = None
            self.game.loadBattle("THB15G")


class GoombaSmolText(pg.sprite.Sprite):
    def __init__(self, game, start, hastexted=False):
        pg.sprite.Sprite.__init__(self, game.npcs)
        self.smoltext = []
        self.text = []
        self.game = game
        self.canTalk = True
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
        if not hastexted:
            self.counter = 0
        else:
            self.counter = 1
        self.text.append("Hello.")
        self.text.append("The phrase that many people use to\nrefer to me is Jeff.")
        self.smoltext.append("My name's jeff!")

    def update(self):
        if self.counter == 0:
            if self.textbox is None:
                keys = pg.key.get_pressed()
                if pg.sprite.collide_rect_ratio(1.1)(self, self.game.player) and keys[pg.K_m]:
                    if not self.game.player.jumping:
                        self.textbox = TextBox(self.game, self, self.text)
                        self.game.goombaHasTexted = True
            elif self.textbox != "complete":
                pg.event.clear()
            else:
                self.textbox = None
                self.counter += 1
        elif self.counter == 1:
            self.canTalk = False
            if self.textbox is None:
                if pg.sprite.collide_rect_ratio(1.5)(self, self.game.player):
                    self.textbox = MiniTextbox(self.game, self, self.smoltext, (self.rect.centerx, self.rect.top - 70))
            elif self.textbox is not None:
                if not pg.sprite.collide_rect_ratio(1.5)(self, self.game.player):
                    self.textbox.closing = True


class CountBleck(pg.sprite.Sprite):
    def __init__(self, game, pos):
        pg.sprite.Sprite.__init__(self, game.npcs)
        self.text = []
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
        self.text.append("COUNT BLECK IS THE DELETER\nOF WORLDS! MY FATE IS WRITTEN\nIN THE DARK PROGNOSTICUS!")
        self.text.append("ARE YOU PREPARED, HEROES?")
        self.text.append("OUR DUEL WILL BE WORTHY OF\nTHE LAST CLASH THE WORLDS WILL\nEVER SEE!")

    def loadImages(self):
        sheet = spritesheet("sprites/count bleck_idle.png", "sprites/count bleck_idle.xml")

        self.sprites = [sheet.getImageName("count_bleck_idle_00.png"),
                        sheet.getImageName("count_bleck_idle_01.png"),
                        sheet.getImageName("count_bleck_idle_02.png"),
                        sheet.getImageName("count_bleck_idle_03.png"),
                        sheet.getImageName("count_bleck_idle_04.png"),
                        sheet.getImageName("count_bleck_idle_05.png"),
                        sheet.getImageName("count_bleck_idle_06.png"),
                        sheet.getImageName("count_bleck_idle_07.png"),
                        sheet.getImageName("count_bleck_idle_08.png"),
                        sheet.getImageName("count_bleck_idle_09.png"),
                        sheet.getImageName("count_bleck_idle_10.png"),
                        sheet.getImageName("count_bleck_idle_11.png"),
                        sheet.getImageName("count_bleck_idle_12.png"),
                        sheet.getImageName("count_bleck_idle_13.png"),
                        sheet.getImageName("count_bleck_idle_14.png"),
                        sheet.getImageName("count_bleck_idle_15.png"),
                        sheet.getImageName("count_bleck_idle_16.png"),
                        sheet.getImageName("count_bleck_idle_17.png"),
                        sheet.getImageName("count_bleck_idle_18.png"),
                        sheet.getImageName("count_bleck_idle_19.png"),
                        sheet.getImageName("count_bleck_idle_20.png"),
                        sheet.getImageName("count_bleck_idle_21.png"),
                        sheet.getImageName("count_bleck_idle_22.png"),
                        sheet.getImageName("count_bleck_idle_23.png"),
                        sheet.getImageName("count_bleck_idle_24.png"),
                        sheet.getImageName("count_bleck_idle_25.png"),
                        sheet.getImageName("count_bleck_idle_26.png"),
                        sheet.getImageName("count_bleck_idle_27.png"),
                        sheet.getImageName("count_bleck_idle_28.png"),
                        sheet.getImageName("count_bleck_idle_29.png"),
                        sheet.getImageName("count_bleck_idle_30.png"),
                        sheet.getImageName("count_bleck_idle_31.png"),
                        sheet.getImageName("count_bleck_idle_32.png"),
                        sheet.getImageName("count_bleck_idle_33.png"),
                        sheet.getImageName("count_bleck_idle_34.png"),
                        sheet.getImageName("count_bleck_idle_35.png"),
                        sheet.getImageName("count_bleck_idle_36.png"),
                        sheet.getImageName("count_bleck_idle_37.png"),
                        sheet.getImageName("count_bleck_idle_38.png"),
                        sheet.getImageName("count_bleck_idle_39.png"),
                        sheet.getImageName("count_bleck_idle_40.png"),
                        sheet.getImageName("count_bleck_idle_41.png"),
                        sheet.getImageName("count_bleck_idle_42.png"),
                        sheet.getImageName("count_bleck_idle_43.png"),
                        sheet.getImageName("count_bleck_idle_44.png"),
                        sheet.getImageName("count_bleck_idle_45.png"),
                        sheet.getImageName("count_bleck_idle_46.png"),
                        sheet.getImageName("count_bleck_idle_47.png"),
                        sheet.getImageName("count_bleck_idle_48.png"),
                        sheet.getImageName("count_bleck_idle_49.png"),
                        sheet.getImageName("count_bleck_idle_50.png")]

        self.shadow = sheet.getImageName("count_bleck_shadow.png")

    def update(self):
        self.animate()
        if self.textbox is None:
            keys = pg.key.get_pressed()
            if pg.sprite.collide_rect_ratio(1.1)(self, self.game.player) and keys[pg.K_m]:
                if not self.game.player.jumping:
                    pg.mixer.music.fadeout(200)
                    self.game.playsong = False
                    self.game.firstLoop = True
                    self.textbox = TextBox(self.game, self, self.text)
        elif self.textbox != "complete":
            if not pg.mixer.music.get_busy() or self.textbox.rect.center == self.textbox.points[-1]:
                self.game.playSong(10.314, 32.016, "the evil count bleck")
            pg.event.clear()
        else:
            self.textbox = None
            self.game.loadBattle("self.loadTeeheeValleyBattle15G()")

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 2:
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