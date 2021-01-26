import pygame 
from pygame.locals import *
import pickle                                                     #for local files
from os import path                                               #to check if level exists

pygame.init()

clock = pygame.time.Clock()
fps = 60                                                           #setting frameset to get better display


screen_width = 801
screen_height = 801

screen = pygame.display.set_mode((screen_width,screen_height))    #setting screen height and width
pygame.display.set_caption("Super Jumpman Game")                          #game caption

#define font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)

#define game variables
tile_size=40
game_over = 0
main_menu = True                                                  #for main menu
level = 1                                                        #initial level 0
max_levels = 7                                                    #max levels
score = 0

#define colours
white = (255, 255, 255)
blue = (0, 0, 255)

#loading images
bg_img=pygame.image.load('Images/bg.gif')
#restart images
restart_img = pygame.image.load('Images/restart_btn.png')
#start and exit images
start_img = pygame.image.load('Images/start_btn.png')
exit_img = pygame.image.load('Images/exit_btn.png')	

#to draw grids on the screen so that i can place objects properly
#def draw_grid():
    #for line in range(0,20):

        #line(surface, color, start_pos, end_pos, width)
        #pygame.draw.line(screen, (225, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))    #starting and ending pos
        #pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


#function to reset level
def reset_level(level):
	player.reset(100, screen_height - 130)
	enemy_group.empty()
	platform_group.empty()
	coin_group.empty()
	lava_group.empty()
	exit_group.empty()

	#load in level data and create world
	if path.exists(f'level{level}_data'):
		pickle_in = open(f'level{level}_data', 'rb')
		world_data = pickle.load(pickle_in)
	world = World(world_data)
	#create dummy coin for showing the score
	score_coin = Coin(tile_size // 2, tile_size // 2)
	coin_group.add(score_coin)
	return world		

class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		#draw button
		screen.blit(self.image, self.rect)

		return action

class Player():                                                                 #declaring class player
	def __init__(self,x,y):                                                    #constructor
		self.reset(x,y)

	def update(self, game_over):
		dx = 0                                                                 #for change in x and y positions
		dy = 0
		walk_cooldown = 5                                                      #speed of walking animation
		col_thresh = 20

		if game_over == 0:

			#to get the keypresses
			key = pygame.key.get_pressed()                                         #when key gets pressed
			if key[pygame.K_SPACE] and self.jumped==False:
				self.vel_y = - 20
				self.jumped = True                                                 #now he jumps
			if key[pygame.K_SPACE] == False:
				self.jumped = False
			if key[pygame.K_LEFT]:
				dx-=2                                                             #go left by 2 pixels
				self.counter += 1                                                 #increment counter for walking
				self.direction = -1                                               # -1 for left direction
			if key[pygame.K_RIGHT]:
				dx+=2                                                             #go right by 2 pixels
				self.counter +=1
				self.direction = 1                                                # 1 for right direction
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:      #if not right nor left:player is stationary
				self.counter = 0                                                  #reset animation from first
				self.index = 0
				if self.direction == 1:                                           #right direction
					self.image = self.images_right[self.index]
				if self.direction == -1:                                           #left direction
					self.image = self.images_left[self.index]			

			#to handle animation
			if self.counter > walk_cooldown:                                      #when self counter is greater
				self.counter = 0	
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:                                           #right direction
					self.image = self.images_right[self.index]
				if self.direction == -1:                                           #left direction
					self.image = self.images_left[self.index]



			#add gravity
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			#check for collision
			self.in_air = True
			for tile in world.tile_list:
				#check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#check if above the ground i.e. falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False

			#check for collision with enemies
			if pygame.sprite.spritecollide(self, enemy_group, False):
				game_over = -1

			#check for collision with lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1

			#check for collision with exit
			if pygame.sprite.spritecollide(self, exit_group, False):
				game_over = 1

			#check for collision with platforms
			for platform in platform_group:
				#collision in the x direction
				if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#collision in the y direction
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below platform
					if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
						self.vel_y = 0
						dy = platform.rect.bottom - self.rect.top
					#check if above platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						dy = 0
					#move sideways with the platform
					if platform.move_x != 0:
						self.rect.x += platform.move_direction						

			# updating player coordinates
			self.rect.x += dx
			self.rect.y += dy

		elif game_over == -1:
			self.image = self.dead_image
			draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2)
			if self.rect.y > 200:
				self.rect.y -= 5

			#if self.rect.bottom >screen_height :
				#self.rect.bottom = screen_height                                 #so that player does not fall down
				#dy=0

		#draw player on screen
		screen.blit(self.image, self.rect)                                  #to display player
		#pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)             #to draw transparent rect around player, colour: white and pixels: 2
		return game_over

	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'Images/guy{num}.png')
			img_right = pygame.transform.scale(img_right, (40, 80))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load('Images/ghost.png')
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True	

class World():
	def __init__(self,data):
		self.tile_list=[]

		#load images
		dirt_img=pygame.image.load("Images/dirt.png")
		grass_img=pygame.image.load("Images/grass.png")

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile==1:
					img=pygame.transform.scale(dirt_img, (tile_size, tile_size))         #for dirt
					img_rect=img.get_rect()
					img_rect.x = col_count * tile_size                                   #to get x and y coordinates
					img_rect.y = row_count * tile_size
					tile = (img,img_rect)
					self.tile_list.append(tile)

				if tile==2:                                                              #tile=2 for grass
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))	
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size                                   #to get x and y coordinates
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 3:
					enemy = Enemy(col_count * tile_size, row_count * tile_size + 9)     #call enemy class
					enemy_group.add(enemy)                                              #add enemy
				if tile == 4:
					platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
					platform_group.add(platform)
				if tile == 5:
					platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
					platform_group.add(platform)	
				if tile == 6:                                                           #for lava
					lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					lava_group.add(lava)
				if tile == 7:
					coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					coin_group.add(coin)	
				if tile == 8:                                                          #for exit window
					exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
					exit_group.add(exit)		
				col_count+=1
			row_count+=1

	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])
			pygame.draw.rect(screen, (150, 81, 28), tile[1], 2)                 #to draw rect around tiles
			#pygame.draw.rect(screen, (150, 81, 28), tile[1], 2)               #to draw rect around tiles.ie collisions

class Enemy(pygame.sprite.Sprite):                                              #has inbuilt draw and update methods
	def __init__(self, x, y):                                                   #constructor
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('Images/enemy.png')                      #loading enemy
		self.rect = self.image.get_rect()                                       #to draw rect around enemy
		self.rect.x = x
		self.rect.y = y	
		self.move_direction = 1                                                 #moving dir of enemies
		self.move_counter = 0

	def update(self):
		self.rect.x += self.move_direction                                     #to move in x-direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1

class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('Images/platform.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0
		self.move_direction = 1
		self.move_x = move_x
		self.move_y = move_y


	def update(self):
		self.rect.x += self.move_direction * self.move_x
		self.rect.y += self.move_direction * self.move_y
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1

class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('Images/lava.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y	

class Coin(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('Images/coin.png')
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)		

class Exit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('Images/exit.png')
		self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y												

'''world_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1], 
[1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1], 
[1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1], 
[1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1], 
[1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]
'''

player = Player(100, screen_height - 300)
enemy_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#create dummy coin for showing the score
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

if path.exists(f'level{level}_data'):
	pickle_in = open(f'level{level}_data', 'rb')                    #load level from binary file
	world_data = pickle.load(pickle_in)

world = World(world_data)

#create buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

run=True                                                          #the window will be displayed until it becomes false
while run:

	clock.tick(fps)                                              #for frameset
	screen.blit(bg_img, (0,0))
	

	if main_menu == True:
		if exit_button.draw():
			run = False
		if start_button.draw():
			main_menu = False
	else:
		world.draw()

		if game_over == 0:
			enemy_group.update()
			platform_group.update()
			#update score
			#check if a coin has been collected
			if pygame.sprite.spritecollide(player, coin_group, True):
				score += 1
			draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

		enemy_group.draw(screen)
		platform_group.draw(screen)
		lava_group.draw(screen)
		coin_group.draw(screen)
		exit_group.draw(screen)
		#draw_grid()
		game_over = player.update(game_over)

		#if player has died
		if game_over == -1:
			if restart_button.draw():
				world_data = []
				world = reset_level(level)
				game_over = 0
				score = 0

		#if player has won
		if game_over == 1:
			#reset game and go to next level
			level += 1
			if level <= max_levels:
				#reset level
				world_data = []
				world = reset_level(level)
				game_over = 0
			else:
				draw_text('YOU WIN!', font, blue, (screen_width // 2) - 140, screen_height // 2)
				if restart_button.draw():
					level = 1
					#reset level
					world_data = []
					world = reset_level(level)
					game_over = 0
					score = 0									

	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()		
	                                   

pygame.quit()

