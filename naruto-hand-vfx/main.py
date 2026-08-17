import sys
import time

import cv2

from hand_tracker import HandTracker
from vfx.rasengan import RasenganEffect


class NarutoHandVFXApp:
    """Phase 3 webcam app with dynamic Rasengan formation animation tied to the palm center."""

    def __init__(self, camera_index: int = 0, frame_width: int = 640, frame_height: int = 480):
        self.tracker = HandTracker(camera_index=camera_index, frame_width=frame_width, frame_height=frame_height)
        self.effect = RasenganEffect(base_radius=62, smoothing=0.18, formation_duration=2.5)

    def run(self) -> None:
        """Main webcam loop for Phase 3."""
        prev_time = time.perf_counter()

        try:
            while True:
                success, frame = self.tracker.cap.read()
                if not success:
                    print("Failed to grab a frame from the webcam.")
                    break

                frame = cv2.flip(frame, 1)
                palm_center, landmarks = self.tracker.process_frame(frame)

                if palm_center is not None:
                    self.effect.update(palm_center, time.perf_counter())
                    self.tracker.draw_landmarks(frame, landmarks)

                    cv2.circle(frame, palm_center, 8, (0, 255, 255), -1)
                    cv2.putText(
                        frame,
                        f"Palm center: ({palm_center[0]}, {palm_center[1]})",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2,
                    )
                else:
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

                frame = self.effect.render(frame)

                current_time = time.perf_counter()
                dt = current_time - prev_time
                fps = 1.0 / dt if dt > 0 else 0.0
                prev_time = current_time

                cv2.putText(
                    frame,
                    f"FPS: {fps:.1f}",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

                cv2.imshow("Naruto Hand VFX Studio - Phase 3", frame)
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
