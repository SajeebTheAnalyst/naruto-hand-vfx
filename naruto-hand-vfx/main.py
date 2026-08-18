import sys
import time

import cv2

from hand_tracker import HandTracker
from gesture_detector import GestureDetector, GestureType
from vfx.chidori import ChidoriEffect
from vfx.energy_beam import EnergyBeamEffect
from vfx.fireball import FireballEffect
from vfx.rasengan import RasenganEffect


class NarutoHandVFXApp:
    """Phase 7 app with Rasengan, Chidori, Fireball, and dual-hand Energy Beam states."""

    def __init__(self, camera_index: int = 0, frame_width: int = 640, frame_height: int = 480):
        self.tracker = HandTracker(camera_index=camera_index, frame_width=frame_width, frame_height=frame_height)
        self.rasengan = RasenganEffect(base_radius=62, smoothing=0.18, formation_duration=2.5)
        self.chidori = ChidoriEffect(base_radius=52, smoothing=0.18, formation_duration=2.2)
        self.fireball = FireballEffect(base_radius=56, smoothing=0.18, formation_duration=2.3)
        self.energy_beam = EnergyBeamEffect(base_width=24.0, smoothing=0.18, formation_duration=2.6)
        self.gesture_detector = GestureDetector(history_length=5)
        self.active_effect = "NONE"
        self.previous_gesture = GestureType.UNKNOWN

    def _apply_effect_state(self, current_gesture, palm_center, timestamp):
        """Switch between NONE, RASENGAN, CHIDORI, FIREBALL, and ENERGY_BEAM based on stable gestures."""
        if palm_center is None:
            self.active_effect = "NONE"
            self.rasengan.set_inactive()
            self.chidori.set_inactive()
            self.fireball.set_inactive()
            self.energy_beam.set_inactive()
            return

        if current_gesture == GestureType.OPEN_PALM:
            self.active_effect = "NONE"
            self.rasengan.set_inactive()
            self.chidori.set_inactive()
            self.fireball.set_inactive()
            self.energy_beam.set_inactive()
            return

        if current_gesture == GestureType.FIST:
            if self.active_effect != "RASENGAN":
                self.rasengan.set_inactive()
                self.chidori.set_inactive()
                self.fireball.set_inactive()
                self.energy_beam.set_inactive()
                self.active_effect = "RASENGAN"
            self.rasengan.update(palm_center, timestamp)
            return

        if current_gesture == GestureType.POINTING:
            if self.active_effect != "CHIDORI":
                self.rasengan.set_inactive()
                self.chidori.set_inactive()
                self.fireball.set_inactive()
                self.energy_beam.set_inactive()
                self.active_effect = "CHIDORI"
            self.chidori.update(palm_center, timestamp)
            return

        if current_gesture == GestureType.TWO_FINGERS:
            if self.active_effect != "FIREBALL":
                self.rasengan.set_inactive()
                self.chidori.set_inactive()
                self.fireball.set_inactive()
                self.energy_beam.set_inactive()
                self.active_effect = "FIREBALL"
            self.fireball.update(palm_center, timestamp)
            return

        if self.active_effect == "RASENGAN":
            self.rasengan.update(palm_center, timestamp)
        elif self.active_effect == "CHIDORI":
            self.chidori.update(palm_center, timestamp)
        elif self.active_effect == "FIREBALL":
            self.fireball.update(palm_center, timestamp)
        else:
            self.rasengan.set_inactive()
            self.chidori.set_inactive()
            self.fireball.set_inactive()
            self.energy_beam.set_inactive()

    def _apply_two_hand_beam(self, hand_1, hand_2, timestamp):
        """Activate or deactivate the two-hand energy beam using both gestures and palm positions."""
        if hand_1 is None or hand_2 is None:
            self.active_effect = "NONE"
            self.rasengan.set_inactive()
            self.chidori.set_inactive()
            self.fireball.set_inactive()
            self.energy_beam.set_inactive()
            return

        if hand_1["gesture"] == GestureType.TWO_FINGERS and hand_2["gesture"] == GestureType.TWO_FINGERS:
            if self.active_effect != "ENERGY_BEAM":
                self.rasengan.set_inactive()
                self.chidori.set_inactive()
                self.fireball.set_inactive()
                self.active_effect = "ENERGY_BEAM"
            self.energy_beam.update(hand_1["palm_center"], hand_2["palm_center"], timestamp)
            return

        if self.active_effect == "ENERGY_BEAM":
            self.active_effect = "NONE"
        self.rasengan.set_inactive()
        self.chidori.set_inactive()
        self.fireball.set_inactive()
        self.energy_beam.set_inactive()

    def run(self) -> None:
        """Main webcam loop for Phase 5 with effect switching via gesture detection."""
        prev_time = time.perf_counter()

        try:
            while True:
                success, frame = self.tracker.cap.read()
                if not success:
                    print("Failed to grab a frame from the webcam.")
                    break

                frame = cv2.flip(frame, 1)
                palm_center, landmarks, hands = self.tracker.process_frame(frame)
                current_gesture = GestureType.UNKNOWN
                detected_hands = []

                if hands:
                    for hand in hands:
                        detected_gesture = self.gesture_detector.detect(hand["landmarks"])
                        hand["gesture"] = detected_gesture
                        detected_hands.append(hand)
                        self.tracker.draw_landmarks(frame, hand["landmarks"])
                        cv2.circle(frame, hand["palm_center"], 8, (0, 255, 255), -1)

                if detected_hands:
                    current_gesture = detected_hands[0]["gesture"]
                    cv2.putText(
                        frame,
                        f"Palm 1: ({detected_hands[0]['palm_center'][0]}, {detected_hands[0]['palm_center'][1]})",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        1,
                    )

                    if len(detected_hands) > 1:
                        cv2.putText(
                            frame,
                            f"Palm 2: ({detected_hands[1]['palm_center'][0]}, {detected_hands[1]['palm_center'][1]})",
                            (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (255, 255, 255),
                            1,
                        )

                    timestamp = time.perf_counter()
                    if len(detected_hands) >= 2:
                        self._apply_two_hand_beam(detected_hands[0], detected_hands[1], timestamp)
                    else:
                        self._apply_effect_state(current_gesture, palm_center, timestamp)
                else:
                    self.active_effect = "NONE"
                    self.rasengan.set_inactive()
                    self.chidori.set_inactive()
                    self.fireball.set_inactive()
                    self.energy_beam.set_inactive()
                    cv2.putText(
                        frame,
                        "No hand detected",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2,
                    )

                if self.active_effect == "RASENGAN":
                    frame = self.rasengan.render(frame)
                elif self.active_effect == "CHIDORI":
                    frame = self.chidori.render(frame)
                elif self.active_effect == "FIREBALL":
                    frame = self.fireball.render(frame)
                elif self.active_effect == "ENERGY_BEAM":
                    frame = self.energy_beam.render(frame)

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

                effect_text = f"Effect: {self.active_effect}"
                effect_color = (0, 255, 0) if self.active_effect != "NONE" else (0, 0, 255)
                cv2.putText(
                    frame,
                    effect_text,
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    effect_color,
                    1,
                )

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

                cv2.imshow("Naruto Hand VFX Studio - Phase 7", frame)
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
