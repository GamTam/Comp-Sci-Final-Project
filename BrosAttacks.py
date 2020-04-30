import xml.etree.ElementTree as ET
import random
from Libraries import ptext
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


class MenuIcon(pg.sprite.Sprite):
    def __init__(self, game, pos, text="Oof, It's [Broke]", icon=talkAdvanceSprite, info=None):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.text = text
        self.icon = icon
        if icon is not None:
         self.rect = self.icon.get_rect()
        if icon is not None:
            self.rect.center = pos
        else:
            self.pos = pos
        self.color = white
        self.info = info

    def draw(self, offset=None):
        if offset is None:
            if self.icon is not None:
                self.game.screen.blit(self.icon, self.rect)
                ptext.draw(self.text, midleft=(self.rect.right + 30, self.rect.centery), color=self.color, surf=self.game.screen, owidth=1,
                               fontname=dialogueFont, fontsize=40)
            else:
                ptext.draw(self.text, midleft=self.pos, color=self.color,
                           surf=self.game.screen, owidth=1,
                           fontname=dialogueFont, fontsize=40)
        else:
            if self.icon is not None:
                self.game.screen.blit(self.icon, offset)
                ptext.draw(self.text, midleft=(offset.right + 30, offset.centery), color=self.color,
                           surf=self.game.screen, owidth=1,
                           fontname=dialogueFont, fontsize=40)
            else:
                ptext.draw(self.text, midleft=self.pos, color=self.color,
                           surf=self.game.screen, owidth=1,
                           fontname=dialogueFont, fontsize=40)


class MarioRecoverables(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.bp = str(self.game.player.stats["bp"])
        self.maxBP = str(self.game.player.stats["maxBP"])
        self.hp = str(self.game.player.stats["hp"])
        self.maxHP = str(self.game.player.stats["maxHP"])
        self.BPimage = pg.image.load("sprites/ui/marioBP.png")
        self.HPimage = pg.image.load("sprites/ui/marioHP.png")
        self.rect = self.BPimage.get_rect()
        self.rect.bottom = height
        self.rect.left = 235

    def draw(self, recoverable="bp"):
        if recoverable == "bp":
            self.game.screen.blit(self.BPimage, self.rect)
            ptext.draw(self.bp + "/" + self.maxBP, (self.rect.left + 80, self.rect.centery), owidth=1,
                       fontname=superMario256, fontsize=40, color=(255, 204, 0), anchor=(0, 0.5))
        else:
            self.game.screen.blit(self.HPimage, self.rect)
            ptext.draw(self.hp + "/" + self.maxHP, (self.rect.left + 80, self.rect.centery), owidth=1,
                       fontname=superMario256, fontsize=40, color=(255, 204, 0), anchor=(0, 0.5))


class LuigiRecoverables(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.bp = str(self.game.follower.stats["bp"])
        self.maxBP = str(self.game.follower.stats["maxBP"])
        self.hp = str(self.game.follower.stats["hp"])
        self.maxHP = str(self.game.follower.stats["maxHP"])
        self.BPimage = pg.image.load("sprites/ui/luigiBP.png")
        self.HPimage = pg.image.load("sprites/ui/luigiHP.png")
        self.rect = self.BPimage.get_rect()
        self.rect.bottom = height
        self.rect.left = 743

    def draw(self, recoverable="bp"):
        if recoverable == "bp":
            self.game.screen.blit(self.BPimage, self.rect)
            ptext.draw(self.bp + "/" + self.maxBP, (self.rect.left + 80, self.rect.centery), owidth=1,
                       fontname=superMario256, fontsize=40, color=(255, 204, 0), anchor=(0, 0.5))
        else:
            self.game.screen.blit(self.HPimage, self.rect)
            ptext.draw(self.hp + "/" + self.maxHP, (self.rect.left + 80, self.rect.centery), owidth=1,
                       fontname=superMario256, fontsize=40, color=(255, 204, 0), anchor=(0, 0.5))


class GreenShell(pg.sprite.Sprite):
    def __init__(self, game, speed):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.alpha = 255
        self.speed = speed
        self.currentFrame = 0
        self.lastUpdate = 0
        self.missed = False
        self.loadImages()
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.travelSpeed = 0
        self.rect.center = (225, 650)
        self.counter = 0
        self.points = []
        self.prevTarget = "luigi"
        self.target = "enemy"

    def loadImages(self):
        sheet = spritesheet("sprites/bros attacks/koopa_shell.png", "sprites/bros attacks/koopa_shell.xml")

        self.frames = [sheet.getImageName("green_shell_1.png"),
                       sheet.getImageName("green_shell_2.png"),
                       sheet.getImageName("green_shell_3.png"),
                       sheet.getImageName("green_shell_4.png"),
                       sheet.getImageName("green_shell_5.png"),
                       sheet.getImageName("green_shell_6.png"),
                       sheet.getImageName("green_shell_7.png"),
                       sheet.getImageName("green_shell_8.png")]

    def update(self):
        self.animate()
        if not self.missed:
            self.rect.center = self.points[self.counter]
            self.counter += 1
        elif self.missed:
            self.rect.centerx += self.travelSpeed[0]
            self.rect.centery += self.travelSpeed[1]

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.currentFrame < len(self.frames):
                self.currentFrame = (self.currentFrame + 1) % (len(self.frames))
            else:
                self.currentFrame = 0
            center = self.rect.center
            self.image = self.frames[self.currentFrame]
            self.rect = self.image.get_rect()
            self.rect.center = center


class RedShell(pg.sprite.Sprite):
    def __init__(self, game, speed):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.alpha = 255
        self.speed = speed
        self.currentFrame = 0
        self.lastUpdate = 0
        self.missed = False
        self.loadImages()
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.travelSpeed = 0
        self.rect.center = (251, 450)
        self.counter = 0
        self.points = []
        self.prevTarget = "mario"
        self.target = "enemy"

    def loadImages(self):
        sheet = spritesheet("sprites/bros attacks/koopa_shell.png", "sprites/bros attacks/koopa_shell.xml")

        self.frames = [sheet.getImageName("red_shell_1.png"),
                       sheet.getImageName("red_shell_2.png"),
                       sheet.getImageName("red_shell_3.png"),
                       sheet.getImageName("red_shell_4.png"),
                       sheet.getImageName("red_shell_5.png"),
                       sheet.getImageName("red_shell_6.png"),
                       sheet.getImageName("red_shell_7.png"),
                       sheet.getImageName("red_shell_8.png")]

    def update(self):
        self.animate()
        if not self.missed:
            self.rect.center = self.points[self.counter]
            self.counter += 1
        elif self.missed:
            self.rect.centerx += self.travelSpeed[0]
            self.rect.centery += self.travelSpeed[1]

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 45:
            self.lastUpdate = now
            if self.currentFrame < len(self.frames):
                self.currentFrame = (self.currentFrame + 1) % (len(self.frames))
            else:
                self.currentFrame = 0
            center = self.rect.center
            self.image = self.frames[self.currentFrame]
            self.rect = self.image.get_rect()
            self.rect.center = center


class MarioShell(pg.sprite.Sprite):
    def __init__(self, game, shell):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.alpha = 255
        self.shell = shell
        self.currentFrame = 0
        self.lastUpdate = 0
        self.loadImages()
        self.target = False
        self.kicking = False
        self.onShell = False
        self.messedUp = False
        self.hitIt = False
        self.lookAtLuigi = False
        self.winPose = False
        self.image = self.standingFrames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (251, 400)

    def loadImages(self):
        sheet = spritesheet("sprites/bros attacks/koopa_shell.png", "sprites/bros attacks/koopa_shell.xml")

        self.standingFrames = [sheet.getImageName("mario_standing_1.png"),
                               sheet.getImageName("mario_standing_2.png"),
                               sheet.getImageName("mario_standing_3.png"),
                               sheet.getImageName("mario_standing_4.png"),
                               sheet.getImageName("mario_standing_5.png"),
                               sheet.getImageName("mario_standing_6.png"),
                               sheet.getImageName("mario_standing_7.png"),
                               sheet.getImageName("mario_standing_8.png"),
                               sheet.getImageName("mario_standing_9.png")]

        self.readyHitFrames = [sheet.getImageName("mario_ready_hit_1.png"),
                               sheet.getImageName("mario_ready_hit_2.png"),
                               sheet.getImageName("mario_ready_hit_3.png"),
                               sheet.getImageName("mario_ready_hit_4.png"),
                               sheet.getImageName("mario_ready_hit_5.png"),
                               sheet.getImageName("mario_ready_hit_6.png"),
                               sheet.getImageName("mario_ready_hit_7.png")]

        self.kickFrames = [sheet.getImageName("mario_hitting_1.png"),
                           sheet.getImageName("mario_hitting_2.png"),
                           sheet.getImageName("mario_hitting_3.png"),
                           sheet.getImageName("mario_hitting_4.png")]

        self.onShellFrames = [sheet.getImageName("mario_on_shell_1.png"),
                              sheet.getImageName("mario_on_shell_2.png"),
                              sheet.getImageName("mario_on_shell_3.png"),
                              sheet.getImageName("mario_on_shell_4.png"),
                              sheet.getImageName("mario_on_shell_5.png"),
                              sheet.getImageName("mario_on_shell_6.png"),
                              sheet.getImageName("mario_on_shell_7.png"),
                              sheet.getImageName("mario_on_shell_8.png"),
                              sheet.getImageName("mario_on_shell_9.png"),
                              sheet.getImageName("mario_on_shell_10.png"),
                              sheet.getImageName("mario_on_shell_11.png")]

        self.messedUpFrames = [sheet.getImageName("mario_miss_hit_1.png"),
                           sheet.getImageName("mario_miss_hit_2.png"),
                           sheet.getImageName("mario_miss_hit_3.png"),
                           sheet.getImageName("mario_miss_hit_4.png")]

        self.lookAtLuigiFrames = [sheet.getImageName("mario_looking_at_luigi_1.png"),
                                  sheet.getImageName("mario_looking_at_luigi_2.png"),
                                  sheet.getImageName("mario_looking_at_luigi_3.png"),
                                  sheet.getImageName("mario_looking_at_luigi_4.png"),
                                  sheet.getImageName("mario_looking_at_luigi_5.png"),
                                  sheet.getImageName("mario_looking_at_luigi_6.png"),
                                  sheet.getImageName("mario_looking_at_luigi_7.png"),
                                  sheet.getImageName("mario_looking_at_luigi_8.png"),
                                  sheet.getImageName("mario_looking_at_luigi_9.png"),
                                  sheet.getImageName("mario_looking_at_luigi_10.png"),
                                  sheet.getImageName("mario_looking_at_luigi_11.png"),
                                  sheet.getImageName("mario_looking_at_luigi_12.png"),
                                  sheet.getImageName("mario_looking_at_luigi_13.png"),
                                  sheet.getImageName("mario_looking_at_luigi_14.png"),
                                  sheet.getImageName("mario_looking_at_luigi_15.png"),
                                  sheet.getImageName("mario_looking_at_luigi_16.png"),
                                  sheet.getImageName("mario_looking_at_luigi_17.png"),
                                  sheet.getImageName("mario_looking_at_luigi_18.png")]

        self.winPoseFrames = [sheet.getImageName("mario_winpose_1.png"),
                              sheet.getImageName("mario_winpose_2.png"),
                              sheet.getImageName("mario_winpose_3.png"),
                              sheet.getImageName("mario_winpose_4.png"),
                              sheet.getImageName("mario_winpose_5.png"),
                              sheet.getImageName("mario_winpose_6.png"),
                              sheet.getImageName("mario_winpose_7.png"),
                              sheet.getImageName("mario_winpose_8.png"),
                              sheet.getImageName("mario_winpose_9.png"),
                              sheet.getImageName("mario_winpose_10.png"),
                              sheet.getImageName("mario_winpose_11.png"),
                              sheet.getImageName("mario_winpose_12.png"),
                              sheet.getImageName("mario_winpose_13.png"),
                              sheet.getImageName("mario_winpose_14.png"),
                              sheet.getImageName("mario_winpose_15.png"),
                              sheet.getImageName("mario_winpose_16.png"),
                              sheet.getImageName("mario_winpose_17.png"),
                              sheet.getImageName("mario_winpose_18.png"),
                              sheet.getImageName("mario_winpose_19.png")]
    def update(self):
        now = pg.time.get_ticks()

        if pg.sprite.collide_rect(self, self.shell):
            self.hitIt = True

        if now - self.lastUpdate > 45:
            if self.lookAtLuigi:
                self.lastUpdate = now
                if self.currentFrame < len(self.lookAtLuigiFrames) - 1:
                    self.currentFrame += 1
                    centerx = self.rect.centerx
                    bottom = self.rect.bottom
                    self.image = self.lookAtLuigiFrames[self.currentFrame]
                    self.rect = self.image.get_rect()
                    self.rect.centerx = centerx
                    self.rect.bottom = bottom
            elif self.winPose:
                self.lastUpdate = now
                if self.currentFrame < len(self.winPoseFrames) - 1:
                    self.currentFrame += 1
                else:
                    self.currentFrame = 6
                centerx = self.rect.centerx
                bottom = self.rect.bottom
                self.image = self.winPoseFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom
            elif not self.target and not self.kicking and not self.onShell and not self.messedUp:
                self.lastUpdate = now
                if self.currentFrame < len(self.standingFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.standingFrames))
                else:
                    self.currentFrame = 0
                centerx = self.rect.centerx
                bottom = self.rect.bottom
                self.image = self.standingFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom
            elif not self.kicking and not self.onShell and not self.messedUp:
                self.lastUpdate = now
                if self.currentFrame < len(self.readyHitFrames) - 1:
                    self.currentFrame += 1
                else:
                    self.currentFrame = 2
                centerx = self.rect.centerx
                bottom = self.rect.bottom
                self.image = self.readyHitFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom
            elif self.kicking and not self.onShell and not self.messedUp:
                self.lastUpdate = now
                if self.currentFrame < len(self.kickFrames) - 1:
                    self.currentFrame += 1
                    centerx = self.rect.centerx
                    bottom = self.rect.bottom
                    self.image = self.kickFrames[self.currentFrame]
                    self.rect = self.image.get_rect()
                    self.rect.centerx = centerx
                    self.rect.bottom = bottom
                else:
                    self.kicking = False
                    if not self.hitIt:
                        self.messedUp = True
                    else:
                        self.hitIt = False
                    self.currentFrame = 0
            elif self.messedUp and not self.onShell:
                self.lastUpdate = now
                if self.currentFrame < len(self.messedUpFrames) - 1:
                    self.currentFrame += 1
                else:
                    self.messedUp = False
                centerx = self.rect.centerx
                bottom = self.rect.bottom
                self.image = self.messedUpFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom
            elif self.onShell:
                self.lastUpdate = now
                if self.currentFrame < len(self.onShellFrames) - 1:
                    self.currentFrame += 1
                else:
                    self.currentFrame = 3
                center = self.rect.center
                self.image = self.onShellFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class LuigiShell(pg.sprite.Sprite):
    def __init__(self, game, shell):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.shell = shell
        self.alpha = 255
        self.currentFrame = 0
        self.lastUpdate = 0
        self.loadImages()
        self.target = False
        self.kicking = False
        self.onShell = False
        self.messedUp = False
        self.hitIt = False
        self.lookAtMario = False
        self.winPose = False
        self.image = self.standingFrames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (225, 600)

    def loadImages(self):
        sheet = spritesheet("sprites/bros attacks/koopa_shell.png", "sprites/bros attacks/koopa_shell.xml")

        self.standingFrames = [sheet.getImageName("luigi_standing_1.png"),
                               sheet.getImageName("luigi_standing_2.png"),
                               sheet.getImageName("luigi_standing_3.png"),
                               sheet.getImageName("luigi_standing_4.png"),
                               sheet.getImageName("luigi_standing_5.png"),
                               sheet.getImageName("luigi_standing_6.png"),
                               sheet.getImageName("luigi_standing_7.png"),
                               sheet.getImageName("luigi_standing_8.png"),
                               sheet.getImageName("luigi_standing_9.png"),
                               sheet.getImageName("luigi_standing_10.png"),
                               sheet.getImageName("luigi_standing_11.png"),
                               sheet.getImageName("luigi_standing_12.png")]

        self.readyHitFrames = [sheet.getImageName("luigi_ready_hit_1.png"),
                               sheet.getImageName("luigi_ready_hit_2.png"),
                               sheet.getImageName("luigi_ready_hit_3.png"),
                               sheet.getImageName("luigi_ready_hit_4.png"),
                               sheet.getImageName("luigi_ready_hit_5.png"),
                               sheet.getImageName("luigi_ready_hit_6.png"),
                               sheet.getImageName("luigi_ready_hit_7.png"),
                               sheet.getImageName("luigi_ready_hit_8.png")]

        self.kickFrames = [sheet.getImageName("luigi_hitting_1.png"),
                           sheet.getImageName("luigi_hitting_2.png"),
                           sheet.getImageName("luigi_hitting_3.png"),
                           sheet.getImageName("luigi_hitting_4.png")]

        self.onShellFrames = [sheet.getImageName("luigi_on_shell_1.png"),
                              sheet.getImageName("luigi_on_shell_2.png"),
                              sheet.getImageName("luigi_on_shell_3.png"),
                              sheet.getImageName("luigi_on_shell_4.png"),
                              sheet.getImageName("luigi_on_shell_5.png"),
                              sheet.getImageName("luigi_on_shell_6.png"),
                              sheet.getImageName("luigi_on_shell_7.png"),
                              sheet.getImageName("luigi_on_shell_8.png"),
                              sheet.getImageName("luigi_on_shell_9.png"),
                              sheet.getImageName("luigi_on_shell_10.png"),
                              sheet.getImageName("luigi_on_shell_11.png")]

        self.messedUpFrames = [sheet.getImageName("luigi_miss_hit_1.png"),
                               sheet.getImageName("luigi_miss_hit_2.png"),
                               sheet.getImageName("luigi_miss_hit_3.png"),
                               sheet.getImageName("luigi_miss_hit_4.png")]

        self.lookAtMarioFrames = [sheet.getImageName("luigi_looking_at_mario_1.png"),
                                  sheet.getImageName("luigi_looking_at_mario_2.png"),
                                  sheet.getImageName("luigi_looking_at_mario_3.png"),
                                  sheet.getImageName("luigi_looking_at_mario_4.png"),
                                  sheet.getImageName("luigi_looking_at_mario_5.png"),
                                  sheet.getImageName("luigi_looking_at_mario_6.png"),
                                  sheet.getImageName("luigi_looking_at_mario_7.png"),
                                  sheet.getImageName("luigi_looking_at_mario_8.png"),
                                  sheet.getImageName("luigi_looking_at_mario_9.png"),
                                  sheet.getImageName("luigi_looking_at_mario_10.png"),
                                  sheet.getImageName("luigi_looking_at_mario_11.png"),
                                  sheet.getImageName("luigi_looking_at_mario_12.png"),
                                  sheet.getImageName("luigi_looking_at_mario_13.png"),
                                  sheet.getImageName("luigi_looking_at_mario_14.png"),
                                  sheet.getImageName("luigi_looking_at_mario_15.png"),
                                  sheet.getImageName("luigi_looking_at_mario_16.png"),
                                  sheet.getImageName("luigi_looking_at_mario_17.png"),
                                  sheet.getImageName("luigi_looking_at_mario_18.png"),
                                  sheet.getImageName("luigi_looking_at_mario_19.png"),
                                  sheet.getImageName("luigi_looking_at_mario_20.png"),
                                  sheet.getImageName("luigi_looking_at_mario_21.png"),
                                  sheet.getImageName("luigi_looking_at_mario_22.png"),
                                  sheet.getImageName("luigi_looking_at_mario_23.png"),
                                  sheet.getImageName("luigi_looking_at_mario_24.png"),
                                  sheet.getImageName("luigi_looking_at_mario_25.png"),
                                  sheet.getImageName("luigi_looking_at_mario_26.png")]

        self.winPoseFrames = [sheet.getImageName("luigi_winpose_1.png"),
                              sheet.getImageName("luigi_winpose_2.png"),
                              sheet.getImageName("luigi_winpose_3.png"),
                              sheet.getImageName("luigi_winpose_4.png"),
                              sheet.getImageName("luigi_winpose_5.png"),
                              sheet.getImageName("luigi_winpose_6.png"),
                              sheet.getImageName("luigi_winpose_7.png"),
                              sheet.getImageName("luigi_winpose_8.png"),
                              sheet.getImageName("luigi_winpose_9.png"),
                              sheet.getImageName("luigi_winpose_10.png"),
                              sheet.getImageName("luigi_winpose_11.png"),
                              sheet.getImageName("luigi_winpose_12.png"),
                              sheet.getImageName("luigi_winpose_13.png"),
                              sheet.getImageName("luigi_winpose_14.png"),
                              sheet.getImageName("luigi_winpose_15.png"),
                              sheet.getImageName("luigi_winpose_16.png"),
                              sheet.getImageName("luigi_winpose_17.png"),
                              sheet.getImageName("luigi_winpose_18.png"),
                              sheet.getImageName("luigi_winpose_19.png"),
                              sheet.getImageName("luigi_winpose_20.png"),
                              sheet.getImageName("luigi_winpose_21.png"),
                              sheet.getImageName("luigi_winpose_22.png"),
                              sheet.getImageName("luigi_winpose_23.png"),
                              sheet.getImageName("luigi_winpose_24.png")]

    def update(self):
        now = pg.time.get_ticks()

        if pg.sprite.collide_rect(self, self.shell):
            self.hitIt = True

        if now - self.lastUpdate > 45:
            if self.lookAtMario:
                self.lastUpdate = now
                if self.currentFrame < len(self.lookAtMarioFrames) - 1:
                    self.currentFrame += 1
                else:
                    self.currentFrame = 4
                centerx = self.rect.centerx
                bottom = self.rect.bottom
                self.image = self.lookAtMarioFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom
            elif self.winPose:
                self.lastUpdate = now
                if self.currentFrame < len(self.winPoseFrames) - 1:
                    self.currentFrame += 1
                else:
                    self.currentFrame = 12
                centerx = self.rect.centerx
                bottom = self.rect.bottom
                self.image = self.winPoseFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom
            elif not self.target and not self.kicking and not self.onShell and not self.messedUp:
                self.lastUpdate = now
                if self.currentFrame < len(self.standingFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.standingFrames))
                else:
                    self.currentFrame = 0
                centerx = self.rect.centerx
                bottom = self.rect.bottom
                self.image = self.standingFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom
            elif not self.kicking and not self.onShell and not self.messedUp:
                self.lastUpdate = now
                if self.currentFrame < len(self.readyHitFrames) - 1:
                    self.currentFrame += 1
                else:
                    self.currentFrame = 2
                centerx = self.rect.centerx
                bottom = self.rect.bottom
                self.image = self.readyHitFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom
            elif self.kicking and not self.onShell and not self.messedUp:
                self.lastUpdate = now
                if self.currentFrame < len(self.kickFrames) - 1:
                    self.currentFrame += 1
                    centerx = self.rect.centerx
                    bottom = self.rect.bottom
                    self.image = self.kickFrames[self.currentFrame]
                    self.rect = self.image.get_rect()
                    self.rect.centerx = centerx
                    self.rect.bottom = bottom
                else:
                    self.kicking = False
                    if not self.hitIt:
                        self.messedUp = True
                    else:
                        self.hitIt = False
                    self.currentFrame = 0
            elif self.messedUp and not self.onShell:
                self.lastUpdate = now
                if self.currentFrame < len(self.messedUpFrames) - 1:
                    self.currentFrame += 1
                else:
                    self.messedUp = False
                centerx = self.rect.centerx
                bottom = self.rect.bottom
                self.image = self.messedUpFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom
            elif self.onShell:
                self.lastUpdate = now
                if self.currentFrame < len(self.onShellFrames) - 1:
                    self.currentFrame += 1
                else:
                    self.currentFrame = 3
                center = self.rect.center
                self.image = self.onShellFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class GoombaBrosAttack(pg.sprite.Sprite):
    def __init__(self, game, enemy):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.hit = False
        self.alpha = 255
        self.lastUpdate = 0
        self.counter = 0
        self.enemy = enemy
        self.loadImages()
        self.currentFrame = random.randrange(0, len(self.standingFrames) - 1)
        self.image = self.standingFrames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (random.randrange(width / 2, width - 100), random.randrange(420, height - 50))
        self.barRect = self.rect

    def loadImages(self):
        sheet = spritesheet("sprites/enemies_bros_attacks.png", "sprites/enemies_bros_attacks.xml")

        self.standingFrames = [sheet.getImageName("goomba_idle_1.png"),
                               sheet.getImageName("goomba_idle_2.png"),
                               sheet.getImageName("goomba_idle_3.png"),
                               sheet.getImageName("goomba_idle_4.png"),
                               sheet.getImageName("goomba_idle_5.png"),
                               sheet.getImageName("goomba_idle_6.png"),
                               sheet.getImageName("goomba_idle_7.png"),
                               sheet.getImageName("goomba_idle_8.png"),
                               sheet.getImageName("goomba_idle_9.png"),
                               sheet.getImageName("goomba_idle_10.png"),
                               sheet.getImageName("goomba_idle_11.png"),
                               sheet.getImageName("goomba_idle_12.png"),
                               sheet.getImageName("goomba_idle_13.png"),
                               sheet.getImageName("goomba_idle_14.png"),
                               sheet.getImageName("goomba_idle_15.png"),
                               sheet.getImageName("goomba_idle_16.png"),
                               sheet.getImageName("goomba_idle_17.png"),
                               sheet.getImageName("goomba_idle_18.png"),
                               sheet.getImageName("goomba_idle_19.png"),
                               sheet.getImageName("goomba_idle_20.png"),
                               sheet.getImageName("goomba_idle_21.png"),
                               sheet.getImageName("goomba_idle_22.png"),
                               sheet.getImageName("goomba_idle_23.png"),
                               sheet.getImageName("goomba_idle_24.png"),
                               sheet.getImageName("goomba_idle_25.png"),
                               sheet.getImageName("goomba_idle_26.png"),
                               sheet.getImageName("goomba_idle_27.png"),
                               sheet.getImageName("goomba_idle_28.png"),
                               sheet.getImageName("goomba_idle_29.png"),
                               sheet.getImageName("goomba_idle_30.png"),
                               sheet.getImageName("goomba_idle_31.png"),
                               sheet.getImageName("goomba_idle_32.png"),
                               sheet.getImageName("goomba_idle_33.png"),
                               sheet.getImageName("goomba_idle_34.png"),
                               sheet.getImageName("goomba_idle_35.png"),
                               sheet.getImageName("goomba_idle_36.png"),
                               sheet.getImageName("goomba_idle_37.png"),
                               sheet.getImageName("goomba_idle_38.png"),
                               sheet.getImageName("goomba_idle_39.png"),
                               sheet.getImageName("goomba_idle_40.png"),
                               sheet.getImageName("goomba_idle_41.png"),
                               sheet.getImageName("goomba_idle_42.png"),
                               sheet.getImageName("goomba_idle_43.png"),
                               sheet.getImageName("goomba_idle_44.png"),
                               sheet.getImageName("goomba_idle_45.png"),
                               sheet.getImageName("goomba_idle_46.png"),
                               sheet.getImageName("goomba_idle_47.png"),
                               sheet.getImageName("goomba_idle_48.png"),
                               sheet.getImageName("goomba_idle_49.png"),
                               sheet.getImageName("goomba_idle_50.png"),
                               sheet.getImageName("goomba_idle_51.png"),
                               sheet.getImageName("goomba_idle_52.png"),
                               sheet.getImageName("goomba_idle_53.png"),
                               sheet.getImageName("goomba_idle_54.png"),
                               sheet.getImageName("goomba_idle_55.png"),
                               sheet.getImageName("goomba_idle_56.png"),
                               sheet.getImageName("goomba_idle_57.png"),
                               sheet.getImageName("goomba_idle_58.png"),
                               sheet.getImageName("goomba_idle_59.png"),
                               sheet.getImageName("goomba_idle_60.png"),
                               sheet.getImageName("goomba_idle_61.png"),
                               sheet.getImageName("goomba_idle_62.png"),
                               sheet.getImageName("goomba_idle_63.png"),
                               sheet.getImageName("goomba_idle_64.png"),
                               sheet.getImageName("goomba_idle_65.png"),
                               sheet.getImageName("goomba_idle_66.png"),
                               sheet.getImageName("goomba_idle_67.png"),
                               sheet.getImageName("goomba_idle_68.png"),
                               sheet.getImageName("goomba_idle_69.png"),
                               sheet.getImageName("goomba_idle_70.png"),
                               sheet.getImageName("goomba_idle_71.png"),
                               sheet.getImageName("goomba_idle_72.png"),
                               sheet.getImageName("goomba_idle_73.png"),
                               sheet.getImageName("goomba_idle_74.png"),
                               sheet.getImageName("goomba_idle_75.png"),
                               sheet.getImageName("goomba_idle_76.png"),
                               sheet.getImageName("goomba_idle_77.png"),
                               sheet.getImageName("goomba_idle_78.png"),
                               sheet.getImageName("goomba_idle_79.png"),
                               sheet.getImageName("goomba_idle_80.png"),
                               sheet.getImageName("goomba_idle_81.png"),
                               sheet.getImageName("goomba_idle_82.png"),
                               sheet.getImageName("goomba_idle_83.png"),
                               sheet.getImageName("goomba_idle_84.png"),
                               sheet.getImageName("goomba_idle_85.png"),
                               sheet.getImageName("goomba_idle_86.png"),
                               sheet.getImageName("goomba_idle_87.png"),
                               sheet.getImageName("goomba_idle_88.png"),
                               sheet.getImageName("goomba_idle_89.png"),
                               sheet.getImageName("goomba_idle_90.png"),
                               sheet.getImageName("goomba_idle_91.png"),
                               sheet.getImageName("goomba_idle_92.png"),
                               sheet.getImageName("goomba_idle_93.png"),
                               sheet.getImageName("goomba_idle_94.png"),
                               sheet.getImageName("goomba_idle_95.png"),
                               sheet.getImageName("goomba_idle_96.png"),
                               sheet.getImageName("goomba_idle_97.png"),
                               sheet.getImageName("goomba_idle_98.png"),
                               sheet.getImageName("goomba_idle_99.png"),
                               sheet.getImageName("goomba_idle_100.png"),
                               sheet.getImageName("goomba_idle_101.png"),
                               sheet.getImageName("goomba_idle_102.png"),
                               sheet.getImageName("goomba_idle_103.png"),
                               sheet.getImageName("goomba_idle_104.png"),
                               sheet.getImageName("goomba_idle_105.png"),
                               sheet.getImageName("goomba_idle_106.png"),
                               sheet.getImageName("goomba_idle_107.png"),
                               sheet.getImageName("goomba_idle_108.png"),
                               sheet.getImageName("goomba_idle_109.png"),
                               sheet.getImageName("goomba_idle_110.png"),
                               sheet.getImageName("goomba_idle_111.png"),
                               sheet.getImageName("goomba_idle_112.png")]

        self.hitFrame = sheet.getImageName("goomba_hit.png")

    def update(self):
        self.animate()

        self.enemy.hpMath()

        if self.hit and self.counter <= 30:
            self.counter += 1
        elif self.hit:
            self.counter = 0
            self.hit = False

        if self.enemy.stats["hp"] <= 0:
            if self.enemy in self.game.enemies:
                self.game.battleCoins += self.enemy.stats["coins"]
                self.game.battleXp += self.enemy.stats["exp"]
                self.game.sprites.remove(self.enemy)
                self.game.enemies.remove(self.enemy)

        if self.enemy not in self.game.enemies:
            self.alpha -= 10

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 45:
            if not self.hit:
                self.lastUpdate = now
                if self.currentFrame < len(self.standingFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.standingFrames))
                else:
                    self.currentFrame = 0
                centerx = self.rect.centerx
                bottom = self.rect.bottom
                self.image = self.standingFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom
            else:
                centerx = self.rect.centerx
                bottom = self.rect.bottom
                self.image = self.hitFrame
                self.rect = self.image.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom


class KoopaBrosAttack(pg.sprite.Sprite):
    def __init__(self, game, enemy):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.hit = False
        self.alpha = 255
        self.lastUpdate = 0
        self.counter = 0
        self.enemy = enemy
        self.loadImages()
        self.currentFrame = random.randrange(0, len(self.standingFrames) - 1)
        self.image = self.standingFrames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (random.randrange(width / 2, width - 100), random.randrange(420, height - 50))
        self.barRect = self.rect

    def loadImages(self):
        sheet = spritesheet("sprites/koopaBrosAttack.png", "sprites/koopaBrosAttack.xml")

        self.standingFrames = [sheet.getImageName("idle_1.png"),
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
                               sheet.getImageName("idle_24.png")]

        self.hitFrame = sheet.getImageName("hit.png")

    def update(self):
        self.animate()

        self.enemy.hpMath()

        if self.hit and self.counter <= 30:
            self.counter += 1
        elif self.hit:
            self.counter = 0
            self.hit = False

        if self.enemy.stats["hp"] <= 0:
            if self.enemy in self.game.enemies:
                self.game.battleCoins += self.enemy.stats["coins"]
                self.game.battleXp += self.enemy.stats["exp"]
                self.game.sprites.remove(self.enemy)
                self.game.enemies.remove(self.enemy)

        if self.enemy not in self.game.enemies:
            self.alpha -= 10

    def animate(self):
        now = pg.time.get_ticks()
        if now - self.lastUpdate > 45:
            if not self.hit:
                self.lastUpdate = now
                if self.currentFrame < len(self.standingFrames):
                    self.currentFrame = (self.currentFrame + 1) % (len(self.standingFrames))
                else:
                    self.currentFrame = 0
                centerx = self.rect.centerx
                bottom = self.rect.bottom
                self.image = self.standingFrames[self.currentFrame]
                self.rect = self.image.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom
            else:
                centerx = self.rect.centerx
                bottom = self.rect.bottom
                self.image = self.hitFrame
                self.rect = self.image.get_rect()
                self.rect.centerx = centerx
                self.rect.bottom = bottom