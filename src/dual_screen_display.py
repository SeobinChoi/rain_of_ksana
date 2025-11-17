#!/usr/bin/env python3
"""
Dual Screen Display Module
Shows camera feed in one window and cumulative text in another.
"""

import cv2
import numpy as np
from typing import List, Optional, Dict, Tuple
import time
import threading
from PIL import Image, ImageDraw, ImageFont

class TypingAnimation:
    """Handles typing animation for captions"""
    
    def __init__(self, typing_delay: int, cursor_effect: str):
        self.typing_delay = typing_delay
        self.cursor_effect = cursor_effect
        self.active_animations: Dict[int, Dict] = {}  # caption_id -> animation data
        self.animation_id_counter = 0
        
    def start_typing(self, full_text: str, callback=None) -> int:
        """Start typing animation for a text"""
        animation_id = self.animation_id_counter
        self.animation_id_counter += 1
        
        self.active_animations[animation_id] = {
            'full_text': full_text,
            'current_text': '',
            'current_index': 0,
            'start_time': time.time(),
            'last_char_time': time.time(),
            'callback': callback,
            'completed': False
        }
        
        return animation_id
    
    def update_animations(self) -> Dict[int, str]:
        """Update all active animations and return current states"""
        current_time = time.time()
        results = {}
        
        for animation_id, animation_data in list(self.active_animations.items()):
            if animation_data['completed']:
                continue
                
            # Check if it's time to add next character
            if current_time - animation_data['last_char_time'] >= self.typing_delay / 1000.0:
                if animation_data['current_index'] < len(animation_data['full_text']):
                    # Add next character
                    animation_data['current_text'] += animation_data['full_text'][animation_data['current_index']]
                    animation_data['current_index'] += 1
                    animation_data['last_char_time'] = current_time
                else:
                    # Animation completed
                    animation_data['completed'] = True
                    if animation_data['callback']:
                        animation_data['callback'](animation_data['full_text'])
            
            # Add cursor effect if enabled
            display_text = animation_data['current_text']
            if not animation_data['completed'] and self.cursor_effect != "none":
                if self.cursor_effect == "blink":
                    # Blinking cursor
                    cursor_visible = int(current_time * 2) % 2 == 0
                    if cursor_visible:
                        display_text += "_"
                elif self.cursor_effect == "highlight":
                    # Highlight effect (bold or different color)
                    display_text += "█"
            
            results[animation_id] = display_text
        
        # Clean up completed animations
        self.active_animations = {k: v for k, v in self.active_animations.items() if not v['completed']}
        
        return results
    
    def get_animation_state(self, animation_id: int) -> Optional[str]:
        """Get current state of specific animation"""
        if animation_id in self.active_animations:
            animation_data = self.active_animations[animation_id]
            return animation_data['current_text']
        return None
    
    def is_completed(self, animation_id: int) -> bool:
        """Check if animation is completed"""
        if animation_id in self.active_animations:
            return self.active_animations[animation_id]['completed']
        return True

class DualScreenDisplay:
    """Manages dual screen display with camera and text windows"""
    
    # ================================
    # DISPLAY SETTINGS - 수정 가능한 설정들
    # ================================
    WINDOW_WIDTH = 2560        # 화면 너비 (2K: 2560, 4K: 3840)
    WINDOW_HEIGHT = 1440       # 화면 높이 (2K: 1440, 4K: 2160)
    FONT_PATH = "/Users/xavi/Desktop/real_code/2025ATC/assets/fonts/Acumin_Variable_Concept.ttf"
    FONT_PATH = None
    
    # 폰트 설정
    FONT_SCALE = 2.0           # OpenCV 폰트 스케일 (1.0 = 기본, 2.0 = 2배)
    
    # 텍스트 레이아웃 설정
    COLUMN_WIDTH = 25          # 컬럼 간격 (가로 간격)
    CHAR_SPACING = 2           # 글자 간격 (세로 여백)
    MAX_CAPTIONS = 200         # 최대 저장 캡션 수
    
    # ================================
    # TYPING ANIMATION SETTINGS - 타이핑 애니메이션 설정
    # ================================
    TYPING_ENABLED = True      # 타이핑 효과 활성화 (True/False)
    TYPING_SPEED = "fast"    # 타이핑 속도 ("fast", "medium", "slow")
    CURSOR_EFFECT = "blink"    # 커서 효과 ("blink", "highlight", "none")
    ANIMATION_DURATION = 2.0   # 애니메이션 지속 시간 (초)
    
    # 타이핑 속도 설정 (밀리초)
    TYPING_DELAYS = {
        "fast": 50,      # 50ms per character
        "medium": 100,   # 100ms per character  
        "slow": 200      # 200ms per character
    }
    
    # ================================
    
    def __init__(self, window_width=None, window_height=None):
        # 설정값 사용 또는 매개변수 사용
        self.window_width = window_width or self.WINDOW_WIDTH
        self.window_height = window_height or self.WINDOW_HEIGHT
        self.camera_window = "Camera Feed"
        self.text_windows = ["Text Window 1", "Text Window 2"]  # 여러 텍스트 창
        
        # Text storage - 두 개의 창을 위한 캡션 저장
        self.window1_captions: List[str] = []  # Text Window 1 캡션들
        self.window2_captions: List[str] = []  # Text Window 2 캡션들
        self.max_captions = self.MAX_CAPTIONS
        
        # Window management
        self.window_capacity = 0  # 한 창당 최대 캡션 수
        
        # Typing animation system
        self.typing_enabled = self.TYPING_ENABLED
        self.typing_animation = TypingAnimation(
            typing_delay=self.TYPING_DELAYS.get(self.TYPING_SPEED, 100),
            cursor_effect=self.CURSOR_EFFECT
        )
        
        # Animation tracking
        self.caption_animations: Dict[int, Dict] = {}  # caption_index -> animation_data
        self.animation_counter = 0
        
        # Font setup
        self.font_path = self.FONT_PATH
        self.font_scale = self.FONT_SCALE
        self.font = None
        self._load_font()
        
        # Vertical layout settings
        self.chars_per_column = None  # No limit - use full height
        self.column_width = self.COLUMN_WIDTH
        
        # Create windows
        self._create_windows()
        
    def _create_windows(self):
        """Create multiple windows (camera + text windows)"""
        # Create camera window
        cv2.namedWindow(self.camera_window, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.camera_window, self.window_width, self.window_height)
        
        # Create text windows
        for i, window_name in enumerate(self.text_windows):
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, self.window_width, self.window_height)
        
        # Position windows
        cv2.moveWindow(self.camera_window, 100, 100)  # 카메라 창 위치
        cv2.moveWindow(self.text_windows[0], self.window_width + 150, 100)  # 첫 번째 텍스트 창
        cv2.moveWindow(self.text_windows[1], self.window_width + 150, self.window_height + 200)  # 두 번째 텍스트 창
    
    def _load_font(self):
        """Load the custom font"""
        try:
            self.font = ImageFont.truetype(self.font_path, int(self.font_scale * 24))
            print(f"Custom font loaded: {self.font_path} (scale: {self.font_scale})")
        except Exception as e:
            print(f"Could not load custom font: {e}")
            print("Using default font")
            try:
                self.font = ImageFont.load_default()
            except:
                self.font = None
    
    def reload_font(self):
        """Reload font with current settings"""
        self.font_scale = self.FONT_SCALE
        self._load_font()
        print(f"Font reloaded with scale: {self.font_scale}")
        
    def display_camera_frame(self, frame, current_caption: str = ""):
        """Display camera frame with optional caption overlay"""
        display_frame = frame.copy()
        
        # Add current caption overlay if available
        if current_caption:
            # Wrap text for better display
            wrapped_caption = self._wrap_text(current_caption, 60)
            y_offset = 30
            
            for line in wrapped_caption.split('\n'):
                cv2.putText(
                    display_frame,
                    line,
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),  # Green color
                    2
                )
                y_offset += 25
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(
            display_frame,
            f"Live - {timestamp}",
            (10, display_frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),  # White color
            1
        )
        
        cv2.imshow(self.camera_window, display_frame)
        
    def add_caption(self, caption: str):
        """Add a new caption to Window 1, overflow goes to Window 2"""
        # Calculate window capacity if not done yet
        if self.window_capacity == 0:
            self._calculate_window_capacity()
        
        # Add new caption to Window 1 (right side)
        caption_index = len(self.window1_captions)
        self.window1_captions.append(caption)
        
        # Start typing animation for new caption if enabled
        if self.typing_enabled:
            animation_id = self.typing_animation.start_typing(caption)
            self.caption_animations[caption_index] = {
                'animation_id': animation_id,
                'completed': False,
                'window': 1
            }
        
        # If Window 1 is full, move oldest caption to Window 2
        if len(self.window1_captions) > self.window_capacity:
            # Move the oldest caption from Window 1 to Window 2
            overflow_caption = self.window1_captions.pop(0)
            self.window2_captions.append(overflow_caption)
            
            # Update animation tracking
            if self.typing_enabled:
                # Remove old animation data
                old_animations = {k: v for k, v in self.caption_animations.items() if v['window'] == 1}
                self.caption_animations = {k: v for k, v in self.caption_animations.items() if v['window'] != 1}
                
                # Add to window 2 with new index
                new_index = len(self.window2_captions) - 1
                if old_animations:
                    # Move animation data to window 2
                    for old_idx, anim_data in old_animations.items():
                        self.caption_animations[new_index] = anim_data
                        self.caption_animations[new_index]['window'] = 2
            
            # If Window 2 is also full, remove oldest caption
            if len(self.window2_captions) > self.window_capacity:
                self.window2_captions.pop(0)
                # Clean up animation data
                if self.typing_enabled:
                    self.caption_animations = {k: v for k, v in self.caption_animations.items() if v['window'] != 2 or k < len(self.window2_captions)}
        
        self._update_text_display()
    
    def _calculate_window_capacity(self):
        """Calculate how many captions can fit in one text window"""
        column_width = self.COLUMN_WIDTH
        
        # Calculate actual character height based on font scale and spacing
        if self.font:
            # Get actual font height from the loaded font
            try:
                bbox = self.font.getbbox("Ag")  # Test with a character
                font_height = bbox[3] - bbox[1]  # Bottom - Top
            except:
                font_height = int(self.font_scale * 24)  # Fallback to scaled font size
        else:
            font_height = int(self.font_scale * 24)  # Fallback to scaled font size
        
        char_height = font_height + self.CHAR_SPACING
        
        # Calculate how many columns can fit horizontally
        max_columns = (self.window_width - 40) // column_width
        
        # Calculate how many characters can fit in each column (full height)
        max_chars_per_column = (self.window_height - 40) // char_height
        
        # Estimate capacity based on average caption length
        # Assume average caption is about 30 characters
        avg_caption_length = 30
        self.window_capacity = max_columns * max(1, int(avg_caption_length / 20))  # Rough estimate
        
    def _update_text_display(self):
        """Update both text windows with vertical Chinese-style layout"""
        # Update typing animations
        if self.typing_enabled:
            self.typing_animation.update_animations()
        
        # Update Window 1
        self._update_single_window(self.window1_captions, 0)
        
        # Update Window 2  
        self._update_single_window(self.window2_captions, 1)
    
    def _update_single_window(self, captions: List[str], window_index: int):
        """Update a single text window with vertical Chinese-style layout"""
        # Create PIL image with black background
        pil_image = Image.new('RGB', (self.window_width, self.window_height), 'black')
        draw = ImageDraw.Draw(pil_image)
        
        if captions:
            # Calculate layout - 실시간으로 설정값 사용
            column_width = self.COLUMN_WIDTH
            
            # Calculate actual character height based on font scale and spacing
            if self.font:
                # Get actual font height from the loaded font
                try:
                    bbox = self.font.getbbox("Ag")  # Test with a character
                    font_height = bbox[3] - bbox[1]  # Bottom - Top
                except:
                    font_height = int(self.font_scale * 24)  # Fallback to scaled font size
            else:
                font_height = int(self.font_scale * 24)  # Fallback to scaled font size
            
            char_height = font_height + self.CHAR_SPACING
            
            # Calculate how many characters can fit in each column (full height)
            max_chars_per_column = (self.window_height - 40) // char_height
            
            # Use full height if no limit specified
            if self.chars_per_column is None:
                chars_per_column = max_chars_per_column
            else:
                chars_per_column = min(self.chars_per_column, max_chars_per_column)
            
            # Calculate how many columns can fit horizontally
            max_columns = (self.window_width - 40) // column_width
            
            # Keep only the latest captions that can fit on screen
            visible_captions = captions[-max_columns:] if len(captions) > max_columns else captions
            
            # Start from right side and work left (newest on right)
            start_x = self.window_width - 20
            current_column = 0
            
            # Process each caption as a separate column (newest first)
            for i, caption in enumerate(reversed(visible_captions)):
                # Get typing animation state if available
                if self.typing_enabled:
                    caption_index = len(captions) - 1 - i
                    if caption_index in self.caption_animations:
                        anim_data = self.caption_animations[caption_index]
                        if not anim_data['completed']:
                            # Use animated text
                            animated_text = self.typing_animation.get_animation_state(anim_data['animation_id'])
                            if animated_text:
                                caption = animated_text
                
                # Replace spaces with hyphens
                caption_text = caption.replace(" ", "-")
                chars = list(caption_text)
                
                # Calculate column position (right to left)
                column_x = start_x - (current_column * column_width)
                
                if column_x < 20:  # Stop if we run out of space
                    break
                
                # Draw characters vertically in this column
                for j, char in enumerate(chars):
                    char_y = 20 + (j * char_height)
                    
                    if char_y + char_height > self.window_height - 20:
                        break
                    
                    # Draw character
                    draw.text(
                        (column_x, char_y),
                        char,
                        font=self.font,
                        fill='white'
                    )
                
                # Move to next column for next caption
                current_column += 1
        
        # Add footer with window info
        window_num = window_index + 1
        footer_text = f"Window {window_num} | Captions: {len(captions)} | Press 'q' to quit"
        draw.text(
            (20, self.window_height - 30),
            footer_text,
            font=self.font,
            fill='white'
        )
        
        # Convert PIL image back to OpenCV format
        text_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Show in the specific text window
        cv2.imshow(self.text_windows[window_index], text_image)
        
    def _wrap_text(self, text: str, max_chars_per_line: int) -> str:
        """Wrap text to fit within specified character limit (kept for compatibility)"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_chars_per_line:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(current_line)
        
        return "\n".join(lines)
        
    def check_for_quit(self) -> bool:
        """Check if user wants to quit (pressed 'q' in either window)"""
        key = cv2.waitKey(1) & 0xFF
        return key == ord('q')
    
    def update_typing_animations(self):
        """Update typing animations and refresh display if needed"""
        if self.typing_enabled:
            # Update animations
            animation_states = self.typing_animation.update_animations()
            
            # Check if any animations are still active
            has_active_animations = len(self.typing_animation.active_animations) > 0
            
            if has_active_animations:
                # Refresh display to show updated animations
                self._update_text_display()
                return True  # Indicates animations are still active
            
            # Mark completed animations
            for caption_index, anim_data in list(self.caption_animations.items()):
                if not anim_data['completed']:
                    animation_id = anim_data['animation_id']
                    if self.typing_animation.is_completed(animation_id):
                        anim_data['completed'] = True
        
        return False  # No active animations
        
    def cleanup(self):
        """Clean up windows and resources"""
        cv2.destroyAllWindows()
        print("🖥️  All display windows closed")
