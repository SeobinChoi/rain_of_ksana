#!/usr/bin/env python3
"""
Multi-Screen Display Module - Fixed Version
Implements cascading overflow across screens (Screen 1 → 2 → 3)
with proper typing animation and column wrapping.
"""

import cv2
import numpy as np
import time
from typing import List, Optional, Tuple, Dict
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


class CascadingMultiScreenDisplay:
    """
    Manages 1-3 text screens as ONE continuous display.
    When Screen 1 is full, overflow goes to Screen 2.
    When Screen 2 is full, overflow goes to Screen 3.
    All screens work together as a single continuous canvas.
    """

    def __init__(self, screen_count: int = 1, config: Optional[dict] = None):
        if not 1 <= screen_count <= 7:
            raise ValueError("Screen count must be between 1 and 7")

        self.screen_count = screen_count
        self.config = config or {}

        # Display configuration
        display_config = self.config.get("display", {})
        self.window_width = display_config.get("window_width", 2560)
        self.window_height = display_config.get("window_height", 1440)
        self.font_size = display_config.get("font_size", 24)
        self.font_path = display_config.get("font_path", "assets/fonts/Acumin_Variable_Concept.ttf")
        self.typing_speed = display_config.get("typing_speed", 0.03)
        self.column_width = display_config.get("column_width", 10)
        self.char_spacing = display_config.get("char_spacing", 2)

        # Load font
        self.font = self._load_font()

        # Calculate layout
        self.chars_per_column = self._calculate_chars_per_column()
        self.columns_per_screen = self._calculate_columns_per_screen()

        # All captions stored in order (oldest to newest)
        self.all_captions = []

        # Typing animation state for each caption
        # {caption_index: {"full_text": str, "revealed_chars": int, "last_update": float}}
        self.typing_states = {}

        # Create windows
        self.windows = []
        for i in range(screen_count):
            window_name = f"Screen {i + 1}"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, self.window_width, self.window_height)
            self.windows.append(window_name)

        # Camera window
        self.camera_window_name = "Camera Feed"
        self._camera_window_created = False

        print(f"✅ CascadingMultiScreenDisplay initialized:")
        print(f"   Screens: {screen_count}")
        print(f"   Chars per column: {self.chars_per_column}")
        print(f"   Columns per screen: {self.columns_per_screen}")
        print(f"   Total capacity: {self.chars_per_column * self.columns_per_screen * screen_count} chars")

    def _load_font(self):
        """Load custom font or fall back to default"""
        try:
            font_path = Path(self.font_path)
            if font_path.exists():
                return ImageFont.truetype(str(font_path), self.font_size)
        except Exception as e:
            print(f"⚠️  Could not load font {self.font_path}: {e}")

        # Fallback to default
        try:
            return ImageFont.load_default()
        except:
            return None

    def _calculate_chars_per_column(self) -> int:
        """Calculate how many characters fit in one vertical column"""
        available_height = self.window_height - 100  # Leave margins
        char_height = self.font_size + self.char_spacing
        return max(1, available_height // char_height)

    def _calculate_columns_per_screen(self) -> int:
        """Calculate how many columns fit in one screen"""
        available_width = self.window_width - 100  # Leave margins
        column_width = self.font_size + self.column_width
        return max(1, available_width // column_width)

    def add_caption(self, caption: str):
        """Add a new caption to the continuous display"""
        if not caption or not caption.strip():
            return

        # Replace spaces with hyphens for vertical display
        formatted_caption = caption.replace(" ", "-")

        # Add to caption list
        self.all_captions.append(formatted_caption)

        # Initialize typing animation for this caption
        caption_index = len(self.all_captions) - 1
        self.typing_states[caption_index] = {
            "full_text": formatted_caption,
            "revealed_chars": 0,
            "last_update": time.time()
        }

        print(f"📝 Added caption {caption_index + 1}: {formatted_caption[:30]}...")

    def add_summary(self, summary: str):
        """Add a summary (just adds as a caption)"""
        self.add_caption(summary)

    def update_typing_animations(self):
        """Update typing animation for all active captions"""
        current_time = time.time()

        for caption_idx, state in list(self.typing_states.items()):
            if caption_idx >= len(self.all_captions):
                continue

            full_text = state["full_text"]
            revealed_chars = state["revealed_chars"]

            # Check if this caption is finished
            if revealed_chars >= len(full_text):
                continue

            # Check if enough time has passed to reveal next character
            time_since_update = current_time - state["last_update"]
            if time_since_update >= self.typing_speed:
                # Reveal next character
                state["revealed_chars"] += 1
                state["last_update"] = current_time

    def _get_displayed_captions(self) -> List[Tuple[int, str]]:
        """
        Get list of (caption_index, displayed_text) for captions to show.
        Takes into account typing animation.
        """
        displayed = []

        for idx, caption in enumerate(self.all_captions):
            if idx in self.typing_states:
                state = self.typing_states[idx]
                revealed_chars = state["revealed_chars"]
                displayed_text = caption[:revealed_chars]

                # Add blinking cursor if still typing
                if revealed_chars < len(caption):
                    # Blink cursor effect
                    if int(time.time() * 2) % 2 == 0:
                        displayed_text += "█"
            else:
                # Fully displayed
                displayed_text = caption

            if displayed_text:  # Only add if there's something to show
                displayed.append((idx, displayed_text))

        return displayed

    def _render_screen(self, screen_index: int) -> np.ndarray:
        """Render a single screen with its portion of the continuous display"""
        # Create black background
        img = Image.new('RGB', (self.window_width, self.window_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Get all captions to display
        displayed_captions = self._get_displayed_captions()

        # Calculate total character count and which ones belong to this screen
        total_capacity_per_screen = self.chars_per_column * self.columns_per_screen
        screen_start_capacity = screen_index * total_capacity_per_screen
        screen_end_capacity = (screen_index + 1) * total_capacity_per_screen

        # Count characters from all captions
        char_positions = []  # [(caption_idx, char_idx, char, global_pos)]
        global_char_pos = 0

        for caption_idx, caption_text in displayed_captions:
            for char_idx, char in enumerate(caption_text):
                char_positions.append((caption_idx, char_idx, char, global_char_pos))
                global_char_pos += 1

        # Determine which characters belong to this screen
        screen_chars = [
            cp for cp in char_positions
            if screen_start_capacity <= cp[3] < screen_end_capacity
        ]

        # Draw characters on this screen
        # Start from RIGHT side of screen, going left
        x_pos = self.window_width - 50
        current_column_chars = 0
        y_pos = 50

        for caption_idx, char_idx, char, global_pos in screen_chars:
            # Calculate position within this screen
            screen_relative_pos = global_pos - screen_start_capacity
            column_in_screen = screen_relative_pos // self.chars_per_column
            row_in_column = screen_relative_pos % self.chars_per_column

            # Calculate actual x, y position
            x = self.window_width - 50 - (column_in_screen * (self.font_size + self.column_width))
            y = 50 + (row_in_column * (self.font_size + self.char_spacing))

            # Draw character
            if self.font:
                draw.text((x, y), char, font=self.font, fill=(255, 255, 255))

        return np.array(img)

    def update_all_screens(self):
        """Update and display all screens"""
        for screen_idx, window_name in enumerate(self.windows):
            frame = self._render_screen(screen_idx)
            cv2.imshow(window_name, frame)

    def display_camera_frame(self, frame: np.ndarray, current_caption: str = ""):
        """Display camera feed"""
        if not self._camera_window_created:
            cv2.namedWindow(self.camera_window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.camera_window_name, 1280, 720)
            self._camera_window_created = True

        # Resize frame
        display_frame = cv2.resize(frame, (1280, 720))

        # Add caption overlay
        if current_caption:
            cv2.putText(display_frame, current_caption[:50], (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow(self.camera_window_name, display_frame)

    def check_for_quit(self) -> bool:
        """Check if user pressed 'q' to quit"""
        key = cv2.waitKey(1) & 0xFF
        return key == ord('q')

    def cleanup(self):
        """Clean up all windows"""
        print("🧹 Cleaning up displays...")

        for window_name in self.windows:
            try:
                cv2.destroyWindow(window_name)
            except:
                pass

        if self._camera_window_created:
            try:
                cv2.destroyWindow(self.camera_window_name)
            except:
                pass

        cv2.destroyAllWindows()
        print("✅ Cleanup complete")

    def get_stats(self) -> dict:
        """Get statistics"""
        total_chars = sum(len(cap) for cap in self.all_captions)
        typing_active = sum(1 for state in self.typing_states.values()
                           if state["revealed_chars"] < len(state["full_text"]))

        return {
            "screen_count": self.screen_count,
            "total_captions": len(self.all_captions),
            "total_characters": total_chars,
            "typing_active": typing_active,
            "chars_per_column": self.chars_per_column,
            "columns_per_screen": self.columns_per_screen
        }


# Alias for compatibility
MultiScreenDisplay = CascadingMultiScreenDisplay


if __name__ == "__main__":
    # Test the fixed display
    print("Testing CascadingMultiScreenDisplay...")

    config = {
        "display": {
            "text_screen_count": 3,
            "window_width": 1920,
            "window_height": 1080,
            "font_size": 48,
            "font_path": "assets/fonts/Acumin_Variable_Concept.ttf",
            "typing_speed": 0.05,
            "column_width": 10,
            "char_spacing": 2
        }
    }

    display = CascadingMultiScreenDisplay(screen_count=3, config=config)

    test_captions = [
        "a person sitting at a desk with a laptop",
        "typing on a keyboard while looking at the screen",
        "a cup of coffee sitting on the table nearby",
        "morning sunlight coming through the window",
        "working on an important project",
        "taking a short break to stretch",
        "checking notifications on the phone",
        "returning to work with renewed focus"
    ]

    try:
        for i, caption in enumerate(test_captions):
            print(f"\n➕ Adding caption {i+1}: {caption}")
            display.add_caption(caption)

            # Update display for a few seconds to show typing effect
            for _ in range(100):  # ~3 seconds at 30fps
                display.update_typing_animations()
                display.update_all_screens()

                if display.check_for_quit():
                    break

                time.sleep(0.03)

        print("\n" + "="*60)
        print("📊 Final Stats:")
        stats = display.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print("="*60)

        print("\nPress 'q' to quit...")
        while True:
            display.update_typing_animations()
            display.update_all_screens()
            if display.check_for_quit():
                break
            time.sleep(0.03)

    finally:
        display.cleanup()
