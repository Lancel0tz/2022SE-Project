import pygame 
from settings import *
from support import import_folder
from entity import Entity

class Player(Entity):
	def __init__(self,pos,groups,obstacle_sprites,create_attack,destroy_attack,create_collect,destroy_collect):
		super().__init__(groups)
		self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0,-26)

		# graphics setup
		self.import_player_assets() # animation surface import and classification
		self.status = 'down'

		# movement
		self.attacking = False
		self.attack_cooldown = 400
		self.attack_time = None
		self.obstacle_sprites = obstacle_sprites

		# weapon
		self.create_attack = create_attack
		self.destroy_attack = destroy_attack
		self.weapon_index = 0
		self.weapon = list(weapon_data.keys())[self.weapon_index] # needn't wrap around
		self.can_switch_weapon = True
		self.weapon_switch_time = None
		self.switch_duration_cooldown = 200

		# collection
		self.create_collect = create_collect
		self.destroy_collect = destroy_collect
		self.collect_index = 0
		self.collect = list(collect_data.keys())[self.collect_index]
		self.can_switch_collect = True
		self.collect_switch_time = None

		# stats
		self.stats = {'health': 100,'energy':60,'attack': 10,'speed': 5}
		self.health = self.stats['health'] * 0.5
		self.energy = self.stats['energy'] * 0.8
		self.exp = 123
		self.speed = self.stats['speed']
		self.death = False # whether the player dead

		# damage timer
		self.vulnerable = True
		self.hurt_time = None
		self.invulnerability_duration = 500

		# import a sound
		self.weapon_attack_sound = pygame.mixer.Sound('../audio/sword.wav')
		self.collect_sound = pygame.mixer.Sound('../audio/collect.wav')
		self.death_sound = pygame.mixer.Sound('../audio/death.wav')
		self.weapon_attack_sound.set_volume(0.4)
		self.collect_sound.set_volume(0.4)
		self.death_sound.set_volume(0.4)




	def import_player_assets(self):
		character_path = '../graphics/player/'
		self.animations = {'up': [],'down': [],'left': [],'right': [],
			'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
			'right_attack':[],'left_attack':[],'up_attack':[],'down_attack':[]}

		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = import_folder(full_path)

	def input(self):
		if not self.attacking:
			keys = pygame.key.get_pressed()

			# movement input
			if keys[pygame.K_w]:
				self.direction.y = -1
				self.status = 'up'
			elif keys[pygame.K_s]:
				self.direction.y = 1
				self.status = 'down'
			else:
				self.direction.y = 0

			if keys[pygame.K_d]:
				self.direction.x = 1
				self.status = 'right'
			elif keys[pygame.K_a]:
				self.direction.x = -1
				self.status = 'left'
			else:
				self.direction.x = 0

			# attack input 
			if pygame.mouse.get_pressed()[0]:
				self.attacking = True
				self.attack_time = pygame.time.get_ticks()
				self.create_attack()
				self.weapon_attack_sound.play()

			# collect input
			if pygame.mouse.get_pressed()[2]:
				self.attacking = True
				self.attack_time = pygame.time.get_ticks()
				content = list(collect_data.keys())[self.collect_index % len(list(collect_data))]
				self.create_collect(content)
				self.collect_sound.play()

			"""Improve, whether switch attack could be mechanism or not"""
			# switch weapons
			if keys[pygame.K_q] and self.can_switch_weapon:
				self.can_switch_weapon = False
				self.weapon_switch_time = pygame.time.get_ticks()
				self.weapon_index += 1
				self.weapon = list(weapon_data.keys())[self.weapon_index % len(list(weapon_data))]

			# switch collection
			if keys[pygame.K_e] and self.can_switch_collect:
				self.can_switch_collect = False
				self.collect_switch_time = pygame.time.get_ticks()
				self.collect_index += 1
				self.collect = list(collect_data.keys())[self.collect_index % len(list(collect_data))]


	def get_status(self):
		# idle status
		if self.direction.x == 0 and self.direction.y == 0:
			if not 'idle' in self.status and not 'attack' in self.status:
				self.status = self.status + '_idle'

		if self.attacking:
			self.direction.x = 0
			self.direction.y = 0
			if not 'attack' in self.status:
				if 'idle' in self.status:
					self.status = self.status.replace('_idle','_attack')
				else:
					self.status = self.status + '_attack'
		else:
			if 'attack' in self.status:
				self.status = self.status.replace('_attack','')

	def cooldowns(self):
		current_time = pygame.time.get_ticks()

		if self.attacking:
			if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
				self.attacking = False
				self.destroy_attack()

		if not self.can_switch_weapon:
			if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
				self.can_switch_weapon = True

		if not self.can_switch_collect:
			if current_time - self.collect_switch_time >= self.switch_duration_cooldown:
				self.can_switch_collect = True

		if not self.vulnerable:
			if current_time - self.hurt_time >= self.invulnerability_duration:
				self.vulnerable = True

	def animate(self):
		animation = self.animations[self.status]

		# loop over the frame index 
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		# set the image
		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center = self.hitbox.center)

		# flicker
		if not self.vulnerable:
			alpha = self.wave_value()
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)

	def get_full_weapon_damage(self):
		base_damage = self.stats['attack']
		weapon_damage = weapon_data[self.weapon]['damage']
		return base_damage + weapon_damage

	def check_death(self):
		if self.health <= 0:
			#self.kill()
			self.death_sound.play()
			self.death = True

	def update(self):
		self.check_death()
		self.input()
		self.cooldowns()
		self.get_status()
		self.animate()
		self.move(self.speed)