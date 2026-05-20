import cv2
import numpy as np
import math
from history_manager import StackHistoryManager
from effects import NeonGlowEffect, ShapeRecognizer

class OneEuroFilter:
    """
    Time-based adaptive low-pass filter (1€ Filter) to smooth cursor coordinates 
    without adding visual latency.
    """
    def __init__(self, t0, x0, dx0=0.0, min_cutoff=1.0, beta=0.02, d_cutoff=1.0):
        self.min_cutoff = float(min_cutoff)
        self.beta = float(beta)
        self.d_cutoff = float(d_cutoff)
        self.x_prev = float(x0)
        self.dx_prev = float(dx0)
        self.t_prev = float(t0)

    def _alpha(self, cutoff, dt):
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def filter(self, t, x):
        t = float(t)
        x = float(x)
        dt = t - self.t_prev
        if dt <= 0:
            return self.x_prev

        # Estimate speed (derivative) and filter it
        dx = (x - self.x_prev) / dt
        edx_alpha = self._alpha(self.d_cutoff, dt)
        dx_hat = edx_alpha * dx + (1.0 - edx_alpha) * self.dx_prev

        # Compute adaptive cutoff frequency based on speed
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)

        # Filter the signal
        x_alpha = self._alpha(cutoff, dt)
        x_hat = x_alpha * x + (1.0 - x_alpha) * self.x_prev

        # Save states
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t

        return x_hat


class OneEuroFilter2D:
    def __init__(self, min_cutoff=1.0, beta=0.02, d_cutoff=1.0):
        self.x_filter = None
        self.y_filter = None
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff

    def filter(self, t, x, y):
        if self.x_filter is None or self.y_filter is None:
            self.x_filter = OneEuroFilter(t, x, min_cutoff=self.min_cutoff, beta=self.beta, d_cutoff=self.d_cutoff)
            self.y_filter = OneEuroFilter(t, y, min_cutoff=self.min_cutoff, beta=self.beta, d_cutoff=self.d_cutoff)
            return int(x), int(y)
        
        smooth_x = self.x_filter.filter(t, x)
        smooth_y = self.y_filter.filter(t, y)
        return int(smooth_x), int(smooth_y)

    def reset(self):
        self.x_filter = None
        self.y_filter = None


class DrawingCanvas:
    """
    Manages the virtual drawing board layer.
    Integrates Neon brush effects, StackHistoryManager for Undo/Redo,
    transparent exports, and stroke tracking for AI Shape Snapping.
    Default size set to 960x540 to match camera optimization bounds.
    """
    def __init__(self, width=960, height=540):
        self.width = width
        self.height = height
        self.canvas = np.zeros((self.height, self.width, 3), np.uint8)
        self.prev_x, self.prev_y = 0, 0
        
        # Integrate stack-based history
        self.history = StackHistoryManager(max_history=20)
        
        # Track coordinate points during a single draw stroke for shape recognition
        self.current_stroke_points = []
        self.active_color = (255, 255, 255)
        self.active_thickness = 15

    def draw(self, x, y, color, thickness):
        """
        Draws neon line segments between consecutive coordinates.
        Captures the path for geometric shape snapping and triggers history saves.
        """
        self.active_color = color
        self.active_thickness = thickness

        if self.prev_x == 0 and self.prev_y == 0:
            # Stroke just started! Save canvas state BEFORE any lines are drawn
            self.history.save_state(self.canvas)
            self.prev_x, self.prev_y = x, y
            self.current_stroke_points = []

        # Record points for AI Shape Snapping
        self.current_stroke_points.append((x, y))

        # Perform high-performance neon line drawing
        NeonGlowEffect.draw_neon_line(self.canvas, (self.prev_x, self.prev_y), (x, y), color, thickness)
        
        self.prev_x, self.prev_y = x, y

    def reset_prev(self, enable_shape_snapping=True):
        """
        Resets continuous line tracking.
        If shape snapping is active, analyzes the current stroke.
        If a geometric shape is matched, it replaces the rough drawing with the perfect shape!
        Returns:
            str: Snapped shape category name (e.g., "CIRCLE", "RECTANGLE", "LINE") or None.
        """
        snapped_shape_name = None

        if enable_shape_snapping and self.current_stroke_points and len(self.current_stroke_points) >= 15:
            # Analyze stroke with ShapeRecognizer
            shape_info = ShapeRecognizer.recognize(self.current_stroke_points)
            
            if shape_info:
                shape_type = shape_info[0]
                
                # Retrieve canvas state BEFORE the current rough scribble started
                undo_canvas = self.history.undo(self.canvas)
                if undo_canvas is not None:
                    # Restore clean canvas
                    self.canvas = undo_canvas
                    
                    # Draw perfect shape
                    if shape_type == "LINE":
                        pt1, pt2 = shape_info[1], shape_info[2]
                        NeonGlowEffect.draw_neon_line(self.canvas, pt1, pt2, self.active_color, self.active_thickness)
                        snapped_shape_name = "LINE"
                    
                    elif shape_type == "CIRCLE":
                        center, radius = shape_info[1], shape_info[2]
                        # Draw circle using neon line segments or concentric rings
                        if self.active_color == (0, 0, 0): # Eraser circle
                            cv2.circle(self.canvas, center, radius, self.active_color, self.active_thickness, cv2.LINE_AA)
                        else:
                            # Neon brush circle: Outer glow, medium glow, core
                            cv2.circle(self.canvas, center, radius, self.active_color, int(self.active_thickness * 2.2), cv2.LINE_AA)
                            cv2.circle(self.canvas, center, radius, self.active_color, int(self.active_thickness * 1.5), cv2.LINE_AA)
                            cv2.circle(self.canvas, center, radius, (255, 255, 255), max(2, int(self.active_thickness * 0.4)), cv2.LINE_AA)
                        snapped_shape_name = "CIRCLE"
                        
                    elif shape_type == "RECTANGLE":
                        pt1, pt2 = shape_info[1], shape_info[2]
                        if self.active_color == (0, 0, 0): # Eraser rect
                            cv2.rectangle(self.canvas, pt1, pt2, self.active_color, self.active_thickness, cv2.LINE_AA)
                        else:
                            # Neon brush rect
                            cv2.rectangle(self.canvas, pt1, pt2, self.active_color, int(self.active_thickness * 2.2), cv2.LINE_AA)
                            cv2.rectangle(self.canvas, pt1, pt2, self.active_color, int(self.active_thickness * 1.5), cv2.LINE_AA)
                            cv2.rectangle(self.canvas, pt1, pt2, (255, 255, 255), max(2, int(self.active_thickness * 0.4)), cv2.LINE_AA)
                        snapped_shape_name = "RECTANGLE"

                    # Save the new perfect canvas state to the history stack
                    self.history.save_state(self.canvas)

        self.prev_x, self.prev_y = 0, 0
        self.current_stroke_points = []
        return snapped_shape_name

    def undo(self):
        """
        Triggers an undo step.
        """
        undone_canvas = self.history.undo(self.canvas)
        if undone_canvas is not None:
            self.canvas = undone_canvas
            return True
        return False

    def redo(self):
        """
        Triggers a redo step.
        """
        redone_canvas = self.history.redo(self.canvas)
        if redone_canvas is not None:
            self.canvas = redone_canvas
            return True
        return False

    def clear(self):
        """
        Clears the canvas, saving state beforehand to support clear-undo.
        """
        self.history.save_state(self.canvas)
        self.canvas = np.zeros((self.height, self.width, 3), np.uint8)
        self.prev_x, self.prev_y = 0, 0
        self.current_stroke_points = []

    def export_transparent_png(self, filepath):
        """
        Exports the canvas drawing as a transparent 4-channel BGRA PNG image.
        """
        # Convert BGR to Grayscale
        gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        
        # Build transparency mask (non-black pixels are opaque)
        _, alpha = cv2.threshold(gray, 5, 255, cv2.THRESH_BINARY)
        
        # Split channels and merge with Alpha mask
        b, g, r = cv2.split(self.canvas)
        bgra = cv2.merge([b, g, r, alpha])
        
        # Write to disk
        return cv2.imwrite(filepath, bgra)

    def merge(self, frame):
        """
        Alpha blends the drawing canvas with the live webcam feed.
        Defensively resizes the canvas if the camera frame dimensions differ.
        """
        fh, fw = frame.shape[:2]
        ch, cw = self.canvas.shape[:2]
        if fh != ch or fw != cw:
            self.canvas = cv2.resize(self.canvas, (fw, fh), interpolation=cv2.INTER_AREA)

        gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, inv_mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY_INV)
        inv_mask = cv2.cvtColor(inv_mask, cv2.COLOR_GRAY2BGR)
        
        frame_bg = cv2.bitwise_and(frame, inv_mask)
        frame = cv2.bitwise_or(frame_bg, self.canvas)
        return frame
