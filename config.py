from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Application-level defaults used for webcam setup and runtime tuning."""

    camera_index: int = 0
    frame_width: int = 640
    frame_height: int = 480
    target_fps: float = 30.0
    gesture_history_length: int = 5
    vfx_scale: float = 1.0
    particle_density: float = 1.0
    glow_strength: float = 1.0
    enable_keyboard_controls: bool = True
    debug_overlay: bool = False
    show_status_panel: bool = True

    @classmethod
    def from_args(cls, argv=None) -> "AppConfig":
        parser = argparse.ArgumentParser(description="Naruto Hand VFX Studio")
        parser.add_argument("--camera-index", type=int, default=0, help="Webcam index to use")
        parser.add_argument("--width", type=int, default=640, help="Capture frame width")
        parser.add_argument("--height", type=int, default=480, help="Capture frame height")
        parser.add_argument("--target-fps", type=float, default=30.0, help="Soft FPS target")
        parser.add_argument("--gesture-history", type=int, default=5, help="Gesture smoothing history length")
        parser.add_argument("--vfx-scale", type=float, default=1.0, help="Global VFX scale multiplier")
        parser.add_argument("--particle-density", type=float, default=1.0, help="Particle density multiplier")
        parser.add_argument("--glow-strength", type=float, default=1.0, help="Glow strength multiplier")
        parser.add_argument("--no-keyboard", action="store_true", help="Disable keyboard fallback controls")
        parser.add_argument("--debug-overlay", action="store_true", help="Render extra debug frames")
        parser.add_argument("--hide-overlay", action="store_true", help="Hide the status panel for clean recording")
        args = parser.parse_args(argv)

        return cls(
            camera_index=max(0, args.camera_index),
            frame_width=max(320, args.width),
            frame_height=max(240, args.height),
            target_fps=max(10.0, args.target_fps),
            gesture_history_length=max(2, args.gesture_history),
            vfx_scale=max(0.5, args.vfx_scale),
            particle_density=max(0.5, args.particle_density),
            glow_strength=max(0.5, args.glow_strength),
            enable_keyboard_controls=not args.no_keyboard,
            debug_overlay=args.debug_overlay,
            show_status_panel=not args.hide_overlay,
        )
