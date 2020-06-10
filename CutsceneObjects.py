from Overworld import *
import random
from statemachine import StateMachine, State
from math import sin, cos, pi, atan2


def project(pos, angle, distance):
    return (pos[0] + (cos(angle) * distance),
            pos[1] - (sin(angle) * distance))


def get_angle(origin, destination):
    x_dist = destination[0] - origin[0]
    y_dist = destination[1] - origin[1]
    return atan2(-y_dist, x_dist) % (2 * pi)


class Cutscene:
    def __init__(self, game, scenes, parent=None, currentScene=0, currentSubscene=0):
        self.over = False
        self.flash = None
        self.game = game
        self.game.cutsceneSprites = []
        self.parent = parent
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
        self.flip = [None,
                     None,
                     None,
                     None,
                     None,
                     None,
                     None,
                     None,
                     None,
                     None]
        self.currentScene = currentScene
        self.currentSubscene = currentSubscene
        self.contSong = False
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
        self.points = [[],
                       [],
                       [],
                       [],
                       [],
                       [],
                       [],
                       [],
                       [],
                       []]
        self.pointCounter = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.mcMuffinSprites = []

        self.timer = 0
        self.counter = 0

        for sprite in self.game.sprites:
            if type(sprite).__name__ == "Decoration":
                self.game.cutsceneSprites.append(sprite)

        for sprite in self.game.blocks:
            self.game.cutsceneSprites.append(sprite)

        while not self.over:
            if self.song is not None:
                self.game.playSong(self.song[0], self.song[1], self.song[2], cont=self.contSong)
            self.game.calculatePlayTime()
            self.game.clock.tick(fps)
            self.game.events()

            [fad.update() for fad in self.game.fadeout]
            self.game.void.update(self.game.voidSize)
            [text.update() for text in self.game.textboxes]
            [sprite.update() for sprite in self.game.cutsceneSprites]
            [effect.update() for effect in self.game.effects]
            if self.game.cameraRect.cameraShake != 0:
                cameraCenter = self.game.cameraRect.rect.center
                self.game.cameraRect.actualPos = self.game.cameraRect.rect.center
                self.game.cameraRect.shakePart1()
                self.game.cameraRect.shakePart2()
            self.game.camera.update(self.game.cameraRect.rect)
            if self.game.cameraRect.cameraShake != 0:
                self.game.cameraRect.rect.center = cameraCenter
            self.action = 0
            for self.action in range(len(self.scenes[self.currentScene])):
                if self.action >= self.currentSubscene:
                    try:
                        eval(self.scenes[self.currentScene][self.action])
                    except:
                        exec(self.scenes[self.currentScene][self.action])

            drawBackground = True
            for fade in self.game.fadeout:
                if fade.alpha >= 250:
                    drawBackground = False

            self.game.screen.fill(black)
            if self.game.area == "Last Corridor" and self.game.room != "battle":
                for sprite in self.game.cutsceneSprites:
                    if sprite not in self.game.blocks:
                        sprite.image = sprite.image.copy()
                        sprite.image.fill((0, 0, 0, 255), special_flags=pg.BLEND_RGBA_MIN)
            if drawBackground:
                try:
                    self.game.screen.blit(self.game.map.background, self.game.map.rect)
                except:
                    pass
                if self.game.area != "Castle Bleck" and self.game.area != "Last Corridor":
                    self.game.screen.blit(self.game.void.image, self.game.void.rect)
                self.game.screen.blit(self.game.map.image, self.game.camera.offset(self.game.map.rect))
                self.game.cutsceneSprites.sort(key=self.game.sortByYPos)
                for sprite in self.game.cutsceneSprites:
                    try:
                        if sprite not in self.mcMuffinSprites:
                            self.game.screen.blit(sprite.shadow, self.game.camera.offset(sprite.rect))
                    except:
                        pass

                for sprite in self.game.cutsceneSprites:
                    try:
                        sprite.draw()
                    except:
                        if sprite not in self.mcMuffinSprites:
                            self.game.blit_alpha(self.game.screen, sprite.image, self.game.camera.offset(sprite.imgRect),
                                                 sprite.alpha)

                try:
                    self.game.screen.blit(self.game.map.foreground, self.game.camera.offset(self.game.map.rect))
                except:
                    pass

                [self.game.screen.blit(fad.image, (0, 0)) for fad in self.game.fadeout]
            for sprite in self.mcMuffinSprites:
                try:
                    self.game.screen.blit(sprite.shadow, sprite.rect)
                except:
                    pass
            [self.game.blit_alpha(self.game.screen, sprite.image, sprite.imgRect, sprite.alpha) for sprite in
             self.mcMuffinSprites]
            [text.draw() for text in self.game.textboxes]
            for fx in self.game.effects:
                if fx.offset:
                    self.game.blit_alpha(self.game.screen, fx.image, self.game.camera.offset(fx.rect), fx.alpha)
                else:
                    self.game.blit_alpha(self.game.screen, fx.image, fx.rect, fx.alpha)

            pg.display.flip()

        self.game.updateOverworld()
        self.game.playtime -= 1

    def screenFlash(self):
        if self.flash is None:
            self.game.flashSound.play()
            self.flash = Flash(self.game)

        if self.flash.done:
            self.flash = None
            self.sceneEnd()

    def bleckCloneCreate(self):
        if self.timer > 0:
            self.timer -= 1
        elif self.counter < 10:
            self.timer = 10
            BleckCloneCutscene(self.game, self.bleck.rect.center, random.randrange(0, 360))
            blek = CountBleckClone()
            blek.init(self.game,
                      (random.randrange(0, self.game.map.width), random.randrange(0, self.game.map.height)))
            self.counter += 1
        else:
            self.counter = 0
            self.sceneEnd()

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

        if self.currentScene >= len(self.scenes):
            self.over = True

    def playMovie(self, movie):
        pg.event.clear()
        mp4 = VideoFileClip("movies/" + movie + ".mp4")
        if self.game.fullscreen:
            mp4.preview(fps=30, fullscreen=True)
        else:
            mp4.preview(fps=30)
        self.sceneEnd()

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

    def undertaleTextBox(self, target, text, type="dialogue", head=None, sound="default", complete=False, font="default", speed=1, id=0):
        if self.textbox[id] is None:
            self.textbox[id] = UndertaleTextBox(self.game, target, text, type, head, sound, complete, font, speed)
        elif self.textbox[id].complete:
            self.textbox[id] = None
            target.talking = False
            self.sceneEnd()
        else:
            if self.textbox[id].talking:
                target.talking = True
            else:
                target.talking = False

    def flipIn(self, image, pos, turns=2, sound="default", id=0):
        if self.flip[id] is None:
            self.flip[id] = LineFlipAppear(self.game, image, pos, turns, sound)
        elif self.flip[id].complete:
            self.flip[id] = None
            self.sceneEnd()

    def flipOut(self, image, pos=(0, 0), turns=3, sound="default", id=0, rectCenter=False):
        if self.flip[id] is None:
            if rectCenter:
                self.flip[id] = LineFlipDisappear(self.game, image, pos, turns, sound)
            else:
                self.flip[id] = LineFlipDisappear(self.game, image, pos, turns, sound)
        elif self.flip[id].complete:
            self.flip[id] = None
            self.sceneEnd()

    def move(self, obj, x, y, relative, spd, id=0):
        if self.xDest[id] == -69:
            if not relative:
                self.xDest[id] = x
                self.yDest[id] = y
            else:
                self.xDest[id] = obj.rect.centerx + x
                self.yDest[id] = obj.rect.centery + y
            if spd != 0:
                for i in range(spd):
                    self.points[id].append(
                        pt.getPointOnLine(obj.rect.centerx, obj.rect.centery, self.xDest[id], self.yDest[id],
                                          (i / spd)))
            else:
                obj.rect.center = (self.xDest[id], self.yDest[id])

        if self.pointCounter[id] < len(self.points[id]):
            obj.rect.center = self.points[id][self.pointCounter[id]]
            self.pointCounter[id] += 1
        else:
            obj.rect.center = (self.xDest[id], self.yDest[id])
            self.pointCounter[id] = 0
            self.points[id] = []
            self.xDest[id] = -69
            self.yDest[id] = -69
            self.sceneEnd()

    def changeSong(self, song, prevCont=False, cont=False):
        if prevCont:
            self.game.currentPoint += pg.mixer.music.get_pos()
        self.song = song
        self.contSong = cont
        self.sceneEnd()

    def mcMuffinGet(self, endChapter=True):
        if self.game.mario not in self.mcMuffinSprites:
            self.timer = 0
            self.game.mario.spinning = True
            self.game.luigi.spinning = True
            self.fade = None
            self.mcMuffinSprites.append(self.game.mario)
            self.mcMuffinSprites.append(self.game.luigi)
            self.mcMuffinSprites.append(self.game.mcMuffin)
            self.room = self.game.room
            self.game.room = "mcMuffin Get"
            self.prevCenters = [self.game.mario.rect.center, self.game.luigi.rect.center, self.game.mcMuffin.rect.center]
            self.game.mario.rect.center = self.game.camera.offset(self.game.mario.rect).center
            self.game.luigi.rect.center = self.game.camera.offset(self.game.luigi.rect).center
            self.game.mcMuffin.rect.center = self.game.camera.offset(self.game.mcMuffin.rect).center
            self.move(self.game.mcMuffin, width / 2, (height / 2) + 80, False, round(fps * 6.1), 2)
            self.move(self.game.mario, 460, 250, False, round(fps * 6.1), 0)
            self.move(self.game.luigi, 780, 250, False, round(fps * 6.1), 1)
            Fadeout(self.game, 1)
        if self.game.songPlaying != "mcMuffin Get":
            try:
                self.prevSong = self.song.copy()
            except:
                pass
            self.song = [14.221, 16.601, "mcMuffin Get"]

        if self.pointCounter[0] < len(self.points[0]):
            self.game.mario.rect.center = self.points[0][self.pointCounter[0]]
            self.pointCounter[0] += 1
        if self.pointCounter[1] < len(self.points[1]):
            self.game.luigi.rect.center = self.points[1][self.pointCounter[1]]
            self.pointCounter[1] += 1
        if self.pointCounter[2] < len(self.points[2]):
            self.game.mcMuffin.rect.center = self.points[2][self.pointCounter[2]]
            self.pointCounter[2] += 1
        elif self.game.mario.spinning:
            self.game.mario.rect.center = (self.xDest[0], self.yDest[0])
            self.game.luigi.rect.center = (self.xDest[1], self.yDest[1])
            self.game.mcMuffin.rect.center = (self.xDest[2], self.yDest[2])
            self.game.mario.currentFrame = 0
            self.game.luigi.currentFrame = 0
            self.game.mario.spinning = False
            self.game.mario.pose = True
            self.game.mario.currentFrame = 0
            self.game.luigi.spinning = False
            self.game.luigi.pose = True
            self.game.luigi.currentFrame = 0

        if self.game.mario.pose:
            self.timer += 1
            if self.timer == fps * 2:
                self.mcMuffinText = McMuffinText(self.game)
                self.mcMuffinSprites.append(self.mcMuffinText)
                self.game.cutsceneSprites.append(self.mcMuffinText)
            for event in self.game.event:
                if event.type == pg.KEYDOWN:
                    if event.key != pg.K_F4:
                        if not endChapter:
                            self.mcMuffinSprites = []
                            if self.mcMuffinText in self.game.cutsceneSprites: self.game.cutsceneSprites.remove(self.mcMuffinText)
                            self.game.mario.rect.center = self.prevCenters[0]
                            self.game.luigi.rect.center = self.prevCenters[1]
                            self.game.mcMuffin.rect.center = self.prevCenters[2]
                            self.song = self.prevSong
                            for fade in self.game.fadeout: fade.speed = 20
                            self.game.room = self.room
                            self.game.mario.pose = False
                            self.game.luigi.pose = False
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
                            self.points = [[],
                                           [],
                                           [],
                                           [],
                                           [],
                                           [],
                                           [],
                                           [],
                                           [],
                                           []]
                            self.pointCounter = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                            self.timer = 0
                            self.sceneEnd()
                        else:
                            self.fade = Fadeout(self.game, 5)
                            self.mcMuffinSprites.append(self.fade)

            if self.fade is not None:
                if self.fade.alpha >= 255:
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
                    self.points = [[],
                                   [],
                                   [],
                                   [],
                                   [],
                                   [],
                                   [],
                                   [],
                                   [],
                                   []]
                    self.pointCounter = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    self.timer = 0
                    self.game.storeData["mario pos"] = "beef"
                    self.game.storeData["luigi pos"] = "beef"
                    self.game.storeData["move"] = Q.deque()
                    self.game.currentPoint = 0
                    self.sceneEnd()


class LoadCutscene:
    def __init__(self, game, rect, delete=False, auto=False,
                 scenes=[["self.wait(2)"], ["""self.textBox(self.game.player, ["You didn't say anything!"])"""]], id=0):
        self.game = game
        self.rect = rect
        self.delete = delete
        self.auto = auto
        self.scenes = scenes.copy()
        self.game.cutscenes.append(self)
        self.room = self.game.room
        self.id = id

    def update(self):
        if self.id not in self.game.usedCutscenes:
            if self.auto:
                if self.delete:
                    self.game.usedCutscenes.append(self.id)
                Cutscene(self.game, self.scenes)
            else:
                if (self.game.leader == "mario" and pg.sprite.collide_rect(self.game.player, self)) or (
                        self.game.leader == "luigi" and pg.sprite.collide_rect(self.game.follower, self)):
                    if self.delete:
                        self.game.usedCutscenes.append(self.id)
                    Cutscene(self.game, self.scenes)
        if self.room != self.game.room:
            self.game.cutscenes.remove(self)


class CountBleckClone(StateMachine):
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
        self.fakeStats = self.game.bleck.stats.copy()
        self.stats = self.fakeStats
        self.rectHP = self.fakeStats["hp"]

        self.description = [
            "That's Count Bleck.",
            "As you know, his main goal\nis to destroy all worlds\nwith the Void.",
            "Max HP is " + str(self.fakeStats["maxHP"]) + ",/p\nAttack is " + str(
                self.fakeStats["pow"]) + ",/p\nDefence is " + str(self.fakeStats["def"]) + ".",
            "He's going to throw everything\nhe can at you.",
            "But you can beat him if you\ngive it your all!",
            "And you have to, or else\neverything we know will be\ngone..."]

    def loadImages(self):
        self.shadow = self.game.bleck.shadow

        self.hitFrame = self.game.bleck.hitFrame

        self.idleImages = self.game.bleck.idleImages

        self.laughingFrames = self.game.bleck.laughingFrames

        self.fireFrames = self.game.bleck.fireFrames

    def hpMath(self):
        if self.rectHP > self.game.bleck.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = ((self.rectHP - self.game.bleck.stats["hp"]) / 30) * -1
        elif self.rectHP < self.game.bleck.stats["hp"] and self.hpSpeed == 0:
            self.hpSpeed = (self.game.bleck.stats["hp"] - self.rectHP) / 30

        if self.hpSpeed != 0:
            if self.rectHP > self.game.bleck.stats["hp"] and self.hpSpeed < 0:
                self.rectHP += self.hpSpeed
            elif self.rectHP < self.game.bleck.stats["hp"] and self.hpSpeed > 0:
                self.rectHP += self.hpSpeed
            else:
                self.rectHP = self.game.bleck.stats["hp"]
                self.hpSpeed = 0

    def update(self):
        self.animate()
        self.hpMath()
        if self.stats["hp"] != 0:
            self.stats["hp"] = self.game.bleck.stats["hp"]

        if self.is_idle:
            chance = random.randrange(0, 100)
            if chance == 0 and self.cooldown <= 0:
                choice = random.randrange(0, 3)
                self.cooldown = fps * 10
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
            if chance == 0:
                self.giveUp()
        elif self.is_speed:
            for wall in self.game.walls:
                if self.rect.colliderect(wall.rect):
                    if self.game.leader == "mario":
                        self.angle = get_angle(self.rect.center, (
                        random.randrange(self.game.player.rect.centerx - 40, self.game.player.rect.centerx + 40),
                        (random.randrange(self.game.player.rect.centery - 40, self.game.player.rect.centery + 40))))
                    else:
                        self.angle = get_angle(self.rect.center, (
                        random.randrange(self.game.follower.rect.centerx - 40, self.game.follower.rect.centerx + 40),
                        (random.randrange(self.game.follower.rect.centery - 40, self.game.follower.rect.centery + 40))))
            self.rect.center = project(self.rect.center, self.angle, self.speed * 3)
            chance = random.randrange(0, 300)
            if chance == 11:
                for i in range(random.randrange(3, 4)):
                    ball = FawfulBullet(self.game, (random.randrange(self.rect.left - 100, self.rect.right + 100),
                                             random.randrange(self.rect.top - 100, self.rect.bottom + 100)), self.stats)
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
                            self.stats["hp"] = 0
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            if self.is_walking:
                                self.giveUp()
                            self.getHit()
                            self.cooldown = fps
                            self.game.player.airTimer = 0

            if self.game.follower.stats["hp"] != 0 and (self.is_idle or self.is_walking):
                hits = pg.sprite.collide_rect(self.game.follower, self)
                if hits:
                    hitsRound2 = pg.sprite.collide_rect(self.game.followerCol, self)
                    if hitsRound2:
                        if self.game.player.going == "down" and self.game.player.jumping and self.stats["hp"] > 0:
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                      (max(2 * (self.game.follower.stats["pow"] - self.stats["def"]), 1)))
                            self.stats["hp"] = 0
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            if self.is_walking:
                                self.giveUp()
                            self.getHit()
                            self.cooldown = fps
                            self.game.follower.airTimer = 0

            if self.stats["hp"] != 0 and self.game.player.isHammer is not None and (self.is_idle or self.is_walking):
                hammerHits = pg.sprite.collide_rect(self, self.game.player.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.playerHammer)
                    if hammerHitsRound2 and not self.is_hit and self.stats["hp"] > 0:
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 0))
                        self.stats["hp"] = 0
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        if self.is_walking:
                            self.giveUp()
                        self.getHit()
                        self.cooldown = fps

            if self.stats["hp"] != 0 and self.game.follower.isHammer is not None and (self.is_idle or self.is_walking):
                hammerHits = pg.sprite.collide_rect(self, self.game.follower.isHammer)
                if hammerHits:
                    hammerHitsRound2 = pg.sprite.collide_rect(self, self.game.followerHammer)
                    if hammerHitsRound2 and not self.is_hit and self.stats["hp"] > 0:
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 1.5), 1))
                        self.stats["hp"] = 0
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        if self.is_walking:
                            self.giveUp()
                        self.getHit()
                        self.cooldown = fps

            for entity in self.game.entities:
                if self.rect.colliderect(entity.rect) and not self.is_hit and self.stats["hp"] > 0 and (self.is_idle or self.is_walking):
                    if type(entity).__name__ == "Lightning":
                        HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                   max(round((self.game.follower.stats["pow"] - self.stats["def"]) * 2), 1))
                        self.stats["hp"] = 0
                        if self.stats["hp"] <= 0:
                            self.game.enemyDieSound.play()
                        self.game.enemyHitSound.play()
                        if self.is_walking:
                            self.giveUp()
                        self.getHit()
                        self.cooldown = fps
                    if self.imgRect.colliderect(entity.imgRect) and (self.is_idle or self.is_walking):
                        if type(entity).__name__ == "Fireball":
                            HitNumbers(self.game, self.game.room, (self.rect.centerx, self.imgRect.top),
                                       max(round((self.game.player.stats["pow"] - self.stats["def"]) * 1.5), 1))
                            self.stats["hp"] = 0
                            if self.stats["hp"] <= 0:
                                self.game.enemyDieSound.play()
                            self.game.enemyHitSound.play()
                            if self.is_walking:
                                self.giveUp()
                            self.getHit()
                            self.cooldown = fps
                            entity.dead = True

        if self.stats["hp"] <= 0:
            self.cooldown = 10000
            self.alpha -= 10

        if self.alpha <= 0:
            self.game.sprites.remove(self)
            self.game.enemies.remove(self)
            blek = CountBleckClone()
            blek.init(self.game, (random.randrange(0, self.game.map.width), random.randrange(0, self.game.map.height)))
        elif self.game.bleck not in self.game.enemies:
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
                    for i in range(random.randrange(1, 2)):
                        FawfulBullet(self.game, (random.randrange(self.rect.left - 100, self.rect.right + 100), random.randrange(self.rect.top - 100, self.rect.bottom + 100)), self.stats)
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
            else:
                self.cooldown -= 1


class FawfulBullet(pg.sprite.Sprite):
    def __init__(self, game, pos, stats):
        self.game = game
        self.game.sprites.append(self)
        sheet = spritesheet("sprites/dark fawful.png", "sprites/dark fawful.xml")
        self.image = sheet.getImageName("ball.png")
        self.imgRect = self.image.get_rect()
        self.shadow = sheet.getImageName("ballShadow.png")
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.imgRect.centerx, self.imgRect.bottom = self.rect.centerx, self.rect.bottom - 10
        self.alpha = 255
        self.speed = 4.9
        self.counter = fps * 3
        self.dead = False
        self.stats = stats
        if self.game.leader == "mario":
            self.angle = get_angle(self.rect.center, self.game.player.rect.center)
        else:
            self.angle = get_angle(self.rect.center, self.game.follower.rect.center)

    def update(self):
        self.counter -= 1

        if self.counter > 0:
            if self.game.leader == "mario":
                self.angle = get_angle(self.rect.center, self.game.player.rect.center)
            else:
                self.angle = get_angle(self.rect.center, self.game.follower.rect.center)

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


class SansOverworld(pg.sprite.Sprite):
    def __init__(self, game, x):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("sprites/sansOverworld.png").convert_alpha()
        self.shadow = pg.image.load("sprites/sansShadow.png").convert_alpha()
        self.rect = self.shadow.get_rect()
        self.imgRect = self.image.get_rect()
        self.rect.centerx = x
        if game.leader == "mario":
            self.rect.centery = game.player.rect.centery
        else:
            self.rect.centery = game.follower.rect.centery
        self.imgRect.bottom = self.rect.bottom - 3
        self.imgRect.centerx = self.rect.centerx
        self.game = game
        self.game.cutsceneSprites.append(self)
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
        self.spinning = False
        self.pose = False
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
        elif self.pose:
            if now - self.lastUpdate > 45:
                if self.currentFrame < len(self.poseFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                    center = self.imgRect.center
                    self.image = self.poseFrames[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
        elif self.spinning:
            if now - self.lastUpdate > 45:
                self.lastUpdate = now
                if self.currentFrame < len(self.spinningFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.spinningFrames))
                else:
                    self.currentFrame = 0
                center = self.imgRect.center
                self.image = self.spinningFrames[self.currentFrame]
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

        if self.walking and (
                self.currentFrame == 0 or self.currentFrame == 6) and now == self.lastUpdate:
            self.game.player.stepSound.stop()
            pg.mixer.Sound.play(self.game.player.stepSound)
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
        self.spinning = False
        self.pose = False
        self.facing = self.game.follower.facing

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
        elif self.pose:
            if now - self.lastUpdate > 45:
                if self.currentFrame < len(self.poseFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                    center = self.imgRect.center
                    self.image = self.poseFrames[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
        elif self.spinning:
            if now - self.lastUpdate > 45:
                self.lastUpdate = now
                if self.currentFrame < len(self.spinningFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.spinningFrames))
                else:
                    self.currentFrame = 0
                center = self.imgRect.center
                self.image = self.spinningFrames[self.currentFrame]
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

        if self.walking and (
                self.currentFrame == 0 or self.currentFrame == 6) and now == self.lastUpdate:
            self.game.follower.stepSound.stop()
            pg.mixer.Sound.play(self.game.follower.stepSound)
        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx


class starlowCutscene(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.cutsceneSprites.append(self)
        self.loadImages()
        self.image = self.idleFramesDown[0]
        self.shadow = self.shadow
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
        if self.game.area == "Castle Bleck":
            self.shadow.fill(gray, special_flags=pg.BLEND_ADD)

    def loadImages(self):
        sheet = spritesheet("sprites/starlow.png", "sprites/starlow.xml")

        self.idleFramesDownRight = [sheet.getImageName("starlow_downright_1.png"),
                                    sheet.getImageName("starlow_downright_2.png"),
                                    sheet.getImageName("starlow_downright_3.png"),
                                    sheet.getImageName("starlow_downright_4.png"),
                                    sheet.getImageName("starlow_downright_5.png"),
                                    sheet.getImageName("starlow_downright_6.png")]

        self.idleFramesDownLeft = [sheet.getImageName("starlow_downleft_1.png"),
                                    sheet.getImageName("starlow_downleft_2.png"),
                                    sheet.getImageName("starlow_downleft_3.png"),
                                    sheet.getImageName("starlow_downleft_4.png"),
                                    sheet.getImageName("starlow_downleft_5.png"),
                                    sheet.getImageName("starlow_downleft_6.png")]

        self.idleFramesRight = [sheet.getImageName("starlow_right_1.png"),
                                sheet.getImageName("starlow_right_2.png"),
                                sheet.getImageName("starlow_right_3.png"),
                                sheet.getImageName("starlow_right_4.png"),
                                sheet.getImageName("starlow_right_5.png"),
                                sheet.getImageName("starlow_right_6.png")]

        self.idleFramesUp = [sheet.getImageName("starlow_up_1.png"),
                                sheet.getImageName("starlow_up_2.png"),
                                sheet.getImageName("starlow_up_3.png"),
                                sheet.getImageName("starlow_up_4.png"),
                                sheet.getImageName("starlow_up_5.png"),
                                sheet.getImageName("starlow_up_6.png")]

        self.idleFramesDown = [sheet.getImageName("starlow_down_1.png"),
                                sheet.getImageName("starlow_down_2.png"),
                                sheet.getImageName("starlow_down_3.png"),
                                sheet.getImageName("starlow_down_4.png"),
                                sheet.getImageName("starlow_down_5.png"),
                                sheet.getImageName("starlow_down_6.png")]

        self.idleFramesLeft = [sheet.getImageName("starlow_left_1.png"),
                                sheet.getImageName("starlow_left_2.png"),
                                sheet.getImageName("starlow_left_3.png"),
                                sheet.getImageName("starlow_left_4.png"),
                                sheet.getImageName("starlow_left_5.png"),
                                sheet.getImageName("starlow_left_6.png")]

        self.idleFramesUpRight = [sheet.getImageName("starlow_upright_1.png"),
                                  sheet.getImageName("starlow_upright_2.png"),
                                  sheet.getImageName("starlow_upright_3.png"),
                                  sheet.getImageName("starlow_upright_4.png"),
                                  sheet.getImageName("starlow_upright_5.png"),
                                  sheet.getImageName("starlow_upright_6.png")]

        self.idleFramesUpLeft = [sheet.getImageName("starlow_upleft_1.png"),
                                  sheet.getImageName("starlow_upleft_2.png"),
                                  sheet.getImageName("starlow_upleft_3.png"),
                                  sheet.getImageName("starlow_upleft_4.png"),
                                  sheet.getImageName("starlow_upleft_5.png"),
                                  sheet.getImageName("starlow_upleft_6.png")]

        self.talkingFramesUp = [sheet.getImageName("starlow_talking_up_1.png"),
                                   sheet.getImageName("starlow_talking_up_2.png"),
                                   sheet.getImageName("starlow_talking_up_3.png"),
                                   sheet.getImageName("starlow_talking_up_4.png"),
                                   sheet.getImageName("starlow_talking_up_5.png"),
                                   sheet.getImageName("starlow_talking_up_6.png"),
                                   sheet.getImageName("starlow_talking_up_7.png"),
                                   sheet.getImageName("starlow_talking_up_8.png")]

        self.talkingFramesDown = [sheet.getImageName("starlow_talking_down_1.png"),
                                   sheet.getImageName("starlow_talking_down_2.png"),
                                   sheet.getImageName("starlow_talking_down_3.png"),
                                   sheet.getImageName("starlow_talking_down_4.png"),
                                   sheet.getImageName("starlow_talking_down_5.png"),
                                   sheet.getImageName("starlow_talking_down_6.png"),
                                   sheet.getImageName("starlow_talking_down_7.png"),
                                   sheet.getImageName("starlow_talking_down_8.png")]

        self.talkingFramesLeft = [sheet.getImageName("starlow_talking_left_1.png"),
                                   sheet.getImageName("starlow_talking_left_2.png"),
                                   sheet.getImageName("starlow_talking_left_3.png"),
                                   sheet.getImageName("starlow_talking_left_4.png"),
                                   sheet.getImageName("starlow_talking_left_5.png"),
                                   sheet.getImageName("starlow_talking_left_6.png"),
                                   sheet.getImageName("starlow_talking_left_7.png"),
                                   sheet.getImageName("starlow_talking_left_8.png")]

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

        self.talkingFramesUpLeft = [sheet.getImageName("starlow_talking_upleft_1.png"),
                                     sheet.getImageName("starlow_talking_upleft_2.png"),
                                     sheet.getImageName("starlow_talking_upleft_3.png"),
                                     sheet.getImageName("starlow_talking_upleft_4.png"),
                                     sheet.getImageName("starlow_talking_upleft_5.png"),
                                     sheet.getImageName("starlow_talking_upleft_6.png"),
                                     sheet.getImageName("starlow_talking_upleft_7.png"),
                                     sheet.getImageName("starlow_talking_upleft_8.png")]

        self.talkingFramesDownRight = [sheet.getImageName("starlow_talking_downright_1.png"),
                                     sheet.getImageName("starlow_talking_downright_2.png"),
                                     sheet.getImageName("starlow_talking_downright_3.png"),
                                     sheet.getImageName("starlow_talking_downright_4.png"),
                                     sheet.getImageName("starlow_talking_downright_5.png"),
                                     sheet.getImageName("starlow_talking_downright_6.png"),
                                     sheet.getImageName("starlow_talking_downright_7.png"),
                                     sheet.getImageName("starlow_talking_downright_8.png")]

        self.talkingFramesDownLeft = [sheet.getImageName("starlow_talking_downleft_1.png"),
                                    sheet.getImageName("starlow_talking_downleft_2.png"),
                                    sheet.getImageName("starlow_talking_downleft_3.png"),
                                    sheet.getImageName("starlow_talking_downleft_4.png"),
                                    sheet.getImageName("starlow_talking_downleft_5.png"),
                                    sheet.getImageName("starlow_talking_downleft_6.png"),
                                    sheet.getImageName("starlow_talking_downleft_7.png"),
                                    sheet.getImageName("starlow_talking_downleft_8.png")]

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
            elif self.facing == "upleft":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesUpLeft):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesUpLeft))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.talkingFramesUpLeft[self.currentFrame]
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
            elif self.facing == "up":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesUp):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesUp))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.talkingFramesUp[self.currentFrame]
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
            elif self.facing == "left":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesLeft):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesLeft))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.talkingFramesLeft[self.currentFrame]
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
            elif self.facing == "upleft":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.idleFramesUpLeft):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.idleFramesUpLeft))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.idleFramesUpLeft[self.currentFrame]
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
            elif self.facing == "downleft":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.idleFramesDownLeft):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.idleFramesDownLeft))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.idleFramesDownLeft[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "up":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.idleFramesUp):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.idleFramesUp))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.idleFramesUp[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "down":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.idleFramesDown):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.idleFramesDown))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.idleFramesDown[self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.center = center
            elif self.facing == "left":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.idleFramesLeft):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.idleFramesLeft))
                    else:
                        self.currentFrame = 0
                    center = self.imgRect.center
                    self.image = self.idleFramesLeft[self.currentFrame]
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
        self.imgRect.centery = self.rect.top - 75
        self.imgRect.centerx = self.rect.centerx


class toadleyCutscene(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.cutsceneSprites.append(self)
        self.loadImages()
        self.image = self.idleFrames["down"]
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

        self.shadow = sheet.getImageName("shadow.png")

        self.idleFrames = {"up": sheet.getImageName("standing_up.png"),
                           "down": sheet.getImageName("standing_down.png"),
                           "left": sheet.getImageName("standing_left.png"),
                           "right": sheet.getImageName("standing_right.png"),
                           "upleft": sheet.getImageName("standing_upleft.png"),
                           "upright": sheet.getImageName("standing_upright.png"),
                           "downleft": sheet.getImageName("standing_downleft.png"),
                           "downright": sheet.getImageName("standing_downright.png")
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
                                        sheet.getImageName("talking_right_6.png")],
                              "upleft": [sheet.getImageName("talking_upleft_1.png"),
                                     sheet.getImageName("talking_upleft_2.png"),
                                     sheet.getImageName("talking_upleft_3.png"),
                                     sheet.getImageName("talking_upleft_4.png"),
                                     sheet.getImageName("talking_upleft_5.png"),
                                     sheet.getImageName("talking_upleft_6.png")],
                              "downleft": [sheet.getImageName("talking_downleft_1.png"),
                                       sheet.getImageName("talking_downleft_2.png"),
                                       sheet.getImageName("talking_downleft_3.png"),
                                       sheet.getImageName("talking_downleft_4.png"),
                                       sheet.getImageName("talking_downleft_5.png"),
                                       sheet.getImageName("talking_downleft_6.png")],
                              "upright": [sheet.getImageName("talking_upright_1.png"),
                                     sheet.getImageName("talking_upright_2.png"),
                                     sheet.getImageName("talking_upright_3.png"),
                                     sheet.getImageName("talking_upright_4.png"),
                                     sheet.getImageName("talking_upright_5.png"),
                                     sheet.getImageName("talking_upright_6.png")],
                              "downright": [sheet.getImageName("talking_downright_1.png"),
                                       sheet.getImageName("talking_downright_2.png"),
                                       sheet.getImageName("talking_downright_3.png"),
                                       sheet.getImageName("talking_downright_4.png"),
                                       sheet.getImageName("talking_downright_5.png"),
                                       sheet.getImageName("talking_downright_6.png")],
                              }

    def update(self):
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
            elif self.facing == "upleft":
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                self.image = self.idleFrames["upleft"]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
            elif self.facing == "upright":
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                self.image = self.idleFrames["upright"]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
            elif self.facing == "downleft":
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                self.image = self.idleFrames["downleft"]
                self.imgRect = self.image.get_rect()
                self.imgRect.centerx = centerx
                self.imgRect.bottom = bottom
            elif self.facing == "downright":
                centerx = self.imgRect.centerx
                bottom = self.imgRect.bottom
                self.image = self.idleFrames["downright"]
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
            elif self.facing == "upleft":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFrames["upleft"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFrames["upleft"]))
                    else:
                        self.currentFrame = 0
                    bottom = self.imgRect.bottom
                    centerx = self.imgRect.centerx
                    self.image = self.talkingFrames["upleft"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.centerx = centerx
            elif self.facing == "upright":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFrames["upright"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFrames["upright"]))
                    else:
                        self.currentFrame = 0
                    bottom = self.imgRect.bottom
                    centerx = self.imgRect.centerx
                    self.image = self.talkingFrames["upright"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.centerx = centerx
            elif self.facing == "downleft":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFrames["downleft"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFrames["downleft"]))
                    else:
                        self.currentFrame = 0
                    bottom = self.imgRect.bottom
                    centerx = self.imgRect.centerx
                    self.image = self.talkingFrames["downleft"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.centerx = centerx
            elif self.facing == "downright":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFrames["downright"]):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFrames["downright"]))
                    else:
                        self.currentFrame = 0
                    bottom = self.imgRect.bottom
                    centerx = self.imgRect.centerx
                    self.image = self.talkingFrames["downright"][self.currentFrame]
                    self.imgRect = self.image.get_rect()
                    self.imgRect.bottom = bottom
                    self.imgRect.centerx = centerx

        self.imgRect.bottom = self.rect.bottom - 5
        self.imgRect.centerx = self.rect.centerx


class BleckCutscene(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.cutsceneSprites.append(self)
        self.loadImages()
        self.image = self.idleFrames[0]
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.imgRect = self.image.get_rect()
        self.imgRect.bottom = self.rect.top - 50
        self.imgRect.centerx = self.rect.centerx
        self.lastUpdate = 0
        self.currentFrame = 0
        self.alpha = 255
        self.laughing = False
        self.talking = False
        if self.game.area == "Castle Bleck":
            self.shadow.fill(gray, special_flags=pg.BLEND_ADD)

    def loadImages(self):
        sheet = spritesheet("sprites/count bleck.png", "sprites/count bleck.xml")

        self.idleFrames = [sheet.getImageName("idle_1.png"),
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

        self.talkingFrames = [sheet.getImageName("talking_1.png"),
                        sheet.getImageName("talking_2.png"),
                        sheet.getImageName("talking_3.png"),
                        sheet.getImageName("talking_4.png"),
                        sheet.getImageName("talking_5.png"),
                        sheet.getImageName("talking_6.png")]

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

        self.shadow = sheet.getImageName("shadow.png")

    def update(self):
        now = pg.time.get_ticks()
        if self.laughing:
            if now - self.lastUpdate > 30:
                self.lastUpdate = now
                if self.currentFrame < len(self.laughingFrames) - 1:
                    self.currentFrame += 1
                else:
                    self.currentFrame = 6
                bottom = self.imgRect.bottom
                left = self.imgRect.left
                self.image = self.laughingFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.bottom = bottom
                self.imgRect.left = left
        elif self.talking:
            if now - self.lastUpdate > 30:
                self.lastUpdate = now
                if self.currentFrame < len(self.talkingFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFrames))
                else:
                    self.currentFrame = 0
                bottom = self.imgRect.bottom
                left = self.imgRect.left
                self.image = self.talkingFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.bottom = bottom
                self.imgRect.left = left
        else:
            if now - self.lastUpdate > 30:
                self.lastUpdate = now
                if self.currentFrame < len(self.idleFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.idleFrames))
                else:
                    self.currentFrame = 0
                bottom = self.imgRect.bottom
                left = self.imgRect.left
                self.image = self.idleFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.bottom = bottom
                self.imgRect.left = left

        if not self.laughing:
            self.imgRect.bottom = self.rect.top - 50
            self.imgRect.left = self.rect.left - 16
        else:
            self.imgRect.bottom = self.rect.top - 50
            self.imgRect.centerx = self.rect.centerx - 20


class BleckCloneCutscene(pg.sprite.Sprite):
    def __init__(self, game, pos, angle):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.angle = angle
        self.game.cutsceneSprites.append(self)
        self.loadImages()
        self.image = self.laughingFrames[0]
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.imgRect = self.image.get_rect()
        self.imgRect.bottom = self.rect.top - 50
        self.imgRect.centerx = self.rect.centerx
        self.lastUpdate = 0
        self.currentFrame = 0
        self.alpha = 255
        self.speed = 20
        self.laughing = True
        self.talking = False

    def loadImages(self):
        self.laughingFrames = self.game.bleck.laughingFrames

        self.shadow = self.game.bleck.shadow

    def update(self):
        now = pg.time.get_ticks()
        if self.laughing:
            if now - self.lastUpdate > 30:
                self.lastUpdate = now
                if self.currentFrame < len(self.laughingFrames) - 1:
                    self.currentFrame += 1
                else:
                    self.currentFrame = 6
                bottom = self.imgRect.bottom
                left = self.imgRect.left
                self.image = self.laughingFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.bottom = bottom
                self.imgRect.left = left

        if not self.laughing:
            self.imgRect.bottom = self.rect.top - 50
            self.imgRect.left = self.rect.left - 16
        else:
            self.imgRect.bottom = self.rect.top - 50
            self.imgRect.centerx = self.rect.centerx - 20

        self.rect.center = project(self.rect.center, self.angle, self.speed)


class FawfulOnCopter(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.cutsceneSprites.append(self)
        self.loadImages()
        self.image = self.game.player.image
        self.fawful = self.game.player.image
        self.copter = self.game.player.image
        self.fRect = self.fawful.get_rect()
        self.cRect = self.copter.get_rect()
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.imgRect = self.image.get_rect()
        self.cRect.centerx, self.cRect.bottom = self.rect.centerx, self.rect.top - 50
        self.fRect.centerx, self.fRect.bottom = self.cRect.centerx, self.cRect.top + 27
        self.lastUpdate = 0
        self.copterLastUpdate = 0
        self.currentFrame = 0
        self.copterCurrentFrame = 0
        self.alpha = 255
        self.talking = False
        self.laughing = False
        self.facing = "down"

    def loadImages(self):
        sheet = spritesheet("sprites/fawful.png", "sprites/fawful.xml")

        self.talkingFramesUp = [sheet.getImageName("talking_up_1.png"),
                                  sheet.getImageName("talking_up_2.png"),
                                  sheet.getImageName("talking_up_3.png"),
                                  sheet.getImageName("talking_up_4.png"),
                                  sheet.getImageName("talking_up_5.png"),
                                  sheet.getImageName("talking_up_6.png"),
                                  sheet.getImageName("talking_up_7.png"),
                                  sheet.getImageName("talking_up_8.png")]

        self.talkingFramesDown = [sheet.getImageName("talking_down_1.png"),
                                  sheet.getImageName("talking_down_2.png"),
                                  sheet.getImageName("talking_down_3.png"),
                                  sheet.getImageName("talking_down_4.png"),
                                  sheet.getImageName("talking_down_5.png"),
                                  sheet.getImageName("talking_down_6.png"),
                                  sheet.getImageName("talking_down_7.png"),
                                  sheet.getImageName("talking_down_8.png")]

        self.talkingFramesLeft = [sheet.getImageName("talking_left_1.png"),
                                  sheet.getImageName("talking_left_2.png"),
                                  sheet.getImageName("talking_left_3.png"),
                                  sheet.getImageName("talking_left_4.png"),
                                  sheet.getImageName("talking_left_5.png"),
                                  sheet.getImageName("talking_left_6.png"),
                                  sheet.getImageName("talking_left_7.png"),
                                  sheet.getImageName("talking_left_8.png")]

        self.talkingFramesRight = [sheet.getImageName("talking_right_1.png"),
                                  sheet.getImageName("talking_right_2.png"),
                                  sheet.getImageName("talking_right_3.png"),
                                  sheet.getImageName("talking_right_4.png"),
                                  sheet.getImageName("talking_right_5.png"),
                                  sheet.getImageName("talking_right_6.png"),
                                  sheet.getImageName("talking_right_7.png"),
                                  sheet.getImageName("talking_right_8.png")]

        self.talkingFramesUpLeft = [sheet.getImageName("talking_upleft_1.png"),
                                  sheet.getImageName("talking_upleft_2.png"),
                                  sheet.getImageName("talking_upleft_3.png"),
                                  sheet.getImageName("talking_upleft_4.png"),
                                  sheet.getImageName("talking_upleft_5.png"),
                                  sheet.getImageName("talking_upleft_6.png"),
                                  sheet.getImageName("talking_upleft_7.png"),
                                  sheet.getImageName("talking_upleft_8.png")]

        self.talkingFramesDownLeft = [sheet.getImageName("talking_downleft_1.png"),
                                      sheet.getImageName("talking_downleft_2.png"),
                                      sheet.getImageName("talking_downleft_3.png"),
                                      sheet.getImageName("talking_downleft_4.png"),
                                      sheet.getImageName("talking_downleft_5.png"),
                                      sheet.getImageName("talking_downleft_6.png"),
                                      sheet.getImageName("talking_downleft_7.png"),
                                      sheet.getImageName("talking_downleft_8.png")]

        self.talkingFramesUpRight = [sheet.getImageName("talking_upright_1.png"),
                                    sheet.getImageName("talking_upright_2.png"),
                                    sheet.getImageName("talking_upright_3.png"),
                                    sheet.getImageName("talking_upright_4.png"),
                                    sheet.getImageName("talking_upright_5.png"),
                                    sheet.getImageName("talking_upright_6.png"),
                                    sheet.getImageName("talking_upright_7.png"),
                                    sheet.getImageName("talking_upright_8.png")]

        self.talkingFramesDownRight = [sheet.getImageName("talking_downright_1.png"),
                                      sheet.getImageName("talking_downright_2.png"),
                                      sheet.getImageName("talking_downright_3.png"),
                                      sheet.getImageName("talking_downright_4.png"),
                                      sheet.getImageName("talking_downright_5.png"),
                                      sheet.getImageName("talking_downright_6.png"),
                                      sheet.getImageName("talking_downright_7.png"),
                                      sheet.getImageName("talking_downright_8.png")]

        self.laughingFramesUp = [sheet.getImageName("laughing_up_1.png"),
                                 sheet.getImageName("laughing_up_2.png"),
                                 sheet.getImageName("laughing_up_3.png"),
                                 sheet.getImageName("laughing_up_4.png")]

        self.laughingFramesDown = [sheet.getImageName("laughing_down_1.png"),
                                   sheet.getImageName("laughing_down_2.png"),
                                   sheet.getImageName("laughing_down_3.png"),
                                   sheet.getImageName("laughing_down_4.png")]

        self.laughingFramesLeft = [sheet.getImageName("laughing_left_1.png"),
                                   sheet.getImageName("laughing_left_2.png"),
                                   sheet.getImageName("laughing_left_3.png"),
                                   sheet.getImageName("laughing_left_4.png")]

        self.laughingFramesRight = [sheet.getImageName("laughing_right_1.png"),
                                    sheet.getImageName("laughing_right_2.png"),
                                    sheet.getImageName("laughing_right_3.png"),
                                    sheet.getImageName("laughing_right_4.png")]

        self.platformFrames = [sheet.getImageName("platform_1.png"),
                            sheet.getImageName("platform_2.png"),
                            sheet.getImageName("platform_3.png"),
                            sheet.getImageName("platform_4.png")]

        self.idleFrameUp = sheet.getImageName("standing_up.png")

        self.idleFrameDown = sheet.getImageName("standing_down.png")

        self.idleFrameLeft = sheet.getImageName("standing_left.png")

        self.idleFrameRight = sheet.getImageName("standing_right.png")

        self.idleFrameDownLeft = sheet.getImageName("standing_downleft.png")

        self.idleFrameUpLeft = sheet.getImageName("standing_upleft.png")

        self.idleFrameDownRight = sheet.getImageName("standing_downright.png")

        self.idleFrameUpRight = sheet.getImageName("standing_upright.png")

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
                    bottom = self.fRect.bottom
                    centerx = self.fRect.centerx
                    self.fawful = self.talkingFramesUpRight[self.currentFrame]
                    self.fRect = self.fawful.get_rect()
                    self.fRect.bottom = bottom
                    self.fRect.centerx = centerx
            elif self.facing == "upleft":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesUpLeft):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesUpLeft))
                    else:
                        self.currentFrame = 0
                    bottom = self.fRect.bottom
                    centerx = self.fRect.centerx
                    self.fawful = self.talkingFramesUpLeft[self.currentFrame]
                    self.fRect = self.fawful.get_rect()
                    self.fRect.bottom = bottom
                    self.fRect.centerx = centerx
            elif self.facing == "downright":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesDownRight):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesDownRight))
                    else:
                        self.currentFrame = 0
                    bottom = self.fRect.bottom
                    centerx = self.fRect.centerx
                    self.fawful = self.talkingFramesDownRight[self.currentFrame]
                    self.fRect = self.fawful.get_rect()
                    self.fRect.bottom = bottom
                    self.fRect.centerx = centerx
            elif self.facing == "downleft":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesDownLeft):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesDownLeft))
                    else:
                        self.currentFrame = 0
                    bottom = self.fRect.bottom
                    centerx = self.fRect.centerx
                    self.fawful = self.talkingFramesDownLeft[self.currentFrame]
                    self.fRect = self.fawful.get_rect()
                    self.fRect.bottom = bottom
                    self.fRect.centerx = centerx
            elif self.facing == "up":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesUp):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesUp))
                    else:
                        self.currentFrame = 0
                    bottom = self.fRect.bottom
                    centerx = self.fRect.centerx
                    self.fawful = self.talkingFramesUp[self.currentFrame]
                    self.fRect = self.fawful.get_rect()
                    self.fRect.bottom = bottom
                    self.fRect.centerx = centerx
            elif self.facing == "down":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesDown):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesDown))
                    else:
                        self.currentFrame = 0
                    bottom = self.fRect.bottom
                    centerx = self.fRect.centerx
                    self.fawful = self.talkingFramesDown[self.currentFrame]
                    self.fRect = self.fawful.get_rect()
                    self.fRect.bottom = bottom
                    self.fRect.centerx = centerx
            elif self.facing == "left":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesLeft):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesLeft))
                    else:
                        self.currentFrame = 0
                    bottom = self.fRect.bottom
                    centerx = self.fRect.centerx
                    self.fawful = self.talkingFramesLeft[self.currentFrame]
                    self.fRect = self.fawful.get_rect()
                    self.fRect.bottom = bottom
                    self.fRect.centerx = centerx
            elif self.facing == "right":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.talkingFramesRight):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFramesRight))
                    else:
                        self.currentFrame = 0
                    bottom = self.fRect.bottom
                    centerx = self.fRect.centerx
                    self.fawful = self.talkingFramesRight[self.currentFrame]
                    self.fRect = self.fawful.get_rect()
                    self.fRect.bottom = bottom
                    self.fRect.centerx = centerx
        elif self.laughing:
            if self.facing == "up":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.laughingFramesUp):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.laughingFramesUp))
                    else:
                        self.currentFrame = 0
                    bottom = self.fRect.bottom
                    centerx = self.fRect.centerx
                    self.fawful = self.laughingFramesUp[self.currentFrame]
                    self.fRect = self.fawful.get_rect()
                    self.fRect.bottom = bottom
                    self.fRect.centerx = centerx
            elif self.facing == "down":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.laughingFramesDown):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.laughingFramesDown))
                    else:
                        self.currentFrame = 0
                    bottom = self.fRect.bottom
                    centerx = self.fRect.centerx
                    self.fawful = self.laughingFramesDown[self.currentFrame]
                    self.fRect = self.fawful.get_rect()
                    self.fRect.bottom = bottom
                    self.fRect.centerx = centerx
            elif self.facing == "left":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.laughingFramesLeft):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.laughingFramesLeft))
                    else:
                        self.currentFrame = 0
                    bottom = self.fRect.bottom
                    centerx = self.fRect.centerx
                    self.fawful = self.laughingFramesLeft[self.currentFrame]
                    self.fRect = self.fawful.get_rect()
                    self.fRect.bottom = bottom
                    self.fRect.centerx = centerx
            elif self.facing == "right":
                if now - self.lastUpdate > 100:
                    self.lastUpdate = now
                    if self.currentFrame < len(self.laughingFramesRight):
                        self.currentFrame = (self.currentFrame + 1) % (len(self.laughingFramesRight))
                    else:
                        self.currentFrame = 0
                    bottom = self.fRect.bottom
                    centerx = self.fRect.centerx
                    self.fawful = self.laughingFramesRight[self.currentFrame]
                    self.fRect = self.fawful.get_rect()
                    self.fRect.bottom = bottom
                    self.fRect.centerx = centerx
        else:
            if self.facing == "upright":
                center = self.fRect.center
                self.fawful = self.idleFrameUpRight
                self.fRect = self.fawful.get_rect()
                self.fRect.center = center
            elif self.facing == "upleft":
                center = self.fRect.center
                self.fawful = self.idleFrameUpLeft
                self.fRect = self.fawful.get_rect()
                self.fRect.center = center
            elif self.facing == "downright":
                center = self.fRect.center
                self.fawful = self.idleFrameDownRight
                self.fRect = self.fawful.get_rect()
                self.fRect.center = center
            elif self.facing == "downleft":
                center = self.fRect.center
                self.fawful = self.idleFrameDownLeft
                self.fRect = self.fawful.get_rect()
                self.fRect.center = center
            elif self.facing == "up":
                center = self.fRect.center
                self.fawful = self.idleFrameUp
                self.fRect = self.fawful.get_rect()
                self.fRect.center = center
            elif self.facing == "down":
                center = self.fRect.center
                self.fawful = self.idleFrameDown
                self.fRect = self.fawful.get_rect()
                self.fRect.center = center
            elif self.facing == "left":
                center = self.fRect.center
                self.fawful = self.idleFrameLeft
                self.fRect = self.fawful.get_rect()
                self.fRect.center = center
            elif self.facing == "right":
                center = self.fRect.center
                self.fawful = self.idleFrameRight
                self.fRect = self.fawful.get_rect()
                self.fRect.center = center

        if now - self.copterLastUpdate > 50:
            self.copterLastUpdate = now
            if self.copterCurrentFrame < len(self.platformFrames):
                self.copterCurrentFrame = (self.copterCurrentFrame + 1) % (len(self.platformFrames))
            else:
                self.copterCurrentFrame = 0
            center = self.cRect.center
            self.copter = self.platformFrames[self.copterCurrentFrame]
            self.cRect = self.copter.get_rect()
            self.cRect.center = center

        self.cRect.centerx = self.rect.centerx
        self.cRect.bottom = self.rect.top - 50
        self.fRect.centerx = self.cRect.centerx
        self.fRect.bottom = self.cRect.top + 27

        combine = CombineSprites([self.copter, self.fawful], [self.cRect, self.fRect])
        self.image = combine.image
        self.imgRect = combine.rect


class DarkFawfulCutscene(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.cutsceneSprites.append(self)
        self.loadImages()
        self.image = self.idleFrames[0]
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.imgRect = self.image.get_rect()
        self.imgRect.bottom = self.rect.top - 50
        self.imgRect.centerx = self.rect.centerx
        self.lastUpdate = 0
        self.currentFrame = 0
        self.alpha = 255
        self.talking = False

    def loadImages(self):
        sheet = spritesheet("sprites/fawful.png", "sprites/fawful.xml")

        self.idleFrames = [sheet.getImageName("dark_idle_1.png"),
                        sheet.getImageName("dark_idle_2.png"),
                        sheet.getImageName("dark_idle_3.png"),
                        sheet.getImageName("dark_idle_4.png"),
                        sheet.getImageName("dark_idle_5.png"),
                        sheet.getImageName("dark_idle_6.png"),
                        sheet.getImageName("dark_idle_7.png"),
                        sheet.getImageName("dark_idle_8.png")]

        self.talkingFrames = [sheet.getImageName("dark_talking_1.png"),
                        sheet.getImageName("dark_talking_2.png"),
                        sheet.getImageName("dark_talking_3.png"),
                        sheet.getImageName("dark_talking_4.png"),
                        sheet.getImageName("dark_talking_5.png"),
                        sheet.getImageName("dark_talking_6.png"),
                        sheet.getImageName("dark_talking_7.png"),
                        sheet.getImageName("dark_talking_8.png")]

        self.shadow = sheet.getImageName("shadow.png")

    def update(self):
        now = pg.time.get_ticks()
        if self.talking:
            if now - self.lastUpdate > 75:
                self.lastUpdate = now
                if self.currentFrame < len(self.talkingFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.talkingFrames))
                else:
                    self.currentFrame = 0
                bottom = self.imgRect.bottom
                left = self.imgRect.left
                self.image = self.talkingFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.bottom = bottom
                self.imgRect.left = left
        else:
            if now - self.lastUpdate > 75:
                self.lastUpdate = now
                if self.currentFrame < len(self.idleFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.idleFrames))
                else:
                    self.currentFrame = 0
                bottom = self.imgRect.bottom
                left = self.imgRect.left
                self.image = self.idleFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.bottom = bottom
                self.imgRect.left = left

        self.imgRect.bottom = self.rect.top - 50
        self.imgRect.centerx = self.rect.centerx


class DarkFawfulDisappear(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.cutsceneSprites.append(self)
        self.loadImages()
        self.image = self.idleFrames[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.lastUpdate = 0
        self.currentFrame = 0
        self.alpha = 255
        self.dead = False

    def loadImages(self):
        sheet = spritesheet("sprites/fawful.png", "sprites/fawful.xml")

        self.idleFrames = [sheet.getImageName("defeat_1.png"),
                        sheet.getImageName("defeat_2.png"),
                        sheet.getImageName("defeat_3.png"),
                        sheet.getImageName("defeat_4.png"),
                        sheet.getImageName("defeat_5.png"),
                        sheet.getImageName("defeat_6.png"),
                        sheet.getImageName("defeat_7.png"),
                        sheet.getImageName("defeat_8.png"),
                        sheet.getImageName("defeat_9.png"),
                        sheet.getImageName("defeat_10.png"),
                        sheet.getImageName("defeat_11.png"),
                        sheet.getImageName("defeat_12.png"),]

        self.disappearFrames = [sheet.getImageName("disappear_1.png"),
                                sheet.getImageName("disappear_2.png"),
                                sheet.getImageName("disappear_3.png"),
                                sheet.getImageName("disappear_4.png"),
                                sheet.getImageName("disappear_5.png"),
                                sheet.getImageName("disappear_6.png"),
                                sheet.getImageName("disappear_7.png"),
                                sheet.getImageName("disappear_8.png"),
                                sheet.getImageName("disappear_9.png"),
                                sheet.getImageName("disappear_10.png"),
                                sheet.getImageName("disappear_11.png"),
                                sheet.getImageName("disappear_12.png"),
                                sheet.getImageName("disappear_13.png"),
                                sheet.getImageName("disappear_14.png"),
                                sheet.getImageName("disappear_15.png"),
                                sheet.getImageName("disappear_16.png"),
                                sheet.getImageName("disappear_17.png"),
                                sheet.getImageName("disappear_18.png"),
                                sheet.getImageName("disappear_19.png"),
                                sheet.getImageName("disappear_20.png"),
                                sheet.getImageName("disappear_21.png"),
                                sheet.getImageName("disappear_22.png"),
                                sheet.getImageName("disappear_23.png"),
                                sheet.getImageName("disappear_24.png"),
                                sheet.getImageName("disappear_25.png"),
                                sheet.getImageName("disappear_26.png")]

    def update(self):
        now = pg.time.get_ticks()
        if self.dead:
            if now - self.lastUpdate > 75:
                self.lastUpdate = now
                if self.currentFrame < len(self.disappearFrames) - 1:
                    self.currentFrame = (self.currentFrame + 1)
                else:
                    self.game.cutsceneSprites.remove(self)
                center = self.rect.center
                self.image = self.disappearFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center
        else:
            if now - self.lastUpdate > 75:
                self.lastUpdate = now
                if self.currentFrame < len(self.idleFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.idleFrames))
                else:
                    self.currentFrame = 0
                bottom = self.rect.bottom
                centerx = self.rect.centerx
                self.image = self.idleFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
                self.rect.centerx = centerx

        self.imgRect = self.rect

    def draw(self):
        self.game.screen.blit(self.image, self.game.camera.offset(self.rect))


class LineFlipAppear(pg.sprite.Sprite):
    def __init__(self, game, image, pos, turns=2, sound="default"):
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
        if self.game.area != "Castle Bleck":
            self.color = black
        else:
            self.color = white
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
            pg.draw.rect(self.game.screen, self.color, self.game.camera.offset(self.rect), 3)


class LineFlipDisappear(pg.sprite.Sprite):
    def __init__(self, game, image, pos, turns=3, sound="default"):
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
        self.scale = 1
        self.turns = 0
        self.rate = 0.125
        self.counter = turns
        self.imgRect = self.image.get_rect()
        self.imgRect.center = self.maxRect.center
        self.complete = False
        if self.game.area != "Castle Bleck":
            self.color = black
        else:
            self.color = white
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
                pg.draw.rect(self.game.screen, self.color, self.game.camera.offset(self.rect), 3)


class EggMcMuffin(pg.sprite.Sprite):
    def __init__(self, pos, color, game):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load("sprites/Egg McMuffin.png").convert_alpha()
        self.shadow = pg.image.load("sprites/mcMuffin Shadow.png").convert_alpha()
        self.rect = self.shadow.get_rect()
        self.image.fill(color, special_flags=pg.BLEND_ADD)
        self.imgRect = self.image.get_rect()
        self.rect.center = pos
        self.imgRect.centerx, self.imgRect.bottom = self.rect.centerx, self.rect.top - 30
        self.alpha = 255
        self.vy = 0
        self.dy = 0.05
        if self.game.area == "Castle Bleck":
            self.shadow.fill(gray, special_flags=pg.BLEND_ADD)

    def update(self):
        self.vy += self.dy
        if self.vy > 1 or self.vy < -1:
            self.dy *= -1

        self.imgRect.bottom = self.rect.top - 30
        self.imgRect.centerx = self.rect.centerx
        self.imgRect.y += round(self.vy)


class McMuffinText(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        sheet = spritesheet("sprites/you got an egg mcmuffin.png", "sprites/you got an egg mcmuffin.xml")
        self.sprites = [sheet.getImageName("1.png"),
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
                        sheet.getImageName("30.png"),
                        sheet.getImageName("31.png"),
                        sheet.getImageName("32.png"),
                        sheet.getImageName("33.png"),
                        sheet.getImageName("34.png"),
                        sheet.getImageName("35.png"),
                        sheet.getImageName("36.png"),
                        sheet.getImageName("37.png"),
                        sheet.getImageName("38.png"),
                        sheet.getImageName("39.png"),
                        sheet.getImageName("40.png"),
                        sheet.getImageName("41.png"),
                        sheet.getImageName("42.png"),
                        sheet.getImageName("43.png"),
                        sheet.getImageName("44.png"),
                        sheet.getImageName("45.png"),
                        sheet.getImageName("46.png"),
                        sheet.getImageName("47.png"),
                        sheet.getImageName("48.png"),
                        sheet.getImageName("49.png"),
                        sheet.getImageName("50.png"),
                        sheet.getImageName("51.png"),
                        sheet.getImageName("52.png"),
                        sheet.getImageName("53.png"),
                        sheet.getImageName("54.png"),
                        sheet.getImageName("55.png"),
                        sheet.getImageName("56.png"),
                        sheet.getImageName("57.png"),
                        sheet.getImageName("58.png"),
                        sheet.getImageName("59.png"),
                        sheet.getImageName("60.png"),
                        sheet.getImageName("61.png"),
                        sheet.getImageName("62.png"),
                        sheet.getImageName("63.png"),
                        sheet.getImageName("64.png"),
                        sheet.getImageName("65.png"),
                        sheet.getImageName("66.png"),
                        sheet.getImageName("67.png"),
                        sheet.getImageName("68.png"),
                        sheet.getImageName("69.png"),
                        sheet.getImageName("70.png"),
                        sheet.getImageName("71.png"),
                        sheet.getImageName("72.png"),
                        sheet.getImageName("73.png"),
                        sheet.getImageName("74.png"),
                        sheet.getImageName("75.png"),
                        sheet.getImageName("76.png"),
                        sheet.getImageName("77.png"),
                        sheet.getImageName("78.png"),
                        sheet.getImageName("79.png"),
                        sheet.getImageName("80.png"),
                        sheet.getImageName("81.png"),
                        sheet.getImageName("82.png"),
                        sheet.getImageName("83.png"),
                        sheet.getImageName("84.png"),
                        sheet.getImageName("85.png"),
                        sheet.getImageName("86.png"),
                        sheet.getImageName("87.png"),
                        sheet.getImageName("88.png"),
                        sheet.getImageName("89.png"),
                        sheet.getImageName("90.png"),
                        sheet.getImageName("91.png"),
                        sheet.getImageName("92.png"),
                        sheet.getImageName("93.png"),
                        sheet.getImageName("94.png"),
                        sheet.getImageName("95.png"),
                        sheet.getImageName("96.png")]
        self.lastUpdate = 0
        self.currentFrame = 0
        self.xScale = 0
        self.yScale = 0
        self.alpha = 255
        self.image = self.sprites[self.currentFrame]
        self.rect = self.image.get_rect()
        self.rect.center = (width / 2, height - 200)
        self.imgRect = self.rect

    def update(self):
        now = pg.time.get_ticks()
        if self.xScale < 1:
            self.xScale += 0.1
        else:
            self.xScale = 1
        if self.yScale < 1:
            self.yScale += 0.1
        else:
            self.yScale = 1

        if now - self.lastUpdate > 30:
            self.lastUpdate = now
            if self.currentFrame < len(self.sprites):
                self.currentFrame = (self.currentFrame + 1) % (len(self.sprites))
            else:
                self.currentFrame = 0
            self.image = pg.transform.scale(self.sprites[self.currentFrame], (
            round(self.rect.width * self.xScale), (round(self.rect.height * self.yScale))))
            self.imgRect = self.image.get_rect()
            self.imgRect.center = self.rect.center


class McMuffinWarp(pg.sprite.Sprite):
    def __init__(self, game, pos, color, warpSpot, world, location, goBack=False):
        self.game = game
        pg.sprite.Sprite.__init__(self, self.game.npcs)
        self.game.sprites.append(self)
        self.image = pg.image.load("sprites/Egg McMuffin.png").convert_alpha()
        self.shadow = pg.image.load("sprites/mcMuffin Shadow.png").convert_alpha()
        self.rect = self.shadow.get_rect()
        self.type = "interact"
        self.color = color
        self.image.fill(self.color, special_flags=pg.BLEND_ADD)
        self.imgRect = self.image.get_rect()
        self.rect.center = pos
        self.imgRect.centerx, self.imgRect.bottom = self.rect.centerx, self.rect.top - 30
        self.alpha = 255
        self.vy = 0
        self.dy = 0.05
        self.warpSpot = warpSpot
        self.textbox = None
        self.options = [pg.rect.Rect(389, 390, 0, 0), pg.rect.Rect(773, 390, 0, 0)]
        self.cursor = None
        self.fade = None
        self.canTalk = True
        self.select = 0
        self.goBack = goBack
        if self.game.area == "Castle Bleck":
            self.shadow.fill(gray, special_flags=pg.BLEND_ADD)
        if not goBack:
            self.text = ["You are about to go to/nworld {}, {}.".format(world, location),
                     "/CDo you want to proceed?\n\a\n\a                 YES                        NO"]
        else:
            self.text = ["/CDo you want to return to Flipside?\n\a\n\a                 YES                        NO"]

    def update(self):
        self.vy += self.dy
        if self.vy > 1 or self.vy < -1:
            self.dy *= -1

        self.imgRect.bottom = self.rect.top - 30
        self.imgRect.centerx = self.rect.centerx
        self.imgRect.y += round(self.vy)

        keys = pg.key.get_pressed()

        if self.game.leader == "mario":
            if pg.sprite.collide_rect_ratio(1.1)(self, self.game.player) and self.textbox is None and keys[pg.K_m] and self.fade is None:
                self.textbox = TextBox(self.game, self, self.text, type="board", dir="None", choice=True)
        elif self.game.leader == "luigi":
            if pg.sprite.collide_rect_ratio(1.1)(self, self.game.follower) and self.textbox is None and keys[pg.K_l] and self.fade is None:
                self.textbox = TextBox(self.game, self, self.text, type="board", dir="None", choice=True)

        if self.fade is not None:
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
            eval(self.warpSpot)

        if self.textbox == "complete":
            self.textbox = None
            self.cursor = None
            if self.select == 0:
                Cutscene(self.game,
                             [["self.setVar('self.game.mario = marioCutscene(self.game, self.game.player.rect.center)')",
                                  "self.setVar('self.game.luigi = luigiCutscene(self.game, self.game.follower.rect.center)')",
                               "self.setVar('self.game.muff = EggMcMuffin(self.parent.rect.center, self.parent.color, self.game)')", "self.command('self.game.cutsceneSprites.append(self.game.muff)')",],
                              ["self.wait(0.2)"],
                              [
                                  "self.flipOut([[self.game.mario.shadow, self.game.mario.image], [self.game.mario.rect, self.game.mario.imgRect]], (self.game.mario.imgRect.centerx, self.game.mario.imgRect.centery + 2))",
                                  "self.command('self.game.cutsceneSprites.remove(self.game.mario)')"],
                              [
                                  "self.flipOut([[self.game.luigi.shadow, self.game.luigi.image], [self.game.luigi.rect, self.game.luigi.imgRect]], (self.game.luigi.imgRect.centerx, self.game.luigi.imgRect.centery + 2))",
                                  "self.command('self.game.cutsceneSprites.remove(self.game.luigi)')"],
                              [
                                  "self.flipOut([[self.game.muff.shadow, self.game.muff.image], [self.game.muff.rect, self.game.muff.imgRect]], (self.game.muff.rect.centerx, self.game.muff.rect.top - 39))",
                                  "self.command('self.game.cutsceneSprites.remove(self.game.muff)')"],
                              ["self.command('Fadeout(self.game, 5)')",
                               "self.command('self.game.player.loadImages()')",
                               "self.command('self.game.follower.loadImages()')"],
                              ["self.wait(3)"]
                              ], parent=self)
                self.fade = 5

        if self.textbox is not None:
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


class mammoshkaOverworld(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self.game = game
        pg.sprite.Sprite.__init__(self)
        self.game.cutsceneSprites.append(self)
        self.loadImages()
        self.image = self.idleFrames[0]
        self.rect = self.shadow.get_rect()
        self.rect.center = pos
        self.imgRect = self.image.get_rect()
        self.imgRect.bottom = self.rect.bottom - 15
        self.imgRect.centerx = self.rect.centerx
        self.lastUpdate = 0
        self.currentFrame = 0
        self.roar = False
        self.done = False
        self.alpha = 255

    def loadImages(self):
        sheet = spritesheet("sprites/mammoshka overworld.png", "sprites/mammoshka overworld.xml")

        self.idleFrames = [sheet.getImageName("angry_1.png"),
                           sheet.getImageName("angry_2.png"),
                           sheet.getImageName("angry_3.png"),
                           sheet.getImageName("angry_4.png"),
                           sheet.getImageName("angry_5.png"),
                           sheet.getImageName("angry_6.png"),
                           sheet.getImageName("angry_7.png"),
                           sheet.getImageName("angry_8.png"),
                           sheet.getImageName("angry_9.png"),
                           sheet.getImageName("angry_10.png")]

        self.roarFrames = [sheet.getImageName("roar_1.png"),
                           sheet.getImageName("roar_2.png"),
                           sheet.getImageName("roar_3.png"),
                           sheet.getImageName("roar_4.png"),
                           sheet.getImageName("roar_5.png"),
                           sheet.getImageName("roar_6.png"),
                           sheet.getImageName("roar_7.png"),
                           sheet.getImageName("roar_8.png"),
                           sheet.getImageName("roar_9.png"),
                           sheet.getImageName("roar_10.png"),
                           sheet.getImageName("roar_11.png"),
                           sheet.getImageName("roar_12.png"),
                           sheet.getImageName("roar_13.png"),
                           sheet.getImageName("roar_14.png"),
                           sheet.getImageName("roar_15.png"),
                           sheet.getImageName("roar_16.png"),
                           sheet.getImageName("roar_17.png"),
                           sheet.getImageName("roar_18.png"),
                           sheet.getImageName("roar_19.png"),
                           sheet.getImageName("roar_20.png"),
                           sheet.getImageName("roar_21.png"),
                           sheet.getImageName("roar_22.png"),
                           sheet.getImageName("roar_23.png"),
                           sheet.getImageName("roar_24.png"),
                           sheet.getImageName("roar_25.png"),
                           sheet.getImageName("roar_26.png"),
                           sheet.getImageName("roar_27.png"),
                           sheet.getImageName("roar_28.png"),
                           sheet.getImageName("roar_29.png"),
                           sheet.getImageName("roar_30.png"),
                           sheet.getImageName("roar_31.png"),
                           sheet.getImageName("roar_32.png"),
                           sheet.getImageName("roar_33.png"),
                           sheet.getImageName("roar_34.png"),
                           sheet.getImageName("roar_35.png"),
                           sheet.getImageName("roar_36.png"),
                           sheet.getImageName("roar_37.png"),
                           sheet.getImageName("roar_38.png"),
                           sheet.getImageName("roar_39.png")]

        self.shadow = sheet.getImageName("shadow.png")

    def update(self):
        now = pg.time.get_ticks()
        if not self.roar:
            if now - self.lastUpdate > 50:
                self.lastUpdate = now
                if self.currentFrame < len(self.idleFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.idleFrames))
                else:
                    self.currentFrame = 0
                center = self.imgRect.center
                self.image = self.idleFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center
        else:
            if now - self.lastUpdate > 50:
                self.lastUpdate = now
                if self.currentFrame < len(self.roarFrames) - 1:
                    self.currentFrame = self.currentFrame + 1
                else:
                    self.currentFrame = len(self.roarFrames) - 1
                    self.done = True
                center = self.imgRect.center
                self.image = self.roarFrames[self.currentFrame]
                self.imgRect = self.image.get_rect()
                self.imgRect.center = center

        self.imgRect.bottom = self.rect.bottom - 15
        self.imgRect.centerx = self.rect.centerx


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
