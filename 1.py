import pygame
import sys
import random
import time

# Инициализация Pygame
pygame.init()

# Определение констант
NUM_ROWS, NUM_COLS = 20, 20  # Количество строк и столбцов
CELL_SIZE = 800 // NUM_ROWS, 800 // NUM_COLS  # Вычисление размера клетки
FPS = 60
white = (255, 255, 255)
black = (0, 0, 0)
gray = (169, 169, 169)
red = (210, 60, 0)
purple = (128, 0, 128)
e_speed = 1000
cl = False
last_move = False

# Создание окна
screen = pygame.display.set_mode((CELL_SIZE[0] * NUM_COLS, CELL_SIZE[1] * NUM_ROWS))
pygame.display.set_caption("228")

# Загрузка картинки заднего плана
background_image = pygame.image.load("data/1677366330_foni-club-p-piksel-art-trava-3.png")
background_image = pygame.transform.scale(background_image, (CELL_SIZE[0] * NUM_COLS, CELL_SIZE[1] * NUM_ROWS))

# Инициализация игрового поля (двумерный массив)
board = [[0] * NUM_COLS for _ in range(NUM_ROWS)]

# Загрузка картинок
player_image = pygame.image.load("data/1.png")
player_image = pygame.transform.scale(player_image, CELL_SIZE)

wall_image1 = pygame.image.load("data/wall1.jpeg")
wall_image1 = pygame.transform.scale(wall_image1, CELL_SIZE)
wall_image = pygame.image.load("data/wall.jpeg")
wall_image = pygame.transform.scale(wall_image, CELL_SIZE)


# Класс игрока    
class Player:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        time.sleep(0.1)


# Класс портала
class Portal:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# Класс стены
class Wall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.texture = random.choice([wall_image, wall_image1])


# Класс врага
class Enemy:
    def __init__(self, x, y, speed, move_delay):
        self.x = x
        self.y = y
        self.speed = speed
        self.move_delay = move_delay
        self.last_move_time = pygame.time.get_ticks()

    def update(self, player, walls):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time > self.move_delay:
            self.last_move_time = current_time
            dx = 0
            dy = 0
            if self.x < player.x:
                dx = self.speed
            elif self.x > player.x:
                dx = -self.speed

            if self.y < player.y:
                dy = self.speed
            elif self.y > player.y:
                dy = -self.speed
            if not self.check_wall_collision(walls, dx, dy):
                self.x += dx
                self.y += dy

    def check_collision(self, player):
        # Проверка столкновения врага с игроком
        if self.x == player.x and self.y == player.y:
            return True
        return False

    def check_wall_collision(self, walls, dx, dy):
        # Проверка столкновения врага со стенами
        next_x = self.x + dx
        next_y = self.y + dy
        for wall in walls:
            if next_x == wall.x and next_y == wall.y:
                return True
        return False


# Функция для отрисовки игрового поля
def draw_grid():
    # Отображение заднего плана
    screen.blit(background_image, (0, 0))
    if cl:
        for x in range(0, CELL_SIZE[0] * NUM_COLS, CELL_SIZE[0]):
            pygame.draw.line(screen, black, (x, 0), (x, CELL_SIZE[1] * NUM_ROWS))
        for y in range(0, CELL_SIZE[1] * NUM_ROWS, CELL_SIZE[1]):
            pygame.draw.line(screen, black, (0, y), (CELL_SIZE[0] * NUM_COLS, y))


# Функция для отрисовки сущности
def draw_entity(entity_pos, color):
    if color == black and last_move == 's':
        screen.blit(player_image, (entity_pos.x * CELL_SIZE[0], entity_pos.y * CELL_SIZE[1]))
    elif color == black and last_move == 'w':
        screen.blit(pygame.transform.scale(pygame.image.load("data/2.png"), CELL_SIZE),
                    (entity_pos.x * CELL_SIZE[0], entity_pos.y * CELL_SIZE[1]))
    elif color == black and last_move == 'left1':
        screen.blit(pygame.transform.scale(pygame.image.load("data/left1.png"), CELL_SIZE),
                    (entity_pos.x * CELL_SIZE[0], entity_pos.y * CELL_SIZE[1]))
    elif color == black and last_move == 'left2':
        screen.blit(pygame.transform.scale(pygame.image.load("data/left2.png"), CELL_SIZE),
                    (entity_pos.x * CELL_SIZE[0], entity_pos.y * CELL_SIZE[1]))
    elif color == black and last_move == 'r1':
        screen.blit(pygame.transform.scale(pygame.image.load("data/r1.png"), CELL_SIZE),
                    (entity_pos.x * CELL_SIZE[0], entity_pos.y * CELL_SIZE[1]))
    elif color == black and last_move == 'r2':
        screen.blit(pygame.transform.scale(pygame.image.load("data/r2.png"), CELL_SIZE),
                    (entity_pos.x * CELL_SIZE[0], entity_pos.y * CELL_SIZE[1]))
    elif color == black:
        screen.blit(player_image, (entity_pos.x * CELL_SIZE[0], entity_pos.y * CELL_SIZE[1]))
    elif color == gray:
        screen.blit(entity_pos.texture, (entity_pos.x * CELL_SIZE[0], entity_pos.y * CELL_SIZE[1]))
    else:
        entity_rect = pygame.Rect(entity_pos.x * CELL_SIZE[0], entity_pos.y * CELL_SIZE[1], CELL_SIZE[0], CELL_SIZE[1])
        pygame.draw.rect(screen, color, entity_rect)


def handle_mouse_events(mouse_pos, walls, enemies):
    x, y = mouse_pos

    # Получение координаты клетки, на которую указывает мышь
    grid_x = x // CELL_SIZE[0]
    grid_y = y // CELL_SIZE[1]

    keys = pygame.key.get_pressed()

    # Shift + правая кнопка мыши - поставить стену или врага
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        if pygame.mouse.get_pressed()[2]:  # Правая кнопка мыши
            # E + правая кнопка мыши - поставить врага
            if keys[pygame.K_e]:
                new_enemy = Enemy(grid_x, grid_y, 1, 0)
                enemies.append(new_enemy)
            # Shift + правая кнопка мыши - поставить стену
            else:
                new_wall = Wall(grid_x, grid_y)
                walls.append(new_wall)

        # Shift + левая кнопка мыши - сломать стену или врага
        elif pygame.mouse.get_pressed()[0]:  # Левая кнопка мыши
            for wall in walls:
                if wall.x == grid_x and wall.y == grid_y:
                    walls.remove(wall)

            for enemy in enemies:
                if enemy.x == grid_x and enemy.y == grid_y:
                    enemies.remove(enemy)


# Главный цикл игры
def main():
    global board
    clock = pygame.time.Clock()

    # Создание объекта игрока
    player = Player(random.randint(0, NUM_COLS - 1), random.randint(0, NUM_ROWS - 1), 1)

    # Создание объекта портала на границе поля
    portal = Portal(random.choice([0, NUM_COLS - 1]), random.choice([0, NUM_ROWS - 1]))

    # Генерация случайного количества стен
    num_walls = random.randint(50, 100)
    walls = [Wall(random.randint(0, NUM_COLS - 1), random.randint(0, NUM_ROWS - 1)) for _ in range(num_walls)]

    # Создание врагов
    num_enemies = 3
    enemies = [Enemy(random.randint(0, NUM_COLS - 1), random.randint(0, NUM_ROWS - 1), 1, e_speed) for _ in
               range(num_enemies)]

    while True:
        global last_move
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Обработка событий мыши
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_events(pygame.mouse.get_pos(), walls, enemies)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player.y > 0 and board[player.y - 1][player.x] != 2:
            player.move(0, -player.speed)
            last_move = 'w'
        if keys[pygame.K_s] and player.y < NUM_ROWS - 1 and board[player.y + 1][player.x] != 2:
            player.move(0, player.speed)
            last_move = 's'
        if keys[pygame.K_a] and player.x > 0 and board[player.y][player.x - 1] != 2:
            player.move(-player.speed, 0)
            if last_move == 'left1':
                last_move = 'left2'
            else:
                last_move = 'left1'
        if keys[pygame.K_d] and player.x < NUM_COLS - 1 and board[player.y][player.x + 1] != 2:
            player.move(player.speed, 0)
            if last_move == 'r1':
                last_move = 'r2'
            else:
                last_move = 'r1'

        # Обновление позиции врагов
        for enemy in enemies:
            enemy.update(player, walls)

        # Проверка столкновения врагов с игроком
        for enemy in enemies:
            if enemy.check_collision(player):
                walls = [Wall(random.randint(0, NUM_COLS - 1), random.randint(0, NUM_ROWS - 1)) for _ in
                         range(num_walls)]
                player = Player(random.randint(0, NUM_COLS - 1), random.randint(0, NUM_ROWS - 1), 1)
                portal = Portal(random.choice([0, NUM_COLS - 1]), random.choice([0, NUM_ROWS - 1]))
                enemies = [Enemy(random.randint(0, NUM_COLS - 1), random.randint(0, NUM_ROWS - 1), 1, e_speed) for _ in
                           range(num_enemies)]
                for _ in enemies:
                    enemy.update(player, walls)
        # Проверка попадания на портал
        if player.x == portal.x and player.y == portal.y:
            walls = [Wall(random.randint(0, NUM_COLS - 1), random.randint(0, NUM_ROWS - 1)) for _ in
                     range(num_walls)]
            player = Player(random.randint(0, NUM_COLS - 1), random.randint(0, NUM_ROWS - 1), 1)

            # Создание объекта портала на границе поля
            portal = Portal(random.choice([0, NUM_COLS - 1]), random.choice([0, NUM_ROWS - 1]))
            enemies = [Enemy(random.randint(0, NUM_COLS - 1), random.randint(0, NUM_ROWS - 1), 1, e_speed) for _ in
                       range(num_enemies)]
            for enemy in enemies:
                enemy.update(player, walls)

        board = [[0] * NUM_COLS for _ in range(NUM_ROWS)]
        for wall in walls:
            board[wall.y][wall.x] = 2
        board[player.y][player.x] = 1

        board[portal.y][portal.x] = -1  # Установка значения -1 для портала

        # Очистка экрана
        screen.fill(white)

        # Отрисовка игрового поля и сущностей
        draw_grid()
        draw_entity(player, black)

        for wall in walls:
            draw_entity(wall, gray)
        draw_entity(player, black)
        draw_entity(portal, purple)  # Отрисовка портала

        # Отрисовка врагов
        for enemy in enemies:
            draw_entity(enemy, red)

        # Обновление экрана
        pygame.display.flip()

        # Задержка, чтобы управлять скоростью игры
        clock.tick(FPS)


if __name__ == "__main__":
    main()
