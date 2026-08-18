import cv2
import numpy as np


class ChidoriEffect:
    """Procedural Chidori-style lightning energy that follows the palm."""

    def __init__(self, base_radius: int = 48, smoothing: float = 0.18, formation_duration: float = 2.2):
        self.base_radius = float(base_radius)
        self.smoothing = smoothing
        self.formation_duration = max(formation_duration, 0.1)

        self.position = np.array([0.0, 0.0], dtype=np.float32)
        self.target_position = np.array([0.0, 0.0], dtype=np.float32)
        self.active = False
        self.timestamp = 0.0
        self.charge = 0.0
        self.last_timestamp = None

        self.branch_count = 12
        self.branch_angles = np.linspace(0.0, 2.0 * np.pi, self.branch_count, endpoint=False)
        self.branch_lengths = np.linspace(self.base_radius * 0.8, self.base_radius * 2.0, self.branch_count)
        self.particle_count = 28
        self.particle_angles = np.linspace(0.0, 2.0 * np.pi, self.particle_count, endpoint=False)

    @staticmethod
    def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, value))

    @staticmethod
    def _smoothstep(value: float) -> float:
        value = ChidoriEffect._clamp(value)
        return value * value * (3.0 - 2.0 * value)

    @staticmethod
    def _ease_out_quad(value: float) -> float:
        value = ChidoriEffect._clamp(value)
        return 1.0 - ((1.0 - value) ** 2)

    def update(self, position, timestamp: float):
        """Update Chidori charge state and smoothed palm-following position."""
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

    def _render_core(self, overlay, center_x: int, center_y: int, progress: float):
        """Render the pulsing electrical core."""
        core_radius = self.base_radius * (0.16 + 0.8 * self._ease_out_quad(progress))
        pulse = 1.0 + 0.2 * np.sin(self.timestamp * 10.0)
        core_radius *= pulse

        cv2.circle(overlay, (center_x, center_y), int(core_radius * 0.9), (255, 255, 255), -1)
        cv2.circle(overlay, (center_x, center_y), int(core_radius * 1.25), (160, 230, 255), -1)
        cv2.circle(overlay, (center_x, center_y), int(core_radius * 1.75), (90, 180, 255), -1)

    def _render_glow(self, overlay, center_x: int, center_y: int, progress: float):
        """Render layered glow around the Chidori core and branches."""
        for layer_index in range(5):
            layer_progress = self._clamp(progress - layer_index * 0.12)
            if layer_progress <= 0.0:
                continue

            layer_scale = 1.2 + layer_index * 0.65 + layer_progress * 0.9
            glow_radius = int(self.base_radius * layer_scale)
            glow_color = (
                int(35 + layer_index * 20 + layer_progress * 35),
                int(110 + layer_index * 26 + layer_progress * 60),
                int(220 + layer_index * 12),
            )
            cv2.circle(overlay, (center_x, center_y), glow_radius, glow_color, thickness=-1)

    def _render_lightning_branches(self, overlay, center_x: int, center_y: int, progress: float):
        """Render irregular lightning branches from the palm core."""
        if progress < 0.15:
            return

        branch_count = max(3, int(3 + progress * self.branch_count))

        for branch_index in range(branch_count):
            branch_progress = self._clamp((progress - branch_index * 0.06) * 1.5)
            if branch_progress <= 0.0:
                continue

            angle = self.branch_angles[branch_index % len(self.branch_angles)]
            angle += 0.35 * np.sin(self.timestamp * 4.5 + branch_index * 1.7)
            base_length = self.branch_lengths[branch_index % len(self.branch_lengths)] * (0.55 + progress * 0.85)
            # The branch starts near the core and grows outward over time
            start_point = np.array([center_x, center_y], dtype=np.float32)
            points = [tuple(start_point.astype(int))]
            segment_count = 6

            for segment_index in range(1, segment_count + 1):
                t = segment_index / float(segment_count)
                local_angle = angle + np.sin(self.timestamp * (7.0 + branch_index) + segment_index * 1.8) * 0.4
                radial_distance = base_length * (t + 0.08 * np.sin(self.timestamp * 8.0 + branch_index))
                x = center_x + np.cos(local_angle) * radial_distance
                y = center_y + np.sin(local_angle) * radial_distance
                points.append((int(x), int(y)))

            brightness = 0.4 + branch_progress * 0.9
            stroke = max(1, int(1 + brightness * 2.5))
            branch_color = (int(120 + brightness * 60), int(170 + brightness * 70), 255)

            for point_index in range(len(points) - 1):
                p1 = points[point_index]
                p2 = points[point_index + 1]
                cv2.line(overlay, p1, p2, branch_color, stroke)

            # Add an additional faint glow line for each branch
            for point_index in range(len(points) - 1):
                p1 = points[point_index]
                p2 = points[point_index + 1]
                if point_index % 2 == 0:
                    cv2.line(overlay, p1, p2, (90, 200, 255), max(1, stroke - 1))

    def _render_particles(self, overlay, center_x: int, center_y: int, progress: float):
        """Render small electrical particles orbiting around the core."""
        if progress < 0.08:
            return

        for particle_index in range(self.particle_count):
            angle = self.particle_angles[particle_index] + self.timestamp * (1.2 + 0.08 * particle_index)
            orbit_radius = self.base_radius * (1.1 + 0.6 * progress) + 18.0 * np.sin(self.timestamp * 2.0 + particle_index)
            px = int(center_x + np.cos(angle) * orbit_radius)
            py = int(center_y + np.sin(angle) * orbit_radius)
            particle_size = max(1, int(1 + progress * 2.2))
            color = (int(120 + progress * 75), int(170 + progress * 60), 255)
            cv2.circle(overlay, (px, py), particle_size, color, -1)

    def _render_flicker(self, overlay, center_x: int, center_y: int, progress: float):
        """Add subtle electrical flicker pulses."""
        if progress < 0.18:
            return

        flicker_count = 5
        for flicker_index in range(flicker_count):
            offset_angle = self.timestamp * (8.0 + flicker_index) + flicker_index * 1.3
            radius = self.base_radius * (1.3 + progress * 0.7) + flicker_index * 12.0
            x = int(center_x + np.cos(offset_angle) * radius)
            y = int(center_y + np.sin(offset_angle) * radius)
            cv2.circle(overlay, (x, y), 2 + flicker_index, (180, 230, 255), -1)

    def render(self, frame):
        """Render the complete Chidori effect onto the webcam frame."""
        if not self.active:
            return frame

        progress = self._formation_progress()
        center = np.rint(self.position).astype(int)
        center_x, center_y = int(center[0]), int(center[1])
        overlay = np.zeros_like(frame)

        self._render_glow(overlay, center_x, center_y, progress)
        self._render_core(overlay, center_x, center_y, progress)
        self._render_lightning_branches(overlay, center_x, center_y, progress)
        self._render_particles(overlay, center_x, center_y, progress)
        self._render_flicker(overlay, center_x, center_y, progress)

        alpha = 0.62 + progress * 0.2
        return cv2.addWeighted(frame, 1.0, overlay, alpha, 0)

    def set_inactive(self):
        self.active = False
        self.charge = 0.0
        self.last_timestamp = None
