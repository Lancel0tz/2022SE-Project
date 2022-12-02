import pygame, sys
from settings import *
from level import Level

class Game:
	def __init__(self):
		# general setup
		pygame.init()
		self.screen = pygame.display.set_mode((WIDTH,HEIGTH))
		pygame.display.set_caption('ELG')
		self.clock = pygame.time.Clock()
		self.level = Level('main')
		self.world_choice = ['main','pharmacy']
		self.count = 0
	
	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif pygame.key.get_pressed()[pygame.K_f]:
					pygame.mixer.stop() # stop the previous music
					self.count += 1
					self.level = Level(self.world_choice[self.count%len(self.world_choice)])


			if self.level.world == 'main':
				self.screen.fill(WATER_COLOR)
			elif self.level.world == 'pharmacy':
				self.screen.fill(FLOOR_COLOR)
			self.level.run()
			pygame.display.update()
			self.clock.tick(FPS)

if __name__ == '__main__':
	game = Game()
	game.run()