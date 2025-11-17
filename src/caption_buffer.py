#!/usr/bin/env python3
"""
Caption Buffer Module
Manages caption accumulation and timing for dual-interval mode.
"""

import time
from typing import List, Optional
from collections import deque


class CaptionBuffer:
    """Manages caption accumulation for periodic summarization"""

    def __init__(self, max_size: int = 20, interval_long: float = 30.0):
        self.buffer = deque(maxlen=max_size)
        self.max_size = max_size
        self.interval_long = interval_long
        self.last_summary_time = time.time()
        self.captions_since_summary = 0

    def add_caption(self, caption: str, timestamp: Optional[float] = None):
        """Add a caption to the buffer"""
        if not caption or not caption.strip():
            return

        timestamp = timestamp or time.time()
        self.buffer.append({
            "text": caption,
            "timestamp": timestamp
        })
        self.captions_since_summary += 1

    def get_all_captions(self) -> List[str]:
        """Get all captions as a list of strings"""
        return [item["text"] for item in self.buffer]

    def get_captions_with_timestamps(self) -> List[dict]:
        """Get all captions with timestamps"""
        return list(self.buffer)

    def get_recent_captions(self, count: int = 10) -> List[str]:
        """Get the most recent N captions"""
        recent = list(self.buffer)[-count:]
        return [item["text"] for item in recent]

    def clear(self):
        """Clear the buffer and reset counters"""
        self.buffer.clear()
        self.captions_since_summary = 0
        self.last_summary_time = time.time()

    def should_summarize(self, current_time: Optional[float] = None) -> bool:
        """Check if it's time to summarize based on interval"""
        current_time = current_time or time.time()
        elapsed = current_time - self.last_summary_time
        return elapsed >= self.interval_long and len(self.buffer) > 0

    def mark_summarized(self, current_time: Optional[float] = None):
        """Mark that a summary was generated"""
        self.last_summary_time = current_time or time.time()
        self.captions_since_summary = 0

    def get_time_until_summary(self, current_time: Optional[float] = None) -> float:
        """Get remaining time until next summary"""
        current_time = current_time or time.time()
        elapsed = current_time - self.last_summary_time
        remaining = max(0, self.interval_long - elapsed)
        return remaining

    def get_stats(self) -> dict:
        """Get buffer statistics"""
        return {
            "buffer_size": len(self.buffer),
            "max_size": self.max_size,
            "captions_since_summary": self.captions_since_summary,
            "time_since_summary": time.time() - self.last_summary_time,
            "time_until_summary": self.get_time_until_summary(),
            "interval_long": self.interval_long
        }

    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        return len(self.buffer) == 0

    def is_full(self) -> bool:
        """Check if buffer is at max capacity"""
        return len(self.buffer) >= self.max_size

    def set_interval(self, interval_long: float):
        """Update the long interval setting"""
        self.interval_long = interval_long

    def __len__(self):
        """Get number of captions in buffer"""
        return len(self.buffer)

    def __str__(self):
        """String representation for debugging"""
        stats = self.get_stats()
        return (
            f"CaptionBuffer("
            f"size={stats['buffer_size']}/{stats['max_size']}, "
            f"since_summary={stats['captions_since_summary']}, "
            f"time_until={stats['time_until_summary']:.1f}s)"
        )


class DualIntervalManager:
    """Manages dual-interval timing for caption generation and summarization"""

    def __init__(self, interval_short: float = 3.0, interval_long: float = 30.0):
        self.interval_short = interval_short
        self.interval_long = interval_long
        self.last_caption_time = 0.0
        self.last_summary_time = 0.0

    def should_generate_caption(self, current_time: Optional[float] = None) -> bool:
        """Check if it's time to generate a new caption"""
        current_time = current_time or time.time()
        elapsed = current_time - self.last_caption_time
        return elapsed >= self.interval_short

    def should_generate_summary(self, current_time: Optional[float] = None) -> bool:
        """Check if it's time to generate a summary"""
        current_time = current_time or time.time()
        elapsed = current_time - self.last_summary_time
        return elapsed >= self.interval_long

    def mark_caption_generated(self, current_time: Optional[float] = None):
        """Mark that a caption was generated"""
        self.last_caption_time = current_time or time.time()

    def mark_summary_generated(self, current_time: Optional[float] = None):
        """Mark that a summary was generated"""
        self.last_summary_time = current_time or time.time()

    def get_time_until_caption(self, current_time: Optional[float] = None) -> float:
        """Get remaining time until next caption"""
        current_time = current_time or time.time()
        elapsed = current_time - self.last_caption_time
        return max(0, self.interval_short - elapsed)

    def get_time_until_summary(self, current_time: Optional[float] = None) -> float:
        """Get remaining time until next summary"""
        current_time = current_time or time.time()
        elapsed = current_time - self.last_summary_time
        return max(0, self.interval_long - elapsed)

    def get_stats(self) -> dict:
        """Get timing statistics"""
        current_time = time.time()
        return {
            "interval_short": self.interval_short,
            "interval_long": self.interval_long,
            "time_until_caption": self.get_time_until_caption(current_time),
            "time_until_summary": self.get_time_until_summary(current_time),
            "time_since_caption": current_time - self.last_caption_time,
            "time_since_summary": current_time - self.last_summary_time
        }

    def reset(self):
        """Reset all timers"""
        self.last_caption_time = time.time()
        self.last_summary_time = time.time()

    def __str__(self):
        """String representation for debugging"""
        stats = self.get_stats()
        return (
            f"DualIntervalManager("
            f"caption_in={stats['time_until_caption']:.1f}s, "
            f"summary_in={stats['time_until_summary']:.1f}s)"
        )


if __name__ == "__main__":
    # Test caption buffer
    print("Testing CaptionBuffer...")

    buffer = CaptionBuffer(max_size=5, interval_long=10.0)

    # Add some captions
    test_captions = [
        "a person sitting at desk",
        "typing on a laptop",
        "drinking coffee",
        "looking at screen",
        "smiling"
    ]

    for i, caption in enumerate(test_captions):
        buffer.add_caption(caption)
        print(f"Added: {caption}")
        print(f"  {buffer}")
        time.sleep(0.1)

    print(f"\nAll captions: {buffer.get_all_captions()}")
    print(f"Recent 3: {buffer.get_recent_captions(3)}")
    print(f"\nStats: {buffer.get_stats()}")

    # Test dual interval manager
    print("\n" + "=" * 60)
    print("Testing DualIntervalManager...")

    manager = DualIntervalManager(interval_short=2.0, interval_long=5.0)
    print(f"Initial state: {manager}")

    # Simulate caption generation
    manager.mark_caption_generated()
    time.sleep(1)
    print(f"After 1s: {manager}")

    time.sleep(1)
    if manager.should_generate_caption():
        print("Time to generate caption!")
        manager.mark_caption_generated()

    print(f"Final state: {manager}")
