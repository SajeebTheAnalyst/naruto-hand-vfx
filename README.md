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
repository root/
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
cd "c:\Python Project"
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

## Phase 5: Chidori Lightning VFX

Phase 5 adds a separate procedural Chidori-style lightning effect that appears around the user's hand. The effect is generated procedurally using OpenCV and NumPy, and it is kept separate from the Rasengan effect so both can coexist cleanly in the same app.

### What Phase 5 adds

- **Electrical Core**: Pulsing blue/white energy core centered on the palm
- **Lightning Branches**: Multiple irregular branches radiate outward from the hand
- **Flicker Control**: Controlled electrical flicker adds motion without excessive flashing
- **Multi-layer Glow**: Soft blue-cyan glow builds around the core and branches
- **Electrical Particles**: Lighting particles orbit and drift around the core
- **Formation Animation**: Chidori grows from spark to full lightning energy through easing-driven stages
- **Gesture Mapping**: `POINTING` triggers Chidori while `FIST` keeps Rasengan active and `OPEN_PALM` disables everything

### Chidori visual architecture

The Chidori effect is implemented in `vfx/chidori.py` and is kept separate from the Rasengan logic.

Key components:

- `ChidoriEffect.__init__()`: stores effect sizing, timing, and deterministic branch/particle configuration
- `update()`: advances formation and smooths the palm-following position
- `_render_core()`: creates the bright electrical core and pulse
- `_render_glow()`: adds layered glow to the core and branches
- `_render_lightning_branches()`: draws irregular branching lightning paths
- `_render_particles()`: emits orbiting electrical particles
- `_render_flicker()`: adds subtle pulse/flicker around lightning structures
- `render()`: composites all lightning layers onto the camera frame

The Chidori is intentionally distinct from the Rasengan:

- Rasengan = swirling spherical energy orb
- Chidori = concentrated electrical lightning around the hand

### Gesture mapping

The current effect-selection behavior is:

- `FIST` → Rasengan active
- `POINTING` → Chidori active
- `OPEN_PALM` → no active effect
- `UNKNOWN` → keep the current effect state or safely clear it if no effect is active

This is handled in `main.py` by selecting one active effect at a time, without mixing Chidori and Rasengan rendering on the same frame.

### Effect state transitions

The effect state machine is intentionally simple and stable:

```
OPEN_PALM
    ↓
No effect

FIST
    ↓
Start Rasengan formation
    ↓
Active Rasengan

POINTING
    ↓
Stop Rasengan
    ↓
Start Chidori formation
    ↓
Active Chidori

OPEN_PALM
    ↓
Clear active effect
```

A continuous `POINTING` gesture does not restart the formation every frame. Only a transition such as `FIST -> POINTING` or `OPEN_PALM -> POINTING` triggers a fresh Chidori startup.

### How to test Chidori

1. Show an open palm → no effect should be active
2. Form a fist → Rasengan should become active
3. Switch from fist to pointing → Rasengan should deactivate and Chidori should begin forming
4. Keep pointing → Chidori should remain active and continue its lightning loop
5. Move the pointing hand → Chidori should follow smoothly
6. Return to open palm → Chidori should disable
7. Point again → Chidori should start a fresh formation

### Performance notes

- The Chidori effect uses deterministic branch angles and lightweight particle counts to stay real-time
- Glow and branch rendering are limited to keep the frame rate stable
- The effect avoids expensive repeated random generation by reusing deterministic animation data

### Current limitations

- Only one effect is active at a time (Rasengan or Chidori)
- Effects are still gesture-driven rather than pose- or context-aware
- Chidori is procedural and stylized rather than physically simulating lightning
- This phase does not add Fireball, Energy Beam, or GUI controls

## Phase 6: Fireball VFX

Phase 6 adds a fiery offensive effect that forms around the palm with a hot core, expanding flame shell, ember particles, and burst sparks. This version is intentionally distinct from both Rasengan and Chidori: where Rasengan is a controlled sphere and Chidori is an electrical storm, Fireball is an aggressive, volumetric flame mass with heat and motion.

### What Phase 6 adds

- **Hot Core**: A bright yellow-white flame center that pulses and intensifies over the charge cycle
- **Flame Shell**: Irregular orange-red perimeter that expands with layered, organic contouring
- **Emission Particles**: Ember and spark particles orbit the flame boundary and spread outward
- **Glow Spill**: Warm layered glow radiates from the core to suggest heat and pressure
- **Formation Animation**: The fireball grows from a small ignited core into a larger, roaring flame
- **Gesture Mapping**: `TWO_FINGERS` triggers Fireball while `FIST` remains Rasengan and `POINTING` remains Chidori
- **Active Effect Management**: Only one VFX is rendered at a time, ensuring stable effect transitions and no overlap

### Fireball visual architecture

The Fireball effect is implemented in `vfx/fireball.py` and is structured to mirror the other procedural VFX classes.

Key components:

- `FireballEffect.__init__()`: initializes size, smoothing, formation duration, and particle layout
- `update()`: advances charge progress and smooths palm-following motion
- `_render_hot_core()`: builds the glowing inner energy nucleus
- `_render_flame_shell()`: draws the irregular flame boundary with animated lobes
- `_render_glow()`: adds warm orange/red layered glow rings
- `_render_fire_particles()`: emits ember particles around the flame
- `_render_sparks()`: adds outward-moving spark trails
- `render()`: blends all layers onto the camera frame with alpha composition

### Effect state transitions

The stable effect flow for the full app becomes:

```
OPEN_PALM
    ↓
No effect

FIST
    ↓
Rasengan active

POINTING
    ↓
Chidori active

TWO_FINGERS
    ↓
Fireball active

OPEN_PALM
    ↓
Clear active effect
```

Only a gesture transition such as `POINTING -> TWO_FINGERS` or `OPEN_PALM -> TWO_FINGERS` triggers a fresh Fireball startup. Holding `TWO_FINGERS` keeps the effect active without restarting each frame.

### How to test Fireball

1. Show an open palm → no effect should be active
2. Form a fist → Rasengan should activate
3. Change to pointing → Chidori should activate
4. Form a two-finger peace/victory pose → Fireball should begin forming
5. Hold the two-finger pose → Fireball should remain active and animate smoothly
6. Return to open palm → all effects should clear

### Notes

- The fireball grows from a small flame core rather than appearing at full size immediately
- The effect remains procedural and uses deterministic animation values for stable output
- The flame shell and particles are intentionally irregular to avoid feeling mechanical
- The effect is designed to coexist within the same single-active-effect state machine as Rasengan and Chidori

## Phase 7: Two-Hand Energy Beam VFX

Phase 7 adds a procedural energy beam that connects the palm of one hand to the palm of a second detected hand. The beam is generated procedurally using OpenCV and NumPy, with a bright core, layered glow, animated streams, and particles traveling along the connecting axis.

### What Phase 7 adds

- **Two-hand tracking**: Up to two hands are now tracked at the same time using MediaPipe's multi-hand landmarker configuration
- **Stable palm centers**: Each recognized hand produces a palm-center position that is smoothed for fluid motion
- **Energy Beam geometry**: The beam start point is Hand 1's palm center and the end is Hand 2's palm center
- **Beam layers**: The beam contains a bright central core, cyan energy layers, glow halos, and animated outer rims
- **Energy streams**: Animated curving strands flow along the beam axis and remain visually attached to the beam
- **Particle flow**: Lightweight particles travel along the beam with directional motion and natural recycling
- **Formation animation**: The beam grows from a small connection into a fully formed energy blast with easing-driven intensity
- **Gesture activation**: `TWO_FINGERS + TWO_FINGERS` triggers the beam; a single `TWO_FINGERS` hand still activates Fireball

### Two-hand tracking changes

The tracker was updated to request `num_hands=2` while preserving the single-hand API used by the rest of the app.

The result is a structure like this:

```python
hands = [
    {"palm_center": (x1, y1), "landmarks": [...], "gesture": GestureType.TWO_FINGERS},
    {"palm_center": (x2, y2), "landmarks": [...], "gesture": GestureType.TWO_FINGERS},
]
```

This allows the app to:

- track both hands at once
- keep Hand 1 and Hand 2 ordering stable during normal motion
- render the beam between the two palm centers
- gracefully deactivate if one hand disappears or the gesture no longer matches

### Beam geometry

The beam is built from the vector between the two palms:

- `start point = Hand 1 palm center`
- `end point = Hand 2 palm center`
- `beam length = distance(start, end)`
- `beam width = clamped function of hand distance and formation progress`

The width is normalized so the beam stays visually strong without becoming oversized. When hands are close together, the beam narrows; when they are farther apart, the beam widens slightly.

### Energy Beam visual architecture

The beam effect is implemented in `vfx/energy_beam.py` and is kept separate from the main app loop.

Key components:

- `EnergyBeamEffect.__init__()`: stores beam size, timing, and deterministic particle layout
- `update()`: advances the formation charge and smooths the end-point movement
- `_draw_core()`: renders the bright luminous center of the beam
- `_draw_outer_layers()`: adds cyan and blue energy shells around the main beam
- `_draw_energy_streams()`: draws flowing animated strands along the beam axis
- `_draw_particles()`: animates particles moving from one hand to the other
- `_draw_fragments()`: adds small energy fragments around the beam to create a lively energetic feel
- `render()`: composites all beam layers using additive blending onto the frame

### Gesture mapping and effect transitions

The current effect mapping is:

```
OPEN_PALM
    ↓
No effect

FIST
    ↓
RASENGAN

POINTING
    ↓
CHIDORI

TWO_FINGERS + ONE HAND
    ↓
FIREBALL

TWO_FINGERS + TWO HANDS
    ↓
ENERGY_BEAM
```

The two-hand state logic is intentionally strict:

- both hands must show `TWO_FINGERS`
- if one hand is missing, no beam is activated
- if one hand changes gesture, the beam deactivates cleanly
- a transition into `ENERGY_BEAM` resets the formation progress once
- continuous beam activation does not restart the formation every frame

### Formation animation behavior

When both hands match the condition:

```
Hand 1 + Hand 2
    ↓
Small energy connection
    ↓
Beam starts forming
    ↓
Beam expands
    ↓
Energy intensity increases
    ↓
FULL ENERGY BEAM
```

The effect uses a `formation_progress` from `0.0` to `1.0` with smooth easing. Width, glow, particles, and beam intensity all ramp up during activation and remain alive after the beam is fully formed.

### Performance

The beam keeps the same performance constraints as the other VFX modules:

- lightweight particle counts
- deterministic animation to avoid per-frame random bursts
- additive blending only on the final result
- no expensive repeated allocations beyond the frame overlay and helper arrays

### How to test Phase 7

1. One hand + `FIST` → Rasengan should remain active
2. One hand + `POINTING` → Chidori should remain active
3. One hand + `TWO_FINGERS` → Fireball should remain active
4. Two hands + both `TWO_FINGERS` → Energy Beam should activate
5. Move Hand 1 → beam start should follow
6. Move Hand 2 → beam end should follow
7. Move both hands apart → beam length grows
8. Move both hands together → beam shortens
9. Keep both hands still → beam animation continues while holding its connection
10. Remove one hand → beam deactivates safely
11. Switch one hand away from `TWO_FINGERS` → beam deactivates
12. Re-enter the two-hand gesture → formation begins again

### Current limitations

- This is still a procedural prototype and not a final VFX engine
- The beam uses deterministic animation and geometric shaping rather than physics simulation
- Hand ordering is stable under normal motion, but extreme rapid swaps may still cause minor visual jitter
- The visual result is tuned for stylized anime energy effects rather than physically accurate beams

### Future Phases

Potential enhancements for future phases:
- **Phase 8**: More advanced multi-hand gesture combinations and triggers
- **Phase 9**: Scene composition, hand distance scaling, and energy tuning
- **Phase 10**: Audio and export tools
