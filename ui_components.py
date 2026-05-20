import cv2
import numpy as np
import time
from effects import VisualEffects

class UIComponents:
    """
    Renders the gorgeous glassmorphic HUD, floating toolbar, cursor particle trails, 
    interactive color swatches, gesture sidebar guide, and visual action toast alerts.
    """
    def __init__(self):
        # Vibrant Neon/Futuristic BGR palette
        self.colors = {
            "RED": (80, 80, 255),      # Neon Red-Crimson
            "GREEN": (100, 255, 100),   # Neon Green
            "BLUE": (255, 190, 50),     # Neon Electric Blue
            "YELLOW": (80, 220, 255),   # Neon Gold-Yellow
            "WHITE": (245, 245, 245),   # Bright Arctic White
            "ERASER": (0, 0, 0)         # Pitch Black (Eraser)
        }
        
        self.header_height = 110
        self.button_rects = []
        
        # Instantiate built-in visual effects (trails, toasts)
        self.effects = VisualEffects()

    def _draw_blur_glass_card(self, img, x1, y1, x2, y2, bg_color=(20, 20, 20), alpha=0.7, border_color=(150, 150, 150), border_thickness=1):
        """
        Draws a realistic glassmorphic card with a Gaussian-blurred backdrop and neon border.
        """
        h, w, c = img.shape
        # Clamping to prevent Out-Of-Bounds slice errors
        x1 = max(0, min(x1, w - 1))
        y1 = max(0, min(y1, h - 1))
        x2 = max(0, min(x2, w - 1))
        y2 = max(0, min(y2, h - 1))

        if x2 <= x1 or y2 <= y1:
            return

        overlay = img.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_color, cv2.FILLED)
        
        # 1. Backing blur crop
        roi = img[y1:y2, x1:x2]
        if roi.size > 0:
            roi_blurred = cv2.GaussianBlur(roi, (25, 25), 0)
            img[y1:y2, x1:x2] = roi_blurred
            
        # 2. Blend dark tint translucent layer
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        
        # 3. Draw sleek anti-aliased border
        cv2.rectangle(img, (x1, y1), (x2, y2), border_color, border_thickness, cv2.LINE_AA)

    def draw_toolbar(self, img, active_name, hovered_name=None):
        """
        Draws the floating glassmorphic toolbar at the top center.
        """
        h, w, c = img.shape
        
        tb_w = 1000
        tb_h = 80
        tb_x1 = (w - tb_w) // 2
        tb_y1 = 15
        tb_x2 = tb_x1 + tb_w
        tb_y2 = tb_y1 + tb_h
        
        # Draw base frosted glass toolbar
        self._draw_blur_glass_card(img, tb_x1, tb_y1, tb_x2, tb_y2, bg_color=(15, 15, 15), alpha=0.6, border_color=(80, 80, 80), border_thickness=1)
        
        buttons = [
            ("RED", self.colors["RED"]),
            ("GREEN", self.colors["GREEN"]),
            ("BLUE", self.colors["BLUE"]),
            ("YELLOW", self.colors["YELLOW"]),
            ("WHITE", self.colors["WHITE"]),
            ("ERASER", (180, 180, 180)), 
            ("CLEAR", (100, 100, 255)),
            ("SAVE", (255, 140, 60))
        ]
        
        col_w = tb_w // len(buttons)
        self.button_rects = []
        
        for i, (name, color) in enumerate(buttons):
            bx1 = tb_x1 + i * col_w
            by1 = tb_y1
            bx2 = tb_x1 + (i + 1) * col_w
            by2 = tb_y2
            
            # Store buttons boundaries
            self.button_rects.append((name, (bx1, by1, bx2, by2), self.colors.get(name, color)))
            
            is_active = (name == active_name)
            is_hovered = (name == hovered_name)
            
            cx = bx1 + col_w // 2
            cy = by1 + tb_h // 2
            
            if name in ["RED", "GREEN", "BLUE", "YELLOW", "WHITE"]:
                # Color Swatch Rendering
                r = 18
                if is_active:
                    # Animated pulsating active ring
                    pulse = int(2 + math.sin(time.time() * 8) * 2)
                    cv2.circle(img, (cx, cy), r + 7 + pulse, color, 2, cv2.LINE_AA)
                    cv2.circle(img, (cx, cy), r + 4, (255, 255, 255), 1, cv2.LINE_AA)
                elif is_hovered:
                    cv2.circle(img, (cx, cy), r + 7, (200, 200, 200), 1, cv2.LINE_AA)
                    
                # Base circle
                cv2.circle(img, (cx, cy), r, color, cv2.FILLED, cv2.LINE_AA)
                cv2.circle(img, (cx, cy), r - 3, (255, 255, 255), 1, cv2.LINE_AA)
                
            else:
                # Pill-shaped utility buttons
                px1 = bx1 + 12
                py1 = by1 + 22
                px2 = bx2 - 12
                py2 = by2 - 22
                
                pill_bg = (30, 30, 30)
                pill_border = (100, 100, 100)
                text_color = (200, 200, 200)
                thick = 1
                
                if is_active:
                    pill_bg = (245, 245, 245)
                    pill_border = (255, 255, 255)
                    text_color = (15, 15, 15)
                    thick = 2
                elif is_hovered:
                    pill_bg = (60, 60, 60)
                    pill_border = color # Light up border with theme color
                    text_color = (255, 255, 255)
                    thick = 2
                
                # Draw rounded rectangle
                cv2.rectangle(img, (px1, py1), (px2, py2), pill_bg, cv2.FILLED)
                cv2.rectangle(img, (px1, py1), (px2, py2), pill_border, 1, cv2.LINE_AA)
                
                # Center-aligned text
                text_size = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.45, thick)[0]
                tx = bx1 + (col_w - text_size[0]) // 2
                ty = by1 + (tb_h + text_size[1]) // 2
                cv2.putText(img, name, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.45, text_color, thick, cv2.LINE_AA)
                
        return img

    def draw_sidebar_guide(self, img):
        """
        Draws a gorgeous, futuristic floating glass side panel explaining the gestures.
        """
        h, w, c = img.shape
        
        sb_w = 280
        sb_h = 360
        sb_x1 = 20
        sb_y1 = (h - sb_h) // 2 - 20
        sb_x2 = sb_x1 + sb_w
        sb_y2 = sb_y1 + sb_h
        
        # Transparent sidebar backer
        self._draw_blur_glass_card(img, sb_x1, sb_y1, sb_x2, sb_y2, bg_color=(12, 12, 12), alpha=0.65, border_color=(90, 90, 90), border_thickness=1)
        
        # Title Header
        title = "GESTURE INTERFACE"
        cv2.putText(img, title, (sb_x1 + 20, sb_y1 + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.line(img, (sb_x1 + 20, sb_y1 + 45), (sb_x2 - 20, sb_y1 + 45), (100, 100, 100), 1, cv2.LINE_AA)
        
        # Gesture instructions
        guides = [
            ("☝ DRAW", "1 Finger Up"),
            ("✌ SELECT", "2 Fingers Up"),
            ("🖐 CLEAR", "5 Fingers Up"),
            ("✊ PAUSE", "Closed Fist"),
            ("👍 SAVE", "Thumb Up"),
            ("🤟 UNDO", "3 Fingers Up"),
            ("🖖 REDO", "4 Fingers Up")
        ]
        
        start_y = sb_y1 + 80
        for i, (action, gesture) in enumerate(guides):
            y_pos = start_y + i * 36
            # Action name with neon theme coloring
            cv2.putText(img, action, (sb_x1 + 20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 220, 255), 1, cv2.LINE_AA)
            # Corresponding finger state description
            cv2.putText(img, gesture, (sb_x1 + 130, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (180, 180, 180), 1, cv2.LINE_AA)
            
        # Draw a mini futuristic neon decor line on sidebar bottom
        cv2.line(img, (sb_x1 + 20, sb_y2 - 15), (sb_x2 - 20, sb_y2 - 15), (80, 80, 80), 1, cv2.LINE_AA)
        
        return img

    def draw_status(self, img, gesture, current_color_name, brush_thickness, fps, latency=0.0):
        """
        Draws the futuristic floating glassmorphism HUD indicator at the bottom center.
        """
        h, w, c = img.shape
        
        hud_w = 880
        hud_h = 55
        hud_x1 = (w - hud_w) // 2
        hud_y1 = h - 75
        hud_x2 = hud_x1 + hud_w
        hud_y2 = hud_y1 + hud_h
        
        # Glassmorphic capsule card
        self._draw_blur_glass_card(img, hud_x1, hud_y1, hud_x2, hud_y2, bg_color=(12, 12, 12), alpha=0.70, border_color=(100, 100, 100), border_thickness=1)
        
        sec_w = hud_w // 5
        
        # Dynamic active theme color for details
        theme_color = self.colors.get(current_color_name, (255, 255, 255))
        if current_color_name == "ERASER":
            theme_color = (200, 200, 200)

        sections = [
            (f"FPS: {fps}", (100, 255, 100)),
            (f"LATENCY: {latency:.1f}ms", (100, 255, 255)),
            (f"MODE: {gesture}", (255, 150, 50)),
            (f"COLOR: {current_color_name}", theme_color),
            (f"BRUSH: {brush_thickness}px", (255, 100, 255))
        ]
        
        for i, (text, t_color) in enumerate(sections):
            sx1 = hud_x1 + i * sec_w
            sx2 = hud_x1 + (i + 1) * sec_w
            
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 2)[0]
            tx = sx1 + (sec_w - text_size[0]) // 2
            ty = hud_y1 + (hud_h + text_size[1]) // 2
            
            cv2.putText(img, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.48, t_color, 2, cv2.LINE_AA)
            
            # Divider
            if i < 4:
                cv2.line(img, (sx2, hud_y1 + 12), (sx2, hud_y2 - 12), (70, 70, 70), 1, cv2.LINE_AA)
                
        # Draw side guide panel
        img = self.draw_sidebar_guide(img)
        
        # Render visual toast notifications
        img = self.effects.draw_toast(img)
        
        return img

    def draw_interactive_cursor(self, img, x, y, gesture, color, thickness):
        """
        Draws dynamic animated glowing cursors, brush previews, and coordinates trials.
        """
        # Save trail coordinate
        self.effects.add_trail((x, y))
        # Draw trails behind cursor
        self.effects.draw_trail(img, color if color != (0, 0, 0) else (150, 150, 150))
        
        if gesture == "SELECT":
            # 1. Target Selector Crosshair (Pulse circle + outer ticks)
            pulse = int(math.sin(time.time() * 12) * 2)
            cv2.circle(img, (x, y), 8 + pulse, color, 2, cv2.LINE_AA)
            cv2.circle(img, (x, y), 2, (255, 255, 255), cv2.FILLED, cv2.LINE_AA)
            
            # Draw cursor selector ticks (North, South, East, West)
            cv2.line(img, (x, y - 14), (x, y - 6), (255, 255, 255), 1, cv2.LINE_AA)
            cv2.line(img, (x, y + 6), (x, y + 14), (255, 255, 255), 1, cv2.LINE_AA)
            cv2.line(img, (x - 14, y), (x - 6, y), (255, 255, 255), 1, cv2.LINE_AA)
            cv2.line(img, (x + 6, y), (x + 14, y), (255, 255, 255), 1, cv2.LINE_AA)
            
        elif gesture == "DRAW":
            # 2. Dynamic Brush Preview Circle showing actual brush circumference
            preview_r = max(4, thickness // 2)
            glow_color = color if color != (0, 0, 0) else (120, 120, 120)
            
            # Outer neon preview ring
            cv2.circle(img, (x, y), preview_r + 3, glow_color, 1, cv2.LINE_AA)
            # Solid white core dot
            cv2.circle(img, (x, y), 3, (255, 255, 255), cv2.FILLED, cv2.LINE_AA)
            
        return img
