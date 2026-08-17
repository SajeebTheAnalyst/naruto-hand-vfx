import cv2
import numpy as np


class RasenganEffect:
    """
    Phase 3: Dynamic Rasengan Formation with detailed charging animation.
    
    The Rasengan forms from a tiny energy core and gradually grows into a full-size effect,
    with distinct visual stages for energy core, energy gathering, formation, and completion.
    """

    def __init__(self, base_radius: int = 64, smoothing: float = 0.18, formation_duration: float = 2.5):
        self.base_radius = float(base_radius)
        self.smoothing = smoothing
        self.formation_duration = max(formation_duration, 0.1)

        self.position = np.array([0.0, 0.0], dtype=np.float32)
        self.target_position = np.array([0.0, 0.0], dtype=np.float32)
        self.active = False
        self.timestamp = 0.0
        self.charge = 0.0  # 0.0 to 1.0, linear progression over formation_duration
        self.last_timestamp = None
        
        # Precomputed particle angles for deterministic orbit paths
        self.particle_count = 48
        self.particle_angles = np.linspace(0.0, 2.0 * np.pi, self.particle_count, endpoint=False)
        
        # Precomputed ring parameters for consistent rendering
        self.ring_colors = [
            (80, 190, 255),
            (120, 220, 255),
            (150, 235, 255),
            (180, 240, 255),
            (200, 245, 255),
        ]

    @staticmethod
    def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        """Clamp a value between minimum and maximum."""
        return max(minimum, min(maximum, value))

    @staticmethod
    def _smoothstep(value: float) -> float:
        """Hermite smoothstep easing function for smooth interpolation."""
        value = RasenganEffect._clamp(value)
        return value * value * (3.0 - 2.0 * value)
    
    @staticmethod
    def _ease_out_cubic(value: float) -> float:
        """Ease-out cubic for fast start and smooth deceleration."""
        value = RasenganEffect._clamp(value)
        return 1.0 - ((1.0 - value) ** 3)
    
    @staticmethod
    def _ease_out_quad(value: float) -> float:
        """Ease-out quadratic for gentle deceleration."""
        value = RasenganEffect._clamp(value)
        return 1.0 - ((1.0 - value) ** 2)

    def update(self, position, timestamp: float):
        """
        Update the charge state and smooth palm-following position.
        
        Args:
            position: (x, y) tuple for the target palm center, or None if no hand detected
            timestamp: Current time in seconds (typically from time.perf_counter())
        """
        if position is None:
            self.active = False
            self.charge = 0.0
            self.last_timestamp = None
            return

        target = np.asarray(position, dtype=np.float32)
        self.target_position = target
        # Smooth palm-following position to avoid jitter
        self.position = self.position + (self.target_position - self.position) * self.smoothing

        if not self.active:
            # Hand just appeared: start formation from scratch
            self.active = True
            self.charge = 0.0
            self.last_timestamp = timestamp
        elif self.last_timestamp is not None:
            dt = max(0.016, timestamp - self.last_timestamp)
            # Linearly increment charge over formation_duration
            self.charge = min(1.0, self.charge + dt / self.formation_duration)

        self.last_timestamp = timestamp
        self.timestamp = timestamp

    def _formation_progress(self) -> float:
        """Return the eased formation progress value from 0.0 to 1.0."""
        if not self.active:
            return 0.0
        # Use smoothstep for overall easing
        return self._smoothstep(self.charge)

    def _get_stage_progress(self, stage_start: float, stage_end: float) -> float:
        """
        Get the progress within a specific formation stage.
        
        Args:
            stage_start: Start of stage as fraction of total progress (0.0-1.0)
            stage_end: End of stage as fraction of total progress (0.0-1.0)
        
        Returns:
            Progress within stage (0.0-1.0), or 0.0 if not yet in stage, 1.0 if past stage
        """
        progress = self._formation_progress()
        if progress < stage_start:
            return 0.0
        if progress >= stage_end:
            return 1.0
        return (progress - stage_start) / (stage_end - stage_start)

    def _render_core(self, overlay, center_x: int, center_y: int, progress: float):
        """
        Render the bright blue/white energy core.
        
        Stage 0.0-1.0: Core grows from 12% to 40% of base radius
        """
        core_radius_min = self.base_radius * 0.12
        core_radius_max = self.base_radius * 0.40
        
        # Use ease-out cubic for responsive core growth
        eased = self._ease_out_cubic(progress)
        core_radius = core_radius_min + (core_radius_max - core_radius_min) * eased
        
        # Bright white center
        cv2.circle(overlay, (center_x, center_y), int(core_radius * 0.8), (255, 255, 255), -1)
        
        # Blue/cyan surrounding
        cv2.circle(overlay, (center_x, center_y), int(core_radius * 1.1), (200, 240, 255), -1)

    def _render_glow(self, overlay, center_x: int, center_y: int, progress: float):
        """
        Render the expanding layered glow around the core.
        
        Stage 0.0-1.0: Glow expands and intensifies
        """
        base_intensity = progress * 0.85  # Ramp up intensity
        
        # 5 glow layers expanding outward
        for layer_idx in range(5):
            # Each layer progressively appears
            layer_progress = self._clamp(progress - layer_idx * 0.15)
            if layer_progress <= 0.0:
                continue
            
            # Layer radius grows with progress
            layer_scale = 1.2 + layer_idx * 0.45 + layer_progress * 0.7
            glow_radius = int(self.base_radius * layer_scale)
            
            # Color gets brighter as we progress
            brightness_boost = layer_progress * 60
            color = (
                int(35 + layer_idx * 22 + brightness_boost),
                int(110 + layer_idx * 30 + brightness_boost),
                int(220 + layer_idx * 12),
            )
            
            cv2.circle(overlay, (center_x, center_y), glow_radius, color, thickness=-1)

    def _render_rings(self, overlay, center_x: int, center_y: int, progress: float):
        """
        Render the rotating energy rings.
        
        Stages: Start appearing at 0.45 progress, fully visible by 0.85
        """
        # Rings don't appear until we're well into formation
        if progress < 0.40:
            return
        
        # Ring visibility ramps up
        ring_progress = (progress - 0.40) / 0.60
        
        # Start with 2 rings, ramp up to 5 by full formation
        max_ring_count = 2 + int(ring_progress * 3)
        
        for ring_idx in range(max_ring_count):
            # Each ring appears progressively
            ring_appearance_progress = self._clamp((ring_progress - ring_idx * 0.25) * 1.5)
            if ring_appearance_progress <= 0.0:
                continue
            
            # Ring size grows with appearance
            ring_scale = 1.15 + ring_idx * 0.18 + ring_appearance_progress * 0.35
            ring_radius_x = int(self.base_radius * ring_scale)
            ring_radius_y = int(self.base_radius * (0.52 + ring_idx * 0.11))
            
            # Rotation speed increases with progress
            rotation_speed = 25.0 + ring_idx * 12.0 + ring_progress * 15.0
            rotation = self.timestamp * rotation_speed * (1 if ring_idx % 2 == 0 else -1)
            
            # Ring color and thickness
            if ring_idx < len(self.ring_colors):
                ring_color = self.ring_colors[ring_idx]
            else:
                ring_color = (200, 245, 255)
            
            # Thickness increases as ring becomes fully visible
            thickness = max(2, int(1 + ring_appearance_progress * 2))
            
            cv2.ellipse(
                overlay,
                (center_x, center_y),
                (ring_radius_x, ring_radius_y),
                rotation,
                0,
                360,
                ring_color,
                thickness,
            )

    def _render_particles(self, overlay, center_x: int, center_y: int, progress: float):
        """
        Render orbiting and converging particles around the Rasengan.
        
        Stage 0.0-1.0: Particle count, speed, and orbit radius all increase
        """
        stage_progress = progress
        
        # Particle visibility ramps up
        visible_particle_count = int(self.particle_count * self._ease_out_quad(stage_progress))
        
        # Particle speed increases as the effect charges
        speed_multiplier = 0.6 + stage_progress * 0.8
        
        for particle_idx in range(visible_particle_count):
            base_angle = self.particle_angles[particle_idx]
            orbit_speed = (1.2 + particle_idx * 0.04) * speed_multiplier
            angle = base_angle + self.timestamp * orbit_speed
            
            # Base orbit radius, with a subtle breathing motion
            breath = 0.28 * np.sin(self.timestamp * 2.0 + particle_idx * 0.7)
            orbit_base = self.base_radius * (1.1 + breath)
            
            # Orbit radius grows with formation progress
            orbit_max_expansion = self.base_radius * 0.8
            orbit_radius = orbit_base + orbit_max_expansion * stage_progress
            
            px = int(center_x + np.cos(angle) * orbit_radius)
            py = int(center_y + np.sin(angle) * orbit_radius)
            
            # Particle size grows slightly with progress
            particle_size = 2 + int((particle_idx % 3) * (0.6 + stage_progress * 0.8))
            
            # Particle color intensifies
            blue_base = 255
            green_base = int(200 + stage_progress * 43)
            red_base = int(145 + stage_progress * 70)
            color = (red_base, green_base, blue_base)
            
            cv2.circle(overlay, (px, py), max(1, particle_size), color, -1)

    def _render_energy_swirls(self, overlay, center_x: int, center_y: int, progress: float):
        """
        Render swirling energy trails that intensify during formation.
        
        Stage 0.60-1.0: Energy swirls become more visible
        """
        if progress < 0.50:
            return
        
        swirl_progress = (progress - 0.50) / 0.50
        swirl_count = int(4 + swirl_progress * 4)
        
        for swirl_idx in range(swirl_count):
            swirl_visibility = self._clamp((swirl_progress - swirl_idx * 0.15) * 2.0)
            if swirl_visibility <= 0.0:
                continue
            
            angle_offset = self.timestamp * (1.2 + swirl_idx * 0.4)
            swirl_radius = self.base_radius * (1.3 + swirl_idx * 0.25)
            
            x1 = int(center_x + np.cos(angle_offset + swirl_idx) * swirl_radius)
            y1 = int(center_y + np.sin(angle_offset + swirl_idx) * swirl_radius)
            x2 = int(center_x + np.cos(angle_offset + swirl_idx + 1.3) * (swirl_radius * 0.8))
            y2 = int(center_y + np.sin(angle_offset + swirl_idx + 1.3) * (swirl_radius * 0.8))
            
            # Swirl color and intensity
            alpha = int(swirl_visibility * 100)
            color = (120, 210, 255)
            
            cv2.line(overlay, (x1, y1), (x2, y2), color, max(1, int(swirl_visibility * 2)))

    def _render_pulse(self, overlay, center_x: int, center_y: int, progress: float):
        """
        Render a subtle pulsing outline around the core.
        
        Stage 0.0-1.0: Pulse becomes more pronounced
        """
        # Pulse is always active but more visible when fully formed
        pulse_base = self.base_radius * (0.8 + 0.12 * np.sin(self.timestamp * 8.0))
        pulse_intensity = int(200 + progress * 55)  # Gets brighter with progress
        
        cv2.circle(overlay, (center_x, center_y), int(pulse_base), (pulse_intensity, pulse_intensity, 255), 2)

    def render(self, frame):
        """
        Render the complete Rasengan formation animation onto the frame.
        
        This implements Phase 3 with detailed charging stages:
        - 0.0-0.20: Energy Core (tiny bright center)
        - 0.20-0.50: Energy Gathering (core grows, glow intensifies)
        - 0.50-0.80: Rasengan Formation (rings appear, particles increase)
        - 0.80-1.0: Full Formation (smooth completion to full size)
        - 1.0+: Fully Formed (sustained full-size effect)
        """
        if not self.active:
            return frame

        progress = self._formation_progress()
        center = np.rint(self.position).astype(int)
        center_x, center_y = int(center[0]), int(center[1])
        
        # Create overlay for all VFX layers
        overlay = np.zeros_like(frame)

        # Render all components (they self-regulate based on progress)
        self._render_core(overlay, center_x, center_y, progress)
        self._render_glow(overlay, center_x, center_y, progress)
        self._render_rings(overlay, center_x, center_y, progress)
        self._render_particles(overlay, center_x, center_y, progress)
        self._render_energy_swirls(overlay, center_x, center_y, progress)
        self._render_pulse(overlay, center_x, center_y, progress)

        # Composite overlay onto frame with progressive alpha
        # As formation completes, the effect becomes more opaque
        base_alpha = 0.70
        final_alpha = base_alpha + progress * 0.20  # Max 0.90 when fully formed
        
        return cv2.addWeighted(frame, 1.0, overlay, final_alpha, 0)

    def set_inactive(self):
        self.active = False
        self.charge = 0.0
        self.last_timestamp = None
