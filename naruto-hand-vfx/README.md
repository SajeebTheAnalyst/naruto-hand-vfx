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

## Phase 4: Reusable Hand Gesture Recognition Engine

Phase 4 introduces a gesture-recognition system that detects hand poses from MediaPipe landmarks and uses them to control the Rasengan effect.

### What Phase 4 adds

- **Geometric Gesture Recognition**: Detects hand poses using MediaPipe's 21 hand landmarks and geometric relationships.
- **Six Supported Gestures**:
  - `OPEN_PALM` — All/most fingers extended
  - `FIST` — Most fingers folded
  - `POINTING` — Index finger extended, others folded
  - `TWO_FINGERS` — Index + middle fingers extended, others folded
  - `THUMBS_UP` — Thumb pointing upward, others folded
  - `UNKNOWN` — Doesn't match any recognized gesture
- **Temporal Smoothing**: Recent gesture history is maintained to prevent frame-to-frame flickering.
- **Gesture-based Rasengan Control**:
  - `FIST` → Rasengan formation activates
  - `OPEN_PALM` → Rasengan deactivates
  - `OTHER` → Previous state is maintained
- **On-Screen Debug Info**: Current gesture, Rasengan state, and FPS are displayed.

### Gesture Detection Approach

The `GestureDetector` class uses normalized geometric measurements:

1. **Hand Scale Reference**: Distance from wrist to middle finger tip is used to normalize all measurements.
2. **Finger Extension Check**: Compares the distance between finger tip and base (MCP) relative to hand scale.
3. **Fold Detection**: Determines if a finger is folded by checking if the tip is close to its base.
4. **Specific Gestures**:
   - **OPEN_PALM**: Most/all fingers extended (threshold ≥ 4/5 fingers)
   - **FIST**: Most fingers folded (threshold ≥ 4/5 fingers)
   - **POINTING**: Index extended, others (except thumb) folded
   - **TWO_FINGERS**: Index + middle extended, ring + pinky folded
   - **THUMBS_UP**: Thumb extended upward (tip above wrist), others folded

**Why No External ML Model?**

- Geometric gesture detection is lightweight and requires no model downloads.
- Works reliably in real-time without GPU overhead.
- Naturally handles different hand sizes and distances.
- Simple to understand, debug, and extend with new gestures.

### Temporal Smoothing

The `GestureDetector` maintains a short history of recent predictions (default 5 frames).

A gesture change is only applied when:
- The new gesture remains consistent for at least 2-3 recent frames
- This prevents flickering from brief misclassifications

### Rasengan State Behavior

```
OPEN_PALM (Initial)
    ↓
Rasengan: INACTIVE

[Hand shape changes to FIST]
    ↓
Rasengan formation starts
    ↓
Rasengan: ACTIVE (and grows)

[Continuous FIST]
    ↓
Formation completes
    ↓
Rasengan remains fully formed
    ↓
Formation animation does NOT restart

[FIST to OPEN_PALM]
    ↓
Rasengan: INACTIVE (deactivates)

[OPEN_PALM to FIST]
    ↓
New formation animation begins
```

### Architecture

**File Structure**:

```
naruto-hand-vfx/
├── main.py                 # App entry point (Phase 4: gesture integration)
├── hand_tracker.py         # MediaPipe wrapper (unchanged)
├── gesture_detector.py     # NEW: Gesture recognition engine
├── vfx/
│   ├── __init__.py
│   └── rasengan.py         # Rasengan VFX (unchanged)
├── requirements.txt        # Dependencies
├── README.md               # Documentation
└── hand_landmarker.task    # MediaPipe model asset
```

**GestureDetector API**:

```python
from gesture_detector import GestureDetector, GestureType

detector = GestureDetector(history_length=5)

# Each frame:
gesture = detector.detect(landmarks)  # Returns GestureType enum
print(gesture.value)  # e.g., "OPEN_PALM", "FIST", "UNKNOWN"
```

### On-Screen Debug Information

**Displayed Elements**:

1. **Palm Position**: Coordinates of the detected palm center
2. **Gesture Label**: Current detected gesture (green if recognized, red if UNKNOWN)
3. **Rasengan State**: ACTIVE or INACTIVE
4. **FPS**: Frames per second

**Example Output**:

```
Palm: (320, 240)
Gesture: FIST
Rasengan: ACTIVE
FPS: 28.5
```

### Testing the Gesture Engine

**Single Gesture Tests**:

1. Show an **Open Palm** → Verify gesture label shows "OPEN_PALM"
2. Make a **Fist** → Verify label shows "FIST"
3. Extend **Index only** → Verify label shows "POINTING"
4. Extend **Index + Middle** → Verify label shows "TWO_FINGERS"
5. Make **Thumbs Up** → Verify label shows "THUMBS_UP"
6. Hold an ambiguous pose → Verify label shows "UNKNOWN"

**Gesture Stability Test**:

- Hold a gesture for 2+ seconds → Should remain stable (no flickering)
- Slowly transition gestures → Label should smoothly update

**Rasengan Control Test**:

```
1. Open hand
   → Verify: "Gesture: OPEN_PALM", "Rasengan: INACTIVE"
   
2. Close hand (FIST)
   → Verify: "Gesture: FIST", "Rasengan: ACTIVE"
   → Rasengan should begin formation animation
   
3. Keep hand closed
   → Formation should complete
   → Rasengan should remain fully formed
   → Formation should NOT restart every frame
   
4. Move the closed hand
   → Rasengan should smoothly follow the palm
   
5. Open hand again
   → Verify: "Gesture: OPEN_PALM", "Rasengan: INACTIVE"
   → Rasengan should deactivate
   
6. Close hand once more
   → Formation animation should restart fresh
```

### Performance

- **Gesture Detection**: Negligible overhead (~1-2ms per frame)
- **Target FPS**: 25-30+ FPS maintained
- **No model download required**: Uses only mathematical calculations
- **Scalable**: Easy to add new gestures without retraining

### Known Limitations & Robustness

**Good Robustness**:

- ✅ Handles left and right hands
- ✅ Works across different hand sizes
- ✅ Robust to small movements/shaking
- ✅ Handles different distances from webcam (through normalization)

**Edge Cases**:

- ⚠️ Very close to camera: Hand landmarks may be distorted
- ⚠️ Extreme angles: Some gestures may be hard to distinguish
- ⚠️ Overlapping hands: Only detects the dominant hand
- ⚠️ Partial occlusion: Gestures may fail if fingers are hidden

**Unreliable Gestures**:

If any gesture is inconsistent, adjusting thresholds in `gesture_detector.py` can improve detection.

---

## Run the application

From the project folder in a terminal:

```powershell
cd "c:\Python Project\naruto-hand-vfx"
& "C:/Users/England/AppData/Local/Programs/Python/Python312/python.exe" -m pip install -r requirements.txt
& "C:/Users/England/AppData/Local/Programs/Python/Python312/python.exe" main.py
```

## Controls

- Press Q to quit the application.
- Use hand gestures to control the Rasengan:
  - **FIST**: Activate Rasengan
  - **OPEN_PALM**: Deactivate Rasengan

## Current limitations

- This is a procedural prototype only; it is not yet a full VFX engine.
- Gesture detection uses geometric heuristics (not machine learning).
- Only one hand is tracked at a time.
- The Rasengan uses a fixed size; future phases may scale based on hand distance.
- This phase intentionally does not include Chidori, fireballs, beams, GUI, sound, or external assets.

## Future Phases

Potential enhancements for future phases:
- **Phase 5**: Multiple VFX types (Chidori, Fireball, Energy Beam) with gesture selection
- **Phase 6**: Advanced gesture combinations (two-finger swipe to throw, etc.)
- **Phase 7**: Hand distance-based scaling
- **Phase 8**: Sound effects and audio feedback
- **Phase 9**: Recording/export capabilities
