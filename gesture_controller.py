from collections import deque, Counter

class GestureController:
    def __init__(self, history_size=5):
        self.history = deque(maxlen=history_size)
    
    def get_gesture(self, fingers):
        """
        Interprets the list of fingers raised into a specific command,
        smoothed over time to prevent flickering.
        """
        raw_gesture = self._get_raw_gesture(fingers)
        self.history.append(raw_gesture)
        
        # Perform majority voting on the history window
        vote_counts = Counter(self.history)
        most_common = vote_counts.most_common(1)[0][0]
        return most_common

    def _get_raw_gesture(self, fingers):
        """
        Detects gesture from a single frame's finger state.
        fingers order: [Thumb, Index, Middle, Ring, Pinky]
        """
        if len(fingers) == 0:
            return "NONE"
            
        # Index finger up only -> DRAW
        if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            return "DRAW"
            
        # Index and Middle up -> SELECT (for toolbar interactions)
        elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
            return "SELECT"
            
        # All fingers up -> CLEAR
        elif sum(fingers) == 5:
            return "CLEAR"
            
        # Closed fist -> PAUSE
        elif sum(fingers) == 0:
            return "PAUSE"
            
        # Only Thumb up -> SAVE
        elif fingers == [1, 0, 0, 0, 0]:
            return "SAVE"
            
        return "NONE"

    def reset(self):
        """
        Clears the gesture history.
        """
        self.history.clear()
