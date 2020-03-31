from Overworld import *


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
