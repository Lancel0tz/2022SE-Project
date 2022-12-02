import pygame 
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice
from weapon import Weapon
from ui import UI

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

		# sprite setup
		if self.world == "pharmacy":
			self.create_pharmacy()
		elif self.world == "main":
			self.create_main()

		# user interface 
		self.ui = UI()

		# npc position
		self.npc_x = -1
		self.npc_y = -1

	def create_pharmacy(self):
		layouts = {
			'boundary': import_csv_layout('../map/pharmacy_ph_bround.csv'),
			#'grass': import_csv_layout('../map/map_Grass.csv'),
			#'object': import_csv_layout('../map/map_Objects.csv'),
			"npc": import_csv_layout("../map/pharmacy_ph_NPC.csv")
		}
		graphics = {
			#'grass': import_folder('../graphics/Grass'),
			#'objects': import_folder('../graphics/objects')
			'npc': import_folder('../graphics/npc')
		}

		for style,layout in layouts.items():
			for row_index,row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * TILESIZE
						y = row_index * TILESIZE
						if style == 'boundary':
							Tile((x,y),[self.obstacle_sprites],'invisible')
						if style == 'grass':
							random_grass_image = choice(graphics['grass'])
							Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'grass',random_grass_image)

						if style == 'object':
							surf = graphics['objects'][int(col)]
							Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'object',surf)
						if style == 'npc':
							surf = graphics['npc'][int(col)]
							self.npc_x = x
							self.npc_y = y
							Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'npc',surf)

		self.player = Player((1000,600),[self.visible_sprites],self.obstacle_sprites,self.create_attack,self.destroy_attack)

	def create_main(self):
		layouts = {
			'boundary': import_csv_layout('../map/map_FloorBlocks.csv'),
			'grass': import_csv_layout('../map/map_Grass.csv'),
			'object': import_csv_layout('../map/map_Objects.csv'),
		}
		graphics = {
			'grass': import_folder('../graphics/Grass'),
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
						if style == 'grass':
							random_grass_image = choice(graphics['grass'])
							Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'grass',random_grass_image)
						if style == 'object':
							surf = graphics['objects'][int(col)]
							Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'object',surf)

		self.player = Player((2000,1430),[self.visible_sprites],self.obstacle_sprites,self.create_attack,self.destroy_attack)

	def create_attack(self):
		
		self.current_attack = Weapon(self.player,[self.visible_sprites])

	def destroy_attack(self):
		if self.current_attack:
			self.current_attack.kill()
		self.current_attack = None

	def run(self):
		# update and draw the game
		self.visible_sprites.custom_draw(self.player)
		self.visible_sprites.update()
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
			self.floor_surf = pygame.image.load('../graphics/tilemap/ground.png').convert()
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
