import pickle
from Enemies import *

pg.display.set_icon(icon)
pg.mixer.pre_init(44100, -16, 2, 2048)
pg.init()
pg.display.set_caption(title)


class Camera:
    def __init__(self, camWidth, camHeight):
        self.camera = pg.Rect(0, 0, camWidth, camHeight)
        self.game = game
        self.width = camWidth
        self.height = camHeight
        self.screen = self.game.screen

    def offset(self, target):
        return target.move(self.camera.topleft)

    def update(self, target):
        self.screen = self.game.screen
        x = -target.x + int(width / 2)
        y = -target.y + int(height / 2)

        # Limit scrolling to map size
        x = min(0, x)  # Left side
        x = max(-(self.width - self.screen.get_width()), x)  # Right side
        y = min(0, y)  # Top
        y = max(-(self.height - self.screen.get_height()), y)  # Bottom
        self.camera = pg.Rect(x, y, int(self.width), int(self.height))


class CameraRect:
    def __init__(self):
        self.rect = pg.rect.Rect(0, 0, 0, 0)
        self.prevTarget = pg.rect.Rect(0, 0, 0, 0)
        self.points = []
        self.counter = -17

    def update(self, target, speed):
        if target != self.prevTarget:
            if self.prevTarget == pg.rect.Rect(0, 0, 0, 0):
                self.counter = speed
            else:
                self.counter = 0
            self.prevTarget = target
        elif self.counter != speed:
            self.rect.center = pt.getPointOnLine(self.rect.centerx, self.rect.centery, target.centerx, target.centery,
                                                 (self.counter / speed))
            self.counter += 1
        else:
            self.counter = speed
            self.rect.center = target.center


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
        self.ui = pg.sprite.Group()
        self.fadeout = pg.sprite.Group()
        self.battleEndUI = []
        self.loadData()
        self.goombaHasTexted = False
        self.player = Mario(self, width / 2, 1278)
        self.follower = Luigi(self, width / 2, 1278)
        MarioUI(self)
        LuigiUI(self)
        self.song_playing = ""
        self.storeData = {}
        self.despawnList = []
        self.hitBlockList = []
        self.currentPoint = 0
        self.volume = 1
        self.room = "blank"
        fad = Fadeout(self)
        fad.alpha = 255
        self.running = True
        self.pause = False

    def playSong(self, introLength, loopLength, song, loop=True, cont=False, fadein=False, fadeinSpeed=0.05):
        if self.song_playing != song:
            pg.mixer.music.load("music/" + song + ".ogg")
            if cont:
                pg.mixer.music.play()
                pg.mixer.music.set_pos(self.currentPoint)
            else:
                pg.mixer.music.play()
            self.song_playing = song
            if fadein:
                self.volume = 0

        totalLength = introLength + loopLength
        if cont:
            soundPos = pg.mixer.music.get_pos() / 1000 + self.currentPoint
        else:
            soundPos = pg.mixer.music.get_pos() / 1000

        if not self.pause and self.volume < 1:
            self.volume += fadeinSpeed

        pg.mixer.music.set_volume(self.volume)

        if loop:
            if soundPos >= totalLength and self.firstLoop:
                self.currentPoint = 0
                pg.mixer.music.play(0, soundPos - loopLength)
                self.firstLoop = False
                print("YEEEEEEEEE")
            elif soundPos >= loopLength and not self.firstLoop:
                self.currentPoint = 0
                pg.mixer.music.play(0, soundPos + introLength - loopLength)
                print("YOOOOOOOOO")

    def saveGame(self):
        with open("saves/File 1.ini", "wb") as file:
            pickle.dump(self.storeData, file)
            pickle.dump(self.despawnList, file)

    def loadGame(self):
        with open("saves/File 1.ini", "rb") as file:
            self.storeData = pickle.load(file)
            self.despawnList = pickle.load(file)

        print(self.storeData)

    def loadData(self):
        self.sandSound = pg.mixer.Sound("sounds/sand footsteps.ogg")
        self.stoneSound = pg.mixer.Sound("sounds/stone footsteps.ogg")
        self.jumpSound = pg.mixer.Sound("sounds/jump.ogg")
        self.battleSound = pg.mixer.Sound("sounds/startbattle.ogg")
        self.talkSoundHigh = pg.mixer.Sound("sounds/talkSound_high.ogg")
        self.talkSoundMed = pg.mixer.Sound("sounds/talkSound_med.ogg")
        self.talkSoundLow = pg.mixer.Sound("sounds/talkSound_low.ogg")
        self.textBoxOpenSound = pg.mixer.Sound("sounds/textboxopen.ogg")
        self.textBoxCloseSound = pg.mixer.Sound("sounds/textboxclose.ogg")
        self.talkAdvanceSound = pg.mixer.Sound("sounds/talkadvance.ogg")
        self.playerHitSound = pg.mixer.Sound("sounds/playerhit.ogg")
        self.enemyHitSound = pg.mixer.Sound("sounds/enemyhit.ogg")
        self.enemyDieSound = pg.mixer.Sound("sounds/enemydie.ogg")
        self.hammerSwingSound = pg.mixer.Sound("sounds/hammer swing.ogg")
        self.hammerHitSound = pg.mixer.Sound("sounds/hammer hit.ogg")
        self.abilityAdvanceSound = pg.mixer.Sound("sounds/ability cycle.ogg")

    def loadBowserCastle(self):
        self.room = "self.loadBowserCastle()"
        self.playsong = True
        self.sprites = []
        self.collision = []
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.blocks = pg.sprite.Group()
        self.npcs = pg.sprite.Group()
        if self.song_playing != "castle bleck":
            self.firstLoop = True
        self.player = Mario(self, width / 2, 1278)
        self.playerCol = MarioCollision(self)
        self.follower = Luigi(self, width / 2, 1278)
        self.followerCol = LuigiCollision(self)
        self.playerHammer = HammerCollisionMario(self)
        self.followerHammer = HammerCollisionLuigi(self)
        self.sprites.append(self.follower)
        self.sprites.append(self.player)
        self.follower.stepSound = self.stoneSound
        self.player.stepSound = self.stoneSound
        self.map = loadMap("Bowser's Castle")
        self.camera = Camera(self.map.width, self.map.height)
        self.cameraRect = CameraRect()
        # GoombaKing(self, (self.map.width / 2 - 2, self.map.height - 620))
        Block(self, (300, self.map.height - 450))
        Block(self, (600, self.map.height - 450))
        GoombaSmolText(self, (self.map.width / 2 - 2, self.map.height - 420), self.goombaHasTexted)
        GoombaO(self, self.map.width / 2 + 500, self.map.height - 500, "self.loadTeeheeValleyBattle1G()")
        GoombaO(self, self.map.width / 2 - 500, self.map.height - 500, "self.loadTeeheeValleyBattle1G()")
        GoombaO(self, self.map.width / 2 + 400, self.map.height - 500, "self.loadTeeheeValleyBattle1G()")
        GoombaO(self, self.map.width / 2 - 400, self.map.height - 500, "self.loadTeeheeValleyBattle1G()")
        GoombaO(self, self.map.width / 2 + 600, self.map.height - 500, "self.loadTeeheeValleyBattle1G()")
        GoombaO(self, self.map.width / 2 - 600, self.map.height - 500, "self.loadTeeheeValleyBattle1G()")
        GoombaO(self, self.map.width / 2 - 200, self.map.height - 500, "self.loadTeeheeValleyBattle1G()")
        GoombaO(self, self.map.width / 2 + 200, self.map.height - 500, "self.loadTeeheeValleyBattle1G()")
        GoombaO(self, self.map.width / 2 + 300, self.map.height - 500, "self.loadTeeheeValleyBattle1G()")
        GoombaO(self, self.map.width / 2 - 300, self.map.height - 500, "self.loadTeeheeValleyBattle1G()")
        GoombaO(self, self.map.width / 2 + 100, self.map.height - 500, "self.loadTeeheeValleyBattle1G()")
        GoombaO(self, self.map.width / 2 - 100, self.map.height - 500, "self.loadTeeheeValleyBattle1G()")
        GoombaO(self, self.map.width / 2 - 700, self.map.height - 500, "self.loadTeeheeValleyBattle1G()")
        GoombaO(self, self.map.width / 2 + 700, self.map.height - 500, "self.loadTeeheeValleyBattle1G()")
        CountBleck(self, (self.map.width / 2 - 5, self.map.height - 620))
        try:
            self.player.rect.center = self.storeData["mario pos"]
            self.player.stats = self.storeData["mario stats"]
            self.follower.rect.center = self.storeData["luigi pos"]
            self.follower.stats = self.storeData["luigi stats"]
            self.player.facing = self.storeData["mario facing"]
            self.follower.facing = self.storeData["luigi facing"]
            self.player.abilities = self.storeData["mario abilities"]
            self.follower.abilities = self.storeData["luigi abilities"]
            self.follower.moveQueue = self.storeData["luigi move"]
        except:
            pass

        counter = 0
        for enemy in self.enemies:
            enemy.ID = counter
            counter += 1

        counter = 0
        for block in self.blocks:
            block.ID = counter
            counter += 1

        self.bowserCastle()

    def bowserCastle(self):
        self.playing = True
        try:
            self.player.ability = self.storeData["mario current ability"]
            self.player.abilities = self.storeData["mario abilities"]
            self.follower.ability = self.storeData["luigi current ability"]
            self.follower.abilities = self.storeData["luigi abilities"]
        except:
            self.playSong(6.749, 102.727, "castle bleck")
        while self.playing:
            if self.playsong:
                self.playSong(6.749, 102.727, "castle bleck", cont=True, fadein=True)
            self.clock.tick(fps)
            self.events()
            if not self.pause:
                self.updateOverworld()
            self.screen.fill(black)
            self.drawOverworld()

    def loadBattle(self, function):
        self.battleXp = 0
        self.currentPoint += pg.mixer.music.get_pos() / 1000
        pg.mixer.music.stop()
        self.battleSound.play()
        trans = BattleTransition(self)
        going = True
        self.storeData["mario stats"] = self.player.stats
        self.storeData["mario pos"] = self.player.rect.center
        self.storeData["mario facing"] = self.player.facing
        self.storeData["mario abilities"] = self.player.abilities
        if self.player.prevAbility == 12:
            self.storeData["mario current ability"] = self.player.ability
        else:
            self.storeData["mario current ability"] = self.player.prevAbility
        self.storeData["luigi stats"] = self.follower.stats
        self.storeData["luigi pos"] = self.follower.rect.center
        self.storeData["luigi move"] = self.follower.moveQueue
        self.storeData["luigi facing"] = self.follower.facing
        self.storeData["luigi abilities"] = self.follower.abilities
        if self.follower.prevAbility == 12:
            self.storeData["luigi current ability"] = self.follower.ability
        else:
            self.storeData["luigi current ability"] = self.follower.prevAbility
        self.prevRoom = self.room
        while going:
            trans.update()
            self.screen.fill(black)
            self.drawOverworld()

            if trans.currentFrame == len(trans.sprites) - 1 and not pg.mixer.get_busy():
                eval(function)

    def loadTeeheeValleyBattle15G(self):
        self.room = "battle"
        self.sprites = []
        self.collision = []
        self.walls = pg.sprite.Group()
        self.npcs = pg.sprite.Group()
        self.enemies = []
        self.playsong = True
        self.firstLoop = True
        self.player = Mario(self, width / 2, 1278)
        self.playerCol = MarioCollision(self)
        self.follower = Luigi(self, width / 2, 1278)
        self.followerCol = LuigiCollision(self)
        Goomba(self, 722, 1228, 4, 4, "left")
        Goomba(self, 722, 1228, 4, 4, "up")
        Goomba(self, 702, 1378, 4, 4, "right")
        Goomba(self, 700, 1328, 4, 4, "right")
        Goomba(self, 720, 1398, 4, 4, "right")
        Goomba(self, 602, 1380, 4, 4, "right")
        Goomba(self, 720, 1100, 4, 4, "right")
        Goomba(self, 820, 1200, 4, 4, "right")
        Goomba(self, 200, 1200, 4, 4, "down")
        Goomba(self, 1400, 1275, 4, 4, "up")
        Goomba(self, 1300, 1275, 4, 4, "left")
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
        self.teeheeValleyBattle2()

    def loadTeeheeValleyBattle1G(self):
        self.room = "battle"
        self.sprites = []
        self.collision = []
        self.walls = pg.sprite.Group()
        self.npcs = pg.sprite.Group()
        self.enemies = []
        self.playsong = True
        if self.song_playing != "battle":
            self.firstLoop = True
        dir = random.randrange(0, 4)
        if dir == 0:
            Goomba(self, random.randrange(100, 1600), random.randrange(1200, 1300), 4, 4, "up")
        elif dir == 1:
            Goomba(self, random.randrange(100, 1600), random.randrange(1200, 1300), 4, 4, "down")
        elif dir == 2:
            Goomba(self, random.randrange(100, 1600), random.randrange(1150, 1300), 4, 4, "left")
        elif dir == 3:
            Goomba(self, random.randrange(100, 1600), random.randrange(1200, 1300), 4, 4, "right")

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

        self.map = loadMap("teehee valley battle", True)
        self.camera = Camera(self.map.width, self.map.height)
        self.player = Mario(self, self.map.width / 2, 1278)
        self.playerCol = MarioCollision(self)
        self.follower = Luigi(self, self.map.width / 2, 1278)
        self.followerCol = LuigiCollision(self)
        self.sprites.append(self.follower)
        self.sprites.append(self.player)
        self.follower.stepSound = self.sandSound
        self.player.stepSound = self.sandSound
        try:
            self.player.stats = self.storeData["mario stats"]
            self.follower.stats = self.storeData["luigi stats"]
        except:
            pass
        self.teeheeValleyBattle()

    def teeheeValleyBattle(self):
        self.playing = True
        self.player.ability = self.storeData["mario current ability"]
        self.player.abilities = self.storeData["mario abilities"]
        self.follower.ability = self.storeData["luigi current ability"]
        self.follower.abilities = self.storeData["luigi abilities"]
        self.cameraRect = CameraRect()
        pg.mixer.music.load("music/battle.ogg")
        pg.mixer.music.play(-1)
        while self.playing:
            self.clock.tick(fps)
            self.events()
            if not self.pause:
                self.updateBattle()
            self.screen.fill(black)
            self.drawBattle()
            # if self.player.stats["hp"] <= 0 and self.follower.stats["hp"] <= 0:
            #     self.gameOver()
            if len(self.enemies) == 0:
                self.battleOver()

    def teeheeValleyBattle2(self):
        self.playing = True
        self.player.ability = self.storeData["mario current ability"]
        self.player.abilities = self.storeData["mario abilities"]
        self.follower.ability = self.storeData["luigi current ability"]
        self.follower.abilities = self.storeData["luigi abilities"]
        self.cameraRect = CameraRect()
        # pg.mixer.music.load("music/battle.ogg")
        # pg.mixer.music.play(-1)
        while self.playing:
            self.playSong(54.965, 191.98, "new soup final boss")
            self.clock.tick(fps)
            self.events()
            if not self.pause:
                self.updateBattle()
            self.screen.fill(black)
            self.drawBattle()
            # if self.player.stats["hp"] <= 0 and self.follower.stats["hp"] <= 0:
            #     self.gameOver()
            if len(self.enemies) == 0:
                self.battleOver()

    def battleOver(self):
        pg.mixer.music.stop()
        self.battleEndUI = []
        self.storeData["mario abilities"] = self.player.abilities
        if self.player.prevAbility == 12:
            self.storeData["mario current ability"] = self.player.ability
        else:
            self.storeData["mario current ability"] = self.player.prevAbility
        self.storeData["luigi abilities"] = self.follower.abilities
        if self.follower.prevAbility == 12:
            self.storeData["luigi current ability"] = self.follower.ability
        else:
            self.storeData["luigi current ability"] = self.follower.prevAbility
        self.storeData["mario stats"] = self.player.stats.copy()
        self.storeData["luigi stats"] = self.follower.stats.copy()
        self.map.rect.center = self.camera.offset(self.map.rect).center
        self.player.imgRect.center = self.camera.offset(self.player.imgRect).center
        self.player.rect.center = self.camera.offset(self.player.rect).center
        self.follower.imgRect.center = self.camera.offset(self.follower.imgRect).center
        self.follower.rect.center = self.camera.offset(self.follower.rect).center
        if not self.player.dead:
            self.marioBattleOver = MarioBattleComplete(self)
            self.sprites.append(self.marioBattleOver)
        if not self.follower.dead:
            self.luigiBattleOver = LuigiBattleComplete(self)
            self.sprites.append(self.luigiBattleOver)
        expNumbers = ExpNumbers(self)
        MarioExpNumbers(self)
        LuigiExpNumbers(self)
        self.dimBackground = fadeout.get_rect()
        while True:
            self.playSong(5.44, 36.708, "battle victory")
            self.clock.tick(60)
            self.events()
            if not self.pause:
                self.updateBattleOver()
            self.screen.fill(black)
            self.drawBattleOver()
            keys = pg.key.get_pressed()
            if keys[pg.K_m] or keys[pg.K_l] or keys[pg.K_SPACE]:
                break

        expNumbers.exp = 0
        if not self.player.dead:
            self.storeData["mario stats"]["exp"] += self.battleXp
            self.player.stats = self.storeData["mario stats"]
        if not self.follower.dead:
            self.storeData["luigi stats"]["exp"] += self.battleXp
            self.follower.stats = self.storeData["luigi stats"]
        fade = Fadeout(self)
        pg.mixer.music.fadeout(1000)
        while True:
            self.clock.tick(fps)
            self.events()
            if not self.pause:
                self.updateBattleOver()
            self.screen.fill(black)
            self.drawBattleOver()
            if fade.alpha >= 255:
                break

        if not self.player.dead:
            self.sprites.remove(self.marioBattleOver)
        if not self.follower.dead:
            self.sprites.remove(self.luigiBattleOver)
        self.room = self.prevRoom
        self.updateBattleOver()
        if self.player.dead:
            self.player.dead = False
            self.player.stats["hp"] = 1
        if self.follower.dead:
            self.follower.dead = False
            self.follower.stats["hp"] = 1
        self.storeData["mario stats"] = self.player.stats
        self.storeData["luigi stats"] = self.follower.stats
        eval(self.prevRoom)

    def events(self):
        self.event = pg.event.get().copy()
        for event in self.event:
            keys = pg.key.get_pressed()
            if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                pg.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p:
                    self.pause = not self.pause
                    if self.pause:
                        self.volume = 0.5
                    else:
                        self.volume = 1
                if event.key == pg.K_f:
                    self.player.stats["hp"] = self.player.stats["maxHP"]
                    if self.player.dead:
                        self.player.dead = False
                        self.player.shadow = self.player.shadowFrames["normal"]
                        center = self.player.rect.center
                        self.player.rect = self.player.shadow.get_rect()
                        self.player.rect.center = center
                    self.follower.stats["hp"] = self.follower.stats["maxHP"]
                    if self.follower.dead:
                        self.follower.dead = False
                        center = self.follower.rect.center
                        self.follower.shadow = self.follower.shadowFrames["normal"]
                        self.follower.rect = self.follower.shadow.get_rect()
                        self.follower.rect.center = center
                if event.key == pg.K_t:
                    self.saveGame()

    def updateBattleOver(self):
        [ui.update() for ui in self.battleEndUI]
        self.fadeout.update()
        self.effects.update()
        for sprite in self.sprites:
            if sprite == self.player or sprite == self.follower:
                pass
            else:
                sprite.update()
        self.ui.update()
        [col.update() for col in self.collision]
        self.camera.update(pg.Rect(width / 2, height / 2, 0, 0))

    def updateBattle(self):
        self.fadeout.update()
        self.effects.update()
        [sprite.update() for sprite in self.sprites]
        self.ui.update()
        [col.update() for col in self.collision]
        if not self.player.dead:
            self.cameraRect.update(self.player.rect, 20)
        else:
            self.cameraRect.update(self.follower.rect, 20)
        self.camera.update(self.cameraRect.rect)

    def updateOverworld(self):
        [ui.update() for ui in self.battleEndUI]
        self.fadeout.update()
        self.npcs.update()
        self.effects.update()
        [enemy.update() for enemy in self.enemies]
        self.ui.update()
        [sprite.update() for sprite in self.sprites]
        [col.update() for col in self.collision]
        self.cameraRect.update(self.player.rect, 20)
        self.camera.update(self.cameraRect.rect)

    def blit_alpha(self, target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pg.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)
        target.blit(temp, location)

    def drawBattleOver(self):
        self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        for sprite in self.sprites:
            if sprite.dead:
                self.screen.blit(sprite.shadow, sprite.rect)
                self.screen.blit(sprite.image, sprite.imgRect)
        self.blit_alpha(self.screen, fadeout, self.dimBackground, 125)
        for ui in self.battleEndUI:
            ui.draw()
        self.sprites.sort(key=self.sortByYPos)

        for sprite in self.sprites:
            if not sprite.dead:
                self.blit_alpha(self.screen, sprite.image, self.camera.offset(sprite.rect), sprite.alpha)

        [self.blit_alpha(self.screen, fad.image, fad.rect, fad.alpha) for fad in self.fadeout]

        pg.display.flip()

    def drawBattle(self):
        self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        self.sprites.sort(key=self.sortByYPos)
        for sprite in self.sprites:
            try:
                self.screen.blit(sprite.shadow, self.camera.offset(sprite.rect))
            except:
                pass

        for sprite in self.sprites:
            if sprite.dead:
                self.blit_alpha(self.screen, sprite.image, self.camera.offset(sprite.imgRect), sprite.alpha)

        for sprite in self.sprites:
            if not sprite.dead:
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

        [ui.draw() for ui in self.ui]

        for fx in self.effects:
            if fx.offset:
                self.blit_alpha(self.screen, fx.image, self.camera.offset(fx.rect), fx.alpha)
            else:
                self.blit_alpha(self.screen, fx.image, fx.rect, fx.alpha)

        [self.blit_alpha(self.screen, fad.image, fad.rect, fad.alpha) for fad in self.fadeout]

        pg.display.flip()

    def drawOverworld(self):
        self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        self.sprites.sort(key=self.sortByYPos)
        for sprite in self.sprites:
            try:
                self.screen.blit(sprite.shadow, self.camera.offset(sprite.rect))
            except:
                pass

        for sprite in self.sprites:
            self.blit_alpha(self.screen, sprite.image, self.camera.offset(sprite.imgRect), sprite.alpha)

        try:
            self.screen.blit(self.map.foreground, self.camera.offset(self.map.rect))
        except:
            pass

        [ui.draw() for ui in self.ui]
        [ui.draw() for ui in self.battleEndUI]

        for fx in self.effects:
            if fx.offset:
                self.blit_alpha(self.screen, fx.image, self.camera.offset(fx.rect), fx.alpha)
            else:
                self.blit_alpha(self.screen, fx.image, fx.rect, fx.alpha)

        [self.blit_alpha(self.screen, fad.image, fad.rect, fad.alpha) for fad in self.fadeout]

        pg.display.flip()

    def sortByYPos(self, element):
        return element.rect.bottom


game = Game()

while game.running:
    # game.loadGame()
    game.loadBowserCastle()
