import pickle
from Settings import *
from BrosAttacks import *
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
        self.blockContents = pg.sprite.Group()
        self.ui = pg.sprite.Group()
        self.fadeout = pg.sprite.Group()
        self.battleEndUI = []
        self.loadData()
        self.playtime = 0
        self.goombaHasTexted = False
        self.player = Mario(self, 0, 0)
        self.follower = Luigi(self, 0, 0)
        MarioUI(self)
        LuigiUI(self)
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
                      ["1-UP Super", -1, oneUpSprite, "hp", 1, "Revives a fallen Bro with full HP.", "maxHP"],
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
        elif self.playSeconds < 10 and self.playHours < 1:
            self.playSeconds = "00:0{0}".format(self.playSeconds)
        elif self.playHours < 1:
            self.playSeconds = "00:{0}".format(self.playSeconds)

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
        luigiRect.center = (771, 595)
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
                    if event.key == pg.K_w or event.key == pg.K_a or event.key == pg.K_s or event.key == pg.K_d:
                        if select == 0:
                            select = 1
                        elif select == 1:
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
                            else:
                                self.menuChooseSound.play()
                                going = False

            fade.update()
            if select == 0:
                cursor.update(pg.rect.Rect(width / 2 - 120, height / 2 - 50, 0, 0), 60)
            if select == 1:
                cursor.update(pg.rect.Rect(width / 2 - 100, height / 2 + 25, 0, 0), 60)

            self.screen.fill(black)
            self.screen.blit(background, bRect)
            self.screen.blit(shadow, marioShadowRect)
            self.screen.blit(marioFrames[marioCounter], marioRect)
            self.screen.blit(peachShadow, peachShadowRect)
            self.screen.blit(peachFrames[peachCounter], peachRect)
            self.screen.blit(shadow, luigiShadowRect)
            self.screen.blit(luigiFrames[luigiCounter], luigiRect)
            self.screen.set_clip(clipRect.left, clipRect.top, clipRect.width, clipRect.height)
            self.screen.blit(smal, smalRect)
            ptext.draw("NEW GAME", (width / 2, height / 2 - 50), surf=self.screen, color=white, owidth=1, fontname=dialogueFont, anchor=(0.5, 0), fontsize=40)
            if cont:
                ptext.draw("CONTINUE", (width / 2, height / 2 + 25), surf=self.screen, color=white, owidth=1,
                           fontname=dialogueFont, anchor=(0.5, 0), fontsize=40)
            else:
                ptext.draw("CONTINUE", (width / 2, height / 2 + 25), surf=self.screen, color=darkGray, owidth=1,
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
                    self.loadDebugLevel()

                if select == 0:
                    cursor.update(pg.rect.Rect(width / 2 - 120, height / 2 - 50, 0, 0), 60)
                if select == 1:
                    cursor.update(pg.rect.Rect(width / 2 - 100, height / 2 + 25, 0, 0), 60)

                self.screen.fill(black)
                self.screen.blit(background, bRect)
                self.screen.blit(shadow, marioShadowRect)
                self.screen.blit(marioFrames[marioCounter], marioRect)
                self.screen.blit(peachShadow, peachShadowRect)
                self.screen.blit(peachFrames[peachCounter], peachRect)
                self.screen.blit(shadow, luigiShadowRect)
                self.screen.blit(luigiFrames[luigiCounter], luigiRect)
                self.screen.set_clip(clipRect.left, clipRect.top, clipRect.width, clipRect.height)
                self.screen.blit(smal, smalRect)
                ptext.draw("NEW GAME", (width / 2, height / 2 - 50), surf=self.screen, color=white, owidth=1,
                           fontname=dialogueFont, anchor=(0.5, 0), fontsize=40)
                if cont:
                    ptext.draw("CONTINUE", (width / 2, height / 2 + 25), surf=self.screen, color=white, owidth=1,
                               fontname=dialogueFont, anchor=(0.5, 0), fontsize=40)
                else:
                    ptext.draw("CONTINUE", (width / 2, height / 2 + 25), surf=self.screen, color=darkGray, owidth=1,
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

    def saveGame(self):
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
        save = True
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
                        going = False
                    if event.key == pg.K_TAB:
                        going = False
                        save = False

            if select == 0:
                cursor.update(saves[0].rect, 60)
            elif select == 1:
                cursor.update(saves[1].rect, 60)
            elif select == 2:
                cursor.update(saves[2].rect, 60)

            self.screen.fill(black)
            self.drawOverworldMenu()
            [save.draw() for save in saves]
            self.screen.blit(cursor.image, cursor.rect)

            pg.display.flip()

        if save:
            with open("saves/File " + str(select + 1) + ".ini", "wb") as file:
                pickle.dump(self.area, file)
                pickle.dump(self.storeData, file)
                pickle.dump(self.displayTime, file)
                pickle.dump(self.playtime, file)
                pickle.dump(self.despawnList, file)
                pickle.dump(self.hitBlockList, file)
                pickle.dump(self.coins, file)
                for item in self.items:
                    pickle.dump(item[1], file)
                pickle.dump(self.room, file)

        self.player.canMove = False
        self.follower.canMove = False

        self.saved = True
        self.pause = False

    def loadGame(self, file=1):
        try:
            with open("saves/File " + str(file) + ".ini", "rb") as file:
                self.area = pickle.load(file)
                self.storeData = pickle.load(file)
                self.displayTime = pickle.load(file)
                self.playtime = pickle.load(file)
                self.despawnList = pickle.load(file)
                self.hitBlockList = pickle.load(file)
                self.coins = pickle.load(file)
                for item in self.items:
                    item[1] = pickle.load(file)
                self.room = pickle.load(file)
            print(self.storeData)
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
            self.loadDebugLevel()

    def loadData(self):
        self.coinSound = pg.mixer.Sound("sounds/coin.ogg")
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
        self.luigiYaHoooo = pg.mixer.Sound("sounds/luigiYaHoooo.ogg")
        self.luigiOhHoHo = pg.mixer.Sound("sounds/luigiOhHoHo.ogg")
        self.itemFromBlockSound = pg.mixer.Sound("sounds/itemFromBlock.ogg")

    def loadDebugLevel(self):
        self.room = "self.loadDebugLevel()"
        self.playsong = True
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
        self.map = loadMap("Bowser's Castle")
        self.camera = Camera(self.map.width, self.map.height)
        self.cameraRect = CameraRect()
        # GoombaKing(self, (self.map.width / 2 - 2, self.map.height - 620))
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

        counter = 0
        for enemy in self.enemies:
            enemy.ID = counter
            counter += 1

        counter = 0
        for block in self.blocks:
            block.ID = counter
            counter += 1

        self.overworld("Debug Area", [6.749, 102.727, "castle bleck"])

    def overworld(self, area, songData):
        menud = False
        self.playing = True
        self.saved = False
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
            self.calculatePlayTime()
            if self.playsong:
                self.playSong(songData[0], songData[1], songData[2], cont=True, fadein=True)
            self.clock.tick(fps)
            self.events()
            for event in self.event:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_TAB:
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

    def overworldMenu(self, song=None):
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
        coinIconRect.center = (coinRect.left + 50, coinRect.centery + 10)
        name = EnemyNames(self, "Items")
        cursor = Cursor(self, itemRect)
        lastUpdate = 0
        currentFrame = 0
        print(song)
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
            if song is not None:
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
            ptext.draw("X" + str(self.coins), (coinRect.left + 100, coinIconRect.centery), fontname=dialogueFont, owidth=1, anchor=(0, 0.5),
                       surf=self.screen, fontsize=50, color=white)
            name.draw()
            self.fadeout.draw(self.screen)

            if self.pause:
                pg.display.flip()

    def brosStats(self, song=None):
        going = True
        up = True
        alpha = 0
        rect = pg.rect.Rect(0, 0, 0, 0)
        rect.center = (150, 150)
        select = "Mario"
        name = EnemyNames(self, select + "'s Stats")

        Mhp = MenuIcon(self, (150, 150), "HP: " + str(self.player.stats["hp"]) + "/" + str(self.player.stats["maxHP"]),
                       hpSprite)
        Mbp = MenuIcon(self, (150, 250), "BP: " + str(self.player.stats["bp"]) + "/" + str(self.player.stats["maxBP"]),
                       bpSprite)
        Mpow = MenuIcon(self, (150, 350), "POW: " + str(self.player.stats["pow"]), powSprite)
        Mdefense = MenuIcon(self, (150, 450), "DEF: " + str(self.player.stats["def"]), defSprite)
        Mlevel = MenuIcon(self, (750, height / 2 - 80), "LEVEL: " + str(self.player.stats["level"]), None)
        Mexp = MenuIcon(self, (750, height / 2), "EXP: " + str(self.player.stats["exp"]), None)
        if self.player.stats["level"] < 100:
            MnextLevel = MenuIcon(self, (750, height / 2 + 40),
                                  "NEXT LEVEL: " + str(round((4 * (self.player.stats["level"] ** 3)) / 5) + 5), None)
        else:
            MnextLevel = MenuIcon(self, (750, height / 2 + 40),
                                  "NEXT LEVEL: N/A", None)
        Mstats = [Mhp, Mbp, Mpow, Mdefense, Mlevel, Mexp, MnextLevel]

        Lhp = MenuIcon(self, (150, 150),
                       "HP: " + str(self.follower.stats["hp"]) + "/" + str(self.follower.stats["maxHP"]), hpSprite)
        Lbp = MenuIcon(self, (150, 250),
                       "BP: " + str(self.follower.stats["bp"]) + "/" + str(self.follower.stats["maxBP"]), bpSprite)
        Lpow = MenuIcon(self, (150, 350), "POW: " + str(self.follower.stats["pow"]), powSprite)
        Ldefense = MenuIcon(self, (150, 450), "DEF: " + str(self.follower.stats["def"]), defSprite)
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

    def loadBattle(self, function, currentPoint=True):
        self.player.isHammer = None
        self.follower.isHammer = None
        self.battleXp = 0
        self.battleCoins = 0
        if currentPoint:
            self.currentPoint += pg.mixer.music.get_pos()
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
            trans.update()
            self.screen.fill(black)
            self.drawOverworld()

            if trans.currentFrame == len(trans.sprites) - 1 and not pg.mixer.get_busy():
                self.pause = False
                eval(function)

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
        self.map = loadMap("teehee valley battle", True)
        self.camera = Camera(self.map.width, self.map.height)
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
            # if self.player.stats["hp"] <= 0 and self.follower.stats["hp"] <= 0:
            #     self.gameOver()
            if menud:
                self.player.canMove = True
                self.follower.canMove = True
                menud = False
            if len(self.enemies) == 0:
                self.battleOver()

    def battleMenu(self, song=None):
        self.menuOpenSound.play()
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

        menuCamera = Camera(width, menuIcons[-1].rect.bottom + (width / 2))
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
            self.menuChooseSound.play()
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
        TextBox(self, enemy, enemy.description)
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

    def battleOver(self):
        self.player.statGrowth = {"maxHP": randomNumber(5), "maxBP": randomNumber(4), "pow": randomNumber(7),
                                  "def": randomNumber(3)}

        self.follower.statGrowth = {"maxHP": randomNumber(7), "maxBP": randomNumber(7), "pow": randomNumber(4),
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
        MarioExpNumbers(self)
        LuigiExpNumbers(self)
        self.coinCollection = CoinCollectionSubtract(self)
        coincollect = CoinCollectionAdd(self)
        while True:
            self.calculatePlayTime()
            self.playSong(5.44, 36.708, "battle victory")
            self.clock.tick(fps)
            self.events()
            self.updateBattleOver()
            self.screen.fill(black)
            self.drawBattleOver()
            keys = pg.key.get_pressed()
            if keys[pg.K_m] or keys[pg.K_l] or keys[pg.K_SPACE]:
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
        if self.player.stats["exp"] >= round((4 * (self.player.stats["level"] ** 3)) / 5) + 5 and self.player.stats["level"] < 100:
            self.marioLevelUp()
        elif self.follower.stats["exp"] >= round((4 * (self.follower.stats["level"] ** 3)) / 4.9) + 5 and self.follower.stats["level"] < 100:
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

        if self.player.stats["exp"] >= round((4 * (self.player.stats["level"] ** 3)) / 5) + 5 and self.player.stats["level"] < 100:
            self.marioLevelUp(True, mario.currentFrame)
        if self.follower.stats["exp"] >= round((4 * (self.follower.stats["level"] ** 3)) / 4.9) + 5 and self.follower.stats["level"] < 100:
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

        if self.follower.stats["exp"] >= round((4 * (self.follower.stats["level"] ** 3)) / 4.9) + 5 and self.follower.stats["level"] < 100:
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
                if event.key == pg.K_TAB:
                    self.pause = not self.pause

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

game.titleScreen()
