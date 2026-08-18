import sys
import time

import cv2
import numpy as np

from config import AppConfig
from hand_tracker import HandTracker
from gesture_detector import GestureDetector, GestureType
from vfx.chidori import ChidoriEffect
from vfx.energy_beam import EnergyBeamEffect
from vfx.fireball import FireballEffect
from vfx.rasengan import RasenganEffect


class NarutoHandVFXApp:
    """Production-ready Phase 8 local VFX app with gesture-driven effect control."""

    def __init__(self, config: AppConfig | None = None):
        self.config = config or AppConfig()
        self.tracker = HandTracker(
            camera_index=self.config.camera_index,
            frame_width=self.config.frame_width,
            frame_height=self.config.frame_height,
        )
        self.rasengan = RasenganEffect(
            base_radius=int(62 * self.config.vfx_scale),
            smoothing=0.18,
            formation_duration=2.5,
        )
        self.chidori = ChidoriEffect(
            base_radius=int(52 * self.config.vfx_scale),
            smoothing=0.18,
            formation_duration=2.2,
        )
        self.fireball = FireballEffect(
            base_radius=int(56 * self.config.vfx_scale),
            smoothing=0.18,
            formation_duration=2.3,
        )
        self.energy_beam = EnergyBeamEffect(
            base_width=24.0 * self.config.vfx_scale,
            smoothing=0.18,
            formation_duration=2.6,
        )
        self.gesture_detector = GestureDetector(history_length=self.config.gesture_history_length)
        self.active_effect = "NONE"
        self.keyboard_effect_override = None
        self.keyboard_effect_expires_at = 0.0
        self.current_gesture = GestureType.UNKNOWN
        self.hands_detected = 0
        self.camera_status = "Connected"
        self.last_error_text = ""

    def _clear_active_effects(self):
        self.rasengan.set_inactive()
        self.chidori.set_inactive()
        self.fireball.set_inactive()
        self.energy_beam.set_inactive()
        self.active_effect = "NONE"

    def _activate_single_hand_effect(self, effect_name: str, palm_center, timestamp):
        if effect_name == "NONE":
            self._clear_active_effects()
            return

        if effect_name == "RASENGAN":
            if self.active_effect != "RASENGAN":
                self._clear_active_effects()
                self.active_effect = "RASENGAN"
            self.rasengan.update(palm_center, timestamp)
            return

        if effect_name == "CHIDORI":
            if self.active_effect != "CHIDORI":
                self._clear_active_effects()
                self.active_effect = "CHIDORI"
            self.chidori.update(palm_center, timestamp)
            return

        if effect_name == "FIREBALL":
            if self.active_effect != "FIREBALL":
                self._clear_active_effects()
                self.active_effect = "FIREBALL"
            self.fireball.update(palm_center, timestamp)
            return

        self._clear_active_effects()

    def _apply_effect_state(self, current_gesture, palm_center, timestamp):
        """Evaluate the active single-hand effect based on pose and state machine rules."""
        if self.keyboard_effect_override is not None and time.perf_counter() < self.keyboard_effect_expires_at:
            self._activate_single_hand_effect(self.keyboard_effect_override, palm_center, timestamp)
            return

        if palm_center is None:
            self._clear_active_effects()
            return

        if current_gesture == GestureType.OPEN_PALM:
            self._clear_active_effects()
            return

        if current_gesture == GestureType.FIST:
            self._activate_single_hand_effect("RASENGAN", palm_center, timestamp)
            return

        if current_gesture == GestureType.POINTING:
            self._activate_single_hand_effect("CHIDORI", palm_center, timestamp)
            return

        if current_gesture == GestureType.TWO_FINGERS:
            self._activate_single_hand_effect("FIREBALL", palm_center, timestamp)
            return

        if self.active_effect == "RASENGAN":
            self.rasengan.update(palm_center, timestamp)
        elif self.active_effect == "CHIDORI":
            self.chidori.update(palm_center, timestamp)
        elif self.active_effect == "FIREBALL":
            self.fireball.update(palm_center, timestamp)
        else:
            self._clear_active_effects()

    def _apply_two_hand_beam(self, hand_1, hand_2, timestamp):
        """Evaluate the two-hand energy beam activation and keep it separate from the single-hand effects."""
        if self.keyboard_effect_override is not None and time.perf_counter() < self.keyboard_effect_expires_at:
            self._activate_single_hand_effect(self.keyboard_effect_override, hand_1["palm_center"], timestamp)
            return

        if hand_1 is None or hand_2 is None:
            self._clear_active_effects()
            return

        if hand_1["gesture"] == GestureType.TWO_FINGERS and hand_2["gesture"] == GestureType.TWO_FINGERS:
            if self.active_effect != "ENERGY_BEAM":
                self._clear_active_effects()
                self.active_effect = "ENERGY_BEAM"
            self.energy_beam.update(hand_1["palm_center"], hand_2["palm_center"], timestamp)
            return

        self._clear_active_effects()

    def _handle_keyboard(self, key):
        if not self.config.enable_keyboard_controls:
            return

        mapping = {
            ord("0"): "NONE",
            ord("1"): "RASENGAN",
            ord("2"): "CHIDORI",
            ord("3"): "FIREBALL",
            ord("4"): "ENERGY_BEAM",
        }
        if key in mapping:
            self.keyboard_effect_override = mapping[key]
            self.keyboard_effect_expires_at = time.perf_counter() + 0.12
        elif key in (ord("q"), ord("Q")):
            self.keyboard_effect_override = "NONE"
            self.keyboard_effect_expires_at = time.perf_counter() + 0.12

    def _render_status_panel(self, frame, fps: float):
        title = "NARUTO HAND VFX STUDIO"
        effect_text = f"Effect: {self.active_effect}"
        gesture_text = f"Gesture: {self.current_gesture.value}"
        hands_text = f"Hands: {self.hands_detected}"
        fps_text = f"FPS: {fps:.1f}"
        camera_text = f"Camera: {self.camera_status}"

        panel_x, panel_y = 10, 10
        panel_w, panel_h = 260, 120
        cv2.rectangle(frame, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), (12, 12, 16), -1)
        cv2.rectangle(frame, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), (255, 255, 255), 1)

        cv2.putText(frame, title, (panel_x + 10, panel_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
        cv2.putText(frame, effect_text, (panel_x + 10, panel_y + 42), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
        cv2.putText(frame, gesture_text, (panel_x + 10, panel_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.putText(frame, hands_text, (panel_x + 10, panel_y + 78), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.putText(frame, fps_text, (panel_x + 10, panel_y + 96), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.putText(frame, camera_text, (panel_x + 10, panel_y + 114), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 0), 1)

    def _render_camera_error(self, frame, message: str):
        frame[:] = (8, 8, 12)
        cv2.putText(frame, "Unable to access webcam.", (60, 220), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        cv2.putText(frame, message, (50, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    def run(self) -> None:
        """Main webcam loop for the local real-time VFX experience."""
        prev_time = time.perf_counter()

        try:
            while True:
                success, frame = self.tracker.cap.read()
                if not success:
                    self.camera_status = "Disconnected"
                    frame = np.zeros((self.config.frame_height, self.config.frame_width, 3), dtype=np.uint8)
                    self._render_camera_error(frame, "Check the webcam connection and retry.")
                    cv2.imshow("Naruto Hand VFX Studio", frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key in (ord("q"), ord("Q")):
                        break
                    continue

                frame = cv2.flip(frame, 1)
                palm_center, landmarks, hands = self.tracker.process_frame(frame)
                self.current_gesture = GestureType.UNKNOWN
                self.hands_detected = len(hands) if hands else 0
                self.camera_status = "Connected"

                detected_hands = []
                if hands:
                    for hand in hands:
                        gesture = self.gesture_detector.detect(hand["landmarks"])
                        hand["gesture"] = gesture
                        detected_hands.append(hand)
                        self.tracker.draw_landmarks(frame, hand["landmarks"])
                        cv2.circle(frame, hand["palm_center"], 8, (0, 255, 255), -1)

                if detected_hands:
                    self.current_gesture = detected_hands[0]["gesture"]
                    timestamp = time.perf_counter()
                    if len(detected_hands) >= 2:
                        self._apply_two_hand_beam(detected_hands[0], detected_hands[1], timestamp)
                    else:
                        self._apply_effect_state(self.current_gesture, palm_center, timestamp)
                else:
                    self._clear_active_effects()
                    self.current_gesture = GestureType.UNKNOWN

                if self.active_effect == "RASENGAN":
                    frame = self.rasengan.render(frame)
                elif self.active_effect == "CHIDORI":
                    frame = self.chidori.render(frame)
                elif self.active_effect == "FIREBALL":
                    frame = self.fireball.render(frame)
                elif self.active_effect == "ENERGY_BEAM":
                    frame = self.energy_beam.render(frame)

                current_time = time.perf_counter()
                dt = current_time - prev_time
                fps = 1.0 / dt if dt > 0 else 0.0
                prev_time = current_time

                self._render_status_panel(frame, fps)

                key = cv2.waitKey(1) & 0xFF
                self._handle_keyboard(key)
                if key in (ord("q"), ord("Q")):
                    break

                cv2.imshow("Naruto Hand VFX Studio", frame)
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Release webcam and OpenCV resources cleanly."""
        self.tracker.cleanup()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        app = NarutoHandVFXApp(config=AppConfig.from_args())
        app.run()
    except RuntimeError as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Program interrupted by user.")
        sys.exit(0)
