import time
from collections import deque, Counter

class GestureController:
    """
    Advanced real-time gesture recognition engine.
    Supports 7 distinct gestures with sliding-window majority voting,
    stateful vs. action gesture segregation, and cooldown debouncing.
    """
    def __init__(self, history_size=7):
        self.history = deque(maxlen=history_size)
        
        # Cooldown management for triggers (to prevent duplicate firings)
        self.last_trigger_times = {
            "UNDO": 0.0,
            "REDO": 0.0,
            "SAVE": 0.0,
            "CLEAR": 0.0
        }
        
        # Custom cooldown limits (seconds)
        self.cooldowns = {
            "UNDO": 0.8,
            "REDO": 0.8,
            "SAVE": 2.0,
            "CLEAR": 1.5
        }

    def get_gesture(self, fingers):
        """
        Interprets finger list, performs temporal smoothing over sliding window,
        and manages action cooldowns.
        """
        if not fingers or len(fingers) != 5:
            self.history.append("NONE")
            return "NONE"
            
        raw_gesture = self._get_raw_gesture(fingers)
        self.history.append(raw_gesture)
        
        # Majority voting on the history window for temporal stability
        vote_counts = Counter(self.history)
        smoothed_gesture = vote_counts.most_common(1)[0][0]
        
        # Handle action cooldowns
        now = time.time()
        if smoothed_gesture in self.last_trigger_times:
            last_time = self.last_trigger_times[smoothed_gesture]
            cooldown_dur = self.cooldowns[smoothed_gesture]
            
            if now - last_time < cooldown_dur:
                # If in cooldown, fallback to "PAUSE" to avoid drawing/accidental actions
                return "PAUSE"
            else:
                # Action is approved! Mark the timestamp
                self.last_trigger_times[smoothed_gesture] = now
                return smoothed_gesture
                
        return smoothed_gesture

    def _get_raw_gesture(self, fingers):
        """
        Maps binary finger combinations to specific gestures.
        fingers: [Thumb, Index, Middle, Ring, Pinky]
        """
        total_fingers = sum(fingers)
        
        # 1. Closed fist -> PAUSE
        if total_fingers == 0:
            return "PAUSE"
            
        # 2. Thumb up only -> SAVE
        if fingers[0] == 1 and sum(fingers[1:]) == 0:
            return "SAVE"
            
        # 3. Index finger up only -> DRAW
        if fingers[1] == 1 and fingers[0] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            return "DRAW"
            
        # 4. Index + Middle fingers up -> SELECT
        if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[3] == 0 and fingers[4] == 0:
            return "SELECT"
            
        # 5. Three fingers up (Index + Middle + Ring) -> UNDO
        if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[0] == 0 and fingers[4] == 0:
            return "UNDO"
            
        # 6. Four fingers up (Index + Middle + Ring + Pinky) -> REDO
        if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1 and fingers[0] == 0:
            return "REDO"
            
        # 7. All five fingers up -> CLEAR
        if total_fingers == 5:
            return "CLEAR"
            
        return "NONE"

    def force_cooldown(self, gesture):
        """
        Manually triggers a cooldown on a specific action gesture.
        Useful when actions are triggered via hotkeys or toolbar.
        """
        if gesture in self.last_trigger_times:
            self.last_trigger_times[gesture] = time.time()

    def reset(self):
        self.history.clear()
