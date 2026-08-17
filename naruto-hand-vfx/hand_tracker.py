import time
import urllib.request
from pathlib import Path

import cv2
import numpy as np

from mediapipe import Image, ImageFormat
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    HandLandmarksConnections,
    RunningMode,
)


MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_PATH = Path(__file__).resolve().with_name("hand_landmarker.task")


def ensure_model_downloaded() -> None:
    """Download the MediaPipe hand landmarker model if it is not already present."""
    if MODEL_PATH.exists():
        return

    print(f"Downloading hand model to {MODEL_PATH}...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)


class HandTracker:
    """Small wrapper around MediaPipe hand-landmarker detection."""

    def __init__(self, camera_index: int = 0, frame_width: int = 640, frame_height: int = 480):
        self.camera_index = camera_index
        self.frame_width = frame_width
        self.frame_height = frame_height

        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(
                "Unable to open the default webcam. Check that a camera is connected and available."
            )

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)

        ensure_model_downloaded()
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
            running_mode=RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarker = HandLandmarker.create_from_options(options)

        self.last_landmarks = None
        self.last_palm_center = None

    def calculate_palm_center(self, landmarks, frame_width: int, frame_height: int):
        """Estimate the hand palm center from a stable subset of landmarks."""
        palm_indices = [0, 5, 9, 13, 17]
        points = []

        for index in palm_indices:
            x, y = landmarks[index]
            points.append((x, y))

        center = np.mean(np.array(points, dtype=np.float32), axis=0)
        return int(center[0]), int(center[1])

    def process_frame(self, frame):
        """Process a single camera frame and return palm center + landmark points."""
        height, width = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
        timestamp_ms = int(time.perf_counter() * 1000)
        results = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        if not results.hand_landmarks:
            self.last_landmarks = None
            self.last_palm_center = None
            return None, None

        hand = results.hand_landmarks[0]
        landmarks = [(int(landmark.x * width), int(landmark.y * height)) for landmark in hand]
        self.last_landmarks = landmarks
        self.last_palm_center = self.calculate_palm_center(landmarks, width, height)
        return self.last_palm_center, landmarks

    def draw_landmarks(self, frame, landmarks):
        """Overlay the detected hand skeleton on the current frame."""
        if not landmarks:
            return

        for connection in HandLandmarksConnections.HAND_CONNECTIONS:
            start_index = connection.start
            end_index = connection.end
            if start_index < len(landmarks) and end_index < len(landmarks):
                start = landmarks[start_index]
                end = landmarks[end_index]
                cv2.line(frame, start, end, (0, 255, 255), 2)
                cv2.circle(frame, start, 3, (255, 0, 0), -1)
                cv2.circle(frame, end, 3, (255, 0, 0), -1)

    def cleanup(self):
        """Release the webcam and MediaPipe resources safely."""
        if self.landmarker is not None:
            self.landmarker.close()
        if self.cap is not None:
            self.cap.release()
