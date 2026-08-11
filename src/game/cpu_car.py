import csv
import math
import random
import pygame
from pathlib import Path

from ..utilities import constants
from .car import Car


class CpuCar(Car):
    """
    A car controlled by AI that follows a recorded path.
    It functions as a 'Smart Ghost' - physics-based but no collisions.
    """

    def __init__(self, screen: pygame.Surface, track_name: str, difficulty: str, game_map_path: Path):
        car_config = random.choice(constants.CAR_DEFINITIONS)
        style_index = random.randint(0, len(car_config["styles"]) - 1)

        super().__init__(screen, track_name, True, car_config, style_index, {})

        self.difficulty = difficulty
        self.path_points: list[tuple[float, float]] = []
        self.current_path_index: int = 0
        self.game_map_path = game_map_path

        self._load_path()

        self.settings = constants.CPU_DIFFICULTY_SETTINGS.get(difficulty, constants.CPU_DIFFICULTY_SETTINGS["medium"])

        self.base_max_speed = constants.BASE_MAX_SPEED * self.settings["speed_multiplier"]
        self.acceleration = constants.BASE_ACCELERATION * self.settings.get("accel_multiplier", 1.0)
        self.turn_speed = constants.BASE_TURN_SPEED * self.settings.get("turn_multiplier", 1.0)

        self.last_angle_diff = 0

    def _load_path(self):
        if not self.game_map_path.exists():
            print(f"CPU Path not found: {self.game_map_path}")
            return

        try:
            with open(self.game_map_path, newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    x = float(row[0])
                    y = float(row[1])
                    self.path_points.append((x, y))
        except Exception as e:
            print(f"Error loading CPU path: {e}")

    def _analyze_track_shape(self, start_idx: int) -> tuple[float, float]:
        points = []
        path_len = len(self.path_points)
        if path_len == 0: return 0.0, 0.0

        for i in range(0, 70, 10):
            idx = (start_idx + i) % path_len
            points.append(self.path_points[idx])

        segment_angles = []
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            angle = math.degrees(math.atan2(dx, -dy))
            segment_angles.append(angle)

        total_change = 0.0
        max_change = 0.0

        for i in range(len(segment_angles) - 1):
            diff = (segment_angles[i + 1] - segment_angles[i] + 180) % 360 - 180
            total_change += abs(diff)
            max_change = max(max_change, abs(diff))

        return total_change, max_change

    def update(self):  # <--- RENAMED FROM update_cpu
        if not self.path_points:
            return

        path_len = len(self.path_points)

        # 1. FIND CLOSEST POINT
        search_window = 50
        closest_dist = float('inf')
        best_index = self.current_path_index

        for i in range(search_window):
            idx = (self.current_path_index + i) % path_len
            px, py = self.path_points[idx]
            dist = math.hypot(px - self.x, py - self.y)
            if dist < closest_dist:
                closest_dist = dist
                best_index = idx

        self.current_path_index = best_index

        # 2. ANALYZE TRACK GEOMETRY
        total_curvature, max_turn_sharpness = self._analyze_track_shape(self.current_path_index)

        # 3. DETERMINE LOOKAHEAD
        base_lookahead = self.settings["lookahead"]

        if self.is_off_road:
            lookahead_distance = 10
        elif total_curvature > 60 or max_turn_sharpness > 15:
            lookahead_distance = 15
        elif total_curvature > 30:
            lookahead_distance = 25
        else:
            lookahead_distance = base_lookahead

        final_lookahead_index = (self.current_path_index + lookahead_distance) % path_len
        aim_x, aim_y = self.path_points[final_lookahead_index]

        # 4. CALCULATE STEERING
        dx = aim_x - self.x
        dy = aim_y - self.y
        target_angle = math.degrees(math.atan2(dx, -dy))
        angle_diff = (target_angle - self.car_angle + 180) % 360 - 180

        check_dist = 40
        check_idx = (self.current_path_index + check_dist) % path_len
        cx, cy = self.path_points[check_idx]
        cdx, cdy = cx - self.x, cy - self.y
        future_angle = math.degrees(math.atan2(cdx, -cdy))
        future_turn_severity = abs((future_angle - self.car_angle + 180) % 360 - 180)

        # 5. DRIFTING LOGIC
        if self.is_off_road:
            self.is_drifting = False
        else:
            speed_threshold = self.base_max_speed * 0.65
            if not self.is_drifting:
                if self.speed > speed_threshold:
                    if total_curvature > 35 or abs(angle_diff) > 22:
                        self.is_drifting = True

            if self.is_drifting:
                if abs(angle_diff) < 10:
                    self.is_drifting = False
                elif (self.last_angle_diff > 0 and angle_diff < 0) or (self.last_angle_diff < 0 and angle_diff > 0):
                    self.is_drifting = False

        self.last_angle_diff = angle_diff

        # 6. APPLY STEERING
        effective_turn_speed = self.turn_speed
        if abs(angle_diff) < 10:
            effective_turn_speed *= 0.7

        turn_amount = min(effective_turn_speed, abs(angle_diff))

        if abs(angle_diff) > 0.5:
            if angle_diff > 0:
                self.car_angle += turn_amount
            else:
                self.car_angle -= turn_amount

        # 7. THROTTLE LOGIC
        current_target_speed = self.base_max_speed

        if self.is_off_road:
            current_target_speed *= 0.5
        elif future_turn_severity > 30:
            current_target_speed *= 0.85
        elif total_curvature < 20 and max_turn_sharpness < 5:
            current_target_speed *= 1.0
        elif self.is_drifting:
            if max_turn_sharpness > 15:
                current_target_speed *= 0.85
            else:
                current_target_speed *= 0.90
        else:
            if abs(angle_diff) > 20:
                current_target_speed *= 0.80
            elif abs(angle_diff) > 10:
                current_target_speed *= 0.95

        if self.speed < current_target_speed:
            self.speed += self.acceleration
        elif self.speed > current_target_speed:
            self.speed -= self.acceleration

        # 8. PHYSICS UPDATE
        error = self.car_angle - self.move_angle
        if self.is_drifting:
            delta_angle = constants.DRIFT_RECOVERY_SPEED * 0.8
        else:
            delta_angle = 4 * constants.DRIFT_RECOVERY_SPEED

        self.move_angle += math.copysign(delta_angle, error)

        self.set_max_speed()
        self.update_position()