import pickle
import numpy as np
import time
from moviepy.editor import *
from Settings import *
from CutsceneObjects import *
from BrosAttacks import *
from Enemies import *

pg.display.set_icon(icon)
pg.mixer.pre_init(44100, -16, 2, 2048)
pg.init()
pg.display.set_caption(title)


class Camera:
    def __init__(self, game, camWidth, camHeight):
        self.camera = pg.Rect(0, 0, camWidth, camHeight)
        self.game = game
        self.width = camWidth
        self.height = camHeight
        self.screen = self.game.screen

    def offset(self, target):
        return target.move(self.camera.topleft)

    def update(self, target):
        self.screen = self.game.screen
        x = -target.x + int(self.screen.get_width() / 2)
        y = -target.y + int(self.screen.get_height() / 2)

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


class Map:
    def __init__(self, mapname, foreground=False, background=False):
        self.image = pg.image.load("sprites/maps/" + mapname + ".png").convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()

        if foreground:
            self.foreground = pg.image.load("sprites/maps/" + mapname + "_foreground.png").convert_alpha()

        if background:
            self.background = pg.image.load("sprites/maps/" + mapname + "_background.png").convert_alpha()


class Game:
    def __init__(self):
        self.playing = False
        self.voidSize = 0.1
        self.void = Void(self, self.voidSize)
        self.screen = pg.display.set_mode((width, height))
        self.camera = Camera(self, width, height)
        self.imgRect = pg.rect.Rect(width / 2, height / 2, 0, 0)
        self.clock = pg.time.Clock()
        self.effects = pg.sprite.Group()
        self.blockContents = pg.sprite.Group()
        self.ui = pg.sprite.Group()
        self.textboxes = pg.sprite.Group()
        self.fadeout = pg.sprite.Group()
        self.cutscenes = []
        self.usedCutscenes = []
        self.battleEndUI = []
        self.cutsceneSprites = []
        self.transistors = []
        self.loadData()
        self.playtime = 0
        self.goombaHasTexted = False
        self.player = Mario(self, 0, 0)
        self.follower = Luigi(self, 0, 0)
        self.file = 1
        self.song_playing = ""
        self.storeData = {}
        self.despawnList = []
        self.hitBlockList = []
        self.currentPoint = 0
        self.volume = 1
        self.room = "title screen"
        self.area = "title screen"
        fad = Fadeout(self)
        fad.alpha = 255
        self.loops = 0
        self.running = True
        self.pause = False
        self.fullscreen = False
        self.leader = "mario"
        self.coins = 0
        self.items = [["Mushroom", -1, mushroomSprite, "hp", "maxHP", "Restores 30 HP to one Bro.", 30],
                      ["Super Mushroom", -1, mushroomSprite, "hp", "maxHP", "Restores 60 HP to one Bro.", 60],
                      ["Ultra Mushroom", -1, mushroomSprite, "hp", "maxHP", "Restores 120 HP to one Bro.", 120],
                      ["Max Mushroom", -1, mushroomSprite, "hp", "maxHP", "Fully restores HP to one Bro.", "maxHP"],
                      ["Nut", -1, NutSprite, "hp", "maxHP", "Restores 20 BP for both Bros.", 20],
                      ["Super Nut", -1, NutSprite, "hp", "maxHP", "Restores 40 BP for both Bros.", 40],
                      ["Ultra Nut", -1, NutSprite, "hp", "maxHP", "Restores 80 BP for both Bros.", 80],
                      ["Max Nut", -1, NutSprite, "hp", "maxHP", "Fuly restores  BP for both Bros.", "maxHP"],
                      ["Syrup", -1, syrupSprite, "bp", "maxBP", "Restores 10 BP to one Bro.", 10],
                      ["Super Syrup", -1, syrupSprite, "bp", "maxBP", "Restores 20 BP to one Bro.", 20],
                      ["Ultra Syrup", -1, syrupSprite, "bp", "maxBP", "Restores 30 BP to one Bro.", 30],
                      ["Max Syrup", -1, syrupSprite, "bp", "maxBP", "Fully restores BP to one Bro.", "maxBP"],
                      ["1-UP Mushroom", -1, oneUpSprite, "hp", 1, "Revives a fallen Bro with 1/2 HP.", "maxHP"],
                      ["1-UP Deluxe", -1, oneUpSprite, "hp", 1, "Revives a fallen Bro with full HP.", "maxHP"],
                      ["Star Cand", -1, candySprite, "hp", "maxHP", "Fully restores HP and BP for one Bro.", "maxHP"]]

    def playSong(self, introLength, loopLength, song, cont=False, fadein=False, fadeinSpeed=0.05):
        if self.song_playing != song:
            pg.mixer.music.load("music/" + song + ".ogg")
            self.loops = 0

            if cont:
                if self.currentPoint > (introLength + loopLength) * 1000:
                    self.currentPoint -= introLength * 1000
                    while self.currentPoint > loopLength * 1000:
                        self.currentPoint -= loopLength * 1000
                pg.mixer.music.play()
                pg.mixer.music.set_pos(self.currentPoint / 1000)
            else:
                pg.mixer.music.play()
            self.song_playing = song
            if fadein:
                self.volume = 0

        if cont:
            soundPos = ((pg.mixer.music.get_pos() + self.currentPoint) / 1000) - (loopLength * self.loops) - introLength
        else:
            soundPos = (pg.mixer.music.get_pos() / 1000) - (loopLength * self.loops) - introLength

        if not self.pause and self.volume < 1:
            self.volume += fadeinSpeed

        pg.mixer.music.set_volume(self.volume)

        if soundPos > loopLength and pg.mixer.music.get_pos() > 500:
            self.loops += 1
            if cont:
                pg.mixer.music.set_pos(
                    ((pg.mixer.music.get_pos() + self.currentPoint) / 1000) - loopLength * self.loops)
            else:
                pg.mixer.music.set_pos((pg.mixer.music.get_pos() / 1000) - loopLength * self.loops)
            if self.loops == 1:
                print("YEEEEEEEEE")
            else:
                print("YOOOOOOOOO")

    def calculatePlayTime(self):
        self.playtime += 1

        self.playSeconds = self.playtime // fps
        self.playMinutes = self.playSeconds // 60
        self.playHours = self.playMinutes // 60

        if self.playSeconds >= 60:
            self.playSeconds %= 60
        if self.playSeconds < 10 and self.playMinutes >= 1:
            self.playSeconds = "0{0}".format(self.playSeconds)

        if self.playMinutes >= 60:
            self.playMinutes %= 60
        if self.playMinutes == 0:
            self.playMinutes = ""
        elif self.playMinutes < 10 and self.playHours >= 1:
            self.playMinutes = "0{0}:".format(self.playMinutes)
        else:
            self.playMinutes = "{0}:".format(self.playMinutes)

        if self.playHours == 0:
            self.playHours = ""
        else:
            self.playHours = "{0}:".format(self.playHours)

        self.playSeconds = str(self.playSeconds)
        self.playMinutes = str(self.playMinutes)
        self.playHours = str(self.playHours)

        self.displayTime = self.playHours + self.playMinutes + self.playSeconds

    def titleScreen(self):
        if self.player.dead:
            self.player.dead = False
            self.player.stats["hp"] = 1
            self.player.shadow = self.player.shadowFrames["normal"]
            self.player.rect = self.player.shadow.get_rect()
        if self.follower.dead:
            self.follower.dead = False
            self.follower.stats["hp"] = 1
            self.follower.shadow = self.follower.shadowFrames["normal"]
            self.follower.rect = self.follower.shadow.get_rect()

        try:
            with open("saves/File 1.ini"):
                pass
            cont = True
        except:
            try:
                with open("saves/File 2.ini"):
                    pass
                cont = True
            except:
                try:
                    with open("saves/File 3.ini"):
                        pass
                    cont = True
                except:
                    cont = False

        background = pg.image.load("sprites/titleScreen.png").convert_alpha()
        bRect = background.get_rect()
        smal = pg.image.load("sprites/super mario & luigi.png").convert_alpha()
        smalRect = smal.get_rect()
        smalRect.centerx = width / 2
        smalRect.top = 25
        going = True
        fade = Fadeout(self, 0.5)
        fade.room = "Nothing"
        fade.alpha = 255
        time = 0
        clipRect = pg.rect.Rect(0, 0, 0, 300)
        self.room = "Title Screen"
        sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")

        shadow = sheet.getImageName("shadow.png")

        luigiShadowRect = shadow.get_rect()
        luigiLastUpdate = 0
        luigiCounter = 0
        luigiFrames = [sheet.getImageName("luigi_tea_1.png"),
                       sheet.getImageName("luigi_tea_2.png"),
                       sheet.getImageName("luigi_tea_3.png"),
                       sheet.getImageName("luigi_tea_4.png"),
                       sheet.getImageName("luigi_tea_5.png"),
                       sheet.getImageName("luigi_tea_6.png"),
                       sheet.getImageName("luigi_tea_7.png"),
                       sheet.getImageName("luigi_tea_8.png"),
                       sheet.getImageName("luigi_tea_9.png"),
                       sheet.getImageName("luigi_tea_10.png"),
                       sheet.getImageName("luigi_tea_11.png"),
                       sheet.getImageName("luigi_tea_12.png"),
                       sheet.getImageName("luigi_tea_13.png"),
                       sheet.getImageName("luigi_tea_14.png"),
                       sheet.getImageName("luigi_tea_15.png"),
                       sheet.getImageName("luigi_tea_16.png"),
                       sheet.getImageName("luigi_tea_17.png"),
                       sheet.getImageName("luigi_tea_18.png"),
                       sheet.getImageName("luigi_tea_19.png"),
                       sheet.getImageName("luigi_tea_20.png"),
                       sheet.getImageName("luigi_tea_21.png"),
                       sheet.getImageName("luigi_tea_22.png"),
                       sheet.getImageName("luigi_tea_23.png"),
                       sheet.getImageName("luigi_tea_24.png"),
                       sheet.getImageName("luigi_tea_25.png"),
                       sheet.getImageName("luigi_tea_26.png"),
                       sheet.getImageName("luigi_tea_27.png"),
                       sheet.getImageName("luigi_tea_28.png"),
                       sheet.getImageName("luigi_tea_29.png"),
                       sheet.getImageName("luigi_tea_30.png"),
                       sheet.getImageName("luigi_tea_31.png"),
                       sheet.getImageName("luigi_tea_32.png"),
                       sheet.getImageName("luigi_tea_33.png"),
                       sheet.getImageName("luigi_tea_34.png"),
                       sheet.getImageName("luigi_tea_35.png"),
                       sheet.getImageName("luigi_tea_36.png"),
                       sheet.getImageName("luigi_tea_37.png"),
                       sheet.getImageName("luigi_tea_38.png"),
                       sheet.getImageName("luigi_tea_39.png"),
                       sheet.getImageName("luigi_tea_40.png"),
                       sheet.getImageName("luigi_tea_41.png"),
                       sheet.getImageName("luigi_tea_42.png"),
                       sheet.getImageName("luigi_tea_43.png"),
                       sheet.getImageName("luigi_tea_44.png"),
                       sheet.getImageName("luigi_tea_45.png"),
                       sheet.getImageName("luigi_tea_46.png"),
                       sheet.getImageName("luigi_tea_47.png"),
                       sheet.getImageName("luigi_tea_48.png"),
                       sheet.getImageName("luigi_tea_49.png"),
                       sheet.getImageName("luigi_tea_50.png"),
                       sheet.getImageName("luigi_tea_51.png"),
                       sheet.getImageName("luigi_tea_52.png")]
        luigiRect = luigiFrames[0].get_rect()
        luigiRect.center = (871, 595)
        luigiShadowRect.centery = luigiRect.bottom - 10
        luigiShadowRect.centerx = luigiRect.centerx

        marioShadowRect = shadow.get_rect()
        marioLastUpdate = 0
        marioCounter = 0
        marioFrames = [sheet.getImageName("mario_talking_left_1.png"),
                       sheet.getImageName("mario_talking_left_2.png"),
                       sheet.getImageName("mario_talking_left_3.png"),
                       sheet.getImageName("mario_talking_left_4.png"),
                       sheet.getImageName("mario_talking_left_5.png"),
                       sheet.getImageName("mario_talking_left_6.png"),
                       sheet.getImageName("mario_talking_left_7.png"),
                       sheet.getImageName("mario_talking_left_8.png"),
                       sheet.getImageName("mario_talking_left_9.png"),
                       sheet.getImageName("mario_talking_left_10.png"),
                       sheet.getImageName("mario_talking_left_11.png"),
                       sheet.getImageName("mario_talking_left_12.png"),
                       sheet.getImageName("mario_talking_left_13.png"),
                       sheet.getImageName("mario_talking_left_14.png"),
                       sheet.getImageName("mario_talking_left_15.png"),
                       sheet.getImageName("mario_talking_left_16.png"),
                       sheet.getImageName("mario_talking_left_17.png"),
                       sheet.getImageName("mario_talking_left_18.png"),
                       sheet.getImageName("mario_talking_left_19.png"),
                       sheet.getImageName("mario_talking_left_20.png"),
                       sheet.getImageName("mario_talking_left_21.png"),
                       sheet.getImageName("mario_talking_left_22.png"),
                       sheet.getImageName("mario_talking_left_23.png"),
                       sheet.getImageName("mario_talking_left_24.png"),
                       sheet.getImageName("mario_talking_left_25.png"),
                       sheet.getImageName("mario_talking_left_26.png"),
                       sheet.getImageName("mario_talking_left_27.png"),
                       sheet.getImageName("mario_talking_left_28.png"),
                       sheet.getImageName("mario_talking_left_29.png"),
                       sheet.getImageName("mario_talking_left_30.png"),
                       sheet.getImageName("mario_talking_left_31.png"),
                       sheet.getImageName("mario_talking_left_32.png"),
                       sheet.getImageName("mario_talking_left_33.png")]
        marioRect = marioFrames[0].get_rect()
        marioRect.center = (width / 2 + 50, 495)
        marioShadowRect.centery = marioRect.bottom - 10
        marioShadowRect.centerx = marioRect.centerx

        sheet = spritesheet("sprites/peach.png", "sprites/peach.xml")
        peachShadow = sheet.getImageName("shadow.png")
        peachShadowRect = peachShadow.get_rect()
        peachLastUpdate = 0
        peachCounter = 0
        peachFrames = [sheet.getImageName("peach_talking_right_1.png"),
                       sheet.getImageName("peach_talking_right_2.png"),
                       sheet.getImageName("peach_talking_right_3.png"),
                       sheet.getImageName("peach_talking_right_4.png"),
                       sheet.getImageName("peach_talking_right_5.png"),
                       sheet.getImageName("peach_talking_right_6.png"),
                       sheet.getImageName("peach_talking_right_7.png"),
                       sheet.getImageName("peach_talking_right_8.png"),
                       sheet.getImageName("peach_talking_right_9.png"),
                       sheet.getImageName("peach_talking_right_10.png"),
                       sheet.getImageName("peach_talking_right_11.png"),
                       sheet.getImageName("peach_talking_right_12.png"),
                       sheet.getImageName("peach_talking_right_13.png"),
                       sheet.getImageName("peach_talking_right_14.png"),
                       sheet.getImageName("peach_talking_right_15.png"),
                       sheet.getImageName("peach_talking_right_16.png")]
        peachRect = peachFrames[0].get_rect()
        peachRect.centerx = width / 2 - 50
        peachRect.bottom = marioRect.bottom
        peachShadowRect.centery = peachRect.bottom - 15
        peachShadowRect.centerx = peachRect.centerx - 3

        select = 0

        cursor = Cursor(self, pg.rect.Rect(width / 2 - 120, height / 2 - 50, 0, 0))

        while going:
            self.clock.tick(fps)
            self.playSong(41.868, 33.329, "Title Screen")
            time += 1

            now = pg.time.get_ticks()
            if now - luigiLastUpdate > 75:
                luigiLastUpdate = now
                if luigiCounter < len(luigiFrames):
                    luigiCounter = (luigiCounter + 1) % (len(luigiFrames))
                else:
                    luigiCounter = 0
                bottom = luigiRect.bottom
                centerx = luigiRect.centerx
                luigiRect = luigiFrames[luigiCounter].get_rect()
                luigiRect.bottom = bottom
                luigiRect.centerx = centerx

            if now - marioLastUpdate > 75:
                marioLastUpdate = now
                if marioCounter < len(marioFrames):
                    marioCounter = (marioCounter + 1) % (len(marioFrames))
                else:
                    marioCounter = 0
                bottom = marioRect.bottom
                right = marioRect.right
                marioRect = marioFrames[marioCounter].get_rect()
                marioRect.bottom = bottom
                marioRect.right = right

            if now - peachLastUpdate > 75:
                peachLastUpdate = now
                if peachCounter < len(peachFrames):
                    peachCounter = (peachCounter + 1) % (len(peachFrames))
                else:
                    peachCounter = 0
                bottom = peachRect.bottom
                centerx = peachRect.centerx
                peachRect = peachFrames[peachCounter].get_rect()
                peachRect.bottom = bottom
                peachRect.centerx = centerx

            if time >= fps * 8.5 and clipRect.width < width:
                clipRect.center = (smalRect.centerx, smalRect.top)
                clipRect.height += 10
                clipRect.width += 10

            self.events()
            for event in self.event:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_w or event.key == pg.K_a:
                        if clipRect.width >= width:
                            if select != 0:
                                select -= 1
                            else:
                                select = 2
                            self.abilityAdvanceSound.play()
                    if event.key == pg.K_s or event.key == pg.K_d:
                        if clipRect.width >= width:
                            if select != 2:
                                select += 1
                            else:
                                select = 0
                            self.abilityAdvanceSound.play()
                    if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                        if clipRect.width < width:
                            clipRect.width = width
                            clipRect.height = height
                            fade.alpha = 0
                        else:
                            if select == 1:
                                if cont:
                                    self.menuChooseSound.play()
                                    going = False
                                else:
                                    self.wrongSound.play()
                            elif select == 2:
                                self.wrongSound.play()
                            else:
                                self.menuChooseSound.play()
                                going = False

            fade.update()
            if select == 0:
                cursor.update(pg.rect.Rect(width / 2 - 120, height / 2 - 75, 0, 0), 60)
            if select == 1:
                cursor.update(pg.rect.Rect(width / 2 - 110, height / 2, 0, 0), 60)
            if select == 2:
                cursor.update(pg.rect.Rect(width / 2 - 100, height / 2 + 200, 0, 0), 60)

            self.screen.fill(black)
            self.screen.blit(background, bRect)
            self.screen.blit(shadow, marioShadowRect)
            self.screen.blit(marioFrames[marioCounter], marioRect)
            self.screen.blit(peachShadow, peachShadowRect)
            self.screen.blit(peachFrames[peachCounter], peachRect)
            luigiRecflectionRect = luigiRect.copy()
            luigiRecflectionRect.top = luigiRect.bottom
            self.blit_alpha(self.screen, pg.transform.flip(luigiFrames[luigiCounter], False, True),
                            luigiRecflectionRect, 100)
            self.screen.blit(shadow, luigiShadowRect)
            self.screen.blit(luigiFrames[luigiCounter], luigiRect)
            self.screen.set_clip(clipRect.left, clipRect.top, clipRect.width, clipRect.height)
            self.screen.blit(smal, smalRect)
            ptext.draw("NEW GAME", (width / 2, height / 2 - 75), surf=self.screen, color=white, owidth=1,
                       fontname=dialogueFont, anchor=(0.5, 0), fontsize=40)
            if cont:
                ptext.draw("CONTINUE", (width / 2, height / 2), surf=self.screen, color=white, owidth=1,
                           fontname=dialogueFont, anchor=(0.5, 0), fontsize=40)
            else:
                ptext.draw("CONTINUE", (width / 2, height / 2), surf=self.screen, color=darkGray, owidth=1,
                           fontname=dialogueFont, anchor=(0.5, 0), fontsize=40)
            ptext.draw("RECORDS", (width / 2, height / 2 + 200), surf=self.screen, color=darkGray, owidth=1,
                       fontname=dialogueFont, anchor=(0.5, 0), fontsize=40)
            ptext.draw(
                "Mario & Luigi is a registered trademark of Nintendo\nPaper Mario is a registered trademark of Nintendo\nThe Legend of Zelda Phantom Hourglass is a registered trademark of Nintendo\nUNDERTALE is a registered trademark of Royal Sciences, LLC",
                (width / 2, height - 60), lineheight=0.8, surf=self.screen, color=white,
                fontname=dialogueFont, anchor=(0.5, 0), fontsize=10, owidth=0.5)
            self.screen.blit(cursor.image, cursor.rect)
            self.screen.set_clip(None)
            self.screen.blit(fade.image, fade.rect)

            pg.display.flip()
        if select == 0:
            fade = Fadeout(self)
            pg.mixer.music.fadeout(1000)
            while True:
                self.clock.tick(fps)

                now = pg.time.get_ticks()
                if now - luigiLastUpdate > 75:
                    luigiLastUpdate = now
                    if luigiCounter < len(luigiFrames):
                        luigiCounter = (luigiCounter + 1) % (len(luigiFrames))
                    else:
                        luigiCounter = 0
                    bottom = luigiRect.bottom
                    centerx = luigiRect.centerx
                    luigiRect = luigiFrames[luigiCounter].get_rect()
                    luigiRect.bottom = bottom
                    luigiRect.centerx = centerx

                if now - marioLastUpdate > 75:
                    marioLastUpdate = now
                    if marioCounter < len(marioFrames):
                        marioCounter = (marioCounter + 1) % (len(marioFrames))
                    else:
                        marioCounter = 0
                    bottom = marioRect.bottom
                    right = marioRect.right
                    marioRect = marioFrames[marioCounter].get_rect()
                    marioRect.bottom = bottom
                    marioRect.right = right

                if now - peachLastUpdate > 75:
                    peachLastUpdate = now
                    if peachCounter < len(peachFrames):
                        peachCounter = (peachCounter + 1) % (len(peachFrames))
                    else:
                        peachCounter = 0
                    bottom = peachRect.bottom
                    centerx = peachRect.centerx
                    peachRect = peachFrames[peachCounter].get_rect()
                    peachRect.bottom = bottom
                    peachRect.centerx = centerx

                self.events()

                fade.update()
                if fade.alpha >= 255:
                    self.screen.fill(black)
                    pg.display.flip()
                    self.newGame()

                if select == 0:
                    cursor.update(pg.rect.Rect(width / 2 - 120, height / 2 - 75, 0, 0), 60)
                if select == 1:
                    cursor.update(pg.rect.Rect(width / 2 - 110, height / 2, 0, 0), 60)
                if select == 2:
                    cursor.update(pg.rect.Rect(width / 2 - 100, height / 2 + 200, 0, 0), 60)

                self.screen.fill(black)
                self.screen.blit(background, bRect)
                self.screen.blit(shadow, marioShadowRect)
                self.screen.blit(marioFrames[marioCounter], marioRect)
                self.screen.blit(peachShadow, peachShadowRect)
                self.screen.blit(peachFrames[peachCounter], peachRect)
                luigiRecflectionRect = luigiRect.copy()
                luigiRecflectionRect.top = luigiRect.bottom
                self.blit_alpha(self.screen, pg.transform.flip(luigiFrames[luigiCounter], False, True),
                                luigiRecflectionRect, 100)
                self.screen.blit(shadow, luigiShadowRect)
                self.screen.blit(luigiFrames[luigiCounter], luigiRect)
                self.screen.set_clip(clipRect.left, clipRect.top, clipRect.width, clipRect.height)
                self.screen.blit(smal, smalRect)
                ptext.draw("NEW GAME", (width / 2, height / 2 - 75), surf=self.screen, color=white, owidth=1,
                           fontname=dialogueFont, anchor=(0.5, 0), fontsize=40)
                if cont:
                    ptext.draw("CONTINUE", (width / 2, height / 2), surf=self.screen, color=white, owidth=1,
                               fontname=dialogueFont, anchor=(0.5, 0), fontsize=40)
                else:
                    ptext.draw("CONTINUE", (width / 2, height / 2), surf=self.screen, color=darkGray, owidth=1,
                               fontname=dialogueFont, anchor=(0.5, 0), fontsize=40)
                ptext.draw("RECORDS", (width / 2, height / 2 + 200), surf=self.screen, color=darkGray, owidth=1,
                           fontname=dialogueFont, anchor=(0.5, 0), fontsize=40)
                ptext.draw(
                    "Mario & Luigi is a registered trademark of Nintendo\nPaper Mario is a registered trademark of Nintendo\nThe Legend of Zelda Phantom Hourglass is a registered trademark of Nintendo\nUNDERTALE is a registered trademark of Royal Sciences, LLC",
                    (width / 2, height - 60), lineheight=0.8, surf=self.screen, color=white,
                    fontname=dialogueFont, anchor=(0.5, 0), fontsize=10, owidth=0.5)
                self.screen.blit(cursor.image, cursor.rect)
                self.screen.set_clip(None)
                self.screen.blit(fade.image, fade.rect)

                pg.display.flip()
        else:
            saves = [SaveSelection(self, 1), SaveSelection(self, 2), SaveSelection(self, 3)]
            select = 0
            going = True
            while going:
                self.clock.tick(fps)

                self.events()
                for event in self.event:
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_a:
                            if select == 0:
                                select = 2
                            else:
                                select -= 1
                            self.abilityAdvanceSound.play()
                        if event.key == pg.K_d:
                            if select == 2:
                                select = 0
                            else:
                                select += 1
                            self.abilityAdvanceSound.play()
                        if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                            self.menuChooseSound.play()
                            going = False

                if select == 0:
                    cursor.update(saves[0].rect, 60)
                elif select == 1:
                    cursor.update(saves[1].rect, 60)
                elif select == 2:
                    cursor.update(saves[2].rect, 60)

                self.screen.fill(black)
                self.screen.blit(background, bRect)
                [save.draw() for save in saves]
                ptext.draw(
                    "Mario & Luigi is a registered trademark of Nintendo\nPaper Mario is a registered trademark of Nintendo\nThe Legend of Zelda Phantom Hourglass is a registered trademark of Nintendo\nUNDERTALE is a registered trademark of Royal Sciences, LLC",
                    (width / 2, height - 60), lineheight=0.8, surf=self.screen, color=white,
                    fontname=dialogueFont, anchor=(0.5, 0), fontsize=10, owidth=0.5)
                self.screen.blit(cursor.image, cursor.rect)
                self.screen.blit(fade.image, fade.rect)

                pg.display.flip()

            fade = Fadeout(self)
            pg.mixer.music.fadeout(1000)

            while True:
                self.clock.tick(fps)

                self.events()

                fade.update()
                if fade.alpha >= 255:
                    self.screen.fill(black)
                    pg.display.flip()
                    self.loadGame(select + 1)

                cursor.update(saves[select].rect, 60)

                self.screen.fill(black)
                self.screen.blit(background, bRect)
                [save.draw() for save in saves]
                ptext.draw(
                    "Mario & Luigi is a registered trademark of Nintendo\nPaper Mario is a registered trademark of Nintendo\nThe Legend of Zelda Phantom Hourglass is a registered trademark of Nintendo\nUNDERTALE is a registered trademark of Royal Sciences, LLC",
                    (width / 2, height - 60), lineheight=0.8, surf=self.screen, color=white,
                    fontname=dialogueFont, anchor=(0.5, 0), fontsize=10, owidth=0.5)
                self.screen.blit(cursor.image, cursor.rect)
                self.screen.blit(fade.image, fade.rect)

                pg.display.flip()

    def newGame(self):
        self.player = Mario(self, 0, 0)
        self.follower = Luigi(self, 0, 0)
        self.leader = "mario"
        #
        # openingText = ["This game includes tutorials for those who\nhave not played this game before."]
        # openingText.append("These are designed to help new players\nwith controls and basic mechanics.")
        # openingText.append("However,/9/6 if you HAVE played this game\nbefore,/9/6 the tutorials might be "
        #                    "more\nannoying than helpful.")
        # openingText.append("/CDo you wish to have tutorials on?\n\a\n\a                 YES                        NO")
        # openingText.append("Recording your choice.../P/P/P Done!")
        # openingText.append("Enjoy!")
        # while pg.mixer.music.get_busy():
        #     pass
        #
        # textbox = TextBox(self, self, openingText, type="board", choice=True, dir="None")
        # options = [pg.rect.Rect(389, 390, 0, 0), pg.rect.Rect(773, 390, 0, 0)]
        # cursor = Cursor(self, options[1])
        # select = 1
        # cursorDraw = True
        #
        # while not textbox.complete:
        #     self.clock.tick(fps)
        #
        #     self.events()
        #
        #     textbox.update()
        #
        #     if textbox.choosing and cursorDraw:
        #         for event in self.event:
        #             if event.type == pg.KEYDOWN:
        #                 if event.key == pg.K_a or event.key == pg.K_d:
        #                     if select == 1:
        #                         select = 0
        #                     elif select == 0:
        #                         select = 1
        #                     self.abilityAdvanceSound.play()
        #                 if event.key == pg.K_m or event.key == pg.K_l:
        #                     self.menuChooseSound.play()
        #                     cursor.kill()
        #                     cursorDraw = False
        #         cursor.update(options[select], 60)
        #
        #     self.screen.fill(black)
        #     textbox.draw()
        #     if textbox.choosing and cursorDraw:
        #         self.screen.blit(cursor.image, cursor.rect)
        #
        #     pg.display.flip()
        #
        # if select == 0:
        #     self.tutorials = True
        # else:
        #     self.tutorials = False
        # 
        # self.map = Map("Bowser's Castle Floor")
        # enemies = []
        # enemiesDisappear = []
        # enemyTextBoxes = []
        #
        # random.seed()
        #
        # iAmount = 20
        # jAmount = 100
        # currentNumber = 0
        #
        # for j in range(jAmount):
        #     for i in range(iAmount):
        #         enemy = random.randrange(0, 59)
        #         if enemy == 0:
        #             enemies.append(PokeyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 1:
        #             enemies.append(KoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 2:
        #             enemies.append(KoopaRC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 3:
        #             enemies.append(BooC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 4:
        #             enemies.append(SpinyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 5:
        #             enemies.append(ShyGuyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 6:
        #             enemies.append(MechaKoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 7:
        #             enemies.append(GoombaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 8:
        #             enemies.append(MonteyMoleC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 9:
        #             enemies.append(GoombaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 10:
        #             enemies.append(KoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 11:
        #             enemies.append(KoopaRC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 12:
        #             enemies.append(BooC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 13:
        #             enemies.append(SpinyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 14:
        #             enemies.append(ShyGuyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 15:
        #             enemies.append(MechaKoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 16:
        #             enemies.append(KoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 17:
        #             enemies.append(KoopaRC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 18:
        #             enemies.append(BooC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 19:
        #             enemies.append(SpinyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 20:
        #             enemies.append(ShyGuyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 21:
        #             enemies.append(MechaKoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 22:
        #             enemies.append(GoombaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 23:
        #             enemies.append(MonteyMoleC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 24:
        #             enemies.append(GoombaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 25:
        #             enemies.append(KoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 26:
        #             enemies.append(KoopaRC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 27:
        #             enemies.append(BooC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 28:
        #             enemies.append(SpinyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 29:
        #             enemies.append(ShyGuyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 30:
        #             enemies.append(MechaKoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 31:
        #             enemies.append(KoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 32:
        #             enemies.append(KoopaRC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 33:
        #             enemies.append(BooC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 34:
        #             enemies.append(SpinyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 35:
        #             enemies.append(ShyGuyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 36:
        #             enemies.append(MechaKoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 37:
        #             enemies.append(GoombaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 38:
        #             enemies.append(MonteyMoleC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 39:
        #             enemies.append(GoombaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 40:
        #             enemies.append(KoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 41:
        #             enemies.append(KoopaRC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 42:
        #             enemies.append(BooC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 43:
        #             enemies.append(SpinyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 44:
        #             enemies.append(ShyGuyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 45:
        #             enemies.append(MechaKoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 46:
        #             enemies.append(KoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 47:
        #             enemies.append(KoopaRC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 48:
        #             enemies.append(BooC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 49:
        #             enemies.append(SpinyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 50:
        #             enemies.append(ShyGuyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 51:
        #             enemies.append(MechaKoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 52:
        #             enemies.append(GoombaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 53:
        #             enemies.append(MonteyMoleC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 54:
        #             enemies.append(GoombaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 55:
        #             enemies.append(KoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 56:
        #             enemies.append(KoopaRC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 57:
        #             enemies.append(BooC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 58:
        #             enemies.append(SpinyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 59:
        #             enemies.append(ShyGuyC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         elif enemy == 60:
        #             enemies.append(MechaKoopaC(((((jAmount - j) / jAmount) * self.map.width), ((i + 1) / 20) * self.map.height)))
        #         enemiesDisappear.append(LineFlipDisappear(self, enemies[-1].images[0], enemies[-1].rect.center))
        #         currentNumber += 1
        #         self.events()
        #
        #         self.screen.fill(black)
        #
        #         pg.draw.rect(self.screen, darkGray, pg.rect.Rect(40, 80, width - 80, 40))
        #         pg.draw.rect(self.screen, red, pg.rect.Rect(40, 80, (width - 80) * (currentNumber / (iAmount * jAmount)), 40))
        #         pg.draw.rect(self.screen, darkGray, pg.rect.Rect(40, 80, width - 80, 40), 5)
        #
        #         pg.display.flip()
        #
        # fade = Fadeout(self, 0.5)
        # fade.alpha = 255
        # self.room = "cutscene"
        # self.map = Map("Mario's House", True)
        # self.camera = Camera(self, self.map.width, self.map.height)
        # cameraRect = CameraRect()
        # cameraRect.update(pg.rect.Rect(376, 342, 0, 0), 1)
        #
        # sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")
        # mario = sheet.getImageName("mario_sleeping.png")
        # luigi = sheet.getImageName("luigi_sleeping.png")
        # marioShadowSprite = sheet.getImageName("shadow.png")
        # luigiShadowSprite = sheet.getImageName("shadow.png")
        # mRect = mario.get_rect()
        # lRect = luigi.get_rect()
        # mRect.center = (446, 224)
        # lRect.center = (303, 229)
        # self.camera.update(cameraRect.rect)
        #
        # while fade.alpha > 0:
        #     self.playSong(8.081, 32.578, "Mario Bros House")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     fade.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(mario,  self.camera.offset(mRect))
        #     self.screen.blit(luigi,  self.camera.offset(lRect))
        #     self.screen.blit(fade.image, fade.rect)
        #
        #     pg.display.flip()
        #
        # time.sleep(2)
        # self.playtime += fps * 2
        #
        # sheet = spritesheet("sprites/toads.png", "sprites/toads.xml")
        #
        # toadSprites = [sheet.getImageName("toad_freakout_left_1.png"),
        #                sheet.getImageName("toad_freakout_left_2.png"),
        #                sheet.getImageName("toad_freakout_left_3.png"),
        #                sheet.getImageName("toad_freakout_left_4.png"),
        #                sheet.getImageName("toad_freakout_left_5.png"),
        #                sheet.getImageName("toad_freakout_left_6.png"),
        #                sheet.getImageName("toad_freakout_left_7.png"),
        #                sheet.getImageName("toad_freakout_left_8.png"),
        #                sheet.getImageName("toad_freakout_left_9.png"),
        #                sheet.getImageName("toad_freakout_left_11.png"),
        #                sheet.getImageName("toad_freakout_left_12.png"),
        #                sheet.getImageName("toad_freakout_left_13.png"),
        #                sheet.getImageName("toad_freakout_left_14.png"),
        #                sheet.getImageName("toad_freakout_left_15.png"),
        #                sheet.getImageName("toad_freakout_left_16.png"),
        #                sheet.getImageName("toad_freakout_left_17.png"),
        #                sheet.getImageName("toad_freakout_left_18.png"),
        #                sheet.getImageName("toad_freakout_left_19.png"),
        #                sheet.getImageName("toad_freakout_left_20.png"),
        #                sheet.getImageName("toad_freakout_left_21.png"),
        #                sheet.getImageName("toad_freakout_left_22.png"),
        #                sheet.getImageName("toad_freakout_left_23.png"),
        #                sheet.getImageName("toad_freakout_left_24.png"),
        #                sheet.getImageName("toad_freakout_left_25.png"),
        #                sheet.getImageName("toad_freakout_left_26.png"),
        #                sheet.getImageName("toad_freakout_left_27.png"),
        #                sheet.getImageName("toad_freakout_left_28.png"),
        #                sheet.getImageName("toad_freakout_left_29.png"),
        #                sheet.getImageName("toad_freakout_left_30.png"),
        #                sheet.getImageName("toad_freakout_left_31.png"),
        #                sheet.getImageName("toad_freakout_left_32.png"),
        #                sheet.getImageName("toad_freakout_left_33.png"),
        #                sheet.getImageName("toad_freakout_left_34.png"),
        #                sheet.getImageName("toad_freakout_left_35.png"),
        #                sheet.getImageName("toad_freakout_left_36.png"),
        #                sheet.getImageName("toad_freakout_left_37.png"),
        #                sheet.getImageName("toad_freakout_left_38.png"),
        #                sheet.getImageName("toad_freakout_left_39.png"),
        #                sheet.getImageName("toad_freakout_left_40.png")]
        # toadShadow = sheet.getImageName("shadow.png")
        # toadFrame = 0
        # toadRect = toadSprites[toadFrame].get_rect()
        # toadShadowRect = toadShadow.get_rect()
        # toadShadowRect.center = (1180, 637)
        # toadRect.centerx = toadShadowRect.centerx - 5
        # toadRect.bottom = toadShadowRect.bottom - 5
        # toadLastUpdate = 0
        #
        # while toadShadowRect.centerx > 924:
        #     now = pg.time.get_ticks()
        #     if now - toadLastUpdate > 10:
        #         toadLastUpdate = now
        #         if toadFrame < len(toadSprites):
        #             toadFrame = (toadFrame + 1) % (len(toadSprites))
        #         else:
        #             toadFrame = 0
        #         bottom = toadRect.bottom
        #         centerx = toadRect.centerx
        #         toadRect = toadSprites[toadFrame].get_rect()
        #         toadRect.bottom = bottom
        #         toadRect.centerx = centerx
        #
        #     self.playSong(8.081, 32.578, "Mario Bros House")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     toadShadowRect.centerx -= 10
        #     toadRect.centerx = toadShadowRect.centerx + 5
        #     toadRect.bottom = toadShadowRect.bottom - 5
        #     cameraRect.update(toadShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(toadShadow, self.camera.offset(toadShadowRect))
        #     self.screen.blit(toadSprites[toadFrame], self.camera.offset(toadRect))
        #     self.screen.blit(self.map.foreground, self.camera.offset(self.map.rect))
        #
        #     pg.display.flip()
        #
        # text = ["M-/9/6M-/9/6M-/9/6M-/9/6M-/9/6M-/9/6M-/p<<RMARIO>>!/P\nL-/9/6L-/9/6L-/9/6L-/9/6L-/9/6L-/9/6L-/p<<GLUIGI>>!/P\nWAKE UP!/P NOW!"]
        # self.imgRect = toadRect
        # textbox = TextBox(self, self, text)
        #
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     if now - toadLastUpdate > 10:
        #         toadLastUpdate = now
        #         if toadFrame < len(toadSprites):
        #             toadFrame = (toadFrame + 1) % (len(toadSprites))
        #         else:
        #             toadFrame = 0
        #         bottom = toadRect.bottom
        #         centerx = toadRect.centerx
        #         toadRect = toadSprites[toadFrame].get_rect()
        #         toadRect.bottom = bottom
        #         toadRect.centerx = centerx
        #
        #     self.playSong(8.081, 32.578, "Mario Bros House")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     toadRect.centerx = toadShadowRect.centerx + 5
        #     toadRect.bottom = toadShadowRect.bottom - 5
        #     textbox.update()
        #     cameraRect.update(toadShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(toadShadow, self.camera.offset(toadShadowRect))
        #     self.screen.blit(toadSprites[toadFrame], self.camera.offset(toadRect))
        #     self.screen.blit(self.map.foreground, self.camera.offset(self.map.rect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")
        #
        # mario = sheet.getImageName("mario_jumping_up_down.png")
        # luigi = sheet.getImageName("luigi_jumping_up_down.png")
        #
        # marioShadowRect = marioShadowSprite.get_rect()
        # luigiShadowRect = luigiShadowSprite.get_rect()
        #
        # luigiShadowRect.center = (304, 324)
        # marioShadowRect.center = (445, 324)
        #
        # self.jumpSound.play()
        #
        # playedJumpSound = False
        # marioJumpTimer = 0
        # luigiJumpTimer = 0
        #
        # marioAirTimer = 0
        # luigiAirTimer = 0
        #
        # marioJumped = False
        # luigiJumped = False
        #
        # marioGoing = "up"
        # luigiGoing = "up"
        #
        # while lRect.bottom != luigiShadowRect.bottom - 5:
        #     now = pg.time.get_ticks()
        #     if now - toadLastUpdate > 10:
        #         toadLastUpdate = now
        #         if toadFrame < len(toadSprites):
        #             toadFrame = (toadFrame + 1) % (len(toadSprites))
        #         else:
        #             toadFrame = 0
        #         bottom = toadRect.bottom
        #         centerx = toadRect.centerx
        #         toadRect = toadSprites[toadFrame].get_rect()
        #         toadRect.bottom = bottom
        #         toadRect.centerx = centerx
        #
        #     self.playSong(8.081, 32.578, "Mario Bros House")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if marioShadowRect.centery < 708:
        #         marioShadowRect.centery += 10
        #
        #     if not marioJumped:
        #         if marioJumpTimer < jumpHeight + 3 and marioAirTimer == 0:
        #             marioJumpTimer += 0.9
        #         elif marioJumpTimer >= jumpHeight + 3:
        #             marioAirTimer += 1
        #         if marioAirTimer >= airTime and marioJumpTimer != 0:
        #             marioJumpTimer -= 0.5
        #             marioGoing = "down"
        #         if marioJumpTimer <= 0 and marioAirTimer != 0:
        #             marioAirTimer = 0
        #             marioJumped = True
        #         jumpOffset = marioJumpTimer * (jumpHeight + 3)
        #         mRect.bottom = (marioShadowRect.bottom - 5) - jumpOffset
        #
        #         if marioGoing == "down":
        #             mario = sheet.getImageName("mario_jumping_down_down.png")
        #     else:
        #         mRect.bottom = marioShadowRect.bottom - 5
        #         mario = sheet.getImageName("mario_standing_down.png")
        #
        #     if not luigiJumped:
        #         if luigiJumpTimer < jumpHeight + 3 and luigiAirTimer == 0:
        #             luigiJumpTimer += 0.9
        #         elif luigiJumpTimer >= jumpHeight + 3:
        #             luigiAirTimer += 1
        #         if luigiAirTimer >= airTime and luigiJumpTimer != 0:
        #             luigiJumpTimer -= 0.5
        #             luigiGoing = "down"
        #         if luigiJumpTimer <= 0 and luigiAirTimer != 0:
        #             luigiAirTimer = 0
        #             luigiJumped = True
        #         jumpOffset = marioJumpTimer * (jumpHeight + 3)
        #         lRect.bottom = (luigiShadowRect.bottom - 5) - jumpOffset
        #
        #         if luigiGoing == "down":
        #             luigi = sheet.getImageName("luigi_jumping_down_down.png")
        #     else:
        #         luigi = sheet.getImageName("luigi_standing_right.png")
        #         lRect = luigi.get_rect()
        #         lRect.bottom = luigiShadowRect.bottom - 5
        #         lRect.centerx = luigiShadowRect.centerx
        #
        #     if luigiShadowRect.centery < 708 and marioShadowRect.centery > 454:
        #         if not playedJumpSound:
        #             self.jumpSound.play()
        #             playedJumpSound = True
        #         luigiShadowRect.centery += 10
        #
        #     toadRect.centerx = toadShadowRect.centerx + 5
        #     toadRect.bottom = toadShadowRect.bottom - 5
        #     cameraRect.update(toadShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(toadShadow, self.camera.offset(toadShadowRect))
        #     self.screen.blit(toadSprites[toadFrame], self.camera.offset(toadRect))
        #     self.screen.blit(self.map.foreground, self.camera.offset(self.map.rect))
        #
        #     pg.display.flip()
        #
        # mario = sheet.getImageName("mario_standing_right.png")
        # text = ["It's sh-/9/6sh-/9/6sh-/9/6sh-/9/6shocking.../P\nM-/9/6M-/9/6Mushroom Castle.../p RAIDED!/P\nP-/9/6P-/9/6Princess Peach.../p STOLEN!",
        #         "It c-/9/6c-/9/6can only be the work of/p \nth-/9/6th-/9/6that <<RGuy>>!/P That B-/9/6B-/9/6<<RBad guy>>!",
        #         "Y-/9/6y-/9/6you know what to do!/P\nYou'll have to sneak into his castle\nand rescue the princes!"]
        #
        # for i in range(fps // 2):
        #     now = pg.time.get_ticks()
        #     if now - toadLastUpdate > 10:
        #         toadLastUpdate = now
        #         if toadFrame < len(toadSprites):
        #             toadFrame = (toadFrame + 1) % (len(toadSprites))
        #         else:
        #             toadFrame = 0
        #         bottom = toadRect.bottom
        #         centerx = toadRect.centerx
        #         toadRect = toadSprites[toadFrame].get_rect()
        #         toadRect.bottom = bottom
        #         toadRect.centerx = centerx
        #
        #     self.playSong(8.081, 32.578, "Mario Bros House")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     toadRect.centerx = toadShadowRect.centerx + 5
        #     toadRect.bottom = toadShadowRect.bottom - 5
        #     cameraRect.update(toadShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(toadShadow, self.camera.offset(toadShadowRect))
        #     self.screen.blit(toadSprites[toadFrame], self.camera.offset(toadRect))
        #
        #     pg.display.flip()
        #
        # textbox = TextBox(self, self, text)
        #
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     if now - toadLastUpdate > 10:
        #         toadLastUpdate = now
        #         if toadFrame < len(toadSprites):
        #             toadFrame = (toadFrame + 1) % (len(toadSprites))
        #         else:
        #             toadFrame = 0
        #         bottom = toadRect.bottom
        #         centerx = toadRect.centerx
        #         toadRect = toadSprites[toadFrame].get_rect()
        #         toadRect.bottom = bottom
        #         toadRect.centerx = centerx
        #
        #     self.playSong(8.081, 32.578, "Mario Bros House")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #     textbox.update()
        #
        #     toadRect.centerx = toadShadowRect.centerx + 5
        #     toadRect.bottom = toadShadowRect.bottom - 5
        #     cameraRect.update(toadShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(toadShadow, self.camera.offset(toadShadowRect))
        #     self.screen.blit(toadSprites[toadFrame], self.camera.offset(toadRect))
        #     self.screen.blit(self.map.foreground, self.camera.offset(self.map.rect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # mPoints = []
        # for i in range(fps * 3):
        #     mPoints.append(pt.getPointOnLine(marioShadowRect.centerx, marioShadowRect.centery, 1186, 633, (i / (fps * 3))))
        #
        # lPoints = []
        # for i in range(fps * 4):
        #     lPoints.append(
        #         pt.getPointOnLine(luigiShadowRect.centerx, luigiShadowRect.centery, 1186, 633, (i / (fps * 4))))
        #
        # mario = [sheet.getImageName("mario_walking_right_1.png"),
        #                            sheet.getImageName("mario_walking_right_2.png"),
        #                            sheet.getImageName("mario_walking_right_3.png"),
        #                            sheet.getImageName("mario_walking_right_4.png"),
        #                            sheet.getImageName("mario_walking_right_5.png"),
        #                            sheet.getImageName("mario_walking_right_6.png"),
        #                            sheet.getImageName("mario_walking_right_7.png"),
        #                            sheet.getImageName("mario_walking_right_8.png"),
        #                            sheet.getImageName("mario_walking_right_9.png"),
        #                            sheet.getImageName("mario_walking_right_10.png"),
        #                            sheet.getImageName("mario_walking_right_11.png"),
        #                            sheet.getImageName("mario_walking_right_12.png")]
        #
        # luigi = [sheet.getImageName("luigi_walking_right_1.png"),
        #                            sheet.getImageName("luigi_walking_right_2.png"),
        #                            sheet.getImageName("luigi_walking_right_3.png"),
        #                            sheet.getImageName("luigi_walking_right_4.png"),
        #                            sheet.getImageName("luigi_walking_right_5.png"),
        #                            sheet.getImageName("luigi_walking_right_6.png"),
        #                            sheet.getImageName("luigi_walking_right_7.png"),
        #                            sheet.getImageName("luigi_walking_right_8.png"),
        #                            sheet.getImageName("luigi_walking_right_9.png"),
        #                            sheet.getImageName("luigi_walking_right_10.png"),
        #                            sheet.getImageName("luigi_walking_right_11.png"),
        #                            sheet.getImageName("luigi_walking_right_12.png")]
        #
        # mCounter = 0
        # lCounter = 0
        #
        # mFrame = 3
        # mLastUpdate = 0
        #
        # lFrame = 0
        # lLastUpdate = 0
        #
        # mStepSound = pg.mixer.Sound("sounds/stone footsteps.ogg")
        # lStepSound = pg.mixer.Sound("sounds/stone footsteps.ogg")
        #
        # while lCounter != len(lPoints) - 1:
        #     now = pg.time.get_ticks()
        #     if now - toadLastUpdate > 10:
        #         toadLastUpdate = now
        #         if toadFrame < len(toadSprites):
        #             toadFrame = (toadFrame + 1) % (len(toadSprites))
        #         else:
        #             toadFrame = 0
        #         bottom = toadRect.bottom
        #         centerx = toadRect.centerx
        #         toadRect = toadSprites[toadFrame].get_rect()
        #         toadRect.bottom = bottom
        #         toadRect.centerx = centerx
        #
        #     if now - mLastUpdate > 25:
        #         mLastUpdate = now
        #         if mFrame < len(mario):
        #             mFrame = (mFrame + 1) % (len(mario))
        #         else:
        #             mFrame = 0
        #         bottom = mRect.bottom
        #         centerx = mRect.centerx
        #         mRect = mario[mFrame].get_rect()
        #         mRect.bottom = bottom
        #         mRect.centerx = centerx
        #
        #     if now - lLastUpdate > 25:
        #         lLastUpdate = now
        #         if lFrame < len(luigi):
        #             lFrame = (lFrame + 1) % (len(luigi))
        #         else:
        #             lFrame = 0
        #         bottom = lRect.bottom
        #         centerx = lRect.centerx
        #         lRect = luigi[lFrame].get_rect()
        #         lRect.bottom = bottom
        #         lRect.centerx = centerx
        #
        #     if (lFrame == 0 or lFrame == 6) and now == lLastUpdate:
        #         mStepSound.stop()
        #         pg.mixer.Sound.play(lStepSound)
        #
        #     if (lFrame == 0 or lFrame == 6) and now == mLastUpdate:
        #         lStepSound.stop()
        #         pg.mixer.Sound.play(lStepSound)
        #
        #     self.playSong(8.081, 32.578, "Mario Bros House")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #     textbox.update()
        #
        #     toadRect.centerx = toadShadowRect.centerx + 5
        #     toadRect.bottom = toadShadowRect.bottom - 5
        #     if mCounter < len(mPoints) - 1:
        #         mCounter += 1
        #     marioShadowRect.center = mPoints[mCounter]
        #     if lCounter < len(lPoints) - 1:
        #         lCounter += 1
        #     luigiShadowRect.center = lPoints[lCounter]
        #     mRect.bottom = marioShadowRect.bottom - 5
        #     mRect.centerx = marioShadowRect.centerx
        #     lRect.bottom = luigiShadowRect.bottom - 5
        #     lRect.centerx = luigiShadowRect.centerx
        #     cameraRect.update(toadShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        #
        #     if mCounter == fps * 2:
        #         for i in range(len(toadSprites)):
        #             toadSprites[i] = pg.transform.flip(toadSprites[i], True, False)
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(toadShadow, self.camera.offset(toadShadowRect))
        #     self.screen.blit(toadSprites[toadFrame], self.camera.offset(toadRect))
        #     if mCounter < len(mPoints) - 1:
        #         self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     if mCounter < len(mPoints) - 1:
        #         self.screen.blit(mario[mFrame], self.camera.offset(mRect))
        #     self.screen.blit(luigi[lFrame], self.camera.offset(lRect))
        #     self.screen.blit(self.map.foreground, self.camera.offset(self.map.rect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # fade = Fadeout(self, 2)
        # pg.mixer.music.fadeout(5000)
        #
        # while fade.alpha < 255 or pg.mixer.music.get_busy():
        #     now = pg.time.get_ticks()
        #     if now - toadLastUpdate > 10:
        #         toadLastUpdate = now
        #         if toadFrame < len(toadSprites):
        #             toadFrame = (toadFrame + 1) % (len(toadSprites))
        #         else:
        #             toadFrame = 0
        #         bottom = toadRect.bottom
        #         centerx = toadRect.centerx
        #         toadRect = toadSprites[toadFrame].get_rect()
        #         toadRect.bottom = bottom
        #         toadRect.centerx = centerx
        #
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     toadRect.centerx = toadShadowRect.centerx + 5
        #     toadRect.bottom = toadShadowRect.bottom - 5
        #     cameraRect.update(toadShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     fade.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(toadShadow, self.camera.offset(toadShadowRect))
        #     self.screen.blit(toadSprites[toadFrame], self.camera.offset(toadRect))
        #     self.screen.blit(self.map.foreground, self.camera.offset(self.map.rect))
        #     self.screen.blit(fade.image, fade.rect)
        #
        #     pg.display.flip()
        #
        # time.sleep(2)
        # self.playtime += fps * 2
        #
        # pg.event.clear()
        # self.playSong(12.81, 73.815, "Bowser's Theme")
        # bowserReveal = VideoFileClip("movies/BowserCastleReveal.mp4")
        # if self.fullscreen:
        #     bowserReveal.preview(fps=30, fullscreen=True)
        # else:
        #     bowserReveal.preview(fps=30)
        # self.bowserLaugh.play()
        # self.imgRect = pg.rect.Rect(width / 2, height / 2, 0, 0)
        # textbox = TextBox(self, self, ["/BBWA HA HA HA!"], dir="None")
        #
        # while not textbox.complete:
        #     self.playSong(12.81, 73.815, "Bowser's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     textbox.draw()
        #
        #     pg.display.flip()
        # 
        # self.room = "mario's house"
        # fade = Fadeout(self, 5)
        # fade.alpha = 255
        # self.room = "bowser's castle"
        # 
        # sheet = spritesheet("sprites/bowser.png", "sprites/bowser.xml")
        # 
        # bowser = sheet.getImageName("bowser_standing_down.png")
        # 
        # bowserTalking = [sheet.getImageName("bowser_talking_down_1.png"),
        #                  sheet.getImageName("bowser_talking_down_2.png"),
        #                  sheet.getImageName("bowser_talking_down_3.png"),
        #                  sheet.getImageName("bowser_talking_down_4.png"),
        #                  sheet.getImageName("bowser_talking_down_5.png"),
        #                  sheet.getImageName("bowser_talking_down_6.png"),
        #                  sheet.getImageName("bowser_talking_down_7.png"),
        #                  sheet.getImageName("bowser_talking_down_8.png")]
        # 
        # bowserRect = bowser.get_rect()
        # 
        # bowserShadow = sheet.getImageName("shadow.png")
        # 
        # bowserShadowRect = bowserShadow.get_rect()
        # 
        # bowserShadowRect.center = (804, 1200)
        # bowserRect.bottom = bowserShadowRect.bottom - 10
        # bowserRect.centerx = bowserShadowRect.centerx
        # 
        # self.map = Map("Bowser's Castle")
        # 
        # self.camera = Camera(self, self.map.width, self.map.height)
        # cameraRect = CameraRect()
        # 
        # while fade.alpha > 0:
        #     self.playSong(12.81, 73.815, "Bowser's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     fade.update()
        #     cameraRect.update(bowserShadowRect, 1)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(fade.image, fade.rect)
        # 
        #     pg.display.flip()
        # 
        # self.imgRect = bowserRect
        # text = ["Listen well, my elite minion\ntask force!",
        #         "Today is the day we succesfully\nraid Peach's Castle!/P\nPrincess Peach will be ours!",
        #         "AND,/p today is the day we'll finally\nget rid of Mario for good!"]
        # textbox = TextBox(self, self, text)
        # 
        # bowserLastUpdate = 0
        # bowserFrame = 0
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(12.81, 73.815, "Bowser's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if textbox.talking and textbox.pause == 0:
        #         if now - bowserLastUpdate > 45:
        #             bowserLastUpdate = now
        #             if bowserFrame < len(bowserTalking) - 1:
        #                 bowserFrame = (bowserFrame + 1) % (len(bowserTalking))
        #             else:
        #                 bowserFrame = 0
        #             bottom = bowserRect.bottom
        #             centerx = bowserRect.centerx
        #             bowserRect = bowserTalking[bowserFrame].get_rect()
        #             bowserRect.bottom = bottom
        #             bowserRect.centerx = centerx
        #     elif not textbox.talking:
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser.get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 1)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # self.map = Map("Bowser's Castle floor")
        # self.camera = Camera(self, self.map.width, self.map.height)
        # cameraRect = pg.rect.Rect(self.map.width, self.map.height / 2, 0, 0)
        # 
        # self.crowdSound.play(-1)
        # 
        # while cameraRect.x > 0:
        #     self.playSong(12.81, 73.815, "Bowser's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     num = random.randrange(0, 25)
        #     if num == 10:
        #         num = random.randrange(0, 4)
        #         if num == 0:
        #             enemyTextBoxes.append(MiniTextbox(self, self, ["We're under attack!"], (cameraRect.centerx, random.randrange(50, height - 50))))
        #         elif num == 1:
        #             enemyTextBoxes.append(
        #                 MiniTextbox(self, self, ["Bowser, Bowser, woo!"], (cameraRect.centerx, random.randrange(50, height - 50))))
        #         elif num == 2:
        #             enemyTextBoxes.append(
        #                 MiniTextbox(self, self, ["It's OUR turn!"], (cameraRect.centerx, random.randrange(50, height - 50))))
        #         elif num == 3:
        #             enemyTextBoxes.append(
        #                 MiniTextbox(self, self, ["Who stole my eggs?"], (cameraRect.centerx, random.randrange(50, height - 50))))
        #
        #     for text in enemyTextBoxes:
        #         if text.rect.centerx - cameraRect.centerx > 200:
        #             text.closing = True
        #     [text.update() for text in enemyTextBoxes]
        #     cameraRect.x -= 3
        #     self.camera.update(cameraRect)
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     for enemy in enemies:
        #         if self.camera.offset(enemy.rect).right > 0 and self.camera.offset(enemy.rect).left < width:
        #             enemy.update()
        #             self.screen.blit(enemy.images[enemy.currentFrame], self.camera.offset(enemy.rect))
        #     [text.draw() for text in enemyTextBoxes]
        #
        #     pg.display.flip()
        # 
        # self.crowdSound.set_volume(0.5)
        # for text in enemyTextBoxes:
        #         text.kill()
        # 
        # text = ['''Bwa ha ha!/p\n"We're under attack!"/p\nYou jokers are the best!''']
        # 
        # bowserLastUpdate = 0
        # bowserFrame = 0
        # 
        # self.map = Map("Bowser's Castle")
        # 
        # self.camera = Camera(self, self.map.width, self.map.height)
        # 
        # cameraRect = CameraRect()
        # 
        # sheet = spritesheet("sprites/bowser.png", "sprites/bowser.xml")
        # 
        # bowserTalking = [sheet.getImageName("bowser_laughing_down_1.png"),
        #                  sheet.getImageName("bowser_laughing_down_2.png"),
        #                  sheet.getImageName("bowser_laughing_down_3.png"),
        #                  sheet.getImageName("bowser_laughing_down_4.png"),
        #                  sheet.getImageName("bowser_laughing_down_5.png"),
        #                  sheet.getImageName("bowser_laughing_down_6.png"),
        #                  sheet.getImageName("bowser_laughing_down_7.png"),
        #                  sheet.getImageName("bowser_laughing_down_8.png")]
        # 
        # bowserRect = bowserTalking[0].get_rect()
        # 
        # bowserShadowRect.center = (804, 1200)
        # bowserRect.bottom = bowserShadowRect.bottom - 10
        # bowserRect.centerx = bowserShadowRect.centerx
        # 
        # cameraRect.update(bowserShadowRect, 1)
        # self.camera.update(cameraRect.rect)
        # 
        # self.imgRect = bowserRect
        # 
        # for i in range(1):
        #     self.playSong(12.81, 73.815, "Bowser's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     cameraRect.update(bowserShadowRect, 1)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowserTalking[0], self.camera.offset(bowserRect))
        # 
        #     pg.display.flip()
        # 
        # textbox = TextBox(self, self, text)
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(12.81, 73.815, "Bowser's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if textbox.talking and textbox.pause == 0:
        #         if now - bowserLastUpdate > 45:
        #             bowserLastUpdate = now
        #             if bowserFrame < len(bowserTalking) - 1:
        #                 bowserFrame = (bowserFrame + 1) % (len(bowserTalking))
        #             else:
        #                 bowserFrame = 0
        #             bottom = bowserRect.bottom
        #             centerx = bowserRect.centerx
        #             bowserRect = bowserTalking[bowserFrame].get_rect()
        #             bowserRect.bottom = bottom
        #             bowserRect.centerx = centerx
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 1)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # bowser = sheet.getImageName("bowser_laughing_surprised.png")
        # 
        # bowserRect = bowserTalking[0].get_rect()
        # 
        # bowserRect.bottom = bowserShadowRect.bottom - 10
        # bowserRect.centerx = bowserShadowRect.centerx
        # 
        # self.ding.play()
        # 
        # sheet = spritesheet("sprites/remark bubbles.png", "sprites/remark bubbles.xml")
        # 
        # exclamation = [sheet.getImageName("!_1.png"),
        #                sheet.getImageName("!_2.png"),
        #                sheet.getImageName("!_3.png"),
        #                sheet.getImageName("!_4.png"),
        #                sheet.getImageName("!_5.png"),
        #                sheet.getImageName("!_6.png")]
        # 
        # exCounter = 0
        # 
        # exRect = exclamation[0].get_rect()
        # 
        # exRect.centerx = bowserRect.centerx
        # exRect.bottom = bowserRect.top - 10
        # 
        # for i in range(fps):
        #     now = pg.time.get_ticks()
        #     self.playSong(12.81, 73.815, "Bowser's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if exCounter < len(exclamation) - 1:
        #             exCounter += 1
        #         bottom = exRect.bottom
        #         centerx = exRect.centerx
        #         exRect = exclamation[exCounter].get_rect()
        #         exRect.bottom = bottom
        #         exRect.centerx = centerx
        # 
        #     cameraRect.update(bowserShadowRect, 1)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(exclamation[exCounter], self.camera.offset(exRect))
        # 
        #     pg.display.flip()
        # 
        # sheet = spritesheet("sprites/bowser.png", "sprites/bowser.xml")
        # 
        # bowser = sheet.getImageName("bowser_standing_down.png")
        # 
        # bowserTalking = [sheet.getImageName("bowser_talking_down_1.png"),
        #                  sheet.getImageName("bowser_talking_down_2.png"),
        #                  sheet.getImageName("bowser_talking_down_3.png"),
        #                  sheet.getImageName("bowser_talking_down_4.png"),
        #                  sheet.getImageName("bowser_talking_down_5.png"),
        #                  sheet.getImageName("bowser_talking_down_6.png"),
        #                  sheet.getImageName("bowser_talking_down_7.png"),
        #                  sheet.getImageName("bowser_talking_down_8.png")]
        # 
        # bowserRect = bowser.get_rect()
        # 
        # bowserRect.bottom = bowserShadowRect.bottom - 10
        # bowserRect.centerx = bowserShadowRect.centerx
        # 
        # text = ["Wait-/p\nWho're the hairy guys in the back?", "We have a STRICT shaving policy\naround here!"]
        # 
        # textbox = TextBox(self, self, text)
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(12.81, 73.815, "Bowser's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if textbox.talking and textbox.pause == 0:
        #         if now - bowserLastUpdate > 45:
        #             bowserLastUpdate = now
        #             if bowserFrame < len(bowserTalking) - 1:
        #                 bowserFrame = (bowserFrame + 1) % (len(bowserTalking))
        #             else:
        #                 bowserFrame = 0
        #             bottom = bowserRect.bottom
        #             centerx = bowserRect.centerx
        #             bowserRect = bowserTalking[bowserFrame].get_rect()
        #             bowserRect.bottom = bottom
        #             bowserRect.centerx = centerx
        #     elif not textbox.talking:
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser.get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 1)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")
        # 
        # mario = sheet.getImageName("mario_jumping_up_up.png")
        # luigi = sheet.getImageName("luigi_jumping_up_up.png")
        # 
        # marioShadowSprite = sheet.getImageName("shadow.png")
        # luigiShadowSprite = sheet.getImageName("shadow.png")
        # 
        # marioShadowRect = marioShadowSprite.get_rect()
        # luigiShadowRect = luigiShadowSprite.get_rect()
        # 
        # mRect = mario.get_rect()
        # lRect = luigi.get_rect()
        # 
        # mRect.center = (self.map.width / 2 - 50, self.map.height + 100)
        # lRect.center = (self.map.width / 2 + 50, self.map.height + 100)
        # 
        # luigiShadowRect.center = (self.map.width / 2 + 50, self.map.height + 100)
        # marioShadowRect.center = (self.map.width / 2 - 50, self.map.height + 100)
        # 
        # self.jumpSound.play()
        # 
        # marioJumpTimer = 0
        # luigiJumpTimer = 0
        # 
        # marioAirTimer = 0
        # luigiAirTimer = 0
        # 
        # marioJumped = False
        # luigiJumped = False
        # 
        # marioGoing = "up"
        # luigiGoing = "up"
        # 
        # mFrames = 0
        # lFrames = 0
        # 
        # marioLastUpdate = 0
        # luigiLastUpdate = 0
        # 
        # self.jumpSound.play()
        # 
        # while lRect.bottom != luigiShadowRect.bottom - 5:
        #     now = pg.time.get_ticks()
        #     self.playSong(12.81, 73.815, "Bowser's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if marioShadowRect.centery > self.map.height - 400:
        #         marioShadowRect.centery -= 10
        # 
        #     if not marioJumped:
        #         if marioJumpTimer < jumpHeight + 3 and marioAirTimer == 0:
        #             marioJumpTimer += 0.9
        #         elif marioJumpTimer >= jumpHeight + 3:
        #             marioAirTimer += 1
        #         if marioAirTimer >= airTime and marioJumpTimer != 0:
        #             marioJumpTimer -= 0.5
        #             marioGoing = "down"
        #         if marioJumpTimer <= 0 and marioAirTimer != 0:
        #             marioAirTimer = 0
        #             marioJumped = True
        #         jumpOffset = marioJumpTimer * (jumpHeight + 3)
        #         mRect.bottom = (marioShadowRect.bottom - 5) - jumpOffset
        # 
        #         if marioGoing == "down":
        #             mario = sheet.getImageName("mario_jumping_down_up.png")
        #     if marioJumped:
        #         mario = [sheet.getImageName("mario_fight_up_1.png"),
        #                  sheet.getImageName("mario_fight_up_2.png"),
        #                  sheet.getImageName("mario_fight_up_3.png"),
        #                  sheet.getImageName("mario_fight_up_4.png"),
        #                  sheet.getImageName("mario_fight_up_5.png"),
        #                  sheet.getImageName("mario_fight_up_6.png"),
        #                  sheet.getImageName("mario_fight_up_7.png"),
        #                  sheet.getImageName("mario_fight_up_8.png"),
        #                  sheet.getImageName("mario_fight_up_9.png"),
        #                  sheet.getImageName("mario_fight_up_10.png"),
        #                  sheet.getImageName("mario_fight_up_11.png"),
        #                  sheet.getImageName("mario_fight_up_12.png"),
        #                  sheet.getImageName("mario_fight_up_13.png"),
        #                  sheet.getImageName("mario_fight_up_14.png"),
        #                  sheet.getImageName("mario_fight_up_15.png"),
        #                  sheet.getImageName("mario_fight_up_16.png"),
        #                  sheet.getImageName("mario_fight_up_17.png"),
        #                  sheet.getImageName("mario_fight_up_18.png"),
        #                  sheet.getImageName("mario_fight_up_19.png"),
        #                  sheet.getImageName("mario_fight_up_20.png")]
        #         if now - marioLastUpdate > 45:
        #             marioLastUpdate = now
        #             if mFrames < len(mario):
        #                 mFrames = (mFrames + 1) % (len(mario))
        #             else:
        #                 mFrames = 0
        #             mRect = mario[mFrames].get_rect()
        #             mRect.centerx = marioShadowRect.centerx
        #             mRect.bottom = marioShadowRect.bottom - 5
        # 
        #     if not luigiJumped:
        #         if luigiJumpTimer < jumpHeight + 3 and luigiAirTimer == 0:
        #             luigiJumpTimer += 0.9
        #         elif luigiJumpTimer >= jumpHeight + 3:
        #             luigiAirTimer += 1
        #         if luigiAirTimer >= airTime and luigiJumpTimer != 0:
        #             luigiJumpTimer -= 0.5
        #             luigiGoing = "down"
        #         if luigiJumpTimer <= 0 and luigiAirTimer != 0:
        #             luigiAirTimer = 0
        #             luigiJumped = True
        #         jumpOffset = marioJumpTimer * (jumpHeight + 3)
        #         lRect.bottom = (luigiShadowRect.bottom - 5) - jumpOffset
        # 
        #         if luigiGoing == "down":
        #             luigi = sheet.getImageName("luigi_jumping_down_up.png")
        #     if marioJumped:
        #         luigi = [sheet.getImageName("luigi_fight_up_1.png"),
        #                  sheet.getImageName("luigi_fight_up_2.png"),
        #                  sheet.getImageName("luigi_fight_up_3.png"),
        #                  sheet.getImageName("luigi_fight_up_4.png"),
        #                  sheet.getImageName("luigi_fight_up_5.png"),
        #                  sheet.getImageName("luigi_fight_up_6.png"),
        #                  sheet.getImageName("luigi_fight_up_7.png"),
        #                  sheet.getImageName("luigi_fight_up_8.png"),
        #                  sheet.getImageName("luigi_fight_up_9.png"),
        #                  sheet.getImageName("luigi_fight_up_10.png"),
        #                  sheet.getImageName("luigi_fight_up_11.png"),
        #                  sheet.getImageName("luigi_fight_up_12.png"),
        #                  sheet.getImageName("luigi_fight_up_13.png"),
        #                  sheet.getImageName("luigi_fight_up_14.png"),
        #                  sheet.getImageName("luigi_fight_up_15.png"),
        #                  sheet.getImageName("luigi_fight_up_16.png"),
        #                  sheet.getImageName("luigi_fight_up_17.png"),
        #                  sheet.getImageName("luigi_fight_up_18.png"),
        #                  sheet.getImageName("luigi_fight_up_19.png"),
        #                  sheet.getImageName("luigi_fight_up_20.png"),
        #                  sheet.getImageName("luigi_fight_up_21.png"),
        #                  sheet.getImageName("luigi_fight_up_22.png"),
        #                  sheet.getImageName("luigi_fight_up_23.png"),
        #                  sheet.getImageName("luigi_fight_up_24.png")]
        #         if now - luigiLastUpdate > 45:
        #             luigiLastUpdate = now
        #             if lFrames < len(luigi):
        #                 lFrames = (lFrames + 1) % (len(luigi))
        #             else:
        #                 lFrames = 0
        #             lRect = luigi[lFrames].get_rect()
        #             lRect.centerx = luigiShadowRect.centerx
        #             lRect.bottom = luigiShadowRect.bottom - 5
        # 
        #     if luigiShadowRect.centery > self.map.height - 400:
        #         luigiShadowRect.centery -= 10
        # 
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     if not marioJumped:
        #         self.screen.blit(mario, self.camera.offset(mRect))
        #     else:
        #         self.screen.blit(mario[mFrames], self.camera.offset(mRect))
        # 
        #     if not luigiJumped:
        #         self.screen.blit(luigi, self.camera.offset(lRect))
        #     else:
        #         self.screen.blit(luigi[lFrames], self.camera.offset(lRect))
        # 
        #     pg.display.flip()
        # 
        # bowserChannel = pg.mixer.Channel(5)
        # bowserChannel.play(self.bowserNgha)
        # 
        # sheet = spritesheet("sprites/bowser.png", "sprites/bowser.xml")
        # 
        # bowser = [sheet.getImageName("bowser_angry_down_1.png"),
        #           sheet.getImageName("bowser_angry_down_2.png"),
        #           sheet.getImageName("bowser_angry_down_3.png"),
        #           sheet.getImageName("bowser_angry_down_4.png"),
        #           sheet.getImageName("bowser_angry_down_5.png"),
        #           sheet.getImageName("bowser_angry_down_6.png"),
        #           sheet.getImageName("bowser_angry_down_7.png"),
        #           sheet.getImageName("bowser_angry_down_8.png"),
        #           sheet.getImageName("bowser_angry_down_9.png"),
        #           sheet.getImageName("bowser_angry_down_10.png"),
        #           sheet.getImageName("bowser_angry_down_11.png"),
        #           sheet.getImageName("bowser_angry_down_12.png"),
        #           sheet.getImageName("bowser_angry_down_13.png"),
        #           sheet.getImageName("bowser_angry_down_14.png"),
        #           sheet.getImageName("bowser_angry_down_15.png"),
        #           sheet.getImageName("bowser_angry_down_16.png"),
        #           sheet.getImageName("bowser_angry_down_17.png"),
        #           sheet.getImageName("bowser_angry_down_18.png"),
        #           sheet.getImageName("bowser_angry_down_19.png"),
        #           sheet.getImageName("bowser_angry_down_20.png"),
        #           sheet.getImageName("bowser_angry_down_21.png"),
        #           sheet.getImageName("bowser_angry_down_22.png"),
        #           sheet.getImageName("bowser_angry_down_23.png"),
        #           sheet.getImageName("bowser_angry_down_24.png")]
        # 
        # while bowserChannel.get_busy():
        #     now = pg.time.get_ticks()
        #     self.playSong(12.81, 73.815, "Bowser's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if bowserFrame < len(bowser) - 1:
        #             bowserFrame = (bowserFrame + 1) % (len(bowser))
        #         else:
        #             bowserFrame = 0
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser[bowserFrame].get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     if now - marioLastUpdate > 45:
        #         marioLastUpdate = now
        #         if mFrames < len(mario):
        #             mFrames = (mFrames + 1) % (len(mario))
        #         else:
        #             mFrames = 0
        #         mRect = mario[mFrames].get_rect()
        #         mRect.centerx = marioShadowRect.centerx
        #         mRect.bottom = marioShadowRect.bottom - 5
        # 
        #     if now - luigiLastUpdate > 45:
        #         luigiLastUpdate = now
        #         if lFrames < len(luigi):
        #             lFrames = (lFrames + 1) % (len(luigi))
        #         else:
        #             lFrames = 0
        #         lRect = luigi[lFrames].get_rect()
        #         lRect.centerx = luigiShadowRect.centerx
        #         lRect.bottom = luigiShadowRect.bottom - 5
        # 
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser[bowserFrame], self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(mario[mFrames], self.camera.offset(mRect))
        #     self.screen.blit(luigi[lFrames], self.camera.offset(lRect))
        # 
        #     pg.display.flip()
        # 
        # bowserChannel.play(self.bowserMario)
        # 
        # while bowserChannel.get_busy():
        #     now = pg.time.get_ticks()
        #     self.playSong(12.81, 73.815, "Bowser's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if bowserFrame < len(bowser) - 1:
        #             bowserFrame = (bowserFrame + 1) % (len(bowser))
        #         else:
        #             bowserFrame = 0
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser[bowserFrame].get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     if now - marioLastUpdate > 45:
        #         marioLastUpdate = now
        #         if mFrames < len(mario):
        #             mFrames = (mFrames + 1) % (len(mario))
        #         else:
        #             mFrames = 0
        #         mRect = mario[mFrames].get_rect()
        #         mRect.centerx = marioShadowRect.centerx
        #         mRect.bottom = marioShadowRect.bottom - 5
        # 
        #     if now - luigiLastUpdate > 45:
        #         luigiLastUpdate = now
        #         if lFrames < len(luigi):
        #             lFrames = (lFrames + 1) % (len(luigi))
        #         else:
        #             lFrames = 0
        #         lRect = luigi[lFrames].get_rect()
        #         lRect.centerx = luigiShadowRect.centerx
        #         lRect.bottom = luigiShadowRect.bottom - 5
        # 
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser[bowserFrame], self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(mario[mFrames], self.camera.offset(mRect))
        #     self.screen.blit(luigi[lFrames], self.camera.offset(lRect))
        # 
        #     pg.display.flip()
        # 
        # text = ["<<RMARIO>>!/p <<GGREEN 'STACHE>>!/p\nWhat are you doing here?",
        #         "Even for you, this is a new low,/9/6\nattacking me before-/9/6/S"]
        # 
        # textbox = TextBox(self, self, text)
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(12.81, 73.815, "Bowser's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if bowserFrame < len(bowser) - 1:
        #             bowserFrame = (bowserFrame + 1) % (len(bowser))
        #         else:
        #             bowserFrame = 0
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser[bowserFrame].get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     if now - marioLastUpdate > 45:
        #         marioLastUpdate = now
        #         if mFrames < len(mario):
        #             mFrames = (mFrames + 1) % (len(mario))
        #         else:
        #             mFrames = 0
        #         mRect = mario[mFrames].get_rect()
        #         mRect.centerx = marioShadowRect.centerx
        #         mRect.bottom = marioShadowRect.bottom - 5
        # 
        #     if now - luigiLastUpdate > 45:
        #         luigiLastUpdate = now
        #         if lFrames < len(luigi):
        #             lFrames = (lFrames + 1) % (len(luigi))
        #         else:
        #             lFrames = 0
        #         lRect = luigi[lFrames].get_rect()
        #         lRect.centerx = luigiShadowRect.centerx
        #         lRect.bottom = luigiShadowRect.bottom - 5
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser[bowserFrame], self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(mario[mFrames], self.camera.offset(mRect))
        #     self.screen.blit(luigi[lFrames], self.camera.offset(lRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # sheet = spritesheet("sprites/starlow.png", "sprites/starlow.xml")
        # 
        # starlow = [sheet.getImageName("starlow_right_1.png"),
        #            sheet.getImageName("starlow_right_2.png"),
        #            sheet.getImageName("starlow_right_3.png"),
        #            sheet.getImageName("starlow_right_4.png"),
        #            sheet.getImageName("starlow_right_5.png"),
        #            sheet.getImageName("starlow_right_6.png")]
        # 
        # sShadow = sheet.getImageName("shadow.png")
        # 
        # sRect = starlow[0].get_rect()
        # sShadowRect = sShadow.get_rect()
        # 
        # sShadowRect.center = (-10, marioShadowRect.centery)
        # sRect.centerx = sShadowRect.centerx
        # sRect.bottom = sShadowRect.top - 25
        # 
        # sLastUpdate = 0
        # sFrame = 0
        # 
        # self.imgRect = sRect
        # 
        # textbox = TextBox(self, self, ["/BWAIT FOR ME!"], sound="starlow")
        # 
        # pg.mixer.music.stop()
        # self.crowdSound.stop()
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if bowserFrame < len(bowser) - 1:
        #             bowserFrame = (bowserFrame + 1) % (len(bowser))
        #         else:
        #             bowserFrame = 0
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser[bowserFrame].get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     if now - marioLastUpdate > 45:
        #         marioLastUpdate = now
        #         if mFrames < len(mario):
        #             mFrames = (mFrames + 1) % (len(mario))
        #         else:
        #             mFrames = 0
        #         mRect = mario[mFrames].get_rect()
        #         mRect.centerx = marioShadowRect.centerx
        #         mRect.bottom = marioShadowRect.bottom - 5
        # 
        #     if now - luigiLastUpdate > 45:
        #         luigiLastUpdate = now
        #         if lFrames < len(luigi):
        #             lFrames = (lFrames + 1) % (len(luigi))
        #         else:
        #             lFrames = 0
        #         lRect = luigi[lFrames].get_rect()
        #         lRect.centerx = luigiShadowRect.centerx
        #         lRect.bottom = luigiShadowRect.bottom - 5
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser[bowserFrame], self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(mario[mFrames], self.camera.offset(mRect))
        #     self.screen.blit(luigi[lFrames], self.camera.offset(lRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")
        # 
        # mario = sheet.getImageName("mario_standing_left.png")
        # mRect = mario.get_rect()
        # luigi = sheet.getImageName("luigi_standing_left.png")
        # lRect = luigi.get_rect()
        # 
        # mRect.centerx = marioShadowRect.centerx
        # mRect.bottom = marioShadowRect.bottom - 5
        # 
        # lRect.centerx = luigiShadowRect.centerx
        # lRect.bottom = luigiShadowRect.bottom - 5
        # 
        # self.starlowTwinkle.play()
        # 
        # while sShadowRect.centerx < 620:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if bowserFrame < len(bowser) - 1:
        #             bowserFrame = (bowserFrame + 1) % (len(bowser))
        #         else:
        #             bowserFrame = 0
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser[bowserFrame].get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     if now - sLastUpdate > 45:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     sShadowRect.centerx += 5
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser[bowserFrame], self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        # 
        #     pg.display.flip()
        # 
        # for i in range(int(fps / 5)):
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - bowserLastUpdate > 100:
        #         bowserLastUpdate = now
        #         if bowserFrame < len(bowser) - 1:
        #             bowserFrame = (bowserFrame + 1) % (len(bowser))
        #         else:
        #             bowserFrame = 0
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser[bowserFrame].get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     if now - sLastUpdate > 45:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser[bowserFrame], self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        # 
        #     pg.display.flip()
        # 
        # text = ["Sorry I'm late,/9/6 there was a surprising\namount of traffic for the road\nto Bowser's Castle."]
        # self.imgRect = sRect
        # textbox = TextBox(self, self, text, sound="starlow")
        # 
        # sheet = spritesheet("sprites/starlow.png", "sprites/starlow.xml")
        # 
        # sTalking = [sheet.getImageName("starlow_talking_right_1.png"),
        #             sheet.getImageName("starlow_talking_right_2.png"),
        #             sheet.getImageName("starlow_talking_right_3.png"),
        #             sheet.getImageName("starlow_talking_right_4.png"),
        #             sheet.getImageName("starlow_talking_right_5.png"),
        #             sheet.getImageName("starlow_talking_right_6.png"),
        #             sheet.getImageName("starlow_talking_right_7.png"),
        #             sheet.getImageName("starlow_talking_right_8.png")]
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if bowserFrame < len(bowser) - 1:
        #             bowserFrame = (bowserFrame + 1) % (len(bowser))
        #         else:
        #             bowserFrame = 0
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser[bowserFrame].get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if not textbox.talking:
        #             if sFrame < len(starlow):
        #                 sFrame = (sFrame + 1) % (len(starlow))
        #             else:
        #                 sFrame = 0
        #             sRect = starlow[sFrame % len(starlow)].get_rect()
        #         else:
        #             if sFrame < len(sTalking):
        #                 sFrame = (sFrame + 1) % (len(sTalking))
        #             else:
        #                 sFrame = 0
        #             sRect = sTalking[sFrame].get_rect()
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser[bowserFrame], self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     if not textbox.talking:
        #         try:
        #             self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #         except:
        #             self.screen.blit(starlow[0], self.camera.offset(sRect))
        #     else:
        #         self.screen.blit(sTalking[sFrame], self.camera.offset(sRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # text = ["WAIT!/p Who are you, and how\ndo so many people keep\nbreaking into my castle?"]
        # self.imgRect = bowserRect
        # textbox = TextBox(self, self, text)
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if bowserFrame < len(bowser) - 1:
        #             bowserFrame = (bowserFrame + 1) % (len(bowser))
        #         else:
        #             bowserFrame = 0
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser[bowserFrame].get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser[bowserFrame], self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # sTalking = [sheet.getImageName("starlow_talking_upright_1.png"),
        #             sheet.getImageName("starlow_talking_upright_2.png"),
        #             sheet.getImageName("starlow_talking_upright_3.png"),
        #             sheet.getImageName("starlow_talking_upright_4.png"),
        #             sheet.getImageName("starlow_talking_upright_5.png"),
        #             sheet.getImageName("starlow_talking_upright_6.png"),
        #             sheet.getImageName("starlow_talking_upright_7.png"),
        #             sheet.getImageName("starlow_talking_upright_8.png")]
        # 
        # starlow = [sheet.getImageName("starlow_upright_1.png"),
        #            sheet.getImageName("starlow_upright_2.png"),
        #            sheet.getImageName("starlow_upright_3.png"),
        #            sheet.getImageName("starlow_upright_4.png"),
        #            sheet.getImageName("starlow_upright_5.png"),
        #            sheet.getImageName("starlow_upright_6.png")]
        # 
        # text = ["Woah, woah, woah./p\nThat's a lot of questions to ask\nat once.",
        #         "Starting off with you first question,/p\nI'm Starlow!",
        #         "Representative of the star sprites,\nand the official companion of\nMario & Luigi.",
        #         "And to answer your second question,/p\nyou left the front gate unlocked.",
        #         "Anyways,/p what did bowser do this\ntime?"]
        # self.imgRect = sRect
        # textbox = TextBox(self, self, text, sound="starlow")
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if textbox.page == len(text) - 1:
        #         sTalking = [sheet.getImageName("starlow_talking_right_1.png"),
        #                     sheet.getImageName("starlow_talking_right_2.png"),
        #                     sheet.getImageName("starlow_talking_right_3.png"),
        #                     sheet.getImageName("starlow_talking_right_4.png"),
        #                     sheet.getImageName("starlow_talking_right_5.png"),
        #                     sheet.getImageName("starlow_talking_right_6.png"),
        #                     sheet.getImageName("starlow_talking_right_7.png"),
        #                     sheet.getImageName("starlow_talking_right_8.png")]
        # 
        #         starlow = [sheet.getImageName("starlow_right_1.png"),
        #                    sheet.getImageName("starlow_right_2.png"),
        #                    sheet.getImageName("starlow_right_3.png"),
        #                    sheet.getImageName("starlow_right_4.png"),
        #                    sheet.getImageName("starlow_right_5.png"),
        #                    sheet.getImageName("starlow_right_6.png")]
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if bowserFrame < len(bowser) - 1:
        #             bowserFrame = (bowserFrame + 1) % (len(bowser))
        #         else:
        #             bowserFrame = 0
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser[bowserFrame].get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if not textbox.talking:
        #             if sFrame < len(starlow):
        #                 sFrame = (sFrame + 1) % (len(starlow))
        #             else:
        #                 sFrame = 0
        #             sRect = starlow[sFrame % len(starlow)].get_rect()
        #         elif textbox.pause == 0:
        #             if sFrame < len(sTalking):
        #                 sFrame = (sFrame + 1) % (len(sTalking))
        #             else:
        #                 sFrame = 0
        #             sRect = sTalking[sFrame].get_rect()
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser[bowserFrame], self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     if not textbox.talking:
        #         try:
        #             self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #         except:
        #             self.screen.blit(starlow[0], self.camera.offset(sRect))
        #     else:
        #         self.screen.blit(sTalking[sFrame], self.camera.offset(sRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # marioChannel = pg.mixer.Channel(5)
        # marioChannel.play(self.marioTalk1)
        # 
        # sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")
        # 
        # mario = [sheet.getImageName("mario_talking_left_1.png"),
        #          sheet.getImageName("mario_talking_left_2.png"),
        #          sheet.getImageName("mario_talking_left_3.png"),
        #          sheet.getImageName("mario_talking_left_4.png"),
        #          sheet.getImageName("mario_talking_left_5.png"),
        #          sheet.getImageName("mario_talking_left_6.png"),
        #          sheet.getImageName("mario_talking_left_7.png"),
        #          sheet.getImageName("mario_talking_left_8.png"),
        #          sheet.getImageName("mario_talking_left_9.png"),
        #          sheet.getImageName("mario_talking_left_10.png"),
        #          sheet.getImageName("mario_talking_left_11.png"),
        #          sheet.getImageName("mario_talking_left_12.png"),
        #          sheet.getImageName("mario_talking_left_13.png"),
        #          sheet.getImageName("mario_talking_left_14.png"),
        #          sheet.getImageName("mario_talking_left_15.png"),
        #          sheet.getImageName("mario_talking_left_16.png"),
        #          sheet.getImageName("mario_talking_left_17.png"),
        #          sheet.getImageName("mario_talking_left_18.png"),
        #          sheet.getImageName("mario_talking_left_19.png"),
        #          sheet.getImageName("mario_talking_left_20.png"),
        #          sheet.getImageName("mario_talking_left_21.png"),
        #          sheet.getImageName("mario_talking_left_22.png"),
        #          sheet.getImageName("mario_talking_left_23.png"),
        #          sheet.getImageName("mario_talking_left_24.png"),
        #          sheet.getImageName("mario_talking_left_25.png"),
        #          sheet.getImageName("mario_talking_left_26.png"),
        #          sheet.getImageName("mario_talking_left_27.png"),
        #          sheet.getImageName("mario_talking_left_28.png"),
        #          sheet.getImageName("mario_talking_left_29.png"),
        #          sheet.getImageName("mario_talking_left_30.png"),
        #          sheet.getImageName("mario_talking_left_31.png"),
        #          sheet.getImageName("mario_talking_left_32.png"),
        #          sheet.getImageName("mario_talking_left_33.png")]
        # 
        # while marioChannel.get_busy():
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if bowserFrame < len(bowser) - 1:
        #             bowserFrame = (bowserFrame + 1) % (len(bowser))
        #         else:
        #             bowserFrame = 0
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser[bowserFrame].get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     if now - marioLastUpdate > 100:
        #         marioLastUpdate = now
        #         if mFrames < len(mario) - 1:
        #             mFrames = (mFrames + 1) % (len(mario))
        #         else:
        #             mFrames = 0
        #         bottom = mRect.bottom
        #         centerx = mRect.centerx
        #         mRect = mario[mFrames].get_rect()
        #         mRect.bottom = bottom
        #         mRect.centerx = centerx
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if not textbox.talking:
        #             if sFrame < len(starlow):
        #                 sFrame = (sFrame + 1) % (len(starlow))
        #             else:
        #                 sFrame = 0
        #             sRect = starlow[sFrame % len(starlow)].get_rect()
        #         elif textbox.pause == 0:
        #             if sFrame < len(sTalking):
        #                 sFrame = (sFrame + 1) % (len(sTalking))
        #             else:
        #                 sFrame = 0
        #             sRect = sTalking[sFrame].get_rect()
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser[bowserFrame], self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(mario[mFrames], self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     if not textbox.talking:
        #         try:
        #             self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #         except:
        #             self.screen.blit(starlow[0], self.camera.offset(sRect))
        #     else:
        #         self.screen.blit(sTalking[sFrame], self.camera.offset(sRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # mario = sheet.getImageName("mario_standing_left.png")
        # 
        # bottom = mRect.bottom
        # centerx = mRect.centerx
        # mRect = mario.get_rect()
        # mRect.bottom = bottom
        # mRect.centerx = centerx
        # 
        # text = ["So, Bowser's kidnapped Peach again,\nhuh?",
        #         "Well, let's stop him!",
        #         "Luigi,/9/6 no offense, but you should\nprobably sit this one out."]
        # self.imgRect = sRect
        # textbox = TextBox(self, self, text, sound="starlow")
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if bowserFrame < len(bowser) - 1:
        #             bowserFrame = (bowserFrame + 1) % (len(bowser))
        #         else:
        #             bowserFrame = 0
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser[bowserFrame].get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if not textbox.talking:
        #             if sFrame < len(starlow):
        #                 sFrame = (sFrame + 1) % (len(starlow))
        #             else:
        #                 sFrame = 0
        #             sRect = starlow[sFrame % len(starlow)].get_rect()
        #         elif textbox.pause == 0:
        #             if sFrame < len(sTalking):
        #                 sFrame = (sFrame + 1) % (len(sTalking))
        #             else:
        #                 sFrame = 0
        #             sRect = sTalking[sFrame].get_rect()
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser[bowserFrame], self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     if not textbox.talking:
        #         try:
        #             self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #         except:
        #             self.screen.blit(starlow[0], self.camera.offset(sRect))
        #     else:
        #         self.screen.blit(sTalking[sFrame], self.camera.offset(sRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # mario = sheet.getImageName("mario_standing_up.png")
        # luigi = sheet.getImageName("luigi_standing_up.png")
        # sheet = spritesheet("sprites/starlow.png", "sprites/starlow.xml")
        # starlow = sheet.getImageName("starlow_upright_1.png")
        # 
        # bottom = mRect.bottom
        # centerx = mRect.centerx
        # mRect = mario.get_rect()
        # mRect.bottom = bottom
        # mRect.centerx = centerx
        # 
        # bottom = lRect.bottom
        # centerx = lRect.centerx
        # lRect = luigi.get_rect()
        # lRect.bottom = bottom
        # lRect.centerx = centerx
        # 
        # self.sprites = []
        # self.sprites.append(EmptyObject(mario, marioShadowSprite, mRect.center, marioShadowRect.center))
        # self.sprites.append(EmptyObject(luigi, luigiShadowSprite, lRect.center, luigiShadowRect.center))
        # self.sprites.append(EmptyObject(starlow, sShadow, sRect.center, sShadowRect.center))
        # self.sprites.append(EmptyObject(bowser[bowserFrame], bowserShadow, bowserRect.center, bowserShadowRect.center))
        # 
        # self.fadeout = pg.sprite.Group()
        # 
        # self.loadBattle("self.loadTutorialBowser()", luigi=False)
        # self.map = Map("bowser's castle")
        # 
        # self.follower.stats["hp"] = self.follower.stats["maxHP"]
        # 
        # sheet = spritesheet("sprites/bowser.png", "sprites/bowser.xml")
        # 
        # bowser = sheet.getImageName("bowser_defeated.png")
        # bowserRect = bowser.get_rect()
        # bowserShadowRect.centery += 50
        # bowserRect.centerx = bowserShadowRect.centerx
        # bowserRect.bottom = bowserShadowRect.bottom
        # 
        # sheet = spritesheet("sprites/starlow.png", "sprites/starlow.xml")
        # 
        # sTalking = [sheet.getImageName("starlow_talking_upright_1.png"),
        #             sheet.getImageName("starlow_talking_upright_2.png"),
        #             sheet.getImageName("starlow_talking_upright_3.png"),
        #             sheet.getImageName("starlow_talking_upright_4.png"),
        #             sheet.getImageName("starlow_talking_upright_5.png"),
        #             sheet.getImageName("starlow_talking_upright_6.png"),
        #             sheet.getImageName("starlow_talking_upright_7.png"),
        #             sheet.getImageName("starlow_talking_upright_8.png")]
        # 
        # starlow = [sheet.getImageName("starlow_upright_1.png"),
        #            sheet.getImageName("starlow_upright_2.png"),
        #            sheet.getImageName("starlow_upright_3.png"),
        #            sheet.getImageName("starlow_upright_4.png"),
        #            sheet.getImageName("starlow_upright_5.png"),
        #            sheet.getImageName("starlow_upright_6.png")]
        # 
        # while len(self.fadeout) > 0:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(sTalking):
        #             sFrame = (sFrame + 1) % (len(sTalking))
        #         else:
        #             sFrame = 0
        #         sRect = sTalking[sFrame].get_rect()
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     self.fadeout.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     try:
        #         self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     except:
        #         self.screen.blit(starlow[0], self.camera.offset(sRect))
        #     self.fadeout.draw(self.screen)
        # 
        #     pg.display.flip()
        # 
        # text = ["Bowser!/p Tell us!/p\nWhere did you put the Princess?"]
        # self.imgRect = sRect
        # textbox = TextBox(self, self, text, sound="starlow")
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if not textbox.talking:
        #             if sFrame < len(starlow):
        #                 sFrame = (sFrame + 1) % (len(starlow))
        #             else:
        #                 sFrame = 0
        #             sRect = starlow[sFrame % len(starlow)].get_rect()
        #         elif textbox.pause == 0:
        #             if sFrame < len(sTalking):
        #                 sFrame = (sFrame + 1) % (len(sTalking))
        #             else:
        #                 sFrame = 0
        #             sRect = sTalking[sFrame].get_rect()
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     if not textbox.talking:
        #         try:
        #             self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #         except:
        #             self.screen.blit(starlow[0], self.camera.offset(sRect))
        #     else:
        #         self.screen.blit(sTalking[sFrame], self.camera.offset(sRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # text = ["I've been trying to tell you...",
        #         "Were were just about to launch our\nattack,/p when <<RMario>> and\n<<GGreen 'Stache>> showed up."]
        # self.imgRect = bowserRect
        # textbox = TextBox(self, self, text)
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     try:
        #         self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     except:
        #         self.screen.blit(starlow[0], self.camera.offset(sRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # text = ["Wait,/9/6 so if YOU didn't kidnap Peach,\nthen who did?"]
        # self.imgRect = sRect
        # textbox = TextBox(self, self, text, sound="starlow")
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if not textbox.talking:
        #             if sFrame < len(starlow):
        #                 sFrame = (sFrame + 1) % (len(starlow))
        #             else:
        #                 sFrame = 0
        #             sRect = starlow[sFrame % len(starlow)].get_rect()
        #         elif textbox.pause == 0:
        #             if sFrame < len(sTalking):
        #                 sFrame = (sFrame + 1) % (len(sTalking))
        #             else:
        #                 sFrame = 0
        #             sRect = sTalking[sFrame].get_rect()
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     if not textbox.talking:
        #         try:
        #             self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #         except:
        #             self.screen.blit(starlow[0], self.camera.offset(sRect))
        #     else:
        #         self.screen.blit(sTalking[sFrame], self.camera.offset(sRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # text = ["/BI HAVE FURY!!!"]
        # self.imgRect = pg.rect.Rect(90, 869, 0, 0)
        # self.fawfulHududu.play()
        # textbox = TextBox(self, self, text, complete=True)
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if not textbox.talking:
        #             if sFrame < len(starlow):
        #                 sFrame = (sFrame + 1) % (len(starlow))
        #             else:
        #                 sFrame = 0
        #             sRect = starlow[sFrame % len(starlow)].get_rect()
        #         elif textbox.pause == 0:
        #             if sFrame < len(sTalking):
        #                 sFrame = (sFrame + 1) % (len(sTalking))
        #             else:
        #                 sFrame = 0
        #             sRect = sTalking[sFrame].get_rect()
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     if not textbox.talking:
        #         try:
        #             self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #         except:
        #             self.screen.blit(starlow[0], self.camera.offset(sRect))
        #     else:
        #         self.screen.blit(sTalking[sFrame], self.camera.offset(sRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # points = []
        # 
        # for i in range(400):
        #     points.append(pt.getPointOnLine(90, 869, 1100, 1200, i / 400))
        # 
        # counter = 0
        # 
        # sheet = spritesheet("sprites/fawful.png", "sprites/fawful.xml")
        # 
        # fTalking = [sheet.getImageName("talking_left_1.png"),
        #             sheet.getImageName("talking_left_2.png"),
        #             sheet.getImageName("talking_left_3.png"),
        #             sheet.getImageName("talking_left_4.png"),
        #             sheet.getImageName("talking_left_5.png"),
        #             sheet.getImageName("talking_left_6.png"),
        #             sheet.getImageName("talking_left_7.png"),
        #             sheet.getImageName("talking_left_8.png")]
        # 
        # platform = [sheet.getImageName("platform_1.png"),
        #             sheet.getImageName("platform_2.png"),
        #             sheet.getImageName("platform_3.png"),
        #             sheet.getImageName("platform_4.png")]
        # 
        # fShadow = sheet.getImageName("shadow.png")
        # 
        # fawful = [sheet.getImageName("laughing_down_1.png"),
        #           sheet.getImageName("laughing_down_2.png"),
        #           sheet.getImageName("laughing_down_3.png"),
        #           sheet.getImageName("laughing_down_4.png")]
        # 
        # pRect = platform[0].get_rect()
        # fShadowRect = fShadow.get_rect()
        # fRect = fawful[0].get_rect()
        # 
        # fLastUpdate = 0
        # fFrame = 0
        # 
        # pLastUpdate = 0
        # pFrame = 0
        # 
        # fShadowRect.centery = 1300
        # 
        # self.fawfulcopterSound.play(-1)
        # 
        # while counter < len(points) - 1:
        #     now = pg.time.get_ticks()
        #     self.playSong(10.88, 30.471, "Fawful's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - fLastUpdate > 75:
        #         fLastUpdate = now
        #         if fFrame < len(fawful):
        #             fFrame = (fFrame + 1) % (len(fawful))
        #         else:
        #             fFrame = 0
        #         fRect = fawful[fFrame].get_rect()
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         pRect = platform[pFrame].get_rect()
        # 
        #     counter += 1
        #     pRect.center = points[counter]
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful[fFrame], self.camera.offset(fRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")
        # mario = sheet.getImageName("mario_standing_right.png")
        # luigi = sheet.getImageName("luigi_standing_right.png")
        # 
        # bottom = mRect.bottom
        # centerx = mRect.centerx
        # mRect = mario.get_rect()
        # mRect.bottom = bottom
        # mRect.centerx = centerx
        # 
        # bottom = lRect.bottom
        # centerx = lRect.centerx
        # lRect = luigi.get_rect()
        # lRect.bottom = bottom
        # lRect.centerx = centerx
        # 
        # sheet = spritesheet("sprites/starlow.png", "sprites/starlow.xml")
        # 
        # starlow = [sheet.getImageName("starlow_right_1.png"),
        #            sheet.getImageName("starlow_right_2.png"),
        #            sheet.getImageName("starlow_right_3.png"),
        #            sheet.getImageName("starlow_right_4.png"),
        #            sheet.getImageName("starlow_right_5.png"),
        #            sheet.getImageName("starlow_right_6.png")]
        # 
        # for i in range(int(fps / 2)):
        #     now = pg.time.get_ticks()
        #     self.playSong(10.88, 30.471, "Fawful's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - fLastUpdate > 75:
        #         fLastUpdate = now
        #         if fFrame < len(fawful):
        #             fFrame = (fFrame + 1) % (len(fawful))
        #         else:
        #             fFrame = 0
        #         fRect = fawful[fFrame].get_rect()
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful[fFrame], self.camera.offset(fRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # sheet = spritesheet("sprites/fawful.png", "sprites/fawful.xml")
        # 
        # fawful = sheet.getImageName("standing_left.png")
        # 
        # self.fawfulcopterSound.fadeout(500)
        # 
        # text = ["Soon is when the Mushroom Kingdom\nwill belong to Fawful!",
        #         "Fawful has surrounded the castle of\nBowser, and the Great King of\nKoopas will begin the crying!",
        #         "Wait.../p It appears that the Koopa\nKing has been defeated!",
        #         "I HAVE CHORTLES!"]
        # 
        # self.imgRect = fRect
        # textbox = TextBox(self, self, text, sound="fawful")
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(10.88, 30.471, "Fawful's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if textbox.talking:
        #         if now - fLastUpdate > 75:
        #             fLastUpdate = now
        #             if textbox.page < len(text) - 1:
        #                 if fFrame < len(fTalking):
        #                     fFrame = (fFrame + 1) % (len(fTalking))
        #                 else:
        #                     fFrame = 0
        #                 fRect = fTalking[fFrame].get_rect()
        #             else:
        #                 fTalking = [sheet.getImageName("laughing_left_1.png"),
        #                             sheet.getImageName("laughing_left_2.png"),
        #                             sheet.getImageName("laughing_left_3.png"),
        #                             sheet.getImageName("laughing_left_4.png")]
        #                 if fFrame < len(fTalking):
        #                     fFrame = (fFrame + 1) % (len(fTalking))
        #                 else:
        #                     fFrame = 0
        #                 fRect = fTalking[fFrame].get_rect()
        #     elif textbox.pause == 0 and textbox.page < len(text) - 1:
        #         fRect = fawful.get_rect()
        #     else:
        #         if now - fLastUpdate > 75:
        #             fLastUpdate = now
        #             fTalking = [sheet.getImageName("laughing_left_1.png"),
        #                         sheet.getImageName("laughing_left_2.png"),
        #                         sheet.getImageName("laughing_left_3.png"),
        #                         sheet.getImageName("laughing_left_4.png")]
        #             if fFrame < len(fTalking):
        #                 fFrame = (fFrame + 1) % (len(fTalking))
        #             else:
        #                 fFrame = 0
        #             fRect = fTalking[fFrame].get_rect()
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     if textbox.talking or textbox.page >= len(text) - 1:
        #         self.screen.blit(fTalking[fFrame], self.camera.offset(fRect))
        #     else:
        #         self.screen.blit(fawful, self.camera.offset(fRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # sheet = spritesheet("sprites/bowser.png", "sprites/bowser.xml")
        # 
        # bowser = sheet.getImageName("bowser_standing_down.png")
        # 
        # bowserTalking = [sheet.getImageName("bowser_talking_down_1.png"),
        #                  sheet.getImageName("bowser_talking_down_2.png"),
        #                  sheet.getImageName("bowser_talking_down_3.png"),
        #                  sheet.getImageName("bowser_talking_down_4.png"),
        #                  sheet.getImageName("bowser_talking_down_5.png"),
        #                  sheet.getImageName("bowser_talking_down_6.png"),
        #                  sheet.getImageName("bowser_talking_down_7.png"),
        #                  sheet.getImageName("bowser_talking_down_8.png")]
        # 
        # bowserRect = bowser.get_rect()
        # 
        # bowserRect.bottom = bowserShadowRect.bottom - 10
        # bowserRect.centerx = bowserShadowRect.centerx
        # 
        # text = ["Wait, did someone ELSE beak in?"]
        # self.imgRect = bowserRect
        # textbox = TextBox(self, self, text)
        # 
        # bowserFrame = 0
        # 
        # fRect = fawful.get_rect()
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(10.88, 30.471, "Fawful's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if textbox.talking:
        #         if now - bowserLastUpdate > 45:
        #             bowserLastUpdate = now
        #             if bowserFrame < len(bowserTalking) - 1:
        #                 bowserFrame = (bowserFrame + 1) % (len(bowserTalking))
        #             else:
        #                 bowserFrame = 0
        #             bowserRect = bowserTalking[bowserFrame].get_rect()
        #     elif textbox.pause == 0:
        #         bowserRect = bowser.get_rect()
        # 
        #     bowserRect.bottom = bowserShadowRect.bottom - 10
        #     bowserRect.centerx = bowserShadowRect.centerx
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # exCounter = 0
        # 
        # exRect = exclamation[0].get_rect()
        # 
        # exRect.centerx = bowserRect.centerx
        # exRect.bottom = bowserRect.top - 10
        # 
        # sheet = spritesheet("sprites/bowser.png", "sprites/bowser.xml")
        # 
        # bowser = sheet.getImageName("bowser_standing_right.png")
        # 
        # self.ding.play()
        # 
        # for i in range(fps):
        #     now = pg.time.get_ticks()
        #     self.playSong(10.88, 30.471, "Fawful's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if exCounter < len(exclamation) - 1:
        #             exCounter += 1
        #         bottom = exRect.bottom
        #         centerx = exRect.centerx
        #         exRect = exclamation[exCounter].get_rect()
        #         exRect.bottom = bottom
        #         exRect.centerx = centerx
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(bowserShadowRect, 1)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(exclamation[exCounter], self.camera.offset(exRect))
        # 
        #     pg.display.flip()
        # 
        # bowser = [sheet.getImageName("bowser_angry_right_1.png"),
        #           sheet.getImageName("bowser_angry_right_2.png"),
        #           sheet.getImageName("bowser_angry_right_3.png"),
        #           sheet.getImageName("bowser_angry_right_4.png"),
        #           sheet.getImageName("bowser_angry_right_5.png"),
        #           sheet.getImageName("bowser_angry_right_6.png"),
        #           sheet.getImageName("bowser_angry_right_7.png"),
        #           sheet.getImageName("bowser_angry_right_8.png"),
        #           sheet.getImageName("bowser_angry_right_9.png"),
        #           sheet.getImageName("bowser_angry_right_10.png"),
        #           sheet.getImageName("bowser_angry_right_11.png"),
        #           sheet.getImageName("bowser_angry_right_12.png"),
        #           sheet.getImageName("bowser_angry_right_13.png"),
        #           sheet.getImageName("bowser_angry_right_14.png"),
        #           sheet.getImageName("bowser_angry_right_15.png"),
        #           sheet.getImageName("bowser_angry_right_16.png"),
        #           sheet.getImageName("bowser_angry_right_17.png"),
        #           sheet.getImageName("bowser_angry_right_18.png"),
        #           sheet.getImageName("bowser_angry_right_19.png"),
        #           sheet.getImageName("bowser_angry_right_20.png"),
        #           sheet.getImageName("bowser_angry_right_21.png"),
        #           sheet.getImageName("bowser_angry_right_22.png"),
        #           sheet.getImageName("bowser_angry_right_23.png"),
        #           sheet.getImageName("bowser_angry_right_24.png")]
        # 
        # text = ["FAWFUL!/p How dare you take Princess\nPeach!/p That's MY thing!"]
        # self.imgRect = bowserRect
        # textbox = TextBox(self, self, text)
        # 
        # self.bowserNgha.play()
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(10.88, 30.471, "Fawful's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if bowserFrame < len(bowser) - 1:
        #             bowserFrame = (bowserFrame + 1) % (len(bowser))
        #         else:
        #             bowserFrame = 0
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser[bowserFrame].get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     if now - fLastUpdate > 75:
        #         fRect = fawful.get_rect()
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser[bowserFrame], self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # text = ["Fawful is not taking the Princess!/p\nNow is the time for the taking of the\nGreat Koopa King's Castle!"]
        # self.imgRect = fRect
        # textbox = TextBox(self, self, text, sound="fawful")
        # 
        # sheet = spritesheet("sprites/fawful.png", "sprites/fawful.xml")
        # 
        # fTalking = [sheet.getImageName("talking_left_1.png"),
        #             sheet.getImageName("talking_left_2.png"),
        #             sheet.getImageName("talking_left_3.png"),
        #             sheet.getImageName("talking_left_4.png"),
        #             sheet.getImageName("talking_left_5.png"),
        #             sheet.getImageName("talking_left_6.png"),
        #             sheet.getImageName("talking_left_7.png"),
        #             sheet.getImageName("talking_left_8.png")]
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(10.88, 30.471, "Fawful's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if textbox.talking:
        #         if now - fLastUpdate > 75:
        #             fLastUpdate = now
        #             if fFrame < len(fTalking):
        #                 fFrame = (fFrame + 1) % (len(fTalking))
        #             else:
        #                 fFrame = 0
        #             fRect = fTalking[fFrame].get_rect()
        #     elif textbox.pause == 0:
        #         fRect = fawful.get_rect()
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if bowserFrame < len(bowser) - 1:
        #             bowserFrame = (bowserFrame + 1) % (len(bowser))
        #         else:
        #             bowserFrame = 0
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser[bowserFrame].get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser[bowserFrame], self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     if textbox.talking:
        #         self.screen.blit(fTalking[fFrame], self.camera.offset(fRect))
        #     else:
        #         self.screen.blit(fawful, self.camera.offset(fRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # text = ["Wait, so if YOU didn't take Peach,\nand I didn't take peach, then who\ndid?",
        #         "Because someone would have to\ntake her for Mario to show up-/9/6/S"]
        # self.imgRect = bowserRect
        # textbox = TextBox(self, self, text)
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(10.88, 30.471, "Fawful's Theme")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - bowserLastUpdate > 45:
        #         bowserLastUpdate = now
        #         if bowserFrame < len(bowser) - 1:
        #             bowserFrame = (bowserFrame + 1) % (len(bowser))
        #         else:
        #             bowserFrame = 0
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser[bowserFrame].get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser[bowserFrame], self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # text = ["/B\a<<RMARIO>>!/P <<GLUIGI>>!",
        #         "/BHELP!"]
        # self.imgRect = pg.rect.Rect(self.map.width / 2, 900, 0, 0)
        # textbox = TextBox(self, self, text)
        # pg.mixer.music.fadeout(2000)
        # 
        # sheet = spritesheet("sprites/bowser.png", "sprites/bowser.xml")
        # 
        # bowser = sheet.getImageName("bowser_standing_right.png")
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     textbox.update()
        #     cameraRect.update(bowserShadowRect, 60)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # bowser = sheet.getImageName("bowser_standing_up.png")
        # 
        # bowserTalking = [sheet.getImageName("bowser_talking_up_1.png"),
        #                  sheet.getImageName("bowser_talking_up_2.png"),
        #                  sheet.getImageName("bowser_talking_up_3.png"),
        #                  sheet.getImageName("bowser_talking_up_4.png"),
        #                  sheet.getImageName("bowser_talking_up_5.png"),
        #                  sheet.getImageName("bowser_talking_up_6.png"),
        #                  sheet.getImageName("bowser_talking_up_7.png"),
        #                  sheet.getImageName("bowser_talking_up_8.png")]
        # 
        # bowserRect = bowser.get_rect()
        # bowserRect.centerx = bowserShadowRect.centerx
        # bowserRect.bottom = bowserShadowRect.bottom + 5
        # 
        # sheet = spritesheet("sprites/fawful.png", "sprites/fawful.xml")
        # 
        # fawful = sheet.getImageName("standing_upright.png")
        # 
        # fTalking = [sheet.getImageName("talking_upleft_1.png"),
        #             sheet.getImageName("talking_upleft_2.png"),
        #             sheet.getImageName("talking_upleft_3.png"),
        #             sheet.getImageName("talking_upleft_4.png"),
        #             sheet.getImageName("talking_upleft_5.png"),
        #             sheet.getImageName("talking_upleft_6.png"),
        #             sheet.getImageName("talking_upleft_7.png"),
        #             sheet.getImageName("talking_upleft_8.png")]
        # 
        # sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")
        # 
        # mario = sheet.getImageName("mario_standing_up.png")
        # 
        # luigi = sheet.getImageName("luigi_standing_up.png")
        # 
        # sheet = spritesheet("sprites/starlow.png", "sprites/starlow.xml")
        # 
        # starlow = [sheet.getImageName("starlow_upright_1.png"),
        #            sheet.getImageName("starlow_upright_2.png"),
        #            sheet.getImageName("starlow_upright_3.png"),
        #            sheet.getImageName("starlow_upright_4.png"),
        #            sheet.getImageName("starlow_upright_5.png"),
        #            sheet.getImageName("starlow_upright_6.png")]
        # 
        # sTalking = [sheet.getImageName("starlow_talking_upright_1.png"),
        #             sheet.getImageName("starlow_talking_upright_2.png"),
        #             sheet.getImageName("starlow_talking_upright_3.png"),
        #             sheet.getImageName("starlow_talking_upright_4.png"),
        #             sheet.getImageName("starlow_talking_upright_5.png"),
        #             sheet.getImageName("starlow_talking_upright_6.png"),
        #             sheet.getImageName("starlow_talking_upright_7.png"),
        #             sheet.getImageName("starlow_talking_upright_8.png")]
        # 
        # while cameraRect.counter != 220:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(self.imgRect, 240)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        # 
        #     pg.display.flip()
        # 
        # sheet = spritesheet("sprites/peach.png", "sprites/peach.xml")
        # 
        # peach = [sheet.getImageName("peach_scared_1.png"),
        #          sheet.getImageName("peach_scared_2.png"),
        #          sheet.getImageName("peach_scared_3.png"),
        #          sheet.getImageName("peach_scared_4.png")]
        # 
        # barrier = pg.image.load("sprites/peach barrier.png").convert_alpha()
        # 
        # peachRect = peach[0].get_rect()
        # bRect = barrier.get_rect()
        # 
        # peachLastUpdate = 0
        # peachFrame = 0
        # 
        # peachRect.center = (self.map.width / 2, 900)
        # bRect.center = (self.map.width / 2, 900)
        # 
        # appear = LineFlipAppear(self, pg.image.load("sprites/peachincage.png").convert_alpha(), (self.map.width / 2, 900))
        # 
        # while not appear.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(self.imgRect, 240)
        #     self.camera.update(cameraRect.rect)
        #     appear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     appear.draw()
        # 
        #     pg.display.flip()
        # 
        # while appear.rect.height > 0:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(self.imgRect, 240)
        #     self.camera.update(cameraRect.rect)
        #     appear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     appear.draw()
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        # 
        #     pg.display.flip()
        # 
        # text = ["Princess Peach?!"]
        # self.imgRect = sRect
        # textbox = TextBox(self, self, text, sound="starlow")
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if not textbox.talking:
        #         if now - sLastUpdate > 100:
        #             sLastUpdate = now
        #             if sFrame < len(starlow):
        #                 sFrame = (sFrame + 1) % (len(starlow))
        #             else:
        #                 sFrame = 0
        #         else:
        #             if sFrame > len(starlow):
        #                 sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #     else:
        #         if now - sLastUpdate > 100:
        #             sLastUpdate = now
        #             if sFrame < len(sTalking):
        #                 sFrame = (sFrame + 1) % (len(sTalking))
        #             else:
        #                 sFrame = 0
        #         else:
        #             if sFrame > len(starlow):
        #                 sFrame = 0
        #         sRect = sTalking[sFrame].get_rect()
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(bRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     appear.update()
        #     textbox.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     if textbox.talking:
        #         self.screen.blit(sTalking[sFrame], self.camera.offset(sRect))
        #     else:
        #         self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     appear.draw()
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # points = []
        # 
        # for i in range(fps):
        #     points.append(pt.getPointOnLine(peachRect.centerx, peachRect.centery, 990, 950, i / fps))
        # 
        # counter = 0
        # 
        # self.imgRect = peachRect
        # 
        # while counter < len(points) - 1:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if not textbox.talking:
        #         if now - sLastUpdate > 100:
        #             sLastUpdate = now
        #             if sFrame < len(starlow):
        #                 sFrame = (sFrame + 1) % (len(starlow))
        #             else:
        #                 sFrame = 0
        #         else:
        #             if sFrame > len(starlow):
        #                 sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #     else:
        #         if now - sLastUpdate > 100:
        #             sLastUpdate = now
        #             if sFrame < len(sTalking):
        #                 sFrame = (sFrame + 1) % (len(sTalking))
        #             else:
        #                 sFrame = 0
        #         else:
        #             if sFrame > len(starlow):
        #                 sFrame = 0
        #         sRect = sTalking[sFrame].get_rect()
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        # 
        #     counter += 1
        # 
        #     peachRect.center = points[counter]
        #     bRect.center = points[counter]
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     if textbox.talking:
        #         self.screen.blit(sTalking[sFrame], self.camera.offset(sRect))
        #     else:
        #         self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # sheet = spritesheet("sprites/count bleck.png", "sprites/count bleck.xml")
        # 
        # bleckIdle = [sheet.getImageName("idle_1.png"),
        #              sheet.getImageName("idle_2.png"),
        #              sheet.getImageName("idle_3.png"),
        #              sheet.getImageName("idle_4.png"),
        #              sheet.getImageName("idle_5.png"),
        #              sheet.getImageName("idle_6.png"),
        #              sheet.getImageName("idle_7.png"),
        #              sheet.getImageName("idle_8.png"),
        #              sheet.getImageName("idle_9.png"),
        #              sheet.getImageName("idle_10.png"),
        #              sheet.getImageName("idle_11.png"),
        #              sheet.getImageName("idle_12.png"),
        #              sheet.getImageName("idle_13.png"),
        #              sheet.getImageName("idle_14.png"),
        #              sheet.getImageName("idle_15.png"),
        #              sheet.getImageName("idle_16.png"),
        #              sheet.getImageName("idle_17.png"),
        #              sheet.getImageName("idle_18.png"),
        #              sheet.getImageName("idle_19.png"),
        #              sheet.getImageName("idle_20.png"),
        #              sheet.getImageName("idle_21.png"),
        #              sheet.getImageName("idle_22.png"),
        #              sheet.getImageName("idle_23.png"),
        #              sheet.getImageName("idle_24.png"),
        #              sheet.getImageName("idle_25.png"),
        #              sheet.getImageName("idle_26.png"),
        #              sheet.getImageName("idle_27.png"),
        #              sheet.getImageName("idle_28.png"),
        #              sheet.getImageName("idle_29.png"),
        #              sheet.getImageName("idle_30.png"),
        #              sheet.getImageName("idle_31.png"),
        #              sheet.getImageName("idle_32.png"),
        #              sheet.getImageName("idle_33.png"),
        #              sheet.getImageName("idle_34.png"),
        #              sheet.getImageName("idle_35.png"),
        #              sheet.getImageName("idle_36.png"),
        #              sheet.getImageName("idle_37.png"),
        #              sheet.getImageName("idle_38.png"),
        #              sheet.getImageName("idle_39.png"),
        #              sheet.getImageName("idle_40.png"),
        #              sheet.getImageName("idle_41.png"),
        #              sheet.getImageName("idle_42.png"),
        #              sheet.getImageName("idle_43.png"),
        #              sheet.getImageName("idle_44.png"),
        #              sheet.getImageName("idle_45.png"),
        #              sheet.getImageName("idle_46.png"),
        #              sheet.getImageName("idle_47.png"),
        #              sheet.getImageName("idle_48.png"),
        #              sheet.getImageName("idle_49.png"),
        #              sheet.getImageName("idle_50.png")]
        # 
        # bleckTalk = [sheet.getImageName("talking_1.png"),
        #              sheet.getImageName("talking_2.png"),
        #              sheet.getImageName("talking_3.png"),
        #              sheet.getImageName("talking_4.png"),
        #              sheet.getImageName("talking_5.png"),
        #              sheet.getImageName("talking_6.png")]
        # 
        # bleckRect = bleckIdle[0].get_rect()
        # bleckRect.center = (self.map.width / 2, 900)
        # 
        # bleckFrame = 0
        # bleckLastUpdate = 0
        # 
        # appear = LineFlipAppear(self, bleckIdle[0], (self.map.width / 2, 900), sound="bleck")
        # 
        # while not appear.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        # 
        #     
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     appear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     appear.draw()
        # 
        #     pg.display.flip()
        # 
        # while appear.rect.height > 0:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        # 
        #     
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     appear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     appear.draw()
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        # 
        #     pg.display.flip()
        # 
        # self.imgRect = bleckRect
        # text = ["/BBLECK!",
        #         "Your princess has been taken.../p\nby Count Bleck!"]
        # textbox = TextBox(self, self, text, dir="up")
        #
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if textbox.startAdvance:
        #         bleckFrame = 23
        #
        #     if textbox.talking:
        #         if now - bleckLastUpdate > 30:
        #             bleckLastUpdate = now
        #             if bleckFrame < len(bleckTalk):
        #                 bleckFrame = (bleckFrame + 1) % (len(bleckTalk))
        #             else:
        #                 bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckTalk[bleckFrame % len(bleckTalk)].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #     else:
        #         if now - bleckLastUpdate > 30:
        #             bleckLastUpdate = now
        #             if bleckFrame < len(bleckIdle):
        #                 bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #             else:
        #                 bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     if textbox.talking:
        #         self.screen.blit(bleckTalk[bleckFrame % len(bleckTalk)], self.camera.offset(bleckRect))
        #     else:
        #         self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # self.imgRect = bowserRect
        #
        # for i in range(round(fps * 0.75)):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # text = ["You.../p Wait, by WHO?!"]
        # textbox = TextBox(self, self, text)
        #
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if textbox.talking and textbox.pause == 0:
        #         if now - bowserLastUpdate > 45:
        #             bowserLastUpdate = now
        #             if bowserFrame < len(bowserTalking) - 1:
        #                 bowserFrame = (bowserFrame + 1) % (len(bowserTalking))
        #             else:
        #                 bowserFrame = 0
        #             bottom = bowserRect.bottom
        #             centerx = bowserRect.centerx
        #             bowserRect = bowserTalking[bowserFrame].get_rect()
        #             bowserRect.bottom = bottom
        #             bowserRect.centerx = centerx
        #     elif not textbox.talking:
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser.get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # self.imgRect = bleckRect
        #
        # for i in range(round(fps * 0.75)):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # text = ["By me... <<RCount Bleck>>!",
        #         "The chosen executor of the\n<<RDark Prognosticus>>... /pis\nCount Bleck!",
        #         "The fine fellow prophesied\nto come to this dimmension.../p\nis also Count Bleck!"]
        # textbox = TextBox(self, self, text)
        #
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if textbox.startAdvance:
        #         bleckFrame = 23
        #
        #     if textbox.talking:
        #         if now - bleckLastUpdate > 30:
        #             bleckLastUpdate = now
        #             if bleckFrame < len(bleckTalk):
        #                 bleckFrame = (bleckFrame + 1) % (len(bleckTalk))
        #             else:
        #                 bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckTalk[bleckFrame % len(bleckTalk)].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #     else:
        #         if now - bleckLastUpdate > 30:
        #             bleckLastUpdate = now
        #             if bleckFrame < len(bleckIdle):
        #                 bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #             else:
        #                 bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     if textbox.talking:
        #         self.screen.blit(bleckTalk[bleckFrame % len(bleckTalk)], self.camera.offset(bleckRect))
        #     else:
        #         self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # self.imgRect = bowserRect
        #
        # for i in range(round(fps * 0.75)):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # text = ["I'll tell you doesn't make\neven a little bit of sense.../p\nCount Bleck!",
        #         "Enough! Release Princess\nPeach, right now! I'm on a\nschedule over here!"]
        # textbox = TextBox(self, self, text)
        #
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if textbox.talking and textbox.pause == 0:
        #         if now - bowserLastUpdate > 45:
        #             bowserLastUpdate = now
        #             if bowserFrame < len(bowserTalking) - 1:
        #                 bowserFrame = (bowserFrame + 1) % (len(bowserTalking))
        #             else:
        #                 bowserFrame = 0
        #             bottom = bowserRect.bottom
        #             centerx = bowserRect.centerx
        #             bowserRect = bowserTalking[bowserFrame].get_rect()
        #             bowserRect.bottom = bottom
        #             bowserRect.centerx = centerx
        #     elif not textbox.talking:
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser.get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # self.imgRect = bleckRect
        #
        # for i in range(round(fps * 0.75)):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # text = ["Count Bleck says NEVER!\nThis princess is integral to\nfulfilling the prophesies...",
        #         "She will be brought to Castle\nBleck and used to destroy\nall worlds.../pby Count Bleck!"]
        # textbox = TextBox(self, self, text)
        #
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if textbox.startAdvance:
        #         bleckFrame = 23
        #
        #     if textbox.talking:
        #         if now - bleckLastUpdate > 30:
        #             bleckLastUpdate = now
        #             if bleckFrame < len(bleckTalk):
        #                 bleckFrame = (bleckFrame + 1) % (len(bleckTalk))
        #             else:
        #                 bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckTalk[bleckFrame % len(bleckTalk)].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #     else:
        #         if now - bleckLastUpdate > 30:
        #             bleckLastUpdate = now
        #             if bleckFrame < len(bleckIdle):
        #                 bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #             else:
        #                 bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     if textbox.talking:
        #         self.screen.blit(bleckTalk[bleckFrame % len(bleckTalk)], self.camera.offset(bleckRect))
        #     else:
        #         self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # self.imgRect = fRect
        #
        # for i in range(round(fps * 0.75)):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # text = ["B-/p b-/p b-/p",
        #         "/BBADNESS!",
        #         "The Count named Bleck is full of\nbadness!",
        #         "Even more badness than the Great\nCackletta!",
        #         "Fawful wishes to be a loyal\nminion of Count Bleck!"]
        # textbox = TextBox(self, self, text, sound="fawful")
        #
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if textbox.startAdvance:
        #         bleckFrame = 23
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if textbox.talking:
        #         if now - fLastUpdate > 75:
        #             fLastUpdate = now
        #             if fFrame < len(fTalking):
        #                 fFrame = (fFrame + 1) % (len(fTalking))
        #             else:
        #                 fFrame = 0
        #             fRect = fTalking[fFrame].get_rect()
        #     else:
        #         fRect = fawful.get_rect()
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     if textbox.talking:
        #         self.screen.blit(fTalking[fFrame], self.camera.offset(fRect))
        #     else:
        #         self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # self.imgRect = bleckRect
        #
        # for i in range(round(fps * 0.75)):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # text = ["It appears that Fawful, Green\nBean of the Beanbean Kingdom\nwants to work.../pfor Count Bleck.",
        #         "If he is able to swear eternal\nloyalty to Count Bleck, then\nhe can become a minion...",
        #         "of Count Bleck!"]
        # textbox = TextBox(self, self, text)
        #
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if textbox.startAdvance:
        #         bleckFrame = 23
        #
        #     if textbox.talking:
        #         if now - bleckLastUpdate > 30:
        #             bleckLastUpdate = now
        #             if bleckFrame < len(bleckTalk):
        #                 bleckFrame = (bleckFrame + 1) % (len(bleckTalk))
        #             else:
        #                 bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckTalk[bleckFrame % len(bleckTalk)].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #     else:
        #         if now - bleckLastUpdate > 30:
        #             bleckLastUpdate = now
        #             if bleckFrame < len(bleckIdle):
        #                 bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #             else:
        #                 bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     if textbox.talking:
        #         self.screen.blit(bleckTalk[bleckFrame % len(bleckTalk)], self.camera.offset(bleckRect))
        #     else:
        #         self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # self.imgRect = fRect
        #
        # for i in range(round(fps * 0.75)):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # text = ["Fawful says YES!",
        #         "Fawful will be loyal!",
        #         "Fawful will give the 110 percents!",
        #         "Then, the Mushroom Kingdom will be\nbelonging to Fawful!"]
        # textbox = TextBox(self, self, text, sound="fawful")
        #
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if textbox.startAdvance:
        #         bleckFrame = 23
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if textbox.talking:
        #         if now - fLastUpdate > 75:
        #             fLastUpdate = now
        #             if fFrame < len(fTalking):
        #                 fFrame = (fFrame + 1) % (len(fTalking))
        #             else:
        #                 fFrame = 0
        #             fRect = fTalking[fFrame].get_rect()
        #     else:
        #         fRect = fawful.get_rect()
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     if textbox.talking:
        #         self.screen.blit(fTalking[fFrame], self.camera.offset(fRect))
        #     else:
        #         self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # points = []
        #
        # counter = 0
        #
        # sheet = spritesheet("sprites/fawful.png", "sprites/fawful.xml")
        #
        # fawful = [sheet.getImageName("laughing_down_1.png"),
        #           sheet.getImageName("laughing_down_2.png"),
        #           sheet.getImageName("laughing_down_3.png"),
        #           sheet.getImageName("laughing_down_4.png")]
        #
        # fRect = fawful[0].get_rect()
        #
        # for i in range(fps * 2):
        #     points.append(pt.getPointOnLine(pRect.centerx, pRect.centery, 622, 943, i / (fps * 2)))
        #
        # self.imgRect = bleckRect
        #
        # while counter < len(points) - 1:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if textbox.startAdvance:
        #         bleckFrame = 23
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     counter += 1
        #
        #     pRect.center = points[counter]
        #
        #     if now - fLastUpdate > 75:
        #         fLastUpdate = now
        #         if fFrame < len(fawful):
        #             fFrame = (fFrame + 1) % (len(fawful))
        #         else:
        #             fFrame = 0
        #         fRect = fawful[fFrame].get_rect()
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(fShadow, self.camera.offset(fShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful[fFrame], self.camera.offset(fRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # fawful = sheet.getImageName("standing_down.png")
        # fRect = fawful.get_rect()
        #
        # sheet = spritesheet("sprites/count bleck.png", "sprites/count bleck.xml")
        #
        # self.imgRect = bowserRect
        #
        # for i in range(round(fps * 0.75)):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # text = ["Hey, here's a thought:/p\nyou calm down and free the\nprincess... OR ELSE!"]
        # textbox = TextBox(self, self, text)
        #
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if textbox.talking and textbox.pause == 0:
        #         if now - bowserLastUpdate > 45:
        #             bowserLastUpdate = now
        #             if bowserFrame < len(bowserTalking) - 1:
        #                 bowserFrame = (bowserFrame + 1) % (len(bowserTalking))
        #             else:
        #                 bowserFrame = 0
        #             bottom = bowserRect.bottom
        #             centerx = bowserRect.centerx
        #             bowserRect = bowserTalking[bowserFrame].get_rect()
        #             bowserRect.bottom = bottom
        #             bowserRect.centerx = centerx
        #     elif not textbox.talking:
        #         bottom = bowserRect.bottom
        #         centerx = bowserRect.centerx
        #         bowserRect = bowser.get_rect()
        #         bowserRect.bottom = bottom
        #         bowserRect.centerx = centerx
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # self.imgRect = bleckRect
        #
        # for i in range(round(fps * 0.75)):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # text = ["Bleh heh heh heh.../p\nYou princess shall NOT be\nreturned.../p by Count Bleck.",
        #         "In fact, Bowser, evil king of\nthe Koopas...Count Bleck will\ntake you, too!"]
        # textbox = TextBox(self, self, text)
        #
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if textbox.startAdvance:
        #         bleckFrame = 23
        #
        #     if textbox.talking:
        #         if now - bleckLastUpdate > 30:
        #             bleckLastUpdate = now
        #             if bleckFrame < len(bleckTalk):
        #                 bleckFrame = (bleckFrame + 1) % (len(bleckTalk))
        #             else:
        #                 bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckTalk[bleckFrame % len(bleckTalk)].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #     else:
        #         if now - bleckLastUpdate > 30:
        #             bleckLastUpdate = now
        #             if bleckFrame < len(bleckIdle):
        #                 bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #             else:
        #                 bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     if textbox.talking:
        #         self.screen.blit(bleckTalk[bleckFrame % len(bleckTalk)], self.camera.offset(bleckRect))
        #     else:
        #         self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # bleckIdle = [sheet.getImageName("laugh_1.png"),
        #              sheet.getImageName("laugh_2.png"),
        #              sheet.getImageName("laugh_3.png"),
        #              sheet.getImageName("laugh_4.png"),
        #              sheet.getImageName("laugh_5.png"),
        #              sheet.getImageName("laugh_6.png"),
        #              sheet.getImageName("laugh_7.png")]
        #
        # bleckToLaugh = [sheet.getImageName("to_laugh_1.png"),
        #              sheet.getImageName("to_laugh_2.png"),
        #              sheet.getImageName("to_laugh_3.png"),
        #              sheet.getImageName("to_laugh_4.png"),
        #              sheet.getImageName("to_laugh_5.png"),
        #              sheet.getImageName("to_laugh_6.png")]
        #
        # bleckFrame = 0
        #
        # while bleckFrame < len(bleckToLaugh) - 1:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         bleckFrame = (bleckFrame + 1) % (len(bleckToLaugh))
        #     bottom = bleckRect.bottom
        #     centerx = bleckRect.centerx
        #     bleckRect = bleckToLaugh[bleckFrame % len(bleckToLaugh)].get_rect()
        #     bleckRect.bottom = bottom
        #     bleckRect.centerx = centerx
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckToLaugh[bleckFrame % len(bleckToLaugh)], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # bleckFrame = 0
        #
        # for i in range(round(fps / 2)):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if textbox.startAdvance:
        #         bleckFrame = 23
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #     bottom = bleckRect.bottom
        #     centerx = bleckRect.centerx
        #     bleckRect = bleckIdle[bleckFrame % len(bleckIdle)].get_rect()
        #     bleckRect.bottom = bottom
        #     bleckRect.centerx = centerx
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame % len(bleckIdle)], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # text = ["\a\nBLEH HEH HEH HEH! BLECK!"]
        # textbox = TextBox(self, self, text)
        #
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if textbox.startAdvance:
        #         bleckFrame = 23
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #     bottom = bleckRect.bottom
        #     centerx = bleckRect.centerx
        #     bleckRect = bleckIdle[bleckFrame % len(bleckIdle)].get_rect()
        #     bleckRect.bottom = bottom
        #     bleckRect.centerx = centerx
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame % len(bleckIdle)], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # self.imgRect = bowserRect
        #
        # for i in range(round(fps * 0.75)):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(bowserShadow, self.camera.offset(bowserShadowRect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     if textbox.talking:
        #         self.screen.blit(bowserTalking[bowserFrame], self.camera.offset(bowserRect))
        #     else:
        #         self.screen.blit(bowser, self.camera.offset(bowserRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        #
        # bowser = CombineSprites([bowserShadow, bowser], [bowserShadowRect, bowserRect])
        #
        # disappear = LineFlipDisappear(self, bowser.image, bowser.rect.center)
        #
        # self.crowdScreamingSound.play(-1)
        #
        # while not disappear.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     disappear.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     disappear.draw()
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #
        #     pg.display.flip()
        #
        # for i in range(round(fps / 4)):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     disappear.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     disappear.draw()
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #
        #     pg.display.flip()
        #
        # self.map = Map("Bowser's Castle floor")
        # self.camera = Camera(self, self.map.width, self.map.height)
        # cameraRect = pg.rect.Rect(self.map.width, self.map.height / 2, 0, 0)
        #
        # while not enemiesDisappear[-1].complete:
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     cameraRect.x -= 3
        #     self.camera.update(cameraRect)
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     for i in range(len(enemiesDisappear)):
        #         if enemiesDisappear[i].maxRect.right > cameraRect.x and not enemiesDisappear[i].complete:
        #             enemiesDisappear[i].update()
        #             enemiesDisappear[i].draw()
        #         elif not enemiesDisappear[i].complete:
        #             enemies[i].update()
        #             self.screen.blit(enemies[i].images[enemies[i].currentFrame], self.camera.offset(enemies[i].rect))
        #
        #     pg.display.flip()
        #
        # self.crowdScreamingSound.fadeout(500)
        #
        # for i in range(round(fps / 4)):
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     cameraRect.x -= 3
        #     self.camera.update(cameraRect)
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     for i in range(len(enemiesDisappear)):
        #         if enemiesDisappear[i].maxRect.right > cameraRect.x and not enemiesDisappear[i].complete:
        #             enemiesDisappear[i].update()
        #             enemiesDisappear[i].draw()
        #         elif not enemiesDisappear[i].complete:
        #             enemies[i].update()
        #             self.screen.blit(enemies[i].images[enemies[i].currentFrame], self.camera.offset(enemies[i].rect))
        #
        #     pg.display.flip()
        #
        # self.map = Map("Bowser's Castle")
        #
        # self.camera = Camera(self, self.map.width, self.map.height)
        #
        # cameraRect = CameraRect()
        # self.imgRect = bleckRect
        #
        # for i in range(fps):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #
        #     pg.display.flip()
        #
        # text = ["BLEH HEH HEH HEH! BLECK!\nCount Bleck's preparations\nare now in order!",
        #         "All that remains is for the\ndimensional void to appear,\nas foretold in the prophecy...",
        #         "Mr. <<RRed>> and Mr. <<GGreen>>, enjoy\nyour final days, before the\nvoid consumes all worlds!",
        #         "Bleh heh heh heh heh...",
        #         "\a\nBLEH HEH HEH HEH! BLECK!"]
        # textbox = TextBox(self, self, text)
        #
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        #
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        #
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        #
        #     if now - peachLastUpdate > 50:
        #         peachLastUpdate = now
        #         if peachFrame < len(peach):
        #             peachFrame = (peachFrame + 1) % (len(peach))
        #         else:
        #             peachFrame = 0
        #         center = peachRect.center
        #         peachRect = peach[peachFrame].get_rect()
        #         peachRect.center = center
        #
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        #
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        #
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        #
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(peach[peachFrame], self.camera.offset(peachRect))
        #     self.screen.blit(barrier, self.camera.offset(bRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        #     textbox.draw()
        #
        #     pg.display.flip()
        # 
        # peach = CombineSprites([peach[peachFrame], barrier], [peachRect, bRect])
        # 
        # disappear = LineFlipDisappear(self, peach.image, peach.rect.center)
        # 
        # while not disappear.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     disappear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     disappear.draw()
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        # 
        #     pg.display.flip()
        # 
        # for i in range(round(fps / 4)):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        # 
        #     if now - pLastUpdate > 50:
        #         pLastUpdate = now
        #         if pFrame < len(platform):
        #             pFrame = (pFrame + 1) % (len(platform))
        #         else:
        #             pFrame = 0
        #         center = pRect.center
        #         pRect = platform[pFrame].get_rect()
        #         pRect.center = center
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     disappear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     disappear.draw()
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(platform[pFrame], self.camera.offset(pRect))
        #     self.screen.blit(fawful, self.camera.offset(fRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        # 
        #     pg.display.flip()
        # 
        # fawful = CombineSprites([platform[pFrame], fawful], [pRect, fRect])
        # 
        # disappear = LineFlipDisappear(self, fawful.image, fawful.rect.center)
        # 
        # while not disappear.complete:
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     disappear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     disappear.draw()
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        # 
        #     pg.display.flip()
        # 
        # for i in range(round(fps / 4)):
        #     now = pg.time.get_ticks()
        #     self.playSong(15.104, 32.001, "The Evil Count Bleck 2")
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     if now - bleckLastUpdate > 30:
        #         bleckLastUpdate = now
        #         if bleckFrame < len(bleckIdle):
        #             bleckFrame = (bleckFrame + 1) % (len(bleckIdle))
        #         else:
        #             bleckFrame = 0
        #         bottom = bleckRect.bottom
        #         left = bleckRect.left
        #         bleckRect = bleckIdle[bleckFrame].get_rect()
        #         bleckRect.bottom = bottom
        #         bleckRect.left = left
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     disappear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     disappear.draw()
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     self.screen.blit(bleckIdle[bleckFrame], self.camera.offset(bleckRect))
        # 
        #     pg.display.flip()
        # 
        # disappear = LineFlipDisappear(self, bleckIdle[bleckFrame], bleckRect.center, sound="bleck")
        # 
        # pg.mixer.music.fadeout(5000)
        # 
        # while not disappear.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     disappear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     disappear.draw()
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        # 
        #     pg.display.flip()
        # 
        # for i in range(fps * 2):
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(self.imgRect, 60)
        #     self.camera.update(cameraRect.rect)
        #     disappear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     disappear.draw()
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        # 
        #     pg.display.flip()
        # 
        # camRect = pg.rect.Rect((marioShadowRect.centerx + luigiShadowRect.centerx) / 2, marioShadowRect.centery, 0, 0)
        # cameraRect.update(camRect, 180)
        # 
        # for i in range(180):
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(camRect, 180)
        #     self.camera.update(cameraRect.rect)
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        # 
        #     pg.display.flip()
        # 
        # sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")
        # 
        # mario = sheet.getImageName("mario_standing_left.png")
        # 
        # luigi = sheet.getImageName("luigi_standing_left.png")
        # 
        # sheet = spritesheet("sprites/starlow.png", "sprites/starlow.xml")
        # 
        # starlow = [sheet.getImageName("starlow_right_1.png"),
        #            sheet.getImageName("starlow_right_2.png"),
        #            sheet.getImageName("starlow_right_3.png"),
        #            sheet.getImageName("starlow_right_4.png"),
        #            sheet.getImageName("starlow_right_5.png"),
        #            sheet.getImageName("starlow_right_6.png")]
        # 
        # sTalking = [sheet.getImageName("starlow_talking_right_1.png"),
        #             sheet.getImageName("starlow_talking_right_2.png"),
        #             sheet.getImageName("starlow_talking_right_3.png"),
        #             sheet.getImageName("starlow_talking_right_4.png"),
        #             sheet.getImageName("starlow_talking_right_5.png"),
        #             sheet.getImageName("starlow_talking_right_6.png"),
        #             sheet.getImageName("starlow_talking_right_7.png"),
        #             sheet.getImageName("starlow_talking_right_8.png")]
        # 
        # self.imgRect = sRect
        # text = ["Wait, did that guy say he was going\nto DESTROY ALL WORLDS?",
        #         "We need to stop him!"]
        # textbox = TextBox(self, self, text, sound="starlow")
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if textbox.talking:
        #         if now - sLastUpdate > 100:
        #             sLastUpdate = now
        #             if sFrame < len(sTalking):
        #                 sFrame = (sFrame + 1) % (len(sTalking))
        #             else:
        #                 sFrame = 0
        #         sRect = sTalking[sFrame % len(sTalking)].get_rect()
        #     else:
        #         if now - sLastUpdate > 100:
        #             sLastUpdate = now
        #             if sFrame < len(starlow):
        #                 sFrame = (sFrame + 1) % (len(starlow))
        #             else:
        #                 sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(camRect, 180)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     if textbox.talking:
        #         self.screen.blit(sTalking[sFrame % len(sTalking)], self.camera.offset(sRect))
        #     else:
        #         self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # sheet = spritesheet("sprites/mario-luigi.png", "sprites/mario-luigi.xml")
        # 
        # mario = sheet.getImageName("mario_standing_up.png")
        # 
        # luigi = sheet.getImageName("luigi_standing_up.png")
        # 
        # mRect = mario.get_rect()
        # lRect = luigi.get_rect()
        # 
        # mRect.centerx = marioShadowRect.centerx
        # mRect.bottom = marioShadowRect.bottom - 5
        # lRect.centerx = luigiShadowRect.centerx
        # lRect.bottom = luigiShadowRect.bottom - 5
        # 
        # sheet = spritesheet("sprites/starlow.png", "sprites/starlow.xml")
        # 
        # starlow = [sheet.getImageName("starlow_upright_1.png"),
        #            sheet.getImageName("starlow_upright_2.png"),
        #            sheet.getImageName("starlow_upright_3.png"),
        #            sheet.getImageName("starlow_upright_4.png"),
        #            sheet.getImageName("starlow_upright_5.png"),
        #            sheet.getImageName("starlow_upright_6.png")]
        # 
        # sTalking = [sheet.getImageName("starlow_talking_upright_1.png"),
        #             sheet.getImageName("starlow_talking_upright_2.png"),
        #             sheet.getImageName("starlow_talking_upright_3.png"),
        #             sheet.getImageName("starlow_talking_upright_4.png"),
        #             sheet.getImageName("starlow_talking_upright_5.png"),
        #             sheet.getImageName("starlow_talking_upright_6.png"),
        #             sheet.getImageName("starlow_talking_upright_7.png"),
        #             sheet.getImageName("starlow_talking_upright_8.png")]
        # 
        # sheet = spritesheet("sprites/toadley.png", "sprites/toadley.xml")
        # 
        # toadley = sheet.getImageName("standing_down.png")
        # 
        # toadleyTalking = [sheet.getImageName("talking_down_1.png"),
        #                   sheet.getImageName("talking_down_2.png"),
        #                   sheet.getImageName("talking_down_3.png"),
        #                   sheet.getImageName("talking_down_4.png"),
        #                   sheet.getImageName("talking_down_5.png"),
        #                   sheet.getImageName("talking_down_6.png")]
        # 
        # toadleyShadow = sheet.getImageName("shadow.png")
        # 
        # tRect = toadley.get_rect()
        # tShadowRect = toadleyShadow.get_rect()
        # 
        # toadleyLastUpdate = 0
        # toadleyFrame = 0
        # 
        # tRect.center = bowserShadowRect.center
        # tRect.centery -= 15
        # tShadowRect.centerx = tRect.centerx
        # tShadowRect.bottom = tRect.bottom + 2
        # 
        # tod = CombineSprites([toadleyShadow, toadley], [tShadowRect, tRect])
        # 
        # appear = LineFlipAppear(self, tod.image, tod.rect.center)
        # 
        # while not appear.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #     sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(camRect, 180)
        #     self.camera.update(cameraRect.rect)
        #     appear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     appear.draw()
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        # 
        #     pg.display.flip()
        # 
        # for i in range(round(fps / 2)):
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if textbox.talking:
        #         if now - toadleyLastUpdate > 100:
        #             toadleyLastUpdate = now
        #             if toadleyFrame < len(toadleyTalking):
        #                 toadleyFrame = (toadleyFrame + 1) % (len(toadleyTalking))
        #             else:
        #                 toadleyFrame = 0
        #         tRect = toadleyTalking[toadleyFrame % len(toadleyTalking)].get_rect()
        #     else:
        #         tRect = toadley.get_rect()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #     sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     tRect.centerx = tShadowRect.centerx
        #     tRect.bottom = tShadowRect.bottom - 2
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(camRect, 180)
        #     self.camera.update(cameraRect.rect)
        #     appear.update()
        #     textbox.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(toadleyShadow, self.camera.offset(tShadowRect))
        #     appear.draw()
        #     if textbox.talking:
        #         self.screen.blit(toadleyTalking[toadleyFrame], self.camera.offset(tRect))
        #     else:
        #         self.screen.blit(toadley, self.camera.offset(tRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # self.imgRect = tRect
        # text = ["Did you meet Count Bleck?/p You did.",
        #         "Did he take Bowser and the\nPrincess?/p Certainly.",
        #         "Will there be disastrous results\nif he is not stopped?/p\nThere will.",
        #         "Is the end of all worlds upon\nus as we speak?/p Without a doubt.",
        #         "Did I come in search of your\naid?/p I did."]
        # textbox = TextBox(self, self, text)
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if textbox.talking:
        #         if now - toadleyLastUpdate > 100:
        #             toadleyLastUpdate = now
        #             if toadleyFrame < len(toadleyTalking):
        #                 toadleyFrame = (toadleyFrame + 1) % (len(toadleyTalking))
        #             else:
        #                 toadleyFrame = 0
        #         tRect = toadleyTalking[toadleyFrame % len(toadleyTalking)].get_rect()
        #     else:
        #         tRect = toadley.get_rect()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #     sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     tRect.centerx = tShadowRect.centerx
        #     tRect.bottom = tShadowRect.bottom - 2
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(camRect, 180)
        #     self.camera.update(cameraRect.rect)
        #     appear.update()
        #     textbox.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(toadleyShadow, self.camera.offset(tShadowRect))
        #     appear.draw()
        #     if textbox.talking:
        #         self.screen.blit(toadleyTalking[toadleyFrame], self.camera.offset(tRect))
        #     else:
        #         self.screen.blit(toadley, self.camera.offset(tRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # self.imgRect = sRect
        # text = ["Wait... Who are you?",
        #         "Why are you looking for Mario\nand Luigi?",
        #         "How did you know about what just\nhappened?"]
        # textbox = TextBox(self, self, text, sound="starlow")
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if textbox.talking:
        #         if now - sLastUpdate > 100:
        #             sLastUpdate = now
        #             if sFrame < len(sTalking):
        #                 sFrame = (sFrame + 1) % (len(sTalking))
        #             else:
        #                 sFrame = 0
        #         sRect = sTalking[sFrame % len(sTalking)].get_rect()
        #     else:
        #         if now - sLastUpdate > 100:
        #             sLastUpdate = now
        #             if sFrame < len(starlow):
        #                 sFrame = (sFrame + 1) % (len(starlow))
        #             else:
        #                 sFrame = 0
        #         sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     fRect.centerx = pRect.centerx
        #     fRect.bottom = pRect.top + 27
        #     fShadowRect.centerx = pRect.centerx
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(camRect, 180)
        #     self.camera.update(cameraRect.rect)
        #     textbox.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(toadleyShadow, self.camera.offset(tShadowRect))
        #     self.screen.blit(toadley, self.camera.offset(tRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     if textbox.talking:
        #         self.screen.blit(sTalking[sFrame % len(sTalking)], self.camera.offset(sRect))
        #     else:
        #         self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # toadley = sheet.getImageName("standing_downleft.png")
        # 
        # toadleyTalking = [sheet.getImageName("talking_downleft_1.png"),
        #                   sheet.getImageName("talking_downleft_2.png"),
        #                   sheet.getImageName("talking_downleft_3.png"),
        #                   sheet.getImageName("talking_downleft_4.png"),
        #                   sheet.getImageName("talking_downleft_5.png"),
        #                   sheet.getImageName("talking_downleft_6.png")]
        # 
        # self.imgRect = tRect
        # text = ["Are you asking too many Questions?/p\nYou are.",
        #         "Will I answer them anyways?/p I will.",
        #         "Am I Dr. Toadley?/p I am.",
        #         "Am I making sure that Count Bleck\ndoes not destroy all worlds?/p\nYes.",
        #         "Are Mario and Luigi the only ones\nwho are able to beat the Count?/p\nThey are indeed.",
        #         "Have I been following Count Bleck's\nevery movement for a long time?/p\nI have.",
        #         "Do you need to come with me in\norder to help save all worlds?/p\nYou do."]
        # textbox = TextBox(self, self, text)
        # 
        # while not textbox.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if textbox.page == len(text) - 1:
        #         toadley = sheet.getImageName("standing_down.png")
        # 
        #         toadleyTalking = [sheet.getImageName("talking_down_1.png"),
        #                           sheet.getImageName("talking_down_2.png"),
        #                           sheet.getImageName("talking_down_3.png"),
        #                           sheet.getImageName("talking_down_4.png"),
        #                           sheet.getImageName("talking_down_5.png"),
        #                           sheet.getImageName("talking_down_6.png")]
        # 
        #     if textbox.talking:
        #         if now - toadleyLastUpdate > 100:
        #             toadleyLastUpdate = now
        #             if toadleyFrame < len(toadleyTalking):
        #                 toadleyFrame = (toadleyFrame + 1) % (len(toadleyTalking))
        #             else:
        #                 toadleyFrame = 0
        #         tRect = toadleyTalking[toadleyFrame % len(toadleyTalking)].get_rect()
        #     else:
        #         tRect = toadley.get_rect()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #     sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     tRect.centerx = tShadowRect.centerx
        #     tRect.bottom = tShadowRect.bottom - 2
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(camRect, 180)
        #     self.camera.update(cameraRect.rect)
        #     appear.update()
        #     textbox.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(luigiShadowSprite, self.camera.offset(luigiShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(toadleyShadow, self.camera.offset(tShadowRect))
        #     appear.draw()
        #     if textbox.talking:
        #         self.screen.blit(toadleyTalking[toadleyFrame], self.camera.offset(tRect))
        #     else:
        #         self.screen.blit(toadley, self.camera.offset(tRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     self.screen.blit(luigi, self.camera.offset(lRect))
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        #     textbox.draw()
        # 
        #     pg.display.flip()
        # 
        # luigi = CombineSprites([luigiShadowSprite, luigi], [luigiShadowRect, lRect])
        # 
        # appear = LineFlipDisappear(self, luigi.image, luigi.rect.center)
        # 
        # while not appear.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #     sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     tRect.centerx = tShadowRect.centerx
        #     tRect.bottom = tShadowRect.bottom - 2
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(camRect, 180)
        #     self.camera.update(cameraRect.rect)
        #     appear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(marioShadowSprite, self.camera.offset(marioShadowRect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(toadleyShadow, self.camera.offset(tShadowRect))
        #     self.screen.blit(toadley, self.camera.offset(tRect))
        #     self.screen.blit(mario, self.camera.offset(mRect))
        #     appear.draw()
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        # 
        #     pg.display.flip()
        # 
        # mario = CombineSprites([marioShadowSprite, mario], [marioShadowRect, mRect])
        # 
        # appear = LineFlipDisappear(self, mario.image, mario.rect.center)
        # 
        # while not appear.complete:
        #     now = pg.time.get_ticks()
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     if now - sLastUpdate > 100:
        #         sLastUpdate = now
        #         if sFrame < len(starlow):
        #             sFrame = (sFrame + 1) % (len(starlow))
        #         else:
        #             sFrame = 0
        #     sRect = starlow[sFrame % len(starlow)].get_rect()
        # 
        #     tRect.centerx = tShadowRect.centerx
        #     tRect.bottom = tShadowRect.bottom - 2
        # 
        #     sRect.centerx = sShadowRect.centerx
        #     sRect.bottom = sShadowRect.top - 25
        # 
        #     cameraRect.update(camRect, 180)
        #     self.camera.update(cameraRect.rect)
        #     appear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(sShadow, self.camera.offset(sShadowRect))
        #     self.screen.blit(toadleyShadow, self.camera.offset(tShadowRect))
        #     self.screen.blit(toadley, self.camera.offset(tRect))
        #     appear.draw()
        #     self.screen.blit(starlow[sFrame % len(starlow)], self.camera.offset(sRect))
        # 
        #     pg.display.flip()
        # 
        # starlow = CombineSprites([sShadow, starlow[sFrame]], [sShadowRect, sRect])
        # 
        # appear = LineFlipDisappear(self, starlow.image, starlow.rect.center)
        # 
        # while not appear.complete:
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     cameraRect.update(camRect, 180)
        #     self.camera.update(cameraRect.rect)
        #     appear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.screen.blit(toadleyShadow, self.camera.offset(tShadowRect))
        #     self.screen.blit(toadley, self.camera.offset(tRect))
        #     appear.draw()
        # 
        #     pg.display.flip()
        # 
        # toadley = CombineSprites([toadleyShadow, toadley], [tShadowRect, tRect])
        # 
        # appear = LineFlipDisappear(self, toadley.image, toadley.rect.center)
        # 
        # while not appear.complete:
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     cameraRect.update(camRect, 180)
        #     self.camera.update(cameraRect.rect)
        #     appear.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     appear.draw()
        # 
        #     pg.display.flip()
        # 
        # time.sleep(1)
        # self.playtime += fps * 2
        # 
        # fade = Fadeout(self, 5)
        # 
        # while fade.alpha < 255:
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        # 
        #     cameraRect.update(camRect, 180)
        #     self.camera.update(cameraRect.rect)
        #     fade.update()
        # 
        #     self.screen.fill(black)
        #     self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        #     self.blit_alpha(self.screen, fade.image, fade.rect, fade.alpha)
        # 
        #     pg.display.flip()
        # 
        # for i in range(fps * 2):
        #     self.calculatePlayTime()
        #     self.clock.tick(fps)
        #     self.events()
        #
        self.currentPoint = 0
        self.loadFlipside()

    def gameOver(self, mario=True, luigi=True):
        pg.mixer.music.fadeout(500)
        sheet = spritesheet("sprites/ui.png", "sprites/ui.xml")
        gameOver = sheet.getImageName("Game Over.png")
        gameOverRect = gameOver.get_rect()
        gameOverRect.center = (width / 2, height / 2)
        alpha = 0
        if mario and luigi:
            self.gameOverBoth.play()
        elif mario:
            self.gameOverMario.play()
        elif luigi:
            self.gameOverLuigi.play()
        fade = Fadeout(self)
        while True:
            alpha += 1

            self.events()

            if not pg.mixer.get_busy() and alpha >= 255:
                fade.update()

            try:
                if fade.alpha >= 255:
                    self.titleScreen()
            except:
                pass

            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(alpha)

            [sprite.update() for sprite in self.sprites]

            self.drawBattleMenu()
            self.screen.blit(s, sRect)
            self.blit_alpha(self.screen, gameOver, gameOverRect, alpha)
            self.screen.blit(fade.image, fade.rect)

            pg.display.flip()

    def saveGame(self, song=None):
        self.menuOpenSound.play()
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
        if self.leader == "mario":
            self.storeData["move"] = self.follower.moveQueue.copy()
        elif self.leader == "luigi":
            self.storeData["move"] = self.player.moveQueue.copy()
        self.storeData["luigi facing"] = self.follower.facing
        self.storeData["luigi abilities"] = self.follower.abilities
        if self.follower.prevAbility == 12:
            self.storeData["luigi current ability"] = self.follower.ability
        else:
            self.storeData["luigi current ability"] = self.follower.prevAbility
        saves = [SaveSelection(self, 1), SaveSelection(self, 2), SaveSelection(self, 3)]
        cursor = Cursor(self, saves[0].rect)
        select = 0
        going = True
        while going:
            self.calculatePlayTime()
            if song is not None:
                self.playSong(song[0], song[1], song[2], cont=True, fadein=True)

            self.clock.tick(fps)

            self.events()
            for event in self.event:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_a:
                        if select == 0:
                            select = 2
                        else:
                            select -= 1
                        self.abilityAdvanceSound.play()
                    if event.key == pg.K_d:
                        if select == 2:
                            select = 0
                        else:
                            select += 1
                        self.abilityAdvanceSound.play()
                    if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                        self.menuChooseSound.play()
                        with open("saves/File " + str(select + 1) + ".ini", "wb") as file:
                            pickle.dump(self.area, file)
                            pickle.dump(self.storeData, file)
                            pickle.dump(self.displayTime, file)
                            pickle.dump(self.player.attackPieces, file)
                            pickle.dump(self.follower.attackPieces, file)
                            pickle.dump(self.playtime, file)
                            pickle.dump(self.despawnList, file)
                            pickle.dump(self.hitBlockList, file)
                            pickle.dump(self.coins, file)
                            for item in self.items:
                                pickle.dump(item[1], file)
                            pickle.dump(self.room, file)
                            pickle.dump(self.usedCutscenes, file)
                            pickle.dump(self.leader, file)
                        saves = [SaveSelection(self, 1), SaveSelection(self, 2), SaveSelection(self, 3)]
                    if event.key == pg.K_TAB:
                        going = False

            if select == 0:
                cursor.update(saves[0].rect, 60)
            elif select == 1:
                cursor.update(saves[1].rect, 60)
            elif select == 2:
                cursor.update(saves[2].rect, 60)

            self.screen.fill(black)
            self.drawOverworldMenu()
            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)
            self.screen.blit(s, sRect)
            [save.draw() for save in saves]
            self.screen.blit(cursor.image, cursor.rect)

            pg.display.flip()

        self.menuCloseSound.play()

        self.player.canMove = False
        self.follower.canMove = False

        self.saved = True
        self.pause = False

    def loadGame(self, file=1):
        try:
            with open("saves/File " + str(file) + ".ini", "rb") as file:
                area = pickle.load(file)
                self.storeData = pickle.load(file)
                self.displayTime = pickle.load(file)
                self.player.attackPieces = pickle.load(file)
                self.follower.attackPieces = pickle.load(file)
                self.playtime = pickle.load(file)
                self.despawnList = pickle.load(file)
                self.hitBlockList = pickle.load(file)
                self.coins = pickle.load(file)
                for item in self.items:
                    item[1] = pickle.load(file)
                self.room = pickle.load(file)
                self.usedCutscenes = pickle.load(file)
                self.leader = pickle.load(file)
            self.currentPoint = 0
            eval(self.room)
        except:
            print("File not found.\nStarting a new game...")
            self.items = [["Mushroom", -1, mushroomSprite, "hp", "maxHP", "Restores 30 HP to one Bro.", 30],
                          ["Super Mushroom", -1, mushroomSprite, "hp", "maxHP", "Restores 60 HP to one Bro.", 60],
                          ["Ultra Mushroom", -1, mushroomSprite, "hp", "maxHP", "Restores 120 HP to one Bro.", 120],
                          ["Max Mushroom", -1, mushroomSprite, "hp", "maxHP", "Fully restores HP to one Bro.", "maxHP"],
                          ["Nut", -1, NutSprite, "hp", "maxHP", "Restores 20 BP for both Bros.", 20],
                          ["Super Nut", -1, NutSprite, "hp", "maxHP", "Restores 40 BP for both Bros.", 40],
                          ["Ultra Nut", -1, NutSprite, "hp", "maxHP", "Restores 80 BP for both Bros.", 80],
                          ["Max Nut", -1, NutSprite, "hp", "maxHP", "Fuly restores  BP for both Bros.", "maxHP"],
                          ["Syrup", -1, syrupSprite, "bp", "maxBP", "Restores 10 BP to one Bro.", 10],
                          ["Super Syrup", -1, syrupSprite, "bp", "maxBP", "Restores 20 BP to one Bro.", 20],
                          ["Ultra Syrup", -1, syrupSprite, "bp", "maxBP", "Restores 30 BP to one Bro.", 30],
                          ["Max Syrup", -1, syrupSprite, "bp", "maxBP", "Fully restores BP to one Bro.", "maxBP"],
                          ["1-UP Mushroom", -1, oneUpSprite, "hp", 1, "Revives a fallen Bro with 1/2 HP.", "maxHP"],
                          ["1-UP Super", -1, oneUpSprite, "hp", 1, "Revives a fallen Bro with full HP.", "maxHP"],
                          ["Star Cand", -1, candySprite, "hp", "maxHP", "Fully restores HP and BP for one Bro.",
                           "maxHP"]]
            self.despawnList = []
            self.hitBlockList = []
            self.coins = 0
            self.newGame()

    def loadData(self):
        self.lineDrawSound = pg.mixer.Sound("sounds/lineDraw.ogg")
        self.fawfulHududu = pg.mixer.Sound("sounds/fawfulHududu.ogg")
        self.fawfulcopterSound = pg.mixer.Sound("sounds/fawfulcopter.ogg")
        self.ding = pg.mixer.Sound("sounds/ding.ogg")
        self.starlowTwinkle = pg.mixer.Sound("sounds/starLowTwinkle.ogg")
        self.coinSound = pg.mixer.Sound("sounds/coin.ogg")
        self.sandSound = pg.mixer.Sound("sounds/sand footsteps.ogg")
        self.stoneSound = pg.mixer.Sound("sounds/stone footsteps.ogg")
        self.jumpSound = pg.mixer.Sound("sounds/jump.ogg")
        self.battleSound = pg.mixer.Sound("sounds/startbattle.ogg")
        self.marioBattleSound = pg.mixer.Sound("sounds/startBattle_mario.ogg")
        self.talkSoundHigh = pg.mixer.Sound("sounds/talkSound_high.ogg")
        self.talkSoundMed = pg.mixer.Sound("sounds/talkSound_med.ogg")
        self.talkSoundLow = pg.mixer.Sound("sounds/talkSound_low.ogg")
        self.starlowTalkSoundHigh = pg.mixer.Sound("sounds/starlowTalkSound_high.ogg")
        self.starlowTalkSoundMed = pg.mixer.Sound("sounds/starlowTalkSound_med.ogg")
        self.starlowTalkSoundLow = pg.mixer.Sound("sounds/starlowTalkSound_low.ogg")
        self.fawfulTalkSoundHigh = pg.mixer.Sound("sounds/fawfulTalkSound_high.ogg")
        self.fawfulTalkSoundMed = pg.mixer.Sound("sounds/fawfulTalkSound_med.ogg")
        self.fawfulTalkSoundLow = pg.mixer.Sound("sounds/fawfulTalkSound_low.ogg")
        self.textBoxOpenSound = pg.mixer.Sound("sounds/textboxopen.ogg")
        self.textBoxCloseSound = pg.mixer.Sound("sounds/textboxclose.ogg")
        self.talkAdvanceSound = pg.mixer.Sound("sounds/talkadvance.ogg")
        self.playerHitSound = pg.mixer.Sound("sounds/playerhit.ogg")
        self.enemyHitSound = pg.mixer.Sound("sounds/enemyhit.ogg")
        self.enemyDieSound = pg.mixer.Sound("sounds/enemydie.ogg")
        self.hammerSwingSound = pg.mixer.Sound("sounds/hammer swing.ogg")
        self.hammerHitSound = pg.mixer.Sound("sounds/hammer hit.ogg")
        self.abilityAdvanceSound = pg.mixer.Sound("sounds/ability cycle.ogg")
        self.menuOpenSound = pg.mixer.Sound("sounds/menuOpen.ogg")
        self.menuChooseSound = pg.mixer.Sound("sounds/menuChoose.ogg")
        self.menuCloseSound = pg.mixer.Sound("sounds/menuClose.ogg")
        self.wrongSound = pg.mixer.Sound("sounds/menuWrong.ogg")
        self.expIncreaseSound = pg.mixer.Sound("sounds/expIncrease.ogg")
        self.expFinishedSound = pg.mixer.Sound("sounds/expIncreaseFinished.ogg")
        self.blockHitSound = pg.mixer.Sound("sounds/hitBlock.ogg")
        self.smallRestoreSound = pg.mixer.Sound("sounds/smallRestore.ogg")
        self.medRestoreSound = pg.mixer.Sound("sounds/medRestore.ogg")
        self.fullRestoreSound = pg.mixer.Sound("sounds/fullRestore.ogg")
        self.levelUpSound = pg.mixer.Sound("sounds/levelUp.ogg")
        self.marioWahoo = pg.mixer.Sound("sounds/marioWahoo.ogg")
        self.marioOhYeah = pg.mixer.Sound("sounds/marioOhYeah.ogg")
        self.marioTalk1 = pg.mixer.Sound("sounds/marioTalk1.ogg")
        self.luigiYaHoooo = pg.mixer.Sound("sounds/luigiYaHoooo.ogg")
        self.luigiOhHoHo = pg.mixer.Sound("sounds/luigiOhHoHo.ogg")
        self.itemFromBlockSound = pg.mixer.Sound("sounds/itemFromBlock.ogg")
        self.gameOverMario = pg.mixer.Sound("sounds/gameOverMario.ogg")
        self.gameOverLuigi = pg.mixer.Sound("sounds/gameOverLuigi.ogg")
        self.gameOverBoth = pg.mixer.Sound("sounds/gameOverBoth.ogg")
        self.buySomethingSound = pg.mixer.Sound("sounds/buySomething.ogg")
        self.bowserLaugh = pg.mixer.Sound("sounds/bowserLaugh.ogg")
        self.bowserNgha = pg.mixer.Sound("sounds/bowserNgha.ogg")
        self.bowserMario = pg.mixer.Sound("sounds/bowserMario.ogg")
        self.bowserPunch = pg.mixer.Sound("sounds/bowserPunch.ogg")
        self.crowdSound = pg.mixer.Sound("sounds/crowd.ogg")
        self.crowdScreamingSound = pg.mixer.Sound("sounds/crowdScreaming.ogg")

    def loadDebugLevel(self):
        self.room = "self.loadDebugLevel()"
        MarioUI(self)
        LuigiUI(self)
        self.sprites = []
        self.collision = []
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.blocks = pg.sprite.Group()
        self.npcs = pg.sprite.Group()
        self.player.rect.center = (width / 2, 1278)
        self.playerCol = MarioCollision(self)
        self.follower.rect.center = (width / 2, 1278)
        self.followerCol = LuigiCollision(self)
        self.playerHammer = HammerCollisionMario(self)
        self.followerHammer = HammerCollisionLuigi(self)
        self.sprites.append(self.follower)
        self.sprites.append(self.player)
        self.follower.stepSound = self.stoneSound
        self.player.stepSound = self.stoneSound
        self.map = Map("Bowser's Castle")
        self.camera = Camera(self, self.map.width, self.map.height)
        self.cameraRect = CameraRect()
        MarioBlock(self, (300, self.map.height - 450))
        LuigiBlock(self, (600, self.map.height - 450))
        Block(self, (900, self.map.height - 450), contents=["Other(self.game, self, 'Max Nut', 1)"])
        LuigiBlock(self, (1100, self.map.height - 450),
                   contents=["Coin(self.game, self)", "Coin(self.game, self)", "Coin(self.game, self)",
                             "Coin(self.game, self)", "Coin(self.game, self)", "Coin(self.game, self)",
                             "Coin(self.game, self)", "Coin(self.game, self)", "Coin(self.game, self)",
                             "Coin(self.game, self)"])
        SaveBlock(self, (1200, self.map.height - 450))
        LinebeckDebug(self, (self.map.width / 2 - 2, self.map.height - 420), self.goombaHasTexted)
        GoombaODebug(self, self.map.width / 2 + 500, self.map.height - 500, "self.loadSingleEnemyDebug()")
        GoombaODebug(self, self.map.width / 2 - 500, self.map.height - 500, "self.loadSingleEnemyDebug()")
        GoombaODebug(self, self.map.width / 2 + 400, self.map.height - 500, "self.loadSingleEnemyDebug()")
        GoombaODebug(self, self.map.width / 2 - 400, self.map.height - 500, "self.loadSingleEnemyDebug()")
        GoombaODebug(self, self.map.width / 2 + 600, self.map.height - 500, "self.loadSingleEnemyDebug()")
        GoombaODebug(self, self.map.width / 2 - 600, self.map.height - 500, "self.loadSingleEnemyDebug()")
        GoombaODebug(self, self.map.width / 2 - 200, self.map.height - 500, "self.loadSingleEnemyDebug()")
        GoombaODebug(self, self.map.width / 2 + 200, self.map.height - 500, "self.loadSingleEnemyDebug()")
        GoombaODebug(self, self.map.width / 2 + 300, self.map.height - 500, "self.loadSingleEnemyDebug()")
        GoombaODebug(self, self.map.width / 2 - 300, self.map.height - 500, "self.loadSingleEnemyDebug()")
        GoombaODebug(self, self.map.width / 2 + 100, self.map.height - 500, "self.loadSingleEnemyDebug()")
        GoombaODebug(self, self.map.width / 2 - 100, self.map.height - 500, "self.loadSingleEnemyDebug()")
        GoombaODebug(self, self.map.width / 2 - 700, self.map.height - 500, "self.loadSingleEnemyDebug()")
        GoombaODebug(self, self.map.width / 2 + 700, self.map.height - 500, "self.loadSingleEnemyDebug()")
        CountBleckDebug(self, (self.map.width / 2 - 5, self.map.height - 620))
        try:
            self.player.rect.center = self.storeData["mario pos"]
            self.player.stats = self.storeData["mario stats"]
            self.follower.rect.center = self.storeData["luigi pos"]
            self.follower.stats = self.storeData["luigi stats"]
            self.player.facing = self.storeData["mario facing"]
            self.follower.facing = self.storeData["luigi facing"]
            self.player.abilities = self.storeData["mario abilities"]
            self.follower.abilities = self.storeData["luigi abilities"]
            if self.leader == "mario":
                self.follower.moveQueue = self.storeData["move"]
            elif self.leader == "luigi":
                self.player.moveQueue = self.storeData["move"]
        except:
            pass

        counter = -100
        for enemy in self.enemies:
            enemy.ID = counter
            counter += 1

        counter = 0
        for block in self.blocks:
            block.ID = counter
            counter += 1

        self.overworld("Debug Area", [6.749, 102.727, "castle bleck"])

    def loadFlipside(self):
        self.room = "self.loadFlipside()"
        MarioUI(self)
        LuigiUI(self)
        self.sprites = []
        self.collision = []
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.blocks = pg.sprite.Group()
        self.npcs = pg.sprite.Group()
        self.map = Map("flipside center", background=True)
        self.camera = Camera(self, self.map.width, self.map.height)
        self.cameraRect = CameraRect()
        self.player.rect.center = (self.map.width / 2, 1178)
        self.playerCol = MarioCollision(self)
        self.follower.rect.center = (self.map.width / 2, 1178)
        self.followerCol = LuigiCollision(self)
        self.playerHammer = HammerCollisionMario(self)
        self.followerHammer = HammerCollisionLuigi(self)
        self.sprites.append(self.follower)
        self.sprites.append(self.player)
        self.follower.stepSound = self.stoneSound
        self.player.stepSound = self.stoneSound

        SaveBlock(self, (670, 637))
        LoadCutscene(self, self.player.rect, True, True,
                     [["self.changeSong([0, 95.997, 'flipside'])"],
                      ["self.setVar('self.game.mario = marioCutscene(self.game, (0, 0))')", "self.setVar('self.game.luigi = luigiCutscene(self.game, (0, 0))')", "self.setVar('self.game.starlow = starlowCutscene(self.game, (0, 0))')", "self.setVar('self.game.toadley = toadleyCutscene(self.game, (0, 0))')"],
                      ['''self.setVar('self.game.mario.facing = "up"')''', '''self.setVar('self.game.luigi.facing = "up"')''', '''self.setVar('self.game.starlow.facing = "upright"')''', '''self.setVar('self.game.toadley.facing = "down"')'''],
                      ["self.move(self.game.cameraRect, self.game.map.width / 2, 0, False, 2)"],
                      ["self.wait(5)"],
                      ["self.move(self.game.cameraRect, 0, 1000, True, 300)"],
                      ["self.flipIn([[self.game.luigi.shadow, self.game.luigi.image], [self.game.luigi.rect, self.game.luigi.imgRect]], ((self.game.map.width / 2) + 75, self.game.cameraRect.rect.y + 20))", "if self.currentSubscene > 0: self.setVar('self.game.luigi.rect.bottom, self.game.luigi.rect.centerx = self.game.cutsceneSprites[-1].maxRect.bottom, self.game.cutsceneSprites[-1].maxRect.centerx')"],
                      ["self.flipIn([[self.game.mario.shadow, self.game.mario.image], [self.game.mario.rect, self.game.mario.imgRect]], ((self.game.map.width / 2) - 75, self.game.cameraRect.rect.y + 20))",
                          "if self.currentSubscene > 0: self.setVar('self.game.mario.rect.bottom, self.game.mario.rect.centerx = self.game.cutsceneSprites[-1].maxRect.bottom, self.game.cutsceneSprites[-1].maxRect.centerx')"],
                      ["self.flipIn([[self.game.starlow.shadow, self.game.starlow.image], [self.game.starlow.rect, self.game.starlow.imgRect]], ((self.game.map.width / 2) - 200, self.game.cameraRect.rect.y))",
                          "if self.currentSubscene > 0: self.setVar('self.game.starlow.rect.bottom, self.game.starlow.rect.centerx = self.game.cutsceneSprites[-1].maxRect.bottom, self.game.cutsceneSprites[-1].maxRect.centerx')"],
                      ["self.flipIn([[self.game.toadley.shadow, self.game.toadley.image], [self.game.toadley.rect, self.game.toadley.imgRect]], ((self.game.map.width / 2), self.game.cameraRect.rect.y - 100))",
                      "if self.currentSubscene > 0: self.setVar('self.game.toadley.rect.bottom, self.game.toadley.rect.centerx = self.game.cutsceneSprites[1].maxRect.bottom, self.game.cutsceneSprites[1].maxRect.centerx')"],
                      ["self.wait(1)"],
                      ["self.textBox(self.game.toadley, ['Have we arrived in <<RFlipside>>?/p/nWe have.'])"],
                      ["self.textBox(self.game.starlow, ['Can you PLEASE stop talking in/nrhetorical questions?'], sound='starlow')"],
                      ["self.setVar('self.game.redMcMuffin = EggMcMuffin(self.game.toadley.rect.center, black, self.game)')", "self.command('self.game.cutsceneSprites.append(self.game.redMcMuffin)')"],
                      ["self.wait(10)"],
                      ["self.setVar('self.game.player.rect.center = self.game.mario.rect.center')",
                       "self.setVar('self.game.follower.rect.center = self.game.luigi.rect.center')"]], id=1)

        Wall(self, -50, 585, 2670, 30)
        Wall(self, -50, self.map.height, 2670, 30)
        Wall(self, -50, 585, 50, 1000)
        Wall(self, self.map.width, 585, 30, 1000)

        try:
            self.player.rect.center = self.storeData["mario pos"]
            self.player.stats = self.storeData["mario stats"]
            self.follower.rect.center = self.storeData["luigi pos"]
            self.follower.stats = self.storeData["luigi stats"]
            self.player.facing = self.storeData["mario facing"]
            self.follower.facing = self.storeData["luigi facing"]
            self.player.abilities = self.storeData["mario abilities"]
            self.follower.abilities = self.storeData["luigi abilities"]
            if self.leader == "mario":
                self.follower.moveQueue = self.storeData["move"]
            elif self.leader == "luigi":
                self.player.moveQueue = self.storeData["move"]

        except:
            pass

        self.overworld("Flipside", [0, 95.997, "flipside"])

    def overworld(self, area, songData):
        menud = False
        self.playsong = True
        self.playing = True
        self.saved = False
        self.save = False
        try:
            self.player.ability = self.storeData["mario current ability"]
            self.player.abilities = self.storeData["mario abilities"]
            self.follower.ability = self.storeData["luigi current ability"]
            self.follower.abilities = self.storeData["luigi abilities"]
        except:
            pass
        if self.area != area:
            self.playSong(songData[0], songData[1], songData[2])
            self.area = area
        while self.playing:
            if self.save:
                self.saveGame(songData)
                self.save = False
            self.calculatePlayTime()
            if self.playsong:
                self.playSong(songData[0], songData[1], songData[2], cont=True, fadein=True)
            self.clock.tick(fps)
            self.events()
            for event in self.event:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_TAB and self.player.canMove and self.follower.canMove:
                        self.player.canMove = False
                        self.follower.canMove = False
                        menud = True
                        self.pause = True
                        self.overworldMenu(songData)
            if len(self.fadeout) != 0:
                self.updateOverworld()
                self.pause = False
            elif not self.pause:
                self.updateOverworld()
            self.screen.fill(black)
            self.drawOverworld()

            if menud or self.saved:
                self.player.canMove = True
                self.follower.canMove = True
                menud = False
                self.saved = False
                print(self.song_playing)

    def overworldMenu(self, song):
        self.menuOpenSound.play()
        going = True
        select = 0
        itemMenu = pg.image.load("sprites/ui/itemsIcon.png").convert_alpha()
        itemRect = itemMenu.get_rect()
        brosMenu = pg.image.load("sprites/ui/statsIcon.png").convert_alpha()
        brosRect = brosMenu.get_rect()
        itemRect.center = (((width / 2) - (itemRect.width / 2)) - 100, height / 2)
        brosRect.center = (((width / 2) + (brosRect.width / 2)) + 100, height / 2)
        coinAmount = pg.transform.flip(pg.image.load("sprites/ui/enemySelection.png").convert_alpha(), True, True)
        playTime = pg.transform.flip(pg.image.load("sprites/ui/enemySelection.png").convert_alpha(), False, True)
        playRect = playTime.get_rect()
        playRect.bottom = height
        sheet = spritesheet("sprites/blocks.png", "sprites/blocks.xml")
        coinIcon = [sheet.getImageName("coin_1.png"),
                    sheet.getImageName("coin_2.png"),
                    sheet.getImageName("coin_3.png"),
                    sheet.getImageName("coin_4.png"),
                    sheet.getImageName("coin_5.png"),
                    sheet.getImageName("coin_6.png"),
                    sheet.getImageName("coin_7.png"),
                    sheet.getImageName("coin_8.png")]
        coinIconRect = coinIcon[0].get_rect()
        coinRect = coinAmount.get_rect()
        coinRect.right = width
        coinRect.bottom = height
        coinIconRect.center = (coinRect.left + 50, coinRect.centery)
        name = EnemyNames(self, "Items")
        cursor = Cursor(self, itemRect)
        lastUpdate = 0
        currentFrame = 0
        while going and self.pause:
            self.calculatePlayTime()
            now = pg.time.get_ticks()
            if now - lastUpdate > 45:
                lastUpdate = now
                if currentFrame < len(coinIcon):
                    currentFrame = (currentFrame + 1) % (len(coinIcon))
                else:
                    currentFrame = 0
                center = coinIconRect.center
                coinIconRect = coinIcon[currentFrame].get_rect()
                coinIconRect.center = center
            self.clock.tick(fps)
            self.playSong(song[0], song[1], song[2])

            self.fadeout.update()
            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)

            keys = pg.key.get_pressed()
            self.event = pg.event.get().copy()
            for event in self.event:
                if event == pg.QUIT or keys[pg.K_ESCAPE]:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_a or event.key == pg.K_d:
                        if select == 0:
                            select = 1
                        elif select == 1:
                            select = 0
                        self.abilityAdvanceSound.play()
                    if event.key == pg.K_m or event.key == pg.K_l:
                        if select == 0:
                            canMenu = False
                            for item in self.items:
                                if item[1] >= 0:
                                    canMenu = True
                            if canMenu:
                                going = False
                                self.menuChooseSound.play()
                                self.itemSelect(song)
                            else:
                                self.wrongSound.play()
                        if select == 1:
                            going = False
                            self.menuChooseSound.play()
                            self.brosStats(song)
                    if event.key == pg.K_TAB:
                        cursor.kill()
                        self.pause = False
                        going = False
                        self.menuCloseSound.play()

            if select == 0:
                name.update("Items")
                cursor.update(itemRect, 60)
            if select == 1:
                name.update("Statistics")
                cursor.update(brosRect, 60)

            self.drawOverworldMenu()
            self.screen.blit(itemMenu, itemRect)
            self.screen.blit(s, sRect)
            canMenu = False
            for item in self.items:
                if item[1] >= 0:
                    canMenu = True
            if canMenu:
                self.screen.blit(itemMenu, itemRect)
            self.screen.blit(brosMenu, brosRect)
            self.screen.blit(cursor.image, cursor.rect)
            self.screen.blit(coinAmount, coinRect)
            self.screen.blit(coinIcon[currentFrame], coinIconRect)
            ptext.draw("X" + str(self.coins), (coinRect.left + 100, coinRect.centery), fontname=dialogueFont,
                       anchor=(0, 0.5),
                       surf=self.screen, fontsize=40)
            self.screen.blit(playTime, playRect)
            ptext.draw(self.displayTime, (playRect.left + 10, playRect.centery), fontname=dialogueFont,
                       anchor=(0, 0.5),
                       surf=self.screen, fontsize=40)
            name.draw()
            self.fadeout.draw(self.screen)

            if self.pause:
                pg.display.flip()

    def shop(self, items, song=None):
        self.menuOpenSound.play()
        cursor = Cursor(self, self.player.imgRect)
        going = True
        menuIcons = []
        rect = pg.rect.Rect(0, 0, 0, 0)
        rect.center = (150, 150)
        select = 0
        coinAmount = pg.transform.flip(pg.image.load("sprites/ui/enemySelection.png").convert_alpha(), True, True)
        sheet = spritesheet("sprites/blocks.png", "sprites/blocks.xml")
        coinIcon = [sheet.getImageName("coin_1.png"),
                    sheet.getImageName("coin_2.png"),
                    sheet.getImageName("coin_3.png"),
                    sheet.getImageName("coin_4.png"),
                    sheet.getImageName("coin_5.png"),
                    sheet.getImageName("coin_6.png"),
                    sheet.getImageName("coin_7.png"),
                    sheet.getImageName("coin_8.png")]
        coinIconRect = coinIcon[0].get_rect()
        coinRect = coinAmount.get_rect()
        coinRect.right = width
        coinRect.bottom = height
        coinIconRect.center = (coinRect.left + 50, coinRect.centery)
        lastUpdate = 0
        currentFrame = 0

        for item in items:
            for tem in self.items:
                if tem[0] == item[0]:
                    if item[0] == "Star Cand":
                        menuIcons.append(
                            MenuIcon(self, rect.center, item[0] + "y (" + str(item[1]) + " Coins)", tem[2], item + tem))
                    else:
                        menuIcons.append(
                            MenuIcon(self, rect.center, item[0] + " (" + str(item[1]) + " Coins)", tem[2], item + tem))

                        rect.y += 100

        for icon in menuIcons:
            icon.color = darkGray
            if self.coins >= icon.info[1]:
                icon.color = white
            print(icon.info)

        if len(menuIcons) >= 6:
            menuCamera = Camera(self, width, menuIcons[-1].rect.bottom + (width / 2))
        else:
            menuCamera = Camera(self, width, height)
        name = EnemyNames(self, menuIcons[0].info[-2],
                          pg.image.load("sprites/ui/enemySelectionFullScreen.png").convert_alpha())

        self.pause = True
        while going:
            now = pg.time.get_ticks()
            if now - lastUpdate > 45:
                lastUpdate = now
                if currentFrame < len(coinIcon):
                    currentFrame = (currentFrame + 1) % (len(coinIcon))
                else:
                    currentFrame = 0
                center = coinIconRect.center
                coinIconRect = coinIcon[currentFrame].get_rect()
                coinIconRect.center = center

            self.calculatePlayTime()
            self.fadeout.update()
            self.clock.tick(fps)
            if song is not None:
                if type(song) is str:
                    eval(song)
                elif type(song) is list:
                    self.playSong(song[0], song[1], song[2], cont=True, fadein=True)

            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)

            for item in menuIcons:
                if item.info[1] > self.coins:
                    item.color = darkGray

            keys = pg.key.get_pressed()
            self.event = pg.event.get().copy()
            for event in self.event:
                if event == pg.QUIT or keys[pg.K_ESCAPE]:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_w or event.key == pg.K_a:
                        if len(menuIcons) != 1:
                            select -= 1
                            if select > len(menuIcons) - 1:
                                select = 0
                            if select < 0:
                                select = len(menuIcons) - 1
                            self.abilityAdvanceSound.play()
                    if event.key == pg.K_s or event.key == pg.K_d:
                        if len(menuIcons) != 1:
                            select += 1
                            if select > len(menuIcons) - 1:
                                select = 0
                            if select < 0:
                                select = len(menuIcons) - 1
                            self.abilityAdvanceSound.play()
                    if event.key == pg.K_m or event.key == pg.K_l:
                        if menuIcons[select].color != darkGray:
                            self.menuChooseSound.play()
                            for item in self.items:
                                print(item)
                                if menuIcons[select].info[0] == item[0]:
                                    if item[1] < 0:
                                        item[1] = 1
                                        self.coins -= menuIcons[select].info[1]
                                        self.buySomethingSound.play()
                                    else:
                                        item[1] += 1
                                        self.coins -= menuIcons[select].info[1]
                                        self.buySomethingSound.play()
                        else:
                            self.wrongSound.play()
                    if event.key == pg.K_TAB:
                        cursor.kill()
                        self.pause = False
                        going = False
                        self.menuCloseSound.play()

            cursor.update(menuIcons[select].rect, 60)
            name.update(menuIcons[select].info[-2])
            rect.center = cursor.rect.center
            menuCamera.update(rect)

            self.screen.fill(black)
            self.drawOverworldMenu()
            self.screen.blit(s, sRect)
            [a.draw(menuCamera.offset(a.rect)) for a in menuIcons]
            self.screen.blit(coinAmount, coinRect)
            self.screen.blit(coinIcon[currentFrame], coinIconRect)
            ptext.draw("X" + str(self.coins), (coinRect.left + 100, coinRect.centery), fontname=dialogueFont,
                       anchor=(0, 0.5),
                       surf=self.screen, fontsize=40)
            name.draw()
            self.screen.blit(cursor.image, menuCamera.offset(cursor.rect))
            self.fadeout.draw(self.screen)

            if self.pause:
                pg.display.flip()
            else:
                break

        self.pause = False

    def brosStats(self, song=None):
        going = True
        up = True
        alpha = 0
        rect = pg.rect.Rect(0, 0, 0, 0)
        rect.center = (150, 150)
        select = "Mario"
        name = EnemyNames(self, select + "'s Stats")

        Mhp = MenuIcon(self, (150, 200), "HP: " + str(self.player.stats["hp"]) + "/" + str(self.player.stats["maxHP"]),
                       hpSprite)
        Mbp = MenuIcon(self, (150, 300), "BP: " + str(self.player.stats["bp"]) + "/" + str(self.player.stats["maxBP"]),
                       bpSprite)
        Mpow = MenuIcon(self, (150, 400), "POW: " + str(self.player.stats["pow"]), powSprite)
        Mdefense = MenuIcon(self, (150, 500), "DEF: " + str(self.player.stats["def"]), defSprite)
        Mlevel = MenuIcon(self, (750, height / 2 - 80), "LEVEL: " + str(self.player.stats["level"]), None)
        Mexp = MenuIcon(self, (750, height / 2), "EXP: " + str(self.player.stats["exp"]), None)
        if self.player.stats["level"] < 100:
            MnextLevel = MenuIcon(self, (750, height / 2 + 40),
                                  "NEXT LEVEL: " + str(round((4 * (self.player.stats["level"] ** 3)) / 5) + 5), None)
        else:
            MnextLevel = MenuIcon(self, (750, height / 2 + 40),
                                  "NEXT LEVEL: N/A", None)
        Mstats = [Mhp, Mbp, Mpow, Mdefense, Mlevel, Mexp, MnextLevel]

        Lhp = MenuIcon(self, (150, 200),
                       "HP: " + str(self.follower.stats["hp"]) + "/" + str(self.follower.stats["maxHP"]), hpSprite)
        Lbp = MenuIcon(self, (150, 300),
                       "BP: " + str(self.follower.stats["bp"]) + "/" + str(self.follower.stats["maxBP"]), bpSprite)
        Lpow = MenuIcon(self, (150, 400), "POW: " + str(self.follower.stats["pow"]), powSprite)
        Ldefense = MenuIcon(self, (150, 500), "DEF: " + str(self.follower.stats["def"]), defSprite)
        Llevel = MenuIcon(self, (750, height / 2 - 80), "LEVEL: " + str(self.follower.stats["level"]), None)
        Lexp = MenuIcon(self, (750, height / 2), "EXP: " + str(self.follower.stats["exp"]), None)
        if self.follower.stats["level"] < 100:
            LnextLevel = MenuIcon(self, (750, height / 2 + 40),
                                  "NEXT LEVEL: " + str(round((4 * (self.follower.stats["level"] ** 3)) / 4.9) + 5),
                                  None)
        else:
            LnextLevel = MenuIcon(self, (750, height / 2 + 40),
                                  "NEXT LEVEL: N/A", None)
        Lstats = [Lhp, Lbp, Lpow, Ldefense, Llevel, Lexp, LnextLevel]

        while going:
            self.calculatePlayTime()
            if up:
                alpha += 10
                if alpha >= 255:
                    up = not up
            else:
                alpha -= 10
                if alpha <= 5:
                    up = not up
            self.fadeout.update()
            self.clock.tick(fps)
            if song is not None:
                self.playSong(song[0], song[1], song[2], cont=True, fadein=True)

            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)

            keys = pg.key.get_pressed()
            self.event = pg.event.get().copy()
            for event in self.event:
                if event == pg.QUIT or keys[pg.K_ESCAPE]:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_a or event.key == pg.K_d:
                        if select == "Mario":
                            select = "Luigi"
                        elif select == "Luigi":
                            select = "Mario"
                        self.abilityAdvanceSound.play()
                    if event.key == pg.K_m or event.key == pg.K_l:
                        self.pause = False
                        going = False
                        self.menuCloseSound.play()
                    if event.key == pg.K_TAB:
                        self.pause = False
                        going = False
                        self.menuCloseSound.play()

            name.update(select)

            self.screen.fill(black)
            if type(song) is list:
                self.drawOverworldMenu()
            else:
                self.drawBattleMenu()
            self.screen.blit(s, sRect)
            if select == "Mario":
                self.blit_alpha(self.screen, self.player.image, self.camera.offset(self.player.imgRect), alpha)
                [s.draw() for s in Mstats]
            elif select == "Luigi":
                self.blit_alpha(self.screen, self.follower.image, self.camera.offset(self.follower.imgRect), alpha)
                [s.draw() for s in Lstats]
            name.draw()
            self.fadeout.draw(self.screen)

            if self.pause:
                pg.display.flip()
            else:
                break

    def loadBattle(self, function, currentPoint=True, mario=True, luigi=True):
        self.player.isHammer = None
        self.follower.isHammer = None
        self.battleXp = 0
        self.battleCoins = 0
        if currentPoint:
            self.currentPoint += pg.mixer.music.get_pos()
        pg.mixer.music.stop()
        if mario and luigi:
            self.battleSound.play()
        elif mario:
            self.marioBattleSound.play()
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
        if self.leader == "mario":
            self.storeData["move"] = self.follower.moveQueue.copy()
        elif self.leader == "luigi":
            self.storeData["move"] = self.player.moveQueue.copy()
        self.storeData["luigi facing"] = self.follower.facing
        self.storeData["luigi abilities"] = self.follower.abilities
        if self.follower.prevAbility == 12:
            self.storeData["luigi current ability"] = self.follower.ability
        else:
            self.storeData["luigi current ability"] = self.follower.prevAbility
        self.prevRoom = self.room
        while going:
            self.calculatePlayTime()
            trans.update()
            self.screen.fill(black)
            self.drawOverworld()

            if trans.currentFrame == len(trans.sprites) - 1 and not pg.mixer.get_busy():
                self.pause = False
                eval(function)
                going = False

    def loadMultiEnemyDebug(self):
        self.room = "battle"
        self.sprites = []
        self.collision = []
        self.walls = pg.sprite.Group()
        self.npcs = pg.sprite.Group()
        self.enemies = []
        self.playsong = True
        self.firstLoop = True
        self.player.rect.center = (width / 2, 1278)
        self.playerCol = MarioCollision(self)
        self.follower.rect.center = (width / 2, 1278)
        self.followerCol = LuigiCollision(self)
        self.follower.moveQueue.clear()
        self.player.moveQueue.clear()
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
        self.map = Map("teehee valley battle", True)
        self.camera = Camera(self, self.map.width, self.map.height)
        # self.battle('self.playSong(54.965, 191.98, "New Soup Final Boss")')
        self.battle('self.playSong(8.148, 71.893, "Vs Linebeck")')

    def loadSingleEnemyDebug(self):
        self.room = "battle"
        self.sprites = []
        self.collision = []
        self.walls = pg.sprite.Group()
        self.npcs = pg.sprite.Group()
        self.enemies = []
        self.playsong = True
        if self.song_playing != "battle":
            self.firstLoop = True
        bowser = TutorialBowser()
        bowser.init(self, (self.map.width / 2, 1200))
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

        self.map = Map("teehee valley battle", True)
        self.camera = Camera(self, self.map.width, self.map.height)
        self.player.rect.center = (width / 2, 1278)
        self.playerCol = MarioCollision(self)
        self.follower.rect.center = (width / 2, 1278)
        self.follower.moveQueue.clear()
        self.player.moveQueue.clear()
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
        self.battle()

    def loadTutorialBowser(self):
        self.ui = pg.sprite.Group()
        MarioUI(self)
        self.room = "battle"
        self.sprites = []
        self.collision = []
        self.walls = pg.sprite.Group()
        self.npcs = pg.sprite.Group()
        self.enemies = []
        self.playsong = True
        if self.song_playing != "battle":
            self.firstLoop = True

        # Top Half Collision
        Wall(self, -50, 1117, 1889, 27)
        Wall(self, 655, 1138, 297, 48)

        # Bottom Half Collision
        Wall(self, -50, 1437, 1867, 20)
        Wall(self, 215, 1420, 307, 22)
        Wall(self, 690, 1392, 227, 50)
        Wall(self, 1143, 1392, 250, 50)

        self.map = Map("Bowser's Castle", True)
        self.camera = Camera(self, self.map.width, self.map.height)
        bowser = TutorialBowser()
        bowser.init(self, (self.map.width / 2, 1200))
        self.player.rect.center = (self.map.width / 2, 1278)
        self.player.facing = "up"
        self.playerCol = MarioCollision(self)
        self.follower.rect.center = (0, 0)
        self.follower.stats["hp"] = 0
        self.follower.moveQueue.clear()
        self.player.moveQueue.clear()
        self.followerCol = LuigiCollision(self)
        self.sprites.append(self.follower)
        self.sprites.append(self.player)
        self.follower.stepSound = self.stoneSound
        self.player.stepSound = self.stoneSound
        try:
            self.player.stats = self.storeData["mario stats"]
            self.follower.stats = self.storeData["luigi stats"]
        except:
            pass
        self.firstTutorialBattle("self.playSong(24.873, 74.996, 'King Bowser')")

    def firstTutorialBattle(self, song=None):
        menud = False
        self.countdown = 0
        self.playing = True
        self.player.ability = self.storeData["mario current ability"]
        self.player.abilities = self.storeData["mario abilities"]
        self.follower.ability = self.storeData["luigi current ability"]
        self.follower.abilities = self.storeData["luigi abilities"]
        text = ["Mario!/p When was the last time\nyou battled?",
                "I'd better give you a refresher on\nthe basics of battling.",
                "You can move around the battlefield\nby pressing <<RW, A, S,>> or <<RD>>.",
                "Try your best to dodge Bowser's\nattacks by pressing <<RM>> to jump.",
                "If you get hit, it's not the end of\nthe world, your <<RHP>> will lower.",
                "However, if your <<RHP>> reaches <<B0>>, then\nit IS the end of the world.",
                "But, the same will happen with\nBowser once you jump on him\nenough times.",
                "So, try your best to jump on Bowser\nuntill he gets K.O'd!",
                "Also, if you press <<RTAB>>, then you can\naccess the <<BMenu>> for additional\ninformation.",
                "But BE CAREFUL!/p When you use\nthe menu, you won't be able to use\nit again for a while."]
        self.cameraRect = CameraRect()
        textboxd = False
        textbox = None
        if song is None:
            pg.mixer.music.load("music/battle.ogg")
            pg.mixer.music.play(-1)
        while len(self.enemies) > 0:
            self.calculatePlayTime()
            if song is not None:
                eval(song)
            self.clock.tick(fps)
            self.events()
            for event in self.event:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_TAB:
                        if self.countdown == 0:
                            self.player.canMove = False
                            self.follower.canMove = False
                            menud = True
                            self.battleMenu(song)
                        else:
                            self.wrongSound.play()
            if not textboxd and self.tutorials:
                if len(self.effects) == 0:
                    if textbox is None:
                        textbox = TextBox(self, self.player, text, sound="starlow")
                    textbox.update()
                    if textbox.complete:
                        textboxd = True
                else:
                    self.updateBattle()
            else:
                self.updateBattle()
            self.screen.fill(black)
            self.drawBattle()
            if self.countdown != 0:
                self.countdown -= 1
            if self.player.stats["hp"] <= 0 and self.follower.stats["hp"] <= 0:
                self.gameOver()
            if menud:
                self.player.canMove = True
                self.follower.canMove = True
                menud = False

        self.battleOver(luigi=False, tutorial=True)

    def battle(self, song=None):
        menud = False
        self.countdown = 0
        self.playing = True
        self.player.ability = self.storeData["mario current ability"]
        self.player.abilities = self.storeData["mario abilities"]
        self.follower.ability = self.storeData["luigi current ability"]
        self.follower.abilities = self.storeData["luigi abilities"]
        self.cameraRect = CameraRect()
        if song is None:
            pg.mixer.music.set_volume(1)
            pg.mixer.music.load("music/battle.ogg")
            pg.mixer.music.play(-1)
        while self.playing:
            self.calculatePlayTime()
            if song is not None:
                eval(song)
            self.clock.tick(fps)
            self.events()
            for event in self.event:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_TAB:
                        if self.countdown == 0:
                            self.player.canMove = False
                            self.follower.canMove = False
                            menud = True
                            self.battleMenu(song)
                        else:
                            self.wrongSound.play()
            self.updateBattle()
            self.screen.fill(black)
            self.drawBattle()
            if self.countdown != 0:
                self.countdown -= 1
            if self.player.stats["hp"] <= 0 and self.follower.stats["hp"] <= 0:
                self.gameOver()
            if menud:
                self.player.canMove = True
                self.follower.canMove = True
                menud = False
            if len(self.enemies) == 0:
                self.battleOver()

    def battleMenu(self, song=None):
        self.menuOpenSound.play()
        self.pause = True
        going = True
        select = 0
        itemMenu = pg.image.load("sprites/ui/itemsIcon.png").convert_alpha()
        itemRect = itemMenu.get_rect()
        checkEnemies = pg.image.load("sprites/ui/Enemy Check.png").convert_alpha()
        checkRect = checkEnemies.get_rect()
        checkRect.center = (width / 2, height - 100)
        if self.player.attackPieces[0][1] >= 10:
            brosMenu = pg.image.load("sprites/ui/brosAttacksIcon.png").convert_alpha()
            brosRect = brosMenu.get_rect()
            itemRect.center = (((width / 2) - (itemRect.width / 2)) - 100, height / 2)
            brosRect.center = (((width / 2) + (brosRect.width / 2)) + 100, height / 2)
        else:
            itemRect.center = (width / 2, height / 2)
        name = EnemyNames(self, "Items")
        cursor = Cursor(self, itemRect)
        print(song)
        while going and self.pause:
            self.calculatePlayTime()
            self.clock.tick(fps)
            if song is not None:
                eval(song)

            self.fadeout.update()
            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)

            keys = pg.key.get_pressed()
            self.event = pg.event.get().copy()
            for event in self.event:
                if event == pg.QUIT or keys[pg.K_ESCAPE]:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_a or event.key == pg.K_d:
                        if self.player.attackPieces[0][1] >= 10:
                            if select == 0:
                                select = 1
                            elif select == 1:
                                select = 0
                            if select == 2:
                                if event.key == pg.K_a:
                                    select = 0
                                else:
                                    select = 1
                            self.abilityAdvanceSound.play()
                        else:
                            if select == 2:
                                select = 0
                    if event.key == pg.K_w or event.key == pg.K_s:
                        if select != 2:
                            select = 2
                        else:
                            select = 0
                        self.abilityAdvanceSound.play()
                    if event.key == pg.K_m or event.key == pg.K_l:
                        if select == 1:
                            if self.player.dead or self.follower.dead:
                                self.wrongSound.play()
                            else:
                                going = False
                                self.menuChooseSound.play()
                                self.brosAttackSelect(song)
                        if select == 0:
                            canMenu = False
                            for item in self.items:
                                if item[1] >= 0:
                                    canMenu = True
                            if canMenu:
                                going = False
                                self.menuChooseSound.play()
                                self.itemSelect(song)
                            else:
                                self.wrongSound.play()
                        if select == 2:
                            self.menuChooseSound.play()
                            going = False
                            self.enemySelect("self.enemyCheck(enemies[0], song=song)", song=song, fadeout=False)
                    if event.key == pg.K_TAB:
                        cursor.kill()
                        self.pause = False
                        going = False
                        self.menuCloseSound.play()

            if select == 0:
                name.update("Items")
                cursor.update(itemRect, 60)
            elif select == 1:
                name.update("Bros. Attacks")
                cursor.update(brosRect, 60)
            elif select == 2:
                name.update("Check Enemies")
                cursor.update(checkRect, 60)

            self.drawBattleMenu()
            if self.player.attackPieces[0][1] >= 10:
                self.screen.blit(brosMenu, brosRect)
            self.screen.blit(itemMenu, itemRect)
            self.screen.blit(s, sRect)
            canMenu = False
            for item in self.items:
                if item[1] >= 0:
                    canMenu = True
            if canMenu:
                self.screen.blit(itemMenu, itemRect)
            if self.player.attackPieces[0][1] >= 10 and not self.player.dead and not self.follower.dead:
                self.screen.blit(brosMenu, brosRect)
            self.screen.blit(checkEnemies, checkRect)
            self.screen.blit(cursor.image, cursor.rect)
            name.draw()
            self.fadeout.draw(self.screen)

            if self.pause:
                pg.display.flip()

    def brosAttackSelect(self, song=None):
        self.player.alpha = 255
        self.follower.alpha = 255
        cursor = Cursor(self, self.player.imgRect)
        name = EnemyNames(self, "Mario")
        going = True
        up = True
        alpha = 0
        select = 0
        while going:
            if up:
                alpha += 10
                if alpha >= 255:
                    up = not up
            else:
                alpha -= 10
                if alpha <= 5:
                    up = not up
            self.clock.tick(fps)
            if song is not None:
                eval(song)

            self.fadeout.update()
            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)

            keys = pg.key.get_pressed()
            self.event = pg.event.get().copy()
            for event in self.event:
                if event == pg.QUIT or keys[pg.K_ESCAPE]:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_a or event.key == pg.K_d:
                        if select == 0:
                            select = 1
                        elif select == 1:
                            select = 0
                        self.abilityAdvanceSound.play()
                    if event.key == pg.K_m or event.key == pg.K_l:
                        if select == 1:
                            going = False
                            self.menuChooseSound.play()
                            self.luigiAttackSelect(song)
                        if select == 0:
                            self.menuChooseSound.play()
                            going = False
                            self.marioAttackSelect(song)
                    if event.key == pg.K_TAB:
                        cursor.kill()
                        self.pause = False
                        going = False
                        self.menuCloseSound.play()

            if select == 0:
                name.update("Mario")
                cursor.update(self.player.imgRect, 60)
            elif select == 1:
                name.update("Luigi")
                cursor.update(self.follower.imgRect, 60)

            self.drawBattleMenu()
            self.screen.blit(s, sRect)
            if select == 0:
                self.blit_alpha(self.screen, self.player.image, self.camera.offset(self.player.imgRect), alpha)
            elif select == 1:
                self.blit_alpha(self.screen, self.follower.image, self.camera.offset(self.follower.imgRect), alpha)
            self.screen.blit(cursor.image, self.camera.offset(cursor.rect))
            name.draw()
            self.fadeout.draw(self.screen)

            if self.pause:
                pg.display.flip()

    def itemSelect(self, song=None):
        cursor = Cursor(self, self.player.imgRect)
        marioBP = MarioRecoverables(self)
        luigiBP = LuigiRecoverables(self)
        bp = [marioBP, luigiBP]
        going = True
        menuIcons = []
        rect = pg.rect.Rect(0, 0, 0, 0)
        rect.center = (150, 150)
        select = 0
        for item in self.items:
            if item[1] == 1:
                if item[0] == "Star Cand":
                    menuIcons.append(MenuIcon(self, rect.center, item[0] + "y X" + str(
                        item[1]), item[2], item))
                else:
                    menuIcons.append(MenuIcon(self, rect.center, item[0] + " X" + str(
                        item[1]), item[2], item))
                rect.y += 100
            elif item[1] >= 0:
                if item[0] == "Star Cand":
                    menuIcons.append(MenuIcon(self, rect.center, item[0] + "ies X" + str(
                        item[1]), item[2], item))
                else:
                    menuIcons.append(MenuIcon(self, rect.center, item[0] + "s X" + str(
                        item[1]), item[2], item))
                rect.y += 100

        for icon in menuIcons:
            icon.color = darkGray
            if icon.info[1] > 0:
                try:
                    if self.player.stats[icon.info[3]] < self.player.stats[icon.info[4]] - 1:
                        icon.color = white
                    if self.follower.stats[icon.info[3]] < self.follower.stats[icon.info[4]] - 1:
                        icon.color = white
                except:
                    if self.player.stats[icon.info[3]] < icon.info[4] - 1:
                        icon.color = white
                    if self.follower.stats[icon.info[3]] < icon.info[4] - 1:
                        icon.color = white
                if "Star Cand" in icon.info[0]:
                    if self.player.stats["hp"] < self.player.stats["maxHP"] or self.player.stats["bp"] < \
                            self.player.stats["maxBP"]:
                        icon.color = white
                    if self.follower.stats["hp"] < self.follower.stats["maxHP"] or self.follower.stats["bp"] < \
                            self.follower.stats["maxBP"]:
                        icon.color = white
                if "1-UP" in icon.info[0]:
                    if self.player.dead or self.follower.dead:
                        icon.color = white

        if len(menuIcons) >= 6:
            menuCamera = Camera(self, width, menuIcons[-1].rect.bottom + (width / 2))
        else:
            menuCamera = Camera(self, width, height)
        name = EnemyNames(self, menuIcons[0].info[-2],
                          pg.image.load("sprites/ui/enemySelectionFullScreen.png").convert_alpha())

        while going:
            self.calculatePlayTime()
            self.fadeout.update()
            self.clock.tick(fps)
            if song is not None:
                if type(song) is str:
                    eval(song)
                elif type(song) is list:
                    self.playSong(song[0], song[1], song[2], cont=True, fadein=True)

            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)

            keys = pg.key.get_pressed()
            self.event = pg.event.get().copy()
            for event in self.event:
                if event == pg.QUIT or keys[pg.K_ESCAPE]:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_w or event.key == pg.K_a:
                        if len(menuIcons) != 1:
                            select -= 1
                            if select > len(menuIcons) - 1:
                                select = 0
                            if select < 0:
                                select = len(menuIcons) - 1
                            self.abilityAdvanceSound.play()
                    if event.key == pg.K_s or event.key == pg.K_d:
                        if len(menuIcons) != 1:
                            select += 1
                            if select > len(menuIcons) - 1:
                                select = 0
                            if select < 0:
                                select = len(menuIcons) - 1
                            self.abilityAdvanceSound.play()
                    if event.key == pg.K_m or event.key == pg.K_l:
                        if menuIcons[select].color != darkGray:
                            going = False
                            self.menuChooseSound.play()
                            self.brosItemSelect(song, menuIcons[select].info)
                        else:
                            self.wrongSound.play()
                    if event.key == pg.K_TAB:
                        cursor.kill()
                        self.pause = False
                        going = False
                        self.menuCloseSound.play()

            cursor.update(menuIcons[select].rect, 60)
            name.update(menuIcons[select].info[-2])
            rect.center = cursor.rect.center
            menuCamera.update(rect)
            recoverable = menuIcons[select].info[3]

            self.screen.fill(black)
            if type(song) is list:
                self.drawOverworldMenu()
            else:
                self.drawBattleMenu()
            self.screen.blit(s, sRect)
            [a.draw(menuCamera.offset(a.rect)) for a in menuIcons]
            [bp.draw(recoverable) for bp in bp]
            name.draw()
            self.screen.blit(cursor.image, menuCamera.offset(cursor.rect))
            self.fadeout.draw(self.screen)

            if self.pause:
                pg.display.flip()
            else:
                break

    def brosItemSelect(self, song=None, info=None):
        self.player.alpha = 255
        self.follower.alpha = 255
        cursor = Cursor(self, self.player.imgRect)
        name = EnemyNames(self, "Mario")
        going = True
        up = True
        alpha = 0
        select = 0
        while going:
            if up:
                alpha += 10
                if alpha >= 255:
                    up = not up
            else:
                alpha -= 10
                if alpha <= 5:
                    up = not up
            self.clock.tick(fps)
            if song is not None:
                if type(song) is str:
                    eval(song)
                elif type(song) is list:
                    self.playSong(song[0], song[1], song[2], cont=True, fadein=True)

            self.fadeout.update()
            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)

            keys = pg.key.get_pressed()
            self.event = pg.event.get().copy()
            for event in self.event:
                if event == pg.QUIT or keys[pg.K_ESCAPE]:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_a or event.key == pg.K_d:
                        if select == 0:
                            select = 1
                        elif select == 1:
                            select = 0
                        self.abilityAdvanceSound.play()
                    if event.key == pg.K_m or event.key == pg.K_l:
                        if select == 1:
                            self.pause = False
                            going = False
                            self.menuChooseSound.play()
                            if "Nut" in info[0]:
                                if "Max" in info[0]:
                                    self.follower.stats["hp"] = self.follower.stats["maxHP"]
                                    self.player.stats["hp"] = self.player.stats["maxHP"]
                                else:
                                    self.follower.stats[info[3]] += info[-1]
                                    self.player.stats[info[3]] += info[-1]
                            elif "Star Cand" in info[0]:
                                self.follower.stats["hp"] = self.follower.stats["maxHP"]
                                self.follower.stats["bp"] = self.follower.stats["maxBP"]
                            elif "Max " in info[0]:
                                self.follower.stats[info[3]] = self.follower.stats[info[4]]
                            elif "1-UP " in info[0]:
                                if "Mushroom" in info[0]:
                                    self.follower.stats["hp"] = round(self.follower.stats["maxHP"] / 2)
                                else:
                                    self.follower.stats["hp"] = self.follower.stats["maxHP"]
                                self.follower.dead = False
                                center = self.follower.rect.center
                                self.follower.shadow = self.follower.shadowFrames["normal"]
                                self.follower.rect = self.follower.shadow.get_rect()
                                self.follower.rect.center = center
                                self.follower.jumping = True
                                self.jumpSound.play()
                            else:
                                self.follower.stats[info[3]] += info[-1]

                            if self.player.stats["hp"] > self.player.stats["maxHP"]:
                                self.player.stats["hp"] = self.player.stats["maxHP"]
                            if self.player.stats["bp"] > self.player.stats["maxBP"]:
                                self.player.stats["bp"] = self.player.stats["maxBP"]
                            if self.follower.stats["hp"] > self.follower.stats["maxHP"]:
                                self.follower.stats["hp"] = self.follower.stats["maxHP"]
                            if self.follower.stats["bp"] > self.follower.stats["maxBP"]:
                                self.follower.stats["bp"] = self.follower.stats["maxBP"]
                            info[1] -= 1
                            pg.event.clear()
                        if select == 0:
                            self.pause = False
                            self.menuChooseSound.play()
                            going = False
                            if "Nut" in info[0]:
                                if "Max" in info[0]:
                                    self.follower.stats["hp"] = self.follower.stats["maxHP"]
                                    self.player.stats["hp"] = self.player.stats["maxHP"]
                                else:
                                    self.follower.stats[info[3]] += info[-1]
                                    self.player.stats[info[3]] += info[-1]
                            elif "Star Cand" in info[0]:
                                self.player.stats["hp"] = self.player.stats["maxHP"]
                                self.player.stats["bp"] = self.player.stats["maxBP"]
                            elif "Max " in info[0]:
                                self.player.stats[info[3]] = self.player.stats[info[4]]
                            elif "1-UP " in info[0]:
                                if "Mushroom" in info[0]:
                                    self.player.stats["hp"] = round(self.player.stats["maxHP"] / 2)
                                else:
                                    self.player.stats["hp"] = self.player.stats["maxHP"]
                                self.player.dead = False
                                center = self.player.rect.center
                                self.player.shadow = self.player.shadowFrames["normal"]
                                self.player.rect = self.player.shadow.get_rect()
                                self.player.rect.center = center
                                self.player.jumping = True
                                self.jumpSound.play()
                            else:
                                self.player.stats[info[3]] += info[-1]
                            if self.player.stats["hp"] > self.player.stats["maxHP"]:
                                self.player.stats["hp"] = self.player.stats["maxHP"]
                            if self.player.stats["bp"] > self.player.stats["maxBP"]:
                                self.player.stats["bp"] = self.player.stats["maxBP"]
                            if self.follower.stats["hp"] > self.follower.stats["maxHP"]:
                                self.follower.stats["hp"] = self.follower.stats["maxHP"]
                            if self.follower.stats["bp"] > self.follower.stats["maxBP"]:
                                self.follower.stats["bp"] = self.follower.stats["maxBP"]
                            info[1] -= 1
                            pg.event.clear()
                        if "1-UP" in info[0]:
                            self.fullRestoreSound.play()
                        elif "Super" in info[0]:
                            self.medRestoreSound.play()
                        elif "Ultra" in info[0]:
                            self.medRestoreSound.play()
                        elif "Max" in info[0]:
                            self.fullRestoreSound.play()
                        else:
                            self.smallRestoreSound.play()

                        self.countdown = fps * 10
                    if event.key == pg.K_TAB:
                        cursor.kill()
                        self.pause = False
                        going = False
                        self.menuCloseSound.play()

            if select == 0:
                name.update("Mario")
                cursor.update(self.player.imgRect, 60)
            elif select == 1:
                name.update("Luigi")
                cursor.update(self.follower.imgRect, 60)

            if type(song) is list:
                self.drawOverworldMenu()
            else:
                self.drawBattleMenu()
            self.screen.blit(s, sRect)
            if select == 0:
                self.blit_alpha(self.screen, self.player.image, self.camera.offset(self.player.imgRect), alpha)
            elif select == 1:
                self.blit_alpha(self.screen, self.follower.image, self.camera.offset(self.follower.imgRect), alpha)
            self.screen.blit(cursor.image, self.camera.offset(cursor.rect))
            name.draw()
            self.fadeout.draw(self.screen)

            if self.pause:
                pg.display.flip()

    def marioAttackSelect(self, song=None):
        cursor = Cursor(self, self.player.imgRect)
        marioBP = MarioRecoverables(self)
        luigiBP = LuigiRecoverables(self)
        bp = [marioBP, luigiBP]
        going = True
        menuIcons = []
        rect = pg.rect.Rect(0, 0, 0, 0)
        rect.center = (150, 150)
        counter = 0
        select = 0
        for pieces in self.player.attackPieces:
            if pieces[1] == 10:
                menuIcons.append(MenuIcon(self, rect.center, self.player.brosAttacks[counter][0] + " (" + str(
                    self.player.brosAttacks[counter][4]) + " BP)", self.player.brosAttacks[counter][2]))
            elif 10 > pieces[1] > 0:
                menuIcons.append(MenuIcon(self, rect.center, pieces[0] + " Attack Pieces: " + str(pieces[1]) + "/10"))
            rect.y += 100
            counter += 1

        for icon in menuIcons:
            if self.player.attackPieces[int((icon.rect.centery - 150) / 100)][1] < 10:
                icon.color = darkGray

        while going:
            self.calculatePlayTime()
            self.fadeout.update()
            self.clock.tick(fps)
            if song is not None:
                eval(song)

            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)

            keys = pg.key.get_pressed()
            self.event = pg.event.get().copy()
            for event in self.event:
                if event == pg.QUIT or keys[pg.K_ESCAPE]:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_w or event.key == pg.K_a:
                        if len(menuIcons) != 1:
                            select -= 1
                            if select > len(menuIcons) - 1:
                                select = 0
                            if select < 0:
                                select = len(menuIcons) - 1
                            self.abilityAdvanceSound.play()
                    if event.key == pg.K_s or event.key == pg.K_d:
                        if len(menuIcons) != 1:
                            select += 1
                            if select > len(menuIcons) - 1:
                                select = 0
                            if select < 0:
                                select = len(menuIcons) - 1
                            self.abilityAdvanceSound.play()
                    if event.key == pg.K_m or event.key == pg.K_l:
                        if self.player.attackPieces[int((menuIcons[select].rect.centery - 150) / 100)][1] == 10:
                            if self.player.stats["bp"] >= \
                                    self.player.brosAttacks[int((menuIcons[select].rect.centery - 150) / 100)][4]:
                                self.player.stats["bp"] -= \
                                    self.player.brosAttacks[int((menuIcons[select].rect.centery - 150) / 100)][4]
                                self.menuChooseSound.play()
                                self.enemySelect(
                                    self.player.brosAttacks[int((menuIcons[select].rect.centery - 150) / 100)][1],
                                    self.player.brosAttacks[int((menuIcons[select].rect.centery - 150) / 100)][3], song,
                                    cost=self.player.brosAttacks[int((menuIcons[select].rect.centery - 150) / 100)][4],
                                    bro="mario")
                            else:
                                self.wrongSound.play()
                        else:
                            self.wrongSound.play()
                    if event.key == pg.K_TAB:
                        cursor.kill()
                        self.pause = False
                        going = False
                        self.menuCloseSound.play()

            cursor.update(menuIcons[select].rect, 60)

            for icon in menuIcons:
                if self.player.attackPieces[int((icon.rect.centery - 150) / 100)][1] < 10:
                    icon.color = darkGray
                elif self.player.brosAttacks[int((icon.rect.centery - 150) / 100)][4] > self.player.stats["bp"]:
                    icon.color = darkGray

            self.screen.fill(black)
            self.drawBattleMenu()
            self.screen.blit(s, sRect)
            [a.draw() for a in menuIcons]
            [bp.draw() for bp in bp]
            self.screen.blit(cursor.image, cursor.rect)
            self.fadeout.draw(self.screen)

            if self.pause:
                pg.display.flip()
            else:
                break

    def luigiAttackSelect(self, song=None):
        cursor = Cursor(self, self.follower.imgRect)
        marioBP = MarioRecoverables(self)
        luigiBP = LuigiRecoverables(self)
        bp = [marioBP, luigiBP]
        going = True
        menuIcons = []
        rect = pg.rect.Rect(0, 0, 0, 0)
        rect.center = (150, 150)
        counter = 0
        select = 0
        for pieces in self.follower.attackPieces:
            if pieces[1] == 10:
                menuIcons.append(MenuIcon(self, rect.center, self.follower.brosAttacks[counter][0] + " (" + str(
                    self.follower.brosAttacks[counter][4]) + " BP)", self.follower.brosAttacks[counter][2]))
            elif 10 > pieces[1] > 0:
                menuIcons.append(MenuIcon(self, rect.center, pieces[0] + " Attack Pieces: " + str(pieces[1]) + "/10"))
            rect.y += 100
            counter += 1

        for icon in menuIcons:
            if self.follower.attackPieces[int((icon.rect.centery - 150) / 100)][1] < 10:
                icon.color = darkGray

        while going:
            self.calculatePlayTime()
            self.fadeout.update()
            self.clock.tick(fps)
            if song is not None:
                eval(song)

            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)

            keys = pg.key.get_pressed()
            self.event = pg.event.get().copy()
            for event in self.event:
                if event == pg.QUIT or keys[pg.K_ESCAPE]:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_w or event.key == pg.K_a:
                        if len(menuIcons) != 1:
                            select -= 1
                            if select > len(menuIcons) - 1:
                                select = 0
                            if select < 0:
                                select = len(menuIcons) - 1
                            self.abilityAdvanceSound.play()
                    if event.key == pg.K_s or event.key == pg.K_d:
                        if len(menuIcons) != 1:
                            select += 1
                            if select > len(menuIcons) - 1:
                                select = 0
                            if select < 0:
                                select = len(menuIcons) - 1
                            self.abilityAdvanceSound.play()
                    if event.key == pg.K_m or event.key == pg.K_l:
                        if self.follower.attackPieces[int((menuIcons[select].rect.centery - 150) / 100)][1] == 10:
                            if self.follower.stats["bp"] >= \
                                    self.follower.brosAttacks[int((menuIcons[select].rect.centery - 150) / 100)][4]:
                                self.follower.stats["bp"] -= \
                                    self.follower.brosAttacks[int((menuIcons[select].rect.centery - 150) / 100)][4]
                                self.menuChooseSound.play()
                                self.enemySelect(
                                    self.follower.brosAttacks[int((menuIcons[select].rect.centery - 150) / 100)][1],
                                    self.follower.brosAttacks[int((menuIcons[select].rect.centery - 150) / 100)][3],
                                    song,
                                    cost=self.follower.brosAttacks[int((menuIcons[select].rect.centery - 150) / 100)][
                                        4],
                                    bro="luigi")
                            else:
                                self.wrongSound.play()
                        else:
                            self.wrongSound.play()
                    if event.key == pg.K_TAB:
                        cursor.kill()
                        self.pause = False
                        going = False
                        self.menuCloseSound.play()

            cursor.update(menuIcons[select].rect, 60)

            for icon in menuIcons:
                if self.follower.attackPieces[int((icon.rect.centery - 150) / 100)][1] < 10:
                    icon.color = darkGray
                elif self.follower.brosAttacks[int((icon.rect.centery - 150) / 100)][4] > self.follower.stats["bp"]:
                    icon.color = darkGray

            self.screen.fill(black)
            self.drawBattleMenu()
            self.screen.blit(s, sRect)
            [a.draw() for a in menuIcons]
            [bp.draw() for bp in bp]
            self.screen.blit(cursor.image, cursor.rect)
            self.fadeout.draw(self.screen)

            if self.pause:
                pg.display.flip()
            else:
                break

    def enemySelect(self, command, size=0, song=None, fadeout=True, bro="mario", cost=0):
        going = True
        attacking = False
        alpha = 255
        up = True
        for enemy in self.enemies:
            if enemy.stats["hp"] <= 0:
                self.battleCoins += enemy.stats["coins"]
                self.battleXp += enemy.stats["exp"]
                self.enemies.remove(enemy)
                self.sprites.remove(enemy)
        self.enemies.sort(key=self.sortByXPos)
        if len(self.enemies) != 0:
            cursor = Cursor(self, self.enemies[0].imgRect)
            enemyNames = EnemyNames(self, self.enemies[0].stats["name"])
        else:
            going = False
        number = 0
        colRect = pg.rect.Rect(0, 0, size, size)
        while going:
            self.calculatePlayTime()
            self.clock.tick(fps)
            if up:
                alpha += 10
                if alpha >= 255:
                    up = not up
            else:
                alpha -= 10
                if alpha <= 5:
                    up = not up
            if song is not None:
                eval(song)
            self.fadeout.update()
            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)
            keys = pg.key.get_pressed()
            cursor.update(self.enemies[number].imgRect, 60)
            enemyNames.update(self.enemies[number].stats["name"])
            self.cameraRect.update(self.enemies[number].rect, 60)
            self.camera.update(self.cameraRect.rect)
            self.ui.update()
            self.event = pg.event.get().copy()
            for event in self.event:
                if event == pg.QUIT or keys[pg.K_ESCAPE]:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_d:
                        if number < len(self.enemies):
                            number = (number + 1) % (len(self.enemies))
                        if len(self.enemies) > 1:
                            self.abilityAdvanceSound.play()
                    if event.key == pg.K_a:
                        if number < len(self.enemies):
                            number = (number - 1) % (len(self.enemies))
                        if len(self.enemies) > 1:
                            self.abilityAdvanceSound.play()
                    if event.key == pg.K_m or event.key == pg.K_l:
                        cursor.kill()
                        self.menuChooseSound.play()
                        self.countdown = fps * 10
                        if fadeout:
                            going = False
                            attacking = True
                        else:
                            going = False
                            enemies = [self.enemies[number]]
                            for enemy in self.enemies:
                                if colRect.colliderect(enemy.imgRect) and colRect.center != enemy.rect.center:
                                    enemies.append(enemy)
                            eval(command)
                    if event.key == pg.K_TAB:
                        if bro == "mario":
                            self.player.stats["bp"] += cost
                        else:
                            self.follower.stats["bp"] += cost
                        self.menuCloseSound.play()
                        cursor.kill()
                        going = False
                        self.pause = False
            self.drawBattleMenu()
            self.blit_alpha(self.screen, self.enemies[number].image,
                            self.camera.offset(self.enemies[number].imgRect),
                            255)
            self.screen.blit(s, sRect)
            colRect.center = self.enemies[number].rect.center
            for enemy in self.enemies:
                if colRect.colliderect(enemy.rect) and enemy.rect.center != colRect.center:
                    self.blit_alpha(self.screen, enemy.image,
                                    self.camera.offset(enemy.imgRect),
                                    enemy.alpha)
            self.blit_alpha(self.screen, self.enemies[number].image,
                            self.camera.offset(self.enemies[number].imgRect),
                            alpha)
            pg.draw.rect(self.screen, darkGray,
                         self.camera.offset(
                             pg.Rect(self.enemies[number].rect.left, self.enemies[number].imgRect.bottom + 12,
                                     self.enemies[number].rect.width, 10)))
            if self.enemies[number].rectHP >= 0:
                pg.draw.rect(self.screen, red, self.camera.offset(
                    pg.Rect(self.enemies[number].rect.left, self.enemies[number].imgRect.bottom + 12,
                            (self.enemies[number].rect.width * (
                                    self.enemies[number].rectHP / self.enemies[number].stats["maxHP"])), 10)))
            pg.draw.rect(self.screen, black,
                         self.camera.offset(
                             pg.Rect(self.enemies[number].rect.left, self.enemies[number].imgRect.bottom + 12,
                                     self.enemies[number].rect.width, 10)),
                         1)

            self.screen.blit(cursor.image, self.camera.offset(cursor.rect))
            enemyNames.draw()

            [self.screen.blit(fad.image, (0, 0)) for fad in self.fadeout]

            if self.pause:
                pg.display.flip()
        if attacking:
            if up:
                alpha += 10
                if alpha >= 255:
                    up = not up
            else:
                alpha -= 10
                if alpha <= 5:
                    up = not up
            fad = Fadeout(self)
            enemies = [self.enemies[number]]
            for enemy in self.enemies:
                if colRect.colliderect(enemy.imgRect) and colRect.center != enemy.rect.center:
                    enemies.append(enemy)
            while True:
                self.calculatePlayTime()
                self.clock.tick(fps)
                s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
                sRect = s.get_rect()
                s.fill(black)
                s.set_alpha(125)
                keys = pg.key.get_pressed()
                cursor.update(self.enemies[number].imgRect, 60)
                enemyNames.update(self.enemies[number].stats["name"])
                self.cameraRect.update(self.enemies[number].rect, 60)
                self.camera.update(self.cameraRect.rect)
                self.ui.update()
                self.fadeout.update()
                if fad.alpha >= 255:
                    cursor.kill()
                    self.pause = False
                    self.room = "bros attack"
                    eval(command)
                    break
                self.event = pg.event.get().copy()
                for event in self.event:
                    if event == pg.QUIT or keys[pg.K_ESCAPE]:
                        pg.quit()
                self.drawBattleMenu()
                self.blit_alpha(self.screen, self.enemies[number].image,
                                self.camera.offset(self.enemies[number].imgRect),
                                255)
                self.screen.blit(s, sRect)
                for enemy in self.enemies:
                    if colRect.colliderect(enemy.imgRect):
                        self.blit_alpha(self.screen, enemy.image,
                                        self.camera.offset(enemy.imgRect),
                                        enemy.alpha)
                self.blit_alpha(self.screen, self.enemies[number].image,
                                self.camera.offset(self.enemies[number].imgRect),
                                alpha)
                pg.draw.rect(self.screen, darkGray,
                             self.camera.offset(
                                 pg.Rect(self.enemies[number].rect.left, self.enemies[number].imgRect.bottom + 12,
                                         self.enemies[number].rect.width, 10)))
                if self.enemies[number].rectHP >= 0:
                    pg.draw.rect(self.screen, red, self.camera.offset(
                        pg.Rect(self.enemies[number].rect.left, self.enemies[number].imgRect.bottom + 12,
                                (self.enemies[number].rect.width * (
                                        self.enemies[number].rectHP / self.enemies[number].stats["maxHP"])), 10)))
                pg.draw.rect(self.screen, black,
                             self.camera.offset(
                                 pg.Rect(self.enemies[number].rect.left, self.enemies[number].imgRect.bottom + 12,
                                         self.enemies[number].rect.width, 10)),
                             1)

                self.screen.blit(cursor.image, self.camera.offset(cursor.rect))
                enemyNames.draw()

                [self.screen.blit(fad.image, (0, 0)) for fad in self.fadeout]

                if self.pause:
                    pg.display.flip()

    def enemyCheck(self, enemy, song=None):
        TextBox(self, enemy, enemy.description, sound="starlow")
        alpha = 255
        up = True
        while not enemy.textbox.closing:
            self.calculatePlayTime()
            self.clock.tick(fps)
            if song is not None:
                eval(song)

            self.fadeout.update()
            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)

            if up:
                alpha += 10
                if alpha >= 255:
                    up = not up
            else:
                alpha -= 10
                if alpha <= 5:
                    up = not up

            self.event = pg.event.get().copy()

            enemy.textbox.update()

            self.screen.fill(black)
            self.drawBattleMenu()
            self.blit_alpha(self.screen, enemy.image, self.camera.offset(enemy.imgRect), 255)
            self.screen.blit(s, sRect)
            self.blit_alpha(self.screen, enemy.image, self.camera.offset(enemy.imgRect), alpha)
            enemy.textbox.draw()

            pg.display.flip()

        self.pause = False

    def greenShell(self, enems, song=None):
        going = True
        started = False
        button = pg.image.load("sprites/bros attack start.png").convert_alpha()
        buRect = button.get_rect()
        buRect.center = (width / 2, height / 2)
        s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
        sRect = s.get_rect()
        s.fill(black)
        s.set_alpha(125)
        background = pg.image.load("sprites/maps/Bros Attack.png")
        bRect = background.get_rect()
        shell = GreenShell(self, 50)
        mario = MarioShell(self, shell)
        luigi = LuigiShell(self, shell)
        self.camera.update(mario.rect)
        sprites = [mario, luigi]
        enemies = []
        for enemy in enems:
            command = enemy.stats["name"] + "BrosAttack(self, enemy)"
            en = eval(command)
            sprites.append(en)
            enemies.append(en)
        while going:
            self.calculatePlayTime()
            sprites.sort(key=self.sortByYPos)
            for sprite in sprites:
                if sprite in self.ui:
                    sprites.remove(sprite)
                    sprites.append(sprite)
            self.clock.tick(fps)
            if len(enemies) != 0:
                target = enemies[0]
            if song is not None:
                eval(song)
            self.event = pg.event.get().copy()
            keys = pg.key.get_pressed()
            for event in self.event:
                if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_F4:
                        self.fullscreen = not self.fullscreen
                        if not self.fullscreen:
                            self.screen = pg.display.set_mode((width, height))
                        else:
                            self.screen = pg.display.set_mode((width, height), pg.FULLSCREEN)
                    if event.key == pg.K_m and started:
                        if not mario.kicking and not mario.onShell and not mario.lookAtLuigi and not mario.winPose:
                            mario.currentFrame = 0
                            mario.kicking = True
                    if event.key == pg.K_l and started:
                        if not luigi.kicking and not luigi.onShell and not luigi.lookAtMario and not luigi.winPose:
                            luigi.currentFrame = 0
                            luigi.kicking = True
                    if event.key == pg.K_m or event.key == pg.K_l:
                        if shell not in sprites:
                            started = True
                            sprites.append(shell)
                            luigi.currentFrame = 0
                            luigi.kicking = True
                            for i in range(shell.speed + 1):
                                shell.points.append(
                                    pt.getPointOnLine(shell.rect.centerx, shell.rect.centery,
                                                      target.rect.centerx, target.rect.bottom - 10, (i / shell.speed)))

            self.fadeout.update()
            if shell in sprites:
                if shell.counter >= shell.speed and not shell.missed:
                    if shell.target == "enemy":
                        if shell.speed <= 10 or target.enemy.stats["hp"] <= 0 and len(enemies) == 1:
                            shell.missed = True
                            shell.travelSpeed = (
                                shell.points[1][0] - shell.points[0][0], shell.points[1][1] - shell.points[0][1])
                            target.hit = True
                            mario.winPose = True
                            luigi.winPose = True
                        elif shell.prevTarget == "mario":
                            shell.target = "luigi"
                            luigi.target = True
                            luigi.currentFrame = 0
                            shell.prevTarget = "enemy"
                            sprites.append(HitNumbers(self, self.room, (target.rect.centerx, target.rect.top),
                                                      (self.player.stats["pow"] - target.enemy.stats["def"])))
                            target.enemy.stats["hp"] -= (self.player.stats["pow"] - target.enemy.stats["def"])
                            self.enemyHitSound.play()
                            if target.enemy.stats["hp"] <= 0 and len(enemies) == 1:
                                shell.travelSpeed = (
                                    shell.points[1][0] - shell.points[0][0], shell.points[1][1] - shell.points[0][1])
                                shell.missed = True
                            if target.enemy.stats["hp"] <= 0:
                                enemies.remove(target)
                                self.enemyDieSound.play()
                            shell.points = []
                            for i in range(shell.speed + 1):
                                shell.points.append(
                                    pt.getPointOnLine(shell.rect.centerx, shell.rect.centery,
                                                      luigi.rect.centerx, luigi.rect.bottom - 10, (i / shell.speed)))
                            shell.counter = 0
                            target.hit = True
                        elif shell.prevTarget == "luigi":
                            shell.target = "mario"
                            mario.target = True
                            mario.currentFrame = 0
                            shell.prevTarget = "enemy"
                            sprites.append(HitNumbers(self, self.room, (target.rect.centerx, target.rect.top),
                                                      (self.follower.stats["pow"] - target.enemy.stats["def"])))
                            target.enemy.stats["hp"] -= (self.follower.stats["pow"] - target.enemy.stats["def"])
                            self.enemyHitSound.play()
                            if target.enemy.stats["hp"] <= 0 and len(enemies) == 1:
                                shell.travelSpeed = (
                                    shell.points[1][0] - shell.points[0][0], shell.points[1][1] - shell.points[0][1])
                                shell.missed = True
                            if target.enemy.stats["hp"] <= 0:
                                enemies.remove(target)
                                self.enemyDieSound.play()
                            shell.points = []
                            for i in range(shell.speed + 1):
                                shell.points.append(
                                    pt.getPointOnLine(shell.rect.centerx, shell.rect.centery,
                                                      mario.rect.centerx, mario.rect.bottom - 10, (i / shell.speed)))
                            shell.counter = 0
                            target.hit = True
                    else:
                        if shell.target == "mario":
                            shell.target = "enemy"
                            shell.prevTarget = "mario"
                            kik = mario.kicking
                        elif shell.target == "luigi":
                            shell.target = "enemy"
                            shell.prevTarget = "luigi"
                            kik = luigi.kicking
                        mario.target = False
                        luigi.target = False
                        if kik:
                            if shell.speed != 2:
                                shell.speed -= 3
                            shell.points = []
                            for i in range(shell.speed + 1):
                                shell.points.append(
                                    pt.getPointOnLine(shell.rect.centerx, shell.rect.centery,
                                                      target.rect.centerx, target.rect.bottom - 10, (i / shell.speed)))
                            shell.counter = 0
                        else:
                            if shell.prevTarget == "luigi":
                                luigi.onShell = True
                                sprites.remove(luigi)
                                sprites.append(luigi)
                                mario.currentFrame = 0
                                mario.lookAtLuigi = True
                            if shell.prevTarget == "mario":
                                mario.onShell = True
                                sprites.remove(mario)
                                sprites.append(mario)
                                luigi.currentFrame = 0
                                luigi.lookAtMario = True
                            shell.missed = True
                            shell.travelSpeed = (
                                shell.points[1][0] - shell.points[0][0], shell.points[1][1] - shell.points[0][1])
            if len(enemies) == 0:
                mario.winPose = True
                luigi.winPose = True
            [sprite.update() for sprite in sprites]
            if luigi.onShell:
                luigi.rect.centerx = shell.rect.centerx
                luigi.rect.centery = shell.rect.top - 10
            if mario.onShell:
                mario.rect.centerx = shell.rect.centerx
                mario.rect.centery = shell.rect.top - 10
            if shell.rect.right < 0 or shell.rect.left > width:
                going = False

            self.screen.fill((59, 59, 59))
            self.screen.blit(background, bRect)
            for sprite in sprites:
                try:
                    sprite.draw()
                except:
                    self.blit_alpha(self.screen, sprite.image, sprite.rect, sprite.alpha)
            for enemy in enemies:
                pg.draw.rect(self.screen, darkGray,
                             pg.Rect(enemy.barRect.left, enemy.barRect.bottom + 12,
                                     enemy.barRect.width, 10))
                if enemy.enemy.rectHP >= 0:
                    pg.draw.rect(self.screen, red,
                                 pg.Rect(enemy.barRect.left, enemy.barRect.bottom + 12,
                                         (enemy.barRect.width * (
                                                 enemy.enemy.rectHP / enemy.enemy.stats["maxHP"])), 10))
                pg.draw.rect(self.screen, black,
                             pg.Rect(enemy.barRect.left, enemy.barRect.bottom + 12,
                                     enemy.barRect.width, 10),
                             1)
            for sprite in sprites:
                try:
                    sprite.draw()
                except:
                    pass
            if not started:
                self.screen.blit(s, sRect)
                self.screen.blit(button, buRect)
            [self.screen.blit(fad.image, (0, 0)) for fad in self.fadeout]

            pg.display.flip()
        fad = Fadeout(self, 5)
        while fad.alpha <= 255:
            self.calculatePlayTime()
            self.fadeout.update()
            [sprite.update() for sprite in sprites]
            self.screen.fill((59, 59, 59))
            self.screen.blit(background, bRect)
            if luigi.onShell:
                luigi.rect.centerx = shell.rect.centerx
                luigi.rect.centery = shell.rect.top - 10
            if mario.onShell:
                mario.rect.centerx = shell.rect.centerx
                mario.rect.centery = shell.rect.top - 10
            for sprite in sprites:
                try:
                    sprite.draw()
                except:
                    self.blit_alpha(self.screen, sprite.image, sprite.rect, sprite.alpha)
            [self.screen.blit(fad.image, (0, 0)) for fad in self.fadeout]

            pg.display.flip()
        self.camera.update(self.player.rect)
        self.room = "battle"

    def redShell(self, enems, song=None):
        going = True
        started = False
        button = pg.image.load("sprites/bros attack start.png").convert_alpha()
        buRect = button.get_rect()
        buRect.center = (width / 2, height / 2)
        s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
        sRect = s.get_rect()
        s.fill(black)
        s.set_alpha(125)
        background = pg.image.load("sprites/maps/Bros Attack.png")
        bRect = background.get_rect()
        shell = RedShell(self, 50)
        mario = MarioShell(self, shell)
        luigi = LuigiShell(self, shell)
        self.camera.update(mario.rect)
        sprites = [mario, luigi]
        enemies = []
        for enemy in enems:
            command = enemy.stats["name"] + "BrosAttack(self, enemy)"
            en = eval(command)
            sprites.append(en)
            enemies.append(en)
        while going:
            self.calculatePlayTime()
            sprites.sort(key=self.sortByYPos)
            for sprite in sprites:
                if sprite in self.ui:
                    sprites.remove(sprite)
                    sprites.append(sprite)
            self.clock.tick(fps)
            if len(enemies) != 0:
                target = enemies[0]
            if song is not None:
                eval(song)
            self.event = pg.event.get().copy()
            keys = pg.key.get_pressed()
            for event in self.event:
                if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                    pg.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_F4:
                        self.fullscreen = not self.fullscreen
                        if not self.fullscreen:
                            self.screen = pg.display.set_mode((width, height))
                        else:
                            self.screen = pg.display.set_mode((width, height), pg.FULLSCREEN)
                    if event.key == pg.K_m and started:
                        if not mario.kicking and not mario.onShell and not mario.lookAtLuigi and not mario.winPose:
                            mario.currentFrame = 0
                            mario.kicking = True
                    if event.key == pg.K_l and started:
                        if not luigi.kicking and not luigi.onShell and not luigi.lookAtMario and not luigi.winPose:
                            luigi.currentFrame = 0
                            luigi.kicking = True
                    if event.key == pg.K_m or event.key == pg.K_l:
                        if shell not in sprites:
                            started = True
                            sprites.append(shell)
                            mario.currentFrame = 0
                            mario.kicking = True
                            for i in range(shell.speed + 1):
                                shell.points.append(
                                    pt.getPointOnLine(shell.rect.centerx, shell.rect.centery,
                                                      target.rect.centerx, target.rect.bottom - 10, (i / shell.speed)))

            self.fadeout.update()
            if shell in sprites:
                if shell.counter >= shell.speed and not shell.missed:
                    if shell.target == "enemy":
                        if shell.speed <= 10 or target.enemy.stats["hp"] <= 0 and len(enemies) == 1:
                            shell.missed = True
                            shell.travelSpeed = (
                                shell.points[1][0] - shell.points[0][0], shell.points[1][1] - shell.points[0][1])
                            target.hit = True
                            mario.winPose = True
                            luigi.winPose = True
                        elif shell.prevTarget == "mario":
                            shell.target = "luigi"
                            luigi.target = True
                            luigi.currentFrame = 0
                            shell.prevTarget = "enemy"
                            sprites.append(HitNumbers(self, self.room, (target.rect.centerx, target.rect.top),
                                                      (self.player.stats["pow"] - target.enemy.stats["def"])))
                            target.enemy.stats["hp"] -= (self.player.stats["pow"] - target.enemy.stats["def"])
                            self.enemyHitSound.play()
                            if target.enemy.stats["hp"] <= 0 and len(enemies) == 1:
                                shell.travelSpeed = (
                                    shell.points[1][0] - shell.points[0][0], shell.points[1][1] - shell.points[0][1])
                                shell.missed = True
                            if target.enemy.stats["hp"] <= 0:
                                enemies.remove(target)
                                self.enemyDieSound.play()
                            shell.points = []
                            for i in range(shell.speed + 1):
                                shell.points.append(
                                    pt.getPointOnLine(shell.rect.centerx, shell.rect.centery,
                                                      luigi.rect.centerx, luigi.rect.bottom - 10, (i / shell.speed)))
                            shell.counter = 0
                            target.hit = True
                        elif shell.prevTarget == "luigi":
                            shell.target = "mario"
                            mario.target = True
                            mario.currentFrame = 0
                            shell.prevTarget = "enemy"
                            sprites.append(HitNumbers(self, self.room, (target.rect.centerx, target.rect.top),
                                                      (self.follower.stats["pow"] - target.enemy.stats["def"])))
                            target.enemy.stats["hp"] -= (self.follower.stats["pow"] - target.enemy.stats["def"])
                            self.enemyHitSound.play()
                            if target.enemy.stats["hp"] <= 0 and len(enemies) == 1:
                                shell.travelSpeed = (
                                    shell.points[1][0] - shell.points[0][0], shell.points[1][1] - shell.points[0][1])
                                shell.missed = True
                            if target.enemy.stats["hp"] <= 0:
                                enemies.remove(target)
                                self.enemyDieSound.play()
                            shell.points = []
                            for i in range(shell.speed + 1):
                                shell.points.append(
                                    pt.getPointOnLine(shell.rect.centerx, shell.rect.centery,
                                                      mario.rect.centerx, mario.rect.bottom - 10, (i / shell.speed)))
                            shell.counter = 0
                            target.hit = True
                    else:
                        if shell.target == "mario":
                            shell.target = "enemy"
                            shell.prevTarget = "mario"
                            kik = mario.kicking
                        elif shell.target == "luigi":
                            shell.target = "enemy"
                            shell.prevTarget = "luigi"
                            kik = luigi.kicking
                        mario.target = False
                        luigi.target = False
                        if kik:
                            if shell.speed != 2:
                                shell.speed -= 3
                            shell.points = []
                            for i in range(shell.speed + 1):
                                shell.points.append(
                                    pt.getPointOnLine(shell.rect.centerx, shell.rect.centery,
                                                      target.rect.centerx, target.rect.bottom - 10, (i / shell.speed)))
                            shell.counter = 0
                        else:
                            if shell.prevTarget == "luigi":
                                luigi.onShell = True
                                sprites.remove(luigi)
                                sprites.append(luigi)
                                mario.currentFrame = 0
                                mario.lookAtLuigi = True
                            if shell.prevTarget == "mario":
                                mario.onShell = True
                                sprites.remove(mario)
                                sprites.append(mario)
                                luigi.currentFrame = 0
                                luigi.lookAtMario = True
                            shell.missed = True
                            shell.travelSpeed = (
                                shell.points[1][0] - shell.points[0][0], shell.points[1][1] - shell.points[0][1])
            if len(enemies) == 0:
                mario.winPose = True
                luigi.winPose = True
            [sprite.update() for sprite in sprites]
            if luigi.onShell:
                luigi.rect.centerx = shell.rect.centerx
                luigi.rect.centery = shell.rect.top - 10
            if mario.onShell:
                mario.rect.centerx = shell.rect.centerx
                mario.rect.centery = shell.rect.top - 10
            if shell.rect.right < 0 or shell.rect.left > width:
                going = False

            self.screen.fill((59, 59, 59))
            self.screen.blit(background, bRect)
            for sprite in sprites:
                try:
                    sprite.draw()
                except:
                    self.blit_alpha(self.screen, sprite.image, sprite.rect, sprite.alpha)
            for enemy in enemies:
                pg.draw.rect(self.screen, darkGray,
                             pg.Rect(enemy.barRect.left, enemy.barRect.bottom + 12,
                                     enemy.barRect.width, 10))
                if enemy.enemy.rectHP >= 0:
                    pg.draw.rect(self.screen, red,
                                 pg.Rect(enemy.barRect.left, enemy.barRect.bottom + 12,
                                         (enemy.barRect.width * (
                                                 enemy.enemy.rectHP / enemy.enemy.stats["maxHP"])), 10))
                pg.draw.rect(self.screen, black,
                             pg.Rect(enemy.barRect.left, enemy.barRect.bottom + 12,
                                     enemy.barRect.width, 10),
                             1)
            for sprite in sprites:
                try:
                    sprite.draw()
                except:
                    pass
            if not started:
                self.screen.blit(s, sRect)
                self.screen.blit(button, buRect)
            [self.screen.blit(fad.image, (0, 0)) for fad in self.fadeout]

            pg.display.flip()
        fad = Fadeout(self, 5)
        while fad.alpha <= 255:
            self.calculatePlayTime()
            self.fadeout.update()
            [sprite.update() for sprite in sprites]
            self.screen.fill((59, 59, 59))
            self.screen.blit(background, bRect)
            if luigi.onShell:
                luigi.rect.centerx = shell.rect.centerx
                luigi.rect.centery = shell.rect.top - 10
            if mario.onShell:
                mario.rect.centerx = shell.rect.centerx
                mario.rect.centery = shell.rect.top - 10
            for sprite in sprites:
                try:
                    sprite.draw()
                except:
                    self.blit_alpha(self.screen, sprite.image, sprite.rect, sprite.alpha)
            [self.screen.blit(fad.image, (0, 0)) for fad in self.fadeout]

            pg.display.flip()
        self.camera.update(self.player.rect)
        self.room = "battle"

    def battleOver(self, mario=True, luigi=True, tutorial=False):
        self.player.statGrowth = {"maxHP": randomNumber(10), "maxBP": randomNumber(4), "pow": randomNumber(7),
                                  "def": randomNumber(3)}

        self.follower.statGrowth = {"maxHP": randomNumber(13), "maxBP": randomNumber(7), "pow": randomNumber(4),
                                    "def": randomNumber(6)}

        self.player.isHammer = None
        self.follower.isHammer = None
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
        self.expNumbers = ExpNumbers(self)
        if mario:
            MarioExpNumbers(self)
        if luigi:
            LuigiExpNumbers(self)
        self.coinCollection = CoinCollectionSubtract(self)
        coincollect = CoinCollectionAdd(self)

        textbox = None
        if tutorial and self.tutorials:
            textboxd = False
        else:
            textboxd = True
        text = ["Oh!/p It looks like you beat Bowser!",
                "After you beat an enemy, you'll gain\nExperience Points, or <<BEXP>> for short.",
                "If you gain enough <<BEXP>>, you'll\n<<BLevel Up>>, and your stats will\nincrease!",
                "So, try to beat as many enemies as\nyou can!"]

        while True:
            self.calculatePlayTime()
            self.playSong(5.44, 36.708, "battle victory")
            self.clock.tick(fps)
            self.events()
            if tutorial and self.tutorials:
                if self.marioBattleOver.counter >= len(self.marioBattleOver.points) - 1:
                    if textbox is None:
                        self.imgRect = self.marioBattleOver.rect
                        textbox = TextBox(self, self, text, sound="starlow")
                    if textbox.complete:
                        textboxd = True
                        tutorial = False
                    textbox.update()
                else:
                    self.updateBattleOver()
            else:
                self.updateBattleOver()
            self.screen.fill(black)
            self.drawBattleOver()
            if textbox is not None:
                textbox.draw()
            pg.display.flip()
            keys = pg.key.get_pressed()
            if (keys[pg.K_m] or keys[pg.K_l] or keys[pg.K_SPACE]) and textboxd:
                break

        self.expNumbers.exp = 0
        if not self.player.dead:
            self.storeData["mario stats"]["exp"] += self.battleXp
            self.player.stats = self.storeData["mario stats"]
        if not self.follower.dead:
            self.storeData["luigi stats"]["exp"] += self.battleXp
            self.follower.stats = self.storeData["luigi stats"]
        coincollect.exp = self.coins + self.battleCoins
        self.coins += self.battleCoins
        if self.player.stats["exp"] >= round((4 * (self.player.stats["level"] ** 3)) / 5) + 5 and self.player.stats[
            "level"] < 100:
            self.marioLevelUp()
        elif self.follower.stats["exp"] >= round((4 * (self.follower.stats["level"] ** 3)) / 4.9) + 5 and \
                self.follower.stats["level"] < 100:
            self.luigiLevelUp()
        fade = Fadeout(self)
        pg.mixer.music.fadeout(1000)
        while True:
            self.calculatePlayTime()
            self.clock.tick(fps)
            self.events()
            self.updateBattleOver()
            self.screen.fill(black)
            self.drawBattleOver()
            pg.display.flip()
            if fade.alpha > 255:
                self.pause = False
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
            self.player.shadow = self.player.shadowFrames["normal"]
            self.player.rect = self.player.shadow.get_rect()
        if self.follower.dead:
            self.follower.dead = False
            self.follower.stats["hp"] = 1
            self.follower.shadow = self.follower.shadowFrames["normal"]
            self.follower.rect = self.follower.shadow.get_rect()
        self.storeData["mario stats"] = self.player.stats
        self.storeData["luigi stats"] = self.follower.stats
        try:
            eval(self.prevRoom)
        except:
            pass

    def marioLevelUp(self, allReadyLeveled=False, currentFrame=0):
        levelUpChannel = pg.mixer.Channel(0)
        playedLevelUpSound = False
        self.player.statGrowth = {"maxHP": randomNumber(5), "maxBP": randomNumber(4), "pow": randomNumber(5),
                                  "def": randomNumber(3)}
        going = True
        mario = MarioLevelUp()
        luigi = LuigiLevelUpLeave()
        text = MarioLevelUpUI(self)
        levelUp = pg.image.load("sprites/LevelUpText.png").convert_alpha()
        levelUpRect = levelUp.get_rect()
        levelUpRect.center = (width / 2, 120)
        counter = 0
        clipTime = fps * 2
        expClipTime = fps * 3
        expClipAmount = 0
        if self.follower.dead:
            luigi.counter = len(luigi.points) - 1
        if allReadyLeveled:
            mario.counter = len(mario.points) - 1
            mario.currentFrame = currentFrame
            mario.rect.center = mario.points[mario.counter]
            expClipAmount = height + 3
            counter = clipTime
            luigi.counter = len(luigi.points) - 1
        while going:
            self.calculatePlayTime()
            self.playSong(5.44, 36.708, "battle victory")
            self.clock.tick(fps)
            self.events()

            for event in self.event:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                        going = False

            if allReadyLeveled:
                if not playedLevelUpSound:
                    levelUpChannel.play(self.levelUpSound)
                    self.marioWahoo.play()
                    playedLevelUpSound = True

            mario.update()
            if luigi.counter < len(luigi.points) - 1:
                luigi.update()
            if mario.counter >= len(mario.points) - 1 and counter < clipTime:
                counter += 1
                if not playedLevelUpSound:
                    levelUpChannel.play(self.levelUpSound)
                    self.marioWahoo.play()
                    playedLevelUpSound = True

            if expClipAmount < height:
                expClipAmount += height / expClipTime

            clipAmount = (counter / clipTime) * height

            self.screen.fill(black)
            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)
            try:
                self.screen.blit(self.map.background, self.map.rect)
            except:
                pass
            self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
            self.screen.set_clip(0, expClipAmount, width, height)
            for ui in self.battleEndUI:
                try:
                    if ui.dead:
                        ui.draw()
                except:
                    pass
            self.screen.set_clip(None)
            self.screen.blit(s, sRect)

            self.screen.set_clip(0, expClipAmount, width, height)
            for ui in self.battleEndUI:
                try:
                    if not ui.dead:
                        ui.draw()
                except:
                    ui.draw()

            self.screen.set_clip(0, 0, width, clipAmount)
            text.draw(False)
            self.screen.set_clip(None)

            if mario.counter >= len(mario.points) - 1:
                self.screen.blit(levelUp, levelUpRect)

            self.screen.blit(mario.image, mario.rect)
            if luigi.counter < len(luigi.points) - 1:
                self.screen.blit(luigi.image, luigi.rect)

            pg.display.flip()

        going = True
        self.marioOhYeah.play()
        counter = 0

        while going:
            self.calculatePlayTime()
            self.playSong(5.44, 36.708, "battle victory")
            self.clock.tick(fps)
            self.events()

            if counter != fps / 2:
                counter += 1
                self.expFinishedSound.stop()
                self.expFinishedSound.play()

            for event in self.event:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                        going = False

            mario.update()
            self.screen.fill(black)

            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)
            try:
                self.screen.blit(self.map.background, self.map.rect)
            except:
                pass
            self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
            self.screen.blit(s, sRect)

            self.screen.blit(levelUp, levelUpRect)
            text.draw(True)
            self.screen.set_clip(None)

            self.screen.blit(mario.image, mario.rect)

            pg.display.flip()

        self.player.stats["level"] += 1
        self.player.stats["maxHP"] += self.player.statGrowth["maxHP"]
        self.player.stats["maxBP"] += self.player.statGrowth["maxBP"]
        self.player.stats["pow"] += self.player.statGrowth["pow"]
        self.player.stats["def"] += self.player.statGrowth["def"]

        if self.player.stats["exp"] >= round((4 * (self.player.stats["level"] ** 3)) / 5) + 5 and self.player.stats[
            "level"] < 100:
            self.marioLevelUp(True, mario.currentFrame)
        if self.follower.stats["exp"] >= round((4 * (self.follower.stats["level"] ** 3)) / 4.9) + 5 and \
                self.follower.stats["level"] < 100:
            self.luigiLevelUp(False, True)

        fade = Fadeout(self)
        pg.mixer.music.fadeout(1000)
        while True:
            self.calculatePlayTime()
            self.clock.tick(fps)
            self.events()
            mario.update()
            self.screen.fill(black)
            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)
            try:
                self.screen.blit(self.map.background, self.map.rect)
            except:
                pass
            self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
            self.screen.blit(s, sRect)

            self.screen.blit(levelUp, levelUpRect)
            text.draw(False, False)

            self.screen.blit(mario.image, mario.rect)

            self.screen.blit(fade.image, fade.rect)

            pg.display.flip()

            fade.update()
            if fade.alpha > 255:
                self.pause = False
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
            self.player.shadow = self.player.shadowFrames["normal"]
            self.player.rect = self.player.shadow.get_rect()
        if self.follower.dead:
            self.follower.dead = False
            self.follower.stats["hp"] = 1
            self.follower.shadow = self.follower.shadowFrames["normal"]
            self.follower.rect = self.follower.shadow.get_rect()
        self.storeData["mario stats"] = self.player.stats
        self.storeData["luigi stats"] = self.follower.stats
        eval(self.prevRoom)

    def luigiLevelUp(self, allReadyLeveled=False, marioBefore=False, currentFrame=0):
        levelUpChannel = pg.mixer.Channel(0)
        playedLevelUpSound = False
        self.follower.statGrowth = {"maxHP": randomNumber(7), "maxBP": randomNumber(7), "pow": randomNumber(4),
                                    "def": randomNumber(6)}
        going = True
        luigi = LuigiLevelUp()
        text = LuigiLevelUpUI(self)
        mario = MarioLevelUpLeave((200, 300))
        levelUp = pg.image.load("sprites/LevelUpText.png").convert_alpha()
        levelUpRect = levelUp.get_rect()
        levelUpRect.center = (width / 2, 120)
        counter = 0
        clipTime = fps * 2
        expClipTime = fps * 3
        expClipAmount = 0
        if self.player.dead:
            mario.counter = len(mario.points) - 1
        if allReadyLeveled:
            luigi.counter = len(luigi.points) - 1
            luigi.currentFrame = currentFrame
            luigi.rect.center = luigi.points[luigi.counter]
            expClipAmount = height + 3
            counter = clipTime
            mario.counter = len(mario.points) - 1
        if marioBefore:
            mario = MarioLevelUpLeave((width / 2 - 5, 385))
            marioText = MarioLevelUpUI(self)
            luigi = LuigiLevelUp(True)
        while going:
            self.calculatePlayTime()
            self.playSong(5.44, 36.708, "battle victory")
            self.clock.tick(fps)
            self.events()

            for event in self.event:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                        going = False

            if allReadyLeveled:
                if not playedLevelUpSound:
                    levelUpChannel.play(self.levelUpSound)
                    self.luigiYaHoooo.play()
                    playedLevelUpSound = True

            luigi.update()
            if mario.counter < len(mario.points) - 1:
                mario.update()

            if luigi.counter >= len(luigi.points) - 1 and counter < clipTime:
                counter += 1
                if not playedLevelUpSound:
                    levelUpChannel.play(self.levelUpSound)
                    self.luigiYaHoooo.play()
                    playedLevelUpSound = True

            if expClipAmount < height:
                expClipAmount += height / expClipTime

            clipAmount = (counter / clipTime) * height

            self.screen.fill(black)
            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)
            try:
                self.screen.blit(self.map.background, self.map.rect)
            except:
                pass
            self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
            if not marioBefore:
                self.screen.set_clip(0, expClipAmount, width, height)
                for ui in self.battleEndUI:
                    try:
                        if ui.dead:
                            ui.draw()
                    except:
                        pass
                self.screen.set_clip(None)
            self.screen.blit(s, sRect)

            if not marioBefore:
                self.screen.set_clip(0, expClipAmount, width, height)
                for ui in self.battleEndUI:
                    try:
                        if not ui.dead:
                            ui.draw()
                    except:
                        ui.draw()
            else:
                if clipAmount < height:
                    marioText.draw(False, False)

            self.screen.set_clip(0, 0, width, clipAmount)
            text.draw(False)
            self.screen.set_clip(None)

            if mario.counter < len(mario.points) - 1:
                self.screen.blit(mario.image, mario.rect)

            if luigi.counter >= len(luigi.points) - 1:
                self.screen.blit(levelUp, levelUpRect)

            self.screen.blit(luigi.image, luigi.rect)

            pg.display.flip()

        going = True
        self.luigiOhHoHo.play()
        counter = 0

        while going:
            self.calculatePlayTime()
            self.playSong(5.44, 36.708, "battle victory")
            self.clock.tick(fps)
            self.events()

            if counter != fps / 2:
                counter += 1
                self.expFinishedSound.stop()
                self.expFinishedSound.play()

            for event in self.event:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_m or event.key == pg.K_l or event.key == pg.K_SPACE:
                        going = False

            luigi.update()
            self.screen.fill(black)

            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)
            try:
                self.screen.blit(self.map.background, self.map.rect)
            except:
                pass
            self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
            self.screen.blit(s, sRect)

            if luigi.counter >= len(luigi.points) - 1:
                self.screen.blit(levelUp, levelUpRect)
            text.draw(True)
            self.screen.set_clip(None)

            self.screen.blit(luigi.image, luigi.rect)

            pg.display.flip()

        self.follower.stats["level"] += 1
        self.follower.stats["maxHP"] += self.follower.statGrowth["maxHP"]
        self.follower.stats["maxBP"] += self.follower.statGrowth["maxBP"]
        self.follower.stats["pow"] += self.follower.statGrowth["pow"]
        self.follower.stats["def"] += self.follower.statGrowth["def"]

        if self.follower.stats["exp"] >= round((4 * (self.follower.stats["level"] ** 3)) / 4.9) + 5 and \
                self.follower.stats["level"] < 100:
            self.luigiLevelUp(True, False, luigi.currentFrame)

        fade = Fadeout(self)
        pg.mixer.music.fadeout(1000)
        while True:
            self.calculatePlayTime()
            self.clock.tick(fps)
            self.events()
            luigi.update()
            self.screen.fill(black)
            s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
            sRect = s.get_rect()
            s.fill(black)
            s.set_alpha(125)
            try:
                self.screen.blit(self.map.background, self.map.rect)
            except:
                pass
            self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
            self.screen.blit(s, sRect)

            self.screen.blit(levelUp, levelUpRect)
            text.draw(False, False)

            self.screen.blit(luigi.image, luigi.rect)

            self.screen.blit(fade.image, fade.rect)

            pg.display.flip()

            fade.update()
            if fade.alpha > 255:
                self.pause = False
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
            self.player.shadow = self.player.shadowFrames["normal"]
            self.player.rect = self.player.shadow.get_rect()
        if self.follower.dead:
            self.follower.dead = False
            self.follower.stats["hp"] = 1
            self.follower.shadow = self.follower.shadowFrames["normal"]
            self.follower.rect = self.follower.shadow.get_rect()
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
                if event.key == pg.K_F4:
                    self.fullscreen = not self.fullscreen
                    if not self.fullscreen:
                        self.screen = pg.display.set_mode((width, height))
                    else:
                        self.screen = pg.display.set_mode((width, height), pg.FULLSCREEN)
                if event.key == pg.K_RETURN and not self.player.dead and not self.follower.dead:
                    if self.leader == "mario":
                        self.leader = "luigi"
                        self.follower.moveQueue = self.player.moveQueue
                    elif self.leader == "luigi":
                        self.leader = "mario"
                        self.player.moveQueue = self.follower.moveQueue

                    self.player.rect.center, self.follower.rect.center = self.follower.rect.center, self.player.rect.center
                    self.player.facing, self.follower.facing = self.follower.facing, self.player.facing

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
        if self.leader == "mario":
            self.cameraRect.update(self.player.rect, 600)
        else:
            self.cameraRect.update(self.follower.rect, 600)
        self.camera.update(self.cameraRect.rect)

    def updateOverworld(self):
        self.void.update(self.voidSize)
        [ui.update() for ui in self.battleEndUI]
        self.fadeout.update()
        self.npcs.update()
        self.effects.update()
        [enemy.update() for enemy in self.enemies]
        self.ui.update()
        [sprite.update() for sprite in self.sprites]
        [col.update() for col in self.collision]
        if self.leader == "mario":
            self.cameraRect.update(self.player.rect, 600)
        else:
            self.cameraRect.update(self.follower.rect, 600)
        self.camera.update(self.cameraRect.rect)
        [room.update() for room in self.transistors]
        [cutscene.update() for cutscene in self.cutscenes]

    def blit_alpha(self, target, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pg.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(target, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)
        target.blit(temp, location)

    def drawBattleOver(self):
        s = pg.Surface((self.screen.get_width(), self.screen.get_height()))
        sRect = s.get_rect()
        s.fill(black)
        s.set_alpha(125)
        self.screen.blit(self.map.image, self.camera.offset(self.map.rect))
        for sprite in self.sprites:
            if sprite.dead:
                self.screen.blit(sprite.shadow, sprite.rect)
                self.screen.blit(sprite.image, sprite.imgRect)
        for ui in self.battleEndUI:
            try:
                if ui.dead:
                    ui.draw()
            except:
                pass
        self.screen.blit(s, sRect)
        for ui in self.battleEndUI:
            try:
                if not ui.dead:
                    ui.draw()
            except:
                ui.draw()
        self.sprites.sort(key=self.sortByYPos)

        for sprite in self.sprites:
            if not sprite.dead:
                self.blit_alpha(self.screen, sprite.image, self.camera.offset(sprite.rect), sprite.alpha)

        [self.screen.blit(fad.image, (0, 0)) for fad in self.fadeout]

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
                pg.draw.rect(self.screen, darkGray,
                             self.camera.offset(
                                 pg.Rect(enemy.rect.left, enemy.imgRect.bottom + 12, enemy.rect.width, 10)))
                if enemy.rectHP >= 0:
                    pg.draw.rect(self.screen, red, self.camera.offset(
                        pg.Rect(enemy.rect.left, enemy.imgRect.bottom + 12,
                                (enemy.rect.width * (enemy.rectHP / enemy.stats["maxHP"])), 10)))
                pg.draw.rect(self.screen, black,
                             self.camera.offset(
                                 pg.Rect(enemy.rect.left, enemy.imgRect.bottom + 12, enemy.rect.width, 10)),
                             1)

        [ui.draw() for ui in self.ui]

        for fx in self.effects:
            if fx.offset:
                self.blit_alpha(self.screen, fx.image, self.camera.offset(fx.rect), fx.alpha)
            else:
                self.blit_alpha(self.screen, fx.image, fx.rect, fx.alpha)

        [self.screen.blit(fad.image, (0, 0)) for fad in self.fadeout]

        pg.display.flip()

    def drawBattleMenu(self):
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

        for fx in self.effects:
            if fx.offset:
                self.blit_alpha(self.screen, fx.image, self.camera.offset(fx.rect), fx.alpha)
            else:
                self.blit_alpha(self.screen, fx.image, fx.rect, fx.alpha)

    def drawOverworld(self):
        try:
            self.screen.blit(self.map.background, self.map.rect)
        except:
            pass

        self.screen.blit(self.void.image, self.void.rect)
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

        for item in self.blockContents:
            item.draw()

        for fx in self.effects:
            if fx.offset:
                self.blit_alpha(self.screen, fx.image, self.camera.offset(fx.rect), fx.alpha)
            else:
                self.blit_alpha(self.screen, fx.image, fx.rect, fx.alpha)

        [self.screen.blit(fad.image, (0, 0)) for fad in self.fadeout]

        pg.display.flip()

    def drawOverworldMenu(self):
        try:
            self.screen.blit(self.map.background, self.map.rect)
        except:
            pass
        self.screen.blit(self.void.image, self.void.rect)
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

        for fx in self.effects:
            if fx.offset:
                self.blit_alpha(self.screen, fx.image, self.camera.offset(fx.rect), fx.alpha)
            else:
                self.blit_alpha(self.screen, fx.image, fx.rect, fx.alpha)

        [self.screen.blit(fad.image, (0, 0)) for fad in self.fadeout]

    def sortByYPos(self, element):
        return element.rect.bottom

    def sortByXPos(self, element):
        return element.rect.left


game = Game()

# game.loadDebugLevel()
game.titleScreen()
