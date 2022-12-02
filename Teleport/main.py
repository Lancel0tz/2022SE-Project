import pygame, sys
from settings import *
from level import Level

class Game:
	def __init__(self):
		# general setup
		pygame.init()
		self.screen = pygame.display.set_mode((WIDTH,HEIGTH))
		pygame.display.set_caption('Zelda')
		self.clock = pygame.time.Clock()
		self.level = Level("main")
	
	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif pygame.key.get_pressed()[pygame.K_f]:
					self.level = Level("pharmacy")

			self.screen.fill('black')
			self.level.run()
			pygame.display.update()
			self.clock.tick(FPS)

if __name__ == '__main__':
	game = Game()
	game.run()