import cv2
import numpy as np
import math

class OneEuroFilter:
    def __init__(self, t0, x0, dx0=0.0, min_cutoff=0.8, beta=0.03, d_cutoff=1.0):
        """
        Adaptive low-pass filter (1€ Filter).
        - min_cutoff: Minimum cutoff frequency (Hz). Higher values reduce lag at low speeds.
        - beta: Speed coefficient. Higher values reduce lag at high speeds.
        - d_cutoff: Cutoff frequency for derivative smoothing.
        """
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

        # Estimate derivative (speed) and filter it
        dx = (x - self.x_prev) / dt
        edx_alpha = self._alpha(self.d_cutoff, dt)
        dx_hat = edx_alpha * dx + (1.0 - edx_alpha) * self.dx_prev

        # Compute adaptive cutoff frequency
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)

        # Filter the signal
        x_alpha = self._alpha(cutoff, dt)
        x_hat = x_alpha * x + (1.0 - x_alpha) * self.x_prev

        # Save state
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t

        return x_hat

class OneEuroFilter2D:
    def __init__(self, min_cutoff=0.8, beta=0.03, d_cutoff=1.0):
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
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        # Canvas initialized to pitch black
        self.canvas = np.zeros((self.height, self.width, 3), np.uint8)
        self.prev_x, self.prev_y = 0, 0
        
    def draw(self, x, y, color, thickness):
        """
        Draws a line on the canvas from the previous coordinates to the current ones.
        Smooths out the drawing experience.
        """
        if self.prev_x == 0 and self.prev_y == 0:
            self.prev_x, self.prev_y = x, y
            
        cv2.line(self.canvas, (self.prev_x, self.prev_y), (x, y), color, thickness)
        self.prev_x, self.prev_y = x, y
        
    def reset_prev(self):
        """
        Resets previous coordinates, stopping the line continuity.
        Call this when the user pauses drawing or lifts their finger.
        """
        self.prev_x, self.prev_y = 0, 0
        
    def clear(self):
        """
        Wipes the canvas clean.
        """
        self.canvas = np.zeros((self.height, self.width, 3), np.uint8)
        
    def merge(self, frame):
        """
        Merges the drawing canvas with the webcam feed.
        """
        # Convert canvas to grayscale to create masks
        gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        
        # Anything not black becomes white (mask for the drawing)
        _, inv_mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY_INV)
        inv_mask = cv2.cvtColor(inv_mask, cv2.COLOR_GRAY2BGR)
        
        # Black out the regions on the webcam frame where the drawing should go
        frame_bg = cv2.bitwise_and(frame, inv_mask)
        
        # Add the drawing canvas onto the frame
        frame = cv2.bitwise_or(frame_bg, self.canvas)
        return frame
