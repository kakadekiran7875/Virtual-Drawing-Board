import numpy as np

class StackHistoryManager:
    """
    Manages drawing canvas history using standard double-stack architecture.
    Caps memory footprints to prevent system slowing down.
    """
    def __init__(self, max_history=20):
        self.max_history = max_history
        self.undo_stack = []
        self.redo_stack = []

    def save_state(self, canvas_img):
        """
        Saves a snapshot of the current canvas before a new drawing stroke.
        Clears redo stack on new action.
        """
        # Save a deep copy of the canvas
        self.undo_stack.append(canvas_img.copy())
        
        # Enforce boundary limits to keep memory in check
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
            
        # Reset redo actions as a new stroke is drawn
        self.redo_stack.clear()

    def undo(self, current_canvas):
        """
        Reverts the canvas to the last saved state.
        Returns the popped canvas, or None if history is empty.
        """
        if not self.undo_stack:
            return None
            
        # Push current state onto the redo stack
        self.redo_stack.append(current_canvas.copy())
        
        # Pull the last state
        prev_state = self.undo_stack.pop()
        return prev_state

    def redo(self, current_canvas):
        """
        Re-applies the last undone drawing action.
        Returns the popped canvas, or None if redo stack is empty.
        """
        if not self.redo_stack:
            return None
            
        # Push current state onto the undo stack
        self.undo_stack.append(current_canvas.copy())
        
        # Pull the next state
        next_state = self.redo_stack.pop()
        return next_state

    def clear(self):
        """
        Wipes out all history stacks.
        """
        self.undo_stack.clear()
        self.redo_stack.clear()
