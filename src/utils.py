import webbrowser
from random import choice as rchoice
import speech_recognition as sr
import win32com.client
import subprocess, sys, os
import difflib, datetime
import platform
import pyttsx3
import requests
from colorama import Fore
import json
import threading
import itertools
from pathlib import Path
import time as _time

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.live import Live
    _HAS_RICH = True
    console = Console()
except ImportError:
    _HAS_RICH = False
    console = None



# ==================== TOOLS SCHEMA ====================

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Execute a shell command on the computer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "cwd": {"type": "string"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and folders in a directory.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "default": "."}},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_content",
            "description": "Read a text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "max_chars": {"type": "integer", "default": 8000}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file_content",
            "description": "Write or overwrite a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Get CPU, RAM, disk, and OS info.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Take a screenshot.",
            "parameters": {
                "type": "object",
                "properties": {"save_path": {"type": "string", "default": "screenshot.png"}},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Open an app by name.",
            "parameters": {
                "type": "object",
                "properties": {"app_name": {"type": "string"}},
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Play a music file by name.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_website",
            "description": "Open a website.",
            "parameters": {
                "type": "object",
                "properties": {"site_name": {"type": "string"}},
                "required": ["site_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get current date/time.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]


# ==================== TOOL IMPLEMENTATIONS ====================

def run_shell_command(command, cwd=None):
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=30, encoding='utf-8', errors='ignore'
        )
        out = result.stdout.strip() if result.stdout.strip() else "[No output]"
        err = result.stderr.strip() if result.stderr.strip() else ""
        return f"Exit: {result.returncode}\n{out}" + (f"\nErr: {err}" if err else "")
    except subprocess.TimeoutExpired:
        return "Timed out after 30s"
    except Exception as e:
        return f"Error: {e}"


def list_directory(path="."):
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"Not found: {path}"
        lines = []
        for item in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            icon = "📁" if item.is_dir() else "📄"
            size = f" ({item.stat().st_size:,}B)" if item.is_file() else ""
            lines.append(f"{icon} {item.name}{size}")
        return "\n".join(lines) if lines else "Empty"
    except Exception as e:
        return f"Error: {e}"


def read_file_content(filepath, max_chars=8000):
    try:
        p = Path(filepath).expanduser()
        if not p.exists():
            return f"Not found: {filepath}"
        text = p.read_text(encoding='utf-8', errors='ignore')
        if len(text) > max_chars:
            text = text[:max_chars] + f"\n... [truncated, total {len(text):,} chars]"
        return text
    except Exception as e:
        return f"Error: {e}"


def write_file_content(filepath, content):
    try:
        p = Path(filepath).expanduser()
        p.write_text(content, encoding='utf-8')
        return f"Saved: {p}"
    except Exception as e:
        return f"Error: {e}"


def get_system_info():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return (f"OS: {platform.system()} {platform.release()}\n"
                f"CPU: {cpu}% | Cores: {psutil.cpu_count()}\n"
                f"RAM: {mem.percent}% | {mem.used//1024//1024:,}MB / {mem.total//1024//1024:,}MB\n"
                f"Disk: {disk.percent}% | {disk.used//1024//1024//1024:,}GB / {disk.total//1024//1024//1024:,}GB")
    except ImportError:
        return f"OS: {platform.system()} {platform.release()}\nInstall psutil for full stats"
    except Exception as e:
        return f"Error: {e}"


def take_screenshot(save_path="screenshot.png"):
    try:
        import pyautogui
        img = pyautogui.screenshot()
        full = Path(save_path).expanduser().resolve()
        img.save(str(full))
        return f"Screenshot: {full}"
    except ImportError:
        return "Install pyautogui"
    except Exception as e:
        return f"Error: {e}"


def open_application(app_name):
    try:
        s = platform.system()
        if s == "Windows":
            os.system(f'start "" "{app_name}"')
        elif s == "Linux":
            subprocess.Popen([app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif s == "Darwin":
            subprocess.Popen(["open", "-a", app_name])
        return f"Opened: {app_name}"
    except Exception as e:
        return f"Error: {e}"


def open_website(site_name):
    import webbrowser
    site_map = {
        "youtube": "https://youtube.com", "google": "https://google.com",
        "github": "https://github.com", "stackoverflow": "https://stackoverflow.com",
        "reddit": "https://reddit.com", "twitter": "https://twitter.com",
        "facebook": "https://facebook.com", "instagram": "https://instagram.com",
        "linkedin": "https://linkedin.com", "netflix": "https://netflix.com",
        "amazon": "https://amazon.com", "spotify": "https://spotify.com",
        "discord": "https://discord.com", "gmail": "https://mail.google.com",
        "drive": "https://drive.google.com", "wikipedia": "https://en.wikipedia.org",
    }
    url = site_map.get(site_name.lower())
    if url:
        webbrowser.open(url)
        return f"Opened {site_name}"
    return f"Unknown site. Known: {', '.join(site_map.keys())}"


def get_current_time():
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def execute_tool(name, arguments):
    tools = {
        "run_shell_command": run_shell_command,
        "list_directory": list_directory,
        "read_file_content": read_file_content,
        "write_file_content": write_file_content,
        "get_system_info": get_system_info,
        "take_screenshot": take_screenshot,
        "open_application": open_application,
        "play_music": play_music,
        "open_website": open_website,
        "get_current_time": get_current_time,
    }
    func = tools.get(name)
    if not func:
        return f"Tool '{name}' not found."
    try:
        return func(**arguments)
    except Exception as e:
        return f"Error in {name}: {e}"


# ==================== STREAMING + TOOLS ====================

def _stream_chat_completion(payload, on_token, on_thinking_done=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers, json=payload, stream=True, timeout=60
    )
    if response.status_code == 401:
        raise PermissionError("Invalid API Key (401)")
    elif response.status_code != 200:
        raise ConnectionError(f"HTTP {response.status_code}: {response.text[:200]}")

    full_text = ""
    full_thinking = ""
    in_thinking = False
    tool_calls_buffer = []
    thinking_done_called = False

    for line in response.iter_lines():
        if not line:
            continue
        decoded = line.decode('utf-8')
        if not decoded.startswith('data: '):
            continue
        data_str = decoded[6:]
        if data_str.strip() == '[DONE]':
            break
        try:
            chunk = json.loads(data_str)
            delta = chunk.get('choices', [{}])[0].get('delta', {})

            tc_delta = delta.get('tool_calls')
            if tc_delta:
                for tc in tc_delta:
                    idx = tc.get('index', 0)
                    while len(tool_calls_buffer) <= idx:
                        tool_calls_buffer.append({"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                    if tc.get('id'):
                        tool_calls_buffer[idx]['id'] += tc['id']
                    if tc.get('type'):
                        tool_calls_buffer[idx]['type'] = tc['type']
                    func = tc.get('function', {})
                    if func.get('name'):
                        tool_calls_buffer[idx]['function']['name'] += func['name']
                    if func.get('arguments'):
                        tool_calls_buffer[idx]['function']['arguments'] += func['arguments']
                continue

            reasoning = delta.get('reasoning') or delta.get('reasoning_content')
            if reasoning:
                full_thinking += reasoning
                in_thinking = True
                continue

            content = delta.get('content', '')
            if content:
                if in_thinking and on_thinking_done and not thinking_done_called:
                    on_thinking_done(full_thinking)
                    thinking_done_called = True
                in_thinking = False
                full_text += content
                on_token(content, full_text)

        except json.JSONDecodeError:
            continue

    if in_thinking and on_thinking_done and not thinking_done_called:
        on_thinking_done(full_thinking)

    return full_text, full_thinking, tool_calls_buffer


def _run_conversation_with_tools(messages, model="nvidia/nemotron-3-ultra-550b-a55b:free",
                                  on_token=None, on_thinking_done=None, max_iterations=5):
    iteration = 0
    final_content = ""
    final_thinking = ""

    while iteration < max_iterations:
        iteration += 1

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "stream": True,
            "tools": TOOLS_SCHEMA,
            "tool_choice": "auto",
        }

        content, thinking, tool_calls = _stream_chat_completion(
            payload, on_token or (lambda t, f: None), on_thinking_done
        )
        final_content = content
        final_thinking += thinking

        if not tool_calls:
            break

        messages.append({
            "role": "assistant",
            "content": content or "",
            "tool_calls": tool_calls
        })

        for tc in tool_calls:
            name = tc['function']['name']
            args_str = tc['function']['arguments']
            try:
                args = json.loads(args_str) if args_str else {}
            except json.JSONDecodeError:
                args = {}

            console.print(f"\n[bold yellow]🔧 {name}({json.dumps(args, ensure_ascii=False)[:80]})[/bold yellow]")
            result = execute_tool(name, args)
            console.print(f"[dim]📤 {str(result)[:500]}{'...' if len(str(result))>500 else ''}[/dim]\n")

            messages.append({
                "role": "tool",
                "tool_call_id": tc['id'],
                "name": name,
                "content": str(result)
            })

    return final_content, final_thinking

# ==================== SPINNER ====================

def _thinking_spinner():
    thinking_done = threading.Event()

    def worker():
        chars = itertools.cycle(['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'])
        while not thinking_done.is_set():
            sys.stdout.write(f"\r\033[90m🧠 Thinking {next(chars)}\033[0m")
            sys.stdout.flush()
            _time.sleep(0.06)
        sys.stdout.write("\r" + " "*30 + "\r")
        sys.stdout.flush()

    t = threading.Thread(target=worker)
    t.start()
    return thinking_done, t


# ==================== AI FUNCTIONS ====================


def ai_speak(self):
    md_buffer = [""]

    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You ARE Zeus Agent — created by Taha-Azadi. "
                    "You have FULL ACCESS to the user's computer via tools. "
                    "Use tools when needed. Respond as Zeus Agent with Markdown."
                ),
            },
            {"role": "user", "content": f"My name is {self.name}.\n\n{self.text}"},
        ]

        md = Markdown("")
        panel = Panel(
            md,
            title="[bold cyan]Zeus Agent[/]",
            border_style="cyan",
            subtitle="⚡ Live Stream",
            padding=(1, 2)
        )

        def on_thinking_done(thinking):
            if thinking:
                console.print(f"\n[dim]💭 {thinking[:300]}{'...' if len(thinking)>300 else ''}[/dim]\n")

        def on_token(token, full):
            md_buffer[0] += token
            new_md = Markdown(md_buffer[0])
            new_panel = Panel(
                new_md,
                title="[bold cyan]Zeus Agent[/]",
                border_style="cyan",
                subtitle="⚡ Live Stream",
                padding=(1, 2)
            )
            live.update(new_panel)

        with console.status("[bold cyan]🧠 Thinking...[/bold cyan]", spinner="dots"):
            with Live(panel, console=console, refresh_per_second=20, vertical_overflow="visible") as live:
                full_content, _ = _run_conversation_with_tools(
                    messages, on_token=on_token, on_thinking_done=on_thinking_done
                )

        console.print()

        if full_content:
            say(full_content)

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")


def ai_type(self):
    md_buffer = [""]

    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You ARE Zeus Agent — created by Taha-Azadi. "
                    "You have FULL ACCESS to the user's computer via tools. "
                    "Think step by step. Use Markdown."
                ),
            },
            {"role": "user", "content": f"My name is {self.name}.\n\n{self.text}"},
        ]

        md = Markdown("")
        panel = Panel(
            md,
            title="[bold cyan]Zeus Agent[/]",
            border_style="cyan",
            subtitle="⚡ Live Stream",
            padding=(1, 2)
        )

        def on_thinking_done(thinking):
            if thinking:
                console.print(f"\n[dim]💭 {thinking[:300]}{'...' if len(thinking)>300 else ''}[/dim]\n")

        def on_token(token, full):
            md_buffer[0] += token
            new_md = Markdown(md_buffer[0])
            new_panel = Panel(
                new_md,
                title="[bold cyan]Zeus Agent[/]",
                border_style="cyan",
                subtitle="⚡ Live Stream",
                padding=(1, 2)
            )
            live.update(new_panel)

        with console.status("[bold cyan]🧠 Thinking...[/bold cyan]", spinner="dots"):
            with Live(panel, console=console, refresh_per_second=20, vertical_overflow="visible") as live:
                full_content, _ = _run_conversation_with_tools(
                    messages, on_token=on_token, on_thinking_done=on_thinking_done
                )

        console.print()

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")

# ==================== PRINT HELPERS ====================

def _print_md(text: str, title: str = "Zeus Agent"):
    if _HAS_RICH:
        md = Markdown(text)
        console.print(Panel(md, title=f"[bold cyan]{title}[/]", border_style="cyan"))
    else:
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}")
        print(text)
        print(f"{'='*50}\n")


def _print_error(msg: str):
    if _HAS_RICH:
        console.print(f"[bold red]❌ {msg}[/]")
    else:
        print(f"❌ {msg}")


def _print_warn(msg: str):
    if _HAS_RICH:
        console.print(f"[bold yellow]⚠️ {msg}[/]")
    else:
        print(f"⚠️ {msg}")


# ==================== SETUP ====================

with open("ai.txt", "r") as r:
    re = r.read()

API_KEY = re
USER_PATH = os.path.expanduser("~")

MUSIC_EXTENSIONS = (".mp3", ".wav", ".m4a", ".flac", ".ogg")


def clear():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"""
    {Fore.YELLOW}
╶─╮   ╭─╴   ╷ ╷   ╭─╮      ╭─╮   ╭─╴   ╭─╴   ╭╮╷   ╶┬╴
╭─╯   ├╴    │ │   ╰─╮      ├─┤   │╶╮   ├╴    │╰┤    │
╰─╴   ╰─╴   ╰─╯   ╰─╯      ╵ ╵   ╰─╯   ╰─╴   ╵ ╵    ╵
                           ╔══════════════════════════════════╗
╔══════════════════════════╝══════════════════════════════════╝══════════════════════════╗
║                         for clear Enter clear or say clear                             ║
║                     for edit api key go to ai.txt and edit this                        ║
║                   for edit your name go to ask2.txt and edit this                      ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
{Fore.RESET}
""")


def get_all_music():
    songs = []
    skip_dirs = {
        "AppData", "node_modules", "__pycache__",
        ".cache", ".local", "Library",
        ".npm", ".pip", "venv", ".venv", "env"
    }

    for root, dirs, files in os.walk(USER_PATH):
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if file.lower().endswith(MUSIC_EXTENSIONS):
                songs.append(os.path.join(root, file))

    return songs


def find_music(name):
    songs = get_all_music()

    if not songs:
        return None

    name = name.lower()

    for song in songs:
        filename = os.path.basename(song).lower()

        if name in filename:
            return song

    music_names = [os.path.splitext(os.path.basename(x))[0].lower() for x in songs]

    result = difflib.get_close_matches(name, music_names, n=1, cutoff=0.25)

    if result:
        index = music_names.index(result[0])
        return songs[index]

    return None


def open_file(path):
    system = platform.system()

    if system == "Windows":
        os.startfile(path)

    elif system == "Linux":
        subprocess.Popen(["xdg-open", path])

    elif system == "Darwin":
        subprocess.Popen(["open", path])


current_music = None


def play_music(name):
    music = find_music(name)

    if music:
        print(f"Zeus: Playing {music}")

        open_file(music)

        return True

    return False


sites = [
    ["youtube", "https://www.youtube.com"],
    ["wikipedia", "https://en.wikipedia.org"],
    ["google", "https://www.google.com"],
    ["zero day", "https://zerodey.ir"],
    ["github", "https://github.com"],
    ["stackoverflow", "https://stackoverflow.com"],
    ["reddit", "https://www.reddit.com"],
    ["twitter", "https://twitter.com"],
    ["facebook", "https://www.facebook.com"],
    ["instagram", "https://www.instagram.com"],
    ["linkedin", "https://www.linkedin.com"],
    ["netflix", "https://www.netflix.com"],
    ["amazon", "https://www.amazon.com"],
    ["ebay", "https://www.ebay.com"],
    ["spotify", "https://www.spotify.com"],
    ["apple", "https://www.apple.com"],
    ["microsoft", "https://www.microsoft.com"],
    ["slack", "https://slack.com"],
    ["discord", "https://discord.com"],
    ["twitch", "https://www.twitch.tv"],
    ["pinterest", "https://www.pinterest.com"],
    ["tumblr", "https://www.tumblr.com"],
    ["medium", "https://medium.com"],
    ["quora", "https://www.quora.com"],
    ["dropbox", "https://www.dropbox.com"],
    ["google drive", "https://drive.google.com"],
    ["gmail", "https://mail.google.com"],
    ["outlook", "https://outlook.live.com"],
    ["yahoo mail", "https://mail.yahoo.com"],
    ["bing", "https://www.bing.com"],
    ["duckduckgo", "https://duckduckgo.com"],
    ["gitlab", "https://gitlab.com"],
    ["bitbucket", "https://bitbucket.org"],
    ["npm", "https://www.npmjs.com"],
    ["pypi", "https://pypi.org"],
    ["docker hub", "https://hub.docker.com"],
    ["kubernetes", "https://kubernetes.io"],
    ["mozilla", "https://www.mozilla.org"],
    ["w3schools", "https://www.w3schools.com"],
    ["mdn web docs", "https://developer.mozilla.org"],
    ["can i use", "https://caniuse.com"],
    ["css tricks", "https://css-tricks.com"],
    ["dribbble", "https://dribbble.com"],
    ["behance", "https://www.behance.net"],
    ["figma", "https://www.figma.com"],
    ["unsplash", "https://unsplash.com"],
    ["pexels", "https://www.pexels.com"],
    ["pixabay", "https://pixabay.com"],
    ["google fonts", "https://fonts.google.com"],
    ["fontawesome", "https://fontawesome.com"],
    ["stripe", "https://stripe.com"],
    ["paypal", "https://www.paypal.com"],
    ["shopify", "https://www.shopify.com"],
    ["wordpress", "https://wordpress.org"],
    ["wix", "https://www.wix.com"],
    ["squarespace", "https://www.squarespace.com"],
    ["notion", "https://www.notion.so"],
    ["trello", "https://trello.com"],
    ["asana", "https://asana.com"],
    ["jira", "https://www.atlassian.com/software/jira"],
    ["confluence", "https://www.atlassian.com/software/confluence"],
    ["zoom", "https://zoom.us"],
    ["skype", "https://www.skype.com"],
    ["telegram", "https://telegram.org"],
    ["whatsapp", "https://www.whatsapp.com"],
    ["signal", "https://signal.org"],
    ["vivaldi", "https://vivaldi.com"],
    ["opera", "https://www.opera.com"],
    ["brave", "https://brave.com"],
    ["tor project", "https://www.torproject.org"],
    ["archive.org", "https://archive.org"],
    ["pastebin", "https://pastebin.com"],
    ["hacker news", "https://news.ycombinator.com"],
    ["product hunt", "https://www.producthunt.com"],
    ["indie hackers", "https://www.indiehackers.com"],
    ["dev.to", "https://dev.to"],
    ["hashnode", "https://hashnode.com"],
    ["freecodecamp", "https://www.freecodecamp.org"],
    ["codecademy", "https://www.codecademy.com"],
    ["coursera", "https://www.coursera.org"],
    ["udemy", "https://www.udemy.com"],
    ["edx", "https://www.edx.org"],
    ["khan academy", "https://www.khanacademy.org"],
    ["udacity", "https://www.udacity.com"],
    ["pluralsight", "https://www.pluralsight.com"],
    ["skillshare", "https://www.skillshare.com"],
    ["linkedin learning", "https://www.linkedin.com/learning"],
    ["arxiv", "https://arxiv.org"],
    ["google scholar", "https://scholar.google.com"],
    ["pubmed", "https://pubmed.ncbi.nlm.nih.gov"],
    ["ieee xplore", "https://ieeexplore.ieee.org"],
    ["springer", "https://link.springer.com"],
    ["nature", "https://www.nature.com"],
    ["science", "https://www.science.org"],
    ["reuters", "https://www.reuters.com"],
    ["bbc", "https://www.bbc.com"],
    ["cnn", "https://www.cnn.com"],
    ["the guardian", "https://www.theguardian.com"],
    ["the new york times", "https://www.nytimes.com"],
    ["the washington post", "https://www.washingtonpost.com"],
    ["al jazeera", "https://www.aljazeera.com"],
    ["associated press", "https://apnews.com"],
    ["bloomberg", "https://www.bloomberg.com"],
    ["forbes", "https://www.forbes.com"],
    ["the verge", "https://www.theverge.com"],
    ["wired", "https://www.wired.com"],
    ["techcrunch", "https://techcrunch.com"],
    ["engadget", "https://www.engadget.com"],
    ["ars technica", "https://arstechnica.com"],
    ["slashdot", "https://slashdot.org"],
    ["lifehacker", "https://lifehacker.com"],
    ["gizmodo", "https://gizmodo.com"],
    ["mashable", "https://mashable.com"],
    ["cnet", "https://www.cnet.com"],
    ["pcmag", "https://www.pcmag.com"],
    ["tom's hardware", "https://www.tomshardware.com"],
    ["anandtech", "https://www.anandtech.com"],
    ["linus tech tips", "https://linustechtips.com"],
    ["xkcd", "https://xkcd.com"],
    ["dilbert", "https://dilbert.com"],
    ["imdb", "https://www.imdb.com"],
    ["rotten tomatoes", "https://www.rottentomatoes.com"],
    ["letterboxd", "https://letterboxd.com"],
    ["goodreads", "https://www.goodreads.com"],
    [" audible", "https://www.audible.com"],
    ["libgen", "https://libgen.is"],
    ["zlibrary", "https://z-lib.org"],
    ["project gutenberg", "https://www.gutenberg.org"],
    ["open library", "https://openlibrary.org"],
    ["duolingo", "https://www.duolingo.com"],
    ["quizlet", "https://quizlet.com"],
    ["wolfram alpha", "https://www.wolframalpha.com"],
    ["desmos", "https://www.desmos.com"],
    ["geogebra", "https://www.geogebra.org"],
    ["overleaf", "https://www.overleaf.com"],
    ["latex project", "https://www.latex-project.org"],
    ["draw.io", "https://app.diagrams.net"],
    ["excalidraw", "https://excalidraw.com"],
    ["miro", "https://miro.com"],
    ["lucidchart", "https://www.lucidchart.com"],
    ["tableau", "https://www.tableau.com"],
    ["powerbi", "https://powerbi.microsoft.com"],
    ["grafana", "https://grafana.com"],
    ["prometheus", "https://prometheus.io"],
    ["elastic", "https://www.elastic.co"],
    ["splunk", "https://www.splunk.com"],
    ["datadog", "https://www.datadoghq.com"],
    ["new relic", "https://newrelic.com"],
    ["sentry", "https://sentry.io"],
    ["logrocket", "https://logrocket.com"],
    ["hotjar", "https://www.hotjar.com"],
    ["google analytics", "https://analytics.google.com"],
    ["segment", "https://segment.com"],
    ["mixpanel", "https://mixpanel.com"],
    ["amplitude", "https://amplitude.com"],
    ["mailchimp", "https://mailchimp.com"],
    ["sendgrid", "https://sendgrid.com"],
    ["mailgun", "https://www.mailgun.com"],
    ["postman", "https://www.postman.com"],
    ["insomnia", "https://insomnia.rest"],
    ["swagger", "https://swagger.io"],
    ["rapidapi", "https://rapidapi.com"],
    ["jsonplaceholder", "https://jsonplaceholder.typicode.com"],
    ["reqres", "https://reqres.in"],
    ["httpbin", "https://httpbin.org"],
    ["ngrok", "https://ngrok.com"],
    ["cloudflare", "https://www.cloudflare.com"],
    ["akamai", "https://www.akamai.com"],
    ["fastly", "https://www.fastly.com"],
    ["vercel", "https://vercel.com"],
    ["netlify", "https://www.netlify.com"],
    ["heroku", "https://www.heroku.com"],
    ["railway", "https://railway.app"],
    ["render", "https://render.com"],
    ["fly.io", "https://fly.io"],
    ["digitalocean", "https://www.digitalocean.com"],
    ["linode", "https://www.linode.com"],
    ["vultr", "https://www.vultr.com"],
    ["aws", "https://aws.amazon.com"],
    ["google cloud", "https://cloud.google.com"],
    ["azure", "https://azure.microsoft.com"],
    ["ibm cloud", "https://www.ibm.com/cloud"],
    ["oracle cloud", "https://www.oracle.com/cloud"],
    ["alibaba cloud", "https://www.alibabacloud.com"],
    ["terraform", "https://www.terraform.io"],
    ["ansible", "https://www.ansible.com"],
    ["puppet", "https://puppet.com"],
    ["chef", "https://www.chef.io"],
    ["saltstack", "https://saltproject.io"],
    ["vagrant", "https://www.vagrantup.com"],
    ["packer", "https://www.packer.io"],
    ["consul", "https://www.consul.io"],
    ["vault", "https://www.vaultproject.io"],
    ["nomad", "https://www.nomadproject.io"],
    ["boundary", "https://www.boundaryproject.io"],
    ["waypoint", "https://www.waypointproject.io"],
    ["boundary", "https://www.boundaryproject.io"],
    ["boundary", "https://www.boundaryproject.io"],
]


# ==================== LEGACY FUNCTIONS ====================

def open_any(self):
    for site in sites:
        if f"open {site[0]}" in self.text.lower():
            webbrowser.open(f"{site[1]}")
            self.say(f"I opened {site[0]} for you.")
            print(f"Zeus: I opened {site[0]} for you.")
    if "open" in self.text.lower() and "music" in self.text.lower() or "song" in self.text.lower():
        music_name = self.text.lower().replace("open", "").replace("music", "").strip()
        if play_music(music_name):
            self.say(f"I opened {music_name} for you.")
            print(f"Zeus: Playing {music_name}")
        else:
            self.say("I couldn't find that music.")
            print("Zeus: Music not found")
    if "open camera" in self.text.lower() or "open facetime" in self.text.lower():
        system = platform.system()
        if system == "Windows":
            os.system("start microsoft.windows.camera:")
        elif system == "Linux":
            subprocess.Popen(["cheese"])
        elif system == "Darwin":
            if "facetime" in self.text.lower():
                subprocess.Popen(["open", "-a", "FaceTime"])
            else:
                subprocess.Popen(["open", "-a", "Photo Booth"])
        self.say("I open camera for you")
        print("Zeus I open camera for you")


def open_any_type(self):
    for site in sites:
        if f"open {site[0]}" in self.text.lower():
            webbrowser.open(f"{site[1]}")
            print(f"Zeus: I opened {site[0]} for you.")
    if (("open" in self.text.lower() and "music" in self.text.lower()) or ("open" in self.text.lower() and "song" in self.text.lower())):
        music_name = self.text.lower().replace("open", "").replace("music", "").replace("song", "").strip()
        if play_music(music_name):
            print(f"Zeus: Playing {music_name}")
        else:
            print("Zeus: Music not found")
    if "open camera" in self.text.lower() or "open facetime" in self.text.lower():
        system = platform.system()
        if system == "Windows":
            os.system("start microsoft.windows.camera:")
        elif system == "Linux":
            subprocess.Popen(["cheese"])
        elif system == "Darwin":
            if "facetime" in self.text.lower():
                subprocess.Popen(["open", "-a", "FaceTime"])
            else:
                subprocess.Popen(["open", "-a", "Photo Booth"])
        print("Zeus I open camera for you")


def wtime(self):
    hour = datetime.datetime.now().strftime("%H")
    min = datetime.datetime.now().strftime("%M")
    sec = datetime.datetime.now().strftime("%S")
    say(f"{self.name}; the time is {hour} hours and {min} minutes and {sec}")
    print(f"Zeus: {self.name} the time is {hour}:{min}:{sec}")


def time_type(self):
    hour = datetime.datetime.now().strftime("%H")
    min = datetime.datetime.now().strftime("%M")
    sec = datetime.datetime.now().strftime("%S")
    print(f"Zeus: {self.name} the time is {hour}:{min}:{sec}")


def generate_and_bye(self):
    name = self.name
    global bye
    self.bye = rchoice([
        f"GoodBye {name}", f"bye {name}", f"Goodbye {name}, see you later",
        f"See you soon {name}", f"Bye bye {name}", f"Take care {name}",
        f"Have a nice day {name}", f"See you again {name}",
        f"Until next time {name}", f"Good night {name}", f"Farewell {name}",
        f"Catch you later {name}", f"Talk to you later {name}",
        f"Have a good one {name}", f"Bye for now {name}",
        f"See you around {name}", f"Stay safe {name}",
        f"Take it easy {name}", f"Thanks for talking {name}",
        f"Closing session {name}",
    ])
    self.say(f"{self.bye}")
    print(f"Zeus: {self.bye}")


def generate_and_bye_type(self):
    name = self.name
    global bye
    self.bye = rchoice([
        f"GoodBye {name}", f"bye {name}", f"Goodbye {name}, see you later",
        f"See you soon {name}", f"Bye bye {name}", f"Take care {name}",
        f"Have a nice day {name}", f"See you again {name}",
        f"Until next time {name}", f"Good night {name}", f"Farewell {name}",
        f"Catch you later {name}", f"Talk to you later {name}",
        f"Have a good one {name}", f"Bye for now {name}",
        f"See you around {name}", f"Stay safe {name}",
        f"Take it easy {name}", f"Thanks for talking {name}",
        f"Closing session {name}",
    ])
    print(f"Zeus: {self.bye}")


def generate_and_hello(self):
    name = self.name
    global hello
    self.hello = rchoice([
        f"Hello {name}", f"Hi {name}", f"Hey {name}",
        f"Hello there {name}", f"Hi there {name}", f"Welcome {name}",
        f"Welcome back {name}", f"Nice to see you {name}",
        f"Good to see you {name}", f"Hey there {name}",
        f"Greetings {name}", f"Howdy {name}", f"What's up {name}",
        f"How are you {name}", f"Hope you're doing well {name}",
        f"Nice to meet you {name}", f"Great to see you {name}",
        f"Hello again {name}", f"Hey, welcome {name}",
        f"Ready to help you {name}",
    ])
    self.say(f"{self.hello}")
    print(f"Zeus: {self.hello}")


def generate_and_hello_type(self):
    name = self.name
    global hello
    self.hello = rchoice([
        f"Hello {name}", f"Hi {name}", f"Hey {name}",
        f"Hello there {name}", f"Hi there {name}", f"Welcome {name}",
        f"Welcome back {name}", f"Nice to see you {name}",
        f"Good to see you {name}", f"Hey there {name}",
        f"Greetings {name}", f"Howdy {name}", f"What's up {name}",
        f"How are you {name}", f"Hope you're doing well {name}",
        f"Nice to meet you {name}", f"Great to see you {name}",
        f"Hello again {name}", f"Hey, welcome {name}",
        f"Ready to help you {name}",
    ])
    print(f"Zeus: {self.hello}")


def hey_Zeus(self):
    self.say(f"what you need {self.name}")
    print(f"Zeus: what you need {self.name}")


def hey_Zeus_type(self):
    print(f"Zeus: what you need {self.name}")


def takeCommand(self):
    self.r = sr.Recognizer()
    self.r.pause_threshold = 1.5
    self.r.energy_threshold = 300

    with sr.Microphone() as source:
        print("Listening...")
        self.r.adjust_for_ambient_noise(source, duration=0.5)
        self.audio = self.r.listen(source)
        print("Recognizing...")

    try:
        self.query = self.r.recognize_google(self.audio, language="en-US")
        return self.query.lower()

    except sr.UnknownValueError:
        print("Zeus: I didn't understand what you said; please say it again.")
        return ""

    except sr.RequestError:
        return "Internet error"


def say(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
