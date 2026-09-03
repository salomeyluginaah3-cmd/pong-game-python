import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Game constants
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 10
PADDLE_SPEED = 6
BALL_SPEED = 5
AI_SPEED = 4.5

class Paddle:
    """Represents a paddle in the game"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED
    
    def move_up(self):
        if self.rect.top > 0:
            self.rect.y -= self.speed
    
    def move_down(self):
        if self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
    
    def get_center(self):
        return self.rect.centery

class Ball:
    """Represents the ball in the game"""
    def __init__(self):
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT / 2
        self.vx = BALL_SPEED * random.choice([-1, 1])
        self.vy = BALL_SPEED * random.choice([-1, 1])
        self.radius = BALL_SIZE
    
    def update(self):
        """Update ball position"""
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off top and bottom walls
        if self.y - self.radius <= 0 or self.y + self.radius >= SCREEN_HEIGHT:
            self.vy = -self.vy
            self.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.y))
    
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
    
    def get_rect(self):
        """Get a rectangle representing the ball for collision detection"""
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)
    
    def reset(self):
        """Reset ball to center"""
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT / 2
        self.vx = BALL_SPEED * random.choice([-1, 1])
        self.vy = BALL_SPEED * random.choice([-1, 1])

class PongGame:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60
        
        # Initialize game objects
        self.player_paddle = Paddle(20, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ai_paddle = Paddle(SCREEN_WIDTH - 35, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball()
        
        # Score tracking
        self.player_score = 0
        self.ai_score = 0
        
        # Font for scoreboard
        self.font_large = pygame.font.Font(None, 72)
        self.font_small = pygame.font.Font(None, 36)
    
    def handle_input(self):
        """Handle keyboard and mouse input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        
        keys = pygame.key.get_pressed()
        
        # Arrow keys or W/S for player paddle
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player_paddle.move_up()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player_paddle.move_down()
        
        # Mouse control - move paddle to mouse Y position
        mouse_pos = pygame.mouse.get_pos()
        mouse_y = mouse_pos[1]
        
        # Smoothly move paddle towards mouse position
        paddle_center = self.player_paddle.get_center()
        if mouse_y < paddle_center - 10:
            self.player_paddle.move_up()
        elif mouse_y > paddle_center + 10:
            self.player_paddle.move_down()
    
    def update_ai(self):
        """Update AI paddle movement"""
        ai_center = self.ai_paddle.get_center()
        ball_y = self.ball.y
        
        # AI tries to track the ball
        if ball_y < ai_center - 10:
            self.ai_paddle.move_up()
        elif ball_y > ai_center + 10:
            self.ai_paddle.move_down()
    
    def check_paddle_collision(self):
        """Check and handle ball-paddle collisions"""
        ball_rect = self.ball.get_rect()
        
        # Player paddle collision
        if ball_rect.colliderect(self.player_paddle.rect):
            if self.ball.vx < 0:  # Ball moving left
                self.ball.x = self.player_paddle.rect.right + self.ball.radius
                self.ball.vx = -self.ball.vx
                
                # Add spin based on where the ball hits the paddle
                hit_pos = (self.ball.y - self.player_paddle.rect.centery) / (PADDLE_HEIGHT / 2)
                self.ball.vy += hit_pos * 2
        
        # AI paddle collision
        if ball_rect.colliderect(self.ai_paddle.rect):
            if self.ball.vx > 0:  # Ball moving right
                self.ball.x = self.ai_paddle.rect.left - self.ball.radius
                self.ball.vx = -self.ball.vx
                
                # Add spin based on where the ball hits the paddle
                hit_pos = (self.ball.y - self.ai_paddle.rect.centery) / (PADDLE_HEIGHT / 2)
                self.ball.vy += hit_pos * 2
    
    def check_score(self):
        """Check if ball went out of bounds and update score"""
        if self.ball.x < 0:
            self.ai_score += 1
            self.ball.reset()
        elif self.ball.x > SCREEN_WIDTH:
            self.player_score += 1
            self.ball.reset()
    
    def draw_scoreboard(self):
        """Draw the scoreboard"""
        # Draw center line
        for y in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.line(self.screen, GRAY, (SCREEN_WIDTH // 2, y), 
                           (SCREEN_WIDTH // 2, y + 10), 2)
        
        # Draw player score (left side)
        player_text = self.font_large.render(str(self.player_score), True, WHITE)
        self.screen.blit(player_text, (SCREEN_WIDTH // 4 - player_text.get_width() // 2, 50))
        
        # Draw AI score (right side)
        ai_text = self.font_large.render(str(self.ai_score), True, WHITE)
        self.screen.blit(ai_text, (3 * SCREEN_WIDTH // 4 - ai_text.get_width() // 2, 50))
        
        # Draw instructions at bottom
        instruction_text = self.font_small.render("Arrow Keys/Mouse to Move | ESC to Quit", True, GRAY)
        self.screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 
                                            SCREEN_HEIGHT - 40))
    
    def update(self):
        """Update game state"""
        self.handle_input()
        self.ball.update()
        self.update_ai()
        self.check_paddle_collision()
        self.check_score()
    
    def draw(self):
        """Draw all game elements"""
        self.screen.fill(BLACK)
        
        self.player_paddle.draw(self.screen)
        self.ai_paddle.draw(self.screen)
        self.ball.draw(self.screen)
        self.draw_scoreboard()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()

if __name__ == "__main__":
    game = PongGame()
    game.run()
