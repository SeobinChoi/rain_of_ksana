#!/usr/bin/env python3
"""
Test font reloading functionality
"""

from dual_screen_display import DualScreenDisplay
import time

def test_font_reload():
    """Test font reloading"""
    print("Testing font reloading...")
    
    # Create display
    display = DualScreenDisplay()
    
    # Test captions
    test_captions = [
        "Font size test",
        "This should be big text",
        "Testing font reload"
    ]
    
    print("Adding captions...")
    for caption in test_captions:
        display.add_caption(caption)
        time.sleep(1)
    
    print("Font reloading...")
    display.reload_font()
    
    print("Adding more captions after reload...")
    display.add_caption("RELOADED FONT")
    display.add_caption("SHOULD BE BIGGER")
    
    print("Test completed! Press 'q' in any window to quit.")
    
    # Keep display running
    while True:
        display.update_typing_animations()
        if display.check_for_quit():
            break
        time.sleep(0.1)
    
    display.cleanup()

if __name__ == "__main__":
    test_font_reload()
