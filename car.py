import csv
import math
import pygame

import constants


class Car:
    # Represents the player's car, handling its state, movement, input, and drawing

    def __init__(self, screen: pygame.Surface, track_name: str, is_ghost: bool, style_index: int) -> None:
        self.screen: pygame.Surface = screen
        self.x: float = constants.START_X[track_name]
        self.y: float = constants.START_Y[track_name]
        self.car_angle: float = constants.START_ROTATION[track_name]
        self.move_angle: float = self.car_angle
        self.speed: float = 0.0
        self.width: int = constants.CAR_WIDTH
        self.height: int = constants.CAR_HEIGHT
        self.color: tuple[int, int, int] = constants.CAR_COLOR
        self.opacity: int = 128 if is_ghost else 255

        self.style_index: int = style_index
        self.sprite = pygame.image.load(constants.CAR_IMAGE_PATH.format(car_type=constants.CAR_TYPES[self.style_index])).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))

    def handle_input(self, keys: pygame.key.ScancodeWrapper, is_race_active: bool) -> None:
        #Processes keyboard input to adjust speed and angle
        if not is_race_active:
            self.speed = math.copysign(max(abs(self.speed) - constants.FRICTION, 0), self.speed)
            return

        if keys[pygame.K_w]:
            self.speed += constants.ACCELERATION
        elif keys[pygame.K_s]:
            self.speed -= constants.ACCELERATION
        else:
            self.speed = math.copysign(max(abs(self.speed) - constants.FRICTION, 0), self.speed)

        # Directly change the car angle (which direction the car is facing)
        turn_factor: float = constants.TURN_SPEED * (self.speed / constants.MAX_SPEED)
        if keys[pygame.K_a]:
            self.car_angle -= turn_factor
        if keys[pygame.K_d]:
            self.car_angle += turn_factor

        # The move angle (the direction the car is going) should lag behind the car angle.
        error = self.car_angle - self.move_angle
        # Don't allow the move angle to get too far behind.
        if abs(error) > constants.MAX_DRIFT_ANGLE:
            delta_angle = abs(error) - 80
        else:
            # When drifting (space), the move angle should lag more.
            delta_angle = (
                constants.DRIFT_RECOVERY_SPEED
                if keys[pygame.K_SPACE]
                else 2 * constants.DRIFT_RECOVERY_SPEED
            )
        self.move_angle += math.copysign(min(abs(error), delta_angle), error)

    def update_position(self, max_speed: float) -> None:
        # Clamps speed and updates car position based on current angle and speed
        self.speed = max(-max_speed / 2.0, min(max_speed, self.speed))

        self.x += float(math.sin(math.radians(self.move_angle)) * self.speed)
        self.y -= float(math.cos(math.radians(self.move_angle)) * self.speed)

    def draw(self, camera_x: float, camera_y: float) -> None:
        """Draws the car on the track"""
        rotated_image = pygame.transform.rotate(self.sprite, -self.car_angle)
        rotated_image.set_alpha(self.opacity)

        # Calculate the car's position *on the screen*
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # Center the rect on its screen-space coordinates
        rect = rotated_image.get_rect(center=(screen_x, screen_y))
        self.screen.blit(rotated_image, rect)

    def log_properties(self, track_name: str) -> None:
        """Write the car's position and angle to the .csv file"""
        with open(constants.REPLAY_FILE_PATH.format(track_name=track_name), "a", newline="") as replay_file:
            csv_writer = csv.writer(replay_file)
            csv_writer.writerow([self.x, self.y, self.move_angle, self.car_angle])
