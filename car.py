import csv
import math
import pygame

import constants


class Car:
    """Represents the player's car, handling its state, movement, input, and drawing"""

    def __init__(self, screen: pygame.Surface, track_name: str, is_ghost: bool, style_index: int) -> None:
        self.screen: pygame.Surface = screen

        # Store start values
        self.start_x: float = constants.START_X[track_name]
        self.start_y: float = constants.START_Y[track_name]
        self.start_angle: float = constants.START_ROTATION[track_name]
        self.max_speed: float = constants.MAX_SPEED

        # Set initial dynamic position
        self.x: float = self.start_x
        self.y: float = self.start_y
        self.car_angle: float = self.start_angle
        self.move_angle: float = self.car_angle
        self.speed: float = 0.0

        # State
        self.is_off_road: bool = False
        self.is_drifting: bool = False

        # Set initial respawn point (updated in Race class)
        self.respawn_x: float = self.start_x
        self.respawn_y: float = self.start_y
        self.respawn_angle: float = self.start_angle

        self.width: int = constants.CAR_WIDTH
        self.height: int = constants.CAR_HEIGHT
        self.color: tuple[int, int, int] = constants.CAR_COLOR
        self.opacity: int = 128 if is_ghost else 255

        self.style_index: int = style_index
        self.sprite = pygame.image.load(constants.CAR_IMAGE_PATH.format(car_type=constants.CAR_TYPES[self.style_index])).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))

    def set_max_speed(self) -> None:
        """Sets the maximum speed of the car based on if it is drifting and if it is off-road"""
        self.max_speed = constants.MAX_SPEED
        if self.is_off_road:
            self.max_speed = max(self.speed - constants.ACCELERATION, self.max_speed * 0.5)
        elif self.is_drifting:
            self.max_speed = min(constants.MAX_SPEED * 2, self.max_speed * 1.1)

    def handle_input(self, keys: pygame.key.ScancodeWrapper, is_race_active: bool) -> None:
        """Processes keyboard input to adjust speed and angle"""
        if not is_race_active:
            self.speed = math.copysign(max(abs(self.speed) - constants.FRICTION, 0), self.speed)
            error = self.car_angle - self.move_angle
            delta_angle = 2 * constants.DRIFT_RECOVERY_SPEED
            self.move_angle += math.copysign(delta_angle, error)
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
        self.is_drifting = True if abs(error) > constants.MIN_DRIFT_ANGLE else False

        # Don't allow the move angle to get too far behind.
        if abs(error) > constants.MAX_DRIFT_ANGLE:
            delta_angle = 2 * constants.DRIFT_RECOVERY_SPEED
        # When drifting (space), the move angle should lag more.
        elif keys[pygame.K_SPACE]:
            delta_angle = constants.DRIFT_RECOVERY_SPEED
        else:
            delta_angle = 2 * constants.DRIFT_RECOVERY_SPEED
        self.move_angle += math.copysign(delta_angle, error)

    def update_position(self) -> None:
        """Clamps speed and updates car position based on current angle and speed"""
        self.speed = max(-self.max_speed / 2.0, min(self.max_speed, self.speed))

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

    def respawn(self) -> None:
        """Resets the car to the last known respawn point"""
        self.x = self.respawn_x
        self.y = self.respawn_y
        self.speed = 0.0
        self.car_angle = self.respawn_angle
        self.move_angle = self.respawn_angle

    def set_respawn_point(self, x: float, y: float, angle: float) -> None:
        """Updates the car's respawn location"""
        self.respawn_x = x
        self.respawn_y = y
        self.respawn_angle = angle

    def log_properties(self, track_name: str) -> None:
        """Write the car's position and angle to the .csv file"""
        with open(constants.REPLAY_FILE_PATH.format(track_name=track_name), "a", newline="") as replay_file:
            csv_writer = csv.writer(replay_file)
            csv_writer.writerow([self.x, self.y, self.move_angle, self.car_angle])