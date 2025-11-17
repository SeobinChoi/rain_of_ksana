#!/usr/bin/env python3
"""
System Test Script
Quick verification of all components before running the main application.
"""

import sys
from pathlib import Path


def test_imports():
    """Test if all required modules can be imported"""
    print("\n" + "=" * 60)
    print("🧪 Testing Module Imports")
    print("=" * 60)

    modules = [
        ("torch", "PyTorch"),
        ("transformers", "HuggingFace Transformers"),
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("numpy", "NumPy"),
        ("yaml", "PyYAML"),
        ("requests", "Requests"),
    ]

    success = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"✅ {name} - OK")
        except ImportError as e:
            print(f"❌ {name} - MISSING")
            print(f"   Error: {e}")
            success = False

    return success


def test_gpu():
    """Test GPU availability"""
    print("\n" + "=" * 60)
    print("🎮 Testing GPU Support")
    print("=" * 60)

    try:
        import torch

        print(f"PyTorch version: {torch.__version__}")

        if torch.cuda.is_available():
            print(f"✅ CUDA available")
            print(f"   Device: {torch.cuda.get_device_name(0)}")
            print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            return True
        elif torch.backends.mps.is_available():
            print(f"✅ MPS (Apple Silicon) available")
            return True
        else:
            print("⚠️  No GPU detected - will use CPU (slower)")
            return True
    except Exception as e:
        print(f"❌ Error checking GPU: {e}")
        return False


def test_ollama():
    """Test Ollama connection"""
    print("\n" + "=" * 60)
    print("🦙 Testing Ollama")
    print("=" * 60)

    try:
        from ollama_integration import OllamaIntegration

        ollama = OllamaIntegration()

        if ollama.check_ollama_available():
            print("✅ Ollama server is running")

            if ollama.check_model_available():
                print(f"✅ Model '{ollama.model}' is available")
                return True
            else:
                print(f"⚠️  Model '{ollama.model}' not found")
                print(f"   Run: ollama pull {ollama.model}")
                return False
        else:
            print("⚠️  Ollama not available")
            print("   Install: https://ollama.ai/download")
            return False

    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")
        return False


def test_camera():
    """Test camera availability"""
    print("\n" + "=" * 60)
    print("📷 Testing Camera")
    print("=" * 60)

    try:
        from camera_manager import CameraManager

        devices = CameraManager.list_cameras(max_index=5, backend="auto")

        available_cameras = [d for d in devices if d.get("available")]

        if available_cameras:
            print(f"✅ Found {len(available_cameras)} available camera(s)")
            for cam in available_cameras:
                print(f"   • Index {cam['index']}: {cam['width']}x{cam['height']} @ {cam['fps']}fps")
            return True
        else:
            print("⚠️  No cameras detected")
            print("   Check camera connections and permissions")
            return False

    except Exception as e:
        print(f"❌ Error testing camera: {e}")
        return False


def test_font():
    """Test font file availability"""
    print("\n" + "=" * 60)
    print("🔤 Testing Font")
    print("=" * 60)

    font_path = Path("assets/fonts/Acumin_Variable_Concept.ttf")

    if font_path.exists():
        print(f"✅ Custom font found: {font_path}")
        return True
    else:
        print(f"⚠️  Custom font not found: {font_path}")
        print("   System will use default font")
        return True  # Not critical, just a warning


def test_config():
    """Test configuration system"""
    print("\n" + "=" * 60)
    print("⚙️  Testing Configuration System")
    print("=" * 60)

    try:
        from config_manager import ConfigManager

        config_manager = ConfigManager()

        if config_manager.validate_config():
            print("✅ Configuration system OK")
            return True
        else:
            print("❌ Configuration validation failed")
            return False

    except Exception as e:
        print(f"❌ Error testing config: {e}")
        return False


def test_modules():
    """Test custom modules"""
    print("\n" + "=" * 60)
    print("📦 Testing Custom Modules")
    print("=" * 60)

    modules = [
        "src.config_manager",
        "src.ollama_integration",
        "src.caption_buffer",
        "src.multi_screen_display",
        "src.caption_engine_enhanced",
        "main",
    ]

    success = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} - OK")
        except Exception as e:
            print(f"❌ {module} - FAILED")
            print(f"   Error: {e}")
            success = False

    return success


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🚀 BLIP Camera Captioning - System Test")
    print("=" * 70)

    results = {
        "Imports": test_imports(),
        "GPU": test_gpu(),
        "Ollama": test_ollama(),
        "Camera": test_camera(),
        "Font": test_font(),
        "Config": test_config(),
        "Modules": test_modules(),
    }

    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15s}: {status}")

    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    print("\n" + "-" * 70)
    print(f"Total: {total} tests, {passed} passed, {failed} failed")
    print("=" * 70)

    # Recommendations
    print("\n💡 Recommendations:")

    if not results["Imports"]:
        print("❌ Install missing dependencies:")
        print("   pip install -r requirements.txt")

    if not results["Ollama"]:
        print("⚠️  For dual-interval mode, install Ollama:")
        print("   https://ollama.ai/download")
        print("   ollama pull llama3.2:3b")

    if not results["Camera"]:
        print("⚠️  Check camera connections and permissions")

    if not results["Font"]:
        print("ℹ️  Custom font not found (system will use default)")

    # Final verdict
    print("\n" + "=" * 70)

    critical_tests = ["Imports", "GPU", "Camera", "Config", "Modules"]
    critical_passed = all(results[t] for t in critical_tests if t in results)

    if critical_passed:
        print("✅ System is ready to run!")
        print("\nQuick start:")
        print("  python main.py --interactive")
        print("\nOr test with defaults:")
        print("  python main.py --show-camera")
    else:
        print("❌ System has critical issues - please fix errors above")
        sys.exit(1)

    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
