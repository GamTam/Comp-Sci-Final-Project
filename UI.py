import pickle
import xml.etree.ElementTree as ET

import pytweening as pt

from Settings import *


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


class MarioUI(pg.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.ui
        pg.sprite.Sprite.__init__(self, self.groups)
        sheet = spritesheet("sprites/ui.png", "sprites/ui.xml")
        self.game = game
        self.numbers = [sheet.getImageName("0_hp.png"),
                        sheet.getImageName("1_hp.png"),
                        sheet.getImageName("2_hp.png"),
                        sheet.getImageName("3_hp.png"),
                        sheet.getImageName("4_hp.png"),
                        sheet.getImageName("5_hp.png"),
                        sheet.getImageName("6_hp.png"),
                        sheet.getImageName("7_hp.png"),
                        sheet.getImageName("8_hp.png"),
                        sheet.getImageName("9_hp.png")]
        self.sprites = [pg.image.load("sprites/ui/mariojump.png"),
                        pg.image.load("sprites/ui/mariohammer.png"),
                        pg.image.load("sprites/ui/MarioInteract.png"),
                        pg.image.load("sprites/ui/MarioTalk.png"),
                        pg.image.load("sprites/ui/MarioFire.png")]
        self.image = self.sprites[0]
        self.rect = self.image.get_rect()
        self.rect.left = 0
        self.rect.top = 0
        self.speed = 0
        self.hp = self.game.player.stats["hp"]

    def update(self):
        if self.game.player.abilities[self.game.player.ability] == "jump":
            self.image = self.sprites[0]
        elif self.game.player.abilities[self.game.player.ability] == "hammer":
            self.image = self.sprites[1]
        elif self.game.player.abilities[self.game.player.ability] == "interact":
            self.image = self.sprites[2]
        elif self.game.player.abilities[self.game.player.ability] == "talk":
            self.image = self.sprites[3]
        elif self.game.player.abilities[self.game.player.ability] == "fire":
            self.image = self.sprites[4]

    def draw(self):
        if self.hp > self.game.player.stats["hp"] and self.speed == 0:
            self.speed = ((self.hp - self.game.player.stats["hp"]) / 30) * -1
        elif self.hp < self.game.player.stats["hp"] and self.speed == 0:
            self.speed = (self.game.player.stats["hp"] - self.hp) / 30

        if self.speed != 0:
            if self.hp > self.game.player.stats["hp"] + self.speed and self.speed < 0:
                self.hp += self.speed
            elif self.hp < self.game.player.stats["hp"] - self.speed and self.speed > 0:
                self.hp += self.speed
            else:
                self.hp = self.game.player.stats["hp"]
                self.speed = 0

        if self.hp < 0:
            hp = [0]
        else:
            hp = [int(i) for i in str(round(self.hp))]

        if len(hp) == 1:
            if hp[0] == 0:
                self.numberImg = self.numbers[0]
            elif hp[0] == 1:
                self.numberImg = self.numbers[1]
            elif hp[0] == 2:
                self.numberImg = self.numbers[2]
            elif hp[0] == 3:
                self.numberImg = self.numbers[3]
            elif hp[0] == 4:
                self.numberImg = self.numbers[4]
            elif hp[0] == 5:
                self.numberImg = self.numbers[5]
            elif hp[0] == 6:
                self.numberImg = self.numbers[6]
            elif hp[0] == 7:
                self.numberImg = self.numbers[7]
            elif hp[0] == 8:
                self.numberImg = self.numbers[8]
            elif hp[0] == 9:
                self.numberImg = self.numbers[9]

            self.numberRect = self.numberImg.get_rect()
            self.numberRect.right = self.rect.right - 65
            self.numberRect.centery = self.rect.bottom - 25
            self.numberImg1 = None
        elif len(hp) == 2:
            self.numberImg3 = None
            if hp[0] == 0:
                self.numberImg1 = self.numbers[0]
            elif hp[0] == 1:
                self.numberImg1 = self.numbers[1]
            elif hp[0] == 2:
                self.numberImg1 = self.numbers[2]
            elif hp[0] == 3:
                self.numberImg1 = self.numbers[3]
            elif hp[0] == 4:
                self.numberImg1 = self.numbers[4]
            elif hp[0] == 5:
                self.numberImg1 = self.numbers[5]
            elif hp[0] == 6:
                self.numberImg1 = self.numbers[6]
            elif hp[0] == 7:
                self.numberImg1 = self.numbers[7]
            elif hp[0] == 8:
                self.numberImg1 = self.numbers[8]
            elif hp[0] == 9:
                self.numberImg1 = self.numbers[9]

            if hp[1] == 0:
                self.numberImg2 = self.numbers[0]
            elif hp[1] == 1:
                self.numberImg2 = self.numbers[1]
            elif hp[1] == 2:
                self.numberImg2 = self.numbers[2]
            elif hp[1] == 3:
                self.numberImg2 = self.numbers[3]
            elif hp[1] == 4:
                self.numberImg2 = self.numbers[4]
            elif hp[1] == 5:
                self.numberImg2 = self.numbers[5]
            elif hp[1] == 6:
                self.numberImg2 = self.numbers[6]
            elif hp[1] == 7:
                self.numberImg2 = self.numbers[7]
            elif hp[1] == 8:
                self.numberImg2 = self.numbers[8]
            elif hp[1] == 9:
                self.numberImg2 = self.numbers[9]

            self.numberRect1 = self.numberImg1.get_rect()
            self.numberRect2 = self.numberImg2.get_rect()

            self.numberRect2.centery = self.rect.bottom - 25
            self.numberRect2.right = self.rect.right - 65
            self.numberRect1.centery = self.rect.bottom - 25
            self.numberRect1.right = self.numberRect2.left
        elif len(hp) == 3:
            if hp[0] == 0:
                self.numberImg1 = self.numbers[0]
            elif hp[0] == 1:
                self.numberImg1 = self.numbers[1]
            elif hp[0] == 2:
                self.numberImg1 = self.numbers[2]
            elif hp[0] == 3:
                self.numberImg1 = self.numbers[3]
            elif hp[0] == 4:
                self.numberImg1 = self.numbers[4]
            elif hp[0] == 5:
                self.numberImg1 = self.numbers[5]
            elif hp[0] == 6:
                self.numberImg1 = self.numbers[6]
            elif hp[0] == 7:
                self.numberImg1 = self.numbers[7]
            elif hp[0] == 8:
                self.numberImg1 = self.numbers[8]
            elif hp[0] == 9:
                self.numberImg1 = self.numbers[9]

            if hp[1] == 0:
                self.numberImg2 = self.numbers[0]
            elif hp[1] == 1:
                self.numberImg2 = self.numbers[1]
            elif hp[1] == 2:
                self.numberImg2 = self.numbers[2]
            elif hp[1] == 3:
                self.numberImg2 = self.numbers[3]
            elif hp[1] == 4:
                self.numberImg2 = self.numbers[4]
            elif hp[1] == 5:
                self.numberImg2 = self.numbers[5]
            elif hp[1] == 6:
                self.numberImg2 = self.numbers[6]
            elif hp[1] == 7:
                self.numberImg2 = self.numbers[7]
            elif hp[1] == 8:
                self.numberImg2 = self.numbers[8]
            elif hp[1] == 9:
                self.numberImg2 = self.numbers[9]

            if hp[2] == 0:
                self.numberImg3 = self.numbers[0]
            elif hp[2] == 1:
                self.numberImg3 = self.numbers[1]
            elif hp[2] == 2:
                self.numberImg3 = self.numbers[2]
            elif hp[2] == 3:
                self.numberImg3 = self.numbers[3]
            elif hp[2] == 4:
                self.numberImg3 = self.numbers[4]
            elif hp[2] == 5:
                self.numberImg3 = self.numbers[5]
            elif hp[2] == 6:
                self.numberImg3 = self.numbers[6]
            elif hp[2] == 7:
                self.numberImg3 = self.numbers[7]
            elif hp[2] == 8:
                self.numberImg3 = self.numbers[8]
            elif hp[2] == 9:
                self.numberImg3 = self.numbers[9]

            self.numberRect1 = self.numberImg1.get_rect()
            self.numberRect2 = self.numberImg2.get_rect()
            self.numberRect3 = self.numberImg3.get_rect()

            self.numberRect3.centery = self.rect.bottom - 25
            self.numberRect3.right = self.rect.right - 65
            self.numberRect2.right = self.numberRect3.left
            self.numberRect2.centery = self.rect.bottom - 25
            self.numberRect1.centery = self.rect.bottom - 25
            self.numberRect1.right = self.numberRect2.left
        else:
            self.numberImg = self.numbers[7]

            self.numberRect = self.numberImg.get_rect()
            self.numberRect.right = self.rect.right - 70
            self.numberRect.centery = self.rect.bottom - 25

        self.game.screen.blit(self.image, self.rect)
        try:
            self.game.screen.blit(self.numberImg1, self.numberRect1)
            self.game.screen.blit(self.numberImg2, self.numberRect2)
            try:
                self.game.screen.blit(self.numberImg3, self.numberRect3)
            except:
                pass
        except:
            self.game.screen.blit(self.numberImg, self.numberRect)


class LuigiUI(pg.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.ui
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        sheet = spritesheet("sprites/ui.png", "sprites/ui.xml")
        self.numbers = [sheet.getImageName("0_hp.png"),
                        sheet.getImageName("1_hp.png"),
                        sheet.getImageName("2_hp.png"),
                        sheet.getImageName("3_hp.png"),
                        sheet.getImageName("4_hp.png"),
                        sheet.getImageName("5_hp.png"),
                        sheet.getImageName("6_hp.png"),
                        sheet.getImageName("7_hp.png"),
                        sheet.getImageName("8_hp.png"),
                        sheet.getImageName("9_hp.png")]
        self.sprites = [pg.image.load("sprites/ui/LuigiJump.png"),
                        pg.image.load("sprites/ui/LuigiHammer.png"),
                        pg.image.load("sprites/ui/LuigiInteract.png"),
                        pg.image.load("sprites/ui/LuigiTalk.png"),
                        pg.image.load("sprites/ui/LuigiThunder.png")]
        self.image = self.sprites[0]
        self.rect = self.image.get_rect()
        self.rect.right = width
        self.rect.top = 0
        self.speed = 0
        self.hp = self.game.follower.stats["hp"]

    def update(self):
        if self.game.follower.abilities[self.game.follower.ability] == "jump":
            self.image = self.sprites[0]
        elif self.game.follower.abilities[self.game.follower.ability] == "hammer":
            self.image = self.sprites[1]
        elif self.game.follower.abilities[self.game.follower.ability] == "interact":
            self.image = self.sprites[2]
        elif self.game.follower.abilities[self.game.follower.ability] == "talk":
            self.image = self.sprites[3]
        elif self.game.follower.abilities[self.game.follower.ability] == "thunder":
            self.image = self.sprites[4]

        self.rect = self.image.get_rect()
        self.rect.right = width
        self.rect.top = 0

    def draw(self):
        if self.hp > self.game.follower.stats["hp"] and self.speed == 0:
            self.speed = ((self.hp - self.game.follower.stats["hp"]) / 30) * -1
        elif self.hp < self.game.follower.stats["hp"] and self.speed == 0:
            self.speed = (self.game.follower.stats["hp"] - self.hp) / 30

        if self.speed != 0:
            if self.hp > self.game.follower.stats["hp"] + self.speed and self.speed < 0:
                self.hp += self.speed
            elif self.hp < self.game.follower.stats["hp"] - self.speed and self.speed > 0:
                self.hp += self.speed
            else:
                self.hp = self.game.follower.stats["hp"]
                self.speed = 0

        if self.hp < 0:
            hp = [0]
        else:
            hp = [int(i) for i in str(round(self.hp))]

        if len(hp) == 1:
            self.numberImg1 = None

            if hp[0] == 0:
                self.numberImg = self.numbers[0]
            elif hp[0] == 1:
                self.numberImg = self.numbers[1]
            elif hp[0] == 2:
                self.numberImg = self.numbers[2]
            elif hp[0] == 3:
                self.numberImg = self.numbers[3]
            elif hp[0] == 4:
                self.numberImg = self.numbers[4]
            elif hp[0] == 5:
                self.numberImg = self.numbers[5]
            elif hp[0] == 6:
                self.numberImg = self.numbers[6]
            elif hp[0] == 7:
                self.numberImg = self.numbers[7]
            elif hp[0] == 8:
                self.numberImg = self.numbers[8]
            elif hp[0] == 9:
                self.numberImg = self.numbers[9]

            self.numberRect = self.numberImg.get_rect()
            self.numberRect.right = self.rect.right - 45
            self.numberRect.centery = self.rect.bottom - 25
        elif len(hp) == 2:
            self.numberImg = None
            self.numberImg3 = None
            if hp[0] == 0:
                self.numberImg1 = self.numbers[0]
            elif hp[0] == 1:
                self.numberImg1 = self.numbers[1]
            elif hp[0] == 2:
                self.numberImg1 = self.numbers[2]
            elif hp[0] == 3:
                self.numberImg1 = self.numbers[3]
            elif hp[0] == 4:
                self.numberImg1 = self.numbers[4]
            elif hp[0] == 5:
                self.numberImg1 = self.numbers[5]
            elif hp[0] == 6:
                self.numberImg1 = self.numbers[6]
            elif hp[0] == 7:
                self.numberImg1 = self.numbers[7]
            elif hp[0] == 8:
                self.numberImg1 = self.numbers[8]
            elif hp[0] == 9:
                self.numberImg1 = self.numbers[9]

            if hp[1] == 0:
                self.numberImg2 = self.numbers[0]
            elif hp[1] == 1:
                self.numberImg2 = self.numbers[1]
            elif hp[1] == 2:
                self.numberImg2 = self.numbers[2]
            elif hp[1] == 3:
                self.numberImg2 = self.numbers[3]
            elif hp[1] == 4:
                self.numberImg2 = self.numbers[4]
            elif hp[1] == 5:
                self.numberImg2 = self.numbers[5]
            elif hp[1] == 6:
                self.numberImg2 = self.numbers[6]
            elif hp[1] == 7:
                self.numberImg2 = self.numbers[7]
            elif hp[1] == 8:
                self.numberImg2 = self.numbers[8]
            elif hp[1] == 9:
                self.numberImg2 = self.numbers[9]

            self.numberRect1 = self.numberImg1.get_rect()
            self.numberRect2 = self.numberImg2.get_rect()

            self.numberRect2.centery = self.rect.bottom - 25
            self.numberRect2.right = self.rect.right - 45
            self.numberRect1.centery = self.rect.bottom - 25
            self.numberRect1.right = self.numberRect2.left
        elif len(hp) == 3:
            if hp[0] == 0:
                self.numberImg1 = self.numbers[0]
            elif hp[0] == 1:
                self.numberImg1 = self.numbers[1]
            elif hp[0] == 2:
                self.numberImg1 = self.numbers[2]
            elif hp[0] == 3:
                self.numberImg1 = self.numbers[3]
            elif hp[0] == 4:
                self.numberImg1 = self.numbers[4]
            elif hp[0] == 5:
                self.numberImg1 = self.numbers[5]
            elif hp[0] == 6:
                self.numberImg1 = self.numbers[6]
            elif hp[0] == 7:
                self.numberImg1 = self.numbers[7]
            elif hp[0] == 8:
                self.numberImg1 = self.numbers[8]
            elif hp[0] == 9:
                self.numberImg1 = self.numbers[9]

            if hp[1] == 0:
                self.numberImg2 = self.numbers[0]
            elif hp[1] == 1:
                self.numberImg2 = self.numbers[1]
            elif hp[1] == 2:
                self.numberImg2 = self.numbers[2]
            elif hp[1] == 3:
                self.numberImg2 = self.numbers[3]
            elif hp[1] == 4:
                self.numberImg2 = self.numbers[4]
            elif hp[1] == 5:
                self.numberImg2 = self.numbers[5]
            elif hp[1] == 6:
                self.numberImg2 = self.numbers[6]
            elif hp[1] == 7:
                self.numberImg2 = self.numbers[7]
            elif hp[1] == 8:
                self.numberImg2 = self.numbers[8]
            elif hp[1] == 9:
                self.numberImg2 = self.numbers[9]

            if hp[2] == 0:
                self.numberImg3 = self.numbers[0]
            elif hp[2] == 1:
                self.numberImg3 = self.numbers[1]
            elif hp[2] == 2:
                self.numberImg3 = self.numbers[2]
            elif hp[2] == 3:
                self.numberImg3 = self.numbers[3]
            elif hp[2] == 4:
                self.numberImg3 = self.numbers[4]
            elif hp[2] == 5:
                self.numberImg3 = self.numbers[5]
            elif hp[2] == 6:
                self.numberImg3 = self.numbers[6]
            elif hp[2] == 7:
                self.numberImg3 = self.numbers[7]
            elif hp[2] == 8:
                self.numberImg3 = self.numbers[8]
            elif hp[2] == 9:
                self.numberImg3 = self.numbers[9]

            self.numberRect1 = self.numberImg1.get_rect()
            self.numberRect2 = self.numberImg2.get_rect()
            self.numberRect3 = self.numberImg3.get_rect()

            self.numberRect3.centery = self.rect.bottom - 25
            self.numberRect3.right = self.rect.right - 45
            self.numberRect2.right = self.numberRect3.left
            self.numberRect2.centery = self.rect.bottom - 25
            self.numberRect1.centery = self.rect.bottom - 25
            self.numberRect1.right = self.numberRect2.left
        else:
            self.numberImg = self.numbers[9]

            self.numberRect = self.numberImg.get_rect()
            self.numberRect.right = self.rect.right - 70
            self.numberRect.centery = self.rect.bottom - 25

        self.game.screen.blit(self.image, self.rect)
        try:
            self.game.screen.blit(self.numberImg, self.numberRect)
        except:
            self.game.screen.blit(self.numberImg1, self.numberRect1)
            self.game.screen.blit(self.numberImg2, self.numberRect2)
            try:
                self.game.screen.blit(self.numberImg3, self.numberRect3)
            except:
                pass


class HitNumbers(pg.sprite.Sprite):
    def __init__(self, game, room, pos, number, type="normal"):
        self.groups = game.ui
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.offset = True
        sheet = spritesheet("sprites/ui.png", "sprites/ui.xml")
        self.alpha = 255
        if type == "normal":
            self.base = sheet.getImageName("hit.png")
            self.game.damageGiven += number
        elif type == "mario":
            self.base = sheet.getImageName("hit_mario.png")
            self.game.damageTaken += number
        elif type == "luigi":
            self.base = sheet.getImageName("hit_luigi.png")
            self.game.damageTaken += number
        self.counter = 0
        self.room = room
        self.image = self.base
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.number = str(number)

    def draw(self):
        self.game.blit_alpha(self.game.screen, self.image, self.game.camera.offset(self.rect), self.alpha)
        ptext.draw(self.number, (self.game.camera.offset(self.rect).centerx, self.game.camera.offset(self.rect).centery + 5), anchor=(0.5, 0.5), color=(255, 213, 0),
                       gcolor=(242, 113, 100), fontname=superMario256, owidth=0.7, surf=self.game.screen, fontsize=50, alpha=self.alpha / 255)

    def update(self):
        self.counter += 1

        if self.counter >= fps:
            self.alpha -= 10
            if self.alpha <= 0:
                self.kill()

        if self.game.room != self.room:
            self.kill()


class ExpNumbers(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.game.battleEndUI.append(self)
        self.offset = False
        self.image = pg.image.load("sprites/ui/exp collection_exp.png")
        self.rect = self.image.get_rect()
        self.exp = self.game.battleXp
        self.prevXp = self.game.battleXp
        self.totalXp = self.game.battleXp
        self.room = self.game.room
        self.counter = 0
        self.rect.center = (500, 150)
        self.speed = self.exp / 45

    def update(self):
        if not self.game.player.dead:
            if self.game.marioBattleOver.counter >= len(self.game.marioBattleOver.points) - 1 and self.exp > self.speed:
                self.exp -= self.speed
            elif self.game.marioBattleOver.counter >= len(self.game.marioBattleOver.points) - 1:
                self.exp = 0
        elif not self.game.follower.dead:
            if self.game.luigiBattleOver.counter >= len(self.game.luigiBattleOver.points) - 1 and self.exp > self.speed:
                self.exp -= self.speed
            elif self.game.luigiBattleOver.counter >= len(self.game.luigiBattleOver.points) - 1:
                self.exp = 0

        if round(self.exp) != self.prevXp:
            self.prevXp = round(self.exp)
            self.game.expIncreaseSound.stop()
            self.game.expFinishedSound.stop()
            if self.totalXp <= 9:
                self.game.expFinishedSound.play()
            else:
                if self.prevXp == 0:
                    self.game.expFinishedSound.play()
                else:
                    self.game.expIncreaseSound.play()

        if self.room != self.game.room:
            self.game.battleEndUI.remove(self)

    def draw(self):
        self.game.screen.blit(self.image, self.rect)
        ptext.draw(str(round(self.exp)), (self.rect.right - 50, self.rect.bottom - 70), owidth=1, fontname=expNumbers,
                   fontsize=40, color=(255, 204, 0), anchor=(1, 0))


class MarioExpNumbers(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.game.battleEndUI.append(self)
        if self.game.player.dead:
            self.dead = True
        else:
            self.dead = False
        self.offset = False
        self.image = pg.image.load("sprites/ui/exp collection_mario.png")
        self.rect = self.image.get_rect()
        self.room = self.game.room
        self.rect.center = (500, 300)

    def update(self):
        if self.room != self.game.room:
            self.game.battleEndUI.remove(self)

    def draw(self):
        self.game.screen.blit(self.image, self.rect)
        ptext.draw(str(round(self.game.player.stats["exp"])), (self.rect.right - 50, self.rect.bottom - 70), owidth=1,
                   fontname=expNumbers, fontsize=40, color=(255, 204, 0), anchor=(1, 0))


class LuigiExpNumbers(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.game.battleEndUI.append(self)
        self.offset = False
        if self.game.follower.dead:
            self.dead = True
        else:
            self.dead = False
        self.image = pg.image.load("sprites/ui/exp collection_luigi.png")
        self.rect = self.image.get_rect()
        self.room = self.game.room
        self.rect.center = (500, 500)

    def update(self):
        if self.room != self.game.room:
            self.game.battleEndUI.remove(self)

    def draw(self):
        self.game.screen.blit(self.image, self.rect)
        ptext.draw(str(round(self.game.follower.stats["exp"])), (self.rect.right - 50, self.rect.bottom - 70), owidth=1,
                   fontname=expNumbers, fontsize=40, color=(255, 204, 0), anchor=(1, 0))


class CoinCollectionSubtract(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.game.battleEndUI.append(self)
        self.offset = False
        self.image = pg.image.load("sprites/ui/coin collection_earned.png")
        self.rect = self.image.get_rect()
        self.exp = self.game.battleCoins
        self.prevXp = self.game.battleCoins
        self.totalXp = self.game.battleCoins
        self.room = self.game.room
        self.counter = 0
        self.rect.center = (1000, 150)
        self.speed = self.exp / 45
        if not self.game.player.dead:
            self.parent = self.game.marioBattleOver
        else:
            self.parent = self.game.luigiBattleOver
        self.canGo = False

    def update(self):
        if self.parent.counter >= len(self.parent.points) - 1:
            self.canGo = True
        if self.game.expNumbers.exp == 0 and self.exp > self.speed and self.canGo:
            if self.counter >= 45:
                self.exp -= self.speed
            else:
                self.counter += 1
        elif self.game.expNumbers.exp == 0:
            self.exp = 0

        if round(self.exp) != self.prevXp:
            self.prevXp = round(self.exp)
            self.game.expIncreaseSound.stop()
            self.game.expFinishedSound.stop()
            if self.totalXp <= 9:
                self.game.expFinishedSound.play()
            else:
                if self.prevXp == 0:
                    self.game.expFinishedSound.play()
                else:
                    self.game.expIncreaseSound.play()

        if self.room != self.game.room:
            self.game.battleEndUI.remove(self)

    def draw(self):
        self.game.screen.blit(self.image, self.rect)
        ptext.draw(str(round(self.exp)), (self.rect.right - 50, self.rect.bottom - 70), owidth=1, fontname=expNumbers,
                   fontsize=40, color=(255, 204, 0), anchor=(1, 0))


class CoinCollectionAdd(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.game.battleEndUI.append(self)
        self.offset = False
        self.image = pg.image.load("sprites/ui/coin collection_total.png")
        self.rect = self.image.get_rect()
        self.exp = 0
        self.counter = 0
        self.totalCoins = self.game.battleCoins
        self.coins = self.game.coins
        self.room = self.game.room
        self.rect.center = (1000, 400)
        self.speed = self.totalCoins / 45

    def update(self):
        if self.game.expNumbers.exp == 0 and self.exp < self.totalCoins:
            if self.counter >= 45:
                self.exp += self.speed
            else:
                self.counter += 1
        elif self.game.expNumbers.exp == 0:
            self.exp = self.totalCoins

        if self.room != self.game.room:
            self.game.battleEndUI.remove(self)

    def draw(self):
        self.game.screen.blit(self.image, self.rect)
        if round(self.exp) + self.coins > self.game.coins:
            ptext.draw(str(round(self.exp) + self.coins), (self.rect.right - 50, self.rect.bottom - 70), owidth=1,
                       fontname=expNumbers, fontsize=40, color=(255, 204, 0), anchor=(1, 0))
        else:
            ptext.draw(str(self.game.coins), (self.rect.right - 50, self.rect.bottom - 70), owidth=1,
                       fontname=expNumbers, fontsize=40, color=(255, 204, 0), anchor=(1, 0))


class Cursor(pg.sprite.Sprite):
    def __init__(self, game, target, facing="left"):
        pg.sprite.Sprite.__init__(self, game.cursors)
        self.game = game
        sheet = spritesheet("sprites/ui.png", "sprites/ui.xml")
        self.facing = facing
        self.sprites = [sheet.getImageName("cursor_1.png"),
                        sheet.getImageName("cursor_2.png"),
                        sheet.getImageName("cursor_3.png"),
                        sheet.getImageName("cursor_4.png"),
                        sheet.getImageName("cursor_5.png"),
                        sheet.getImageName("cursor_6.png"),
                        sheet.getImageName("cursor_7.png"),
                        sheet.getImageName("cursor_8.png"),
                        sheet.getImageName("cursor_9.png"),
                        sheet.getImageName("cursor_10.png"),
                        sheet.getImageName("cursor_11.png"),
                        sheet.getImageName("cursor_12.png"),
                        sheet.getImageName("cursor_13.png"),
                        sheet.getImageName("cursor_14.png"),
                        sheet.getImageName("cursor_15.png"),
                        sheet.getImageName("cursor_16.png"),
                        sheet.getImageName("cursor_17.png"),
                        sheet.getImageName("cursor_18.png"),
                        sheet.getImageName("cursor_19.png"),
                        sheet.getImageName("cursor_20.png"),
                        sheet.getImageName("cursor_21.png")]
        self.reverseSprites = []
        for sprite in self.sprites:
            self.reverseSprites.append(pg.transform.flip(sprite, True, False))
        if self.facing == "left":
            self.image = self.sprites[0]
        elif self.facing == "right":
            self.image = self.reverseSprites[0]
        self.rect = self.image.get_rect()
        if self.facing == "right":
            self.rect.left = target.right + 5
            self.rect.centery = target.top - 10
        elif self.facing == "left":
            self.rect.right = target.left - 5
            self.rect.centery = target.top - 10
        self.target = target
        self.prevTarget = target
        self.lastUpdate = 0
        self.currentFrame = 0
        self.points = []
        self.counter = -17

    def update(self, target, speed):
        self.animate()

        if target != self.prevTarget:
            self.counter = 0
            self.prevTarget = target
        elif self.counter != speed:
            if self.facing == "right":
                self.rect.left, self.rect.centery = pt.getPointOnLine(self.rect.left, self.rect.centery,
                                                                      target.right + 5, target.top - 10,
                                                                      (self.counter / speed))
            elif self.facing == "left":
                self.rect.right, self.rect.centery = pt.getPointOnLine(self.rect.right, self.rect.centery,
                                                                       target.left - 5, target.top - 10,
                                                                       (self.counter / speed))
            self.counter += 1
        else:
            self.counter = speed
            if self.facing == "right":
                self.rect.left = target.right + 5
                self.rect.centery = target.top - 10
            elif self.facing == "left":
                self.rect.right = target.left - 5
                self.rect.centery = target.top - 10

    def animate(self):
        now = pg.time.get_ticks()

        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.currentFrame < len(self.sprites):
                self.currentFrame = (self.currentFrame + 1) % (len(self.sprites))
            else:
                self.currentFrame = 0
            center = self.rect.center
            if self.facing == "right":
                self.image = self.sprites[self.currentFrame]
            elif self.facing == "left":
                self.image = self.reverseSprites[self.currentFrame]
            self.rect = self.image.get_rect()
            self.rect.center = center


class EnemyNames(pg.sprite.Sprite):
    def __init__(self, game, name, image=None):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        if image is None:
            self.image = pg.image.load("sprites/ui/enemySelection.png").convert_alpha()
        else:
            self.image = image
        self.rect = self.image.get_rect()
        self.rect.left = 0
        self.rect.top = 0
        self.name = name

    def update(self, name):
        self.name = name

    def draw(self):
        self.game.screen.blit(self.image, self.rect)
        ptext.draw(self.name, (self.rect.left + 10, self.rect.bottom - 75), fontname=dialogueFont,
                   fontsize=40,
                   lineheight=0.8, surf=self.game.screen)


class Fadeout(pg.sprite.Sprite):
    def __init__(self, game, speed=20):
        pg.sprite.Sprite.__init__(self, game.fadeout)
        self.game = game
        self.speed = speed
        self.image = pg.Surface((self.game.screen.get_width(), self.game.screen.get_height()))
        self.rect = self.image.get_rect()
        self.imgRect = self.rect
        self.image.fill(black)
        self.alpha = 1
        self.image.set_alpha(self.alpha)
        self.room = self.game.room

    def update(self):
        self.image.set_alpha(self.alpha)
        if self.room == self.game.room and self.alpha < 255:
            self.alpha += self.speed
        elif self.room != self.game.room:
            self.alpha -= self.speed
        elif self.alpha > 255:
            self.alpha = 255

        if self.alpha < 0:
            self.kill()

        self.image.set_alpha(self.alpha)


class SaveSelection(pg.sprite.Sprite):
    def __init__(self, game, save):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        try:
            with open("saves/File " + str(save) + ".ini", "rb") as file:
                self.image = pg.image.load("sprites/save selection.png").convert_alpha()
                self.area = pickle.load(file)
                self.storeData = pickle.load(file)
                self.playtime = pickle.load(file)
        except:
            self.image = pg.image.load("sprites/save selection ng.png").convert_alpha()
        self.rect = self.image.get_rect()
        if save == 1:
            self.rect.center = (217, 360)
        elif save == 2:
            self.rect.center = (640, 360)
        elif save == 3:
            self.rect.center = (1061, 360)

    def draw(self):
        self.game.screen.blit(self.image, self.rect)
        try:
            ptext.draw("LV " + str(self.storeData["mario stats"]["level"]), (self.rect.left + 30, self.rect.top + 260),
                       fontname=superMario256, fontsize=25, anchor=(0, 0.5), surf=self.game.screen)
            ptext.draw("LV " + str(self.storeData["luigi stats"]["level"]), (self.rect.left + 185, self.rect.top + 260),
                       fontname=superMario256, fontsize=25, anchor=(0, 0.5), surf=self.game.screen)
            ptext.draw(str(self.area), (self.rect.left + self.rect.width / 2, self.rect.top + 330),
                       fontname=dialogueFont, fontsize=25, anchor=(0.5, 0.5), surf=self.game.screen)
            ptext.draw(self.playtime, (self.rect.left + self.rect.width / 2, self.rect.top + 414),
                       fontname=dialogueFont, fontsize=25, anchor=(0.5, 0.5), surf=self.game.screen)
        except:
            pass
