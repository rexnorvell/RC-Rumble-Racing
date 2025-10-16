import pygame
import math
import sys

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 1920, 1080
# screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Car Rug Racer")

# Colors
GREEN = (34, 139, 34)
GRAY = (100, 100, 100)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Track boundaries (outer and inner rectangles)
track_outer = pygame.Rect(50, 50, 700, 500)
track_inner = pygame.Rect(200, 150, 400, 300)

# Car parameters
car_width, car_height = 20, 40
car_x, car_y = WIDTH // 5, HEIGHT // 2
car_angle = 0
car_speed = 0
max_speed = 3
acceleration = 0.2
friction = 0.05
turn_speed = 1.8

track_image = pygame.image.load("magnificent_meadow.png").convert()

def draw_track():
    # screen.fill(GREEN)
    # pygame.draw.rect(screen, GRAY, track_outer)
    # pygame.draw.rect(screen, GREEN, track_inner)
    screen.blit(track_image, (0, 0))

def get_car_corners(center, size, angle):
    w, h = size
    cx, cy = center
    hw, hh = w / 2, h / 2
    local_corners = [
        pygame.math.Vector2(-hw, -hh),
        pygame.math.Vector2(hw, -hh),
        pygame.math.Vector2(hw, hh),
        pygame.math.Vector2(-hw, hh),
    ]
    world_corners = []
    for v in local_corners:
        rv = v.rotate(angle)
        world_corners.append((cx + rv.x, cy + rv.y))
        # pygame.draw.circle(screen, BLUE, (cx + rv.x, cy + rv.y), 10)
    return world_corners

def draw_car(x, y, angle):
    car_surface = pygame.Surface((car_width, car_height), pygame.SRCALPHA)
    car_surface.fill(RED)
    rotated_car = pygame.transform.rotate(car_surface, -angle)
    rect = rotated_car.get_rect(center=(x, y))
    screen.blit(rotated_car, rect.topleft)

def check_collision(corners):
    # if any(track_inner.collidepoint(corner) for corner in corners):
    #     return True
    # if not all(track_outer.collidepoint(corner) for corner in corners):
    #     return True
    for c in corners:
        color = track_image.get_at((int(c[0]), int(c[1])))[:3]
        # if color[1] > 38 and color[0] < 38 and color[2] < 38:
        if sum(color) < 9:
            return True
    return False

running = True
while running:
    dt = clock.tick(60) / 1000  # seconds per frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Acceleration / deceleration
    if keys[pygame.K_w]:
        car_speed += acceleration
    elif keys[pygame.K_s]:
        car_speed -= acceleration
    else:
        car_speed = math.copysign(max(abs(car_speed) - friction, 0), car_speed)

    # Clamp speed
    car_speed = max(-max_speed / 2, min(max_speed, car_speed))

    # Steering
    if keys[pygame.K_a]:
        car_angle -= turn_speed * (car_speed / max_speed)
    if keys[pygame.K_d]:
        car_angle += turn_speed * (car_speed / max_speed)

    # Movement
    car_x += math.sin(math.radians(car_angle)) * car_speed
    car_y -= math.cos(math.radians(car_angle)) * car_speed

    # Draw everything
    draw_track()
    draw_car(car_x, car_y, car_angle)
    # car_rect = draw_car(car_x, car_y, car_angle)

    # Collision detection
    if check_collision(get_car_corners((car_x, car_y), (car_width, car_height), car_angle)):
        print('collision!: ', car_x, car_y)
    #     # car_speed = -car_speed * 0.5  # bounce back effect

    pygame.display.flip()

pygame.quit()
sys.exit()
