#!/usr/bin/env python3
"""
BLIP Model Management Module
Handles BLIP model loading, processing, and caption generation.
"""

import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import os

class BLIPModelManager:
    """Manages BLIP model loading and caption generation"""
    
    def __init__(self, model_name="Salesforce/blip-image-captioning-base"):
        self.model_name = model_name
        self.device = self._get_device()
        self.processor = None
        self.model = None
        
    def _get_device(self):
        """Determine the best available device"""
        if torch.cuda.is_available():
            device = "cuda"
            print(f"CUDA GPU detected: {torch.cuda.get_device_name(0)}")
            print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        elif torch.backends.mps.is_available():
            device = "mps"
            print("MPS (Apple Silicon) detected")
        else:
            device = "cpu"
            print("WARNING: No GPU detected, using CPU (slower)")
        return device
    
    def load_model(self):
        """Load BLIP model and processor"""
        print(f"Loading {self.model_name}...")
        print(f"Using device: {self.device}")
        
        try:
            # Load processor with fast tokenizer
            self.processor = BlipProcessor.from_pretrained(
                self.model_name, 
                use_fast=True
            )
            
            # Load model with appropriate settings for GPU acceleration
            model_dtype = torch.float16 if self.device in ["mps", "cuda"] else torch.float32
            self.model = BlipForConditionalGeneration.from_pretrained(
                self.model_name,
                torch_dtype=model_dtype,
                use_safetensors=True
            ).to(dtype=model_dtype)
            
            # Move model to GPU if available
            if self.device == "cuda":
                self.model = self.model.to(self.device)
                print(f"Model moved to GPU: {torch.cuda.get_device_name(0)}")
            elif self.device == "mps":
                self.model = self.model.to(self.device)
            
            print("Model loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def generate_caption(self, image):
        """Generate caption for the given image"""
        if not self.processor or not self.model:
            return "Error: Model not loaded"
        
        try:
            # Ensure image is PIL Image
            if hasattr(image, 'shape'):  # OpenCV frame
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(image_rgb)
            else:
                pil_image = image
            
            # Process with BLIP
            inputs = self.processor(images=pil_image, return_tensors="pt").to(self.device)
            
            # Generate caption
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs, 
                    max_length=50, 
                    num_beams=5,
                    do_sample=False
                )
            
            caption = self.processor.decode(outputs[0], skip_special_tokens=True)
            return caption
            
        except Exception as e:
            return f"Error generating caption: {e}"
    
    def get_model_info(self):
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "loaded": self.model is not None
        }

# Import cv2 here to avoid circular imports
import cv2
