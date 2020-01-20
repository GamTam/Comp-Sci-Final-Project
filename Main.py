import pygame as pg
from settings import *
from sprites import *

pg.mixer.pre_init(44100, -16, 2, 2048)
pg.init()

class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((width,height))
        self.clock = pg.time.Clock()
        self.running = True

    def new(self):
        self.sprites = pg.sprite.Group()
        self.player = marioOverworld(self, width / 2, height / 2)
        self.sprites.add(self.player)
        self.run()

    def run(self):
        self.playing = True

        while self.playing:
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