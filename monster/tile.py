import pygame 
from settings import *

class Tile(pygame.sprite.Sprite):
	def __init__(self,pos,groups,sprite_type,surface = pygame.Surface((TILESIZE,TILESIZE)),word_index=None):
		super().__init__(groups)
		self.word_index = word_index
		self.sprite_type = sprite_type
		self.image = surface
		if sprite_type == 'object':
			self.rect = self.image.get_rect(topleft = (pos[0],pos[1] - TILESIZE))
		if sprite_type == 'npc':
			self.rect = self.image.get_rect(topleft = (pos[0],pos[1] - TILESIZE))
		else:
			self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0,-10)


class Npc(Tile):
	def __init__(self, pos, groups, question, answer, player,
				 surface=pygame.Surface((TILESIZE, TILESIZE)), ):

		super().__init__(pos, groups, 'npc', surface)
		self.display_surface = pygame.display.get_surface()
		self.center = self.display_surface.get_rect().center
		self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
		self.player = player
		self.listener = []

		# question
		self.show_question = [False]
		self.question = self.font.render(question, False, 'black')
		self.question_rect = self.question.get_rect(center=(300, 300))

		# check for answer
		self.tocheck = [False]
		self.right = False
		self.answer = answer

		self.strategy = self.tocheck

	def setlistener(self, *args):
		for l in args:
			self.listener.append(l)

	def listen(self):
		self.strategy[0] = not self.strategy[0]

	def notice(self):
		for listens in self.listener:
			listens.listen()

	def setup(self):
		self.answer_sprites = pygame.sprite.Group()
		self.text = InputBox((self.center[0] - 100, self.center[1] + 50), self.font, self.answer_sprites)
		self.button = Button((720, 550), "D:\\资料\\program\\Software_pygame\\ball.gif", self.answer_sprites)
		self.button.setlistener(self)  # 开始查看答案是否正确

		self.setlistener(self.text, self.button)  # 关闭显示
		self.notice()

		self.again = Button((450, 450), "D:\\资料\\program\\Software_pygame\\again.jpeg", self.answer_sprites)
		self.again.listen()
		self.again.setlistener(self, self.button)
		self.next = Button((450, 400), 'D:\\资料\\program\\Software_pygame\\next.jpeg', self.answer_sprites)
		self.next.setlistener(self.text, self)
		self.next.listen()

	def update(self):
		try:
			event = pygame.event.get()
			self.button.get_event(event)
			self.text.get_text(event)
			self.next.get_event(event)
			self.again.get_event(event)
			self.draw()
			self.player.answering = self.show_question[0]
			if self.right and not self.next.active:
				for sprite in self.answer_sprites.sprites():
					sprite.kill()
		except:
			pass

	def draw(self):
		if self.show_question[0]:
			self.display_surface.blit(self.question, self.question_rect)
		if self.tocheck[0]:
			self.check()
			if self.right:
				a = self.font.render("Yeah! Here we go!", False, (255, 0, 0), (254, 253, 252))
				self.display_surface.blit(a, (500, 300))
				self.next.active = True
			else:
				a = self.font.render("No, we will not go there.", False, (255, 0, 0), (254, 253, 252))
				self.display_surface.blit(a, (500, 300))
				self.again.active = True
		for sprite in self.answer_sprites.sprites():
			sprite.draw()

	def check(self):
		textin = self.text.output()
		for ans in self.answer:
			if textin in ans:
				self.right = True
				self.strategy = self.show_question
				break
			if not self.right:
				self.strategy = self.tocheck