import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HandTracker:
    def __init__(self, mode=False, max_hands=1, detection_con=0.85, track_con=0.85):
        self.max_hands = max_hands
        self.detection_con = float(detection_con)
        self.track_con = float(track_con)

        # Use the modern MediaPipe Tasks API
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
        self.lm_list = []
        
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
        Processes the image to find hand landmarks and optionally draws them.
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        self.results = self.detector.detect(mp_image)

        if self.results.hand_landmarks:
            for hand_lms in self.results.hand_landmarks:
                if draw:
                    h, w, c = img.shape
                    # Draw connections
                    for connection in self.HAND_CONNECTIONS:
                        pt1 = hand_lms[connection[0]]
                        pt2 = hand_lms[connection[1]]
                        x1, y1 = int(pt1.x * w), int(pt1.y * h)
                        x2, y2 = int(pt2.x * w), int(pt2.y * h)
                        cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
                    
                    # Draw landmarks
                    for lm in hand_lms:
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
        return img

    def find_position(self, img, hand_no=0, draw=True):
        """
        Returns a list of landmarks for a specific hand and optionally draws the landmarks.
        """
        self.lm_list = []
        if self.results and self.results.hand_landmarks:
            if hand_no < len(self.results.hand_landmarks):
                my_hand = self.results.hand_landmarks[hand_no]
                for id, lm in enumerate(my_hand):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.lm_list.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return self.lm_list

    def fingers_up(self, hand_no=0):
        """
        Checks which fingers are up. 
        Returns a list of 5 integers (1 for up, 0 for down).
        """
        fingers = []
        if len(self.lm_list) != 0:
            # Determine handedness of the active hand
            hand_type = "Right"
            if self.results and self.results.handedness and hand_no < len(self.results.handedness):
                hand_type = self.results.handedness[hand_no][0].category_name

            # Thumb (Checking x coordinate since thumb moves horizontally)
            if hand_type == "Right":
                if self.lm_list[self.tip_ids[0]][1] > self.lm_list[self.tip_ids[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else: # Left Hand
                if self.lm_list[self.tip_ids[0]][1] < self.lm_list[self.tip_ids[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            
            # 4 Fingers (Checking y coordinate since they move vertically)
            for id in range(1, 5):
                if self.lm_list[self.tip_ids[id]][2] < self.lm_list[self.tip_ids[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        return fingers
