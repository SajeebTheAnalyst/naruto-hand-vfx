import cv2
import numpy as np


class RasenganEffect:
    """Procedural Rasengan-inspired energy orb with a charging formation phase."""

    def __init__(self, base_radius: int = 64, smoothing: float = 0.18, formation_duration: float = 2.2):
        self.base_radius = float(base_radius)
        self.smoothing = smoothing
        self.formation_duration = max(formation_duration, 0.1)

        self.position = np.array([0.0, 0.0], dtype=np.float32)
        self.target_position = np.array([0.0, 0.0], dtype=np.float32)
        self.active = False
        self.timestamp = 0.0
        self.charge = 0.0
        self.last_timestamp = None
        self.particle_count = 42
        self.particle_angles = np.linspace(0.0, 2.0 * np.pi, self.particle_count, endpoint=False)

    @staticmethod
    def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, value))

    @staticmethod
    def _smoothstep(value: float) -> float:
        value = RasenganEffect._clamp(value)
        return value * value * (3.0 - 2.0 * value)

    def update(self, position, timestamp: float):
        """Update the charge state and smooth palm-following position."""
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
        """Return the eased formation progress value from 0.0 to 1.0."""
        if not self.active:
            return 0.0
        return self._smoothstep(self.charge)

    def render(self, frame):
        """Render the charging Rasengan onto the webcam frame."""
        if not self.active:
            return frame

        progress = self._formation_progress()
        radius = self.base_radius * (0.12 + 0.88 * progress)
        center = np.rint(self.position).astype(int)
        center_x, center_y = int(center[0]), int(center[1])
        overlay = np.zeros_like(frame)

        # Small starting core grows into a bright blue-white sphere.
        core_radius = radius * (0.32 + 0.68 * progress)
        cv2.circle(overlay, (center_x, center_y), int(core_radius * 0.8), (255, 255, 255), -1)
        cv2.circle(overlay, (center_x, center_y), int(core_radius * 1.2), (120, 220, 255), -1)

        # Outer glow expands as the sphere charges up.
        for layer_index in range(5):
            radius_scale = 1.0 + layer_index * 0.45 + progress * 0.85
            glow_radius = int(radius * radius_scale)
            color = (
                int(35 + layer_index * 22 + progress * 40),
                int(110 + layer_index * 30 + progress * 70),
                int(220 + layer_index * 12),
            )
            cv2.circle(overlay, (center_x, center_y), glow_radius, color, thickness=-1)

        # Rings appear progressively rather than all at once.
        ring_count = 2 + int(progress * 4)
        ring_colors = [(80, 190, 255), (120, 220, 255), (150, 235, 255), (180, 240, 255), (200, 245, 255)]
        for ring_index in range(ring_count):
            if ring_index >= len(ring_colors):
                break
            if progress < (ring_index + 1) / (ring_count + 1):
                continue

            ring_scale = 1.15 + ring_index * 0.18 + progress * 0.24
            ring_radius_x = int(radius * ring_scale)
            ring_radius_y = int(radius * (0.52 + ring_index * 0.11))
            rotation = self.timestamp * (25.0 + ring_index * 12.0) * (1 if ring_index % 2 == 0 else -1)
            cv2.ellipse(
                overlay,
                (center_x, center_y),
                (ring_radius_x, ring_radius_y),
                rotation,
                0,
                360,
                ring_colors[ring_index],
                2,
            )

        # Particle orbit intensity and count rise with formation progress.
        for particle_index in range(self.particle_count):
            base_angle = self.particle_angles[particle_index]
            orbit_speed = 1.2 + particle_index * 0.04
            angle = base_angle + self.timestamp * orbit_speed
            orbit_base = radius * (1.1 + 0.28 * np.sin(self.timestamp * 2.0 + particle_index * 0.7))
            orbit_peak = orbit_base + (radius * 0.8 * progress)
            px = int(center_x + np.cos(angle) * orbit_peak)
            py = int(center_y + np.sin(angle) * orbit_peak)
            particle_radius = 2 + int((particle_index % 3) * (0.5 + progress))
            color = (int(145 + progress * 70), int(200 + progress * 43), int(255))
            cv2.circle(overlay, (px, py), particle_radius, color, -1)

        # Swirling trails intensify as the charge reaches full size.
        swirl_count = 4 + int(progress * 4)
        for swirl_index in range(swirl_count):
            angle_offset = self.timestamp * (1.2 + swirl_index * 0.4)
            swirl_radius = radius * (1.3 + swirl_index * 0.25)
            x1 = int(center_x + np.cos(angle_offset + swirl_index) * swirl_radius)
            y1 = int(center_y + np.sin(angle_offset + swirl_index) * swirl_radius)
            x2 = int(center_x + np.cos(angle_offset + swirl_index + 1.3) * (swirl_radius * 0.8))
            y2 = int(center_y + np.sin(angle_offset + swirl_index + 1.3) * (swirl_radius * 0.8))
            cv2.line(overlay, (x1, y1), (x2, y2), (120, 210, 255), 1)

        pulse_radius = int(radius * (0.8 + 0.12 * np.sin(self.timestamp * 8.0)))
        cv2.circle(overlay, (center_x, center_y), pulse_radius, (255, 255, 255), 2)

        return cv2.addWeighted(frame, 1.0, overlay, 0.78 + progress * 0.12, 0)

    def set_inactive(self):
        self.active = False
        self.charge = 0.0
        self.last_timestamp = None
