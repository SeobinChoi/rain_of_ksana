#!/usr/bin/env python3
"""
BLIP Camera Captioning - Main Script
Modular version with separated concerns.
"""

import argparse
import sys
from caption_engine import CaptionEngine

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="BLIP Camera Captioning")
    
    parser.add_argument("--model", 
                       default="Salesforce/blip-image-captioning-base",
                       help="BLIP model name (default: Salesforce/blip-image-captioning-base)")
    
    parser.add_argument("--interval", 
                       type=int, 
                       default=5,
                       help="Caption generation interval in seconds (default: 5)")
    
    parser.add_argument("--camera", 
                       type=int, 
                       default=0,
                       help="Camera index (default: 0)")
    
    parser.add_argument("--blip2", 
                       action="store_true",
                       help="Use BLIP-2 model instead of BLIP")
    
    parser.add_argument("--show-camera", 
                       action="store_true",
                       help="Show camera window with live preview")
    
    parser.add_argument("--list-cameras",
                       action="store_true",
                       help="List available camera devices and exit")
    
    parser.add_argument("--auto-camera",
                       action="store_true",
                       help="Automatically select the first available camera")
    
    parser.add_argument("--backend",
                       default="auto",
                       help="Camera backend to use (auto, dshow, msmf, avfoundation, v4l2)")
    
    parser.add_argument("--status", 
                       action="store_true",
                       help="Show system status and exit")
    
    parser.add_argument("--dual-screen", 
                       action="store_true",
                       help="Enable dual screen display (camera + text)")
    
    return parser.parse_args()

def select_model(args):
    """Select model based on arguments"""
    if args.blip2:
        return "Salesforce/blip2-opt-2.7b"
    else:
        return args.model

def main():
    """Main function"""
    args = parse_arguments()
    
    # Handle camera discovery
    if args.list_cameras:
        from camera_manager import CameraManager
        devices = CameraManager.list_cameras(max_index=10, backend=args.backend)
        print("Detected camera devices:")
        print("=" * 50)
        for info in devices:
            status = "OK" if info.get("available") else "NO"
            backend = info.get("backend") or "-"
            dims = f"{info.get('width')}x{info.get('height')}@{info.get('fps')}" if info.get("available") else "-"
            print(f"Index {info['index']}: {status} backend={backend} dims={dims}")
        return

    # Auto-select camera if requested
    if args.auto_camera:
        from camera_manager import CameraManager
        selected = CameraManager.auto_select_camera(max_index=10, backend=args.backend)
        if selected is None:
            print("ERROR: No available camera found. Try --list-cameras or a different --backend.")
            sys.exit(1)
        print(f"Auto-selected camera index: {selected}")
        args.camera = selected

    # Select model
    model_name = select_model(args)
    
    # Create caption engine
    engine = CaptionEngine(
        model_name=model_name,
        camera_index=args.camera,
        show_camera=args.show_camera,
        interval=args.interval,
        dual_screen=args.dual_screen,
        backend=args.backend
    )
    
    # Show status if requested
    if args.status:
        print("System Status:")
        print("=" * 50)
        status = engine.get_status()
        
        print(f"Model: {status['model_info']['model_name']}")
        print(f"Device: {status['model_info']['device']}")
        print(f"Model Loaded: {status['model_info']['loaded']}")
        print(f"Camera Index: {status['camera_info'].get('camera_index', 'N/A')}")
        print(f"Camera Backend: {status['camera_info'].get('backend', 'N/A')}")
        print(f"Show Camera: {status['settings']['show_camera']}")
        print(f"Dual Screen: {status['settings']['dual_screen']}")
        print(f"Interval: {status['settings']['interval']} seconds")
        return
    
    # Initialize and run
    if not engine.initialize():
        print("ERROR: Failed to initialize caption engine")
        sys.exit(1)
    
    try:
        engine.run()
    except Exception as e:
        print(f"ERROR: Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
