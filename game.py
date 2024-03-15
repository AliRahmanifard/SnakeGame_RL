import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

Point = namedtuple('Point', 'x, y')


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


class SnakeGameAI:
    def __init__(self, width=640, height=480, block_size=20, speed=10, has_ui=True):
        self.w = width
        self.h = height
        self.BLOCK_SIZE = block_size
        self.SPEED = speed
        self.ui = has_ui
        # init display
        if self.ui:
            pygame.init()
            self.display = pygame.display.set_mode((self.w, self.h))
            pygame.display.set_caption('Snake Game')
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont('arial', 25)

            # Load images
            self.food_img = pygame.image.load('Resources/apple.png').convert_alpha()
            self.food_img = pygame.transform.scale(self.food_img, (self.BLOCK_SIZE, self.BLOCK_SIZE))

            self.snake_head_img = pygame.image.load('Resources/snake_head.png').convert_alpha()
            self.snake_head_img = pygame.transform.scale(self.snake_head_img, (self.BLOCK_SIZE, self.BLOCK_SIZE))

            self.snake_body_img = pygame.image.load('Resources/snake_body.png').convert_alpha()
            self.snake_body_img = pygame.transform.scale(self.snake_body_img, (self.BLOCK_SIZE, self.BLOCK_SIZE))

            self.snake_curve_img = pygame.image.load('Resources/snake_curve.png').convert_alpha()
            self.snake_curve_img = pygame.transform.scale(self.snake_curve_img, (self.BLOCK_SIZE, self.BLOCK_SIZE))

            self.snake_tail_img = pygame.image.load('Resources/snake_tail.png').convert_alpha()
            self.snake_tail_img = pygame.transform.scale(self.snake_tail_img, (self.BLOCK_SIZE, self.BLOCK_SIZE))

        self.reset()

    def reset(self):
        # init game state
        self.direction = random.choice([Direction.RIGHT, Direction.UP, Direction.DOWN])

        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - self.BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * self.BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0, (self.w - self.BLOCK_SIZE) // self.BLOCK_SIZE) * self.BLOCK_SIZE
        y = random.randint(0, (self.h - self.BLOCK_SIZE) // self.BLOCK_SIZE) * self.BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        if self.ui:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

        # 2. move
        self._move(action)  # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        # 5. update ui and clock
        if self.ui:
            self._update_ui()
            self.clock.tick(self.SPEED)
        # 6. return game over and score
        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        # if pt.x > self.w-BLOCK_SIZE or pt.x < 0 or pt.y > self.h-BLOCK_SIZE or pt.y < 0:
        #     return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        self.display.fill(pygame.color.THECOLORS['lightskyblue'])

        # Draw snake head
        snake_head_rect = pygame.Rect(self.snake[0].x, self.snake[0].y, self.BLOCK_SIZE, self.BLOCK_SIZE)
        match self.direction:
            case Direction.RIGHT:
                self.display.blit(self.snake_head_img, snake_head_rect)
            case Direction.UP:
                self.display.blit(pygame.transform.rotate(self.snake_head_img, 90), snake_head_rect)
            case Direction.LEFT:
                self.display.blit(pygame.transform.rotate(self.snake_head_img, 180), snake_head_rect)
            case Direction.DOWN:
                self.display.blit(pygame.transform.rotate(self.snake_head_img, 270), snake_head_rect)

        # Draw snake body
        for b in range(1, len(self.snake) - 1):
            x_avg = (self.snake[b - 1].x + self.snake[b + 1].x) / 2
            y_avg = (self.snake[b - 1].y + self.snake[b + 1].y) / 2
            snake_body_rect = pygame.Rect(self.snake[b].x, self.snake[b].y, self.BLOCK_SIZE, self.BLOCK_SIZE)
            if (self.snake[b - 1].y == self.snake[b].y) and (self.snake[b].y == self.snake[b + 1].y):
                self.display.blit(self.snake_body_img, snake_body_rect)
            elif (self.snake[b - 1].x == self.snake[b].x) and (self.snake[b].x == self.snake[b + 1].x):
                self.display.blit(pygame.transform.rotate(self.snake_body_img, 90), snake_body_rect)
            elif (x_avg < self.snake[b].x) and (y_avg < self.snake[b].y):
                if self.snake[b].y - y_avg > self.BLOCK_SIZE:
                    self.display.blit(pygame.transform.rotate(self.snake_curve_img, 90), snake_body_rect)
                elif self.snake[b].x - x_avg > self.BLOCK_SIZE:
                    self.display.blit(pygame.transform.rotate(self.snake_curve_img, 270), snake_body_rect)
                else:
                    self.display.blit(self.snake_curve_img, snake_body_rect)
            elif (x_avg < self.snake[b].x) and (y_avg > self.snake[b].y):
                if y_avg - self.snake[b].y > self.BLOCK_SIZE:
                    self.display.blit(self.snake_curve_img, snake_body_rect)
                elif self.snake[b].x - x_avg > self.BLOCK_SIZE:
                    self.display.blit(pygame.transform.rotate(self.snake_curve_img, 180), snake_body_rect)
                else:
                    self.display.blit(pygame.transform.rotate(self.snake_curve_img, 90), snake_body_rect)
            elif (x_avg > self.snake[b].x) and (y_avg > self.snake[b].y):
                if y_avg - self.snake[b].y > self.BLOCK_SIZE:
                    self.display.blit(pygame.transform.rotate(self.snake_curve_img, 270), snake_body_rect)
                elif x_avg - self.snake[b].x > self.BLOCK_SIZE:
                    self.display.blit(pygame.transform.rotate(self.snake_curve_img, 90), snake_body_rect)
                else:
                    self.display.blit(pygame.transform.rotate(self.snake_curve_img, 180), snake_body_rect)
            elif (x_avg > self.snake[b].x) and (y_avg < self.snake[b].y):
                if self.snake[b].y - y_avg > self.BLOCK_SIZE:
                    self.display.blit(pygame.transform.rotate(self.snake_curve_img, 180), snake_body_rect)
                elif x_avg - self.snake[b].x > self.BLOCK_SIZE:
                    self.display.blit(self.snake_curve_img, snake_body_rect)
                else:
                    self.display.blit(pygame.transform.rotate(self.snake_curve_img, 270), snake_body_rect)

        # Draw snake tail
        snake_tail_rect = pygame.Rect(self.snake[-1].x, self.snake[-1].y, self.BLOCK_SIZE, self.BLOCK_SIZE)
        if (self.snake[-1].x < self.snake[-2].x) and (self.snake[-1].y == self.snake[-2].y):
            if self.snake[-2].x - self.snake[-1].x > self.BLOCK_SIZE:
                self.display.blit(pygame.transform.rotate(self.snake_tail_img, 180), snake_tail_rect)
            else:
                self.display.blit(self.snake_tail_img, snake_tail_rect)
        elif (self.snake[-1].x == self.snake[-2].x) and (self.snake[-1].y > self.snake[-2].y):
            if self.snake[-1].y - self.snake[-2].y > self.BLOCK_SIZE:
                self.display.blit(pygame.transform.rotate(self.snake_tail_img, 270), snake_tail_rect)
            else:
                self.display.blit(pygame.transform.rotate(self.snake_tail_img, 90), snake_tail_rect)
        elif (self.snake[-1].x > self.snake[-2].x) and (self.snake[-1].y == self.snake[-2].y):
            if self.snake[-1].x - self.snake[-2].x > self.BLOCK_SIZE:
                self.display.blit(self.snake_tail_img, snake_tail_rect)
            else:
                self.display.blit(pygame.transform.rotate(self.snake_tail_img, 180), snake_tail_rect)
        elif (self.snake[-1].x == self.snake[-2].x) and (self.snake[-1].y < self.snake[-2].y):
            if self.snake[-2].y - self.snake[-1].y > self.BLOCK_SIZE:
                self.display.blit(pygame.transform.rotate(self.snake_tail_img, 90), snake_tail_rect)
            else:
                self.display.blit(pygame.transform.rotate(self.snake_tail_img, 270), snake_tail_rect)

        # Draw food
        food_rect = pygame.Rect(self.food.x, self.food.y, self.BLOCK_SIZE, self.BLOCK_SIZE)
        self.display.blit(self.food_img, food_rect)

        # Draw score
        text = self.font.render("Score: " + str(self.score), True, (255, 255, 255))
        self.display.blit(text, [0, 0])

        # Update the full display surface
        pygame.display.flip()

    def _move(self, action):
        # action is in this form: [straight, right, left]
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # going straight
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # right turn (R -> D -> L -> U)
        elif np.array_equal(action, [0, 0, 1]):
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # left turn (R -> U -> L -> D)

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += self.BLOCK_SIZE
            if x >= self.w:
                x = 0
        elif self.direction == Direction.LEFT:
            x -= self.BLOCK_SIZE
            if x < 0:
                x = self.w - self.BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += self.BLOCK_SIZE
            if y >= self.h:
                y = 0
        elif self.direction == Direction.UP:
            y -= self.BLOCK_SIZE
            if y < 0:
                y = self.h - self.BLOCK_SIZE

        self.head = Point(x, y)
