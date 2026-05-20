import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HandTracker:
    """
    Highly optimized multi-hand landmarker wrapper using Google MediaPipe Tasks API.
    Maintains full backwards compatibility while adding support for multi-hand coordinate mapping.
    """
    def __init__(self, mode=False, max_hands=2, detection_con=0.75, track_con=0.75):
        self.max_hands = max_hands
        self.detection_con = float(detection_con)
        self.track_con = float(track_con)

        # Initialize MediaPipe Hand Landmarker Tasks API
        base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=self.max_hands,
            min_hand_detection_confidence=self.detection_con,
            min_hand_presence_confidence=self.track_con,
            running_mode=vision.RunningMode.IMAGE
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        self.tip_ids = [4, 8, 12, 16, 20]
        self.results = None
        self.lm_list = [] # Backwards compatibility for Hand 0
        self.hands_info = [] # Store all hands' metrics
        
        # Connections definition for hand drawing
        self.HAND_CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17)
        ]

    def find_hands(self, img, draw=True):
        """
        Processes flipped image to detect hands. Supports dynamic downscaling to 
        speed up internal landmark detection, mapping results back to native resolution.
        """
        h, w, c = img.shape
        
        # Performance optimization: Resize frame to 640x360 internally for MediaPipe processing
        # This keeps the landmarks extremely responsive and stable
        scale_w, scale_h = 640, 360
        img_small = cv2.resize(img, (scale_w, scale_h))
        img_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        # Perform inference
        self.results = self.detector.detect(mp_image)
        self.hands_info = []

        if self.results.hand_landmarks:
            for hand_idx, hand_lms in enumerate(self.results.hand_landmarks):
                # Retrieve handedness (Left/Right)
                hand_type = "Right"
                if self.results.handedness and hand_idx < len(self.results.handedness):
                    hand_type = self.results.handedness[hand_idx][0].category_name

                # Extract and scale coordinates back to original size
                hand_lms_scaled = []
                for lm_id, lm in enumerate(hand_lms):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    hand_lms_scaled.append([lm_id, cx, cy])

                # Draw skeleton skeleton overlays if requested
                if draw:
                    for connection in self.HAND_CONNECTIONS:
                        pt1 = hand_lms_scaled[connection[0]]
                        pt2 = hand_lms_scaled[connection[1]]
                        # Sleek thin translucent white skeletons
                        cv2.line(img, (pt1[1], pt1[2]), (pt2[1], pt2[2]), (220, 220, 220), 1, cv2.LINE_AA)
                    
                    for pt in hand_lms_scaled:
                        # Soft small crimson joints
                        cv2.circle(img, (pt[1], pt[2]), 4, (80, 80, 240), cv2.FILLED, cv2.LINE_AA)

                self.hands_info.append({
                    "hand_no": hand_idx,
                    "type": hand_type,
                    "lm_list": hand_lms_scaled
                })

        # Set backwards compatible lm_list for single hand tracking (defaulting to first detected hand)
        if self.hands_info:
            self.lm_list = self.hands_info[0]["lm_list"]
        else:
            self.lm_list = []

        return img

    def find_position(self, img, hand_no=0, draw=True):
        """
        Returns landmark lists for backwards compatibility with single-hand controllers.
        """
        if hand_no < len(self.hands_info):
            self.lm_list = self.hands_info[hand_no]["lm_list"]
            if draw and self.lm_list:
                for pt in self.lm_list:
                    cv2.circle(img, (pt[1], pt[2]), 5, (255, 0, 255), cv2.FILLED)
            return self.lm_list
        return []

    def get_active_hands(self):
        """
        Returns the parsed hands_info list containing scaled landmarks and classification types.
        """
        return self.hands_info

    def fingers_up(self, hand_no=0):
        """
        Interprets which fingers are up for the requested hand.
        Returns a list of 5 binary indicators: [Thumb, Index, Middle, Ring, Pinky]
        """
        fingers = []
        target_lm_list = []
        hand_type = "Right"

        if hand_no < len(self.hands_info):
            target_lm_list = self.hands_info[hand_no]["lm_list"]
            hand_type = self.hands_info[hand_no]["type"]
        elif hand_no == 0 and len(self.lm_list) > 0:
            # Fallback to compatibility array
            target_lm_list = self.lm_list
            if self.results and self.results.handedness:
                hand_type = self.results.handedness[0][0].category_name

        if len(target_lm_list) != 0:
            # 1. Thumb State (Horizontal comparison check)
            # If flipped, right hand thumb moves left or right
            if hand_type == "Right":
                if target_lm_list[self.tip_ids[0]][1] > target_lm_list[self.tip_ids[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else: # Left Hand
                if target_lm_list[self.tip_ids[0]][1] < target_lm_list[self.tip_ids[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            
            # 2. Other 4 Fingers States (Vertical comparison check)
            for id in range(1, 5):
                # Check if tip y is higher than pip joint y (lower value means higher on screen)
                if target_lm_list[self.tip_ids[id]][2] < target_lm_list[self.tip_ids[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
                    
        return fingers
