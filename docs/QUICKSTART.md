# Quick Start Guide

Get up and running with BLIP Camera Captioning in 5 minutes!

---

## 🚀 Installation

### 1. Install Dependencies

```bash
# Activate your virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # macOS/Linux

# Install Python packages
pip install -r requirements.txt
```

### 2. Install Ollama (Optional, for dual-interval mode)

**Windows/macOS/Linux:**
1. Download from: https://ollama.ai/download
2. Install and run Ollama
3. Pull a model:
   ```bash
   ollama pull llama3.2:3b
   ```

---

## 🎮 Usage

### Method 1: Interactive Setup (Recommended)

```bash
python main.py --interactive
```

Follow the prompts to configure:
- Number of text screens
- BLIP model selection
- Camera settings
- Timing intervals
- Ollama integration

Your settings will be saved to `config.yaml` for future use.

---

### Method 2: Quick Start with Defaults

**Single screen, standard mode:**
```bash
python main.py
```

**Triple screen with BLIP-2:**
```bash
python main.py --screens 3 --blip2
```

**With dual-interval mode and Ollama:**
```bash
python main.py --screens 2 --dual-interval
```

---

### Method 3: Use Configuration File

```bash
# Copy example config
cp config.example.yaml config.yaml

# Edit config.yaml to your preferences
# Then run:
python main.py --config config.yaml
```

---

## 📋 Command-Line Options

### Configuration Mode
- `--interactive`, `-i` - Interactive setup wizard
- `--config FILE`, `-c FILE` - Load configuration from file

### Quick Options
- `--screens N` - Number of text screens (1-3)
- `--blip2` - Use BLIP-2 model (more accurate, slower)
- `--dual-interval` - Enable dual-interval mode with Ollama
- `--interval N` - Caption generation interval (seconds)

### Camera Options
- `--camera N` - Camera index (default: 0)
- `--list-cameras` - List available cameras
- `--auto-camera` - Auto-select first available camera
- `--show-camera` - Show camera feed window
- `--backend TYPE` - Camera backend (auto, dshow, msmf)

### System Options
- `--status` - Show system status and exit
- `--test-ollama` - Test Ollama connection and exit

---

## 🎯 Common Scenarios

### Scenario 1: Basic Usage
```bash
python main.py --show-camera --interval 5
```
- Single text screen
- BLIP model
- Camera feed visible
- Captions every 5 seconds

### Scenario 2: Multi-Screen Display
```bash
python main.py --screens 3 --camera 0
```
- 3 independent text screens
- Round-robin caption distribution
- Camera index 0

### Scenario 3: AI-Powered Summarization
```bash
python main.py --dual-interval --interval 3
```
- Short captions every 3 seconds
- AI summary every 30 seconds (default)
- Ollama integration enabled

### Scenario 4: High-Accuracy Mode
```bash
python main.py --blip2 --screens 2 --interval 10
```
- BLIP-2 model (better quality)
- 2 text screens
- Slower interval to accommodate processing

---

## ⚙️ Configuration Examples

### config.yaml - Minimal Setup
```yaml
display:
  text_screen_count: 1

model:
  type: "blip"

camera:
  index: 0

timing:
  dual_interval_mode: false
  interval_short: 5
```

### config.yaml - Advanced Setup
```yaml
display:
  text_screen_count: 3
  font_size: 28

model:
  type: "blip2"
  use_gpu: true

camera:
  index: 0
  show_camera: true

timing:
  dual_interval_mode: true
  interval_short: 3
  interval_long: 30

ollama:
  enabled: true
  model: "llama3.2:3b"
```

---

## 🔧 Troubleshooting

### Camera Not Found
```bash
# List available cameras
python main.py --list-cameras

# Try different camera index
python main.py --camera 1

# Try different backend (Windows)
python main.py --backend dshow
```

### Ollama Not Working
```bash
# Test Ollama connection
python main.py --test-ollama

# If test fails, check:
# 1. Is Ollama installed? https://ollama.ai/download
# 2. Is Ollama running?
# 3. Is the model downloaded? Run: ollama pull llama3.2:3b
```

### GPU Not Detected
```bash
# Check if CUDA is available
python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# For GPU setup, see: scripts/GPU_SETUP_GUIDE.md
```

### Font Not Loading
```bash
# Check font file exists
ls assets/fonts/Acumin_Variable_Concept.ttf

# System will fall back to default font if missing
```

---

## 🎨 Controls

- **Press `q`** in any window to quit
- **Press `Ctrl+C`** in terminal to stop

---

## 📊 Viewing Statistics

While running, the system will display:
- Number of captions generated
- Number of summaries created (dual-interval mode)
- Runtime duration
- Buffer status (dual-interval mode)

Press `Ctrl+C` to see final statistics.

---

## 💡 Tips

1. **First Time?** Use `--interactive` to configure everything properly
2. **Save Your Config:** Interactive mode saves to `config.yaml`
3. **Reuse Config:** Use `--config config.yaml` for consistent settings
4. **Start Simple:** Try single screen mode first before multi-screen
5. **GPU Recommended:** For BLIP-2 and multi-screen setups
6. **Test Ollama First:** Run `--test-ollama` before dual-interval mode

---

## 🆘 Getting Help

```bash
# Show all options
python main.py --help

# Check system status
python main.py --status

# Test components
python main.py --test-ollama
python main.py --list-cameras
```

---

**Ready to go!** Start with `python main.py --interactive` 🚀
