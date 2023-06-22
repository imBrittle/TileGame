import pygame, sys, random, math

pygame.init()

font = pygame.font.Font(None, 20)

def DrawText(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def Collide(obj, group):
    if pygame.sprite.spritecollideany(obj, group):
        DrawText('Collide', font, (255, 255, 255), screen, obj.rect.x, obj.rect.y - 20)
        return pygame.sprite.spritecollideany(obj, group)
    else:
        return None

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        image = pygame.image.load('assets/img/player.png')
        self.image = pygame.transform.scale(image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.pos = pygame.Vector2(pos)
        self.posBackup = pygame.Vector2(self.pos.x, self.pos.y)
        self.direction = pygame.Vector2((0, 0))
        self.vel = pygame.Vector2((0, 0))
        self.baseSpeed = 3
        self.speed = self.baseSpeed
        self.maxEnergy = 100
        self.energy = self.maxEnergy
        self.exhaustTimer = 0
        self.sprint = False
        self.collision = None
        self.framesSinceLastSprint = 0
        self.sprintThreshold = 120

    def Input(self):
        # Inputs
        keys = pygame.key.get_pressed()

        self.direction.xy = (0, 0)
        normalise = False

        if keys[pygame.K_w]:    
            self.direction.y = -1
        if keys[pygame.K_s]:
            self.direction.y = 1
        if keys[pygame.K_a]:
            self.direction.x = -1
        if keys[pygame.K_d]:
            self.direction.x = 1
        if self.direction.xy in [(1, 1), (1,-1), (-1, 1), (-1, -1)]:
            normalise = True
        self.sprint = False
        if keys[pygame.K_LSHIFT] and (self.direction.x or self.direction.y) != 0:
            self.framesSinceLastSprint = 0
            if self.energy > 0:
                self.sprint = True

        # Move State Updates
        if self.sprint:
            self.speed = self.baseSpeed + 2
            self.energy -= 1
        else:
            self.speed = self.baseSpeed
            self.framesSinceLastSprint += 1

        if self.framesSinceLastSprint > self.sprintThreshold:
            self.energy += 1 if self.energy < self.maxEnergy else 0

        # Movement Updates
        if not self.collision:
            self.posBackup.xy = self.pos.xy

        self.vel.xy = (self.direction.xy * self.speed) / math.sqrt(2) if normalise else self.direction.xy * self.speed
        self.vel.x = round(self.vel.x)
        self.vel.y = round(self.vel.y)
        self.pos.xy += self.vel.xy

        # if self.collision:
        #     self.pos.xy = self.posBackup.xy

        self.rect.center = self.pos

        self.rect.clamp_ip(screen.get_rect())

    def DisplayEnergy(self):
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.pos.x - 64, self.pos.y - 64, 128, 16))
        pygame.draw.rect(screen, (255, 255, 0), pygame.Rect(self.pos.x - 62, self.pos.y - 63, (self.energy / self.maxEnergy) * 124, 14))

    def update(self):
        self.Input()
        self.DisplayEnergy()

        DrawText(f'Speed: {self.speed}', font, (255, 255, 255), screen, self.pos.x, self.pos.y - 160)
        DrawText(f'Frames Since Last Sprint: {self.framesSinceLastSprint}', font, (255, 255, 255), screen, self.pos.x, self.pos.y - 140)
        DrawText(f'Energy: {self.energy}', font, (255, 255, 255), screen, self.pos.x, self.pos.y - 120)
        DrawText(f'Pos: {self.pos}', font, (255, 255, 255), screen, self.pos.x, self.pos.y - 100)
        DrawText(f'PosBackup: {self.posBackup}', font, (255, 255, 255), screen, self.pos.x, self.pos.y - 80)
        DrawText(f'Collision: {self.collision}', font, (255, 255, 255), screen, self.pos.x, self.pos.y - 180)


class Level:
    def __init__(self):
        # Get Display Surface
        self.displaySurface = pygame.display.get_surface()
        
        # Sprite Group Setup
        self.groundSprites = pygame.sprite.Group()
        self.obstacleSprites = pygame.sprite.Group()
        self.entitySprites = pygame.sprite.Group()
        
        # Sprite Setup
        self.createMap()
        
    def createMap(self):
        for rowIndex, row in enumerate(GRASSY_SECTOR_LEVEL_1_MAP):
            for colIndex, col in enumerate(row):
                x = colIndex * TILESIZE
                y = rowIndex * TILESIZE
                Grass((x, y), [self.groundSprites])
                if col == 'x':
                    Rock((x, y), [self.obstacleSprites])
                if col == 't':
                    Tree((x - TILESIZE / 2, y), [self.obstacleSprites])
                if col == 'r':
                    Ruin((x, y), [self.obstacleSprites])
                if col == 'p':
                    self.player = Player((x, y), [self.entitySprites])
                    
    def run(self):
        # Update and Draw Game
        self.groundSprites.update()
        self.groundSprites.draw(self.displaySurface)
        self.entitySprites.update()
        self.entitySprites.draw(self.displaySurface)
        self.obstacleSprites.update()
        self.obstacleSprites.draw(self.displaySurface)

        self.player.collision = Collide(self.player, self.obstacleSprites)
        
class Grass(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        image = pygame.image.load('assets/img/greenGrass.png').convert_alpha()
        self.image = pygame.transform.scale(image, (TILESIZE + 1, TILESIZE + 1))
        self.rect = self.image.get_rect(topleft = pos)
        self.pos = pos

class Rock(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        images = ['assets/img/Rocks/Rock1_2.png', 'assets/img/Rocks/Rock4_2.png', 'assets/img/Rocks/Rock6_2.png']
        image = pygame.image.load(random.choice(images)).convert_alpha()
        self.image = pygame.transform.scale(image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect(topleft = pos)
        self.pos = pos

class Tree(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        images = ['assets\img\Trees\Tree2.png']
        image = pygame.image.load(random.choice(images)).convert_alpha()
        self.image = pygame.transform.scale(image, (TILESIZE * 2, TILESIZE * 2))
        self.rect = self.image.get_rect(topleft = pos)
        self.pos = pos

class Ruin(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        images = ['assets/img/Ruins/Blue-gray_ruins1.png']
        image = pygame.image.load(random.choice(images)).convert_alpha()
        self.image = pygame.transform.scale(image, (TILESIZE * 6, TILESIZE * 6))
        self.rect = self.image.get_rect(topleft = pos)
        self.pos = pos

# Settings
WIDTH = 1920
HEIGHT = 1080
TILESIZE = 64
FPS = 60
GRASSY_SECTOR_LEVEL_1_MAP = [
['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
['x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x'],
['x', ' ', 'p', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x'],
['x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 't', ' ', ' ', ' ', 'x', ' ', ' ', 'r', ' ', ' ', ' ', ' ', ' ', 't', ' ', 'x', ' ', ' ', ' ', ' ', ' ', 'x'],
['x', ' ', ' ', ' ', ' ', 'x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x'],
['x', ' ', 'x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x', ' ', 'x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x'],
['x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x', ' ', ' ', 'x'],
['x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x', ' ', ' ', ' ', ' ', 't', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x'],
['x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x', ' ', ' ', ' ', ' ', ' ', 'x', ' ', ' ', ' ', ' ', ' ', 'x'],
['x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x'],
['x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x', ' ', ' ', ' ', ' ', ' ', ' ', 't', ' ', 'x'],
['x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x'],
['x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x', ' ', ' ', ' ', 't', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x'],
['x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 't', ' ', ' ', ' ', 'x'],
['x', ' ', ' ', ' ', 'x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x', ' ', ' ', ' ', ' ', ' ', 'x'],
['x', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'x'],
['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x']]
# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

level = Level()

game = True
while game:

    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    level.run()

    pygame.display.update()
    clock.tick(FPS)

# def Input(self):
#     framesSinceLastShift = 0

#     keys = pygame.key.get_pressed()

#     self.direction.xy = (0, 0)

#     if self.energy == 0 and self.exhaustTimer == 0:
#         self.exhaustTimer = 100

#     if self.exhaustTimer > 0:
#         self.exhaustTimer -= 1

#     if keys[pygame.K_w]:
#         self.direction.y = -1
#     if keys[pygame.K_s]:
#         self.direction.y = 1
#     if keys[pygame.K_a]:
#         self.direction.x = -1
#     if keys[pygame.K_d]:
#         self.direction.x = 1
#     self.sprint = True if keys[pygame.K_LSHIFT] and self.energy > 0  and self.exhaustTimer == 0 else False

#     if self.sprint:
#         self.speed = self.baseSpeed + 2
#         self.energy -= 1
#         framesSinceLastShift = 0
#     elif self.exhaustTimer > 0:
#         self.speed = self.baseSpeed
#         framesSinceLastShift += 1
#     else:
#         self.speed = self.baseSpeed
#         self.energy += 1 if self.energy < self.maxEnergy else 0
#         framesSinceLastShift += 1

#     self.vel.xy = self.direction.xy * self.speed

#     self.pos.xy += self.vel.xy
#     self.rect.center = self.pos
#     self.rect.clamp_ip(screen.get_rect())