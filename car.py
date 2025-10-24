import math
import pygame

import constants


class Car:
    """Represents the player's car, handling its state, movement, input, and drawing."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen: pygame.Surface = screen
        self.x: float = constants.START_X
        self.y: float = constants.START_Y
        self.angle: float = 0.0
        self.speed: float = 0.0
        self.width: int = constants.CAR_WIDTH
        self.height: int = constants.CAR_HEIGHT
        self.color: tuple[int, int, int] = constants.CAR_COLOR

    def get_car_corners(self, center: tuple[float, float], size: tuple[int, int], angle: float) -> list[tuple[float, float]]:
        """Calculates the four corner coordinates of the rotated car body."""
        w, h = size
        cx, cy = center
        hw, hh = w / 2, h / 2
        local_corners: list[pygame.math.Vector2] = [
            pygame.math.Vector2(-hw, -hh),
            pygame.math.Vector2(hw, -hh),
            pygame.math.Vector2(hw, hh),
            pygame.math.Vector2(-hw, hh),
        ]
        world_corners: list[tuple[float, float]] = []
        for v in local_corners:
            rv: pygame.math.Vector2 = v.rotate(angle)
            world_corners.append((cx + rv.x, cy + rv.y))
        return world_corners

    def handle_input(self, keys: pygame.key.ScancodeWrapper, is_race_active: bool) -> None:
        """Processes keyboard input to adjust speed and angle."""
        if not is_race_active:
            self.speed = math.copysign(max(abs(self.speed) - constants.FRICTION, 0), self.speed)
            return

        if keys[pygame.K_w]:
            self.speed += constants.ACCELERATION
        elif keys[pygame.K_s]:
            self.speed -= constants.ACCELERATION
        else:
            self.speed = math.copysign(max(abs(self.speed) - constants.FRICTION, 0), self.speed)

        turn_factor: float = constants.TURN_SPEED * (self.speed / constants.MAX_SPEED)
        if keys[pygame.K_a]:
            self.angle -= turn_factor
        if keys[pygame.K_d]:
            self.angle += turn_factor

    def update_position(self, max_speed: float) -> None:
        """Clamps speed and updates car position based on current angle and speed."""
        self.speed = max(-max_speed / 2.0, min(max_speed, self.speed))

        self.x += float(math.sin(math.radians(self.angle)) * self.speed)
        self.y -= float(math.cos(math.radians(self.angle)) * self.speed)

    def draw(self, car_design_id: int = 1) -> None:
        if car_design_id == 1:
            self._draw_car1()
        else:
            self._draw_car2()

    def _draw_car2(self) -> None:
        body_offset_x: int = 3
        oval_nose_height: int = 8
        radius: int = constants.CAR_WIDTH // 2

        new_width: int = constants.CAR_WIDTH + (2 * body_offset_x)
        car_surface: pygame.Surface = pygame.Surface((new_width, constants.CAR_HEIGHT), pygame.SRCALPHA)

        body_rect: tuple[int, int, int, int] = (body_offset_x, radius, constants.CAR_WIDTH, constants.CAR_HEIGHT - radius)
        pygame.draw.rect(car_surface, self.color, body_rect)
        ellipse_rect: tuple[int, int, int, int] = (body_offset_x, 0, constants.CAR_WIDTH, oval_nose_height * 2)
        pygame.draw.ellipse(car_surface, self.color, ellipse_rect)

        windshield_color: tuple[int, int, int] = (173, 216, 230)
        windshield_height: int = 5
        windshield_y: int = oval_nose_height + 1
        windshield_x: int = body_offset_x + 3
        windshield_width: int = constants.CAR_WIDTH - 6
        windshield_rect: tuple[int, int, int, int] = (windshield_x, windshield_y, windshield_width, windshield_height)
        pygame.draw.rect(car_surface, windshield_color, windshield_rect)

        headlight_color: tuple[int, int, int] = (255, 255, 200)
        headlight_radius: int = 2
        headlight_y: int = oval_nose_height - 5
        pygame.draw.circle(car_surface, headlight_color, (body_offset_x + (radius // 2), headlight_y), headlight_radius)
        pygame.draw.circle(car_surface, headlight_color, (body_offset_x + (radius + radius // 2), headlight_y), headlight_radius)

        spoiler_color: tuple[int, int, int] = (50, 50, 50)
        spoiler_height: int = 5
        spoiler_y: int = constants.CAR_HEIGHT - spoiler_height
        spoiler_rect: tuple[int, int, int, int] = (0, spoiler_y, new_width, spoiler_height)
        pygame.draw.rect(car_surface, spoiler_color, spoiler_rect)

        wheel_color: tuple[int, int, int] = (20, 20, 20)
        wheel_width: int = body_offset_x
        wheel_height: int = 8
        front_wheel_y: int = oval_nose_height
        rear_wheel_y: int = constants.CAR_HEIGHT - wheel_height - spoiler_height - 2

        right_wheel_x: int = new_width - wheel_width

        for y in [front_wheel_y, rear_wheel_y]:
            pygame.draw.rect(car_surface, wheel_color, (0, y, wheel_width, wheel_height))
            pygame.draw.rect(car_surface, wheel_color, (right_wheel_x, y, wheel_width, wheel_height))

        rotated_car: pygame.Surface = pygame.transform.rotate(car_surface, -self.angle)
        rect: pygame.Rect = rotated_car.get_rect(center=(self.x, self.y))
        self.screen.blit(rotated_car, rect.topleft)

    def _draw_car1(self) -> None:
        body_width: int = 12
        new_car_length: int = 60
        total_width: int = 48

        body_x_start: int = (total_width - body_width) // 2
        body_x_end: int = body_x_start + body_width

        car_surface: pygame.Surface = pygame.Surface((total_width, new_car_length), pygame.SRCALPHA)

        wheel_color: tuple[int, int, int] = (20, 20, 20)
        axle_color: tuple[int, int, int] = (50, 50, 50)
        wing_color: tuple[int, int, int] = (0, 0, 0)

        nose_height: int = 10
        pygame.draw.ellipse(car_surface, self.color, (body_x_start, 0, body_width, nose_height * 2))

        sidepod_width: int = 24
        sidepod_x_start: int = (total_width - sidepod_width) // 2
        sidepod_x_end: int = sidepod_x_start + sidepod_width
        taper_start_y: int = 26
        sidepod_start_y: int = 38
        sidepod_end_y: int = 49

        body_points: list[tuple[int, int]] = [
            (body_x_start, nose_height), (body_x_end, nose_height),
            (body_x_end, taper_start_y), (sidepod_x_end, sidepod_start_y),
            (sidepod_x_end, sidepod_end_y), (body_x_end, new_car_length),
            (body_x_start, new_car_length), (sidepod_x_start, sidepod_end_y),
            (sidepod_x_start, sidepod_start_y), (body_x_start, taper_start_y)
        ]
        pygame.draw.polygon(car_surface, self.color, body_points)

        cockpit_y: int = 31
        pygame.draw.rect(car_surface, wing_color, (body_x_start, cockpit_y, body_width, 10))

        front_wing_width: int = total_width - 20
        front_wing_x: int = (total_width - front_wing_width) // 2
        pygame.draw.rect(car_surface, wing_color, (front_wing_x, 2, front_wing_width, 6))

        rear_wing_width: int = 16
        rear_wing_x: int = (total_width - rear_wing_width) // 2
        rear_wing_y: int = new_car_length - 8
        pygame.draw.rect(car_surface, wing_color, (rear_wing_x, rear_wing_y, rear_wing_width, 6))

        wheel_width, wheel_height = 8, 12
        axle_width: int = 2
        front_wheel_y: int = nose_height + 2
        rear_wheel_y: int = new_car_length - wheel_height - 5
        left_wheel_x: int = 4
        right_wheel_x: int = total_width - wheel_width - 4

        wheel_positions: list[tuple[int, int]] = [
            (left_wheel_x, front_wheel_y), (right_wheel_x, front_wheel_y),
            (left_wheel_x, rear_wheel_y), (right_wheel_x, rear_wheel_y)
        ]
        for x, y in wheel_positions:
            pygame.draw.rect(car_surface, wheel_color, (x, y, wheel_width, wheel_height))

        for y in [front_wheel_y, rear_wheel_y]:
            y_mid: int = y + wheel_height // 2
            pygame.draw.line(car_surface, axle_color, (left_wheel_x + wheel_width, y_mid), (body_x_start, y_mid), axle_width)
            pygame.draw.line(car_surface, axle_color, (body_x_start + body_width, y_mid), (right_wheel_x, y_mid), axle_width)

        rotated_car: pygame.Surface = pygame.transform.rotate(car_surface, -self.angle)
        rect: pygame.Rect = rotated_car.get_rect(center=(self.x, self.y))
        self.screen.blit(rotated_car, rect.topleft)

