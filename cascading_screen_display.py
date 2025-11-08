#!/usr/bin/env python3
"""
Cascading Screen Display - Correct Chinese Classical Document Style
New captions appear on RIGHT, old columns shift LEFT across screens.
"""

import cv2
import numpy as np
import time
from typing import List, Optional, Dict
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


class CascadingScreenDisplay:
    """
    Chinese classical document style display:
    - New captions appear on the RIGHTMOST column of Screen 1
    - As new captions are added, old columns shift LEFT
    - When Screen 1 is full, leftmost column moves to rightmost of Screen 2
    - When Screen 2 is full, leftmost column moves to rightmost of Screen 3
    - Columns flow: Screen 1 (right→left) → Screen 2 (right→left) → Screen 3 (right→left)
    """

    def __init__(self, screen_count: int = 1, config: Optional[dict] = None):
        if not 1 <= screen_count <= 3:
            raise ValueError("Screen count must be between 1 and 3")

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

        # NEW: Truncate long captions or wrap to multiple columns
        self.truncate_long_captions = display_config.get("truncate_long_captions", False)
        self.max_caption_length = display_config.get("max_caption_length", 100)

        # Load font
        self.font = self._load_font()

        # Calculate layout
        self.chars_per_column = self._calculate_chars_per_column()
        self.columns_per_screen = self._calculate_columns_per_screen()

        # Store columns (each column is a caption string)
        # Index 0 = oldest (leftmost of Screen 3)
        # Index -1 = newest (rightmost of Screen 1)
        self.columns: List[str] = []

        # Typing animation for the NEWEST column only
        self.typing_state = {
            "full_text": "",
            "revealed_chars": 0,
            "last_update": 0.0,
            "active": False
        }

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

        print(f"✅ CascadingScreenDisplay initialized:")
        print(f"   Screens: {screen_count}")
        print(f"   Chars per column: {self.chars_per_column}")
        print(f"   Columns per screen: {self.columns_per_screen}")
        print(f"   Total columns: {self.columns_per_screen * screen_count}")
        print(f"   Truncate long captions: {self.truncate_long_captions}")

    def _load_font(self):
        """Load custom font or fall back to default"""
        try:
            font_path = Path(self.font_path)
            if font_path.exists():
                return ImageFont.truetype(str(font_path), self.font_size)
        except Exception as e:
            print(f"⚠️  Could not load font {self.font_path}: {e}")

        try:
            return ImageFont.load_default()
        except:
            return None

    def _calculate_chars_per_column(self) -> int:
        """Calculate how many characters fit in one vertical column"""
        available_height = self.window_height - 100
        char_height = self.font_size + self.char_spacing
        return max(1, available_height // char_height)

    def _calculate_columns_per_screen(self) -> int:
        """Calculate how many columns fit in one screen"""
        available_width = self.window_width - 100
        column_width_total = self.font_size + self.column_width
        return max(1, available_width // column_width_total)

    def add_caption(self, caption: str):
        """
        Add a new caption - appears on RIGHTMOST column of Screen 1.
        All old columns shift LEFT.
        """
        if not caption or not caption.strip():
            return

        # Replace spaces with hyphens
        formatted_caption = caption.replace(" ", "-")

        # Truncate if needed
        if self.truncate_long_captions and len(formatted_caption) > self.max_caption_length:
            formatted_caption = formatted_caption[:self.max_caption_length] + "..."

        # If caption is longer than column height, split into multiple columns
        if len(formatted_caption) > self.chars_per_column and not self.truncate_long_captions:
            # Split into multiple columns
            chunks = []
            for i in range(0, len(formatted_caption), self.chars_per_column):
                chunk = formatted_caption[i:i + self.chars_per_column]
                chunks.append(chunk)

            # Add chunks in reverse order so they read correctly
            # (first chunk should be leftmost)
            for chunk in reversed(chunks):
                self.columns.append(chunk)
        else:
            # Single column
            if len(formatted_caption) > self.chars_per_column:
                formatted_caption = formatted_caption[:self.chars_per_column]
            self.columns.append(formatted_caption)

        # Start typing animation for the newest column
        self.typing_state = {
            "full_text": self.columns[-1],
            "revealed_chars": 0,
            "last_update": time.time(),
            "active": True
        }

        # Limit total columns
        max_total_columns = self.columns_per_screen * self.screen_count
        if len(self.columns) > max_total_columns:
            # Remove oldest columns
            overflow = len(self.columns) - max_total_columns
            self.columns = self.columns[overflow:]

        print(f"📝 Added caption (column {len(self.columns)}): {caption[:30]}...")

    def add_summary(self, summary: str):
        """Add a summary (just adds as a caption)"""
        self.add_caption(summary)

    def update_typing_animations(self):
        """Update typing animation for the newest column"""
        if not self.typing_state["active"]:
            return

        current_time = time.time()
        full_text = self.typing_state["full_text"]
        revealed_chars = self.typing_state["revealed_chars"]

        # Check if animation is complete
        if revealed_chars >= len(full_text):
            self.typing_state["active"] = False
            return

        # Check if enough time has passed to reveal next character
        time_since_update = current_time - self.typing_state["last_update"]
        if time_since_update >= self.typing_speed:
            self.typing_state["revealed_chars"] += 1
            self.typing_state["last_update"] = current_time

    def _get_column_text(self, column_index: int) -> str:
        """Get the text for a specific column, with typing effect for newest"""
        if column_index >= len(self.columns):
            return ""

        column_text = self.columns[column_index]

        # Apply typing effect ONLY to the newest column (last one)
        if column_index == len(self.columns) - 1 and self.typing_state["active"]:
            revealed_chars = self.typing_state["revealed_chars"]
            displayed_text = column_text[:revealed_chars]

            # Add blinking cursor
            if revealed_chars < len(column_text):
                if int(time.time() * 2) % 2 == 0:
                    displayed_text += "█"

            return displayed_text
        else:
            return column_text

    def _render_screen(self, screen_index: int) -> np.ndarray:
        """
        Render a single screen.
        Screen layout (Chinese classical style):
        - Newest columns on the RIGHT
        - Oldest columns on the LEFT
        - Screen 1 has the newest columns
        - Screen 2 has older columns
        - Screen 3 has the oldest columns
        """
        img = Image.new('RGB', (self.window_width, self.window_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Calculate which columns belong to this screen
        # Screen 0 (rightmost) gets newest columns
        # Screen 1 (middle) gets older columns
        # Screen 2 (leftmost) gets oldest columns

        # Reverse screen index: Screen 1 = index 0, Screen 3 = index 2
        # But we want Screen 1 to have newest, so:
        reversed_screen_index = (self.screen_count - 1) - screen_index

        # Calculate column range for this screen
        start_col = reversed_screen_index * self.columns_per_screen
        end_col = start_col + self.columns_per_screen

        # Get columns for this screen (newest to oldest)
        total_columns = len(self.columns)
        screen_columns = []

        for i in range(start_col, end_col):
            # Calculate absolute column index (from the end, since newest is last)
            col_idx = total_columns - 1 - i
            if 0 <= col_idx < total_columns:
                screen_columns.append((i - start_col, self._get_column_text(col_idx)))

        # Draw columns from right to left
        for relative_col_idx, column_text in screen_columns:
            # Calculate x position (rightmost = highest x)
            x = self.window_width - 50 - (relative_col_idx * (self.font_size + self.column_width))

            # Draw characters vertically
            y = 50
            for char in column_text:
                if self.font:
                    draw.text((x, y), char, font=self.font, fill=(255, 255, 255))
                y += self.font_size + self.char_spacing

                # Stop if we run out of vertical space
                if y > self.window_height - 50:
                    break

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

        display_frame = cv2.resize(frame, (1280, 720))

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
        return {
            "screen_count": self.screen_count,
            "total_columns": len(self.columns),
            "typing_active": self.typing_state["active"],
            "chars_per_column": self.chars_per_column,
            "columns_per_screen": self.columns_per_screen,
            "max_columns": self.columns_per_screen * self.screen_count
        }


# Alias for compatibility
MultiScreenDisplay = CascadingScreenDisplay
CascadingMultiScreenDisplay = CascadingScreenDisplay


if __name__ == "__main__":
    print("Testing CascadingScreenDisplay - Chinese Classical Style...")

    config = {
        "display": {
            "text_screen_count": 3,
            "window_width": 1920,
            "window_height": 1080,
            "font_size": 48,
            "font_path": "assets/fonts/Acumin_Variable_Concept.ttf",
            "typing_speed": 0.05,
            "column_width": 20,
            "char_spacing": 5,
            "truncate_long_captions": False,
            "max_caption_length": 30
        }
    }

    display = CascadingScreenDisplay(screen_count=3, config=config)

    test_captions = [
        "Caption 1",
        "Caption 2 is longer",
        "Caption 3",
        "Caption 4 - testing the flow",
        "Caption 5",
        "Caption 6 - old ones shift left",
        "Caption 7",
        "Caption 8 - newest on right!"
    ]

    try:
        for i, caption in enumerate(test_captions):
            print(f"\n➕ Adding: {caption}")
            display.add_caption(caption)

            # Show typing animation
            for _ in range(100):
                display.update_typing_animations()
                display.update_all_screens()

                if display.check_for_quit():
                    break

                time.sleep(0.03)

        print("\n" + "="*60)
        stats = display.get_stats()
        print("📊 Stats:", stats)
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
