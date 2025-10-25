#!/usr/bin/env python3
"""
Camera Management Module
Handles camera initialization, frame capture, and display.
"""

import cv2
import time
import platform
from typing import Optional, Tuple, List, Dict

class CameraManager:
    """Manages camera operations and display"""
    
    # Map friendly backend names to OpenCV API constants
    BACKEND_MAP = {
        "auto": cv2.CAP_ANY,
        "any": cv2.CAP_ANY,
        # Windows
        "dshow": getattr(cv2, "CAP_DSHOW", cv2.CAP_ANY),
        "msmf": getattr(cv2, "CAP_MSMF", cv2.CAP_ANY),
        # macOS
        "avfoundation": getattr(cv2, "CAP_AVFOUNDATION", cv2.CAP_ANY),
        # Linux
        "v4l2": getattr(cv2, "CAP_V4L2", cv2.CAP_ANY),
    }

    def __init__(self, camera_index=0, show_window=False, backend: str = "auto"):
        self.camera_index = camera_index
        self.show_window = show_window
        self.cap = None
        self.current_caption = ""
        self.backend_preference = backend.lower() if isinstance(backend, str) else "auto"
        self._opened_backend: Optional[int] = None
        self._opened_backend_name: Optional[str] = None
        
    def initialize(self):
        """Initialize camera capture"""
        print(f"📷 Initializing camera (index {self.camera_index})...")

        # Try opening with preferred backends
        backends_to_try = self._select_backend_order(self.backend_preference)

        self.cap = None
        for backend_name in backends_to_try:
            api = self.BACKEND_MAP.get(backend_name, cv2.CAP_ANY)
            if api == cv2.CAP_ANY:
                cap = cv2.VideoCapture(self.camera_index)
            else:
                cap = cv2.VideoCapture(self.camera_index, api)
            if cap.isOpened():
                self.cap = cap
                self._opened_backend = api
                self._opened_backend_name = backend_name
                break

        if not self.cap or not self.cap.isOpened():
            print("❌ Cannot open camera. Please check:")
            print("   - Camera is not being used by another application")
            print("   - Camera permissions are granted")
            print("   - Camera index is correct (try 0, 1, or 2)")
            print("   - Try a different backend with --backend (dshow/msmf/any)")
            return False
        
        # Set camera properties for better quality
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        backend_info = self._opened_backend_name or "auto"
        print(f"✅ Camera initialized successfully! (backend: {backend_info})")
        return True
    
    def read_frame(self) -> Tuple[bool, Optional[cv2.Mat]]:
        """Read a frame from the camera"""
        if not self.cap:
            return False, None
        
        ret, frame = self.cap.read()
        return ret, frame
    
    def display_frame(self, frame, caption: str = ""):
        """Display frame with optional caption overlay"""
        if not self.show_window:
            return
        
        # Create display frame with caption
        display_frame = frame.copy()
        
        if caption:
            self.current_caption = caption
            # Add caption text to the frame
            cv2.putText(
                display_frame, 
                caption, 
                (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, 
                (0, 255, 0), 
                2
            )
        
        cv2.imshow('BLIP Camera Captioning', display_frame)
    
    def check_for_quit(self) -> bool:
        """Check if user wants to quit (pressed 'q')"""
        if not self.show_window:
            return False
        
        key = cv2.waitKey(1) & 0xFF
        return key == ord('q')
    
    def release(self):
        """Release camera and close windows"""
        if self.cap:
            self.cap.release()
        
        if self.show_window:
            cv2.destroyAllWindows()
        
        print("📷 Camera released")
    
    def get_camera_info(self):
        """Get camera information"""
        if not self.cap:
            return {"status": "not_initialized"}
        
        return {
            "camera_index": self.camera_index,
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": int(self.cap.get(cv2.CAP_PROP_FPS)),
            "show_window": self.show_window,
            "backend": self._opened_backend_name or self.backend_preference
        }

    @classmethod
    def _select_backend_order(cls, preferred: str) -> List[str]:
        """Select sensible backend order based on OS and user preference"""
        preferred = preferred.lower() if preferred else "auto"
        system = platform.system().lower()

        # OS defaults
        if system == "windows":
            default_order = ["dshow", "msmf", "any"]
        elif system == "darwin":
            default_order = ["avfoundation", "any"]
        else:
            default_order = ["v4l2", "any"]

        if preferred in ("auto", "any"):
            return default_order

        # If a specific backend is requested, try it first then fall back
        if preferred in cls.BACKEND_MAP:
            order = [preferred]
            for b in default_order:
                if b not in order:
                    order.append(b)
            return order

        return default_order

    @classmethod
    def list_cameras(cls, max_index: int = 10, backend: str = "auto") -> List[Dict[str, object]]:
        """Probe camera indices and return a list of available devices with basic info"""
        results: List[Dict[str, object]] = []
        backends = cls._select_backend_order(backend)

        for index in range(max_index + 1):
            opened = False
            opened_backend_name: Optional[str] = None
            width = height = fps = None

            for backend_name in backends:
                api = cls.BACKEND_MAP.get(backend_name, cv2.CAP_ANY)
                cap = cv2.VideoCapture(index) if api == cv2.CAP_ANY else cv2.VideoCapture(index, api)
                if cap.isOpened():
                    opened = True
                    opened_backend_name = backend_name
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = int(cap.get(cv2.CAP_PROP_FPS))
                    cap.release()
                    break
                cap.release()

            results.append({
                "index": index,
                "available": opened,
                "backend": opened_backend_name or None,
                "width": width,
                "height": height,
                "fps": fps,
            })

        return results

    @classmethod
    def auto_select_camera(cls, max_index: int = 10, backend: str = "auto") -> Optional[int]:
        """Return the first available camera index or None if not found"""
        for info in cls.list_cameras(max_index=max_index, backend=backend):
            if info.get("available"):
                return int(info.get("index"))
        return None
