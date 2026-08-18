import cv2
import numpy as np


class FireballEffect:
    """Procedural fireball energy effect centered on the palm."""

    def __init__(self, base_radius: int = 50, smoothing: float = 0.18, formation_duration: float = 2.4):
        self.base_radius = float(base_radius)
        self.smoothing = smoothing
        self.formation_duration = max(formation_duration, 0.1)

        self.position = np.array([0.0, 0.0], dtype=np.float32)
        self.target_position = np.array([0.0, 0.0], dtype=np.float32)
        self.active = False
        self.charge = 0.0
        self.timestamp = 0.0
        self.last_timestamp = None

        self.particle_count = 44
        self.particle_angles = np.linspace(0.0, 2.0 * np.pi, self.particle_count, endpoint=False)
        self.particle_lifetime = np.linspace(0.5, 1.5, self.particle_count)
        self.particle_sizes = np.linspace(1.5, 4.0, self.particle_count)
        self.particle_velocities = np.linspace(1.4, 3.6, self.particle_count)

    @staticmethod
    def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, value))

    @staticmethod
    def _smoothstep(value: float) -> float:
        value = FireballEffect._clamp(value)
        return value * value * (3.0 - 2.0 * value)

    @staticmethod
    def _ease_out_quad(value: float) -> float:
        value = FireballEffect._clamp(value)
        return 1.0 - ((1.0 - value) ** 2)

    def update(self, position, timestamp: float):
        """Update fireball formation progress and smoothed palm-following position."""
        if position is None:
            self.active = False
            self.charge = 0.0
            self.last_timestamp = None
            return

        target = np.asarray(position, dtype=np.float32)
        self.target_position = target
        self.position = self.position + (self.target_position - self.position) * self.smoothing

        if not self.active:
            self.active = True
            self.charge = 0.0
            self.last_timestamp = timestamp
        elif self.last_timestamp is not None:
            dt = max(0.016, timestamp - self.last_timestamp)
            self.charge = min(1.0, self.charge + dt / self.formation_duration)

        self.last_timestamp = timestamp
        self.timestamp = timestamp

    def _formation_progress(self) -> float:
        if not self.active:
            return 0.0
        return self._smoothstep(self.charge)

    def _render_hot_core(self, overlay, center_x: int, center_y: int, progress: float):
        """Render the hot glowing center of the fireball."""
        pulse = 1.0 + 0.22 * np.sin(self.timestamp * 11.0)
        radius = self.base_radius * (0.18 + 0.82 * self._ease_out_quad(progress)) * pulse

        cv2.circle(overlay, (center_x, center_y), int(radius * 0.7), (255, 247, 170), -1)
        cv2.circle(overlay, (center_x, center_y), int(radius * 1.05), (255, 180, 70), -1)
        cv2.circle(overlay, (center_x, center_y), int(radius * 1.45), (255, 110, 40), -1)

    def _render_flame_shell(self, overlay, center_x: int, center_y: int, progress: float):
        """Render irregular flame boundary with animated lobes."""
        flame_progress = self._clamp(progress)
        if flame_progress < 0.05:
            return

        max_radius = self.base_radius * (0.85 + 0.9 * flame_progress)
        points = []
        segments = 28

        for i in range(segments):
            angle = (2.0 * np.pi * i) / segments
            shape_variation = 0.55 + 0.45 * np.sin(self.timestamp * 7.0 + i * 1.3)
            lobe = 0.65 + 0.35 * np.sin(self.timestamp * 5.0 + i * 0.9 + progress * 8.0)
            radius = max_radius * (0.72 + 0.38 * shape_variation + 0.2 * lobe * progress)
            x = center_x + np.cos(angle) * radius
            y = center_y + np.sin(angle) * radius * (0.88 + 0.16 * np.sin(self.timestamp * 6.0 + i))
            points.append((int(x), int(y)))

        contour = np.array(points, dtype=np.int32)
        cv2.fillPoly(overlay, [contour], (255, 140, 40))

        # Outer flame glow
        outer_radius = int(max_radius * 1.18)
        cv2.circle(overlay, (center_x, center_y), outer_radius, (255, 80, 30), 2)

    def _render_glow(self, overlay, center_x: int, center_y: int, progress: float):
        """Render layered orange/red glow around the core."""
        for layer_index in range(5):
            layer_progress = self._clamp(progress - layer_index * 0.12)
            if layer_progress <= 0.0:
                continue

            layer_scale = 1.2 + layer_index * 0.55 + layer_progress * 0.8
            radius = int(self.base_radius * layer_scale)
            glow_color = (
                int(35 + layer_index * 18 + layer_progress * 50),
                int(100 + layer_index * 28 + layer_progress * 80),
                int(205 + layer_index * 10),
            )
            cv2.circle(overlay, (center_x, center_y), radius, glow_color, thickness=-1)

    def _render_fire_particles(self, overlay, center_x: int, center_y: int, progress: float):
        """Render a dynamic particle burst around the fireball."""
        if progress < 0.05:
            return

        particle_count = min(self.particle_count, int(self.particle_count * (0.25 + progress * 0.95)))

        for particle_index in range(particle_count):
            base_angle = self.particle_angles[particle_index]
            drift = 0.5 + 0.8 * np.sin(self.timestamp * 6.0 + particle_index)
            radial_distance = self.base_radius * (0.9 + progress) + 10.0 * drift
            angle = base_angle + self.timestamp * (0.7 + self.particle_velocities[particle_index] * 0.15)
            x = center_x + np.cos(angle) * radial_distance
            y = center_y + np.sin(angle) * radial_distance

            size = int(self.particle_sizes[particle_index] * (0.7 + progress))
            color = (int(220 + progress * 20), int(110 + progress * 70), int(30 + progress * 90))
            cv2.circle(overlay, (int(x), int(y)), max(1, size), color, -1)

    def _render_sparks(self, overlay, center_x: int, center_y: int, progress: float):
        """Render outward-moving sparks from the flame."""
        sparkle_count = 8 + int(progress * 10)
        for spark_index in range(sparkle_count):
            angle = self.timestamp * (2.0 + spark_index * 0.35) + spark_index * 1.1
            dist = self.base_radius * (1.2 + progress) + spark_index * 7.5
            x1 = int(center_x + np.cos(angle) * (dist * 0.5))
            y1 = int(center_y + np.sin(angle) * (dist * 0.5))
            x2 = int(center_x + np.cos(angle) * dist)
            y2 = int(center_y + np.sin(angle) * dist)
            cv2.line(overlay, (x1, y1), (x2, y2), (255, 180, 60), 1)

    def render(self, frame):
        """Render the full Fireball onto the frame."""
        if not self.active:
            return frame

        progress = self._formation_progress()
        center = np.rint(self.position).astype(int)
        center_x, center_y = int(center[0]), int(center[1])
        overlay = np.zeros_like(frame)

        self._render_glow(overlay, center_x, center_y, progress)
        self._render_hot_core(overlay, center_x, center_y, progress)
        self._render_flame_shell(overlay, center_x, center_y, progress)
        self._render_fire_particles(overlay, center_x, center_y, progress)
        self._render_sparks(overlay, center_x, center_y, progress)

        alpha = 0.7 + progress * 0.18
        return cv2.addWeighted(frame, 1.0, overlay, alpha, 0)

    def set_inactive(self):
        self.active = False
        self.charge = 0.0
        self.last_timestamp = None
