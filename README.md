# TZ - The Lost War Robot 🤖

An interactive text adventure game with GUI interface, featuring an LLM-driven NPC dialogue system. Players engage in conversations with TZ, a memory-lost war robot, helping restore its memory and system functions through various technical puzzles.

---

## 🎮 Game Features

- **🧠 Intelligent NPC Dialogue**: Dynamic conversations powered by OpenAI API, with TZ exhibiting various emotional states and personality traits
- **🧩 Diverse Puzzles**: Technical challenges including path planning, frequency adjustment, password decryption, and logical reasoning
- **🌟 Branching Storylines**: Multiple endings based on player choices and performance
- **💭 Memory Fragment System**: AI-generated dynamic memory content for unique gameplay experiences
- **💻 Modern GUI Interface**: Elegant Tkinter-based chat interface with bubble conversations and status notifications

---

## 🛠️ Technology Stack

- **Python 3.7+** - Core programming language
- **Tkinter** - GUI framework
- **OpenAI Python SDK** - LLM API integration
- **Threading** - Asynchronous processing

### Supported AI Backends
- 🌐 **DeepSeek API** (online)
- 🌐 **OpenAI API** (online)
- 🏠 **Ollama** (local deployment)

---

## 📋 System Requirements

- **Python**: 3.7 or higher
- **OS**: Windows/macOS/Linux
- **Network**: Stable connection (for online APIs) or sufficient local resources (for Ollama)
- **Storage**: At least 100MB available disk space
- **Memory**: 8GB+ recommended when using Ollama for local AI models

---

## 🚀 Quick Start

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

- **GitHub Issues**: [Project Issues](https://github.com/yourusername/tz-lost-war-robot/issues)
- **Email**: your.email@example.com

---

**Enjoy your conversation journey with TZ!** 🤖✨