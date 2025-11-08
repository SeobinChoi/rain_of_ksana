# BLIP Camera Captioning System - Enhanced Edition

Real-time camera feed analysis with BLIP AI models, featuring multi-screen display, AI-powered text summarization, and advanced configuration options.

---

## ✨ Features

### Core Features
- **Real-time Image Captioning**: BLIP/BLIP-2 models
- **Multi-Screen Display**: Up to 3 independent text screens
- **AI Text Summarization**: Ollama LLM integration
- **Dual-Interval Mode**: Short captions → AI summary
- **GPU Acceleration**: CUDA/MPS auto-detection
- **Typing Animation**: Character-by-character text reveal
- **Vertical Text Layout**: Chinese classical document style
- **2K Resolution Support**: 2560x1440 high-resolution display

### Display Features
- Black background with white text
- Space → hyphen auto-conversion
- Right-to-left column layout
- New captions appear on the right
- Auto-scrolling when screen fills
- Independent caption queues per screen

### Advanced Features
- **Configuration System**: Interactive CLI setup
- **YAML/JSON Config**: Save and reuse settings
- **Ollama Integration**: LLM-powered text summarization
- **Caption Buffering**: Smart accumulation and timing
- **Round-Robin Distribution**: Automatic caption balancing across screens

---

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

### Basic Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run interactive setup
python main_enhanced.py --interactive
```

### Quick Examples
```bash
# Single screen, standard mode
python main_enhanced.py

# Triple screen with BLIP-2
python main_enhanced.py --screens 3 --blip2

# With AI summarization
python main_enhanced.py --dual-interval
```

---

## 📋 System Modes

### Single-Interval Mode (Standard)
```
Camera → BLIP Caption (every 5s) → Multi-Screen Display
```

**Use case**: Standard real-time captioning
**Best for**: Single continuous descriptions

### Dual-Interval Mode (AI-Enhanced)
```
Camera → BLIP Short Captions (every 3s)
      → Accumulate in Buffer
      → Ollama AI Summary (every 30s)
      → Coherent Narrative → Display
```

**Example**:
- Short captions: `"person at desk"`, `"typing on laptop"`, `"coffee cup nearby"`
- AI summary: `"A person sitting at their desk, working on a laptop while enjoying a cup of coffee"`

**Use case**: Natural, flowing descriptions
**Best for**: Storytelling, narrative descriptions

---

## ⚙️ Configuration

### Interactive Setup
```bash
python main_enhanced.py --interactive
```

Guided configuration wizard for:
- Text screen count (1-3)
- BLIP model selection
- Font size and animation speed
- Camera settings
- Timing intervals
- Ollama integration

### Configuration File
```yaml
display:
  text_screen_count: 3
  font_size: 24
  typing_speed: 0.03

model:
  type: "blip"         # or "blip2"
  use_gpu: "auto"

timing:
  dual_interval_mode: true
  interval_short: 3    # Caption generation
  interval_long: 30    # AI summarization

ollama:
  enabled: true
  model: "llama3.2:3b"
```

See [config.example.yaml](config.example.yaml) for full configuration options.

---

## 🎮 Command-Line Interface

### Configuration Mode
- `--interactive`, `-i` - Interactive setup wizard
- `--config FILE`, `-c FILE` - Load configuration file

### Quick Options
- `--screens N` - Number of text screens (1-3)
- `--blip2` - Use BLIP-2 model
- `--dual-interval` - Enable AI summarization mode
- `--interval N` - Caption interval (seconds)
- `--show-camera` - Show camera feed window

### Camera Options
- `--camera N` - Camera index
- `--list-cameras` - List available cameras
- `--auto-camera` - Auto-select camera
- `--backend TYPE` - Camera backend (auto, dshow, msmf)

### System Options
- `--status` - Show system status
- `--test-ollama` - Test Ollama connection

### Full Help
```bash
python main_enhanced.py --help
```

---

## 📦 Requirements

### Python Packages
```
Python 3.11+ (3.12 recommended)
PyTorch 2.0+
HuggingFace Transformers
OpenCV
Pillow
NumPy
PyYAML
requests
```

### Optional
- **Ollama** (for dual-interval mode): https://ollama.ai/download
- **CUDA** (for GPU acceleration): See [scripts/GPU_SETUP_GUIDE.md](scripts/GPU_SETUP_GUIDE.md)
- **Custom Font**: Acumin Variable Concept (included)

---

## 🏗️ Project Structure

```
rain_of_ksana/
├── main_enhanced.py              # Enhanced main entry point
├── caption_engine_enhanced.py    # Enhanced caption engine
├── config_manager.py             # Configuration system
├── ollama_integration.py         # Ollama LLM integration
├── caption_buffer.py             # Caption buffering system
├── multi_screen_display.py       # Multi-screen management
├── blip_model.py                 # BLIP model manager
├── blip2_model.py                # BLIP-2 model manager
├── camera_manager.py             # Camera management
├── dual_screen_display.py        # Legacy dual-screen display
├── config.example.yaml           # Example configuration
├── QUICKSTART.md                 # Quick start guide
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development tools
├── scripts/                      # Setup scripts
│   ├── GPU_SETUP_GUIDE.md
│   ├── install_gpu.bat
│   └── install_gpu_pytorch.py
├── docs/                         # Documentation
│   ├── FEATURE_PLAN.md
│   ├── IMPLEMENTATION_STATUS.md
│   └── DEVELOPMENT_SUMMARY.md
└── assets/
    └── fonts/
        └── Acumin_Variable_Concept.ttf
```

---

## 🎯 Usage Scenarios

### Scenario 1: Basic Captioning
```bash
python main_enhanced.py --show-camera --interval 5
```
- Single screen
- BLIP model
- Caption every 5 seconds
- Camera feed visible

### Scenario 2: Multi-Screen Exhibition
```bash
python main_enhanced.py --screens 3 --font-size 32
```
- 3 text screens
- Large font
- Round-robin caption distribution
- Installation/exhibition mode

### Scenario 3: AI-Enhanced Storytelling
```bash
python main_enhanced.py --dual-interval --screens 2
```
- 2 text screens
- Short captions every 3s
- AI-generated summary every 30s
- Coherent narrative mode

### Scenario 4: High-Accuracy Mode
```bash
python main_enhanced.py --blip2 --interval 10
```
- BLIP-2 model (better quality)
- Slower interval (10s)
- GPU acceleration recommended

---

## 🔧 Troubleshooting

### Camera Issues
```bash
# List cameras
python main_enhanced.py --list-cameras

# Try different camera
python main_enhanced.py --camera 1

# Try different backend (Windows)
python main_enhanced.py --backend dshow
```

### Ollama Issues
```bash
# Test connection
python main_enhanced.py --test-ollama

# If failed, install:
# 1. Download: https://ollama.ai/download
# 2. Install Ollama
# 3. Run: ollama pull llama3.2:3b
```

### GPU Not Working
```bash
# Check CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# See GPU setup guide
cat scripts/GPU_SETUP_GUIDE.md
```

### Font Not Loading
- Check file exists: `assets/fonts/Acumin_Variable_Concept.ttf`
- System will use default font if missing

---

## 🧪 Testing

### Test Individual Modules
```bash
# Configuration system
python config_manager.py

# Ollama integration
python ollama_integration.py

# Caption buffer
python caption_buffer.py

# Multi-screen display
python multi_screen_display.py
```

### System Tests
```bash
# Full system status
python main_enhanced.py --status

# Test Ollama
python main_enhanced.py --test-ollama

# List cameras
python main_enhanced.py --list-cameras
```

---

## 📊 Performance

### Recommended Specifications

**Minimum**:
- CPU: Quad-core
- RAM: 8 GB
- GPU: Integrated (CPU mode)
- Display: 1080p

**Recommended**:
- CPU: 6-core or better
- RAM: 16 GB
- GPU: NVIDIA (4GB+ VRAM) or Apple Silicon
- Display: 2K or 4K

### Performance Tips
1. Use GPU acceleration (auto-detected)
2. Start with BLIP (faster than BLIP-2)
3. Use 1-2 screens on lower-end systems
4. Increase interval for slower systems
5. Close other applications for best performance

---

## 🦙 Ollama Models

### Supported Models
- **llama3.2:3b** - Lightweight (3B params, ~2GB)
  - Fast, multilingual
  - Best for most use cases

- **llama3.1:8b** - Medium (8B params, ~4.7GB)
  - Better quality
  - Requires more resources

- **qwen2.5:7b** - Medium (7B params, ~4.4GB)
  - Multilingual optimized
  - Good for non-English

### Installing Models
```bash
# Download a model
ollama pull llama3.2:3b

# List installed models
ollama list

# Test a model
ollama run llama3.2:3b
```

---

## 🎨 Customization

### Display Settings
- Window size: 2K (2560x1440) or 4K (3840x2160)
- Font size: 12-48 pixels
- Typing speed: 0.01-0.1 seconds per character
- Column spacing: Adjustable
- Character spacing: Adjustable

### Timing Settings
- Short interval: 1-60 seconds
- Long interval: 10-300 seconds
- Customizable per use case

### Prompt Template
Customize the AI summarization prompt in `config.yaml`:
```yaml
ollama:
  prompt_template: |
    Your custom prompt here.
    Use {captions} placeholder for caption list.
```

---

## 🔐 Privacy & Security

- **Local Processing**: All AI runs locally (BLIP models)
- **Optional Ollama**: Also runs locally if used
- **No Cloud**: No data sent to external servers
- **No Analytics**: No tracking or telemetry

---

## 📝 License

This project is created for educational and research purposes.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [config.example.yaml](config.example.yaml) - Configuration example
- [scripts/GPU_SETUP_GUIDE.md](scripts/GPU_SETUP_GUIDE.md) - GPU setup
- [docs/FEATURE_PLAN.md](docs/FEATURE_PLAN.md) - Feature planning
- [docs/DEVELOPMENT_SUMMARY.md](docs/DEVELOPMENT_SUMMARY.md) - Development notes

---

## 🆘 Support

- Issues: Report bugs via GitHub Issues
- Documentation: See docs/ directory
- Examples: See QUICKSTART.md

---

## 🎉 Acknowledgments

- **BLIP/BLIP-2**: Salesforce Research
- **Ollama**: Ollama team
- **PyTorch**: Meta AI
- **HuggingFace**: Transformers library

---

**🚀 Ready to start? Run `python main_enhanced.py --interactive`**
