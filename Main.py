import pygame as pg
from settings import *
from sprites import *

pg.mixer.pre_init(44100, -16, 2, 2048)
pg.init()
pg.display.set_caption(title)


class Camera:
    def __init__(self, camWidth, camHeight):
        self.camera = pg.Rect(0, 0, camWidth, camHeight)
        self.width = camWidth
        self.height = camHeight

    def offset(self, target):
        return target.move(self.camera.topleft)

    def update(self, target):
        x = -target.x + int(width / 2)
        y = -target.y + int(height / 2)

        # Limit scrolling to map size
        x = min(0, x)  # Left side
        x = max(-(self.width - width), x)  # Right side
        y = min(0, y)  # Top
        y = max(-(self.height - height), y)  # Bottom
        self.camera = pg.Rect(x, y, int(self.width), int(self.height))


class loadMap:
    def __init__(self, mapname, foreground=False):
        self.image = pg.image.load("sprites/maps/" + mapname + ".png").convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()

        if foreground:
            self.foreground = pg.image.load("sprites/maps/" + mapname + "_foreground.png").convert_alpha()


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((width, height))
        self.clock = pg.time.Clock()
        self.effects = pg.sprite.Group()
        self.loadData()
        self.song_playing = ""
        self.storeData = {}
        self.despawnList = []
        self.running = True
        self.fullscreen = False

    def playSong(self, introLength, loopLength, song, loop=True):
        if self.song_playing != song:
            pg.mixer.music.load("music/" + song + ".ogg")
            pg.mixer.music.play()
            self.song_playing = song

        self.totalLength = introLength + loopLength
        self.soundPos = pg.mixer.music.get_pos() / 1000

        if loop:
            if self.soundPos >= self.totalLength and self.firstLoop:
                pg.mixer.music.play(0, self.soundPos - loopLength)
                self.firstLoop = False
                print("YEEEEEEEEE")
            elif self.soundPos >= loopLength and not self.firstLoop:
                pg.mixer.music.play(0, self.soundPos + introLength - loopLength)
                print("YOOOOOOOOO")

    def loadData(self):
        self.sandSound = pg.mixer.Sound("sounds/sand footsteps.ogg")
        self.stoneSound = pg.mixer.Sound("sounds/stone footsteps.ogg")
        self.jumpSound = pg.mixer.Sound("sounds/jump.ogg")
        self.battleSound = pg.mixer.Sound("sounds/startbattle.ogg")

    def loadBowserCastle(self):
        self.room = "BC"
        self.sprites = []
        self.collision = []
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        if self.song_playing != "cackletta battle":
            self.firstLoop = True
        self.player = Mario(self, width / 2, 1278)
        self.playerCol = MarioCollision(self)
        self.follower = Luigi(self, width / 2, 1278)
        self.followerCol = LuigiCollision(self)
        self.sprites.append(self.follower)
        self.sprites.append(self.player)
        self.follower.stepSound = self.stoneSound
        self.player.stepSound = self.stoneSound
        self.map = loadMap("Bowser's Castle")
        self.camera = Camera(self.map.width, self.map.height)
        GoombaO(self, self.map.width / 2, self.map.height - 620, "THB15G")
        GoombaO(self, self.map.width / 2 + 500, self.map.height - 500, "THB1G")
        GoombaO(self, self.map.width / 2 - 500, self.map.height - 500, "THB1G")
        GoombaO(self, self.map.width / 2 + 400, self.map.height - 500, "THB1G")
        GoombaO(self, self.map.width / 2 - 400, self.map.height - 500, "THB1G")
        GoombaO(self, self.map.width / 2 + 600, self.map.height - 500, "THB1G")
        GoombaO(self, self.map.width / 2 - 600, self.map.height - 500, "THB1G")
        GoombaO(self, self.map.width / 2 - 200, self.map.height - 500, "THB1G")
        GoombaO(self, self.map.width / 2 + 200, self.map.height - 500, "THB1G")
        GoombaO(self, self.map.width / 2 + 300, self.map.height - 500, "THB1G")
        GoombaO(self, self.map.width / 2 - 300, self.map.height - 500, "THB1G")
        GoombaO(self, self.map.width / 2 + 100, self.map.height - 500, "THB1G")
        GoombaO(self, self.map.width / 2 - 100, self.map.height - 500, "THB1G")
        GoombaO(self, self.map.width / 2 - 700, self.map.height - 500, "THB1G")
        GoombaO(self, self.map.width / 2 + 700, self.map.height - 500, "THB1G")
        try:
            self.player.rect.center = self.storeData["mario pos"]
            self.player.stats = self.storeData["mario stats"]
            self.follower.rect.center = self.storeData["luigi pos"]
            self.follower.stats = self.storeData["luigi stats"]
            self.follower.moveQueue = self.storeData["luigi move"]
            self.player.facing = self.storeData["mario facing"]
            self.follower.facing = self.storeData["luigi facing"]
        except:
            pass

        counter = 0
        for enemy in self.enemies:
            enemy.ID = counter
            counter += 1

        self.bowserCastle()

    def bowserCastle(self):
        self.playing = True
        while self.playing:
            self.playSong(17.235, 64.755, "cackletta battle")
            self.clock.tick(fps)
            self.events()
            self.updateOverworld()
            self.drawOverworld()

    def loadTeeheeValleyBattle15G(self):
        self.room = "THB15G"
        self.sprites = []
        self.collision = []
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        if self.song_playing != "battle":
            self.firstLoop = True
        self.player = Mario(self, width / 2, 1278)
        self.playerCol = MarioCollision(self)
        self.follower = Luigi(self, width / 2, 1278)
        self.followerCol = LuigiCollision(self)
        Goomba(self, 722, 1228, 4, 4, "left")
        Goomba(self, 722, 1228, 4, 4, "up")
        Goomba(self, 702, 1378, 4, 4, "right")
        Goomba(self, 702, 1378, 4, 4, "right")
        Goomba(self, 700, 1328, 4, 4, "right")
        Goomba(self, 720, 1398, 4, 4, "right")
        Goomba(self, 602, 1380, 4, 4, "right")
        Goomba(self, 720, 1100, 1, 1, "right")
        Goomba(self, 200, 1200, 4, 4, "down")
        Goomba(self, 1400, 1275, 4, 4, "up")
        Goomba(self, 1300, 1275, 1, 5, "left")
        Goomba(self, 1500, 1275, 4, 4, "down")
        Goomba(self, 500, 1275, 4, 4, "up")
        Goomba(self, 400, 1275, 4, 4, "up")
        Goomba(self, 800, 1275, 4, 4, "up")

        # Top Half Collision
        Wall(self, 96, 1090, 384, 62)
        Wall(self, 552, 1064, 136, 88)
        Wall(self, -60, 1028, 706, 76)
        Wall(self, 640, 1014, 243, 42)
        Wall(self, 750, 1015, 98, 73)
        Wall(self, 808, 1052, 92, 72)
        Wall(self, 896, 1037, 213, 61)
        Wall(self, 1026, 1098, 42, 42)
        Wall(self, 1104, 1083, 480, 69)
        Wall(self, 1572, 1055, 126, 45)

        # Bottom Half Collision
        Wall(self, -70, 1455, 300, 70)
        Wall(self, 229, 1486, 72, 22)
        Wall(self, 300, 1455, 170, 100)
        Wall(self, 454, 1522, 188, 32)
        Wall(self, 642, 1552, 68, 32)
        Wall(self, 704, 1522, 120, 32)
        Wall(self, 792, 1455, 186, 72)
        Wall(self, 975, 1522, 70, 72)
        Wall(self, 1038, 1455, 374, 72)
        Wall(self, 1407, 1486, 116, 72)
        Wall(self, 1522, 1455, 200, 72)

        try:
            self.player.stats = self.storeData["mario stats"]
            self.follower.stats = self.storeData["luigi stats"]
        except:
            pass

        self.sprites.append(self.follower)
        self.sprites.append(self.player)
        self.follower.stepSound = self.sandSound
        self.player.stepSound = self.sandSound
        self.map = loadMap("teehee valley battle", True)
        self.camera = Camera(self.map.width, self.map.height)
        self.teeheeValleyBattle()

    def loadTeeheeValleyBattleEm(self):
        self.room = "THBEM"
        self.sprites = []
        self.collision = []
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        if self.song_playing != "battle":
            self.firstLoop = True
        Goomba(self, 0, 0, 0, 0)
        self.player = Mario(self, width / 2, 1278)
        self.playerCol = MarioCollision(self)
        self.follower = Luigi(self, width / 2, 1278)
        self.followerCol = LuigiCollision(self)
        self.sprites.append(self.follower)
        self.sprites.append(self.player)
        try:
            self.player.rect.center = self.storeData["mario pos"]
            self.player.stats = self.storeData["mario stats"]
            self.follower.rect.center = self.storeData["luigi pos"]
            self.follower.stats = self.storeData["luigi stats"]
            self.follower.moveQueue = self.storeData["luigi move"]
            self.player.facing = self.storeData["mario facing"]
            self.follower.facing = self.storeData["luigi facing"]
        except:
            pass

        # Top Half Collision
        Wall(self, 96, 1090, 384, 62)
        Wall(self, 552, 1064, 136, 88)
        Wall(self, -60, 1028, 706, 76)
        Wall(self, 640, 1014, 243, 42)
        Wall(self, 750, 1015, 98, 73)
        Wall(self, 808, 1052, 92, 72)
        Wall(self, 896, 1037, 213, 61)
        Wall(self, 1026, 1098, 42, 42)
        Wall(self, 1104, 1083, 480, 69)
        Wall(self, 1572, 1055, 126, 45)

        # Bottom Half Collision
        Wall(self, -70, 1455, 300, 70)
        Wall(self, 229, 1486, 72, 22)
        Wall(self, 300, 1455, 170, 100)
        Wall(self, 454, 1522, 188, 32)
        Wall(self, 642, 1552, 68, 32)
        Wall(self, 704, 1522, 120, 32)
        Wall(self, 792, 1455, 186, 72)
        Wall(self, 975, 1522, 70, 72)
        Wall(self, 1038, 1455, 374, 72)
        Wall(self, 1407, 1486, 116, 72)
        Wall(self, 1522, 1455, 200, 72)

        self.follower.stepSound = self.sandSound
        self.player.stepSound = self.sandSound
        self.map = loadMap("teehee valley battle", True)
        self.camera = Camera(self.map.width, self.map.height)
        self.teeheeValleyBattle()

    def loadTeeheeValleyBattle1G(self):
        self.room = "THB1G"
        self.sprites = []
        self.collision = []
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        if self.song_playing != "battle":
            self.firstLoop = True
        self.player = Mario(self, width / 2, 1278)
        self.playerCol = MarioCollision(self)
        self.follower = Luigi(self, width / 2, 1278)
        self.followerCol = LuigiCollision(self)
        Goomba(self, 722, 1228, 4, 4, "up")

        # Top Half Collision
        Wall(self, 96, 1090, 384, 62)
        Wall(self, 552, 1064, 136, 88)
        Wall(self, -60, 1028, 706, 76)
        Wall(self, 640, 1014, 243, 42)
        Wall(self, 750, 1015, 98, 73)
        Wall(self, 808, 1052, 92, 72)
        Wall(self, 896, 1037, 213, 61)
        Wall(self, 1026, 1098, 42, 42)
        Wall(self, 1104, 1083, 480, 69)
        Wall(self, 1572, 1055, 126, 45)

        # Bottom Half Collision
        Wall(self, -70, 1455, 300, 70)
        Wall(self, 229, 1486, 72, 22)
        Wall(self, 300, 1455, 170, 100)
        Wall(self, 454, 1522, 188, 32)
        Wall(self, 642, 1552, 68, 32)
        Wall(self, 704, 1522, 120, 32)
        Wall(self, 792, 1455, 186, 72)
        Wall(self, 975, 1522, 70, 72)
        Wall(self, 1038, 1455, 374, 72)
        Wall(self, 1407, 1486, 116, 72)
        Wall(self, 1522, 1455, 200, 72)

        try:
            self.player.stats = self.storeData["mario stats"]
            self.follower.stats = self.storeData["luigi stats"]
        except:
            pass

        self.sprites.append(self.follower)
        self.sprites.append(self.player)
        self.follower.stepSound = self.sandSound
        self.player.stepSound = self.sandSound
        self.map = loadMap("teehee valley battle", True)
        self.camera = Camera(self.map.width, self.map.height)
        self.teeheeValleyBattle()

    def teeheeValleyBattle(self):
        if not self.running:
            return
        self.playing = True
        while self.playing:
            self.playSong(7.01, 139.132, "battle")
            self.clock.tick(fps)
            self.events()
            self.updateBattle()
            self.drawBattle()
            if len(self.enemies) == 0:
                self.room = self.prevRoom
                self.storeData["mario stats"] = self.player.stats
                self.storeData["luigi stats"] = self.follower.stats
                self.gotoPrevRoom()

    def gotoPrevRoom(self):
        if self.prevRoom == "THBEM":
            self.loadTeeheeValleyBattleEm()
        elif self.prevRoom == "BC":
            self.loadBowserCastle()

    def loadBattle(self, room):
        pg.mixer.music.stop()
        self.battleSound.play()
        trans = BattleTransition(self)
        going = True
        self.storeData["mario stats"] = self.player.stats
        self.storeData["mario pos"] = self.player.rect.center
        self.storeData["mario facing"] = self.player.facing
        self.storeData["luigi stats"] = self.follower.stats
        self.storeData["luigi pos"] = self.follower.rect.center
        self.storeData["luigi move"] = self.follower.moveQueue
        self.storeData["luigi facing"] = self.follower.facing
        self.prevRoom = self.room
        while going:
            trans.update()
            self.drawOverworld()
            for event in pg.event.get():
                if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                    if self.playing:
                        self.playing = False
                    self.running = False

            if trans.currentFrame == len(trans.sprites) - 1:
                if room == "THB1G":
                    self.loadTeeheeValleyBattle1G()
                    going = False
                elif room == "THB15G":
                    self.loadTeeheeValleyBattle15G()
                    going = False

    def events(self):
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_F4:
                    if self.fullscreen:
                        self.screen = pg.display.set_mode((width, height))
                    else:
                        self.screen = pg.display.set_mode((width, height), pg.FULLSCREEN)
                    self.fullscreen = not self.fullscreen
                if event.key == pg.K_m:
                    if not self.player.jumping:
                        self.player.jumping = True
                        self.player.jumpTimer = 1
                        self.player.airTimer = 0
                        self.jumpSound.play()
                if event.key == pg.K_l:
                    if not self.follower.jumping:
                        self.follower.jumping = True
                        self.follower.jumpTimer = 1
                        self.follower.airTimer = 0
                        self.jumpSound.play()
                if event.key == pg.K_SPACE:
                    if not self.player.jumping:
                        self.player.jumping = True
                        self.player.jumpTimer = 1
                        self.player.airTimer = 0
                        self.jumpSound.play()
                    if not self.follower.jumping:
                        self.follower.jumping = True
                        self.follower.jumpTimer = 1
                        self.follower.airTimer = 0
                        self.jumpSound.play()

    def updateBattle(self):
        keys = pg.key.get_pressed()
        doubleDamageM = False
        doubleDamageL = False
        self.effects.update()
        [sprite.update() for sprite in self.sprites]
        [col.update() for col in self.collision]
        self.camera.update(self.player.rect)

        hits = pg.sprite.spritecollideany(self.player, self.enemies)
        if hits:
            hitsRound2 = pg.sprite.collide_rect(self.playerCol, hits)
            if keys[pg.K_m] and self.player.going == "down" and self.player.imgRect.bottom <= hits.imgRect.top + 50:
                doubleDamageM = True
            if hitsRound2:
                if self.player.imgRect.bottom - 50 <= hits.imgRect.top and self.player.going == "down" and self.player.jumping and hits.stats["hp"] > 0:
                    if doubleDamageM:
                        hits.stats["hp"] -= 2 * (self.player.stats["pow"] - hits.stats["def"])
                    else:
                        hits.stats["hp"] -= (self.player.stats["pow"] - hits.stats["def"])
                    self.player.airTimer = 0

        luigiHits = pg.sprite.spritecollideany(self.follower, self.enemies)
        if luigiHits:
            hitsRound2 = pg.sprite.collide_rect(self.followerCol, luigiHits)
            if keys[pg.K_l] and self.follower.going == "down" and self.follower.imgRect.bottom <= luigiHits.imgRect.top + 50:
                doubleDamageL = True
            if hitsRound2:
                if self.follower.imgRect.bottom - 50 <= luigiHits.imgRect.top and self.follower.going == "down" and self.follower.jumping and luigiHits.stats["hp"] > 0:
                    if doubleDamageL:
                        luigiHits.stats["hp"] -= 2 * (self.follower.stats["pow"] - luigiHits.stats["def"])
                    else:
                        luigiHits.stats["hp"] -= (self.follower.stats["pow"] - luigiHits.stats["def"])
                    self.follower.airTimer = 0

    def updateOverworld(self):
        self.effects.update()
        self.enemies.update()
        [sprite.update() for sprite in self.sprites]
        [col.update() for col in self.collision]
        self.camera.update(self.player.rect)

    def blit_alpha(self, target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pg.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)
        target.blit(temp, location)

    def drawBattle(self):
        self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        self.sprites.sort(key=self.sortByYPos)
        for sprite in self.sprites:
            self.screen.blit(sprite.shadow, self.camera.offset(sprite.rect))

        for sprite in self.sprites:
            self.blit_alpha(self.screen, sprite.image, self.camera.offset(sprite.imgRect), sprite.alpha)

        try:
            self.screen.blit(self.map.foreground, self.camera.offset(self.map.rect))
        except:
            pass

        for enemy in self.enemies:
            if enemy.stats["hp"] != enemy.stats["maxHP"]:
                if enemy.stats["hp"] >= 0:
                    pg.draw.rect(self.screen, red, self.camera.offset(
                        pg.Rect(enemy.rect.left, enemy.imgRect.top - 12,
                                (enemy.rect.width * (enemy.stats["hp"] / enemy.stats["maxHP"])), 10)))
                pg.draw.rect(self.screen, black,
                             self.camera.offset(pg.Rect(enemy.rect.left, enemy.imgRect.top - 12, enemy.rect.width, 10)),
                             1)

        for fx in self.effects:
            if fx.offset:
                self.blit_alpha(self.screen, fx.image, self.camera.offset(fx.rect), fx.alpha)
            else:
                self.blit_alpha(self.screen, fx.image, fx.rect, fx.alpha)

        pg.display.flip()

    def drawOverworld(self):
        self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        self.sprites.sort(key=self.sortByYPos)
        for sprite in self.sprites:
            self.screen.blit(sprite.shadow, self.camera.offset(sprite.rect))

        for sprite in self.sprites:
            self.blit_alpha(self.screen, sprite.image, self.camera.offset(sprite.imgRect), sprite.alpha)

        try:
            self.screen.blit(self.map.foreground, self.camera.offset(self.map.rect))
        except:
            pass

        for fx in self.effects:
            if fx.offset:
                self.blit_alpha(self.screen, fx.image, self.camera.offset(fx.rect), fx.alpha)
            else:
                self.blit_alpha(self.screen, fx.image, fx.rect, fx.alpha)

        pg.display.flip()

    def sortByYPos(self, element):
        return element.rect.bottom

    def drawTextIU(self, text, size, color, x, y, font, hilight=False):
        fnt = pg.font.Font("fonts/" + font, size)
        textSurface = fnt.render(text, True, color)
        textRect = textSurface.get_rect()
        textRect.midtop = (int(x), int(y))
        if hilight:
            pg.draw.rect(self.screen, black, self.camera.offset(textRect))
        self.screen.blit(textSurface, self.camera.offset(textRect))

    def drawTextUI(self, text, size, color, x, y, font, hilight=False):
        fnt = pg.font.Font("fonts/" + font, size)
        textSurface = fnt.render(text, True, color)
        textRect = textSurface.get_rect()
        textRect.midtop = (int(x), int(y))
        if hilight:
            pg.draw.rect(self.screen, black, textRect)
        self.screen.blit(textSurface, textRect)


game = Game()

while game.running:
    game.loadBowserCastle()

pg.quit()
