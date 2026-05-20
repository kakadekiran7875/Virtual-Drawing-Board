import cv2
import time
import os
import math
import numpy as np

from hand_tracking import HandTracker
from gesture_controller import GestureController
from drawing_utils import DrawingCanvas, OneEuroFilter2D
from ui_components import UIComponents
from performance_utils import ThreadedCamera, PerformanceMonitor

def optimize_lighting(img):
    """
    Applies real-time lighting optimization using CLAHE on the LAB luminance
    channel to normalize exposure and boost hand visibility for AI tracking.
    """
    # Convert BGR to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Create and apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    # Merge channels and convert back to BGR
    limg = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return enhanced


def main():
    # 1. Initialize folders
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    
    # Capture size optimized to 960x540 for hardware-level latency reduction
    width, height = 960, 540
    
    # 2. Threaded Video Capture (runs camera I/O on background thread to prevent lag)
    cap = ThreadedCamera(src=0, width=width, height=height)
    cap.start()
    
    # 3. Core Modules
    tracker = HandTracker(max_hands=2, detection_con=0.80, track_con=0.80)
    gesture_ctrl = GestureController()
    ui = UIComponents()
    canvas = DrawingCanvas(width, height)
    perf = PerformanceMonitor()
    
    # 4. State Variables
    current_color = ui.colors["RED"]
    current_color_name = "RED"
    brush_thickness = 15
    eraser_thickness = 80
    
    # Coordinate smoothing via OneEuroFilter2D
    filter_2d = OneEuroFilter2D(min_cutoff=1.0, beta=0.02)
    prev_gesture = "NONE"
    
    # 5. Fullscreen window configuration
    window_name = "Virtual Drawing Board"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    print("🚀 Premium AI Virtual Drawing Board Active (Fullscreen Mode)...")
    print("Press 'q' or 'ESC' to exit.")
    
    try:
        while True:
            # Start profiling latency
            perf.start_frame()
            
            # Fetch frame from Threaded Camera
            success, img = cap.read()
            if not success or img is None:
                continue
                
            img = cv2.flip(img, 1) # Mirror naturally
            
            # Optimize lighting, balance exposure and improve hand visibility
            img = optimize_lighting(img)
            
            # Find hands & draw skeleton overlays
            img = tracker.find_hands(img, draw=True)
            hands_info = tracker.get_active_hands()
            
            hovered_button = None
            
            # Check hand presence
            if len(hands_info) != 0:
                # ----------------------------------------------------
                # HAND 1: DOMINANT HAND (Drawing, UI Selector, Actions)
                # ----------------------------------------------------
                dom_hand = hands_info[0]
                dom_lm = dom_hand["lm_list"]
                dom_type = dom_hand["type"]
                
                # Check gesture of dominant hand
                fingers = tracker.fingers_up(hand_no=0)
                gesture = gesture_ctrl.get_gesture(fingers)
                
                # Coordinate Smoothing for index finger tip (landmark 8)
                x1, y1 = dom_lm[8][1], dom_lm[8][2]
                x1, y1 = filter_2d.filter(time.time(), x1, y1)
                
                # Reset coordinates filter on mode changes (prevents rubber-banding)
                if gesture != prev_gesture:
                    filter_2d.reset()
                    
                    # Finger is lifted! End current stroke and try shape snapping
                    snapped = canvas.reset_prev(enable_shape_snapping=True)
                    if snapped:
                        # Success toast alert for AI Shape Snapping
                        ui.effects.show_toast(f"Snapped to {snapped}!", "AI SHAPE", (80, 220, 255))
                        
                    prev_gesture = gesture
                
                # Render cursor trails
                img = ui.draw_interactive_cursor(img, x1, y1, gesture, current_color, brush_thickness)
                
                # --- A. SELECTION MODE (Index + Middle Up) ---
                if gesture == "SELECT":
                    canvas.reset_prev(enable_shape_snapping=False)
                    
                    # Check intersection with glassmorphic top toolbar
                    for name, (bx1, by1, bx2, by2), btn_color in ui.button_rects:
                        if bx1 < x1 < bx2 and by1 < y1 < by2:
                            hovered_button = name
                            
                            # Interactive Color Selector
                            if name in ["RED", "GREEN", "BLUE", "YELLOW", "WHITE"]:
                                current_color = btn_color
                                current_color_name = name
                            elif name == "ERASER":
                                current_color = ui.colors["ERASER"]
                                current_color_name = "ERASER"
                            elif name == "CLEAR":
                                canvas.clear()
                                ui.effects.show_toast("Canvas Cleared", "CLEAR", (100, 100, 255))
                                gesture_ctrl.force_cooldown("CLEAR")
                            elif name == "SAVE":
                                timestamp = int(time.time())
                                filename = f"drawing_{timestamp}.png"
                                
                                # Export transparent PNG
                                canvas.export_transparent_png(f"outputs/{filename}")
                                # Merge camera frame with canvas and save standard screenshot
                                merged = canvas.merge(img.copy())
                                cv2.imwrite(f"screenshots/screenshot_{timestamp}.png", merged)
                                
                                # Visual Toast alert with saved filename
                                ui.effects.show_toast(f"Saved: {filename}", "SAVE", (100, 255, 100))
                                gesture_ctrl.force_cooldown("SAVE")
                
                # --- B. DRAWING MODE (Index Up Only) ---
                elif gesture == "DRAW":
                    # Draw with active color and selected thickness
                    if current_color_name == "ERASER":
                        canvas.draw(x1, y1, current_color, eraser_thickness)
                    else:
                        canvas.draw(x1, y1, current_color, brush_thickness)
                
                # --- C. UNDO GESTURE (3 Fingers Up) ---
                elif gesture == "UNDO":
                    success = canvas.undo()
                    if success:
                        ui.effects.show_toast("Undo Successful", "UNDO", (100, 100, 255))
                    else:
                        ui.effects.show_toast("Nothing to Undo", "WARN", (80, 80, 240))
                
                # --- D. REDO GESTURE (4 Fingers Up) ---
                elif gesture == "REDO":
                    success = canvas.redo()
                    if success:
                        ui.effects.show_toast("Redo Successful", "REDO", (255, 100, 255))
                    else:
                        ui.effects.show_toast("Nothing to Redo", "WARN", (80, 80, 240))
                
                # --- E. CLEAR GESTURE (All 5 Fingers Up) ---
                elif gesture == "CLEAR":
                    canvas.clear()
                    ui.effects.show_toast("Canvas Cleared", "CLEAR", (100, 100, 255))
                
                # --- F. SAVE GESTURE (Thumb Up) ---
                elif gesture == "SAVE":
                    timestamp = int(time.time())
                    filename = f"drawing_{timestamp}.png"
                    
                    # Export transparent drawing
                    canvas.export_transparent_png(f"outputs/{filename}")
                    # Screenshot
                    merged = canvas.merge(img.copy())
                    cv2.imwrite(f"screenshots/screenshot_{timestamp}.png", merged)
                    
                    # Visual Toast with exact filename
                    ui.effects.show_toast(f"Saved: {filename}", "SAVE", (100, 255, 100))
                
                # --- G. PAUSE DRAWING (Fist) ---
                elif gesture == "PAUSE":
                    canvas.reset_prev(enable_shape_snapping=True)
                    filter_2d.reset()

                # ----------------------------------------------------
                # HAND 2: CONTROL HAND (Dynamic Brush Size Pinch scaling)
                # ----------------------------------------------------
                if len(hands_info) > 1:
                    ctrl_hand = hands_info[1]
                    ctrl_lm = ctrl_hand["lm_list"]
                    ctrl_type = ctrl_hand["type"]
                    
                    # Index tip (8) and Thumb tip (4) landmarks of control hand
                    cx_thumb, cy_thumb = ctrl_lm[4][1], ctrl_lm[4][2]
                    cx_index, cy_index = ctrl_lm[8][1], ctrl_lm[8][2]
                    
                    # Compute distance
                    dist = math.hypot(cx_thumb - cx_index, cy_thumb - cy_index)
                    
                    # Interpolate thickness (pinch width 20px to 140px -> brush width 2px to 50px)
                    brush_thickness = int(np.interp(dist, [20, 140], [2, 50]))
                    
                    # Draw a gorgeous neon circular resize gauge at the pinch midpoint
                    mid_x = (cx_thumb + cx_index) // 2
                    mid_y = (cy_thumb + cy_index) // 2
                    
                    # Dynamic resizing gauge
                    cv2.circle(img, (mid_x, mid_y), int(dist // 2), (255, 130, 255), 2, cv2.LINE_AA)
                    cv2.line(img, (cx_thumb, cy_thumb), (cx_index, cy_index), (255, 255, 255), 1, cv2.LINE_AA)
                    
                    cv2.putText(img, f"BRUSH: {brush_thickness}px", (mid_x - 55, mid_y - int(dist // 2) - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1, cv2.LINE_AA)
            
            else:
                # No hands detected: lift finger, flush filters
                canvas.reset_prev(enable_shape_snapping=True)
                filter_2d.reset()
                prev_gesture = "NONE"

            # 5. Render Glassmorphic UI Toolbar
            img = ui.draw_toolbar(img, current_color_name, hovered_button)
            
            # 6. Smooth Overlay canvas on camera stream
            img = canvas.merge(img)
            
            # 7. End performance latency profiling
            perf.end_frame()
            
            # 8. Render Glassmorphic bottom HUD
            img = ui.draw_status(img, prev_gesture, current_color_name, brush_thickness, perf.get_fps(), perf.get_latency())
            
            # 9. Frame Display window
            cv2.imshow(window_name, img)
            
            # 10. Key events
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27: # 'q' or ESC
                break
            elif key == ord('+') or key == ord('='):
                brush_thickness = min(50, brush_thickness + 2)
            elif key == ord('-'):
                brush_thickness = max(2, brush_thickness - 2)
                
    finally:
        # Cleanup properly to avoid locking hardware resources
        cap.stop()
        cv2.destroyAllWindows()
        print("👋 Drawing Board Exited Cleanly.")

if __name__ == "__main__":
    main()
