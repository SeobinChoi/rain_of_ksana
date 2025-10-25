#!/usr/bin/env python3
"""
Test GPU acceleration for BLIP models
"""

import torch
import time
from PIL import Image
import numpy as np

def test_gpu_acceleration():
    """Test GPU acceleration with a simple operation"""
    print("=== GPU Acceleration Test ===")
    
    # Check CUDA availability
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU name: {torch.cuda.get_device_name(0)}")
        print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        
        # Test tensor operations
        print("\nTesting tensor operations...")
        
        # CPU test
        start_time = time.time()
        cpu_tensor = torch.randn(1000, 1000)
        cpu_result = torch.mm(cpu_tensor, cpu_tensor)
        cpu_time = time.time() - start_time
        print(f"CPU operation time: {cpu_time:.4f} seconds")
        
        # GPU test
        start_time = time.time()
        gpu_tensor = torch.randn(1000, 1000).cuda()
        gpu_result = torch.mm(gpu_tensor, gpu_tensor)
        torch.cuda.synchronize()  # Wait for GPU to finish
        gpu_time = time.time() - start_time
        print(f"GPU operation time: {gpu_time:.4f} seconds")
        
        speedup = cpu_time / gpu_time
        print(f"GPU speedup: {speedup:.2f}x faster")
        
        # Test model loading
        print("\nTesting model loading...")
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            
            print("Loading BLIP model...")
            processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            
            # Move to GPU
            model = model.to("cuda")
            print("Model moved to GPU successfully!")
            
            # Test with dummy image
            dummy_image = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
            
            print("Testing caption generation...")
            start_time = time.time()
            inputs = processor(images=dummy_image, return_tensors="pt").to("cuda")
            
            with torch.no_grad():
                outputs = model.generate(**inputs, max_length=50, num_beams=5)
            
            caption = processor.decode(outputs[0], skip_special_tokens=True)
            generation_time = time.time() - start_time
            
            print(f"Generated caption: {caption}")
            print(f"Generation time: {generation_time:.4f} seconds")
            
        except Exception as e:
            print(f"Error testing model: {e}")
            
    else:
        print("No CUDA GPU available")

if __name__ == "__main__":
    test_gpu_acceleration()
