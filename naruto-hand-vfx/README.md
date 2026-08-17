# Naruto Hand VFX Studio

Naruto Hand VFX Studio is a procedural computer-vision prototype focused on real-time hand tracking and a Rasengan-inspired energy effect.

## Phase 1 summary

Phase 1 established the camera pipeline and stable palm detection using MediaPipe HandLandmarker.

- Open the default webcam
- Detect a single hand reliably
- Draw landmarks and connections on the frame
- Estimate a palm-center position from the hand landmarks
- Show the palm center and FPS on screen
- Handle no-hand states gracefully
- Exit cleanly when the user presses Q

## Phase 2: Rasengan VFX prototype

This phase adds a procedural blue Rasengan-style energy sphere that follows the palm center in real time and charges up from a small core into a full-form energy orb.

### What Phase 2 adds

- A charged Rasengan that starts tiny and grows smoothly from the palm
- Blue/white core intensification as the formation completes
- Layered outer glow that expands with the charge state
- Progressive ring formation instead of all rings appearing at once
- Deterministic particles that orbit and converge toward the sphere during formation
- Palm-following smoothing so the effect moves smoothly instead of jittering
- Rendering on top of the live webcam feed with alpha blending
- Formation reset when a hand disappears and re-trigger when a new hand appears

### How the Rasengan is generated

The Rasengan effect is produced programmatically using OpenCV and NumPy:

- The palm center from MediaPipe is used as the target position.
- A smoothed position keeps the effect stable while following the hand.
- A normalized charge value from 0.0 to 1.0 controls the formation animation.
- Smooth easing is used so the core, glow, particles, and rings grow naturally instead of scaling linearly.
- The radius, glow density, particle count/activity, ring visibility, and swirl intensity all respond to the formation progress.
- The final result is composited onto the webcam frame with alpha blending.

### Formation behavior

The Rasengan now follows a staged energy buildup:

- Tiny core at first detection
- Small glow and initial particles
- Expanding sphere with more active particle motion
- Rings emerging progressively as the charge completes
- Full Rasengan once the charge reaches 1.0

When the hand disappears, the formation state resets. When a hand reappears, the animation begins again from the small core.

## Phase 3: Dynamic Rasengan Formation / Charging Animation

Phase 3 dramatically enhances the visual quality and realism of the Rasengan formation by implementing detailed charging stages. The effect now visually evolves through four distinct phases as the energy gathers in the user's palm.

### What Phase 3 adds

- **Detailed Formation Stages**: The Rasengan now forms through clearly defined visual stages instead of a simple linear growth.
- **Energy Core Stage (0-20%)**: Starts as a tiny bright blue/white energy core with subtle glow.
- **Energy Gathering Stage (20-50%)**: Core expands, glow intensifies, particles activate and orbit the developing core.
- **Rasengan Formation Stage (50-80%)**: Full sphere growth, rotating rings progressively appear, particle density increases, energy swirls become visible.
- **Full Formation Stage (80-100%)**: Smooth completion to full size, all components reach maximum intensity without visual jumping.
- **Organic Animation**: Multiple visual properties animate independently (core radius, glow layers, particle count/speed, ring visibility/rotation, energy intensity) for a dynamic, non-linear feel.
- **Easing Functions**: Uses smoothstep and ease-out cubic/quadratic curves to create responsive, smooth transitions instead of mechanical scaling.
- **Responsive Particles**: Particle count, speed, and orbit radius all respond to formation progress, creating a sense of converging energy.
- **Progressive Ring Formation**: Rings appear one at a time with increasing opacity and rotation speed as the Rasengan charges.
- **Energy Swirls**: Subtle swirling energy trails intensify during the final formation stages.
- **Responsive Glow**: Five-layer glow system expands and brightens as formation progresses, creating a luminous effect.

### Formation Timeline

```
Hand Detected
     ↓
Stage 1: Energy Core (0-20%)
  • 12% → 40% of base radius
  • White center with blue surround
  • Subtle glow
  • 0-10% of particles visible
     ↓
Stage 2: Energy Gathering (20-50%)
  • Core continues to 40% radius
  • Glow expands 1.2x → 3.5x base radius
  • 10-35% of particles visible
  • Particles orbit and converge
     ↓
Stage 3: Rasengan Formation (50-80%)
  • Rings begin appearing (2 → 5 rings)
  • Glow reaches maximum layers
  • 35-80% of particles visible
  • Particle speed increases
  • Energy swirls become visible
     ↓
Stage 4: Full Formation (80-100%)
  • Smooth transition to full size
  • All visual components reach maximum intensity
  • No sudden visual jumps
     ↓
Fully Formed (100%+)
  • Rasengan remains at full size
  • Continues rotating rings
  • Continuous particle motion
  • Sustained energy animation
  • Follows palm smoothly
     ↓
Hand Disappears
  • Effect fades and resets
  • Formation state returns to 0.0
     ↓
Hand Reappears
  • New formation animation begins from tiny core
```

### Visual Components

1. **Energy Core**: Bright white and cyan center that grows with formation progress
2. **Layered Glow**: Five concentric glow layers that expand and brighten
3. **Rotating Rings**: 2-5 elliptical rings that spin at increasing speeds, appearing progressively
4. **Orbiting Particles**: 48 deterministic particles that follow orbital paths with breathing motion
5. **Energy Swirls**: Swirling trails that intensify during final formation stages
6. **Pulse Outline**: Subtle pulsing circle around the core for visual emphasis

### Performance & Stability

- **Real-time Performance**: Maintains 25-30+ FPS on typical hardware
- **Deterministic Particles**: Particle angles are precomputed for consistent rendering
- **Efficient Rendering**: All expensive calculations are precomputed or reused
- **Smooth Palm Following**: Position smoothing prevents jitter while maintaining responsiveness
- **Formation Duration**: Default 2.5 seconds per formation cycle (configurable)

### Implementation Details

The Phase 3 Rasengan is implemented in `vfx/rasengan.py` with the following key methods:

- `_formation_progress()`: Returns eased 0-1 progress value
- `_render_core()`: Renders the bright energy core
- `_render_glow()`: Renders the expanding glow layers
- `_render_rings()`: Renders the rotating elliptical rings
- `_render_particles()`: Renders orbiting particles
- `_render_energy_swirls()`: Renders swirling energy trails
- `_render_pulse()`: Renders the pulsing outline
- `render()`: Composites all layers and applies them to the frame

All rendering uses OpenCV and NumPy—no external assets or images.

## Run the application

From the project folder in a terminal:

```powershell
cd "c:\Python Project\naruto-hand-vfx"
& "C:/Users/England/AppData/Local/Programs/Python/Python312/python.exe" -m pip install -r requirements.txt
& "C:/Users/England/AppData/Local/Programs/Python/Python312/python.exe" main.py
```

## Controls

- Press Q to quit the application.

## Current limitations

- This is a procedural prototype only; it is not yet a full VFX engine.
- The Rasengan is active whenever a hand is detected and does not use gesture activation.
- The effect uses a fixed size and can later be adapted to hand distance or scale.
- This phase intentionally does not include Chidori, fireballs, beams, particles beyond the local sphere, or external assets.
- Sound effects are not implemented.
- Recording/export features are not implemented.

## Future Phases

Potential enhancements for future phases:
- Gesture-based activation (hand poses to trigger/release Rasengan)
- Multiple VFX types (Chidori, Fireball, Energy Beam)
- Hand distance-based scaling
- Sound effects
- Recording/export capabilities
