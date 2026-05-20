import cv2
import threading
import time

class ThreadedCamera:
    """
    Grabs frames from the camera asynchronously in a background thread to 
    eliminate blocking I/O overhead from cap.read() and ensure 30+ FPS.
    """
    def __init__(self, src=0, width=1280, height=720):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Verify video stream initialized
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()
        
    def start(self):
        if self.started:
            return self
        self.started = True
        self.thread = threading.Thread(target=self.update, args=(), daemon=True)
        self.thread.start()
        return self

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            if grabbed:
                with self.read_lock:
                    self.grabbed = grabbed
                    self.frame = frame
            time.sleep(0.01) # Small rest to prevent maxing CPU cores

    def read(self):
        with self.read_lock:
            # Copy to avoid race conditions when writing/reading numpy arrays
            frame_copy = self.frame.copy() if self.frame is not None else None
            return self.grabbed, frame_copy

    def stop(self):
        self.started = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1.0)
        self.cap.release()


class PerformanceMonitor:
    """
    Measures frame processing latency and averages FPS smoothly to provide
    real-time optimization metrics.
    """
    def __init__(self, alpha=0.9):
        self.alpha = alpha # Smoothing factor for running averages
        self.avg_fps = 0.0
        self.prev_time = time.time()
        self.proc_times = [] # Processing times of recent frames

    def start_frame(self):
        self.frame_start = time.time()

    def end_frame(self):
        now = time.time()
        # Compute dynamic FPS
        dt = now - self.prev_time
        self.prev_time = now
        fps = 1.0 / dt if dt > 0 else 0.0
        self.avg_fps = (self.alpha * self.avg_fps) + ((1 - self.alpha) * fps)
        
        # Latency of the current frame in ms
        latency = (now - self.frame_start) * 1000.0
        self.proc_times.append(latency)
        if len(self.proc_times) > 30:
            self.proc_times.pop(0)

    def get_fps(self):
        return int(self.avg_fps)

    def get_latency(self):
        """
        Returns average frame processing latency in ms over the last 30 frames.
        """
        if not self.proc_times:
            return 0.0
        return sum(self.proc_times) / len(self.proc_times)
