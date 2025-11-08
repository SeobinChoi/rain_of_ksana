#!/usr/bin/env python3
"""
Multi-Screen Display Module
Manages multiple text display screens (up to 3) with independent caption queues.
"""

import cv2
import numpy as np
from typing import List, Optional, Tuple
from dual_screen_display import DualScreenDisplay, TypingAnimation


class TextScreen:
    """Single text display screen with independent caption management"""

    def __init__(self, screen_index: int, config: dict):
        self.screen_index = screen_index
        self.config = config

        # Window settings
        self.window_width = config.get("window_width", 2560)
        self.window_height = config.get("window_height", 1440)
        self.font_size = config.get("font_size", 24)
        self.font_path = config.get("font_path", "assets/fonts/Acumin_Variable_Concept.ttf")
        self.typing_speed = config.get("typing_speed", 0.03)
        self.column_width = config.get("column_width", 10)
        self.char_spacing = config.get("char_spacing", 2)

        # Window name
        self.window_name = f"Text Screen {screen_index + 1}"

        # Caption management
        self.captions = []
        self.max_captions = 200

        # Animation
        self.typing_animator = TypingAnimation(
            typing_delay=int(self.typing_speed * 1000),
            cursor_effect="blink"
        )

        # Display components (reuse DualScreenDisplay logic)
        self._init_display()

    def _init_display(self):
        """Initialize display window"""
        # Create window
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.window_width, self.window_height)

        # Load font (simplified)
        try:
            from PIL import ImageFont
            self.font = ImageFont.truetype(self.font_path, self.font_size)
        except Exception:
            self.font = None

    def add_caption(self, caption: str):
        """Add a new caption to this screen"""
        if not caption or not caption.strip():
            return

        # Replace spaces with hyphens
        formatted_caption = caption.replace(" ", "-")

        # Add to captions list
        self.captions.append(formatted_caption)

        # Limit caption count
        if len(self.captions) > self.max_captions:
            self.captions.pop(0)

        # Start typing animation
        self.typing_animator.start_typing(formatted_caption)

    def render(self) -> np.ndarray:
        """Render the text screen"""
        # Create black background
        img = np.zeros((self.window_height, self.window_width, 3), dtype=np.uint8)

        # Update animations
        self.typing_animator.update_animations()

        # Render captions (simplified vertical text layout)
        from PIL import Image, ImageDraw

        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)

        # Draw captions vertically from right to left
        x_pos = self.window_width - 50
        for caption in reversed(self.captions[-20:]):  # Show last 20 captions
            y_pos = 50
            for char in caption:
                if self.font:
                    draw.text((x_pos, y_pos), char, font=self.font, fill=(255, 255, 255))
                    y_pos += self.font_size + self.char_spacing
                else:
                    # Fallback to cv2.putText
                    cv2.putText(img, char, (x_pos, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    y_pos += 30

                if y_pos > self.window_height - 50:
                    break

            x_pos -= self.font_size + self.column_width
            if x_pos < 50:
                break

        return np.array(pil_img)

    def display(self):
        """Display the text screen"""
        frame = self.render()
        cv2.imshow(self.window_name, frame)

    def cleanup(self):
        """Clean up resources"""
        try:
            cv2.destroyWindow(self.window_name)
        except Exception:
            pass


class MultiScreenDisplay:
    """Manages multiple text display screens"""

    def __init__(self, screen_count: int = 1, config: Optional[dict] = None):
        if not 1 <= screen_count <= 3:
            raise ValueError("Screen count must be between 1 and 3")

        self.screen_count = screen_count
        self.config = config or {}

        # Display configuration
        self.display_config = self._build_display_config()

        # Create screens
        self.screens: List[TextScreen] = []
        for i in range(screen_count):
            screen_config = self.display_config.copy()
            screen = TextScreen(i, screen_config)
            self.screens.append(screen)

        # Camera window
        self.camera_window_name = "Camera Feed"
        self._camera_window_created = False

        # Screen assignment strategy
        self.current_screen_index = 0  # Round-robin assignment

        print(f"✅ MultiScreenDisplay initialized with {screen_count} screen(s)")

    def _build_display_config(self) -> dict:
        """Build display configuration from config"""
        display_config = self.config.get("display", {})

        return {
            "window_width": display_config.get("window_width", 2560),
            "window_height": display_config.get("window_height", 1440),
            "font_size": display_config.get("font_size", 24),
            "font_path": display_config.get("font_path", "assets/fonts/Acumin_Variable_Concept.ttf"),
            "typing_speed": display_config.get("typing_speed", 0.03),
            "column_width": display_config.get("column_width", 10),
            "char_spacing": display_config.get("char_spacing", 2)
        }

    def add_caption(self, caption: str, screen_index: Optional[int] = None):
        """
        Add a caption to a specific screen or distribute automatically

        Args:
            caption: Caption text to add
            screen_index: Target screen index (None for automatic round-robin)
        """
        if screen_index is not None:
            if 0 <= screen_index < self.screen_count:
                self.screens[screen_index].add_caption(caption)
            else:
                print(f"⚠️  Invalid screen index {screen_index}")
        else:
            # Round-robin distribution
            self.screens[self.current_screen_index].add_caption(caption)
            self.current_screen_index = (self.current_screen_index + 1) % self.screen_count

    def add_summary(self, summary: str):
        """Add a summary to all screens (for dual-interval mode)"""
        for screen in self.screens:
            screen.add_caption(summary)

    def display_camera_frame(self, frame: np.ndarray, current_caption: str = ""):
        """Display camera feed"""
        if not self._camera_window_created:
            cv2.namedWindow(self.camera_window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.camera_window_name, 1280, 720)
            self._camera_window_created = True

        # Resize frame if needed
        display_frame = cv2.resize(frame, (1280, 720))

        # Add current caption overlay
        if current_caption:
            cv2.putText(display_frame, current_caption, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow(self.camera_window_name, display_frame)

    def update_all_screens(self):
        """Update and display all text screens"""
        for screen in self.screens:
            screen.display()

    def update_typing_animations(self):
        """Update typing animations for all screens"""
        for screen in self.screens:
            screen.typing_animator.update_animations()

    def check_for_quit(self) -> bool:
        """Check if user pressed 'q' to quit"""
        key = cv2.waitKey(1) & 0xFF
        return key == ord('q')

    def cleanup(self):
        """Clean up all windows and resources"""
        print("🧹 Cleaning up multi-screen display...")

        # Clean up camera window
        if self._camera_window_created:
            try:
                cv2.destroyWindow(self.camera_window_name)
            except Exception:
                pass

        # Clean up all text screens
        for screen in self.screens:
            screen.cleanup()

        cv2.destroyAllWindows()
        print("✅ Cleanup complete")

    def get_stats(self) -> dict:
        """Get statistics for all screens"""
        return {
            "screen_count": self.screen_count,
            "screens": [
                {
                    "index": i,
                    "caption_count": len(screen.captions)
                }
                for i, screen in enumerate(self.screens)
            ]
        }

    def __str__(self):
        """String representation"""
        stats = self.get_stats()
        screen_info = ", ".join([
            f"Screen{s['index']+1}={s['caption_count']}"
            for s in stats['screens']
        ])
        return f"MultiScreenDisplay({screen_info})"


if __name__ == "__main__":
    # Test multi-screen display
    print("Testing MultiScreenDisplay...")

    # Create 3-screen display
    display = MultiScreenDisplay(screen_count=3)

    # Test captions
    test_captions = [
        "a person sitting at desk",
        "typing on laptop",
        "drinking coffee",
        "looking at screen",
        "smiling",
        "working on code",
        "debugging",
        "testing features"
    ]

    try:
        for i, caption in enumerate(test_captions):
            print(f"Adding caption {i+1}: {caption}")
            display.add_caption(caption)  # Will distribute round-robin

            # Update display
            display.update_all_screens()
            display.update_typing_animations()

            # Check for quit
            if display.check_for_quit():
                break

            import time
            time.sleep(1)

        print(f"\nStats: {display.get_stats()}")
        print("Press 'q' to quit...")

        # Keep display running
        while True:
            display.update_all_screens()
            display.update_typing_animations()
            if display.check_for_quit():
                break

    finally:
        display.cleanup()
