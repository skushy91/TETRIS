import pygame

from random import *

from settings import *

pygame.init()

pygame.mixer.init()

#Tetris playing grid = 250 x 500

SCREEN_WIDTH, SCREEN_HEIGHT = 700, 900

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

font = pygame.font.SysFont('Arial', 60)
font1 = pygame.font.SysFont('Arial', 30)
font2 = pygame.font.SysFont('Arial', 25)

CELL_SIZE = 40
ROWS = 20
COLS = 10

TEMP_OFFSET = pygame.Vector2(COLS // 2, -1)

DARK_GREY = (50, 50, 50)

pygame.mixer.music.load('Tetris.mp3')

pygame.mixer.music.set_volume(0.3)

pygame.mixer.music.play(-1)

class Game:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.surface = pygame.Surface((COLS * CELL_SIZE, ROWS * CELL_SIZE))
        self.rect = self.surface.get_rect(bottomleft = (20, self.display_surface.get_height() - 20))
        self.panel = Panel((440, 80), 'preview')
        self.score = Panel((440, 340), 'score')
        self.sprites = pygame.sprite.Group()

        self.field_data = [[0 for x in range(COLS)] for y in range(ROWS)]
        self.next_str_shape = choice(list(TETROMINOS.keys()))
        self.tetromino = Tetromino(choice(list(TETROMINOS.keys())), self.sprites, self.create_new_tetromino, self.field_data)
        self.preview_tetromino = PreviewTetromino(self.next_str_shape)

        self.click = True
        self.current = pygame.time.get_ticks()
        
        self.fall = True
        self.current1 = pygame.time.get_ticks()

        self.rotate_piece = True
        self.rotate_timer = pygame.time.get_ticks()

        self.move_fast_down = True
        self.fast_timer = pygame.time.get_ticks()

        self.down_speed = 500
        
        self.game_over = False

        self.game_score = 0

        self.creating_new = False

        self.paused = False

    def input(self):
        if not self.creating_new:
            if self.click:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a]:
                    self.tetromino.move_horizontal(-1)
                if keys[pygame.K_d]:
                    self.tetromino.move_horizontal(1)
                self.click = False

            if not self.click:
                if pygame.time.get_ticks() - self.current >= 150:
                    self.click = True
                    self.current = pygame.time.get_ticks()

            if self.rotate_piece:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_w]:
                    self.tetromino.rotate()

                self.rotate_piece = False

            if not self.rotate_piece:
                if pygame.time.get_ticks() - self.rotate_timer >= 200:
                    self.rotate_piece = True
                    self.rotate_timer = pygame.time.get_ticks()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_s]:
                self.down_speed = 200

            elif keys[pygame.K_SPACE] and self.move_fast_down:
                for i in range(20):
                    if not self.tetromino.next_move_vertical_collide(self.tetromino.blocks, i):
                        pass
                    else:
                        break

                if self.check_row_is_clear(self.tetromino.blocks, i):
                    for block in self.tetromino.blocks:
                        block.pos.y += i - 1

                self.move_fast_down = False
            else:
                self.down_speed = 500

            if not self.move_fast_down:

                if pygame.time.get_ticks() - self.fast_timer >= 600:
                    
                    self.move_fast_down = True
                    self.fast_timer = pygame.time.get_ticks()

    def check_row_is_clear(self, blocks, index):
        for block in blocks:
            for i in range(index):
                if self.field_data[i][int(block.pos.x)] != 0:
                    return False
                
        return True

    def move_down(self):
        if self.fall:
            self.tetromino.movedown()
            self.fall = False
        
        if not self.fall:
            if pygame.time.get_ticks() - self.current1 >= self.down_speed:
                self.fall = True
                self.current1 = pygame.time.get_ticks()

    def draw_grid(self):
        for col in range(1, COLS):
            x = col * CELL_SIZE
            pygame.draw.line(self.surface, 'grey', (x, 0), (x, self.surface.get_height()))
        
        for row in range(1, ROWS):
            y = row * CELL_SIZE
            pygame.draw.line(self.surface, 'grey', (0, y), (self.surface.get_width(), y))
    
    def update(self):
        self.surface.fill('black')

        self.sprites.draw(self.surface)
        if not self.game_over:
            if not self.paused:
                self.sprites.update()
                self.panel.update()
                self.move_down()
                self.input()

        self.draw_grid()

        if self.game_over:
            self.gameover_func()

        self.display_surface.blit(self.surface, self.rect)

    def create_new_tetromino(self):
        self.check_rows()
        self.tetromino = Tetromino(self.next_str_shape, self.sprites, self.create_new_tetromino, self.field_data)
        self.next_str_shape = choice(list(TETROMINOS.keys()))
        self.preview_tetromino = PreviewTetromino(self.next_str_shape)

    def check_rows(self):
        delete_rows = []

        for i, row in enumerate(self.field_data):
            if all(row):
                delete_rows.append(i)

        if delete_rows:
            for delete_row in delete_rows:
                self.game_score += 100
                for block in self.field_data[delete_row]:
                    block.kill()

                for row in self.field_data:
                    for block in row:
                        if block and block.pos.y < delete_row:
                            block.pos.y += 1

            self.field_data = [[0 for x in range(COLS)] for y in range(ROWS)]
            for block in self.sprites:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block

    def gameover_func(self):
        gameover_title = font.render('Gameover!', False, DARK_GREY)
        self.display_surface.blit(gameover_title, (440, 600))

        gameover_title1 = font2.render(f'Your final score was {game.game_score}!', False, DARK_GREY)
        self.display_surface.blit(gameover_title1, (self.display_surface.get_width() / 2 - gameover_title1.get_width()/2 + 210, 670))

class Panel:
    def __init__(self, pos, type):
        self.display_surface = pygame.display.get_surface()
        self.surface = pygame.Surface((240, 240))
        self.rect = self.surface.get_rect(topleft = pos)

        self.type = type

    def update(self):
        self.surface.fill(DARK_GREY)
        if self.type == 'preview':
            game.preview_tetromino.update()
            preview_title = font1.render('Next Tetromino:', False, 'white')
            self.surface.blit(preview_title, (self.surface.get_width() / 2 - preview_title.get_width() / 2, 10))

        else:
            score_title = font.render('Score:', False, 'white')
            self.surface.blit(score_title, (self.surface.get_width() / 2 - score_title.get_width() / 2, 10))

            score_title1 = font.render(f'{game.game_score}', False, 'white')
            self.surface.blit(score_title1, (self.surface.get_width() / 2 - score_title1.get_width() / 2, 100))
        self.display_surface.blit(self.surface, self.rect)

class Block(pygame.sprite.Sprite):
    def __init__(self, group, pos, color):
        super().__init__(group)
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(color)

        self.pos = pygame.Vector2(pos) + TEMP_OFFSET

        x = self.pos.x * CELL_SIZE
        y = self.pos.y * CELL_SIZE

        self.rect = self.image.get_rect(topleft = (x, y))

    def update(self):
        x = self.pos.x * CELL_SIZE
        y = self.pos.y * CELL_SIZE

        self.rect = self.image.get_rect(topleft = (x, y))

    def horizontal_collide(self, x, field_data):
        if not 0 <= x < COLS:
            return True
        
        if field_data[int(self.pos.y)][x]:
            return True
        
    def vertical_collide(self, y, field_data):
        if y >= ROWS:
            return True
        
        if y >= 0 and field_data[y][int(self.pos.x)]:
            return True
        
    def rotate(self, pivot_pos):
        distance = self.pos - pivot_pos
        rotated = distance.rotate(90)
        new_pos = pivot_pos + rotated
        return new_pos

class Tetromino:
    def __init__(self, shape, group, create_new_tetromino, field_data):
        self.block_positions = TETROMINOS[shape]['shape']
        self.color = TETROMINOS[shape]['color']

        self.shape = shape

        self.field_data = field_data

        self.blocks = [Block(group, pos, self.color) for pos in self.block_positions]

        self.create_new_tetromino = create_new_tetromino

    def movedown(self):
        if not self.next_move_vertical_collide(self.blocks, 1):
            for block in self.blocks:
                block.pos.y += 1

        else:
            if not game.game_over:
                self.creating_new = True
                for block in self.blocks:
                    self.field_data[int(block.pos.y)][int(block.pos.x)] = block

                    if block.pos.y < 0:
                        game.game_over = True

                self.create_new_tetromino()
                self.creating_new = False
        
    def move_horizontal(self, amount):
        if not self.next_move_horizontal_collide(self.blocks, amount):
            for block in self.blocks:
                block.pos.x += amount

    def next_move_horizontal_collide(self, blocks, amount):
        collision_list = [block.horizontal_collide(int(block.pos.x + amount), self.field_data) for block in blocks]
        return True if any(collision_list) else False
    
    def next_move_vertical_collide(self, blocks, amount):
        collision_list = [block.vertical_collide(int(block.pos.y + amount), self.field_data) for block in blocks]
        return True if any(collision_list) else False
    
    def rotate(self):
        if self.shape != 'O':

            pivot_pos = self.blocks[0].pos

            new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]

            for pos in new_block_positions:

                if pos.x < 0 or pos.x >= COLS:
                    return
                
                if self.field_data[int(pos.y)][int(pos.x)]:
                    return
                
                if pos.y > ROWS:
                    return

            for i, block in enumerate(self.blocks):
                block.pos = new_block_positions[i]

class PreviewTetromino:
    def __init__(self, shape):
        self.block_positions = TETROMINOS[shape]['shape']
        self.color = TETROMINOS[shape]['color']

        self.group = pygame.sprite.Group()

        self.shape = shape

        self.blocks = [Block(self.group, pos, self.color) for pos in self.block_positions]

    def update(self):
        for block in self.blocks:
            game.panel.surface.blit(block.image, (block.rect.centerx - 120, block.rect.centery + 140))

game = Game()

pause_timer = pygame.time.get_ticks()
pause_allow = True

run = True
while run:
    screen.fill('grey')

    game.update()
    game.panel.update()
    game.score.update()

    title = font.render('Tetris', False, DARK_GREY)
    screen.blit(title, (160, 15))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN and pause_allow:
            if event.key == pygame.K_p:
                pause_allow = False
                game.paused = not game.paused
                print(game.paused)

    if not pause_allow:
        if pygame.time.get_ticks() - pause_timer >= 400:
            pause_allow = True
            pause_timer = pygame.time.get_ticks()

    pygame.display.update()

pygame.quit()
