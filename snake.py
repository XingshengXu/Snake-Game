from random import randint
from sys import exit
import pygame as pg


# Game Dimensions
WIDTH, HEIGHT = 800, 800
GRID_WIDTH = 40
ROW_NUMBER = WIDTH // GRID_WIDTH

# Game Timer
REACTION_TIME = 100
DELAY_TIME = 4000

# FPS, Directions, and Moving Speed
FPS = 30
MOVING_SPEED = GRID_WIDTH
UP, DOWN, LEFT, RIGHT = range(4)
DIRECTIONS = {
    UP: (0, -MOVING_SPEED),
    DOWN: (0, MOVING_SPEED),
    LEFT: (-MOVING_SPEED, 0),
    RIGHT: (MOVING_SPEED, 0),
}

# Image Path
GRASS_BACKGROUND = 'assets/image/grass.png'

SNAKE_HEAD = ['assets/image/head_up.png', 'assets/image/head_down.png',
              'assets/image/head_left.png', 'assets/image/head_right.png']

SNAKE_BODY = 'assets/image/body.png'
FOOD = 'assets/image/food.png'

# Sound Path
BITE_SOUND = 'assets/sound/apple_bite.ogg'
HIT_SOUND = 'assets/sound/hit.mp3'

# Music Path
MUSIC = 'assets/sound/snake_bgm.mp3'

# Game Events
SNAKE_GROW = pg.USEREVENT + 1
SNAKE_HIT = pg.USEREVENT + 2


class Snake(pg.sprite.Sprite):
    '''This class represents the snake object in the game.'''

    def __init__(self, idx=0, ishead=True, position=None, direction=LEFT):
        super().__init__()
        self.dir = direction
        self.ishead = ishead
        self.idx = idx
        self.prev_pos = position
        self.prev_dir = direction

        # Load and Transform Snake Head and Body Image
        if self.ishead:
            self.head_image = {}
            for i in range(len(SNAKE_HEAD)):
                head_image = pg.image.load(SNAKE_HEAD[i]).convert_alpha()
                head_image = pg.transform.scale(
                    head_image, (GRID_WIDTH, GRID_WIDTH))
                self.head_image[i] = head_image
            self.image = self.head_image[LEFT]
        else:
            body_image = pg.image.load(SNAKE_BODY).convert_alpha()
            self.image = pg.transform.scale(
                body_image, (GRID_WIDTH, GRID_WIDTH))

        if position is None:
            position = (WIDTH // 2, HEIGHT // 2)
        self.rect = self.image.get_rect(topleft=position)

    def move(self):
        '''Move the snake in the specified direction, updating its position accordingly. 
        The head's direction can be updated by arrow key inputs, and the body parts follow 
        the head and preceding body parts.'''
        if self.ishead:
            # Store the previous direction and position of the head
            self.prev_dir = self.dir
            self.prev_pos = self.rect.topleft
            # Check for arrow key events and update the snake's direction accordingly
            key = pg.key.get_pressed()
            if key[pg.K_UP] and self.dir != DOWN:
                self.dir = UP
                self.image = self.head_image[UP]
            elif key[pg.K_DOWN] and self.dir != UP:
                self.dir = DOWN
                self.image = self.head_image[DOWN]
            elif key[pg.K_LEFT] and self.dir != RIGHT:
                self.dir = LEFT
                self.image = self.head_image[LEFT]
            elif key[pg.K_RIGHT] and self.dir != LEFT:
                self.dir = RIGHT
                self.image = self.head_image[RIGHT]

            # Get the x and y offsets for the current direction
            offset_x, offset_y = DIRECTIONS[self.dir]

            # Update the position of the snake's head
            self.rect.x = (self.rect.x + offset_x) % WIDTH
            self.rect.y = (self.rect.y + offset_y) % HEIGHT
        else:
            # Store the current position of the body part before updating
            temp_pos = self.rect.topleft
            temp_dir = self.dir

            # Update the position of the snake's body part to the previous position of the preceding part
            prev_body = snake.sprites()[self.idx - 1]
            self.rect.topleft = prev_body.prev_pos
            self.dir = prev_body.prev_dir

            # Update the previous position of the body part
            self.prev_pos = temp_pos
            self.prev_dir = temp_dir

    def update(self):
        self.move()


class Food(pg.sprite.Sprite):
    '''It represents the food object in the game.'''

    def __init__(self):
        super().__init__()

        # Load Food Image
        food_image = pg.image.load(FOOD).convert_alpha()
        self.image = pg.transform.scale(food_image, (GRID_WIDTH, GRID_WIDTH))
        self.rect = self.image.get_rect(topleft=self.food_spawn())

    def food_spawn(self):
        '''Generate a random position for the food.'''

        while True:
            food_x = randint(0, ROW_NUMBER - 1) * GRID_WIDTH
            food_y = randint(0, ROW_NUMBER - 1) * GRID_WIDTH
            food_position = (food_x, food_y)

            # Check if the food_position is not part of the snake's body
            if all(body.rect.topleft != food_position for body in snake.sprites()):
                return food_position


class Game:
    '''It initializes the game window, clock, and the Pygame library. 
    It loads and plays background music, as well as the bite and hit sound effects. 
    It also draws the grid, grass background, and score text.'''

    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.game_message = ''
        self.font = pg.font.SysFont('comicsans', 30)  # Message Font
        pg.display.set_caption('Snake Game')

        # Load Background Images
        self.grass_background = pg.image.load(GRASS_BACKGROUND).convert()
        self.grass_background = pg.transform.scale(
            self.grass_background, (GRID_WIDTH, GRID_WIDTH))

        # Load Game Music
        pg.mixer.music.load(MUSIC)
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(loops=-1)

        # Load Sound Effect
        self.bite_sound = pg.mixer.Sound(BITE_SOUND)
        self.hit_sound = pg.mixer.Sound(HIT_SOUND)

    def draw_grid(self):
        '''Draw grid on screen.'''
        x, y = 0, 0
        for _ in range(ROW_NUMBER):
            x = x + GRID_WIDTH
            y = y + GRID_WIDTH

            pg.draw.line(self.screen, 'black', (x, 0), (x, HEIGHT))
            pg.draw.line(self.screen, 'black', (0, y), (WIDTH, y))

    def draw_grass(self):
        '''Draw grass on screen.'''
        for x in range(0, WIDTH, GRID_WIDTH):
            for y in range(0, HEIGHT, GRID_WIDTH):
                self.screen.blit(self.grass_background, (x, y))

    def draw_score(self, text):
        '''Draws the score message on the game display.'''
        draw_text = self.font.render(text, False, 'red')
        self.screen.blit(draw_text, (WIDTH//2 - draw_text.get_width() //
                                     2, HEIGHT//2 - draw_text.get_height()//2))
        pg.display.update()

    def snake_grow(self):
        '''Extend the length of the snake by adding a new body part.'''
        last_body = snake.sprites()[-1]
        idx = last_body.idx
        pos_x, pos_y = last_body.rect.topleft
        newbody_location = {
            UP: (pos_x, pos_y + GRID_WIDTH),
            DOWN: (pos_x, pos_y - GRID_WIDTH),
            LEFT: (pos_x + GRID_WIDTH, pos_y),
            RIGHT: (pos_x - GRID_WIDTH, pos_y),
        }
        snake.add(Snake(idx=idx + 1, ishead=False,
                  position=newbody_location[last_body.dir], direction=last_body.dir))

    def collision(self):
        '''Handle collisions between the snake and food or 
        between the snake's head and its body.'''
        # Collision with Itself
        head = snake.sprites()[0]
        body = snake.sprites()[1:]
        if pg.sprite.spritecollide(head, body, False):
            self.hit_sound.play()
            pg.event.post(pg.event.Event(SNAKE_HIT))

        # Collision with Food
        if pg.sprite.spritecollide(food.sprite, snake, False):
            self.bite_sound.play()
            pg.event.post(pg.event.Event(SNAKE_GROW))
            food.empty()
            food.add(Food())

    def handle_events(self):
        '''Process Pygame events, including quitting the game, 
        collisions, and snake growth.'''
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == SNAKE_HIT:
                self.game_message = f'Game Over! Wow, the snake length is {len(snake.sprites())}!'
                self.draw_score(self.game_message)
                pg.time.delay(DELAY_TIME)
                self.game_message = ''
                snake.empty()
                food.empty()
                snake.add(Snake())
                food.add(Food())

            if event.type == SNAKE_GROW:
                self.snake_grow()

    def main_loop(self):
        while True:
            pg.time.delay(REACTION_TIME)  # Delay for User Reaction
            self.clock.tick(FPS)

            # Handle Events
            self.handle_events()

            # Display Game Backgrounds and Objects
            self.draw_grass()
            self.draw_grid()

            snake.draw(self.screen)
            food.draw(self.screen)

            # Update Sprites
            snake.update()
            food.update()

            self.collision()
            pg.display.update()


# Create Class Instances and Add Sprites
game = Game()
snake = pg.sprite.Group()
snake.add(Snake())

food = pg.sprite.GroupSingle()
food.add(Food())

# Run Main Loop
game.main_loop()
