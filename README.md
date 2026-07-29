# Zeus

<div align="center">

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=28&duration=3000&pause=1000&color=3B8ED0&center=true&vCenter=true&width=500&lines=Zeus+Agent+v1.0.1)](https://github.com/Taha-Azadi/TD-Zeus-Agent)

<p>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4B0082?style=for-the-badge" alt="Platform"></a>
  <a href="#"><img src="https://img.shields.io/badge/AI-OpenRouter-FF6B6B?style=for-the-badge" alt="AI"></a>
</p>

<img src="screenshots/banner.png" alt="Zeus Agent Banner" width="800"/>

<p><b>A voice-enabled AI agent with tool-calling capabilities.</b></p>

<p>
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#tools">Tools</a> •
  <a href="#tech-stack">Tech Stack</a>
</p>

</div>

---

## Features

- **Voice Interface** — Hands-free control using speech recognition and text-to-speech
- **AI-Powered Conversations** — Streaming responses via OpenRouter (NVIDIA Nemotron and other models)
- **Tool Calling** — Execute shell commands, manage files, capture screenshots, and control applications through natural language
- **Web Navigation** — Open websites by voice or text command
- **Music Player** — Launch local music files on demand
- **Rich Terminal Output** — Formatted markdown rendering with syntax highlighting

---

## Tools

Zeus v1.0.1 can invoke the following tools autonomously based on your requests:

| Tool | Description |
|------|-------------|
| `run_shell_command` | Execute terminal commands with 30-second timeout |
| `list_directory` | Browse files and folders with size metadata |
| `read_file_content` | Inspect text files (up to 8,000 characters) |
| `write_file_content` | Create or overwrite files |
| `get_system_info` | Monitor CPU, RAM, disk usage, and OS details |
| `take_screenshot` | Capture and save screen images |
| `open_application` | Launch applications by name |
| `open_website` | Navigate to supported websites |
| `play_music` | Play local audio files |
| `get_current_time` | Retrieve current date and time |

---

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Quick Install
```bash
git clone https://github.com/Taha-Azadi/TD-Zeus-Agent
cd TD-Zeus-Agent
python install.py
```

### Manual Install
```bash
pip install -r requirements.txt
```

> **Linux users:** Install PortAudio before running the installer:
> ```bash
> sudo apt install portaudio19-dev
> ```

---

## Usage

### First Run
```bash
python main.py
```

On first launch, Zeus will:
1. Verify your OpenRouter API key
2. Ask for your preferred name (optional)

### Interaction Modes

| Command | Action |
|---------|--------|
| `speak` | Voice-controlled mode (microphone input, TTS output) |
| `type` | Text-controlled mode (keyboard input, terminal output) |

### Built-in Commands

| Phrase | Function |
|--------|----------|
| `open <website>` | Launch supported sites (YouTube, GitHub, Google, etc.) |
| `open <music>` | Play local audio files |
| `the time` / `time is` | Display current time |
| `clear` / `cls` | Clear terminal screen |
| `hello` / `hi` | Greeting response |
| `hey Zeus` / `Zeus` | Wake phrase |
| `bye` | Exit application |

---

## Tech Stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,git,github,vscode&theme=dark" />
</p>

| Technology | Purpose |
|------------|---------|
| Python 3.9+ | Core runtime |
| OpenAI API | LLM integration via OpenRouter |
| SpeechRecognition | Voice input processing |
| PyAudio | Audio stream capture |
| pyttsx3 | Text-to-speech output |
| Rich | Terminal formatting and markdown rendering |
| Colorama | Cross-platform colored output |
| pyautogui | Screenshot automation |
| psutil | System metrics collection |
| pywin32 | Windows COM integration |

---

## Project Structure

```
TD-Zeus-Agent/
├── main.py                 # Entry point with animated boot sequence
├── install.py              # Cross-platform dependency installer
├── requirements.txt        # Python package manifest
├── LICENSE                 # MIT License
├── README.md               # This file
├── screenshots/            # Application screenshots
│   └── banner.png
├── src/
│   ├── speak.py            # Voice interaction handler
│   ├── type.py             # Text interaction handler
│   └── utils.py            # Tool implementations, AI streaming, site mappings
└── docs/
    └── usage.md            # Extended documentation
```

---

## Configuration

| File | Purpose |
|------|---------|
| `ai.txt` | OpenRouter API key storage |
| `ask2.txt` | User name preference |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m 'Add YourFeature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

## Built by [Taha Azadi](https://github.com/Taha-Azadi)

<p>
  <a href="https://github.com/Taha-Azadi"><img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a>
  <a href="https://x.com/TahaAzadiDev"><img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" alt="Twitter"></a>
  <a href="https://www.linkedin.com/in/Taha-Azadi-Dev"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
  <a href="mailto:taha.azadi.dev@gmail.com"><img src="https://img.shields.io/badge/Email-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"></a>
</p>

</div>
