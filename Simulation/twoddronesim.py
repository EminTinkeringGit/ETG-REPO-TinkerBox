import pygame
import math

# Constants
GRAVITY = 0.15
DRAG = 0.99
FPS = 60
WIDTH, HEIGHT = 800, 600

class Drone:
    def __init__(self):
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.angle = 0
        self.vx, self.vy = 0, 0
        self.v_angle = 0
        self.width = 60
        
    def update(self, thrust_l, thrust_r):
        # 1. Calculate Total Thrust and Torque
        total_thrust = thrust_l + thrust_r
        torque = (thrust_r - thrust_l) * 0.5
        
        # 2. Physics: Update Acceleration
        # Thrust acts perpendicular to the drone's body
        ax = total_thrust * math.sin(math.radians(self.angle))
        ay = -total_thrust * math.cos(math.radians(self.angle)) + GRAVITY
        
        # 3. Update Velocities
        self.vx = (self.vx + ax) * DRAG
        self.vy = (self.vy + ay) * DRAG
        self.v_angle = (self.v_angle + torque) * 0.9  # Angular damping
        
        # 4. Update Position
        self.x += self.vx
        self.y += self.vy
        self.angle += self.v_angle

    def draw(self, screen):
        # Draw the drone body as a line/rectangle
        start_pos = (self.x - (self.width/2) * math.cos(math.radians(self.angle)),
                     self.y - (self.width/2) * math.sin(math.radians(self.angle)))
        end_pos = (self.x + (self.width/2) * math.cos(math.radians(self.angle)),
                   self.y + (self.width/2) * math.sin(math.radians(self.angle)))
        pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos, 5)

# Pygame Setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
drone = Drone()

running = True
while running:
    screen.fill((30, 30, 30))
    t_l, t_r = 0, 0
    
    # Input Handling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]: t_l = 0.3  # Left motor
    if keys[pygame.K_p]: t_r = 0.3  # Right motor

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    drone.update(t_l, t_r)
    drone.draw(screen)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()