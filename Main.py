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
        self.song_playing = ""
        self.running = True

    def playSong(self, introLength, loopLength, song, loop=True):
        if self.song_playing != "playing":
            pg.mixer.music.load("music/" + song + ".ogg")
            pg.mixer.music.play()
            self.song_playing = "playing"

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
        self.jumpSound = pg.mixer.Sound("sounds/jump.ogg")

    def loadTeeheeValleyBattle(self):
        self.loadData()
        self.sprites = []
        self.collision = []
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.firstLoop = True
        self.player = Mario(self, 422, 1228)
        self.playerCol = MarioCollision(self)
        self.follower = Luigi(self, 422, 1228)
        self.followerCol = LuigiCollision(self)
        self.goomba = Goomba(self, 722, 1228, 5, 5, "left")
        self.goomba2 = Goomba(self, 722, 1228, 5, 5, "up")
        self.goomba3 = Goomba(self, 702, 1378, 5, 5, "right")
        self.goomba4 = Goomba(self, 720, 1100, 1, 1, "right")
        self.goomba5 = Goomba(self, 200, 1200, 5, 5, "down")
        self.goomba6 = Goomba(self, 1400, 1275, 5, 5, "up")
        self.goomba7 = Goomba(self, 1300, 1275, 1, 5, "left")

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

        self.sprites.append(self.follower)
        self.sprites.append(self.player)
        self.follower.stepSound = self.sandSound
        self.player.stepSound = self.sandSound
        self.map = loadMap("teehee valley battle", True)
        self.camera = Camera(self.map.width, self.map.height)
        self.teeheeValleyBattle()

    def teeheeValleyBattle(self):
        self.playing = True

        while self.playing:
            # self.playSong(14.764, 42.501, "Teehee Valley")
            self.playSong(7.01, 139.132, "battle")
            self.clock.tick(fps)
            self.events()
            self.update()
            self.draw()

        self.playing = False

    def events(self):
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
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


    def update(self):
        [sprite.update() for sprite in self.sprites]
        [col.update() for col in self.collision]
        self.camera.update(self.player.rect)

        hits = pg.sprite.spritecollideany(self.player, self.enemies)
        if hits:
            hitsRound2 = pg.sprite.collide_rect(self.playerCol, hits)
            if hitsRound2:
                hits.going = False
                hits.image.set_alpha(0)
                hits.shadow.set_alpha(0)
            else:
                hits.going = True
                hits.image.set_alpha(255)
                hits.shadow.set_alpha(255)

        luigiHits = pg.sprite.spritecollideany(self.follower, self.enemies)
        if luigiHits:
            hitsRound2 = pg.sprite.collide_rect(self.followerCol, luigiHits)
            if hitsRound2:
                luigiHits.going = False
            else:
                luigiHits.going = True


    def draw(self):
        self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        self.sprites.sort(key=self.sortByYPos)
        for sprite in self.sprites:
            self.screen.blit(sprite.shadow, self.camera.offset(sprite.rect))
        for sprite in self.sprites:
            self.screen.blit(sprite.image, self.camera.offset(sprite.imgRect))
        if self.map.foreground:
            self.screen.blit(self.map.foreground, self.camera.offset(self.map.rect))
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
    game.loadTeeheeValleyBattle()

pg.quit()
