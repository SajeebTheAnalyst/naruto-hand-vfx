import cv2
import numpy as np


class EnergyBeamEffect:
    """Procedural energy beam that connects two detected palm centers."""

    def __init__(self, base_width: float = 24.0, smoothing: float = 0.18, formation_duration: float = 2.6):
        self.base_width = float(base_width)
        self.smoothing = smoothing
        self.formation_duration = max(formation_duration, 0.1)

        self.start_position = np.array([0.0, 0.0], dtype=np.float32)
        self.target_start_position = np.array([0.0, 0.0], dtype=np.float32)
        self.end_position = np.array([0.0, 0.0], dtype=np.float32)
        self.target_end_position = np.array([0.0, 0.0], dtype=np.float32)
        self.active = False
        self.timestamp = 0.0
        self.charge = 0.0
        self.last_timestamp = None

        self.particle_count = 28
        self.particle_offsets = np.linspace(0.0, 1.0, self.particle_count, endpoint=False)
        self.particle_speeds = np.linspace(0.18, 0.52, self.particle_count)
        self.particle_directions = np.array([1.0 if i % 2 == 0 else -1.0 for i in range(self.particle_count)], dtype=np.float32)

    @staticmethod
    def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, value))

    @staticmethod
    def _smoothstep(value: float) -> float:
        value = EnergyBeamEffect._clamp(value)
        return value * value * (3.0 - 2.0 * value)

    @staticmethod
    def _ease_out_quad(value: float) -> float:
        value = EnergyBeamEffect._clamp(value)
        return 1.0 - ((1.0 - value) ** 2)

    def update(self, start_point, end_point, timestamp: float):
        """Update the beam position and formation charge based on two palms."""
        if start_point is None or end_point is None:
            self.active = False
            self.charge = 0.0
            self.last_timestamp = None
            return

        self.target_start_position = np.asarray(start_point, dtype=np.float32)
        self.target_end_position = np.asarray(end_point, dtype=np.float32)
        self.start_position = self.start_position + (self.target_start_position - self.start_position) * self.smoothing
        self.end_position = self.end_position + (self.target_end_position - self.end_position) * self.smoothing

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

    def _beam_width(self, beam_length: float, progress: float) -> float:
        width = np.clip(beam_length * 0.07, 10.0, 42.0)
        return width * (0.45 + 0.8 * progress)

    def _draw_core(self, overlay, start, end, width, progress):
        """Render the bright central energy core."""
        beam_color = (255, 255, 255)
        core_width = max(2, int(width * 0.25 + 1.5 * progress))
        cv2.line(overlay, tuple(np.rint(start).astype(int)), tuple(np.rint(end).astype(int)), beam_color, core_width)

        inner_color = (120, 220, 255)
        inner_width = max(2, int(width * 0.42 + 1.5 * progress))
        cv2.line(overlay, tuple(np.rint(start).astype(int)), tuple(np.rint(end).astype(int)), inner_color, inner_width)

    def _draw_outer_layers(self, overlay, start, end, width, progress):
        """Render several outer energy layers for a softer beam rim."""
        vector = end - start
        beam_length = np.linalg.norm(vector)
        if beam_length < 1.0:
            return

        direction = vector / beam_length
        perpendicular = np.array([-direction[1], direction[0]], dtype=np.float32)
        layer_specs = [
            (0.9, (140, 180, 255), 1.0),
            (1.35, (100, 160, 255), 1.2),
            (1.8, (70, 130, 255), 1.5),
            (2.25, (35, 90, 255), 1.8),
        ]

        for layer_index, (multiplier, color, thickness_scale) in enumerate(layer_specs):
            oscillation = np.sin(self.timestamp * (3.0 + layer_index * 0.8) + layer_index) * width * 0.35
            offset = perpendicular * (oscillation + width * multiplier * 0.15)
            start_layer = start + offset
            end_layer = end + offset
            start_layer_alt = start - offset
            end_layer_alt = end - offset

            line_thickness = max(1, int(width * 0.18 * thickness_scale + 1.0 + progress * 2.0))
            cv2.line(overlay, tuple(np.rint(start_layer).astype(int)), tuple(np.rint(end_layer).astype(int)), color, line_thickness)
            cv2.line(overlay, tuple(np.rint(start_layer_alt).astype(int)), tuple(np.rint(end_layer_alt).astype(int)), color, line_thickness)

    def _draw_energy_streams(self, overlay, start, end, width, progress):
        """Create flowing energy streams as slightly offset, animated curves."""
        vector = end - start
        beam_length = np.linalg.norm(vector)
        if beam_length < 1.0:
            return

        direction = vector / beam_length
        perpendicular = np.array([-direction[1], direction[0]], dtype=np.float32)
        stream_count = 5

        for stream_index in range(stream_count):
            points = []
            stream_offset = (stream_index - (stream_count - 1) / 2.0) * (width * 0.16)
            for sample_index in range(12):
                t = sample_index / 11.0
                anchor = start + vector * t
                wave = np.sin(self.timestamp * (6.0 + stream_index * 0.8) + sample_index * 1.7 + stream_index) * width * 0.3
                offset = perpendicular * (wave + stream_offset)
                points.append(tuple(np.rint(anchor + offset).astype(int)))

            color = (int(150 + 50 * progress), int(200 + 30 * progress), 255)
            cv2.polylines(overlay, [np.array(points, dtype=np.int32)], False, color, 1)

    def _draw_particles(self, overlay, start, end, width, progress):
        """Render particles traveling along the beam in deterministic motion."""
        vector = end - start
        beam_length = np.linalg.norm(vector)
        if beam_length < 1.0:
            return

        direction = vector / beam_length
        perpendicular = np.array([-direction[1], direction[0]], dtype=np.float32)

        for particle_index in range(self.particle_count):
            offset_t = self.particle_offsets[particle_index]
            phase = (self.timestamp * self.particle_speeds[particle_index] + offset_t) % 1.0
            direction_sign = self.particle_directions[particle_index]
            t = (phase if direction_sign > 0 else 1.0 - phase)
            sample_point = start + vector * t
            wave = np.sin(self.timestamp * 8.0 + particle_index * 1.3) * width * 0.55
            drift = perpendicular * (wave + (particle_index % 5) * 2.5)
            particle_point = sample_point + drift
            radius = max(1, int(1.2 + progress * 2.0))
            color = (180, 230, 255)
            cv2.circle(overlay, tuple(np.rint(particle_point).astype(int)), radius, color, -1)

    def _draw_fragments(self, overlay, start, end, width, progress):
        """Add small energy fragments around the beam path."""
        vector = end - start
        beam_length = np.linalg.norm(vector)
        if beam_length < 1.0:
            return

        direction = vector / beam_length
        perpendicular = np.array([-direction[1], direction[0]], dtype=np.float32)
        fragment_count = 9

        for fragment_index in range(fragment_count):
            phase = (fragment_index / float(fragment_count)) + (self.timestamp * 0.28)
            phase = phase % 1.0
            sample_point = start + vector * phase
            orbital = np.sin(self.timestamp * (4.5 + fragment_index * 0.4) + fragment_index) * width * 0.9
            offset = perpendicular * orbital
            fragment = sample_point + offset
            radius = max(1, int(1 + progress * 2.0))
            color = (120, 220, 255)
            cv2.circle(overlay, tuple(np.rint(fragment).astype(int)), radius, color, -1)

    def render(self, frame):
        """Render the energy beam onto the live frame using additive compositing."""
        if not self.active:
            return frame

        progress = self._formation_progress()
        start = np.rint(self.start_position).astype(int)
        end = np.rint(self.end_position).astype(int)
        vector = end.astype(np.float32) - start.astype(np.float32)
        beam_length = np.linalg.norm(vector)
        if beam_length < 1.0:
            return frame

        overlay = np.zeros_like(frame)
        width = self._beam_width(beam_length, progress)

        self._draw_outer_layers(overlay, start.astype(np.float32), end.astype(np.float32), width, progress)
        self._draw_core(overlay, start.astype(np.float32), end.astype(np.float32), width, progress)
        self._draw_energy_streams(overlay, start.astype(np.float32), end.astype(np.float32), width, progress)
        self._draw_particles(overlay, start.astype(np.float32), end.astype(np.float32), width, progress)
        self._draw_fragments(overlay, start.astype(np.float32), end.astype(np.float32), width, progress)

        alpha = 0.72 + progress * 0.22
        return cv2.addWeighted(frame, 1.0, overlay, alpha, 0)

    def set_inactive(self):
        self.active = False
        self.charge = 0.0
        self.last_timestamp = None
