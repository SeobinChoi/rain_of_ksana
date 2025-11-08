#!/usr/bin/env python3
"""
Enhanced Caption Engine Module
Main orchestrator for BLIP camera captioning system with advanced features.
Supports multi-screen display, dual-interval mode, and Ollama integration.
"""

import time
import os
from typing import Optional, Dict, Any
from blip_model import BLIPModelManager
from blip2_model import BLIP2ModelManager
from camera_manager import CameraManager
from multi_screen_display import MultiScreenDisplay
from caption_buffer import CaptionBuffer, DualIntervalManager
from ollama_integration import OllamaIntegration, create_ollama_from_config


class CaptionEngineEnhanced:
    """Enhanced engine for BLIP camera captioning with multi-screen and Ollama support"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize engine with configuration dictionary

        Args:
            config: Configuration dictionary from ConfigManager
        """
        self.config = config

        # Extract configuration
        self.model_config = config.get("model", {})
        self.camera_config = config.get("camera", {})
        self.display_config = config.get("display", {})
        self.timing_config = config.get("timing", {})
        self.ollama_config = config.get("ollama", {})

        # Model settings
        model_type = self.model_config.get("type", "blip")
        self.model_name = self._get_model_name(model_type)

        # Camera settings
        self.camera_index = self.camera_config.get("index", 0)
        self.show_camera = self.camera_config.get("show_camera", False)
        self.backend = self.camera_config.get("backend", "auto")

        # Timing settings
        self.dual_interval_mode = self.timing_config.get("dual_interval_mode", False)
        self.interval_short = self.timing_config.get("interval_short", 3)
        self.interval_long = self.timing_config.get("interval_long", 30)

        # Display settings
        self.screen_count = self.display_config.get("text_screen_count", 1)

        # Initialize model manager
        if "blip2" in model_type.lower():
            self.model_manager = BLIP2ModelManager(self.model_name)
        else:
            self.model_manager = BLIPModelManager(self.model_name)

        # Initialize camera manager
        self.camera_manager = CameraManager(
            self.camera_index,
            self.show_camera and self.screen_count > 0,
            backend=self.backend
        )

        # Initialize multi-screen display
        self.display = MultiScreenDisplay(
            screen_count=self.screen_count,
            config=config
        )

        # Initialize caption buffer and timing (for dual-interval mode)
        self.caption_buffer = None
        self.interval_manager = None
        self.ollama = None

        if self.dual_interval_mode:
            self.caption_buffer = CaptionBuffer(
                max_size=20,
                interval_long=self.interval_long
            )
            self.interval_manager = DualIntervalManager(
                interval_short=self.interval_short,
                interval_long=self.interval_long
            )

            # Initialize Ollama if enabled
            if self.ollama_config.get("enabled", False):
                self.ollama = create_ollama_from_config(config)
                if self.ollama:
                    print("✅ Ollama integration enabled")
                else:
                    print("⚠️  Ollama not available, will accumulate captions only")

        # Statistics
        self.stats = {
            "captions_generated": 0,
            "summaries_generated": 0,
            "start_time": None
        }

        # Set environment variables for stability
        os.environ['OMP_NUM_THREADS'] = '1'
        os.environ['MKL_NUM_THREADS'] = '1'
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'

    def _get_model_name(self, model_type: str) -> str:
        """Get full model name from model type"""
        if model_type == "blip2":
            return "Salesforce/blip2-opt-2.7b"
        else:
            return "Salesforce/blip-image-captioning-base"

    def initialize(self) -> bool:
        """Initialize the caption engine"""
        print("\n" + "=" * 60)
        print("🚀 BLIP Camera Captioning System - Enhanced")
        print("=" * 60)

        # Load model
        print(f"\n🤖 Model: {self.model_name}")
        if not self.model_manager.load_model():
            return False

        # Initialize camera
        print(f"\n📷 Camera: Index {self.camera_index}, Backend: {self.backend}")
        if not self.camera_manager.initialize():
            return False

        # Display configuration
        print(f"\n🖥️  Display: {self.screen_count} text screen(s)")

        # Timing configuration
        if self.dual_interval_mode:
            print(f"\n⏱️  Dual-Interval Mode:")
            print(f"   • Short interval (captions): {self.interval_short}s")
            print(f"   • Long interval (summary): {self.interval_long}s")
            if self.ollama:
                print(f"   • Ollama model: {self.ollama.model}")
        else:
            print(f"\n⏱️  Single-Interval Mode: {self.interval_short}s")

        print("\n📺 Press 'q' in any window to quit")
        print("📝 Press Ctrl+C to stop")
        print("=" * 60 + "\n")

        self.stats["start_time"] = time.time()
        return True

    def run(self):
        """Run the main captioning loop"""
        try:
            if self.dual_interval_mode:
                self._run_dual_interval()
            else:
                self._run_single_interval()
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()

    def _run_single_interval(self):
        """Run in single-interval mode (standard)"""
        print("🎬 Starting single-interval mode...\n")

        last_caption_time = 0

        while True:
            # Capture frame
            ret, frame = self.camera_manager.read_frame()
            if not ret:
                print("❌ Failed to grab frame")
                break

            # Display camera feed
            if self.show_camera:
                current_caption = getattr(self, 'last_generated_caption', "")
                self.display.display_camera_frame(frame, current_caption)

            # Update display
            self.display.update_all_screens()
            self.display.update_typing_animations()

            # Check for quit
            if self.display.check_for_quit():
                print("\n🛑 Quit requested")
                break

            current_time = time.time()

            # Generate caption at interval
            if current_time - last_caption_time >= self.interval_short:
                timestamp = time.strftime("%H:%M:%S")
                print(f"🔄 [{timestamp}] Processing frame...")

                caption = self.model_manager.generate_caption(frame)
                print(f"📝 [{timestamp}] {caption}")

                # Store and display caption
                self.last_generated_caption = caption
                self.display.add_caption(caption)

                self.stats["captions_generated"] += 1
                last_caption_time = current_time

                # Show stats periodically
                if self.stats["captions_generated"] % 10 == 0:
                    self._print_stats()

            # Small delay
            time.sleep(0.03)

    def _run_dual_interval(self):
        """Run in dual-interval mode (with caption buffering and summarization)"""
        print("🎬 Starting dual-interval mode...\n")

        while True:
            # Capture frame
            ret, frame = self.camera_manager.read_frame()
            if not ret:
                print("❌ Failed to grab frame")
                break

            # Display camera feed
            if self.show_camera:
                current_caption = getattr(self, 'last_generated_caption', "")
                self.display.display_camera_frame(frame, current_caption)

            # Update display
            self.display.update_all_screens()
            self.display.update_typing_animations()

            # Check for quit
            if self.display.check_for_quit():
                print("\n🛑 Quit requested")
                break

            current_time = time.time()

            # Generate short caption at short interval
            if self.interval_manager.should_generate_caption(current_time):
                timestamp = time.strftime("%H:%M:%S")
                print(f"🔄 [{timestamp}] Generating short caption...")

                caption = self.model_manager.generate_caption(frame)
                print(f"📝 [{timestamp}] Short: {caption}")

                # Add to buffer
                self.caption_buffer.add_caption(caption, current_time)
                self.last_generated_caption = caption

                self.stats["captions_generated"] += 1
                self.interval_manager.mark_caption_generated(current_time)

                # Show buffer status
                time_until_summary = self.caption_buffer.get_time_until_summary(current_time)
                print(f"   Buffer: {len(self.caption_buffer)} captions, "
                      f"summary in {time_until_summary:.0f}s")

            # Generate summary at long interval
            if self.interval_manager.should_generate_summary(current_time):
                timestamp = time.strftime("%H:%M:%S")
                print(f"\n✨ [{timestamp}] Generating summary...")

                # Get accumulated captions
                captions = self.caption_buffer.get_all_captions()

                if captions:
                    if self.ollama:
                        # Summarize with Ollama
                        summary = self.ollama.summarize_captions(captions)
                        if summary:
                            print(f"📖 [{timestamp}] Summary: {summary}")
                            self.display.add_summary(summary)
                            self.stats["summaries_generated"] += 1
                        else:
                            print("⚠️  Summary generation failed, using last caption")
                            self.display.add_summary(captions[-1])
                    else:
                        # No Ollama, just use last caption
                        summary = captions[-1]
                        print(f"📖 [{timestamp}] Last caption: {summary}")
                        self.display.add_summary(summary)

                    # Clear buffer
                    self.caption_buffer.clear()
                    self.interval_manager.mark_summary_generated(current_time)

                    print()  # Blank line for readability
                    self._print_stats()

            # Small delay
            time.sleep(0.03)

    def _print_stats(self):
        """Print current statistics"""
        elapsed = time.time() - self.stats["start_time"]
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        print(f"\n📊 Stats: {self.stats['captions_generated']} captions, "
              f"{self.stats['summaries_generated']} summaries, "
              f"runtime: {minutes}m {seconds}s\n")

    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        self.display.cleanup()
        self.camera_manager.release()

        # Final stats
        print("\n" + "=" * 60)
        print("📊 Final Statistics")
        print("=" * 60)
        self._print_stats()
        print("✅ Cleanup complete")

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the engine"""
        return {
            "model_info": self.model_manager.get_model_info(),
            "camera_info": self.camera_manager.get_camera_info(),
            "display_info": self.display.get_stats(),
            "settings": {
                "dual_interval_mode": self.dual_interval_mode,
                "interval_short": self.interval_short,
                "interval_long": self.interval_long,
                "screen_count": self.screen_count,
                "ollama_enabled": self.ollama is not None
            },
            "stats": self.stats
        }


# Backward compatibility: alias to original CaptionEngine
CaptionEngine = CaptionEngineEnhanced


if __name__ == "__main__":
    # Test with default config
    from config_manager import ConfigManager

    print("Testing Enhanced Caption Engine...")
    config_manager = ConfigManager()
    config = config_manager.interactive_setup()

    engine = CaptionEngineEnhanced(config)

    if engine.initialize():
        engine.run()
