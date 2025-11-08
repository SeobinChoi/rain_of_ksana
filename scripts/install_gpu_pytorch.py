#!/usr/bin/env python3
"""
GPU PyTorch Installation Script
Installs CUDA-enabled PyTorch for GPU acceleration
"""

import subprocess
import sys
import platform

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_cuda():
    """Check if CUDA is available"""
    print("🔍 Checking CUDA installation...")
    
    # Check nvidia-smi
    success, stdout, stderr = run_command("nvidia-smi")
    if success:
        print("✅ NVIDIA GPU detected")
        print(stdout.split('\n')[0])  # Show first line with driver info
        return True
    else:
        print("❌ NVIDIA GPU not detected or drivers not installed")
        print("Please install NVIDIA drivers and CUDA toolkit")
        return False

def install_gpu_pytorch():
    """Install CUDA-enabled PyTorch"""
    print("\n🚀 Installing CUDA-enabled PyTorch...")
    
    # Uninstall existing PyTorch if any
    print("🗑️  Uninstalling existing PyTorch...")
    run_command("pip uninstall torch torchvision torchaudio -y")
    
    # Install CUDA-enabled PyTorch
    print("📦 Installing CUDA 12.1 PyTorch...")
    command = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
    
    success, stdout, stderr = run_command(command)
    
    if success:
        print("✅ PyTorch with CUDA support installed successfully!")
        return True
    else:
        print("❌ Failed to install PyTorch with CUDA support")
        print(f"Error: {stderr}")
        return False

def verify_installation():
    """Verify PyTorch CUDA installation"""
    print("\n🔍 Verifying installation...")
    
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"✅ CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"✅ CUDA version: {torch.version.cuda}")
            print(f"✅ GPU count: {torch.cuda.device_count()}")
            print(f"✅ GPU name: {torch.cuda.get_device_name(0)}")
            print(f"✅ GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            return True
        else:
            print("❌ CUDA not available in PyTorch")
            return False
            
    except ImportError:
        print("❌ PyTorch not installed")
        return False

def main():
    """Main installation process"""
    print("🚀 GPU PyTorch Installation Script")
    print("=" * 50)
    
    # Check CUDA
    if not check_cuda():
        print("\n❌ Cannot proceed without CUDA support")
        return False
    
    # Install PyTorch
    if not install_gpu_pytorch():
        print("\n❌ Installation failed")
        return False
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Verification failed")
        return False
    
    print("\n🎉 GPU PyTorch installation completed successfully!")
    print("You can now run BLIP-2 with GPU acceleration!")
    return True

if __name__ == "__main__":
    main()
