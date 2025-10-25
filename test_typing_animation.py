#!/usr/bin/env python3
"""
Test typing animation functionality
"""

from dual_screen_display import DualScreenDisplay
import time

def test_typing_animation():
    """Test the typing animation system"""
    print("Testing typing animation...")
    
    # Create display with typing enabled
    display = DualScreenDisplay()
    
    # Test captions
    test_captions = [
        "A person sitting at a desk",
        "A cat playing with a ball",
        "A beautiful sunset over the ocean",
        "A car driving down the street",
        "A dog running in the park"
    ]
    
    print("Adding captions with typing animation...")
    
    for i, caption in enumerate(test_captions):
        print(f"Adding caption {i+1}: {caption}")
        display.add_caption(caption)
        
        # Wait for animation to complete
        time.sleep(0.5)
        
        # Update animations
        while display.update_typing_animations():
            time.sleep(0.1)
        
        time.sleep(1)  # Pause between captions
    
    print("Test completed! Press 'q' in any window to quit.")
    
    # Keep display running
    while True:
        display.update_typing_animations()
        if display.check_for_quit():
            break
        time.sleep(0.1)
    
    display.cleanup()

if __name__ == "__main__":
    test_typing_animation()
