import cv2
import numpy as np
import math
import time

class NeonGlowEffect:
    """
    Renders beautiful multi-pass lines and points with anti-aliasing to simulate
    a futuristic high-intensity neon glow in real-time.
    """
    @staticmethod
    def draw_neon_line(canvas, pt1, pt2, color, thickness):
        """
        Draws concentric lines with decreasing thickness and increasing brightness
        to form a realistic core-glow neon effect.
        """
        if color == (0, 0, 0): # Eraser
            cv2.line(canvas, pt1, pt2, color, thickness, cv2.LINE_AA)
            return

        # 1. Broad outer glow (highly transparent, simulated by blending a thick line)
        glow_thickness = int(thickness * 2.5)
        # Apply a soft blending by drawing on a temp layer
        glow_color = color
        cv2.line(canvas, pt1, pt2, glow_color, glow_thickness, cv2.LINE_AA)
        
        # 2. Medium inner glow
        cv2.line(canvas, pt1, pt2, color, int(thickness * 1.5), cv2.LINE_AA)

        # 3. Bright core (white/extremely light center)
        core_color = (255, 255, 255)
        if color == (240, 240, 240): # White color
            core_color = (220, 255, 220) # Pale green core for white line
            
        cv2.line(canvas, pt1, pt2, core_color, max(2, int(thickness * 0.4)), cv2.LINE_AA)


class ShapeRecognizer:
    """
    Analyzes drawn coordinate lists when the user lifts their drawing finger
    and approximates them into perfect geometric shapes using contour geometry.
    """
    @staticmethod
    def recognize(points):
        """
        Analyzes a list of points (x, y) representing a single stroke.
        Returns:
            Tuple: (shape_type, *parameters) or None if freehand drawing.
        """
        if len(points) < 15:
            return None

        # Convert points to contour format
        contour = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        
        # 1. Check if it's a straight line
        # If the start-to-end straight-line distance is very close to the actual path length
        perimeter = cv2.arcLength(contour, False)
        start_pt = points[0]
        end_pt = points[-1]
        straight_dist = math.hypot(end_pt[0] - start_pt[0], end_pt[1] - start_pt[1])
        
        if perimeter > 0 and (straight_dist / perimeter) > 0.88:
            return ("LINE", start_pt, end_pt)

        # 2. Check for Circle
        area = cv2.contourArea(contour)
        closed_perimeter = cv2.arcLength(contour, True)
        
        if closed_perimeter > 0:
            circularity = 4 * math.pi * area / (closed_perimeter ** 2)
            # A hand-drawn circle usually has circularity between 0.65 and 0.95
            if circularity > 0.65:
                (cx, cy), radius = cv2.minEnclosingCircle(contour)
                # Ensure the radius is reasonable
                if radius > 10:
                    return ("CIRCLE", (int(cx), int(cy)), int(radius))

        # 3. Check for Rectangle
        # Approximate the polygon shape
        approx = cv2.approxPolyDP(contour, 0.03 * closed_perimeter, True)
        
        # A rectangle/square should approximate to 4 vertices
        if 3 <= len(approx) <= 5:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 15 and h > 15:
                return ("RECTANGLE", (x, y), (x + w, y + h))

        return None


class VisualEffects:
    """
    Manages custom visual aesthetics such as cursor particle trails, 
    pulsating glowing rings, and glassmorphic toast notification cards.
    """
    def __init__(self):
        self.cursor_history = []
        self.toast_text = ""
        self.toast_start_time = 0.0
        self.toast_duration = 1.8
        self.toast_color = (0, 255, 0)
        self.toast_icon = "INFO"

    def add_trail(self, pt):
        self.cursor_history.append((pt, time.time()))
        # Limit cursor trail history size
        if len(self.cursor_history) > 12:
            self.cursor_history.pop(0)

    def draw_trail(self, img, color):
        """
        Draws fading trail circles behind the cursor for smooth visual cues.
        """
        now = time.time()
        for i, (pt, t) in enumerate(self.cursor_history):
            age = now - t
            if age > 0.6:
                continue
            
            # Fading factor
            alpha = max(0.0, 1.0 - (age / 0.6))
            radius = max(2, int((i + 1) * 0.8))
            
            # Fade color towards background
            trail_color = [int(c * alpha) for c in color]
            cv2.circle(img, pt, radius, tuple(trail_color), cv2.FILLED, cv2.LINE_AA)

    def show_toast(self, text, icon="INFO", color=(100, 255, 100)):
        """
        Triggers an animated visual notification.
        """
        self.toast_text = text
        self.toast_icon = icon
        self.toast_color = color
        self.toast_start_time = time.time()

    def draw_toast(self, img):
        """
        Renders a gorgeous glassmorphic notification box at the top center.
        """
        if not self.toast_text:
            return img

        elapsed = time.time() - self.toast_start_time
        if elapsed > self.toast_duration:
            self.toast_text = ""
            return img

        h, w, c = img.shape
        overlay = img.copy()

        # Toast box dimensions (animated drop down or steady top center)
        box_w = 420
        box_h = 55
        box_x1 = (w - box_w) // 2
        box_y1 = 110 # Rendered just below the floating toolbar (which ends at y=95)
        box_x2 = box_x1 + box_w
        box_y2 = box_y1 + box_h

        # Compute transparency fade out
        alpha = 0.85
        if elapsed > (self.toast_duration - 0.5):
            alpha *= (self.toast_duration - elapsed) / 0.5
            alpha = max(0.0, alpha)

        if alpha <= 0:
            return img

        # 1. Frosted card fill
        cv2.rectangle(overlay, (box_x1, box_y1), (box_x2, box_y2), (30, 30, 30), cv2.FILLED)
        
        # Apply ROI blur to simulate glassmorphism background
        roi = img[box_y1:box_y2, box_x1:box_x2]
        if roi.size > 0:
            roi_blurred = cv2.GaussianBlur(roi, (21, 21), 0)
            img[box_y1:box_y2, box_x1:box_x2] = roi_blurred
            
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

        # 2. Glowing animated border
        border_color = [int(val * alpha) for val in self.toast_color]
        cv2.rectangle(img, (box_x1, box_y1), (box_x2, box_y2), tuple(border_color), 2, cv2.LINE_AA)

        # 3. Icon and Text rendering
        full_text = f"[{self.toast_icon}] {self.toast_text}"
        text_size = cv2.getTextSize(full_text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)[0]
        
        tx = box_x1 + (box_w - text_size[0]) // 2
        ty = box_y1 + (box_h + text_size[1]) // 2
        
        text_color = (255, 255, 255)
        cv2.putText(img, full_text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.55, text_color, 2, cv2.LINE_AA)

        return img
