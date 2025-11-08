#!/usr/bin/env python3
"""
BLIP Camera Captioning - Enhanced Main Script
Supports multi-screen display, dual-interval mode, and Ollama integration.
"""

import argparse
import sys
from pathlib import Path
from config_manager import ConfigManager
from caption_engine_enhanced import CaptionEngineEnhanced
from camera_manager import CameraManager


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="BLIP Camera Captioning System - Enhanced Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive setup (recommended for first use)
  python main_enhanced.py --interactive

  # Use saved configuration
  python main_enhanced.py --config config.yaml

  # Quick start with 3 screens
  python main_enhanced.py --screens 3 --blip2

  # List available cameras
  python main_enhanced.py --list-cameras

For more information, see: README.md
        """
    )

    # Configuration mode
    config_group = parser.add_mutually_exclusive_group()
    config_group.add_argument("--interactive", "-i",
                              action="store_true",
                              help="Interactive configuration setup (recommended for first use)")
    config_group.add_argument("--config", "-c",
                              type=str,
                              metavar="FILE",
                              help="Load configuration from YAML/JSON file")

    # Quick configuration options (override config file)
    quick_group = parser.add_argument_group("Quick Configuration Options")
    quick_group.add_argument("--screens",
                            type=int,
                            choices=[1, 2, 3],
                            help="Number of text screens (1-3)")
    quick_group.add_argument("--blip2",
                            action="store_true",
                            help="Use BLIP-2 model (more accurate, slower)")
    quick_group.add_argument("--dual-interval",
                            action="store_true",
                            help="Enable dual-interval mode with Ollama summarization")
    quick_group.add_argument("--interval",
                            type=int,
                            metavar="SECONDS",
                            help="Caption generation interval (seconds)")

    # Camera options
    camera_group = parser.add_argument_group("Camera Options")
    camera_group.add_argument("--camera",
                             type=int,
                             default=0,
                             help="Camera index (default: 0)")
    camera_group.add_argument("--list-cameras",
                             action="store_true",
                             help="List available cameras and exit")
    camera_group.add_argument("--auto-camera",
                             action="store_true",
                             help="Automatically select first available camera")
    camera_group.add_argument("--backend",
                             default="auto",
                             help="Camera backend (auto, dshow, msmf, etc.)")
    camera_group.add_argument("--show-camera",
                             action="store_true",
                             help="Show camera feed window")

    # System options
    system_group = parser.add_argument_group("System Options")
    system_group.add_argument("--status",
                             action="store_true",
                             help="Show system status and exit")
    system_group.add_argument("--test-ollama",
                             action="store_true",
                             help="Test Ollama connection and exit")

    # Legacy compatibility
    legacy_group = parser.add_argument_group("Legacy Compatibility")
    legacy_group.add_argument("--dual-screen",
                             action="store_true",
                             help="(Legacy) Enable dual screen display")

    return parser.parse_args()


def handle_camera_list(args):
    """Handle --list-cameras option"""
    devices = CameraManager.list_cameras(max_index=10, backend=args.backend)
    print("\n" + "=" * 60)
    print("📷 Available Camera Devices")
    print("=" * 60)

    if not devices:
        print("No cameras detected")
        return

    for info in devices:
        status = "✅ Available" if info.get("available") else "❌ Not available"
        backend = info.get("backend") or "unknown"
        if info.get("available"):
            dims = f"{info.get('width')}x{info.get('height')} @ {info.get('fps')}fps"
        else:
            dims = "N/A"

        print(f"\nIndex {info['index']}: {status}")
        print(f"  Backend: {backend}")
        print(f"  Resolution: {dims}")

    print("\n" + "=" * 60)


def handle_test_ollama(args):
    """Handle --test-ollama option"""
    from ollama_integration import OllamaIntegration

    print("\n" + "=" * 60)
    print("🦙 Ollama Connection Test")
    print("=" * 60 + "\n")

    ollama = OllamaIntegration()
    success = ollama.test_connection()

    if success:
        print("\n✅ Ollama is ready to use!")
    else:
        print("\n❌ Ollama test failed")
        print("\nTo install Ollama:")
        print("  1. Visit: https://ollama.ai/download")
        print("  2. Install Ollama")
        print("  3. Run: ollama pull llama3.2:3b")

    print("\n" + "=" * 60)
    sys.exit(0 if success else 1)


def build_config_from_args(args, config_manager: ConfigManager):
    """Build/modify config from command-line arguments"""
    config = config_manager.config

    # Apply quick configuration overrides
    if args.screens:
        config["display"]["text_screen_count"] = args.screens

    if args.blip2:
        config["model"]["type"] = "blip2"

    if args.dual_interval:
        config["timing"]["dual_interval_mode"] = True
        config["ollama"]["enabled"] = True

    if args.interval:
        config["timing"]["interval_short"] = args.interval

    if args.show_camera:
        config["camera"]["show_camera"] = True

    if args.camera:
        config["camera"]["index"] = args.camera

    if args.backend and args.backend != "auto":
        config["camera"]["backend"] = args.backend

    # Legacy compatibility
    if args.dual_screen:
        config["display"]["text_screen_count"] = max(1, config["display"]["text_screen_count"])

    return config


def main():
    """Main function"""
    args = parse_arguments()

    # Handle utility options
    if args.list_cameras:
        handle_camera_list(args)
        return

    if args.test_ollama:
        handle_test_ollama(args)
        return

    # Auto-select camera if requested
    if args.auto_camera:
        selected = CameraManager.auto_select_camera(max_index=10, backend=args.backend)
        if selected is None:
            print("❌ ERROR: No available camera found")
            print("   Try: python main_enhanced.py --list-cameras")
            sys.exit(1)
        print(f"✅ Auto-selected camera index: {selected}")
        args.camera = selected

    # Configuration handling
    config_manager = None

    if args.interactive:
        # Interactive setup mode
        print("\n🎨 Welcome to BLIP Camera Captioning - Enhanced Edition")
        print("=" * 60)
        print("This wizard will help you configure the system.")
        print("=" * 60 + "\n")

        config_manager = ConfigManager()
        config = config_manager.interactive_setup()

    elif args.config:
        # Load from config file
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"❌ ERROR: Config file not found: {args.config}")
            sys.exit(1)

        config_manager = ConfigManager(str(config_path))
        config = config_manager.config
        print(f"✅ Loaded configuration from {args.config}")

        # Apply command-line overrides
        config = build_config_from_args(args, config_manager)

    else:
        # Use defaults with command-line overrides
        config_manager = ConfigManager()
        config = build_config_from_args(args, config_manager)

        # Inform user about interactive mode
        print("\n💡 Tip: Use --interactive for guided setup")
        print("   Or: Use --config to load saved configuration\n")

    # Validate configuration
    if not config_manager.validate_config():
        print("❌ ERROR: Invalid configuration")
        sys.exit(1)

    # Create enhanced caption engine
    engine = CaptionEngineEnhanced(config)

    # Handle status request
    if args.status:
        print("\n" + "=" * 60)
        print("📊 System Status")
        print("=" * 60)

        status = engine.get_status()

        print("\n🤖 Model:")
        print(f"  Name: {status['model_info']['model_name']}")
        print(f"  Device: {status['model_info']['device']}")
        print(f"  Loaded: {status['model_info']['loaded']}")

        print("\n📷 Camera:")
        print(f"  Index: {status['camera_info'].get('camera_index', 'N/A')}")
        print(f"  Backend: {status['camera_info'].get('backend', 'N/A')}")

        print("\n🖥️  Display:")
        print(f"  Screens: {status['settings']['screen_count']}")

        print("\n⏱️  Timing:")
        print(f"  Mode: {'Dual-interval' if status['settings']['dual_interval_mode'] else 'Single-interval'}")
        print(f"  Short interval: {status['settings']['interval_short']}s")
        if status['settings']['dual_interval_mode']:
            print(f"  Long interval: {status['settings']['interval_long']}s")

        print("\n🦙 Ollama:")
        print(f"  Enabled: {status['settings']['ollama_enabled']}")

        print("\n" + "=" * 60)
        return

    # Initialize and run
    try:
        if not engine.initialize():
            print("\n❌ ERROR: Failed to initialize caption engine")
            sys.exit(1)

        engine.run()

    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ ERROR: Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
