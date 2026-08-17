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
