import cv2
import time
import os

from hand_tracking import HandTracker
from gesture_controller import GestureController
from drawing_utils import DrawingCanvas, OneEuroFilter2D
from ui_components import UIComponents

def main():
    # Setup necessary directories
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    
    # Initialization
    width, height = 1280, 720
    cap = cv2.VideoCapture(0)
    cap.set(3, width)
    cap.set(4, height)
    
    # Modules
    # Lowered confidence slightly to 0.75 for better tracking stability when hand moves fast
    tracker = HandTracker(detection_con=0.75, track_con=0.75)
    gesture_ctrl = GestureController()
    ui = UIComponents()
    canvas = DrawingCanvas(width, height)
    
    # State variables
    current_color = ui.colors["RED"]
    current_color_name = "RED"
    brush_thickness = 15
    eraser_thickness = 80
    
    pTime = 0
    save_cooldown = 0
    
    # Coordinate smoothing via adaptive 1€ Filter
    filter_2d = OneEuroFilter2D(min_cutoff=0.8, beta=0.03, d_cutoff=1.0)
    prev_gesture = "NONE"
    
    print("🚀 Virtual Drawing Board Started...")
    print("Press 'q' to quit, 'c' to clear, 's' to save, '+/-' to adjust brush size.")
    
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to capture video.")
            break
            
        img = cv2.flip(img, 1) # Mirror image for natural interaction
        
        # Find hand landmarks
        img = tracker.find_hands(img)
        lm_list = tracker.find_position(img, draw=False)
        
        # Recognize Gestures
        fingers = tracker.fingers_up()
        gesture = gesture_ctrl.get_gesture(fingers)
        
        # Reset filter on gesture transition to prevent trailing lines or rubber-banding
        if gesture != prev_gesture:
            filter_2d.reset()
            canvas.reset_prev()
            prev_gesture = gesture
        
        hovered_button = None
        if len(lm_list) != 0:
            # Coordinates for Index and Middle fingers
            x1, y1 = lm_list[8][1], lm_list[8][2]
            x2, y2 = lm_list[12][1], lm_list[12][2]
            
            # --- Adaptive Speed-Based 1€ Filtering ---
            x1, y1 = filter_2d.filter(time.time(), x1, y1)
            
            # --- SELECTION MODE (Index + Middle Up) ---
            if gesture == "SELECT":
                canvas.reset_prev()
                # Draw a sleek target cursor representing selection
                cv2.circle(img, (x1, y1), 8, current_color, 2, cv2.LINE_AA)
                cv2.circle(img, (x1, y1), 12, (255, 255, 255), 1, cv2.LINE_AA)
                
                # Check precise bounding box interaction with toolbar
                for name, (bx1, by1, bx2, by2), color in ui.button_rects:
                    if bx1 < x1 < bx2 and by1 < y1 < by2:
                        hovered_button = name
                        
                        if name == "CLEAR":
                            canvas.clear()
                        elif name == "SAVE" and time.time() - save_cooldown > 2:
                            timestamp = int(time.time())
                            cv2.imwrite(f"outputs/drawing_{timestamp}.png", canvas.canvas)
                            # Merge current frame with canvas just to save the screenshot
                            screenshot = canvas.merge(img.copy())
                            cv2.imwrite(f"screenshots/screenshot_{timestamp}.png", screenshot)
                            cv2.putText(img, "SAVED!", (500, 300), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5, cv2.LINE_AA)
                            save_cooldown = time.time()
                        elif name == "ERASER":
                            current_color = ui.colors["ERASER"]
                            current_color_name = "ERASER"
                        elif name not in ["CLEAR", "SAVE"]:
                            current_color = color
                            current_color_name = name
                                
            # --- DRAWING MODE (Only Index Up) ---
            elif gesture == "DRAW":
                # Elegant preview cursor when drawing
                cv2.circle(img, (x1, y1), max(4, brush_thickness//2), current_color, cv2.FILLED, cv2.LINE_AA)
                cv2.circle(img, (x1, y1), max(6, brush_thickness//2 + 2), (255, 255, 255), 1, cv2.LINE_AA)
                
                if current_color_name == "ERASER":
                    canvas.draw(x1, y1, current_color, eraser_thickness)
                else:
                    canvas.draw(x1, y1, current_color, brush_thickness)
                    
            # --- CLEAR MODE (All Fingers Up) ---
            elif gesture == "CLEAR":
                canvas.clear()
                canvas.reset_prev()
                
            # --- PAUSE OR SAVE (Fist or Thumb) ---
            elif gesture in ["PAUSE", "SAVE"]:
                canvas.reset_prev()
                filter_2d.reset()
                if gesture == "SAVE" and time.time() - save_cooldown > 2:
                    timestamp = int(time.time())
                    cv2.imwrite(f"outputs/drawing_{timestamp}.png", canvas.canvas)
                    # Merge current frame with canvas just to save the screenshot
                    screenshot = canvas.merge(img.copy())
                    cv2.imwrite(f"screenshots/screenshot_{timestamp}.png", screenshot)
                    cv2.putText(img, "SAVED!", (500, 300), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5, cv2.LINE_AA)
                    save_cooldown = time.time()
        else:
            canvas.reset_prev() # Reset line if hand leaves frame
            filter_2d.reset() # Reset 1€ filter state
            
        # UI Rendering (passing current selection and hover state)
        img = ui.draw_toolbar(img, current_color_name, hovered_button)
        
        # Calculate FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime) if cTime - pTime > 0 else 0
        pTime = cTime
        
        # Merge the drawing canvas over the webcam frame
        img = canvas.merge(img)
        
        # Overlay Status
        img = ui.draw_status(img, gesture, current_color_name, brush_thickness, fps)
        
        # Display
        cv2.imshow("Virtual Drawing Board (AI Powered)", img)
        
        # Keyboard Event Handling
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27: # 'q' or ESC
            break
        elif key == ord('+') or key == ord('='):
            brush_thickness = min(50, brush_thickness + 2)
        elif key == ord('-'):
            brush_thickness = max(2, brush_thickness - 2)
        elif key == ord('c'):
            canvas.clear()
        elif key == ord('s'):
            timestamp = int(time.time())
            cv2.imwrite(f"outputs/drawing_{timestamp}.png", canvas.canvas)
            cv2.imwrite(f"screenshots/screenshot_{timestamp}.png", img)
            print(f"Screenshot saved to screenshots/screenshot_{timestamp}.png")
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
