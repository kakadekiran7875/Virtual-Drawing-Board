# 🎨 AI-Powered Futuristic Virtual Drawing Board

![Virtual Drawing Board](https://img.shields.io/badge/Python-3.10%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer_Vision-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand_Tracking-orange)
![License](https://img.shields.io/badge/License-MIT-purple)

A futuristic, touchless human-computer interaction (HCI) drawing application that uses artificial intelligence and real-time computer vision to let you paint in the air using hand gestures! Fully optimized for ultra-smooth performance with threaded video capture, time-based Coordinate Smoothing, stack-based history controls, glassmorphic UI, and AI-powered shape snapping.

---

## 🚀 Key Features

*   **⚡ Zero-Lag Threaded Capturing**: Utilizes an asynchronous multi-threaded webcam pipeline (`ThreadedCamera`) to entirely decouple frame I/O bottlenecks, securing a locked **30+ FPS** rendering pipeline.
*   **🖐️ Advanced 7-Gesture Control System**: Sleek majority-voting temporal debouncing and customizable action cooldown states prevent false activations.
*   **🖌️ Core-Glow Neon Brush**: Re-engineered visual rendering pipeline utilizing multi-pass concentric anti-aliased drawing overlays to generate a highly detailed electric neon glow.
*   **📐 AI Shape Snapping Engine**: Integrates smart Douglas-Peucker contour approximation to automatically smooth and "snap" messy hand-drawn sketches into perfect circles, rectangles, and straight lines instantly when you lift your hand.
*   **🤏 Pinch-to-Resize Secondary Control**: Two-hand support lets you draw with your dominant hand while pinching your secondary hand's index and thumb to dynamically slide the brush size gauge!
*   **💎 Real Glassmorphism HUD**: Premium floating dashboards featuring localized Gaussian blur cards, animated cursor particle trails, pulsating selector rings, and beautiful toast notifications for actions.
*   **↩️ Double-Stack Undo/Redo Engine**: Local memory-bounded state management stacks allow you to travel back and forward in drawing history up to 20 states instantly.
*   **💾 Transparent Export**: Saves drawings as standard BGR images as well as 4-channel transparent background PNGs (`RGBA`) inside the `outputs/` folder.

---

## 🏗️ Architecture Explanation

The codebase is built using a clean, professional, modular Object-Oriented Architecture:

*   **`main.py`**: The core driver orchestrating the background camera threads, running the multi-hand coordinate smoothers, and executing core event loops.
*   **`hand_tracking.py`**: A highly optimized wrapper around Google's modern MediaPipe Hand Landmarker Tasks API. Scales landmarks dynamically on a resized frame, mapping coordinates back to high-res.
*   **`gesture_controller.py`**: The decision engine analyzing finger arrays into specific commands with majority-voting buffers and action cooldown trackers.
*   **`drawing_utils.py`**: Manages the virtual canvas. Implements time-based One-Euro coordinate filtering, transparent alpha-channel builders, and triggers undo/redo stack pops.
*   **`ui_components.py`**: Renders the top selection toolbar, side gesture visual guide, floating HUD metrics, targeting crosshairs, and animated action toasts.
*   **`history_manager.py`**: Manages deep copy numpy array stacks with bounded memory capping.
*   **`effects.py`**: Houses the multi-pass neon brush formulas, Douglas-Peucker shape fit solvers, and cursor particle trails.
*   **`performance_utils.py`**: Controls background threading for camera stream grabbing and averages FPS / processing latencies in milliseconds.

```
┌────────────────────────────────────────────────────────┐
│                        main.py                         │
└───────────────────────────┬────────────────────────────┘
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │                  ThreadedCamera                      │ ◄─── (Asynchronous webcam grab)
 └──────────────────────────┬───────────────────────────┘
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │                MultiHandTracker                      │ ◄─── (Resizes internally for FPS)
 └──────────────────────────┬───────────────────────────┘
                            ▼
 ┌───────────────┬──────────┴────────────┬──────────────┐
 │               │                       │              │
 ▼               ▼                       ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│GestureEngine│ │DrawingCanvas│ │FuturisticUI │ │VisualEffects│
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
                     │                       ▲
                     ▼                       │
                ┌─────────────┐              │
                │HistoryStack │ ─────────────┘  (Toasts triggers)
                └─────────────┘
```

---

## 🖐️ Gesture Reference Guide

*   **DRAW Mode**: ☝️ **Dominant Index Finger Up Only** — Draw with active neon color.
*   **SELECT Mode**: ✌️ **Dominant Index + Middle Up** — Hover over and select tools on the floating toolbar.
*   **CLEAR Canvas**: 🖐️ **Dominant All 5 Fingers Up (Open Palm)** — Wipes the entire canvas (support undo!).
*   **PAUSE Mode**: ✊ **Dominant Closed Fist** — Suspends brush writing to move hand freely.
*   **SAVE Image**: 👍 **Dominant Thumb Up Only** — Instantly saves canvas drawing as a transparent PNG and standard screenshot.
*   **UNDO Action**: 🤟 **Dominant Three Fingers Up (Index, Middle, Ring)** — Reverts the canvas to the last state.
*   **REDO Action**: 🖖 **Dominant Four Fingers Up** — Re-applies the last undone stroke.
*   **PINCH Size**: 🤏 **Control Hand (Thumb + Index pinch)** — Dynamic pinch distance resizes the active brush in real-time.

---

## 🚀 Setup & Execution

1. **Clone and Navigate**:
   ```bash
   git clone https://github.com/kakadekiran7875/Virtual-Drawing-Board.git
   cd VirtualDrawingBoard
   ```

2. **Setup Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Requires standard `opencv-python`, `mediapipe`, and `numpy`).*

4. **Launch Application**:
   ```bash
   python main.py
   ```

---

## 💼 Resume Description

**AI-Powered Futuristic Gesture-Controlled Virtual Drawing Board**
*   **Architected** an ultra-low latency Touchless Air-Drawing application using Python, OpenCV, and MediaPipe, sustaining locked **30+ FPS** by implementing an asynchronous multi-threaded webcam pipeline.
*   **Engineered** an advanced Human-Computer Interaction (HCI) interface parsing **7 distinct gestural states** with slide-window majority-voting filters, dynamic action cooldown debouncers, and real-time second-hand pinch-to-resize scales.
*   **Developed** a smart **AI Shape Snapping Engine** leveraging Douglas-Peucker contour approximation to snap hand-drawn sketches into perfect circles, rectangles, and lines, and created a bounded double-stack state history manager for undos/redos.
*   **Designed** a premium glassmorphism HUD featuring localized Gaussian blur cards, animated cursor particle trails, pulsating selector rings, and beautiful toast notifications.

---

## 🚀 LinkedIn Showcase

🚀 I'm thrilled to share my latest Computer Vision and Human-Computer Interaction (HCI) project: **An AI-Powered Futuristic Virtual Drawing Board**! 🎨✨

I wanted to push the boundaries of touchless user interfaces and real-time image processing. By leveraging **Python**, **OpenCV**, and **Google MediaPipe**, I built an air-drawing application that feels straight out of a sci-fi movie! 🛸

**Key Innovations:**
⚡ **Zero-Lag Threaded Capturing**: Decoupled OpenCV camera input using asynchronous background threads to lock processing at a smooth 30+ FPS.
📐 **AI Shape Snapping**: Implemented a geometry-analysis algorithm using contour approximation to automatically snap messy hand-drawn circles, lines, and boxes into flawless digital shapes.
↩️ **Double-Stack History Manager**: A custom, memory-bounded stack-popping system allowing real-time Undo and Redo controls.
🤏 **Pinch-to-Resize Secondary Control**: Supports dual hands simultaneously! One hand draws, while pinching the other dynamically slides the glowing brush width gauge.
💎 **Frosted Glass UI**: Floating glassmorphism menus rendered dynamically with real-time ROI Gaussian blurring, particle cursor trails, and toast notification alerts.

This was an incredible deep dive into real-time computer vision optimization, thread safety in Python, and user experience design. 

Check out the full modular repository on my GitHub! 👇
[https://github.com/kakadekiran7875/Virtual-Drawing-Board](https://github.com/kakadekiran7875/Virtual-Drawing-Board)

Let me know what you think in the comments! 🚀

#Python #OpenCV #ComputerVision #MediaPipe #MachineLearning #ArtificialIntelligence #HCI #Developer #GitHub #SoftwareEngineering
