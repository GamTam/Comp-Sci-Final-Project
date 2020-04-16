from Overworld import *


class Cutscene:
    def __init__(self, game, scenes):
        self.over = False
        self.game = game
        self.scenes = scenes
        self.song = None
        self.textbox = [None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None,
                        None]
        self.flip = None
        self.currentScene = 0
        self.currentSubscene = 0
        self.action = 0

        self.xDest = [-69,
                      -69,
                      -69,
                      -69,
                      -69,
                      -69,
                      -69,
                      -69,
                      -69,
                      -69]
        self.yDest = [-69,
                      -69,
                      -69,
                      -69,
                      -69,
                      -69,
                      -69,
                      -69,
                      -69,
                      -69]
        self.points = []
        self.pointCounter = 0

        self.timer = 0

        while not self.over:
            if self.song is not None:
                self.game.playSong(self.song[0], self.song[1], self.song[2])
            self.game.calculatePlayTime()
            self.game.clock.tick(fps)
            self.game.events()

            self.game.fadeout.update()
            self.game.void.update(self.game.voidSize)
            [text.update() for text in self.game.textboxes]
            [sprite.update() for sprite in self.game.cutsceneSprites]
            self.game.camera.update(self.game.cameraRect.rect)
            self.action = 0
            for self.action in range(len(self.scenes[self.currentScene])):
                if self.action >= self.currentSubscene:
                    try:
                        eval(self.scenes[self.currentScene][self.action])
                    except:
                        exec(self.scenes[self.currentScene][self.action])

            self.game.screen.fill(black)
            try:
                self.game.screen.blit(self.game.map.background, self.game.map.rect)
            except:
                pass
            self.game.screen.blit(self.game.void.image, self.game.void.rect)
            self.game.screen.blit(self.game.map.image, self.game.camera.offset(self.game.map.rect))
            self.game.cutsceneSprites.sort(key=self.game.sortByYPos)
            for sprite in self.game.cutsceneSprites:
                try:
                    self.game.screen.blit(sprite.shadow, self.game.camera.offset(sprite.rect))
                except:
                    pass

            for sprite in self.game.cutsceneSprites:
                try:
                    sprite.draw()
                except:
                    self.game.blit_alpha(self.game.screen, sprite.image, self.game.camera.offset(sprite.imgRect),
                                         sprite.alpha)

            try:
                self.game.screen.blit(self.game.map.foreground, self.game.camera.offset(self.game.map.rect))
            except:
                pass

            [self.game.screen.blit(fad.image, (0, 0)) for fad in self.game.fadeout]

            [text.draw() for text in self.game.textboxes]

            pg.display.flip()

        self.game.updateOverworld()
        self.game.playtime -= 1

    def sceneEnd(self):
        if len(self.scenes[self.currentScene]) == 1:
            self.currentScene += 1
        else:
            if self.action == 0:
                self.currentSubscene += 1
                self.scenes[self.currentScene].insert(0, self.scenes[self.currentScene].pop(self.action))
            elif self.action != 0:
                self.currentSubscene += 1
                self.scenes[self.currentScene].insert(0, self.scenes[self.currentScene].pop(self.action))
            if self.currentSubscene == len(self.scenes[self.currentScene]):
                self.currentSubscene = 0
                self.currentScene += 1

        if self.currentScene > len(self.scenes) - 1:
            self.over = True

    def wait(self, seconds):
        self.timer += 1

        if self.timer >= seconds * fps:
            self.timer = 0
            self.sceneEnd()

    def setVar(self, var):
        exec(var)
        self.sceneEnd()

    def command(self, component):
        eval(component)
        self.sceneEnd()

    def textBox(self, target, text, type="dialogue", dir=None, choice=False, sound="default", complete=False, id=0):
        if self.textbox[id] is None:
            self.textbox[id] = TextBox(self.game, target, text, type, dir, choice, sound, complete)
        elif self.textbox[id].complete:
            self.textbox[id] = None
            target.talking = False
            self.sceneEnd()
        else:
            if self.textbox[id].talking:
                target.talking = True
            else:
                target.talking = False

    def flipIn(self, image, pos, turns=2, color=black, sound="default"):
        if self.flip is None:
            self.flip = LineFlipAppear(self.game, image, pos, turns, color, sound)
        elif self.flip.complete:
            self.flip = None
            self.sceneEnd()

    def move(self, obj, x, y, relative, spd, id=0):
        if self.xDest[id] == -69:
            if not relative:
                self.xDest[id] = x
                self.yDest[id] = y
            else:
                self.xDest[id] = obj.rect.centerx + x
                self.yDest[id] = obj.rect.centery + y

            for i in range(spd):
                self.points.append(
                    pt.getPointOnLine(obj.rect.centerx, obj.rect.centery, self.xDest[id], self.yDest[id], (i / spd)))

        if self.pointCounter < len(self.points):
            obj.rect.center = self.points[self.pointCounter]
            self.pointCounter += 1
        else:
            obj.rect.center = (self.xDest[id], self.yDest[id])
            self.pointCounter = 0
            self.points = []
            self.xDest[id] = -69
            self.yDest[id] = -69
            self.sceneEnd()

    def changeSong(self, song, prevCont=False):
        if prevCont:
            self.game.currentPoint += pg.mixer.music.get_pos()
        self.song = song
        self.sceneEnd()


class LoadCutscene:
    def __init__(self, game, rect, delete=False, auto=False, scenes=[["self.wait(2)"],["""self.textBox(self.game.player, ["You didn't say anything!"])"""]], id=0):
        self.game = game
        self.rect = rect
        self.delete = delete
        self.auto = auto
        self.scenes = scenes
        self.game.cutscenes.append(self)
        self.id = id

    def update(self):
        if self.id not in self.game.usedCutscenes:
            if self.auto:
                if self.delete:
                    self.game.usedCutscenes.append(self.id)
                Cutscene(self.game, self.scenes)
            else:
                if (self.game.leader == "mario" and pg.sprite.collide_rect(self.game.player, self)) or (self.game.leader == "luigi" and pg.sprite.collide_rect(self.game.follower, self)):
                    if self.delete:
                        self.game.usedCutscenes.append(self.id)
                    Cutscene(self.game, self.scenes)


class GoombaC(pg.sprite.Sprite):
    def __init__(self, pos):
        self.name = "GoombaC"
        pg.sprite.Sprite.__init__(self)
        sheet = spritesheet("sprites/minions.png", "sprites/minions.xml")

        self.images = [sheet.getImageName("goomba_1.png"),
                       sheet.getImageName("goomba_2.png"),
                       sheet.getImageName("goomba_3.png"),
                       sheet.getImageName("goomba_4.png"),
                       sheet.getImageName("goomba_5.png"),
                       sheet.getImageName("goomba_6.png"),
                       sheet.getImageName("goomba_7.png"),
                       sheet.getImageName("goomba_8.png")]

        self.rect = self.images[0].get_rect()
        self.rect.bottom = pos[1]
        self.rect.centerx = pos[0]
        self.currentFrame = random.randrange(0, len(self.images))
        self.lastUpdate = 0

    def update(self):
        now = pg.time.get_ticks()

        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.currentFrame < len(self.images):
                self.currentFrame = (self.currentFrame + 1) % (len(self.images))
            else:
                self.currentFrame = 0
            bottom = self.rect.bottom
            centerx = self.rect.centerx
            self.rect = self.images[self.currentFrame].get_rect()
            self.rect.bottom = bottom
            self.rect.centerx = centerx


class KoopaC(pg.sprite.Sprite):
    def __init__(self, pos):
        self.name = "KoopaC"
        pg.sprite.Sprite.__init__(self)
        sheet = spritesheet("sprites/minions.png", "sprites/minions.xml")

        self.images = [sheet.getImageName("koopa_1.png"),
                       sheet.getImageName("koopa_2.png"),
                       sheet.getImageName("koopa_3.png"),
                       sheet.getImageName("koopa_4.png"),
                       sheet.getImageName("koopa_5.png"),
                       sheet.getImageName("koopa_6.png"),
                       sheet.getImageName("koopa_7.png"),
                       sheet.getImageName("koopa_8.png"),
                       sheet.getImageName("koopa_9.png"),
                       sheet.getImageName("koopa_10.png"),
                       sheet.getImageName("koopa_11.png"),
                       sheet.getImageName("koopa_12.png"),
                       sheet.getImageName("koopa_13.png"),
                       sheet.getImageName("koopa_14.png"),
                       sheet.getImageName("koopa_15.png"),
                       sheet.getImageName("koopa_16.png"),
                       sheet.getImageName("koopa_17.png"),
                       sheet.getImageName("koopa_18.png")]

        self.rect = self.images[0].get_rect()
        self.rect.bottom = pos[1]
        self.rect.centerx = pos[0]
        self.currentFrame = random.randrange(0, len(self.images))
        self.lastUpdate = 0

    def update(self):
        now = pg.time.get_ticks()

        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.currentFrame < len(self.images):
                self.currentFrame = (self.currentFrame + 1) % (len(self.images))
            else:
                self.currentFrame = 0
            bottom = self.rect.bottom
            centerx = self.rect.centerx
            self.rect = self.images[self.currentFrame].get_rect()
            self.rect.bottom = bottom
            self.rect.centerx = centerx


class KoopaRC(pg.sprite.Sprite):
    def __init__(self, pos):
        self.name = "KoopaRC"
        pg.sprite.Sprite.__init__(self)
        sheet = spritesheet("sprites/minions.png", "sprites/minions.xml")

        self.images = [sheet.getImageName("koopa_red_1.png"),
                       sheet.getImageName("koopa_red_2.png"),
                       sheet.getImageName("koopa_red_3.png"),
                       sheet.getImageName("koopa_red_4.png"),
                       sheet.getImageName("koopa_red_5.png"),
                       sheet.getImageName("koopa_red_6.png"),
                       sheet.getImageName("koopa_red_7.png"),
                       sheet.getImageName("koopa_red_8.png"),
                       sheet.getImageName("koopa_red_9.png"),
                       sheet.getImageName("koopa_red_10.png"),
                       sheet.getImageName("koopa_red_11.png"),
                       sheet.getImageName("koopa_red_12.png"),
                       sheet.getImageName("koopa_red_13.png"),
                       sheet.getImageName("koopa_red_14.png"),
                       sheet.getImageName("koopa_red_15.png"),
                       sheet.getImageName("koopa_red_16.png"),
                       sheet.getImageName("koopa_red_17.png"),
                       sheet.getImageName("koopa_red_18.png")]

        self.rect = self.images[0].get_rect()
        self.rect.bottom = pos[1]
        self.rect.centerx = pos[0]
        self.currentFrame = random.randrange(0, len(self.images))
        self.lastUpdate = 0

    def update(self):
        now = pg.time.get_ticks()

        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.currentFrame < len(self.images):
                self.currentFrame = (self.currentFrame + 1) % (len(self.images))
            else:
                self.currentFrame = 0
            bottom = self.rect.bottom
            centerx = self.rect.centerx
            self.rect = self.images[self.currentFrame].get_rect()
            self.rect.bottom = bottom
            self.rect.centerx = centerx


class BooC(pg.sprite.Sprite):
    def __init__(self, pos):
        self.name = "BooC"
        pg.sprite.Sprite.__init__(self)
        sheet = spritesheet("sprites/minions.png", "sprites/minions.xml")

        self.images = [sheet.getImageName("boo_1.png"),
                       sheet.getImageName("boo_2.png"),
                       sheet.getImageName("boo_3.png"),
                       sheet.getImageName("boo_4.png"),
                       sheet.getImageName("boo_5.png"),
                       sheet.getImageName("boo_6.png"),
                       sheet.getImageName("boo_7.png"),
                       sheet.getImageName("boo_8.png"),
                       sheet.getImageName("boo_9.png"),
                       sheet.getImageName("boo_10.png"),
                       sheet.getImageName("boo_11.png"),
                       sheet.getImageName("boo_12.png"),
                       sheet.getImageName("boo_13.png"),
                       sheet.getImageName("boo_14.png"),
                       sheet.getImageName("boo_15.png"),
                       sheet.getImageName("boo_16.png")]

        self.rect = self.images[0].get_rect()
        self.rect.bottom = pos[1]
        self.rect.centerx = pos[0]
        self.currentFrame = random.randrange(0, len(self.images))
        self.lastUpdate = 0

    def update(self):
        now = pg.time.get_ticks()

        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.currentFrame < len(self.images):
                self.currentFrame = (self.currentFrame + 1) % (len(self.images))
            else:
                self.currentFrame = 0
            bottom = self.rect.bottom
            centerx = self.rect.centerx
            self.rect = self.images[self.currentFrame].get_rect()
            self.rect.bottom = bottom
            self.rect.centerx = centerx


class SpinyC(pg.sprite.Sprite):
    def __init__(self, pos):
        self.name = "SpinyC"
        pg.sprite.Sprite.__init__(self)
        sheet = spritesheet("sprites/minions.png", "sprites/minions.xml")

        self.images = [sheet.getImageName("spiny_1.png"),
                       sheet.getImageName("spiny_2.png"),
                       sheet.getImageName("spiny_3.png"),
                       sheet.getImageName("spiny_4.png"),
                       sheet.getImageName("spiny_5.png"),
                       sheet.getImageName("spiny_6.png"),
                       sheet.getImageName("spiny_7.png"),
                       sheet.getImageName("spiny_8.png"),
                       sheet.getImageName("spiny_9.png"),
                       sheet.getImageName("spiny_10.png"),
                       sheet.getImageName("spiny_11.png"),
                       sheet.getImageName("spiny_12.png"),
                       sheet.getImageName("spiny_13.png"),
                       sheet.getImageName("spiny_14.png"),
                       sheet.getImageName("spiny_15.png"),
                       sheet.getImageName("spiny_16.png"),
                       sheet.getImageName("spiny_17.png"),
                       sheet.getImageName("spiny_18.png"),
                       sheet.getImageName("spiny_19.png"),
                       sheet.getImageName("spiny_20.png")]

        self.rect = self.images[0].get_rect()
        self.rect.bottom = pos[1]
        self.rect.centerx = pos[0]
        self.currentFrame = random.randrange(0, len(self.images))
        self.lastUpdate = 0

    def update(self):
        now = pg.time.get_ticks()

        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.currentFrame < len(self.images):
                self.currentFrame = (self.currentFrame + 1) % (len(self.images))
            else:
                self.currentFrame = 0
            bottom = self.rect.bottom
            centerx = self.rect.centerx
            self.rect = self.images[self.currentFrame].get_rect()
            self.rect.bottom = bottom
            if self.currentFrame == 0:
                self.rect.centerx = centerx
            elif self.currentFrame == 1:
                self.rect.centerx = centerx + 2
            elif self.currentFrame == 2:
                self.rect.centerx = centerx + 2
            elif self.currentFrame == 3:
                self.rect.centerx = centerx + 2
            elif self.currentFrame == 4:
                self.rect.centerx = centerx - 2
            elif self.currentFrame == 5:
                self.rect.centerx = centerx - 2
            elif self.currentFrame == 6:
                self.rect.centerx = centerx - 2
            elif self.currentFrame == 7:
                self.rect.centerx = centerx - 2
            elif self.currentFrame == 8:
                self.rect.centerx = centerx
            elif self.currentFrame == 9:
                self.rect.centerx = centerx
            elif self.currentFrame == 10:
                self.rect.centerx = centerx + 2
            elif self.currentFrame == 11:
                self.rect.centerx = centerx + 2
            elif self.currentFrame == 12:
                self.rect.centerx = centerx - 2
            elif self.currentFrame == 13:
                self.rect.centerx = centerx + 2
            elif self.currentFrame == 14:
                self.rect.centerx = centerx - 2
            elif self.currentFrame == 15:
                self.rect.centerx = centerx - 2
            elif self.currentFrame == 16:
                self.rect.centerx = centerx + 2
            elif self.currentFrame == 17:
                self.rect.centerx = centerx - 2
            elif self.currentFrame == 18:
                self.rect.centerx = centerx + 2
            elif self.currentFrame == 19:
                self.rect.centerx = centerx


class ShyGuyC(pg.sprite.Sprite):
    def __init__(self, pos):
        self.name = "ShyGuyC"
        pg.sprite.Sprite.__init__(self)
        sheet = spritesheet("sprites/minions.png", "sprites/minions.xml")

        self.images = [sheet.getImageName("shy guy_1.png"),
                       sheet.getImageName("shy guy_2.png"),
                       sheet.getImageName("shy guy_3.png"),
                       sheet.getImageName("shy guy_4.png"),
                       sheet.getImageName("shy guy_5.png"),
                       sheet.getImageName("shy guy_6.png"),
                       sheet.getImageName("shy guy_7.png"),
                       sheet.getImageName("shy guy_8.png"),
                       sheet.getImageName("shy guy_9.png"),
                       sheet.getImageName("shy guy_10.png"),
                       sheet.getImageName("shy guy_11.png")]

        self.rect = self.images[0].get_rect()
        self.rect.bottom = pos[1]
        self.rect.centerx = pos[0]
        self.currentFrame = random.randrange(0, len(self.images))
        self.lastUpdate = 0

    def update(self):
        now = pg.time.get_ticks()

        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.currentFrame < len(self.images):
                self.currentFrame = (self.currentFrame + 1) % (len(self.images))
            else:
                self.currentFrame = 0
            bottom = self.rect.bottom
            centerx = self.rect.centerx
            self.rect = self.images[self.currentFrame].get_rect()
            self.rect.bottom = bottom
            self.rect.centerx = centerx


class MechaKoopaC(pg.sprite.Sprite):
    def __init__(self, pos):
        self.name = "MechaKoopaC"
        pg.sprite.Sprite.__init__(self)
        sheet = spritesheet("sprites/minions.png", "sprites/minions.xml")

        self.images = [sheet.getImageName("mecha koopa_1.png"),
                       sheet.getImageName("mecha koopa_2.png"),
                       sheet.getImageName("mecha koopa_3.png"),
                       sheet.getImageName("mecha koopa_4.png"),
                       sheet.getImageName("mecha koopa_5.png"),
                       sheet.getImageName("mecha koopa_6.png"),
                       sheet.getImageName("mecha koopa_7.png"),
                       sheet.getImageName("mecha koopa_8.png")]

        self.rect = self.images[0].get_rect()
        self.rect.bottom = pos[1]
        self.rect.centerx = pos[0]
        self.currentFrame = random.randrange(0, len(self.images))
        self.lastUpdate = 0

    def update(self):
        now = pg.time.get_ticks()

        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.currentFrame < len(self.images):
                self.currentFrame = (self.currentFrame + 1) % (len(self.images))
            else:
                self.currentFrame = 0
            bottom = self.rect.bottom
            centerx = self.rect.centerx
            self.rect = self.images[self.currentFrame].get_rect()
            self.rect.bottom = bottom
            self.rect.centerx = centerx


class PokeyC(pg.sprite.Sprite):
    def __init__(self, pos):
        self.name = "PokeyC"
        pg.sprite.Sprite.__init__(self)
        sheet = spritesheet("sprites/minions.png", "sprites/minions.xml")

        self.images = [sheet.getImageName("pokey_1.png"),
                       sheet.getImageName("pokey_2.png"),
                       sheet.getImageName("pokey_3.png"),
                       sheet.getImageName("pokey_4.png"),
                       sheet.getImageName("pokey_5.png"),
                       sheet.getImageName("pokey_6.png"),
                       sheet.getImageName("pokey_7.png"),
                       sheet.getImageName("pokey_8.png")]

        self.rect = self.images[0].get_rect()
        self.rect.bottom = pos[1]
        self.rect.centerx = pos[0]
        self.currentFrame = random.randrange(0, len(self.images))
        self.lastUpdate = 0

    def update(self):
        now = pg.time.get_ticks()

        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.currentFrame < len(self.images):
                self.currentFrame = (self.currentFrame + 1) % (len(self.images))
            else:
                self.currentFrame = 0
            bottom = self.rect.bottom
            centerx = self.rect.centerx
            self.rect = self.images[self.currentFrame].get_rect()
            self.rect.bottom = bottom
            self.rect.centerx = centerx


class MonteyMoleC(pg.sprite.Sprite):
    def __init__(self, pos):
        self.name = "MonteyMoleC"
        pg.sprite.Sprite.__init__(self)
        sheet = spritesheet("sprites/minions.png", "sprites/minions.xml")

        self.images = [sheet.getImageName("montey mole_1.png"),
                       sheet.getImageName("montey mole_2.png"),
                       sheet.getImageName("montey mole_3.png"),
                       sheet.getImageName("montey mole_4.png"),
                       sheet.getImageName("montey mole_5.png"),
                       sheet.getImageName("montey mole_6.png"),
                       sheet.getImageName("montey mole_7.png"),
                       sheet.getImageName("montey mole_8.png"),
                       sheet.getImageName("montey mole_9.png"),
                       sheet.getImageName("montey mole_10.png"),
                       sheet.getImageName("montey mole_11.png"),
                       sheet.getImageName("montey mole_12.png"),
                       sheet.getImageName("montey mole_13.png"),
                       sheet.getImageName("montey mole_14.png"),
                       sheet.getImageName("montey mole_15.png"),
                       sheet.getImageName("montey mole_16.png"),
                       sheet.getImageName("montey mole_17.png"),
                       sheet.getImageName("montey mole_18.png"),
                       sheet.getImageName("montey mole_19.png"),
                       sheet.getImageName("montey mole_20.png"),
                       sheet.getImageName("montey mole_21.png"),
                       sheet.getImageName("montey mole_22.png")]

        self.rect = self.images[0].get_rect()
        self.rect.bottom = pos[1]
        self.rect.centerx = pos[0]
        self.currentFrame = random.randrange(0, len(self.images))
        self.lastUpdate = 0

    def update(self):
        now = pg.time.get_ticks()

        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.currentFrame < len(self.images):
                self.currentFrame = (self.currentFrame + 1) % (len(self.images))
            else:
                self.currentFrame = 0
            bottom = self.rect.bottom
            centerx = self.rect.centerx
            self.rect = self.images[self.currentFrame].get_rect()
            self.rect.bottom = bottom
            self.rect.centerx = centerx


class EmptyObject(pg.sprite.Sprite):
    def __init__(self, image, shadow, imagePos, shadowPos):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.shadow = shadow
        self.rect = self.shadow.get_rect()
        self.rect.center = shadowPos
        self.imgRect = self.image.get_rect()
        self.imgRect.center = imagePos
        self.alpha = 255


class marioCutscene(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.cutsceneSprites.append(self)
        self.loadImages()
        self.image = self.game.player.image
        self.shadow = self.game.player.shadow
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.imgRect = self.image.get_rect()
        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx
        self.lastUpdate = 0
        self.currentFrame = 0
        self.alpha = 255
        self.walking = False
        self.facing = self.game.player.facing

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

    def update(self):
        now = pg.time.get_ticks()
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
        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx


class luigiCutscene(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.cutsceneSprites.append(self)
        self.loadImages()
        self.image = self.game.follower.image
        self.shadow = self.game.follower.shadow
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.imgRect = self.image.get_rect()
        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx
        self.lastUpdate = 0
        self.currentFrame = 0
        self.alpha = 255
        self.walking = False
        self.facing = self.game.follower.facing

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

    def update(self):
        now = pg.time.get_ticks()
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
        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx


class starlowCutscene(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.cutsceneSprites.append(self)
        self.loadImages()
        self.image = self.game.player.image
        self.shadow = self.game.player.shadow
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.imgRect = self.image.get_rect()
        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx
        self.lastUpdate = 0
        self.currentFrame = 0
        self.alpha = 255
        self.talking = False
        self.facing = "down"

    def loadImages(self):
        sheet = spritesheet("sprites/starlow.png", "sprites/starlow.xml")

        self.idleFramesDownRight = [sheet.getImageName("starlow_downright_1.png"),
                                   sheet.getImageName("starlow_downright_2.png"),
                                   sheet.getImageName("starlow_downright_3.png"),
                                   sheet.getImageName("starlow_downright_4.png"),
                                   sheet.getImageName("starlow_downright_5.png"),
                                   sheet.getImageName("starlow_downright_6.png")]

        self.idleFramesRight = [sheet.getImageName("starlow_right_1.png"),
                                    sheet.getImageName("starlow_right_2.png"),
                                    sheet.getImageName("starlow_right_3.png"),
                                    sheet.getImageName("starlow_right_4.png"),
                                    sheet.getImageName("starlow_right_5.png"),
                                    sheet.getImageName("starlow_right_6.png")]

        self.idleFramesUpRight = [sheet.getImageName("starlow_upright_1.png"),
                                    sheet.getImageName("starlow_upright_2.png"),
                                    sheet.getImageName("starlow_upright_3.png"),
                                    sheet.getImageName("starlow_upright_4.png"),
                                    sheet.getImageName("starlow_upright_5.png"),
                                    sheet.getImageName("starlow_upright_6.png")]

        self.talkingFramesRight = [sheet.getImageName("starlow_talking_right_1.png"),
                                sheet.getImageName("starlow_talking_right_2.png"),
                                sheet.getImageName("starlow_talking_right_3.png"),
                                sheet.getImageName("starlow_talking_right_4.png"),
                                sheet.getImageName("starlow_talking_right_5.png"),
                                sheet.getImageName("starlow_talking_right_6.png"),
                                sheet.getImageName("starlow_talking_right_7.png"),
                                sheet.getImageName("starlow_talking_right_8.png")]

        self.talkingFramesUpRight = [sheet.getImageName("starlow_talking_upright_1.png"),
                                   sheet.getImageName("starlow_talking_upright_2.png"),
                                   sheet.getImageName("starlow_talking_upright_3.png"),
                                   sheet.getImageName("starlow_talking_upright_4.png"),
                                   sheet.getImageName("starlow_talking_upright_5.png"),
                                   sheet.getImageName("starlow_talking_upright_6.png"),
                                   sheet.getImageName("starlow_talking_upright_7.png"),
                                   sheet.getImageName("starlow_talking_upright_8.png")]

        self.talkingFramesRight = [sheet.getImageName("starlow_talking_right_1.png"),
                                   sheet.getImageName("starlow_talking_right_2.png"),
                                   sheet.getImageName("starlow_talking_right_3.png"),
                                   sheet.getImageName("starlow_talking_right_4.png"),
                                   sheet.getImageName("starlow_talking_right_5.png"),
                                   sheet.getImageName("starlow_talking_right_6.png"),
                                   sheet.getImageName("starlow_talking_right_7.png"),
                                   sheet.getImageName("starlow_talking_right_8.png")]

        self.shadow = sheet.getImageName("shadow.png")

    def update(self):
        now = pg.time.get_ticks()
        if self.talking:
            if self.facing == "upright":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesUpRight):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesUpRight))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.talkingFramesUpRight[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "downright":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesDownRight):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesDownRight))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.talkingFramesDownRight[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "right":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesRight):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesRight))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.talkingFramesRight[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
        else:
            if self.facing == "upright":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.idleFramesUpRight):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.idleFramesUpRight))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.idleFramesUpRight[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "downright":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.idleFramesDownRight):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.idleFramesDownRight))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.idleFramesDownRight[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "right":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.idleFramesRight):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.idleFramesRight))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.idleFramesRight[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
        self.imgRect.bottom = self.rect.top - 25
        self.imgRect.centerx = self.rect.centerx


class toadleyCutscene(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.cutsceneSprites.append(self)
        self.loadImages()
        self.image = self.game.player.image
        self.shadow = self.game.player.shadow
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.imgRect = self.image.get_rect()
        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx
        self.lastUpdate = 0
        self.currentFrame = 0
        self.alpha = 255
        self.talking = False
        self.facing = "down"

    def loadImages(self):
        sheet = spritesheet("sprites/toadley.png", "sprites/toadley.xml")

        self.talkingFramesDown = [sheet.getImageName("talking_down_1.png"),
                                  sheet.getImageName("talking_down_2.png"),
                                  sheet.getImageName("talking_down_3.png"),
                                  sheet.getImageName("talking_down_4.png"),
                                  sheet.getImageName("talking_down_5.png"),
                                  sheet.getImageName("talking_down_6.png")]

        self.talkingFramesDownLeft = [sheet.getImageName("talking_downleft_1.png"),
                                  sheet.getImageName("talking_downleft_2.png"),
                                  sheet.getImageName("talking_downleft_3.png"),
                                  sheet.getImageName("talking_downleft_4.png"),
                                  sheet.getImageName("talking_downleft_5.png"),
                                  sheet.getImageName("talking_downleft_6.png")]

        self.idleFrameDown = sheet.getImageName("standing_down.png")

        self.idleFrameDownleft = sheet.getImageName("standing_downleft.png")

        self.shadow = sheet.getImageName("shadow.png")

    def update(self):
        now = pg.time.get_ticks()
        if self.talking:
            if self.facing == "upright":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesUpRight):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesUpRight))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.talkingFramesUpRight[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "downright":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesDownRight):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesDownRight))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.talkingFramesDownRight[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "downleft":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesDownLeft):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesDownLeft))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.talkingFramesDownLeft[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "right":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesRight):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesRight))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.talkingFramesRight
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "down":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesDown):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesDown))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.talkingFramesDown[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
        else:
            if self.facing == "upright":
                center = self.imgRect.center
                self.image = self.idleFrameUpRight
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "downright":
                center = self.imgRect.center
                self.image = self.idleFrameDownRight
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "right":
                center = self.imgRect.center
                self.image = self.idleFrameRight
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "down":
                center = self.imgRect.center
                self.image = self.idleFrameDown
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
            elif self.facing == "downleft":
                center = self.imgRect.center
                self.image = self.idleFrameDownleft
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        self.imgRect.bottom = self.rect.bottom - 2
        self.imgRect.centerx = self.rect.centerx


class LineFlipAppear(pg.sprite.Sprite):
    def __init__(self, game, image, pos, turns=2, color=black, sound="default"):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.game.cutsceneSprites.append(self)
        if type(image) is list:
            self.image = CombineSprites([image[0][i] for i in range(len(image))],
                                        [image[1][i] for i in range(len(image))])
            self.image = self.image.image
            self.unharmedImage = self.image.copy()
        else:
            self.unharmedImage = image
            self.image = image
        self.maxRect = self.image.get_rect()
        self.maxRect.center = pos
        self.rect = pg.rect.Rect(pos[0], self.maxRect.top - 10, 0, 0)
        self.alpha = 255
        self.scale = 0
        self.turns = 0
        self.rate = 0.125
        self.counter = turns
        self.game.lineDrawSound.play()
        self.complete = False
        self.color = color
        self.hasPlayedSound = False
        self.turnSound = pg.mixer.Sound("sounds/" + sound + "TurnSound.ogg")

    def update(self):
        if self.rect.height < self.maxRect.height + 20 and not self.complete:
            self.rect.height += round((self.maxRect.height + 20) / (fps / 2.5))
            self.rect.top = self.maxRect.top - 10
        elif self.turns < self.counter or self.scale < 1:
            self.rect.height = self.maxRect.height + 20
            if not self.hasPlayedSound:
                self.turnSound.play()
                self.hasPlayedSound = True
            if abs(self.scale) < 1:
                self.scale += self.rate
                self.rect.width = round(abs((self.maxRect.width + 20) * self.scale))
            else:
                self.rate *= -1
                self.turns += 1
                self.scale += self.rate
                self.rect.width = round(abs((self.maxRect.width + 20) * self.scale))

            self.rect.center = self.maxRect.center
        else:
            if self.rect.height > 0 - round((self.maxRect.height + 20) / (fps / 2)):
                self.rect.height -= round((self.maxRect.height + 20) / (fps / 2))
                self.rect.center = self.maxRect.center
            if self.rect.height < 0 - round((self.maxRect.height + 20) / (fps / 2)):
                self.game.cutsceneSprites.remove(self)
                self.rect.height = 0
                self.rect.center = self.maxRect.center
            self.complete = True

    def draw(self):
        if self.scale < 0:
            self.image = pg.transform.flip(self.unharmedImage, True, False)
        else:
            self.image = self.unharmedImage.copy()

        self.image = pg.transform.scale(self.image,
                                        (round(abs((self.maxRect.width * self.scale))), self.maxRect.height))

        self.imgRect = self.image.get_rect()
        self.imgRect.center = self.rect.center

        if self.rect.height >= (self.maxRect.height + 20) - round((self.maxRect.height + 20) / (fps / 2)):
            self.game.screen.blit(self.image, self.game.camera.offset(self.imgRect))
        if self.rect.height > 0 - round((self.maxRect.height + 20) / (fps / 2)):
            pg.draw.rect(self.game.screen, black, self.game.camera.offset(self.rect), 3)


class LineFlipDisappear(pg.sprite.Sprite):
    def __init__(self, game, image, pos, turns=3, color=black, sound="default"):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.unharmedImage = image
        self.image = image
        self.maxRect = self.image.get_rect()
        self.maxRect.center = pos
        self.rect = pg.rect.Rect(pos[0], self.maxRect.top - 10, 0, 0)
        self.alpha = 255
        self.scale = 1
        self.turns = 0
        self.rate = 0.125
        self.counter = turns
        self.imgRect = self.image.get_rect()
        self.imgRect.center = self.maxRect.center
        self.complete = False
        self.color = color
        self.hasPlayedLineSound = False
        self.hasPlayedTurnSound = False
        self.turnSound = pg.mixer.Sound("sounds/" + sound + "TurnSound.ogg")

    def update(self):
        if self.rect.height < self.maxRect.height + 20 and not self.complete:
            if not self.hasPlayedLineSound:
                self.game.lineDrawSound.play()
                self.hasPlayedLineSound = True
            self.rect.height += round((self.maxRect.height + 20) / (fps / 2.5))
            self.rect.width += round((self.maxRect.width + 20) / (fps / 2.5))
            self.rect.top = self.maxRect.top - 10
            self.rect.left = self.maxRect.left - 10
        elif self.turns < self.counter or self.scale != 0:
            self.rect.height = self.maxRect.height + 20
            if not self.hasPlayedTurnSound:
                self.turnSound.play()
                self.hasPlayedTurnSound = True
            if abs(self.scale) < 1:
                self.scale += self.rate
                self.rect.width = round(abs((self.maxRect.width + 20) * self.scale))
            else:
                self.rate *= -1
                self.scale += self.rate
                self.rect.width = round(abs((self.maxRect.width + 20) * self.scale))

            if self.scale == 0:
                self.turns += 1

            self.rect.center = self.maxRect.center
        else:
            self.complete = True

        if self.scale < 0:
            self.image = pg.transform.flip(self.unharmedImage, True, False)
        else:
            self.image = self.unharmedImage.copy()

        self.image = pg.transform.scale(self.image,
                                        (round(abs((self.maxRect.width * self.scale))), self.maxRect.height))

        self.imgRect = self.image.get_rect()
        self.imgRect.center = self.maxRect.center

    def draw(self):
        if not self.complete:
            self.game.screen.blit(self.image, self.game.camera.offset(self.imgRect))
            if self.rect.height != 0:
                pg.draw.rect(self.game.screen, black, self.game.camera.offset(self.rect), 3)


class EggMcMuffin(pg.sprite.Sprite):
    def __init__(self, pos, color, game):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("sprites/Egg McMuffin.png").convert_alpha()
        if color == black:
            self.image.fill(color, special_flags=pg.BLEND_MULT)
            self.game.blit_alpha(self.image, pg.image.load("sprites/Egg McMuffin.png").convert_alpha(), pg.rect.Rect(0, 0, 0, 0), 155)
        else:
            self.image.fill(color, special_flags=pg.BLEND_ADD)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.imgRect = self.rect
        self.alpha = 255


# Skrx on Stack Overflow
class CombineSprites(pg.sprite.Sprite):
    def __init__(self, sprites, rects):
        super().__init__()
        # Combine the rects of the separate sprites.
        self.rect = rects[0].copy()
        for rect in rects[1:]:
            self.rect.union_ip(rect)

        # Create a new transparent image with the combined size.
        self.image = pg.Surface(self.rect.size, pg.SRCALPHA)

        # Now blit all sprites onto the new surface.
        for i in range(len(sprites)):
            self.image.blit(sprites[i], (rects[i].x - self.rect.left,
                                         rects[i].y - self.rect.top))

        # pg.display.flip()
