import os
import sys
import time

import pygame


class Button:
    def __init__(self, x, y, color, text=''):
        self.x, self.y = x, y
        self.width, self.height = 200, 50
        self.color = color
        self.text = text

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        if self.text:
            font = pygame.font.SysFont(None, 20)
            text = font.render(self.text, 1, (255, 255, 255))
            screen.blit(text, (self.x + (self.width / 2 - text.get_width() / 2),
                               self.y + (self.height / 2 - text.get_height() / 2)))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Range(pygame.sprite.Sprite):
    def __init__(self, player_rect, *group):
        super().__init__(*group)
        self.radius = 75
        self.color = (255, 0, 0, 100)  # Red color
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius, 10)
        self.rect = self.image.get_rect(center=(player_rect.centerx, player_rect.centery))

    def update_position(self, player_rect):
        self.rect.center = (player_rect.centerx, player_rect.centery)


class Wall(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(walls_group, all_sprites)
        self.image = tile_images['wall']
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Portal(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(portals_group, all_sprites)
        self.image = tile_images['portal']
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        self.hp = 100
        self.life = LIFE
        self.recoil_distance = 50
        self.last_damage_time = 0
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

    def take_hit(self, damage):
        if self.life <= 0:
            terminate()
        elif self.hp <= 0:
            self.life -= 1
            self.hp = 100

        current_time = time.time()
        if current_time - self.last_damage_time >= 0.5:
            self.hp -= damage
            self.last_damage_time = current_time

    def apply_recoil(self, enemy_rect):
        dx = self.rect.x - enemy_rect.x
        dy = self.rect.y - enemy_rect.y
        dist = max(abs(dx), abs(dy))

        if dist != 0:
            dx = dx / dist * self.recoil_distance
            dy = dy / dist * self.recoil_distance

        new_x = self.rect.x + dx
        new_y = self.rect.y + dy
        self.rect.x = new_x
        self.rect.y = new_y


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, speed=0.1):
        super().__init__(enemy_group, all_sprites)
        self.image = tile_images['enemy']
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.speed = speed
        self.hp = 3

    def move_towards_player(self, player_rect):
        dx = player_rect.x - self.rect.x
        dy = player_rect.y - self.rect.y
        dist = max(abs(dx), abs(dy))

        if dist != 0:
            dx = dx / dist * self.speed
            dy = dy / dist * self.speed

        new_x = self.rect.x + dx
        new_y = self.rect.y + dy
        self.rect.x = new_x
        self.rect.y = new_y

    def take_hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill()


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def terminate():
    pygame.quit()
    sys.exit()


def show_menu():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    easy = Button(150, 180, (0, 0, 255), 'Easy')
    normal = Button(150, 280, (0, 0, 255), 'Normal')
    hard = Button(150, 380, (0, 0, 255), 'Hard')
    easy.draw()
    normal.draw()
    hard.draw()
    font = pygame.font.Font(None, 30)
    text = font.render("Выберите уровень сложности", True, (0, 0, 0))
    screen.blit(text, (100, 50))
    while True:
        global DAMAGE
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if easy.x < pos[0] < easy.x + easy.width and easy.y < pos[1] < easy.y + easy.height:
                    DAMAGE = 5
                    return 'easy'
                elif normal.x < pos[0] < normal.x + normal.width and normal.y < pos[1] < normal.y + normal.height:
                    DAMAGE = 10
                    return 'normal'
                elif hard.x < pos[0] < hard.x + hard.width and hard.y < pos[1] < hard.y + hard.height:
                    DAMAGE = 20
                    return 'hard'

        pygame.display.flip()
        clock.tick(FPS)


def pause():
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return 1
        font = pygame.font.Font(None, 50)
        text = font.render("Игра приостановлена", True, (0, 0, 0))
        text_x = WIDTH // 2 - text.get_width() // 2
        text_y = HEIGHT // 2 - text.get_height() // 2
        text_w = text.get_width()
        text_h = text.get_height()
        pygame.draw.rect(screen, (255, 255, 255), (text_x - 10, text_y - 10,
                                                   text_w + 20, text_h + 20), 0)
        screen.blit(text, (text_x, text_y))
        pygame.display.flip()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Wall(x, y)
            elif level[y][x] == '&':
                Enemy(x, y, speed=1)
                Tile('empty', x, y)
            elif level[y][x] == '!':
                Portal(x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)

    return new_player, x, y


def move_check():
    if pygame.sprite.spritecollideany(player, walls_group) or not pygame.sprite.spritecollideany(player, tiles_group):
        return 'wb'


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 70
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 70
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def draw_player_health():
    font = pygame.font.Font(None, 30)  # Выберите шрифт и размер шрифта по вашему вкусу
    text = font.render(f'Player HP: {player.hp} | Life: {player.life}', True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.topright = (WIDTH - 10, 10)

    # Отрисовка белой рамки
    pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 245, 5, 240, 35), 2)

    # Отрисовка текста
    screen.blit(text, text_rect)


def animation_update():
    screen.fill((0, 0, 255))
    tiles_group.draw(screen)
    walls_group.draw(screen)
    portals_group.draw(screen)
    player_group.draw(screen)
    enemy_group.draw(screen)
    range_a.update_position(player.rect)
    range_group.draw(screen)
    range_group.update()
    camera.update(player)

    for sprite in all_sprites:
        camera.apply(sprite)

    draw_player_health()

    pygame.display.flip()
    clock.tick(FPS)


def smooth_player_move_up():
    for i in range(5):
        player.image = pygame.transform.scale(load_image('2.png'), (50, 50))
        player.rect.y -= STEP / 5

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        animation_update()


def smooth_player_move_down():
    for i in range(5):
        player.image = pygame.transform.scale(load_image('1.png'), (50, 50))
        player.rect.y += STEP / 5

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        animation_update()


def smooth_player_move_left():
    for i in range(5):
        if i % 2 == 0:
            player.image = pygame.transform.scale(load_image('left1.png'), (50, 50))
        else:
            player.image = pygame.transform.scale(load_image('left2.png'), (50, 50))
        player.rect.x -= STEP / 5

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        animation_update()


def smooth_player_move_right():
    for i in range(5):
        if i % 2 == 0:
            player.image = pygame.transform.scale(load_image('r1.png'), (50, 50))
        else:
            player.image = pygame.transform.scale(load_image('r2.png'), (50, 50))
        player.rect.x += STEP / 5

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        animation_update()


def fade_out_and_load_new_world(screen, clock, new_map_filename):
    global base, tiles_group, tile_height, tile_width, camera, all_sprites, player_group, enemy_group, walls_group, \
        portals_group, player, level_x, level_y, state
    fade_duration = 2000
    fade_steps = 50
    fade_step_duration = fade_duration // fade_steps

    fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
    fade_surface.fill((0, 0, 0))

    for alpha in range(fade_steps + 1):
        fade_surface.set_alpha(int(alpha / fade_steps * 255))
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(fade_step_duration)
        clock.tick(60)
    base = load_level(new_map_filename)
    tile_width = tile_height = 50
    camera = Camera()
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    portals_group = pygame.sprite.Group()
    player, level_x, level_y = generate_level(load_level(new_map_filename))
    state = 1
    player.life = LIFE

    pygame.time.delay(1000)


maps = {
    'easy': ['map.txt', 'map2.txt'],
    'normal': ['map.txt', 'map2.txt'],
    'hard': ['map.txt', 'map2.txt']
}
game_level = 'easy'
maplevel = 0
pygame.init()
FPS = 50
DAMAGE = 20
LIFE = 1
WIDTH, HEIGHT = 500, 500
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill((0, 0, 255))
start_screen()
gamelevel = show_menu()
STEP = 50

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'enemy': pygame.transform.scale(load_image('ghost.png'), (50, 50)),
    'portal': load_image('portal.png')
}
player_image = pygame.transform.scale(load_image('1.png'), (50, 50))

base = load_level(maps[gamelevel][0])
tile_width = tile_height = 50
camera = Camera()
all_sprites = pygame.sprite.Group()

tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

walls_group = pygame.sprite.Group()
portals_group = pygame.sprite.Group()
player, level_x, level_y = generate_level(load_level(maps[gamelevel][0]))
range_a = Range(player.rect)
range_group = pygame.sprite.Group()
range_group.add(range_a)
state = 1

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if the click position is within the bomb's zone
            if range_a.rect.collidepoint(event.pos):
                # Check for collision between enemies and the bomb
                enemy_hit = pygame.sprite.spritecollideany(range_a, enemy_group)
                if enemy_hit:
                    # Register a hit on the enemy
                    enemy_hit.take_hit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                smooth_player_move_left()
                if move_check() == 'wb':
                    if pygame.sprite.spritecollideany(player, portals_group):
                        continue
                    smooth_player_move_right()
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                smooth_player_move_right()
                if move_check() == 'wb':
                    if pygame.sprite.spritecollideany(player, portals_group):
                        continue
                    smooth_player_move_left()
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                smooth_player_move_up()
                if move_check() == 'wb':
                    if pygame.sprite.spritecollideany(player, portals_group):
                        continue
                    smooth_player_move_down()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                smooth_player_move_down()
                if move_check() == 'wb':
                    if pygame.sprite.spritecollideany(player, portals_group):
                        maplevel += 1
                        fade_out_and_load_new_world(screen, clock, maps[gamelevel][maplevel])
                        continue
                    smooth_player_move_up()
            elif event.key == pygame.K_ESCAPE:
                state = 0
    if state:
        for enemy in enemy_group:
            enemy.move_towards_player(player.rect)

        screen.fill((0, 0, 255))
        tiles_group.draw(screen)
        walls_group.draw(screen)
        portals_group.draw(screen)
        player_group.draw(screen)
        enemy_group.draw(screen)
        range_a.update_position(player.rect)
        range_group.draw(screen)
        range_group.update()
        camera.update(player)

        for sprite in all_sprites:
            camera.apply(sprite)

        draw_player_health()
        LIFE = player.life

        if player.life == 0 and player.hp == 0:
            terminate()
        for enemy in enemy_group:
            if pygame.sprite.collide_rect(player, enemy):
                enemies_in_radius = pygame.sprite.spritecollide(range_a, enemy_group, False)
                num_enemies_in_radius = len(enemies_in_radius)
                total_damage = len(enemies_in_radius) * DAMAGE
                player.take_hit(total_damage)


    else:
        if pause():
            state = 1
    pygame.display.flip()
    clock.tick(FPS)
