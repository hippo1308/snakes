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
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

class Snake:
    def __init__(self, x, y):
        self.body = [(x,y), (x-1, y), (x-2, y)]
        self.direction = (1, 0)
        self.grow = False

    def move(self, wrap=True):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        if wrap:
            new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)
        else:
            new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
    
    def set_direction(self, dx, dy):
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.direction = (dx, dy)
    
    def collides_with_self(self):
        return self.body[0] in self.body[1:]
    
    def collides_with(self, pos):
        return self.body[0] == pos

class Food:
    def __init__(self):
        self.x = random.randint(0, GRID_WIDTH-1)
        self.y = random.randint(0, GRID_HEIGHT-1)
        self.type = random.choice(['regular', 'golden', 'speed', 'power'])
    
    def draw(self, screen):
        color = RED
        if self.type == "golden":
            color = YELLOW
        elif self.type == "speed":
            color = BLUE
        elif self.type == "power":
            color = PURPLE
        pygame.draw.rect(screen, color, (self.x*GRID_SIZE, self.y*GRID_SIZE, GRID_SIZE, GRID_SIZE))

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(['invincible', 'double_points', 'slow'])
        self.active = False
    
    def draw(self, screen):
        if self.type == "invincible":
            color = ORANGE
        elif self.type == "slow":
            color = GRAY
        elif self.type == "double_points":
            color = GREEN
        pygame.draw.rect(screen, color, (self.x*GRID_SIZE, self.y*GRID_SIZE, GRID_SIZE, GRID_SIZE))

class Menu:
    def __init__(self):
        self.options = ["Easy", "Medium", "Hard", "Quit"]
        self.selected = 0

    
    def draw(self, screen, font):
        for i, option in enumerate(self.options):
            color = WHITE if i == self.selected else GRAY
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 200+i*50))
    
    def move_selection(self, direction):
        self.selected = (self.selected + direction) % len(self.options)

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
        self.obstacles = []

        self.game_speed = 10
        self.base_speed = 10
        self.power_up_duration = 5000
        self.power_up_timer = 0

        self.speed_boost = False
        self.invincible = False
        self.double_points = False

        self.menu = Menu()
        self.spawn_food()
        self.frame_count = 0
        self.level = None

        self.invincible_time = 0
        self.double_points_timer = 0
        self.slow_timer = 0
    
    def set_level_settings(self):
        if self.level == "easy":
            self.base_speed = 10
            self.game_speed = 10
            self.obstacles = []
        elif self.level == "medium":
            self.base_speed = 15
            self.game_speed = 15
            self.obstacles = []
        elif self.level == "hard":
            self.base_speed = 20
            self.game_speed = 20
            self.generate_obstacles()
    
    def generate_obstacles(self):
        self.obstacles = []
        for _ in range(10):
            while True:
                x = random.randint(0, GRID_WIDTH-1)
                y = random.randint(0, GRID_HEIGHT-1)
                if (x, y) not in self.snake.body and (x, y) != (self.food.x, self.food.y):
                    self.obstacles.append((x, y))
                    break

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
        food_count = 3 if self.level == "hard" else 1
        for _ in range(food_count):
            while True:
                x = random.randint(0, GRID_WIDTH-1)
                y = random.randint(0, GRID_HEIGHT-1)

                if (x,y) not in self.snake.body and (x,y) not in getattr(self, 'obstacles', []):
                    self.food.x = x
                    self.food.y = y
                    if self.level == "easy":
                        self.food.type = "regular"
                    else:
                        self.food.type = random.choice(['regular', 'golden', 'speed', 'power'])
                    break

    def spawn_power_up(self):
        if self.level == "easy":
            return
        if random.random() <0.1:
            while True:
                x = random.randint(0, GRID_WIDTH-1)
                y = random.randint(0, GRID_HEIGHT-1)

                if (x,y) not in self.snake.body and (x,y) != (self.food.x, self.food.y):
                    power_up = PowerUp(x,y)
                    self.power_ups.append(power_up)
                    break
    
    def handle_power_ups(self, power_up):
        now = pygame.time.get_ticks()
        if power_up.type == 'invincible':
            self.invincible = True
            self.invincible_timer = now
        elif power_up.type == 'double_points':
            self.double_points_timer = now
            self.double_points = True
        elif power_up.type == 'slow':
            self.game_speed = max(5, self.base_speed -5)
            self.slow_time = now

    def update_power_ups(self):
        now = pygame.time.get_ticks()
        if self.invincible and now - self.invincible_timer > self.power_up_duration:
            self.invincible = False
        if self.double_points and now -self.double_points_timer > self.power_up_duration:
            self.double_points = False
        if self.game_speed != self.base_speed and now - self.slow_timer > self.power_up_duration:
            self.game_speed = self.base_speed

    def run(self):
        while True:
            if self.state == "menu":
                self.handle_menu_events()
                self.draw_menu()
            elif self.state == "playing":
                self.handle_game_events()
                self.frame_count += 1
                if self.frame_count >= self.game_speed:
                    self.update()
                    self.frame_count = 0
                self.draw()
            elif self.state == "game_over":
                self.handle_game_over_events()
                self.draw_game_over()
            pygame.display.flip()
            self.clock.tick(60)
    
    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.menu.move_selection(-1)
                elif event.key == pygame.K_DOWN:
                    self.menu.move_selection(1)
                elif event.key == pygame.K_RETURN:
                    if self.menu.selected == 0:
                        self.level = "easy"
                        self.set_level_settings()
                        self.reset()
                        self.state = "playing"
                    elif self.menu.selected == 1:
                        self.level = "medium"
                        self.set_level_settings()
                        self.reset()
                        self.state = "playing"
                    elif self.menu.selected == 2:
                        self.level = "hard"
                        self.set_level_settings()
                        self.reset()
                        self.state = "playing"
                    elif self.menu.selected == 3:
                        pygame.quit()
                        sys.exit()

        
    def handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.set_direction(0,-1)
                elif event.key == pygame.K_DOWN:
                    self.snake.set_direction(0,1)
                elif event.key == pygame.K_LEFT:
                    self.snake.set_direction(-1,0)
                elif event.key == pygame.K_RIGHT:
                    self.snake.set_direction(1,0)
        
    def handle_game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.state = "menu"
        
    def update(self):
        head_x, head_y = self.snake.body[0]
        dx, dy = self.snake.direction
        new_head = (head_x + dx, head_y + dy)

        if self.level in ["medium", "hard"]:
            if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
                if not self.invincible:
                    self.state = "game_over"
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
                        return
        wrap = self.level == "easy"
        self.snake.move(wrap=wrap)
        self.update_power_ups()
        self.spawn_power_up()

        if self.snake.collides_with((self.food.x, self.food.y)):
            self.snake.grow = True
            if self.food.type == "regular":
                self.score += 1 *(2 if self.double_points else 1)
            elif self.food.type == "golden":
                self.score += 5 *(2 if self.double_points else 1)
            elif self.food.type == "speed":
                self.game_speed += 5
            elif self.food.type == "power":
                self.invincible = True
                self.power_up_timer = pygame.time.get_ticks()
            self.spawn_food()

        for power_up in self.power_ups[:]:
            if self.snake.collides_with((power_up.x, power_up.y)):
                self.handle_power_ups(power_up)
                self.power_ups.remove(power_up)

        if self.snake.collides_with_self() and not self.invincible:
            self.state = "game_over"
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x,0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0,y), (SCREEN_WIDTH, y))
    
    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()

        for i, (x,y) in enumerate(self.snake.body):
            color = GREEN if i == 0 else WHITE
            pygame.draw.rect(self.screen, color, (x*GRID_SIZE, y*GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        self.food.draw(self.screen)

        for power_up in self.power_ups:
            power_up.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10,10))
        high_score_text = self.small_font.render(f"High Score: {self.high_score}", True, YELLOW)
        self.screen.blit(high_score_text, (10,50))

    def draw_menu(self):
        self.screen.fill(BLACK)
        title = self.font.render("Snake Game", True, GREEN)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        self.menu.draw(self.screen, self.font)
        
    def draw_game_over(self):
        self.screen.fill(BLACK)
        over_text = self.font.render("Game Over", True, RED)
        self.screen.blit(over_text, (SCREEN_WIDTH //2 - over_text.get_width()//2, 200))
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 260))
        high_score_text = self.small_font.render(f"High Score: {self.high_score}", True, YELLOW)
        self.screen.blit(high_score_text, (SCREEN_WIDTH//2 - high_score_text.get_width()//2, 320))
        prompt = self.small_font.render("Press Enter to return to menu", True, GRAY)          
        self.screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, 380))

    def reset(self):
        self.score = 0
        self.snake = Snake(GRID_WIDTH//2, GRID_HEIGHT//2)
        self.food = Food()
        self.power_ups = []
        self.game_speed = self.base_speed
        self.invincible = False
        self.double_points = False
if __name__ == "__main__":
    game = Game() 
    game.run() 
    