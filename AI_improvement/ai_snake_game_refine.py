import pygame
import random
import json

pygame.init()

class SnakeGame:
    def __init__(self):
        # Inicialización de variables
        self.screen_width, self.screen_height = 1280, 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.pixel_width = 50
        self.running = True
        self.difficulty = "Easy"
        self.speed_factor = 10
        self.snake_name = ""
        self.snake_color = (0, 255, 0)  # Color predeterminado: verde
        self.high_scores = []
        self.current_score = 0
        self.play_time = 0
        self.max_snake_length = 1
        self.items_collected = 0

        # Inicializar fuentes
        pygame.font.init()
        self.title_font = pygame.font.SysFont(None, 70)
        self.menu_font = pygame.font.SysFont(None, 50)
        self.text_font = pygame.font.SysFont(None, 30)

        # Inicialización de los obstáculos
        self.obstacles = [pygame.Rect(random.randint(0, self.screen_width // self.pixel_width - 1) * self.pixel_width,
                                       random.randint(0, self.screen_height // self.pixel_width - 1) * self.pixel_width,
                                       self.pixel_width, self.pixel_width) for _ in range(5)]

    def random_pos(self):
        return [random.randrange(0, self.screen_width, self.pixel_width) for _ in range(2)]

    def game_loop(self):
        # Inicializa la serpiente y el objetivo
        snake_pixel = pygame.Rect(0, 0, self.pixel_width - 2, self.pixel_width - 2)
        snake_pixel.center = self.random_pos()
        snake = [snake_pixel.copy()]
        snake_direction = (0, 0)
        snake_length = 1

        target = pygame.Rect(0, 0, self.pixel_width - 2, self.pixel_width - 2)
        target.center = self.random_pos()

        powerup = None
        powerup_spawn_time = 0
        powerup_color = None
        moving_powerup = None
        moving_powerup_spawned = False

        while self.running:
            self.play_time += 1 / self.speed_factor  # Incrementar el tiempo de juego

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # Actualizar la pantalla
            self.screen.fill("black")
            self.draw_text(f"Snake Name: {self.snake_name}", (10, 50))
            self.draw_text(f"Score: {self.current_score}", (10, 90))
            self.draw_text(f"Time: {int(self.play_time)} s", (10, 130))

            # Comprobaciones de colisión
            if snake_pixel.colliderect(target):
                target.center = self.random_pos()
                snake_length += 1
                self.items_collected += 1
                self.current_score += 1

                # Spawning power-ups
                if random.random() < 0.2:  # 20% de probabilidad de generar un power-up
                    powerup = self.create_powerup()
                    powerup_spawn_time = pygame.time.get_ticks()
                if random.random() < 0.1:  # 10% de probabilidad de generar un objeto que se mueve
                    moving_powerup = pygame.Rect(random.randint(0, self.screen_width // self.pixel_width - 1) * self.pixel_width,
                                                  random.randint(0, self.screen_height // self.pixel_width - 1) * self.pixel_width,
                                                  self.pixel_width, self.pixel_width)
                    moving_powerup_spawned = True

            if moving_powerup_spawned:
                # Mover el objeto rosado
                moving_powerup.x += random.choice([-self.pixel_width, 0, self.pixel_width])  # Mueve aleatoriamente
                moving_powerup.y += random.choice([-self.pixel_width, 0, self.pixel_width])

                # Comprobar límites
                if (moving_powerup.left < 0 or moving_powerup.right > self.screen_width or
                    moving_powerup.top < 0 or moving_powerup.bottom > self.screen_height):
                    moving_powerup_spawned = False

                # Comprobar colisión con el objeto rosado
                if snake_pixel.colliderect(moving_powerup):
                    powerup_color = "green"  # El siguiente objeto será verde
                    moving_powerup_spawned = False

            # Generar el siguiente objetivo (target)
            if powerup and pygame.time.get_ticks() - powerup_spawn_time > 5000:  # Desaparece después de 5 segundos
                powerup = None

            # Cambiar la dirección de la serpiente
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]: snake_direction = (0, -self.pixel_width)
            if keys[pygame.K_s]: snake_direction = (0, self.pixel_width)
            if keys[pygame.K_a]: snake_direction = (-self.pixel_width, 0)
            if keys[pygame.K_d]: snake_direction = (self.pixel_width, 0)

            # Mover la serpiente
            snake_pixel.move_ip(snake_direction)

            # Comprobar límites
            if (snake_pixel.left < 0 or snake_pixel.right > self.screen_width or
                snake_pixel.top < 0 or snake_pixel.bottom > self.screen_height or
                snake_pixel.collidelist(snake[1:]) != -1):  # Colisión con su propio cuerpo
                self.game_over()

            # Dibujar la serpiente
            snake.append(snake_pixel.copy())
            snake = snake[-snake_length:]

            for part in snake:
                pygame.draw.rect(self.screen, self.snake_color, part)
            pygame.draw.rect(self.screen, "red", target)

            # Dibujar power-up
            if powerup:
                pygame.draw.rect(self.screen, powerup_color, powerup)

            if moving_powerup_spawned:
                pygame.draw.rect(self.screen, "pink", moving_powerup)

            pygame.display.flip()
            self.clock.tick(self.speed_factor)

    def create_powerup(self):
        powerup_type = random.choice(["blue", "yellow", "white", "pink"])  # Elegir tipo de power-up
        return (pygame.Rect(0, 0, self.pixel_width - 2, self.pixel_width - 2), powerup_type)

    def handle_powerup(self, powerup):
        powerup_rect, color = powerup
        if color == "blue":
            self.speed_factor += 2  # Aumenta la velocidad
        elif color == "yellow":
            self.speed_factor -= 2  # Disminuye la velocidad
        elif color == "white":
            self.max_snake_length += 1  # Aumenta la longitud
        elif color == "pink":
            self.snake_color = (0, 255, 0)  # Cambiar a color verde (o lo que el usuario elija)

    def draw_text(self, text, position):
        rendered_text = self.menu_font.render(text, True, (255, 255, 255))
        self.screen.blit(rendered_text, position)

    def game_over(self):
        self.running = False
        self.save_high_score()
        self.show_game_over()

    def show_game_over(self):
        while not self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.show_menu()

            self.screen.fill("black")
            self.draw_text("GAME OVER", (self.screen_width // 2 - 150, self.screen_height // 2 - 50))
            self.draw_text(f"Final Score: {self.current_score}", (self.screen_width // 2 - 150, self.screen_height // 2))
            self.draw_text("Press Enter to go back to menu", (self.screen_width // 2 - 200, self.screen_height // 2 + 50))
            pygame.display.flip()
            self.clock.tick(10)

    def save_high_score(self):
        # Guardar puntuaciones altas
        with open("high_scores.json", "r") as file:
            self.high_scores = json.load(file)
        
        self.high_scores.append({"name": self.snake_name, "score": self.current_score, 
                                  "time": int(self.play_time), "max_length": self.max_snake_length, 
                                  "items_collected": self.items_collected})
        self.high_scores = sorted(self.high_scores, key=lambda x: x['score'], reverse=True)[:5]  # Mantener las 5 mejores puntuaciones
        
        with open("high_scores.json", "w") as file:
            json.dump(self.high_scores, file)

    def show_high_scores(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.show_menu()

            self.screen.fill("black")
            self.draw_text("High Scores", (self.screen_width // 2 - 100, 50))
            for i, score in enumerate(self.high_scores):
                self.draw_text(f"{i + 1}. {score['name']} - {score['score']} points", 
                               (self.screen_width // 2 - 150, 100 + i * 40))

            self.draw_text("Press ESC to go back", (self.screen_width // 2 - 150, self.screen_height - 50))
            pygame.display.flip()
            self.clock.tick(10)

    def show_statistics(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.show_menu()

            self.screen.fill("black")
            self.draw_text("Statistics", (self.screen_width // 2 - 100, 50))
            self.draw_text(f"Total Time Played: {int(self.play_time)} seconds", (self.screen_width // 2 - 150, 100))
            self.draw_text(f"Max Snake Length: {self.max_snake_length}", (self.screen_width // 2 - 150, 140))
            self.draw_text(f"Items Collected: {self.items_collected}", (self.screen_width // 2 - 150, 180))

            self.draw_text("Press ESC to go back", (self.screen_width // 2 - 150, self.screen_height - 50))
            pygame.display.flip()
            self.clock.tick(10)

    def show_tutorial(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.show_menu()

            self.screen.fill("black")
            self.draw_text("Tutorial", (self.screen_width // 2 - 100, 50))
            self.draw_text("Use W, A, S, D to move the snake.", (self.screen_width // 2 - 150, 100))
            self.draw_text("Eat the red object to grow.", (self.screen_width // 2 - 150, 140))
            self.draw_text("Avoid the walls and your own body!", (self.screen_width // 2 - 150, 180))
            self.draw_text("Press ESC to go back", (self.screen_width // 2 - 150, self.screen_height - 50))
            pygame.display.flip()
            self.clock.tick(10)

    def show_menu(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # Menú de opciones
            self.screen.fill("black")
            self.draw_text("Ivy Snake in Python Game", (self.screen_width // 2 - 150, 50))
            self.draw_text("1. New Game", (self.screen_width // 2 - 100, 150))
            self.draw_text("2. High Scores", (self.screen_width // 2 - 100, 200))
            self.draw_text("3. Statistics", (self.screen_width // 2 - 100, 250))
            self.draw_text("4. Tutorial", (self.screen_width // 2 - 100, 300))
            self.draw_text("5. Exit", (self.screen_width // 2 - 100, 350))

            # Selección de dificultad
            self.draw_text(f"Difficulty: {self.difficulty}", (self.screen_width // 2 - 100, 400))
            self.draw_text("Press 1, 2, or 3 to choose difficulty:", (self.screen_width // 2 - 200, 450))
            self.draw_text("1. Easy", (self.screen_width // 2 - 100, 480))
            self.draw_text("2. Medium", (self.screen_width // 2 - 100, 510))
            self.draw_text("3. Hard", (self.screen_width // 2 - 100, 540))

            pygame.display.flip()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_n]:
                pygame.quit()
                exit()
            if keys[pygame.K_h]:
                self.show_high_scores()
            if keys[pygame.K_s]:
                self.show_statistics()
            if keys[pygame.K_t]:
                self.show_tutorial()
            if keys[pygame.K_1]:
                self.difficulty = "Easy"
                self.speed_factor = 10
                self.game_loop()
            if keys[pygame.K_2]:
                self.difficulty = "Medium"
                self.speed_factor = 15
                self.game_loop()
            if keys[pygame.K_3]:
                self.difficulty = "Hard"
                self.speed_factor = 20
                self.game_loop()
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.show_menu()