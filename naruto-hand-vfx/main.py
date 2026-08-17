import sys
import time

import cv2

from hand_tracker import HandTracker
from gesture_detector import GestureDetector, GestureType
from vfx.rasengan import RasenganEffect


class NarutoHandVFXApp:
    """Phase 4 webcam app with gesture recognition controlling the Rasengan effect."""

    def __init__(self, camera_index: int = 0, frame_width: int = 640, frame_height: int = 480):
        self.tracker = HandTracker(camera_index=camera_index, frame_width=frame_width, frame_height=frame_height)
        self.effect = RasenganEffect(base_radius=62, smoothing=0.18, formation_duration=2.5)
        self.gesture_detector = GestureDetector(history_length=5)
        self.previous_gesture = GestureType.UNKNOWN
        self.rasengan_active = False

    def run(self) -> None:
        """Main webcam loop for Phase 4 with gesture-based Rasengan control."""
        prev_time = time.perf_counter()

        try:
            while True:
                success, frame = self.tracker.cap.read()
                if not success:
                    print("Failed to grab a frame from the webcam.")
                    break

                frame = cv2.flip(frame, 1)
                palm_center, landmarks = self.tracker.process_frame(frame)

                current_gesture = GestureType.UNKNOWN

                if palm_center is not None and landmarks is not None:
                    # Detect gesture from landmarks
                    current_gesture = self.gesture_detector.detect(landmarks)
                    self.tracker.draw_landmarks(frame, landmarks)

                    # Draw palm center indicator
                    cv2.circle(frame, palm_center, 8, (0, 255, 255), -1)
                    cv2.putText(
                        frame,
                        f"Palm: ({palm_center[0]}, {palm_center[1]})",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        1,
                    )

                    # Gesture-based Rasengan control
                    # FIST activates the Rasengan
                    if current_gesture == GestureType.FIST:
                        if not self.rasengan_active:
                            # Transition from inactive to active: start formation
                            self.rasengan_active = True
                        # Update Rasengan position and continue animation
                        self.effect.update(palm_center, time.perf_counter())
                    # OPEN_PALM deactivates the Rasengan
                    elif current_gesture == GestureType.OPEN_PALM:
                        if self.rasengan_active:
                            # Transition from active to inactive: deactivate effect
                            self.rasengan_active = False
                            self.effect.set_inactive()
                    # For other gestures, keep the previous state
                    else:
                        if self.rasengan_active:
                            self.effect.update(palm_center, time.perf_counter())
                else:
                    # No hand detected: deactivate Rasengan
                    current_gesture = GestureType.UNKNOWN
                    self.rasengan_active = False
                    self.effect.set_inactive()
                    cv2.putText(
                        frame,
                        "No hand detected",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2,
                    )

                # Render the Rasengan
                frame = self.effect.render(frame)

                # Display gesture information
                gesture_text = f"Gesture: {current_gesture.value}"
                gesture_color = (0, 255, 0) if current_gesture != GestureType.UNKNOWN else (0, 0, 255)
                cv2.putText(
                    frame,
                    gesture_text,
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    gesture_color,
                    2,
                )

                # Display Rasengan state
                rasengan_state = "Rasengan: ACTIVE" if self.rasengan_active else "Rasengan: INACTIVE"
                rasengan_color = (0, 255, 0) if self.rasengan_active else (0, 0, 255)
                cv2.putText(
                    frame,
                    rasengan_state,
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    rasengan_color,
                    1,
                )

                # Calculate and display FPS
                current_time = time.perf_counter()
                dt = current_time - prev_time
                fps = 1.0 / dt if dt > 0 else 0.0
                prev_time = current_time

                cv2.putText(
                    frame,
                    f"FPS: {fps:.1f}",
                    (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    1,
                )

                cv2.imshow("Naruto Hand VFX Studio - Phase 4", frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), ord("Q")):
                    break
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Release webcam and OpenCV resources cleanly."""
        self.tracker.cleanup()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        app = NarutoHandVFXApp()
        app.run()
    except RuntimeError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Program interrupted by user.")
        sys.exit(0)
