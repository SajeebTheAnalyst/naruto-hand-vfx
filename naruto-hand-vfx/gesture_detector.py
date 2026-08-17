import numpy as np
from enum import Enum
from collections import deque


class GestureType(Enum):
    """Enumeration of supported hand gestures."""
    OPEN_PALM = "OPEN_PALM"
    FIST = "FIST"
    POINTING = "POINTING"
    TWO_FINGERS = "TWO_FINGERS"
    THUMBS_UP = "THUMBS_UP"
    UNKNOWN = "UNKNOWN"


class GestureDetector:
    """
    Geometric gesture recognition using MediaPipe hand landmarks.
    
    Detects hand poses from 21 normalized landmarks without external ML models.
    Includes temporal smoothing to prevent frame-to-frame flickering.
    """

    # MediaPipe hand landmark indices
    WRIST = 0
    THUMB_TIP = 4
    INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP = 5, 6, 7, 8
    MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP = 9, 10, 11, 12
    RING_MCP, RING_PIP, RING_DIP, RING_TIP = 13, 14, 15, 16
    PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP = 17, 18, 19, 20

    def __init__(self, history_length: int = 5):
        """
        Initialize the gesture detector.
        
        Args:
            history_length: Number of frames to maintain for smoothing (prevents flickering)
        """
        self.history_length = history_length
        self.gesture_history = deque(maxlen=history_length)
        self.last_stable_gesture = GestureType.UNKNOWN
        self.frame_count = 0

    @staticmethod
    def _distance(point1, point2):
        """Calculate Euclidean distance between two points."""
        return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    @staticmethod
    def _normalized_distance(point1, point2, reference_distance):
        """
        Calculate normalized distance (relative to reference scale).
        
        Returns a value from 0.0 to 1.0+ based on the reference distance.
        """
        if reference_distance < 1e-6:
            return 0.0
        return GestureDetector._distance(point1, point2) / reference_distance

    @staticmethod
    def _is_finger_extended(tip, pip, mcp, reference_distance, threshold=0.5):
        """
        Check if a finger is extended.
        
        A finger is considered extended if the tip is far from its base (MCP).
        Uses normalized distance to handle different hand sizes.
        """
        tip_to_mcp_dist = GestureDetector._normalized_distance(tip, mcp, reference_distance)
        return tip_to_mcp_dist > threshold

    @staticmethod
    def _is_finger_folded(tip, mcp, reference_distance, threshold=0.4):
        """
        Check if a finger is folded.
        
        A finger is considered folded if the tip is close to its base (MCP).
        """
        tip_to_mcp_dist = GestureDetector._normalized_distance(tip, mcp, reference_distance)
        return tip_to_mcp_dist < threshold

    @staticmethod
    def _get_hand_scale(landmarks):
        """
        Estimate hand size using distance from wrist to middle finger tip.
        
        Used as a reference for normalized measurements.
        """
        return GestureDetector._distance(landmarks[GestureDetector.WRIST], 
                                         landmarks[GestureDetector.MIDDLE_TIP])

    @staticmethod
    def _detect_open_palm(landmarks):
        """
        Detect OPEN_PALM gesture.
        
        Expected: Most/all fingers extended away from palm.
        """
        hand_scale = GestureDetector._get_hand_scale(landmarks)
        if hand_scale < 1e-6:
            return False

        # Check if all fingers are extended
        fingers_extended = [
            GestureDetector._is_finger_extended(landmarks[GestureDetector.THUMB_TIP], 
                                               landmarks[GestureDetector.THUMB_TIP - 1], 
                                               landmarks[GestureDetector.WRIST], hand_scale, 0.4),
            GestureDetector._is_finger_extended(landmarks[GestureDetector.INDEX_TIP], 
                                               landmarks[GestureDetector.INDEX_MCP], 
                                               landmarks[GestureDetector.WRIST], hand_scale, 0.5),
            GestureDetector._is_finger_extended(landmarks[GestureDetector.MIDDLE_TIP], 
                                               landmarks[GestureDetector.MIDDLE_MCP], 
                                               landmarks[GestureDetector.WRIST], hand_scale, 0.5),
            GestureDetector._is_finger_extended(landmarks[GestureDetector.RING_TIP], 
                                               landmarks[GestureDetector.RING_MCP], 
                                               landmarks[GestureDetector.WRIST], hand_scale, 0.5),
            GestureDetector._is_finger_extended(landmarks[GestureDetector.PINKY_TIP], 
                                               landmarks[GestureDetector.PINKY_MCP], 
                                               landmarks[GestureDetector.WRIST], hand_scale, 0.5),
        ]

        # At least 4 out of 5 fingers should be extended
        return sum(fingers_extended) >= 4

    @staticmethod
    def _detect_fist(landmarks):
        """
        Detect FIST gesture.
        
        Expected: Most fingers folded/bent, close to palm.
        """
        hand_scale = GestureDetector._get_hand_scale(landmarks)
        if hand_scale < 1e-6:
            return False

        # Check if most fingers are folded
        fingers_folded = [
            GestureDetector._is_finger_folded(landmarks[GestureDetector.THUMB_TIP], 
                                             landmarks[GestureDetector.WRIST], hand_scale, 0.45),
            GestureDetector._is_finger_folded(landmarks[GestureDetector.INDEX_TIP], 
                                             landmarks[GestureDetector.INDEX_MCP], hand_scale, 0.4),
            GestureDetector._is_finger_folded(landmarks[GestureDetector.MIDDLE_TIP], 
                                             landmarks[GestureDetector.MIDDLE_MCP], hand_scale, 0.4),
            GestureDetector._is_finger_folded(landmarks[GestureDetector.RING_TIP], 
                                             landmarks[GestureDetector.RING_MCP], hand_scale, 0.4),
            GestureDetector._is_finger_folded(landmarks[GestureDetector.PINKY_TIP], 
                                             landmarks[GestureDetector.PINKY_MCP], hand_scale, 0.4),
        ]

        # At least 4 out of 5 fingers should be folded
        return sum(fingers_folded) >= 4

    @staticmethod
    def _detect_pointing(landmarks):
        """
        Detect POINTING gesture.
        
        Expected: Index finger extended, other fingers (except thumb) folded.
        """
        hand_scale = GestureDetector._get_hand_scale(landmarks)
        if hand_scale < 1e-6:
            return False

        # Index should be extended
        index_extended = GestureDetector._is_finger_extended(
            landmarks[GestureDetector.INDEX_TIP],
            landmarks[GestureDetector.INDEX_MCP],
            landmarks[GestureDetector.WRIST],
            hand_scale,
            0.5
        )

        # Other fingers should be folded
        other_fingers_folded = [
            GestureDetector._is_finger_folded(landmarks[GestureDetector.MIDDLE_TIP], 
                                             landmarks[GestureDetector.MIDDLE_MCP], hand_scale, 0.4),
            GestureDetector._is_finger_folded(landmarks[GestureDetector.RING_TIP], 
                                             landmarks[GestureDetector.RING_MCP], hand_scale, 0.4),
            GestureDetector._is_finger_folded(landmarks[GestureDetector.PINKY_TIP], 
                                             landmarks[GestureDetector.PINKY_MCP], hand_scale, 0.4),
        ]

        return index_extended and sum(other_fingers_folded) >= 2

    @staticmethod
    def _detect_two_fingers(landmarks):
        """
        Detect TWO_FINGERS (peace/victory) gesture.
        
        Expected: Index + middle fingers extended, other fingers folded.
        """
        hand_scale = GestureDetector._get_hand_scale(landmarks)
        if hand_scale < 1e-6:
            return False

        # Index and middle should be extended
        index_extended = GestureDetector._is_finger_extended(
            landmarks[GestureDetector.INDEX_TIP],
            landmarks[GestureDetector.INDEX_MCP],
            landmarks[GestureDetector.WRIST],
            hand_scale,
            0.5
        )
        
        middle_extended = GestureDetector._is_finger_extended(
            landmarks[GestureDetector.MIDDLE_TIP],
            landmarks[GestureDetector.MIDDLE_MCP],
            landmarks[GestureDetector.WRIST],
            hand_scale,
            0.5
        )

        # Ring and pinky should be folded
        other_fingers_folded = [
            GestureDetector._is_finger_folded(landmarks[GestureDetector.RING_TIP], 
                                             landmarks[GestureDetector.RING_MCP], hand_scale, 0.4),
            GestureDetector._is_finger_folded(landmarks[GestureDetector.PINKY_TIP], 
                                             landmarks[GestureDetector.PINKY_MCP], hand_scale, 0.4),
        ]

        return index_extended and middle_extended and sum(other_fingers_folded) >= 1

    @staticmethod
    def _detect_thumbs_up(landmarks):
        """
        Detect THUMBS_UP gesture.
        
        Expected: Thumb extended upward, other fingers folded.
        The key is that the thumb should be notably higher than the wrist (pointing up).
        """
        hand_scale = GestureDetector._get_hand_scale(landmarks)
        if hand_scale < 1e-6:
            return False

        wrist = landmarks[GestureDetector.WRIST]
        thumb_tip = landmarks[GestureDetector.THUMB_TIP]

        # Thumb should be extended from its base
        thumb_extended = GestureDetector._is_finger_extended(
            thumb_tip,
            landmarks[GestureDetector.THUMB_TIP - 1],  # Thumb IP
            landmarks[GestureDetector.WRIST],
            hand_scale,
            0.4
        )

        # Thumb should be pointing upward (negative Y in image coordinates means up)
        # Check if thumb tip is notably higher than wrist
        thumb_above_wrist = (wrist[1] - thumb_tip[1]) > (hand_scale * 0.3)

        # Other fingers should be folded
        other_fingers_folded = [
            GestureDetector._is_finger_folded(landmarks[GestureDetector.INDEX_TIP], 
                                             landmarks[GestureDetector.INDEX_MCP], hand_scale, 0.4),
            GestureDetector._is_finger_folded(landmarks[GestureDetector.MIDDLE_TIP], 
                                             landmarks[GestureDetector.MIDDLE_MCP], hand_scale, 0.4),
            GestureDetector._is_finger_folded(landmarks[GestureDetector.RING_TIP], 
                                             landmarks[GestureDetector.RING_MCP], hand_scale, 0.4),
            GestureDetector._is_finger_folded(landmarks[GestureDetector.PINKY_TIP], 
                                             landmarks[GestureDetector.PINKY_MCP], hand_scale, 0.4),
        ]

        return thumb_extended and thumb_above_wrist and sum(other_fingers_folded) >= 3

    def detect(self, landmarks):
        """
        Detect hand gesture from landmarks and return a smoothed/stable gesture.
        
        Args:
            landmarks: List of 21 (x, y) tuples representing MediaPipe hand landmarks
        
        Returns:
            GestureType enum value (with temporal smoothing applied)
        """
        if not landmarks or len(landmarks) < 21:
            self.gesture_history.append(GestureType.UNKNOWN)
            return self._get_stable_gesture()

        # Try each gesture in priority order
        if self._detect_thumbs_up(landmarks):
            detected = GestureType.THUMBS_UP
        elif self._detect_two_fingers(landmarks):
            detected = GestureType.TWO_FINGERS
        elif self._detect_pointing(landmarks):
            detected = GestureType.POINTING
        elif self._detect_fist(landmarks):
            detected = GestureType.FIST
        elif self._detect_open_palm(landmarks):
            detected = GestureType.OPEN_PALM
        else:
            detected = GestureType.UNKNOWN

        self.gesture_history.append(detected)
        self.frame_count += 1
        return self._get_stable_gesture()

    def _get_stable_gesture(self):
        """
        Return a temporally smoothed gesture.
        
        Requires the gesture to be consistent for at least 2/3 of the history
        before changing the stable gesture. This prevents flickering.
        """
        if not self.gesture_history:
            return self.last_stable_gesture

        # Find the most common gesture in recent history
        gesture_counts = {}
        for gesture in self.gesture_history:
            gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1

        most_common = max(gesture_counts.items(), key=lambda x: x[1])
        most_common_gesture = most_common[0]
        count = most_common[1]

        # Only change the stable gesture if the new gesture is consistent enough
        threshold = max(2, len(self.gesture_history) // 2)
        if count >= threshold:
            self.last_stable_gesture = most_common_gesture

        return self.last_stable_gesture

    def reset(self):
        """Reset the gesture detector state."""
        self.gesture_history.clear()
        self.last_stable_gesture = GestureType.UNKNOWN
        self.frame_count = 0
