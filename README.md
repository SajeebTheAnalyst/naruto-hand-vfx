# Naruto Hand VFX Studio

Naruto Hand VFX Studio is a real-time hand-tracking VFX demo built with Python, OpenCV, MediaPipe, and NumPy. It turns webcam gestures into anime-inspired combat effects such as Rasengan, Chidori, Fireball, and a two-hand energy beam.

## Features

- Real-time hand tracking and palm-center extraction
- Gesture detection with smoothing and stability checks
- Single-hand VFX state management for Rasengan, Chidori, and Fireball
- Two-hand energy beam using both palms as endpoints
- Minimal overlay with status, effect, gesture, and FPS info
- Local desktop-first design with no external service dependency

## Controls

- Fist: Rasengan
- Pointing: Chidori
- Two fingers: Fireball
- Two hands with two fingers each: Energy Beam
- Open palm: clear active effect
- Q: exit
- Keyboard fallback: 0, 1, 2, 3, 4

## Run it

```powershell
cd "C:\Python Project\naruto-hand-vfx"
.venv\Scripts\activate
python main.py
```

## Project structure

```text
naruto-hand-vfx/
├── main.py
├── config.py
├── hand_tracker.py
├── gesture_detector.py
├── requirements.txt
├── README.md
├── .gitignore
├── hand_landmarker.task
├── vfx/
│   ├── __init__.py
│   ├── rasengan.py
│   ├── chidori.py
│   ├── fireball.py
│   └── energy_beam.py
```

## Notes

This is a polished Phase 8 production pass focused on app stability, cleaner status UI, camera fallback behavior, config-driven defaults, and a cleaner local project setup.