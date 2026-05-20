import cv2
import numpy as np

class UIComponents:
    def __init__(self):
        # Professional color palette (BGR format for OpenCV)
        self.colors = {
            "RED": (60, 60, 255),
            "GREEN": (100, 255, 100),
            "BLUE": (255, 150, 50),
            "YELLOW": (50, 220, 255),
            "WHITE": (240, 240, 240),
            "ERASER": (0, 0, 0) # Pitch black is treated as transparent in merge
        }
        
        # Layout metrics
        self.header_height = 110
        self.button_rects = []
        
    def draw_toolbar(self, img, active_name, hovered_name=None):
        """
        Draws the gorgeous glassmorphism floating toolbar at the top.
        """
        h, w, c = img.shape
        overlay = img.copy()
        
        # Dimensions for the floating toolbar
        tb_w = 960
        tb_h = 80
        tb_x1 = (w - tb_w) // 2
        tb_y1 = 15
        tb_x2 = tb_x1 + tb_w
        tb_y2 = tb_y1 + tb_h
        
        # 1. Translucent background card (frosted glass)
        cv2.rectangle(overlay, (tb_x1, tb_y1), (tb_x2, tb_y2), (25, 25, 25), cv2.FILLED)
        alpha = 0.75
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        
        # 2. Sleek thin border
        cv2.rectangle(img, (tb_x1, tb_y1), (tb_x2, tb_y2), (200, 200, 200), 1, cv2.LINE_AA)
        
        buttons = [
            ("RED", self.colors["RED"]),
            ("GREEN", self.colors["GREEN"]),
            ("BLUE", self.colors["BLUE"]),
            ("YELLOW", self.colors["YELLOW"]),
            ("WHITE", self.colors["WHITE"]),
            ("ERASER", (180, 180, 180)), 
            ("CLEAR", (60, 60, 255)),
            ("SAVE", (255, 140, 60))
        ]
        
        col_w = tb_w // len(buttons)
        self.button_rects = []
        
        for i, (name, color) in enumerate(buttons):
            bx1 = tb_x1 + i * col_w
            by1 = tb_y1
            bx2 = tb_x1 + (i + 1) * col_w
            by2 = tb_y2
            
            # Store exact bounding coordinates
            self.button_rects.append((name, (bx1, by1, bx2, by2), self.colors.get(name, color)))
            
            is_active = (name == active_name)
            is_hovered = (name == hovered_name)
            
            cx = bx1 + col_w // 2
            cy = by1 + tb_h // 2
            
            if name in ["RED", "GREEN", "BLUE", "YELLOW", "WHITE"]:
                # Color Swatch Design
                r = 18
                # Active/Hover rings
                if is_active:
                    cv2.circle(img, (cx, cy), r + 7, (255, 255, 255), 2, cv2.LINE_AA)
                elif is_hovered:
                    cv2.circle(img, (cx, cy), r + 7, (180, 180, 180), 1, cv2.LINE_AA)
                    
                # The core swatch circle
                cv2.circle(img, (cx, cy), r, color, cv2.FILLED, cv2.LINE_AA)
                cv2.circle(img, (cx, cy), r, (255, 255, 255), 1, cv2.LINE_AA)
                
            else:
                # Functional Button Design (Pill shape)
                px1 = bx1 + 10
                py1 = by1 + 20
                px2 = bx2 - 10
                py2 = by2 - 20
                
                # Pill background and border
                if is_active:
                    cv2.rectangle(img, (px1, py1), (px2, py2), (240, 240, 240), cv2.FILLED)
                    border_color = (255, 255, 255)
                    text_color = (30, 30, 30)
                    text_thickness = 2
                elif is_hovered:
                    # Hover transparent fill
                    overlay_pill = img.copy()
                    cv2.rectangle(overlay_pill, (px1, py1), (px2, py2), (100, 100, 100), cv2.FILLED)
                    cv2.addWeighted(overlay_pill, 0.4, img, 0.6, 0, img)
                    border_color = (255, 255, 255)
                    text_color = (255, 255, 255)
                    text_thickness = 2
                else:
                    cv2.rectangle(img, (px1, py1), (px2, py2), (40, 40, 40), cv2.FILLED)
                    border_color = (150, 150, 150)
                    text_color = (200, 200, 200)
                    text_thickness = 1
                
                cv2.rectangle(img, (px1, py1), (px2, py2), border_color, 1, cv2.LINE_AA)
                
                # Typography
                text_size = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_thickness)[0]
                tx = bx1 + (col_w - text_size[0]) // 2
                ty = by1 + (tb_h + text_size[1]) // 2
                cv2.putText(img, name, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, text_thickness, cv2.LINE_AA)
                
        return img
        
    def draw_status(self, img, gesture, current_color_name, brush_thickness, fps):
        """
        Draws dynamic, glassmorphic floating HUD indicator at the bottom center.
        """
        h, w, c = img.shape
        overlay = img.copy()
        
        hud_w = 720
        hud_h = 50
        hud_x1 = (w - hud_w) // 2
        hud_y1 = h - 65
        hud_x2 = hud_x1 + hud_w
        hud_y2 = hud_y1 + hud_h
        
        # 1. Translucent background capsule
        cv2.rectangle(overlay, (hud_x1, hud_y1), (hud_x2, hud_y2), (20, 20, 20), cv2.FILLED)
        alpha = 0.75
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        
        # 2. Sleek thin border
        cv2.rectangle(img, (hud_x1, hud_y1), (hud_x2, hud_y2), (180, 180, 180), 1, cv2.LINE_AA)
        
        # Define statuses and colors
        # Separating HUD into 4 sections
        sec_w = hud_w // 4
        
        sections = [
            (f"FPS: {int(fps)}", (100, 255, 100)),
            (f"MODE: {gesture}", (255, 180, 100)),
            (f"COLOR: {current_color_name}", (100, 220, 255)),
            (f"SIZE: {brush_thickness}px", (255, 150, 255))
        ]
        
        for i, (text, t_color) in enumerate(sections):
            sx1 = hud_x1 + i * sec_w
            sx2 = hud_x1 + (i + 1) * sec_w
            
            # Typography
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)[0]
            tx = sx1 + (sec_w - text_size[0]) // 2
            ty = hud_y1 + (hud_h + text_size[1]) // 2
            
            cv2.putText(img, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.55, t_color, 2, cv2.LINE_AA)
            
            # Vertical divider line (except last section)
            if i < 3:
                cv2.line(img, (sx2, hud_y1 + 10), (sx2, hud_y2 - 10), (100, 100, 100), 1, cv2.LINE_AA)
                
        # Gesture Guide (Floating text above HUD)
        guide_text = "INDEX: Draw | INDEX+MIDDLE: Hover & Select | ALL: Clear | FIST: Pause | THUMB: Save"
        text_size = cv2.getTextSize(guide_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)[0]
        gtx = (w - text_size[0]) // 2
        gty = hud_y1 - 15
        
        # Sleek low-contrast white guide text
        cv2.putText(img, guide_text, (gtx, gty), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1, cv2.LINE_AA)
        
        return img
