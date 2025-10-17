import pygame
import math
import sys
import constants

def start():

    # Initialize pygame
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption(constants.GAME_TITLE)

    # State
    current_lap = 1
    has_checkpoint = False
    before_race = True
    during_race = False
    race_over = False
    applause_played = False
    current_track = 0
    race_start_time = None
    race_end_time = None

    # Car parameters
    car_x, car_y = constants.START_X, constants.START_Y
    car_angle = 0
    car_speed = 0

    # Define the finish line and checkpoints
    finish_line = pygame.Rect(12, 400, 180, 50)
    checkpoint_1 = pygame.Rect(1200, 350, 200, 50)

    # Load the image
    track_image = pygame.image.load(constants.MAGNIFICENT_MEADOW_TRACK_IMAGE).convert()
    track_image = pygame.transform.scale(track_image, (constants.WIDTH, constants.HEIGHT))

    # Create the text for the lap count
    lap_count_font = pygame.font.Font(constants.TEXT_FONT_PATH, 45)
    lap_count_text = lap_count_font.render(f"Lap {current_lap} of {constants.NUM_LAPS}", True, constants.TEXT_COLOR)
    lap_count_text_rect = lap_count_text.get_rect(center=(constants.WIDTH - 250, constants.HEIGHT - 90))

    # Create the text for the countdown
    countdown_font = pygame.font.Font(constants.TEXT_FONT_PATH, 120)

    # --- Countdown Timer ---
    countdown_start_time = pygame.time.get_ticks()
    countdown_duration = 4000

    # Masks
    track_pixels = pygame.surfarray.array3d(track_image)
    offroad_mask = (track_pixels[:, :, 1] > 100) & (track_pixels[:, :, 0] < 100) & (track_pixels[:, :, 2] < 100)

    # Load and play background music
    play_next_track(current_track)
    current_track += 1

    running = True
    while running:
        dt = clock.tick(60) / 1000  # seconds per frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not pygame.mixer.music.get_busy():
            play_next_track(current_track)
            current_track += 1

        current_time = pygame.time.get_ticks()

        if before_race:
            elapsed = current_time - countdown_start_time

            # Determine which text to show
            if elapsed < 1000:
                countdown_text = "3"
            elif elapsed < 2000:
                countdown_text = "2"
            elif elapsed < 3000:
                countdown_text = "1"
            elif elapsed < 4000:
                during_race = True
                race_start_time = pygame.time.get_ticks()
                countdown_text = "Go!"
            else:
                before_race = False
                countdown_text = None  # stop showing countdown

        else:
            countdown_text = None

        if during_race:
            keys = pygame.key.get_pressed()

            # Acceleration / deceleration
            if keys[pygame.K_w]:
                car_speed += constants.ACCELERATION
            elif keys[pygame.K_s]:
                car_speed -= constants.ACCELERATION
            else:
                car_speed = math.copysign(max(abs(car_speed) - constants.FRICTION, 0), car_speed)

            # Clamp speed
            car_speed = max(-constants.MAX_SPEED / 2, min(constants.MAX_SPEED, car_speed))

            # Steering
            if keys[pygame.K_a]:
                car_angle -= constants.TURN_SPEED * (car_speed / constants.MAX_SPEED)
            if keys[pygame.K_d]:
                car_angle += constants.TURN_SPEED * (car_speed / constants.MAX_SPEED)
        else:
            car_speed = math.copysign(max(abs(car_speed) - constants.FRICTION, 0), car_speed)

        # Movement
        car_x += math.sin(math.radians(car_angle)) * car_speed
        car_y -= math.cos(math.radians(car_angle)) * car_speed

        # Draw everything
        draw_track(screen, track_image)
        draw_lap_count(screen, lap_count_text, lap_count_text_rect)
        draw_car(screen, car_x, car_y, car_angle)

        # Offroad detection
        if check_offroad(offroad_mask, car_x, car_y):
            car_speed = car_speed * 0.9

        # Checkpoint detection
        if not has_checkpoint and check_checkpoint(checkpoint_1, car_x, car_y):
            has_checkpoint = True

        # Finish line detection
        if has_checkpoint and check_finish(finish_line, car_x, car_y):
            has_checkpoint = False
            current_lap += 1
            if current_lap > constants.NUM_LAPS:
                lap_count_text = lap_count_font.render("Finish!", True, constants.TEXT_COLOR)
                lap_count_text_rect = lap_count_text.get_rect(center=(constants.WIDTH - 250, constants.HEIGHT - 90))
                during_race = False
                race_over = True
                race_end_time = pygame.time.get_ticks()
            else:
                if current_lap == constants.NUM_LAPS:
                    play_next_track(current_track)
                    current_track += 1
                lap_count_text = lap_count_font.render(f"Lap {current_lap} of {constants.NUM_LAPS}", True,
                                                       constants.TEXT_COLOR)
                lap_count_text_rect = lap_count_text.get_rect(center=(constants.WIDTH - 250, constants.HEIGHT - 90))

        # Draw countdown if active
        if countdown_text:
            countdown_surface = countdown_font.render(countdown_text, True, constants.TEXT_COLOR)
            countdown_rect = countdown_surface.get_rect(center=(constants.WIDTH / 2, constants.HEIGHT / 2))
            screen.blit(countdown_surface, countdown_rect)

        if race_over:
            display_race_time(screen, race_start_time, race_end_time)
            if not applause_played:
                applause_played = True
                play_next_track(current_track)
                current_track += 1

        pygame.display.flip()

    pygame.quit()
    sys.exit()

def play_next_track(current_track):
    if current_track < len(constants.MAGNIFICENT_MEADOW_PLAYLIST):
        track, loops = constants.MAGNIFICENT_MEADOW_PLAYLIST[current_track]
        pygame.mixer.music.load(track)
        pygame.mixer.music.play(loops)

def draw_track(screen, track_image):
    screen.blit(track_image, (0, 0))

def draw_lap_count(screen, lap_count_text, lap_count_text_rect):
    screen.blit(lap_count_text, lap_count_text_rect)

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
    return world_corners

def draw_car(screen, x, y, angle):
    car_surface = pygame.Surface((constants.CAR_WIDTH, constants.CAR_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(car_surface, constants.CAR_COLOR, (0, 0, constants.CAR_WIDTH, constants.CAR_HEIGHT))
    pygame.draw.rect(car_surface, (0, 0, 0), (0, 0, constants.CAR_WIDTH, constants.CAR_HEIGHT), width=2)
    rotated_car = pygame.transform.rotate(car_surface, -angle)
    rect = rotated_car.get_rect(center=(x, y))
    screen.blit(rotated_car, rect.topleft)

def check_offroad(offroad_mask, x, y):
    ix, iy = int(x), int(y)
    if 0 <= ix < offroad_mask.shape[0] and 0 <= iy < offroad_mask.shape[1]:
        if offroad_mask[ix, iy]:
            return True
    return False

def check_checkpoint(checkpoint_1, x, y):
    ix, iy = int(x), int(y)
    if checkpoint_1.collidepoint(ix, iy):
        return True
    return False

def check_finish(finish_line, x, y):
    ix, iy = int(x), int(y)
    if finish_line.collidepoint(ix, iy):
        return True
    return False

def display_race_time(screen, race_start_time, race_end_time):
    total_time_ms = race_end_time - race_start_time
    total_seconds = total_time_ms / 1000
    formatted_time = f"{total_seconds:.2f} s"

    time_font = pygame.font.Font(constants.TEXT_FONT_PATH, 60)
    time_surface = time_font.render(formatted_time, True, constants.TEXT_COLOR)
    time_rect = time_surface.get_rect(center=(constants.WIDTH / 2, constants.HEIGHT / 2))
    screen.blit(time_surface, time_rect)