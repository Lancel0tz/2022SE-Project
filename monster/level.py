import pygame 
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice
from weapon import Weapon
from collect import Collect
from ui import UI
from enemy import Enemy

class Level:
	def __init__(self, world):
		# status of world
		self.world = world

		# get the display surface
		self.display_surface = pygame.display.get_surface()

		# sprite group setup
		self.visible_sprites = YSortCameraGroup(self.world)
		self.obstacle_sprites = pygame.sprite.Group()

		# attack sprites
		self.current_attack = None
		self.attack_sprites = pygame.sprite.Group()
		self.attackable_sprites = pygame.sprite.Group()

		# collect sprites
		self.current_collect = None
		self.collect_sprites = pygame.sprite.Group()
		self.collectable_sprites = pygame.sprite.Group()

		# sprite setup
		if self.world == "pharmacy":
			self.create_pharmacy()
			main_sound = pygame.mixer.Sound('../audio/pharmacy.mpeg')
			main_sound.set_volume(0.3)
			main_sound.play()

		elif self.world == "main":
			self.create_main()
			main_sound = pygame.mixer.Sound('../audio/main.mpeg')
			main_sound.set_volume(0.3)
			main_sound.play()

		# user interface 
		self.ui = UI()

		# npc position
		self.npc_x = -1
		self.npc_y = -1

	def create_pharmacy(self):
		layouts = {
			'boundary': import_csv_layout('../map/pharmacy_ph_bround.csv'),
			'npc': import_csv_layout('../map/pharmacy_ph_NPC.csv'),
			'words': import_csv_layout('../map/pharmacy_ph_words.csv'),
			'entities': import_csv_layout('../map/pharmacy_ph_entities.csv')
		}
		graphics = {
			'npc': import_folder('../graphics/npc'),
			"words": import_folder('../graphics/words')
		}

		for style,layout in layouts.items():
			for row_index,row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * TILESIZE
						y = row_index * TILESIZE
						if style == 'boundary':
							Tile((x,y),[self.obstacle_sprites],'invisible')
						if style == 'npc':
							surf = graphics['npc'][int(col)]
							self.npc_x = x
							self.npc_y = y
							Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'npc',surf)
						if style == 'words':
							surf = graphics['words'][int(col)]
							word_index = int(col)
							Tile((x,y),
								 [self.visible_sprites,self.obstacle_sprites,self.attackable_sprites,self.collectable_sprites],
								 'words',
								 surf,word_index)
						if style == 'entities':
							if col == '394':
								self.player = Player((x,y),
													 [self.visible_sprites], self.obstacle_sprites,
													 self.create_attack, self.destroy_attack,
													 self.create_collect, self.destroy_collect)  # latter 3 are methods
							else:
								if col == '390': monster_name = 'bamboo'
								elif col == '391': monster_name = 'spirit'
								elif col == '392': monster_name = 'raccoon'
								else: monster_name = 'squid'
								Enemy(monster_name,
									  (x,y),
									  [self.visible_sprites,self.attackable_sprites],
									  self.obstacle_sprites,
									  self.damage_player)

	def create_main(self):
		layouts = {
			'boundary': import_csv_layout('../map/mainworld_stop.csv'),
			'object': import_csv_layout('../map/mainworld_objects.csv'),
			'entities': import_csv_layout('../map/mainworld_entities.csv')
		}
		graphics = {
			'objects': import_folder('../graphics/objects')
		}

		for style,layout in layouts.items():
			for row_index,row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * TILESIZE
						y = row_index * TILESIZE
						if style == 'boundary':
							Tile((x,y),[self.obstacle_sprites],'invisible')
						if style == 'object':
							surf = graphics['objects'][int(col)]
							Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'object',surf)

						if style == 'entities':
							if col == '394':
								self.player = Player((x,y),
													 [self.visible_sprites], self.obstacle_sprites,
													 self.create_attack, self.destroy_attack,
													 self.create_collect, self.destroy_collect)  # latter 3 are methods
							else:
								if col == '390': monster_name = 'bamboo'
								elif col == '391': monster_name = 'spirit'
								elif col == '392': monster_name = 'raccoon'
								else: monster_name = 'squid'
								Enemy(monster_name,
									  (x,y),
									  [self.visible_sprites,self.attackable_sprites],
									  self.obstacle_sprites,
									  self.damage_player)


	def create_attack(self):
		self.current_attack = Weapon(self.player,[self.visible_sprites,self.attack_sprites])

	def create_collect(self,content):
		self.current_collect = Collect(self.player,[self.visible_sprites,self.collect_sprites])


	def destroy_attack(self):
		if self.current_attack:
			self.current_attack.kill()
		self.current_attack = None

	def destroy_collect(self):
		if self.current_collect:
			self.current_collect.kill()
		self.current_collect = None

	def player_attack_logic(self):
		if self.attack_sprites:
			for attack_sprite in self.attack_sprites:
				collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
				if collision_sprites:
					for target_sprite in collision_sprites:
						if target_sprite.sprite_type == 'enemy':
							target_sprite.get_damage(self.player,attack_sprite.sprite_type)

	def player_collect_logic(self):
		if self.collect_sprites:
			for collect_sprite in self.collect_sprites:
				collision_sprites = pygame.sprite.spritecollide(collect_sprite,self.collectable_sprites,False)
				if collision_sprites:
					for target_sprite in collision_sprites:
						if target_sprite.sprite_type == 'words':
							collect_data[f'word{target_sprite.word_index}'] = {'exp':100,'graphic':f'../graphics//particles/words/{target_sprite.word_index}.png'}
							#self.player.collect_index = 0
							path = collect_data[f'word{target_sprite.word_index}']['graphic']
							collect = pygame.image.load(path).convert_alpha()
							self.ui.collect_graphics.append(collect)
							target_sprite.kill()

	def damage_player(self,amount,attack_type):
		if self.player.vulnerable:
			self.player.health -= amount
			self.player.vulnerable = False
			self.player.hurt_time = pygame.time.get_ticks()
			# spawn particles

	# Initial run
	def run(self):
		# update and draw the game
		self.visible_sprites.custom_draw(self.player)
		self.visible_sprites.update() # include enemy
		self.visible_sprites.enemy_update(self.player)
		self.player_attack_logic()
		self.player_collect_logic()
		self.ui.display(self.player)


class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self,world):
		# general setup 
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.half_width = self.display_surface.get_size()[0] // 2
		self.half_height = self.display_surface.get_size()[1] // 2
		self.offset = pygame.math.Vector2()

		# creating the floor
		if world == "pharmacy":
			self.floor_surf = pygame.image.load('../graphics/tilemap/pharmacy.png').convert()
		if world == "main":
			self.floor_surf = pygame.image.load('../graphics/tilemap/MainMap.png').convert()
		self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

	def custom_draw(self,player):

		# getting the offset 
		self.offset.x = player.rect.centerx - self.half_width
		self.offset.y = player.rect.centery - self.half_height

		# drawing the floor
		floor_offset_pos = self.floor_rect.topleft - self.offset
		self.display_surface.blit(self.floor_surf,floor_offset_pos)

		# for sprite in self.sprites():
		for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image,offset_pos)

	def enemy_update(self,player):
		enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
		for enemy in enemy_sprites:
			enemy.enemy_update(player)

