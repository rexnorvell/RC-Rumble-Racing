import pygame
import math
import sys
import constants
import numpy as np

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

    # Define the finish line and the checkpoint
    finish_line = pygame.Rect(12, 400, 180, 50)
    checkpoint_1 = pygame.Rect(1200, 350, 200, 50)

    # Load the image of the track, scaling it to the size of the window
    track_image = pygame.image.load(constants.MAGNIFICENT_MEADOW_TRACK_IMAGE).convert()
    track_image = pygame.transform.scale(track_image, (constants.WIDTH, constants.HEIGHT))

    # Load the black and white image of the track, scaling it to the size of the window
    track_image_bw = pygame.image.load(constants.MAGNIFICENT_MEADOW_TRACK_IMAGE_BW).convert()
    track_image_bw = pygame.transform.scale(track_image_bw, (constants.WIDTH, constants.HEIGHT))

    # Create the text for the lap count
    lap_count_font = pygame.font.Font(constants.TEXT_FONT_PATH, 45)
    lap_count_text = lap_count_font.render(f"Lap {current_lap} of {constants.NUM_LAPS}", True, constants.TEXT_COLOR)
    lap_count_text_rect = lap_count_text.get_rect(center=(constants.WIDTH - 250, constants.HEIGHT - 90))

    # Create the text for the countdown
    countdown_font = pygame.font.Font(constants.TEXT_FONT_PATH, 120)

    # --- Countdown Timer ---
    countdown_start_time = pygame.time.get_ticks()

    # Masks
    track_pixels = pygame.surfarray.array3d(track_image_bw)
    off_road_mask = np.all(track_pixels == 255, axis=2)

    # Load and play background music
    play_next_track(current_track)
    current_track += 1

    running = True
    while running:
        clock.tick(60)
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
                countdown_text = None

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

        # Off-road detection
        if check_off_road(off_road_mask, car_x, car_y):
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

"""

# SPORTS_CAR_DESIGN
def draw_car(screen, x, y, angle):
	# This is the extra space on the sides for wheels and spoiler (overhang)
	# This is the x-position where the *main car body* will start on the new, wider surface
	body_offset_x = 3

	# Define a shorter "nose" height to create the oval shape
	oval_nose_height = 8

	# Radius of the front
	radius = constants.CAR_WIDTH // 2

	# Create a new, WIDER surface to fit the overhang
	new_width = constants.CAR_WIDTH + (2 * body_offset_x)
	car_surface = pygame.Surface((new_width, constants.CAR_HEIGHT), pygame.SRCALPHA)

	# Note: All x-coordinates for the body are shifted by 'body_offset_x'
	body_rect = (body_offset_x, radius, constants.CAR_WIDTH, constants.CAR_HEIGHT - radius)
	pygame.draw.rect(car_surface, constants.CAR_COLOR, body_rect)

	# Draw the rounded front
	ellipse_rect = (body_offset_x, 0, constants.CAR_WIDTH, oval_nose_height * 2)
	pygame.draw.ellipse(car_surface, constants.CAR_COLOR, ellipse_rect)

	# Add Windshield
	windshield_color = (173, 216, 230) # Light blue
	windshield_height = 5
	windshield_y = oval_nose_height + 1 # Just behind the nose
	windshield_x = body_offset_x + 3 # Inset from the body edge
	windshield_width = constants.CAR_WIDTH - 6 # Inset on both sides
	windshield_rect = (windshield_x, windshield_y, windshield_width, windshield_height)
	pygame.draw.rect(car_surface, windshield_color, windshield_rect)

	# Add Headlights
	headlight_color = (255, 255, 200) # Light yellow
	headlight_radius = 2
	headlight_y = oval_nose_height - 5 

	# Left headlight
	pygame.draw.circle(car_surface, headlight_color, (body_offset_x + (radius // 2), headlight_y), headlight_radius)
    
	# Right headlight
	pygame.draw.circle(car_surface, headlight_color, (body_offset_x + (radius + radius // 2), headlight_y), headlight_radius)

	# Add Spoiler
	spoiler_color = (50, 50, 50) # Dim Grey
	spoiler_height = 5
	spoiler_y = constants.CAR_HEIGHT - spoiler_height
	spoiler_rect = (0, spoiler_y, new_width, spoiler_height)
	pygame.draw.rect(car_surface, spoiler_color, spoiler_rect)    

	# Add Wheels
	wheel_color = (20, 20, 20) # Very dark gray
	wheel_width = body_offset_x # Use the overhang value
	wheel_height = 8

	# Position wheels vertically
	front_wheel_y = oval_nose_height
	rear_wheel_y = constants.CAR_HEIGHT - wheel_height - spoiler_height - 2
    
	# Left wheels (at x=0)
	pygame.draw.rect(car_surface, wheel_color, (0, front_wheel_y, wheel_width, wheel_height))
	pygame.draw.rect(car_surface, wheel_color, (0, rear_wheel_y, wheel_width, wheel_height))

	# Right wheels (at the far right edge)
	right_wheel_x = new_width - wheel_width
	pygame.draw.rect(car_surface, wheel_color, (right_wheel_x, front_wheel_y, wheel_width, wheel_height))
	pygame.draw.rect(car_surface, wheel_color, (right_wheel_x, rear_wheel_y, wheel_width, wheel_height))

	# Rotate and draw the car
	rotated_car = pygame.transform.rotate(car_surface, -angle)
	rect = rotated_car.get_rect(center=(x, y))
	screen.blit(rotated_car, rect.topleft)

"""

# OPEN_WHELL_CAR_DESGIN
def draw_car(screen, x, y, angle):
	# Define car dimensions
	body_width = 12 	# The narrowest part of the chassis
	new_car_length = 60	# The full length of the car
	total_width = 48	# Full width of the drawing surface (body_width * 4)

	# This is the x-position where the narrow body will start
	# We center it on the wide surface
	body_x_start = (total_width - body_width) // 2	# 18
	body_x_end = body_x_start + body_width		# 30

	# Create the wide surface
	car_surface = pygame.Surface((total_width, new_car_length), pygame.SRCALPHA)

	# Colors
	wheel_color = (20, 20, 20)
	axle_color = (50, 50, 50)
	wing_color = (0, 0, 0) # Black for wings

	# Draw Main Body

	# Draw an oval nose at the front
	nose_height = 10
	ellipse_rect = (body_x_start, 0, body_width, nose_height * 2)
	pygame.draw.ellipse(car_surface, constants.CAR_COLOR, ellipse_rect)

	# The polygon body
	# Define the new wider "sidepod" dimensions
	sidepod_width = 24
	sidepod_x_start = (total_width - sidepod_width) // 2	# 12
	sidepod_x_end = sidepod_x_start + sidepod_width		# 36
	
	# Define the Y-positions for the body shape
	taper_start_y = 26	# Just behind front wheels
	sidepod_start_y = 38	# Just before rear wheels
	sidepod_end_y = 49	# Middle of rear wheels

	# Define the 10 points of the polygon
	body_points = [
		(body_x_start, nose_height),     # 1. Top-left of body (at nose
		(body_x_end, nose_height),       # 2. Top-right of body (at nose
		(body_x_end, taper_start_y),     # 3. Start of taper (right)
		(sidepod_x_end, sidepod_start_y),# 4. End of taper (right)
		(sidepod_x_end, sidepod_end_y),  # 5. Back of sidepod (right)
		(body_x_end, new_car_length),    # 6. Very back of car (right)
		(body_x_start, new_car_length),  # 7. Very back of car (left)
		(sidepod_x_start, sidepod_end_y),# 8. Back of sidepod (left)
		(sidepod_x_start, sidepod_start_y),# 9. End of taper (left)
		(body_x_start, taper_start_y)    # 10. Start of taper (left)
	]

	pygame.draw.polygon(car_surface, constants.CAR_COLOR, body_points)

	# Draw Cockpit
	cockpit_color = (0, 0, 0)
	cockpit_height = 10

	cockpit_y = 31 # This ends at y=41, just before the rear wheels
	cockpit_rect = (body_x_start, cockpit_y, body_width, cockpit_height)
	pygame.draw.rect(car_surface, cockpit_color, cockpit_rect)

	# Draw Wings
	front_wing_height = 6
	front_wing_width = total_width - 20 # Was total_width - 10
	front_wing_x = (total_width - front_wing_width) // 2
	front_wing_y = 2
	pygame.draw.rect(car_surface, wing_color, (front_wing_x, front_wing_y, front_wing_width, front_wing_height))

	rear_wing_height = 6
	rear_wing_width = 16 # Was total_width - 16
	rear_wing_x = (total_width - rear_wing_width) // 2
	rear_wing_y = new_car_length - rear_wing_height - 2
	pygame.draw.rect(car_surface, wing_color, (rear_wing_x, rear_wing_y, rear_wing_width, rear_wing_height))
	
	# --- 5. Draw Wheels & Axles ---
	wheel_width = 8
	wheel_height = 12
	axle_width = 2

	# Wheel Y positions
	front_wheel_y = nose_height + 2				#12
	rear_wheel_y = new_car_length - wheel_height - 5	#43

	# Left wheel X (far left)
	left_wheel_x = 4

	# Right wheel X (far right)
	right_wheel_x = total_width - wheel_width - 4		#36

	# Draw the 4 wheels
	pygame.draw.rect(car_surface, wheel_color, (left_wheel_x, front_wheel_y, wheel_width, wheel_height))
	pygame.draw.rect(car_surface, wheel_color, (right_wheel_x, front_wheel_y, wheel_width, wheel_height))
	pygame.draw.rect(car_surface, wheel_color, (left_wheel_x, rear_wheel_y, wheel_width, wheel_height))
	pygame.draw.rect(car_surface, wheel_color, (right_wheel_x, rear_wheel_y, wheel_width, wheel_height))

	# Draw the 4 axles
	# Front-left axle
	pygame.draw.line(car_surface, axle_color, (left_wheel_x + wheel_width, front_wheel_y + wheel_height // 2), (body_x_start, front_wheel_y + wheel_height // 2), axle_width)

	# Front-right axle
	pygame.draw.line(car_surface, axle_color, (body_x_start + body_width, front_wheel_y + wheel_height // 2), (right_wheel_x, front_wheel_y + wheel_height // 2), axle_width)

	# Rear-left axle
	pygame.draw.line(car_surface, axle_color, (left_wheel_x + wheel_width, rear_wheel_y + wheel_height // 2), (body_x_start, rear_wheel_y + wheel_height // 2), axle_width)

	# Rear-right axle
	pygame.draw.line(car_surface, axle_color, (body_x_start + body_width, rear_wheel_y + wheel_height // 2), (right_wheel_x, rear_wheel_y + wheel_height // 2), axle_width)

	# Rotate and draw the car
	rotated_car = pygame.transform.rotate(car_surface, -angle)
	rect = rotated_car.get_rect(center=(x, y))
	screen.blit(rotated_car, rect.topleft)



def check_off_road(off_road_mask, x, y):
    ix, iy = int(x), int(y)
    if 0 <= ix < off_road_mask.shape[0] and 0 <= iy < off_road_mask.shape[1]:
        if off_road_mask[ix, iy]:
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