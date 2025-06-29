import pygame, sys, random, json, os

pygame.init()
pygame.mixer.init()

EAT_SOUND = pygame.mixer.Sound("eat.wav")
POWERUP_SOUND = pygame.mixer.Sound("powerup.wav")
GAMEOVER_SOUND = pygame.mixer.Sound("gameover.wav")


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
    
    def draw(self, screen, skin_colors):
        for i, segment in enumerate(self.body):
            if i == 0:
                color = skin_colors['head']
            else:
                color = skin_colors['body']
            
            pygame.draw.rect(screen, color, (segment[0]*GRID_SIZE, segment[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BLACK, (segment[0]*GRID_SIZE, segment[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)


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
        self.options = ["Easy", "Medium", "Hard", "AI Snake", "Time Mode", "Snake Skins", "Quit"]
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
        self.level = None
        self.spawn_food()
        self.frame_count = 0
        self.ai_snake = None
        self.ai_score = 0

        self.invincible_timer = 0
        self.double_points_timer = 0
        self.slow_timer = 0

        self.time_mode = False
        self.game_start_time = 0
        self.time_bonus = 0
        self.speed_increase_timer = 0
        self.update_counter = 0

        self.snake_skins = {
            "default": {"head": GREEN, "body": (0,200,0)},
            "fire": {"head": (255,100,0), "body": (255, 50, 0)},
            "ice": {"head": (100, 200, 255), "body": (50, 150, 255)},
            "gold": {"head": (255, 215, 0), "body": (255, 200, 0)}
        }
        self.current_skin = "default"
    
    def start_time_mode(self):
        self.time_mode = True
        self.game_start_time = pygame.time.get_ticks()
        self.speed_increase_timer = 0
        self.base_speed = 10

    def countdown(self):
        for i in range(3,0,-1):
            self.screen.fill(BLACK)
            text = self.font.render(str(i), True, YELLOW)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - text.get_height()//2))
            pygame.display.flip()
            pygame.time.delay(700)
        self.screen.fill(BLACK)
        text = self.font.render("GO!", True, GREEN)
        self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - text.get_height()//2))
        pygame.display.flip()
        pygame.time.delay(500)
    
    def set_level_settings(self):
        if self.level == "ai":
            self.base_speed = 10
            self.game_speed = 10
            self.obstacles = []
            self.ai_snake = Snake(GRID_WIDTH//2, GRID_HEIGHT//2-5)
        else:
            self.ai_snake = None

        if self.level == "easy":
            self.base_speed = 5
            self.game_speed = 5
            self.obstacles = []
        elif self.level == "medium":
            self.base_speed = 10
            self.game_speed = 10
            self.obstacles = []
        elif self.level == "hard":
            self.base_speed = 15
            self.game_speed = 15
            self.generate_obstacles()

    
    def generate_obstacles(self):
        self.obstacles = []
        for _ in range(5):
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
        if self.level =="hard" or self.level == "medium":
            food_count = 3
        else:
            food_count = 1
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
        if self.level == "medium":
            chance = 0.05
        else:
            chance = 0.1
        if random.random() <chance:
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
            self.slow_timer = now

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
                self.update()
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
                        self.time_mode = False
                        self.set_level_settings()
                        self.reset()
                        self.countdown()
                        self.state = "playing"
                    elif self.menu.selected == 1:
                        self.level = "medium"
                        self.time_mode = False
                        self.set_level_settings()
                        self.reset()
                        self.countdown()
                        self.state = "playing"
                    elif self.menu.selected == 2:
                        self.level = "hard"
                        self.time_mode = False
                        self.set_level_settings()
                        self.reset()
                        self.countdown()
                        self.state = "playing"
                    elif self.menu.selected == 3:
                        self.level = "ai"
                        self.time_mode = False
                        self.reset()
                        self.countdown()
                        self.state = "playing"
                    elif self.menu.selected == 4:  # Time Mode
                        self.level = "easy"
                        self.time_mode = True
                        self.game_start_time = pygame.time.get_ticks()
                        self.speed_increase_timer = 0
                        self.base_speed = 10
                        self.set_level_settings()
                        self.reset()
                        self.countdown()
                        self.state = "playing"
                    elif self.menu.selected == 5:  # Snake Skins
                        self.show_skin_selector()
                    elif self.menu.selected == 6:  # Quit
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
        if self.time_mode:
            current_time = pygame.time.get_ticks()
            elapsed_seconds = (current_time - self.game_start_time) // 1000

            if elapsed_seconds > self.speed_increase_timer + 30:
                self.speed_increase_timer = elapsed_seconds
                self.base_speed += 2

            current_speed = min(self.base_speed + (elapsed_seconds // 30) *2, 30)

            if self.update_counter >= 60 // current_speed:
                self.update_counter = 0
            else:
                self.update_counter += 1
                return  # Don't update game logic if not time to move
        else:
            if self.update_counter >= 60 // self.game_speed:
                self.update_counter = 0
            else:
                self.update_counter += 1
                return  # Don't update game logic if not time to move

        head_x, head_y = self.snake.body[0]
        dx, dy = self.snake.direction
        new_head = (head_x + dx, head_y + dy)

        if self.level == "ai" and self.ai_snake:
            head_x, head_y = self.ai_snake.body[0]
            dx = 1 if self.food.x > head_x else -1 if self.food.x < head_x else 0
            dy = 1 if self.food.y > head_y else -1 if self.food.y < head_y else 0
            
            if abs(self.food.x - head_x) > abs(self.food.y -head_y):
                self.ai_snake.set_direction(dx,0)
            else:
                self.ai_snake.set_direction(0,dy)
            self.ai_snake.move(wrap=True)

        if self.level == "hard" and new_head in self.obstacles:
            if not self.invincible:
                self.state = "game_over"
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                return
        wrap = self.level == "easy"
        if not wrap:
            if (new_head[0] <0 or new_head[0] >= GRID_WIDTH or new_head[1] <0 or new_head[1] >= GRID_HEIGHT):
                self.state = "game_over"
                if self.score >self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                return
        self.snake.move(wrap=wrap)
        self.update_power_ups()
        self.spawn_power_up()

        if self.snake.collides_with((self.food.x, self.food.y)):
            pygame.mixer.Sound.play(EAT_SOUND)
            self.snake.grow = True
            if self.food.type == "regular":
                self.score += 1 *(2 if self.double_points else 1)
            elif self.food.type == "golden":
                self.score += 5 *(2 if self.double_points else 1)
            elif self.food.type == "speed":
                self.game_speed += 5
            elif self.food.type == "power":
                self.invincible = True
                self.invincible_timer = pygame.time.get_ticks()
            self.spawn_food()
        
        if self.level == "ai" and self.ai_snake:
            if self.ai_snake.collides_with((self.food.x, self.food.y)):
                self.ai_snake.grow = True
                self.ai_score += 1
                self.spawn_food()
            

        for power_up in self.power_ups[:]:
            if self.snake.collides_with((power_up.x, power_up.y)):
                pygame.mixer.Sound.play(POWERUP_SOUND)
                self.handle_power_ups(power_up)
                self.power_ups.remove(power_up)

        if self.snake.collides_with_self() and not self.invincible:
            pygame.mixer.Sound.play(GAMEOVER_SOUND)
            self.state = "game_over"
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
        
        if self.level == "ai" and self.ai_snake:
            if self.snake.body[0] in self.ai_snake.body:
                pygame.mixer.Sound.play(GAMEOVER_SOUND)
                self.state = "game_over"
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                return
    

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x,0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0,y), (SCREEN_WIDTH, y))
    
    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()

        if self.level == "hard":
            for (x, y) in self.obstacles:
                pygame.draw.rect(self.screen, (251, 118, 255), (x*GRID_SIZE, y*GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        # Draw snake using skin system
        self.snake.draw(self.screen, self.snake_skins[self.current_skin])
        
        if self.level == "ai" and self.ai_snake:
            for i, (x,y) in enumerate(self.ai_snake.body):
                color = (255, 100, 100) if i == 0 else (200, 200, 200)
                pygame.draw.rect(self.screen, color, (x*GRID_SIZE, y*GRID_SIZE, GRID_SIZE, GRID_SIZE))
            
        self.food.draw(self.screen)

        if self.time_mode:
            current_time = pygame.time.get_ticks()
            elapsed_seconds = (current_time - self.game_start_time) // 1000
            time_bonus = elapsed_seconds * 10

            score_text = f"Score: {self.score + time_bonus}"
            time_text = f"Time: {elapsed_seconds}s"
            speed_text = f"Speed: {min(self.base_speed + (elapsed_seconds //30) *2, 30)}"

            score_surface = self.font.render(score_text, True, WHITE)
            time_surface = self.small_font.render(time_text, True, WHITE)
            speed_surface = self.small_font.render(speed_text, True, WHITE)

            self.screen.blit(score_surface,(10,10))
            self.screen.blit(time_surface, (10,40))
            self.screen.blit(speed_surface, (10, 70))
        else:
            score_text = f"Score: {self.score}"
            score_surface = self.font.render(score_text, True, WHITE)
            self.screen.blit(score_surface, (10, 10))

        for power_up in self.power_ups:
            power_up.draw(self.screen)
            
        high_score_text = self.small_font.render(f"High Score: {self.high_score}", True, YELLOW)
        self.screen.blit(high_score_text, (10,50))

        if self.level == "ai":
            ai_score_text = self.small_font.render(f"AI Score: {self.ai_score}", True, (255, 100, 100))
            self.screen.blit(ai_score_text, (10,90))

        bar_width = 150
        bar_height = 15
        bar_y = 80
        now = pygame.time.get_ticks()

        if self.invincible:
            time_left = max(0, self.power_up_duration - (now - self.invincible_timer))
            width = int(bar_width * (time_left / self.power_up_duration))
            pygame.draw.rect(self.screen, ORANGE, (SCREEN_WIDTH - bar_width - 20, bar_y, width, bar_height))
            label = self.small_font.render("Invincible", True, ORANGE)
            self.screen.blit(label, (SCREEN_WIDTH - bar_width - 20, bar_y -20))
            bar_y += 40
        if self.double_points:
            time_left = max(0, self.power_up_duration -(now - self.double_points_timer))
            width = int(bar_width * (time_left / self.power_up_duration))
            pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - bar_width - 20, bar_y, width, bar_height))
            label = self.small_font.render("Double points", True, GREEN)
            self.screen.blit(label, (SCREEN_WIDTH - bar_width - 20, bar_y - 20))
            bar_y += 40
        if self.game_speed != self.base_speed:
            time_left = max(0, self.power_up_duration - (now-self.slow_timer))
            width = int(bar_width * (time_left / self.power_up_duration))
            pygame.draw.rect(self.screen, GRAY, (SCREEN_WIDTH - bar_width - 20, bar_y, width, bar_height))
            label = self.small_font.render("Slow", True, GRAY)
            self.screen.blit(label, (SCREEN_WIDTH - bar_width - 20, bar_y -20))
            bar_y += 40


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

        if self.level == "ai":
            ai_score_text = self.font.render(f"AI Score: {self.ai_score}", True, (255, 100, 100))
            self.screen.blit(ai_score_text, (SCREEN_WIDTH//2 - ai_score_text.get_width()//2, 360))

            if self.ai_snake is None or self.state == "game_over":
                if self.score > self.ai_score:
                    winner = "YOU WON!!"
                elif self.score < self.ai_score:
                    winner = "you lost..."
                else:
                    winner = "Tie?!?!"
                winner_text = self.font.render(winner, True, YELLOW)
                self.screen.blit(winner_text, (SCREEN_WIDTH//2 - winner_text.get_width()//2, 400))

        prompt = self.small_font.render("Press Enter to return to menu", True, GRAY)          
        self.screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, 440))
    
    def show_skin_selector(self):
        import tkinter as tk
        from tkinter import colorchooser

        selector_window = tk.Tk()
        selector_window.title("Snake skin selector")
        selector_window.geometry("400x300")

        title_label = tk.Label(selector_window, text="Choose your snake skin", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        for skin_name in self.snake_skins.keys():
            skin_frame = tk.Frame(selector_window)
            skin_frame.pack(pady=5)

            preview_canvas = tk.Canvas(skin_frame, width=60, height=20, bg="black")
            preview_canvas.pack(side=tk.LEFT, padx=10)

            head_color = self.snake_skins[skin_name]["head"]
            body_color = self.snake_skins[skin_name]['body']

            preview_canvas.create_oval(5,5,15,15, fill=f"#{head_color[0]:02x}{head_color[1]:02x}{head_color[2]:02x}")
            preview_canvas.create_oval(20,5,30,15, fill=f"#{body_color[0]:02x}{body_color[1]:02x}{body_color[2]:02x}")
            preview_canvas.create_oval(35,5,45,15, fill=f"#{body_color[0]:02x}{body_color[1]:02x}{body_color[2]:02x}")

            tk.Button(skin_frame, text=skin_name.title(), command=lambda s=skin_name: self.select_skin(s,selector_window)).pack(side=tk.LEFT, padx=10)

        selector_window.mainloop()
    def select_skin(self, skin_name, window):
        self.current_skin = skin_name
        window.destroy()
        self.reset()
    
    def reset(self):
        self.score = 0
        self.ai_score = 0
        self.snake = Snake(GRID_WIDTH//2, GRID_HEIGHT//2)
        self.food = Food()
        self.power_ups = []
        self.game_speed = self.base_speed
        self.invincible = False
        self.double_points = False

        self.invincible_timer = 0
        self.double_points_timer = 0
        self.slow_timer = 0

        if self.level == "hard":
            self.generate_obstacles()
        else:
            self.obstacles = []
        self.spawn_food()

        if self.level == "ai":
            self.ai_snake = Snake(GRID_WIDTH//2, GRID_HEIGHT//2-5)
        else:
            self.ai_snake = None
            
if __name__ == "__main__":
    game = Game() 
    game.run() 
