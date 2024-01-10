import os
import random
import sys
import time
import sqlite3
import pygame


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Button:
    def __init__(self, x, y, color, text=''):
        self.x, self.y = x, y
        self.width, self.height = 200, 50
        self.color = color
        self.text = text

    def draw(self):
        # отрисовка кнопки на экране
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        if self.text:
            font = pygame.font.SysFont(None, 20)
            text = font.render(self.text, 1, (255, 255, 255))
            screen.blit(text, (self.x + (self.width / 2 - text.get_width() / 2),
                               self.y + (self.height / 2 - text.get_height() / 2)))


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("hit_p.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(particles, all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


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
        self.has_weapon = False
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

    def take_hit(self, damage):
        if self.life <= 0:
            game_over()
        elif self.hp <= 0:
            self.life -= 1
            self.hp = 100
        if self.hp == 0 and self.life == 0:
            game_over()

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


class Sword(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, f=0):
        super().__init__(sword, all_sprites)
        types = ['sword1.png', 'sword2.png', 'sword3.png']
        # изменение текстуры меча в зависимости от его силы
        if 1 <= f < 10:
            self.image = pygame.transform.scale(load_image(types[0]), (50, 50))
        elif 10 <= f < 20:
            self.image = pygame.transform.scale(load_image(types[1]), (50, 50))
        else:
            self.image = pygame.transform.scale(load_image(types[2]), (50, 50))
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.force = 1
        self.rect.y -= 20
        self.y = self.rect.y
        self.gravity = 0.5
        self.velocity = [0, 0]

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        if not self.rect.colliderect(screen_rect) or abs(self.y - self.rect.y) >= 75:
            self.kill()


class Goods(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(equip_group, all_sprites)
        # случайный выбор текстуры предмета
        image_names = ['treasure.png', 'drink.png', 'torch.png', 'drink2.png', 'money.png',
                       'diamond.png', 'blue_stone.png', 'emerald_ball.png', 'green_stone.png',
                       'red_stone.png', 'white_ball.png', 'white_stone.png']
        self.random_type = random.randint(0, len(image_names) - 1)
        self.image = pygame.transform.scale(load_image(image_names[self.random_type]), (50, 50))
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class SimpleSword(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(sword_group, all_sprites)
        self.image = pygame.transform.scale(load_image('sword1.png'), (50, 50))
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


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
        global sum_force
        s = sum_force
        if 1 <= sum_force < 10:
            self.hp -= 1
            sum_force -= 1
        elif 10 <= sum_force < 20:
            self.hp -= 2
            sum_force -= 2
        elif sum_force >= 20:
            self.hp -= 3
            sum_force -= 3
        if self.hp <= 0:
            self.kill()

        Sword(self.rect.x / tile_width, self.rect.y / tile_height, f=s)


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


def portal_sound():
    p = pygame.mixer.Sound('data/перемещение_1.wav')
    p.play()


def sword_sound():
    p = pygame.mixer.Sound('data/удар_меча_1.mp3')
    p.play()


def hitting_the_wall_sound():
    p = pygame.mixer.Sound('data/удар_о_стену.wav')
    p.play()


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def create_particles(position):
    particles.empty()
    particle_count = 10
    # возможные скорости
    numbers = range(-5, 5)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


def terminate():
    pygame.quit()
    sys.exit()


def show_menu():
    fon = pygame.transform.scale(load_image('forest.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    easy = Button(150, 180, (23, 38, 29), 'Easy')
    normal = Button(150, 280, (23, 38, 29), 'Normal')
    hard = Button(150, 380, (23, 38, 29), 'Hard')
    easy.draw()
    normal.draw()
    hard.draw()
    font = pygame.font.Font(None, 30)
    text = font.render("Выберите уровень сложности", True, (255, 255, 255))
    screen.blit(text, (100, 50))
    while True:
        global DAMAGE
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
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
        # создание надписи
        font = pygame.font.Font(None, 50)
        text = font.render("Игра приостановлена", True, (0, 0, 0))
        text_x = WIDTH // 2 - text.get_width() // 2
        text_y = HEIGHT // 2 - text.get_height() // 2
        text_w = text.get_width()
        text_h = text.get_height()
        # отрисовка белой рамки
        pygame.draw.rect(screen, (255, 255, 255), (text_x - 10, text_y - 10,
                                                   text_w + 20, text_h + 20), 0)
        # выведение её на экран
        screen.blit(text, (text_x, text_y))
        pygame.display.flip()


def game_over():
    global collection
    fon = pygame.transform.scale(load_image('gameover.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    collection = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            if ev.type == pygame.MOUSEBUTTONDOWN or ev.type == pygame.KEYDOWN:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


def add_data(g, m, h, n, col, f):
    cur.execute(f'INSERT INTO info (gamelevel, maplevel, health, num_lives, collection, force)'
                f' VALUES ("{g}", {m}, {h}, {n}, {col}, {f})')
    con.commit()


def ask_player():
    fon = pygame.transform.scale(load_image('forest.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    cont = Button(150, 180, (23, 38, 29), 'Continue playing')
    again = Button(150, 280, (23, 38, 29), 'Start from the beginning')
    cont.draw()
    again.draw()
    font = pygame.font.Font(None, 30)
    text = font.render("Вы уже играли в данную игру", True, (255, 255, 255))
    screen.blit(text, (100, 50))
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if cont.x < pos[0] < cont.x + cont.width and cont.y < pos[1] < cont.y + cont.height:
                    return 1
                elif again.x < pos[0] < again.x + again.width and again.y < pos[1] < again.y + again.height:
                    return 0

        pygame.display.flip()
        clock.tick(FPS)


def ask_for_exchange():
    global player, collection
    fon = pygame.transform.scale(load_image('forest.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    # создание надписи
    font = pygame.font.Font(None, 25)
    text = font.render("Вы можете обменять 10 предметов на 1 жизнь?", True, (0, 0, 0))
    text_w = text.get_width()
    text_h = text.get_height()
    # отрисовка белой рамки
    pygame.draw.rect(screen, (255, 255, 255), (50, 50,
                                               text_w + 20, text_h + 20), 0)
    # выведение её на экран
    screen.blit(text, (50, 50))
    ex = Button(150, 180, (23, 38, 29), 'Обменять')
    ex.draw()
    ref = Button(150, 280, (23, 38, 29), 'Отказаться')
    ref.draw()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if ex.x < pos[0] < ex.x + ex.width and ex.y < pos[1] < ex.y + ex.height:
                    collection -= 10
                    player.life += 1
                    return
                elif ref.x < pos[0] < ref.x + ref.width and ref.y < pos[1] < ref.y + ref.height:
                    return
        pygame.display.flip()
        clock.tick(FPS)


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
            elif level[y][x] == '*':
                Tile('empty', x, y)
                SimpleSword(x, y)
    # генерация рандомного инвентаря
    for i in range(0, random.randint(0, 3)):
        x1, y1 = random.randint(0, len(level) - 1), random.randint(0, len(level) - 1)
        if level[y1][x1] == '.':
            Goods(x1, y1)

    return new_player, x, y


def move_check():
    if pygame.sprite.spritecollideany(player, walls_group) or not pygame.sprite.spritecollideany(player, tiles_group):
        return 'wb'


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Игроку нужно добраться до портала,",
                  "Убегая от врагов (призраков) и ",
                  "не потратив все свои жизни и здоровье."]

    fon = pygame.transform.scale(load_image('forest.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 70
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 70
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            elif ev.type == pygame.KEYDOWN or ev.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def final_screen():
    fon = pygame.transform.scale(load_image('final.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    start_chaos = Button(150, 180, (255, 204, 0), 'Play bonus level')
    start_chaos.draw()
    font = pygame.font.Font(None, 30)
    text = font.render("You have successfully completed all levels", True, (255, 216, 0))
    screen.blit(text, (25, 50))
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if start_chaos.x < pos[0] < start_chaos.x + start_chaos.width\
                        and start_chaos.y < pos[1] < start_chaos.y + start_chaos.height:
                    return 1
                return 0
        pygame.display.flip()
        clock.tick(FPS)


def draw_player_health():
    font = pygame.font.Font(None, 22)  # Выберите шрифт и размер шрифта по вашему вкусу
    text = font.render(f'Player HP: {player.hp} | Life: {player.life}', True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.topright = (WIDTH - 10, 10)

    # Отрисовка белой рамки
    pygame.draw.rect(screen, (255, 255, 255), (320, 5, 180, 35), 2)

    # Отрисовка текста
    screen.blit(text, text_rect)


def draw_collection():
    font = pygame.font.Font(None, 22)
    text = font.render(f' Inventory: {collection} | Weapon: {sum_force}', True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.topleft = (0, 10)

    # Отрисовка белой рамки
    pygame.draw.rect(screen, (255, 255, 255), (0, 5, 220, 35), 2)

    # Отрисовка текста
    screen.blit(text, text_rect)


def draw_done_levels():
    levels = cur.execute(f'SELECT maplevel FROM info').fetchall()
    if not flag or not levels:
        num = 0
    else:
        num = levels[0][-1]
    font = pygame.font.Font(None, 22)
    text = font.render(f' Completed levels: {num}', True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.topleft = (0, 45)

    # Отрисовка белой рамки
    pygame.draw.rect(screen, (255, 255, 255), (0, 42, 180, 25), 2)

    # Отрисовка текста
    screen.blit(text, text_rect)


def animation_update():
    particles.update()
    sword.update()
    screen.fill((0, 0, 255))
    tiles_group.draw(screen)
    walls_group.draw(screen)
    equip_group.draw(screen)
    portals_group.draw(screen)
    player_group.draw(screen)
    enemy_group.draw(screen)
    particles.draw(screen)
    sword.draw(screen)
    sword_group.draw(screen)
    range_a.update_position(player.rect)
    range_group.draw(screen)
    range_group.update()
    camera.update(player)

    for sprite in all_sprites:
        camera.apply(sprite)

    draw_player_health()
    draw_collection()
    draw_done_levels()

    pygame.display.flip()
    clock.tick(FPS)


def smooth_player_move_up():
    for i in range(5):
        player.image = pygame.transform.scale(load_image('2.png'), (50, 50))
        player.rect.y -= STEP / 5

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()

        animation_update()


def smooth_player_move_down():
    for i in range(5):
        player.image = pygame.transform.scale(load_image('1.png'), (50, 50))
        player.rect.y += STEP / 5

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
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

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()

        animation_update()


def chaos():
    # карты для последнего уровня
    base = {
        'wall': '#',
        'sword': '*',
        'none': '.'}
    lucky = random.randint(-1, 10)
    n = int(random.randint(3, 40))
    chaos_base = [[0] * n for _ in range(n)]
    with (open('data/chaos.txt', 'w') as f):
        f.write('')
        while True:
            if lucky == -1:
                game_over()
                break
            for y in range(n):
                for x in range(n):
                    item = base[random.choice(list(base.keys()))]
                    chaos_base[y][x] = item

            chaos_base[0][0] = '@'
            chaos_base[n - 1][n - 1] = '!'
            enemy = random.randint(0, lucky * 2 + 1)
            replacements = 0

            while replacements < enemy:
                x, y = random.randint(0, n - 1), random.randint(0, n - 1)
                if chaos_base[y][x] != '&':
                    chaos_base[y][x] = '&'
                    replacements += 1

            chaos_base[0][1] = '.'
            chaos_base[1][0] = '.'
            chaos_base[1][1] = '.'

            for row in chaos_base:
                f.write(''.join(map(str, row)) + '\n')
            break


def fade_out_and_load_new_world(screen, clock, new_map_filename):
    portal_sound()
    global base, tiles_group, tile_height, tile_width, camera, all_sprites, player_group, enemy_group, walls_group, \
        portals_group, player, level_x, level_y, state, equip_group, sword_group
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
    equip_group = pygame.sprite.Group()
    sword_group = pygame.sprite.Group()
    portals_group = pygame.sprite.Group()
    player, level_x, level_y = generate_level(load_level(new_map_filename))
    state = 1

    last = cur.execute(f'SELECT * FROM info'
                       f' WHERE id=(SELECT max(id) FROM info)').fetchall()
    player.life = last[0][4]
    player.hp = last[0][3]

    pygame.time.delay(1000)


maps = {
    'easy': ['map.txt', 'map2.txt'],
    'normal': ['map.txt', 'map2.txt'],
    'hard': ['map.txt', 'map2.txt']
}

con = sqlite3.connect('Game_db.sqlite')
cur = con.cursor()
cur.execute('''
        CREATE TABLE IF NOT EXISTS info (
        id INTEGER PRIMARY KEY,
        gamelevel TEXT NOT NULL,
        maplevel INTEGER NOT NULL,
        health INTEGER NOT NULL,
        num_lives INTEGER NOT NULL,
        collection INTEGER NOT NULL,
        force INTEGER NOT NULL)
        ''')

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.music.load('data/Фоновая_музыка.mp3')
pygame.mixer.music.play(-1)
FPS = 50
DAMAGE = 20
LIFE = 1
GRAVITY = 0
WIDTH, HEIGHT = 500, 500
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen_rect = (0, 0, WIDTH, HEIGHT)
screen.fill((0, 0, 255))
start_screen()
STEP = 50

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'enemy': pygame.transform.scale(load_image('ghost.png'), (50, 50)),
    'portal': load_image('portal.png')
}
player_image = pygame.transform.scale(load_image('1.png'), (50, 50))

tile_width = tile_height = 50
camera = Camera()
all_sprites = pygame.sprite.Group()
particles = pygame.sprite.Group()
sword = pygame.sprite.Group()
sword_group = pygame.sprite.Group()
equip_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
portals_group = pygame.sprite.Group()

last = cur.execute(f'SELECT * FROM info'
                   f' WHERE id=(SELECT max(id) FROM info)').fetchall()
flag = 0 if not last else ask_player()
if last and flag:
    gamelevel = last[0][1]
    maplevel = last[0][2]
    try:
        base = load_level(maps[gamelevel][maplevel])
        player, level_x, level_y = generate_level(load_level(maps[gamelevel][maplevel]))
    except IndexError:
        if final_screen():
            chaos()
        base = load_level('chaos.txt')
        player, level_x, level_y = generate_level(load_level('chaos.txt'))
    player.hp = last[0][3]
    player.life = last[0][4]
    collection = last[0][5]
    sum_force = last[0][6]
else:
    gamelevel = show_menu()
    maplevel = 0
    base = load_level(maps[gamelevel][0])
    player, level_x, level_y = generate_level(load_level(maps[gamelevel][0]))
    collection = 0
    sum_force = 0
range_a = Range(player.rect)
range_group = pygame.sprite.Group()
range_group.add(range_a)
state = 1

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            add_data(gamelevel, maplevel, player.hp, player.life, collection, sum_force)
            terminate()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if range_a.rect.collidepoint(event.pos):
                enemy_hit = pygame.sprite.spritecollideany(range_a, enemy_group)
                if enemy_hit and sum_force >= 1:
                    sword_sound()
                    create_particles(pygame.mouse.get_pos())
                    enemy_hit.take_hit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                smooth_player_move_left()
                if move_check() == 'wb':
                    if pygame.sprite.spritecollideany(player, portals_group):
                        add_data(gamelevel, maplevel, player.hp, player.life, collection, sum_force)
                        maplevel += 1
                        try:
                            fade_out_and_load_new_world(screen, clock, maps[gamelevel][maplevel])
                        except IndexError:
                            portal_sound()
                            if final_screen():
                                chaos()
                                fade_out_and_load_new_world(screen, clock, 'chaos.txt')
                        continue
                    else:
                        hitting_the_wall_sound()
                    smooth_player_move_right()
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                smooth_player_move_right()
                if move_check() == 'wb':
                    if pygame.sprite.spritecollideany(player, portals_group):
                        add_data(gamelevel, maplevel, player.hp, player.life, collection, sum_force)
                        maplevel += 1
                        try:
                            fade_out_and_load_new_world(screen, clock, maps[gamelevel][maplevel])
                        except IndexError:
                            portal_sound()
                            if final_screen():
                                chaos()
                                fade_out_and_load_new_world(screen, clock, 'chaos.txt')
                        continue
                    else:
                        hitting_the_wall_sound()
                    smooth_player_move_left()
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                smooth_player_move_up()
                if move_check() == 'wb':
                    if pygame.sprite.spritecollideany(player, portals_group):
                        continue
                    else:
                        hitting_the_wall_sound()
                    smooth_player_move_down()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                smooth_player_move_down()
                if move_check() == 'wb':
                    if pygame.sprite.spritecollideany(player, portals_group):
                        add_data(gamelevel, maplevel, player.hp, player.life, collection, sum_force)
                        maplevel += 1
                        try:
                            fade_out_and_load_new_world(screen, clock, maps[gamelevel][maplevel])
                        except IndexError:
                            portal_sound()
                            if final_screen():
                                chaos()
                                fade_out_and_load_new_world(screen, clock, 'chaos.txt')
                        continue
                    else:
                        hitting_the_wall_sound()
                    smooth_player_move_up()
            elif event.key == pygame.K_ESCAPE:
                state = 0
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e and collection >= 10:
                    ask_for_exchange()
    if state:
        for enemy in enemy_group:
            enemy.move_towards_player(player.rect)
        particles.update()
        sword.update()
        screen.fill((0, 0, 255))
        tiles_group.draw(screen)
        walls_group.draw(screen)
        portals_group.draw(screen)
        player_group.draw(screen)
        equip_group.draw(screen)
        enemy_group.draw(screen)
        particles.draw(screen)
        sword.draw(screen)
        sword_group.draw(screen)
        range_a.update_position(player.rect)
        range_group.draw(screen)
        range_group.update()
        camera.update(player)

        for sprite in all_sprites:
            camera.apply(sprite)

        draw_player_health()
        draw_collection()
        draw_done_levels()
        LIFE = player.life

        # коллекционирование инвентаря, находящегося на карте
        for thing in equip_group:
            if pygame.sprite.collide_rect(player, thing):
                if thing.random_type == 1:
                    player.hp += 20
                    if player.hp > 100:
                        player.hp %= 100
                        player.life += 1
                elif thing.random_type == 3:
                    player.hp += 25
                    if player.hp > 100:
                        player.hp %= 100
                        player.life += 1
                collection += 1
                thing.kill()
                if collection // 10 >= 1:
                    ask_for_exchange()
        for sw in sword_group:
            if pygame.sprite.collide_rect(player, sw):
                sw.kill()
                sum_force += 1
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
