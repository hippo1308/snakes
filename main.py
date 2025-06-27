import pygame, sys, random, json, os
#IMPORT THE REST LATER

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH//GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT//GRID_SIZE

BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
BLUE =(0,0,255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 265, 0)
GRAY = (128, 128, 128)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("snakes")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.state = "menu"
        self. score = 0
        self.high_score = self.load_high_score()

        self.snake = Snake(GRID_WIDTH//2, GRID_HEIGHT)
        self.food = Food()
        self. power_ups = []

        self.game_speed = 10
        self.base_speed = 10
        self.power_up_duration = 5000
        self.power_up_timer = 0

        self.speed_boost = False
        self.invincible = False
        self.double_points = False

        self.menu = Menu()
        self.spawn_food()

    def load_high_score(self):

        try:
            if os.path.exists('high_score.json'):
                with open('high_score.json', 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    def save_high_score(self):
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass

    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH-1)
            y = random.randint(0, GRID_HEIGHT-1)

            if (x,y) not in self.snake.body:
                self.food.x = x
                self.food.y = y
                self.food.type = random.choice(['regular', 'golden', 'speed', 'power'])
                break

    def spawn_power_up(self):
        if random.random() <0.1:
            while True:
                x = random.randint(0, GRID_WIDTH-1)
                y = random.randint(0, GRID_HEIGHT-1)

                if (x,y) not in self.snake.body and (x,y) != (self.food.x, self.food.y):
                    power_up = PowerUp(x,y)
                    self.power_ups.append
