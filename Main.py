import pygame as pg
from settings import *
from sprites import *

pg.mixer.pre_init(44100, -16, 2, 2048)
pg.init()

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((width,height))
        self.clock = pg.time.Clock()
        self.song_playing = ""
        self.running = True

    def playSong(self, introLength, loopLength, song):
        if self.song_playing != "playing":
            pg.mixer.music.load("music/" + song + ".ogg")
            pg.mixer.music.play()
            self.song_playing = "playing"

        self.totalLength = introLength + loopLength
        self.soundPos = pg.mixer.music.get_pos() / 1000

        if self.soundPos >= self.totalLength and self.firstLoop:
            pg.mixer.music.play(0, self.soundPos - loopLength)
            self.firstLoop = False
        elif self.soundPos >= loopLength and not self.firstLoop:
            pg.mixer.music.play(0, self.soundPos + introLength - loopLength)

    def new(self):
        self.sprites = pg.sprite.Group()
        self.firstLoop = True
        self.player = marioOverworld(self, width / 2, height / 2)
        self.sprites.add(self.player)
        self.run()

    def run(self):
        self.playing = True

        while self.playing:
            self.playSong(5.954, 52.489, "Teehee Valley")
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

    def update(self):
        self.sprites.update()

    def draw(self):
        self.screen.fill(black)
        self.sprites.draw(self.screen)

        pg.display.flip()


game = Game()

while game.running:
    game.new()

pg.quit()