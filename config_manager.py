#!/usr/bin/env python3
"""
Configuration Manager Module
Handles configuration loading, saving, validation, and interactive setup.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration with interactive setup"""

    DEFAULT_CONFIG = {
        "display": {
            "text_screen_count": 1,
            "window_width": 2560,
            "window_height": 1440,
            "font_size": 24,
            "font_path": "assets/fonts/Acumin_Variable_Concept.ttf",
            "typing_speed": 0.03,
            "column_width": 10,
            "char_spacing": 2
        },
        "model": {
            "type": "blip",  # blip or blip2
            "use_gpu": "auto"  # auto, true, false
        },
        "camera": {
            "index": 0,
            "backend": "auto",
            "show_camera": False
        },
        "timing": {
            "dual_interval_mode": False,
            "interval_short": 3,  # seconds
            "interval_long": 30   # seconds
        },
        "ollama": {
            "enabled": False,
            "model": "llama3.2:3b",
            "base_url": "http://localhost:11434",
            "timeout": 30,
            "prompt_template": (
                "Summarize the following scene descriptions into one coherent narrative sentence. "
                "Consider the time order and describe it like a story:\n\n{captions}"
            )
        }
    }

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.suffix == '.json':
                        config = json.load(f)
                    else:  # yaml
                        config = yaml.safe_load(f)
                print(f"✅ Configuration loaded from {self.config_path}")
                return self._merge_with_defaults(config)
            except Exception as e:
                print(f"⚠️  Error loading config: {e}")
                print("Using default configuration")
                return self.DEFAULT_CONFIG.copy()
        else:
            print("📝 No config file found, using defaults")
            return self.DEFAULT_CONFIG.copy()

    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults to ensure all keys exist"""
        merged = self.DEFAULT_CONFIG.copy()

        for section, values in config.items():
            if section in merged and isinstance(values, dict):
                merged[section].update(values)
            else:
                merged[section] = values

        return merged

    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.suffix == '.json':
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                else:  # yaml
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)

            print(f"✅ Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False

    def interactive_setup(self) -> Dict[str, Any]:
        """Interactive CLI configuration setup"""
        print("\n" + "=" * 60)
        print("🎨 BLIP Camera Captioning - Interactive Setup")
        print("=" * 60 + "\n")

        # Display settings
        print("📺 Display Settings")
        print("-" * 60)

        screen_count = self._ask_int(
            "Number of text screens (1-7)",
            default=1,
            min_val=1,
            max_val=7
        )
        self.config["display"]["text_screen_count"] = screen_count

        font_size = self._ask_int(
            "Font size (12-48)",
            default=24,
            min_val=12,
            max_val=48
        )
        self.config["display"]["font_size"] = font_size

        typing_speed = self._ask_float(
            "Typing animation speed (0.01-0.1, lower is faster)",
            default=0.03,
            min_val=0.01,
            max_val=0.1
        )
        self.config["display"]["typing_speed"] = typing_speed

        # Model settings
        print("\n🤖 Model Settings")
        print("-" * 60)

        model_type = self._ask_choice(
            "Select BLIP model",
            choices=["blip", "blip2"],
            default="blip",
            descriptions={
                "blip": "Fast and lightweight base model",
                "blip2": "More accurate but slower advanced model"
            }
        )
        self.config["model"]["type"] = model_type

        # Camera settings
        print("\n📷 Camera Settings")
        print("-" * 60)

        camera_index = self._ask_int(
            "Camera index",
            default=0,
            min_val=0,
            max_val=10
        )
        self.config["camera"]["index"] = camera_index

        show_camera = self._ask_bool(
            "Show camera feed window",
            default=False
        )
        self.config["camera"]["show_camera"] = show_camera

        # Timing settings
        print("\n⏱️  Timing Settings")
        print("-" * 60)

        dual_mode = self._ask_bool(
            "Use dual-interval mode (staged text generation and summarization)",
            default=False
        )
        self.config["timing"]["dual_interval_mode"] = dual_mode

        if dual_mode:
            interval_short = self._ask_int(
                "Short interval - caption generation period (seconds)",
                default=3,
                min_val=1,
                max_val=60
            )
            self.config["timing"]["interval_short"] = interval_short

            interval_long = self._ask_int(
                "Long interval - text summary period (seconds)",
                default=30,
                min_val=10,
                max_val=300
            )
            self.config["timing"]["interval_long"] = interval_long

            # Ollama settings
            print("\n🦙 Ollama Settings (for text summarization)")
            print("-" * 60)

            use_ollama = self._ask_bool(
                "Use Ollama for text summarization",
                default=True
            )
            self.config["ollama"]["enabled"] = use_ollama

            if use_ollama:
                ollama_model = self._ask_choice(
                    "Select Ollama model",
                    choices=["llama3.2:3b", "llama3.1:8b", "qwen2.5:7b"],
                    default="llama3.2:3b",
                    descriptions={
                        "llama3.2:3b": "Lightweight model (fast, multilingual)",
                        "llama3.1:8b": "Medium model (better quality)",
                        "qwen2.5:7b": "Medium model (multilingual optimized)"
                    }
                )
                self.config["ollama"]["model"] = ollama_model
        else:
            interval = self._ask_int(
                "Caption generation interval (seconds)",
                default=5,
                min_val=1,
                max_val=60
            )
            self.config["timing"]["interval_short"] = interval

        # Save option
        print("\n💾 Save Configuration")
        print("-" * 60)

        save_config = self._ask_bool(
            f"Save configuration to {self.config_path}",
            default=True
        )

        if save_config:
            self.save_config()

        print("\n✅ Configuration setup complete!")
        print("=" * 60 + "\n")

        return self.config

    def _ask_int(self, prompt: str, default: int, min_val: int, max_val: int) -> int:
        """Ask for integer input with validation"""
        while True:
            try:
                response = input(f"{prompt} [{default}]: ").strip()
                if not response:
                    return default
                value = int(response)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"⚠️  Value must be between {min_val} and {max_val}.")
            except ValueError:
                print("⚠️  Please enter a valid number.")

    def _ask_float(self, prompt: str, default: float, min_val: float, max_val: float) -> float:
        """Ask for float input with validation"""
        while True:
            try:
                response = input(f"{prompt} [{default}]: ").strip()
                if not response:
                    return default
                value = float(response)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"⚠️  Value must be between {min_val} and {max_val}.")
            except ValueError:
                print("⚠️  Please enter a valid number.")

    def _ask_bool(self, prompt: str, default: bool) -> bool:
        """Ask for yes/no input"""
        default_str = "Y/n" if default else "y/N"
        while True:
            response = input(f"{prompt}? [{default_str}]: ").strip().lower()
            if not response:
                return default
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("⚠️  Please enter 'y' or 'n'.")

    def _ask_choice(self, prompt: str, choices: list, default: str,
                   descriptions: Optional[Dict[str, str]] = None) -> str:
        """Ask for choice from a list"""
        print(f"\n{prompt}:")
        for i, choice in enumerate(choices, 1):
            desc = f" - {descriptions[choice]}" if descriptions and choice in descriptions else ""
            default_mark = " [default]" if choice == default else ""
            print(f"  {i}. {choice}{desc}{default_mark}")

        while True:
            response = input(f"Select (1-{len(choices)}) [{choices.index(default) + 1}]: ").strip()
            if not response:
                return default
            try:
                index = int(response) - 1
                if 0 <= index < len(choices):
                    return choices[index]
                else:
                    print(f"⚠️  Please enter a number between 1 and {len(choices)}.")
            except ValueError:
                print("⚠️  Please enter a valid number.")

    def validate_config(self) -> bool:
        """Validate current configuration"""
        try:
            # Validate display settings
            assert 1 <= self.config["display"]["text_screen_count"] <= 7
            assert 12 <= self.config["display"]["font_size"] <= 48
            assert 0.01 <= self.config["display"]["typing_speed"] <= 0.1

            # Validate model settings
            assert self.config["model"]["type"] in ["blip", "blip2"]

            # Validate timing settings
            assert self.config["timing"]["interval_short"] >= 1
            if self.config["timing"]["dual_interval_mode"]:
                assert self.config["timing"]["interval_long"] >= self.config["timing"]["interval_short"]

            return True
        except (AssertionError, KeyError) as e:
            print(f"❌ Configuration validation failed: {e}")
            return False

    def get(self, *keys, default=None):
        """Get nested configuration value"""
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, *keys, value):
        """Set nested configuration value"""
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value

    def print_config(self):
        """Print current configuration in readable format"""
        print("\n📋 Current Configuration:")
        print("=" * 60)
        print(yaml.dump(self.config, default_flow_style=False, allow_unicode=True))
        print("=" * 60)


if __name__ == "__main__":
    # Test interactive setup
    manager = ConfigManager()
    manager.interactive_setup()
    manager.print_config()
