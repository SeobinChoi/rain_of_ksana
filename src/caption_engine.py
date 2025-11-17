#!/usr/bin/env python3
"""
Caption Engine Module
Main orchestrator for BLIP camera captioning system.
"""

import time
import os
from typing import Optional
from .blip_model import BLIPModelManager
from .blip2_model import BLIP2ModelManager
from .camera_manager import CameraManager
from .dual_screen_display import DualScreenDisplay

class CaptionEngine:
    """Main engine for BLIP camera captioning"""
    
    def __init__(self, model_name="Salesforce/blip-image-captioning-base", 
                 camera_index=0, show_camera=False, interval=5, dual_screen=False, backend: str = "auto"):
        self.model_name = model_name
        self.camera_index = camera_index
        self.show_camera = show_camera
        self.interval = interval
        self.dual_screen = dual_screen
        self.backend = backend
        
        # Initialize managers - choose BLIP or BLIP-2 based on model name
        if "blip2" in model_name.lower():
            self.model_manager = BLIP2ModelManager(model_name)
        else:
            self.model_manager = BLIPModelManager(model_name)
        self.camera_manager = CameraManager(camera_index, show_camera and not dual_screen, backend=self.backend)
        
        # Initialize dual screen display if requested
        if dual_screen:
            self.display = DualScreenDisplay()
        else:
            self.display = None
        
        # Set environment variables for stability
        os.environ['OMP_NUM_THREADS'] = '1'
        os.environ['MKL_NUM_THREADS'] = '1'
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    
    def initialize(self) -> bool:
        """Initialize the caption engine"""
        print(f"🤖 Using BLIP model: {self.model_name}")
        
        # Load model (BLIP or BLIP-2)
        if not self.model_manager.load_model():
            return False
        
        # Initialize camera
        if not self.camera_manager.initialize():
            return False
        
        print(f"\n🎯 Starting caption generation every {self.interval} seconds...")
        if self.dual_screen:
            print("🖥️  Dual screen display enabled (camera + text windows)")
            print("📺 Press 'q' in either window to quit")
        elif self.show_camera:
            print("📺 Camera window will be displayed (press 'q' to quit)")
        print("📝 Press Ctrl+C to stop\n")
        
        return True
    
    def run(self):
        """Run the main captioning loop"""
        last_caption_time = 0
        
        try:
            while True:
                # Capture frame
                ret, frame = self.camera_manager.read_frame()
                if not ret:
                    print("❌ Failed to grab frame")
                    break
                
                # Display frame
                if self.dual_screen:
                    # Use dual screen display
                    current_caption = ""
                    if hasattr(self, 'last_generated_caption'):
                        current_caption = self.last_generated_caption
                    self.display.display_camera_frame(frame, current_caption)
                    
                    # Update typing animations
                    self.display.update_typing_animations()
                    
                    # Check for quit request
                    if self.display.check_for_quit():
                        print("\n🛑 Quit requested via display window")
                        break
                else:
                    # Use single camera window
                    self.camera_manager.display_frame(frame)
                    
                    # Check for quit request
                    if self.camera_manager.check_for_quit():
                        print("\n🛑 Quit requested via camera window")
                        break
                
                current_time = time.time()
                
                # Generate caption every specified interval
                if current_time - last_caption_time >= self.interval:
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"🔄 [{timestamp}] Processing frame...")
                    
                    caption = self.model_manager.generate_caption(frame)
                    print(f"📝 [{timestamp}] {caption}\n")
                    
                    # Store caption for display
                    self.last_generated_caption = caption
                    
                    # Update display with caption
                    if self.dual_screen:
                        self.display.add_caption(caption)
                    else:
                        self.camera_manager.display_frame(frame, caption)
                    
                    last_caption_time = current_time
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.03)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.dual_screen:
            self.display.cleanup()
        else:
            self.camera_manager.release()
    
    def get_status(self):
        """Get current status of the engine"""
        return {
            "model_info": self.model_manager.get_model_info(),
            "camera_info": self.camera_manager.get_camera_info(),
            "settings": {
                "interval": self.interval,
                "show_camera": self.show_camera,
                "dual_screen": self.dual_screen
            }
        }
