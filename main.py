
import json
import pygame
pygame.init()

width = 800
height = 800

display = pygame.display.set_mode((width,height))
pygame.display.set_caption("Platformer")
fon_img = pygame.image.load("image/bg4.png")
fon_rect =fon_img.get_rect()
font=pygame.font.SysFont("Arial",24)
with open("lvl/lvl3.json","r") as file :
    world_data = json.load(file)
tile_size = 40
score= 0
level = 1
max_level =4
score_surf=font.render(f"score: {score}",True,"white")


sound_jump=pygame.mixer.Sound("sounds/jump.wav")
sound_game_over=pygame.mixer.Sound("sounds/game_over.wav")
sound_coin=pygame.mixer.Sound("sounds/coin.wav")

def reset_level():
    player.rect.x =100
    player.rect.y = height -130
    lava_group.empty()
    exit_group.empty()
    coin_group.empty()
    with open(f"lvl/lvl{level}.json", "r") as file:
        world_data = json.load(file)
    world = World (world_data)
    return  world


class Coin(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("image/coin.png")
        size = tile_size // 2
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect(center=(x,y))




class Button:
    def __init__(self,x,y,img):
        self.image=pygame.image.load("image/"+img)
        self.img_rect=self.image.get_rect(center=(x,y))
    def draw(self):
        display.blit(self.image,self.img_rect)

start_btn=Button(width/2-150,height/2,"start_btn.png")

exit_btn=Button(width/2+150,height/2,"exit_btn.png")

restart_btn=Button(width/2,height/2,"restart_btn.png")


status="game"
lives =5

class World:
    def __init__(self,data):
        dirt_img = pygame.image.load("image/tile4.png")
        grass_img = pygame.image.load("image/tile1.png")
        self.tile_list = []
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1 or tile == 2:
                    images = {1:dirt_img,2:grass_img}
                    img = pygame.transform.scale(images[tile],
                                                 (tile_size,tile_size))
                    img_rect = img.get_rect()
                    img_rect.x= col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img,img_rect)
                    self.tile_list.append(tile)
                elif tile==3:
                    lava=Lava(col_count*tile_size,
                              row_count * tile_size +(tile_size//2))
                    lava_group.add(lava)
                elif tile ==5:
                    exit=Exit(col_count*tile_size,
                              row_count * tile_size +(tile_size//2))
                    exit_group.add(exit)
                elif tile == 6:
                    coin=Coin(col_count*tile_size,
                              row_count * tile_size +(tile_size//2))
                    coin_group.add(coin)

                col_count += 1
            row_count +=1


    def draw(self):
        for tile_img,tile_rect in self.tile_list:
            display.blit(tile_img,tile_rect)

class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        img = pygame.image.load("image/lava.png")
        self.image=pygame.transform.scale(img,(tile_size,tile_size//2))
        self.rect=self.image.get_rect(left=x,top=y)
class Exit(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load("image/door1.png")
        self.image=pygame.transform.scale (self.image,(tile_size,tile_size*1.6))
        self.rect =self.image.get_rect(left=x,top=y)


class Player:

    def __init__(self):
        self.images_right = []
        self.images_left = []
        self.index=0
        self.counter =0
        self.direction = 0
        for num in range(1,5):
            img_right = pygame.image.load(f"image/player{num}.png")
            img_right =pygame.transform.scale(img_right,(35,70))
            img_left = pygame.transform.flip(img_right,True,False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.ghost =pygame.image.load("image/ghost.png")
        self.ghost=pygame.transform.scale(self.ghost,(35,70))

        self.player_img =self.images_right[0]
        self.rect=self.player_img.get_rect()
        self.rect.x = 100
        self.rect.y = height - 130
        self.gravity = 0
        self.jumped = False
        self.width = self.rect.width
        self.height =self.rect.height


    def update(self):
        global status,lives,score,score_surf
        walk_speed = 10


        x=0
        y=0
        if status == "game":
            key = pygame.key.get_pressed()
            if key [pygame.K_SPACE] and not self.jumped :
                sound_jump.play()
                self.gravity =-15
                self.jumped = True

            if key [pygame.K_a]:
                x-=5
                self.direction = -1
                self.counter += 1


            if key[pygame.K_d]:
                x+=5
                self.direction = 1
                self.counter += 1
            if self.counter >= walk_speed:
                self.counter =0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction ==1:
                    self.player_img = self.images_right[self.index]
                else:
                    self.player_img = self.images_left[self.index]


            self.gravity += 1
            if self.gravity > 10:
                self.gravity =10
            y += self.gravity

            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + x, self.rect.y,
                                       self.width, self.height):
                    x=0
                if tile[1].colliderect(self.rect.x, self.rect.y + y,
                                       self.width, self.height):
                    if self.gravity >=0:
                        y=tile[1].top-self.rect.bottom
                        self.gravity=0
                        self.jumped=False
                    if self.gravity<0:
                        y=tile[1].bottom-self.rect.top
                        self.gravity=0
            if pygame.sprite.spritecollide(self, lava_group, False):
                sound_game_over.play()
                lives -=1
                status = "lose"
                self.player_img=self.ghost
            if pygame.sprite.spritecollide(self, exit_group, False):
                status ="next level"
            if pygame.sprite.spritecollide(self,coin_group,True):
                sound_coin.play()
                score +=1
                score_surf = font.render(f"score: {score}", True, "white")




            self.rect.x += x
            self.rect.y += y
            if self.rect.bottom > height :
                self.rect.bottom = height

        if status == "lose":
            self.rect.y -= 5


        display.blit(self.player_img, self.rect)







coin_group=pygame.sprite.Group()
lava_group=pygame.sprite.Group()
exit_group=pygame.sprite.Group()

player = Player()

world = reset_level()

menu=True
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if menu:
                    if exit_btn.img_rect.collidepoint(event.pos):

                        run = False
                    elif start_btn.img_rect.collidepoint(event.pos):
                        menu = False
                        level =1
                        lives = 5
                        score =0
                        world=reset_level()


                if status == "lose":
                    if restart_btn.img_rect.collidepoint(event.pos):
                        status= "game"
                        player=Player()
                        world=reset_level()


    display.blit(fon_img, fon_rect)
    if menu:
        start_btn.draw()
        exit_btn.draw()
    else:

        world.draw()
        exit_group.draw(display)
        exit_group.update()
        coin_group.draw(display)
        coin_group.update()
        lava_group.draw(display)
        lava_group.update()
        player.update()
        display.blit(score_surf,(20,20))
        if status == "lose":
            if lives == 0:
                menu = True

            else:
                restart_btn.draw()
        elif status == "next level":
            level += 1
            if level > max_level:
                menu =True
                print("win")

            else:
                status ="game"
                world=reset_level()
    pygame.display.update()





pygame.quit()





