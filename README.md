# 🎨 AI-Powered Virtual Drawing Board

![Virtual Drawing Board](https://img.shields.io/badge/Python-3.10%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand_Tracking-orange)

A futuristic touchless drawing application that uses Artificial Intelligence and Computer Vision to let you draw in the air using hand gestures!

## 📌 Project Explanation
The **Virtual Drawing Board** is a Computer Vision-based human-computer interaction project. It utilizes **MediaPipe Hands** to detect 21 hand landmarks in real-time through a standard webcam. By analyzing the states of fingers (open vs. closed), it identifies specific gestures and maps them to drawing actions. **OpenCV** is used to render the drawing canvas, the modern UI, and the camera feed together, creating a seamless Augmented Reality (AR) drawing experience. 

## 🏗️ Architecture Explanation
The project is built using a modular Object-Oriented approach for clean code and scalability:
- **`main.py`**: The core driver that initializes the camera, instantiates modules, and contains the main while-loop.
- **`hand_tracking.py`**: A wrapper around `mediapipe.solutions.hands`. It extracts hand landmarks and handles the logic for detecting which fingers are up.
- **`gesture_controller.py`**: A decision engine that takes the array of "fingers up" and returns a recognized gesture command (e.g., DRAW, SELECT, CLEAR).
- **`drawing_utils.py`**: Manages the virtual canvas. It draws smooth lines using OpenCV's `cv2.line`, handles history tracking for continuity, and merges the black canvas onto the live webcam feed using bitwise operations.
- **`ui_components.py`**: Renders the modern toolbar, colors, and the status/FPS overlay using OpenCV drawing functions.

## 🚀 Setup Instructions

1. **Clone the Repository** (or download the files):
   ```bash
   git clone https://github.com/yourusername/VirtualDrawingBoard.git
   cd VirtualDrawingBoard
   ```

2. **Create a Virtual Environment** (Optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python main.py
   ```

## 🖐️ Gesture Explanation
The system recognizes specific finger combinations for seamless control:
- **DRAW Mode**: ☝️ **Index Finger Up Only** — Move your index finger to draw on the screen.
- **SELECT Mode**: ✌️ **Index + Middle Fingers Up** — Used to hover over and select items in the toolbar without drawing.
- **CLEAR Screen**: 🖐️ **All Fingers Up (Open Palm)** — Wipes the entire drawing canvas clean.
- **PAUSE Drawing**: ✊ **Closed Fist** — Lifts the virtual pen off the canvas. Move your hand without drawing.
- **SAVE Drawing**: 👍 **Thumb Up Only** — Instantly saves your current artwork as an image.

## 🔮 Future Scope
- **Multi-Hand Support**: Allowing two-handed drawing or using one hand for color selection and the other for drawing.
- **AI Shape Recognition**: Automatically converting messy drawn circles/squares into perfect geometric shapes.
- **Undo / Redo System**: Using a state stack to navigate history.
- **Customizable Gestures**: A UI to let users map their own gestures to actions.
- **Air Handwriting Recognition**: Integrating an OCR engine (like Tesseract) to read text drawn in the air.

---

## 📝 Resume Description
**AI-Powered Touchless Virtual Drawing Board**
- Developed a real-time computer vision application using **Python, OpenCV, and MediaPipe** to enable touchless air-drawing via webcam.
- Implemented robust hand-tracking algorithms to extract 21 3D landmarks and programmed a custom gesture recognition engine to interpret 5 distinct commands.
- Designed a modular, object-oriented architecture, managing real-time canvas rendering and a modern HUD interface using bitwise masking at **30+ FPS**.

## 💼 LinkedIn Project Description
🚀 Excited to share my latest Computer Vision project: **An AI-Powered Virtual Drawing Board**! 🎨

I built a touchless application that lets you draw in the air using just hand gestures. No mouse, no stylus—just your fingers! 

**Key Features:**
✨ Real-time hand tracking and 21-point landmark detection using Google's **MediaPipe**.
✨ Custom Gesture Recognition (e.g., Index finger to draw, Peace sign to select colors, Open palm to clear).
✨ Glassmorphic UI toolbar and canvas rendering using **OpenCV**.
✨ Highly optimized modular code in **Python**, running at a smooth 30+ FPS.

This project was a fantastic deep-dive into Human-Computer Interaction (HCI) and real-time image processing. Check out the source code on my GitHub! Let me know what you think in the comments! 👇

#Python #OpenCV #ComputerVision #MediaPipe #ArtificialIntelligence #MachineLearning #Developer #HCI
