# TZ - The Lost War Robot 🤖

An interactive text adventure game with a GUI chat interface, featuring an LLM-driven NPC dialogue system. Players converse with **TZ**, a war robot who has lost parts of its memory and logic core, and help restore its systems through a series of technical puzzles and moral decisions.

The current **v1.0** release uses a **web-based cyber UI** (frontend + Flask backend) and also provides a packaged macOS app (`dist/TZ_War_Robot.app`) so the game can be played without setting up the development environment.

---

## 🎮 Game Features

- **🧠 Intelligent NPC Dialogue**  
  Dynamic conversations powered by OpenAI-compatible APIs (DeepSeek / OpenAI / Ollama), with configurable persona, emotion and intensity for TZ.

- **🧩 Structured Technical Puzzles**  
  A sequence of system-repair tasks, including:
  - Power path restoration  
  - Signal amplifier frequency calibration  
  - Code / password decryption  
  - Alien signal decoding  
  - Combat logic reconstruction

- **🌟 Branching Storylines**  
  A deviation value tracks the player’s decisions and performance, unlocking multiple endings and different attitudes from TZ.

- **💭 Memory Fragment System**  
  AI-generated memory clips that reflect the current game state, giving each playthrough slightly different narrative details.

- **💻 Modern GUI Interface**  
  A custom sci-fi chat UI in the browser (frontend) with bubble messages, status notifications, typing delays and timed message sequencing to preserve narrative rhythm.

- **📦 Packaged Desktop Build (macOS)**  
  A standalone `TZ_War_Robot.app` (PyInstaller + pywebview) in the `dist` folder for one-click play on macOS.

> Note: A legacy Tkinter prototype was used in earlier versions; the current 1.0 build is based on the web UI + Flask backend architecture.

---

## 🛠️ Technology Stack

- **Backend**
  - Python 3.9+ (tested)  
  - Flask – HTTP API and game session management  
  - Custom game state machine (`game_logic.py`, `task_handlers.py`, `memory_generator.py`, `stage_handlers.py`)  
  - OpenAI-compatible HTTP client (supports DeepSeek, OpenAI, Ollama, etc.)

- **Frontend**
  - Modern web stack (React-style SPA, built into `frontend/dist`)  
  - Chat-style layout with neon / cyberpunk theming

- **Desktop Packaging**
  - PyInstaller – builds `TZ_War_Robot.app` using `TZ_Game.spec`  
  - pywebview – opens the web UI in a native desktop window

---

## 📋 System Requirements

### Running the packaged macOS app

- **OS**: macOS (Apple Silicon or Intel)
- **Storage**: ~200 MB free disk space
- **Network**:  
  - Stable connection for online APIs (DeepSeek / OpenAI), or  
  - Sufficient local resources when using **Ollama** for on-device LLMs
- No separate Python / Node installation is required if you only use the packaged app in `dist/`.

### Running from source (development mode)

- **Python**: 3.9 or higher
- **Node.js + npm**: for building the frontend
- **OS**: Windows / macOS / Linux
- **Memory**: 8 GB+ recommended when using local LLMs (Ollama)
- See the “Local Development” section for detailed setup instructions.
---


## 🚀 Quick Start

### 🧪 Playing the packaged 1.0 build (macOS)

If you downloaded the final 1.0 release that already contains a `dist` folder, you can try the game **without installing Python or Node**:

1. Open the `dist` folder in Finder.
2. On macOS, double-click **`TZ_War_Robot.app`** to launch the game.
3. Scroll down to the **Security** section. You should see a message like  
      `“TZ_War_Robot.app” was blocked from use because it is not from an identified developer.`
4. Click **“Open Anyway”** (or **Allow**).
5. Go back to Finder and open `TZ_War_Robot.app` again, then click **Open** in the dialog.

The sections below describe how to run the game from source when you want to modify the code or rebuild the project.


### 1. Virtual Environment Setup (Recommended)

```bash
# Create virtual environment
python -m venv tz-env

# Activate virtual environment
# On Windows:
tz-env\Scripts\activate
# On macOS/Linux:
source tz-env/bin/activate

# Verify activation (should show your venv path)
which python
```

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/Tz476/YI_Ding_FINAL.git
cd YI_Ding_FINAL

# Install dependencies
pip install openai
# or
pip install -r requirements.txt
```

### 3. Configuration

Find and modify the following in `main.py`:

```python
client = OpenAI(
    api_key='your-api-key-here',  # Replace with your actual API key
    base_url="https://api.deepseek.com/v1"
)
```

### 4. Run the Game

```bash
python "main.py"
```

### 5. Deactivate Virtual Environment

When you're done playing, deactivate the virtual environment:
```bash
deactivate
```

⚠️ **Note**: Remember to reactivate the virtual environment (`tz-env\Scripts\activate` on Windows or `source tz-env/bin/activate` on macOS/Linux) every time you want to run the game!

---

## 🔑 API Configuration

### DeepSeek API (Recommended)
1. Visit [DeepSeek website](https://www.deepseek.com/)
2. Create account and obtain API key
3. Replace the key in the code

### OpenAI API
1. Modify `base_url` to `https://api.openai.com/v1`
2. Get API key from [OpenAI website](https://openai.com/)

### Ollama (Free Local Option)
1. Download and install [Ollama](https://ollama.ai/)
2. Pull a model: `ollama pull qwen:7b`
3. Update configuration (see Advanced Configuration)

⚠️ **Security Note**: Never commit real API keys to public repositories!

---

## 🎲 Game Flow

### Chapter 1: Exceptional Access
- Establish initial connection with TZ
- Identity verification and permission confirmation
- Understanding TZ's basic situation

### Chapter 2: Regression Logic
Fix 5 core system modules:
1. **⚡ Power Path Restoration** - Graph theory path planning
2. **📡 Signal Amplifier Calibration** - Frequency adjustment challenge
3. **🔐 Data Decryption Program** - Cryptography decryption
4. **👽 Alien Language Decoding** - Linguistic inference
5. **⚔️ Combat Logic Reconstruction** - Logical sequence sorting

### Chapter 3: Emotional Bias Emergence
- TZ develops self-awareness
- Memory fragment recovery and interpretation
- Moral and ethical choice emergence

### Chapter 4: Ultimate Decision
- Final outcome based on previous choices
- Multiple endings: Return to Command, Free Awakening, Coexistence Signal, Failure

---

## ⚙️ Advanced Configuration

### Using Ollama (Local AI)

#### Setup
```bash
# Install Ollama from https://ollama.ai/
# Pull recommended models
ollama pull qwen:7b      # Chinese-optimized
ollama pull llama2:7b    # English-focused
ollama pull mistral:7b   # Lightweight
```

#### Code Configuration
```python
# Replace OpenAI client configuration
client = OpenAI(
    api_key='ollama',  # Placeholder for Ollama
    base_url="http://localhost:11434/v1"
)

MODEL_NAME = "qwen:7b"  # Your installed model
```

#### Start Service
```bash
ollama serve  # Start Ollama service
ollama run qwen:7b "Hello"  # Test model
```

### Personality Customization
Available AI personalities:
- **Calm_Conscientious** - Technical and methodical
- **Empathic_Agreeable** - Cooperative and reassuring
- **Controlled_Anger** - Urgent but professional
- **Melancholic_Sober** - Reflective and measured

---

## 🎮 How to Play

### Controls
- **Input**: Type responses in the bottom text field
- **Send**: Press Enter to send messages
- **Exit**: Type `exit`, `bye`, `goodbye`, `quit`, or `q`

### Gameplay Tips
1. Follow TZ's instructions carefully
2. Make thoughtful choices at decision points
3. Solve technical puzzles step by step
4. Pay attention to TZ's emotional state changes

---

## 🐛 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **API Connection Failed** | Check network, verify API key, confirm service availability |
| **Chinese Display Issues** | Ensure UTF-8 encoding, check font files |
| **Program Unresponsive** | Check firewall settings, restart program |
| **Ollama Connection Failed** | Ensure `ollama serve` is running |
| **Model Not Found** | Verify installation with `ollama list` |
| **Slow Response** | Use lighter models or increase system memory |

### Error Logs
Check console output for detailed error messages and debugging information.

---

## 📁 Project Structure

```
tz-lost-war-robot/
├── main.py               # Main program file
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** your feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI/DeepSeek** for powerful AI model support
- **Python Tkinter Community** for GUI development resources
- **All testers and contributors** for feedback and improvements

---

## 📞 Contact

- **Email**: dingyi476@163.com
---

**Enjoy your conversation journey with TZ!** 🤖✨