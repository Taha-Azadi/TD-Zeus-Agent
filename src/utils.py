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
import time
import threading
import itertools
from pathlib import Path
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    _HAS_RICH = True
    console = Console()
except ImportError:
    _HAS_RICH = False
    console = None


TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Execute a shell command on the computer. Use for file operations, git, pip, system commands, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run."},
                    "cwd": {"type": "string", "description": "Optional working directory."}
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
                "properties": {
                    "path": {"type": "string", "description": "Directory path. Defaults to current directory.", "default": "."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_content",
            "description": "Read content of a text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the file."},
                    "max_chars": {"type": "integer", "description": "Max characters to read.", "default": 8000}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file_content",
            "description": "Write or overwrite content to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the file."},
                    "content": {"type": "string", "description": "Content to write."}
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
            "description": "Take a screenshot and save it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "save_path": {"type": "string", "description": "Save path. Default: screenshot.png", "default": "screenshot.png"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Open an application by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Application name."}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Find and play a music file on the computer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name or part of the music filename."}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_website",
            "description": "Open a website in the default browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_name": {"type": "string", "description": "Site name like youtube, github, google, etc."}
                },
                "required": ["site_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get current system date and time.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]

def run_shell_command(command, cwd=None):
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=30, encoding='utf-8', errors='ignore'
        )
        out = result.stdout.strip() if result.stdout.strip() else "[No output]"
        err = result.stderr.strip() if result.stderr.strip() else ""
        return f"📟 Exit Code: {result.returncode}\n📝 Output:\n{out}" + (f"\n⚠️ Error:\n{err}" if err else "")
    except subprocess.TimeoutExpired:
        return "⏱️ Command timed out after 30 seconds"
    except Exception as e:
        return f"❌ Exception: {e}"


def list_directory(path="."):
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"❌ Path not found: {path}"
        lines = []
        for item in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            icon = "📁" if item.is_dir() else "📄"
            size = f" ({item.stat().st_size:,} bytes)" if item.is_file() else ""
            lines.append(f"{icon} {item.name}{size}")
        return "\n".join(lines) if lines else "📭 Directory is empty"
    except Exception as e:
        return f"❌ Error: {e}"


def read_file_content(filepath, max_chars=8000):
    try:
        p = Path(filepath).expanduser()
        if not p.exists():
            return f"❌ File not found: {filepath}"
        text = p.read_text(encoding='utf-8', errors='ignore')
        if len(text) > max_chars:
            text = text[:max_chars] + f"\n\n... [truncated, total {len(text):,} chars]"
        return text
    except Exception as e:
        return f"❌ Error: {e}"


def write_file_content(filepath, content):
    try:
        p = Path(filepath).expanduser()
        p.write_text(content, encoding='utf-8')
        return f"✅ Written to: {p}"
    except Exception as e:
        return f"❌ Error: {e}"


def get_system_info():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        info = (f"🖥️  System: {platform.system()} {platform.release()} ({platform.machine()})\n"
                f"⚡ CPU: {cpu}% usage | Cores: {psutil.cpu_count()}\n"
                f"🧠 RAM: {mem.percent}% used | {mem.used//1024//1024:,}MB / {mem.total//1024//1024:,}MB\n"
                f"💾 Disk: {disk.percent}% used | {disk.used//1024//1024//1024:,}GB / {disk.total//1024//1024//1024:,}GB")
        return info
    except ImportError:
        return (f"🖥️  System: {platform.system()} {platform.release()}\n"
                f"💡 Install psutil for full stats: pip install psutil")
    except Exception as e:
        return f"❌ Error: {e}"


def take_screenshot(save_path="screenshot.png"):
    try:
        import pyautogui
        img = pyautogui.screenshot()
        full = Path(save_path).expanduser().resolve()
        img.save(str(full))
        return f"📸 Screenshot saved: {full}"
    except ImportError:
        return "❌ pyautogui not installed. Run: pip install pyautogui"
    except Exception as e:
        return f"❌ Error: {e}"


def open_application(app_name):
    system = platform.system()
    try:
        if system == "Windows":
            os.system(f'start "" "{app_name}"')
        elif system == "Linux":
            subprocess.Popen([app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Darwin":
            subprocess.Popen(["open", "-a", app_name])
        return f"🚀 Opened: {app_name}"
    except Exception as e:
        return f"❌ Error: {e}"


# ==================== STREAMING + THINKING AI ====================

def _stream_chat_completion(payload, on_token, on_thinking_chunk=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        stream=True,
        timeout=60
    )
    
    if response.status_code == 401:
        raise PermissionError("Invalid API Key (401)")
    elif response.status_code != 200:
        raise ConnectionError(f"HTTP {response.status_code}: {response.text[:200]}")
    
    full_text = ""
    full_thinking = ""
    in_thinking = False
    
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
            
            # Thinking / reasoning content (DeepSeek R1 style)
            reasoning = delta.get('reasoning') or delta.get('reasoning_content')
            if reasoning:
                full_thinking += reasoning
                if on_thinking_chunk:
                    on_thinking_chunk(reasoning, full_thinking)
                in_thinking = True
                continue
            
            # Main content
            content = delta.get('content', '')
            if content:
                if in_thinking and on_thinking_chunk:
                    on_thinking_chunk(None, full_thinking) 
                in_thinking = False
                full_text += content
                on_token(content, full_text)
                
        except json.JSONDecodeError:
            continue
    
    return full_text, full_thinking

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

with open("ai.txt", "r") as r:
    re = r.read()
def clear():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"""
    {Fore.YELLOW}
╶─╮   ╭─╴   ╷ ╷   ╭─╮      ╭─╮   ╭─╴   ╭─╴   ╭╮╷   ╶┬╴
╭─╯   ├╴    │ │   ╰─╮      ├─┤   │╶╮   ├╴    │╰┤    │
╰─╴   ╰─╴   ╰─╯   ╰─╯      ╵ ╵   ╰─╯   ╰─╴   ╵ ╵    ╵
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⠀
⠀⠀⠈⠲⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣶⣿⣿⠃⠀
⠀⠀⠀⠀⠈⠻⣷⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⡿⠋⣨⣿⠏⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠛⢿⣿⣦⣀⠀⠀⠀⠀⠀⠀⠀⣠⣾⡿⠋⣠⣾⡿⠋⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣿⣿⣿⡦⠀⠀⠀⣠⣾⡿⠋⣠⣾⡿⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣯⡀⠀⣠⣾⡿⠋⣠⣾⡿⠋⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣾⣿⠋⣠⣾⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣨⣿⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣠⣄⠀⠀⠀⣠⣾⡿⠋⣨⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠻⣿⣧⡀⠸⡿⠋⣠⣾⡿⠋⠀⠙⢿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠻⣿⣦⡀⠺⠿⠋⠀⠀⠀⢠⣾⣿⣿⣅⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣠⣦⡈⠻⣿⣦⣀⠀⠀⠀⠀⠀⠈⠙⢿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣠⣾⡿⠋⠀⠀⠈⠻⣿⡷⠀⠀⠀⠀⠀⠀⠀⠈⠙⠿⣷⣄⡀⠀⠀⠀⠀
⠀⠀⣾⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⢦⡀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠂⠀
                           ╔══════════════════════════════════╗
╔══════════════════════════╝══════════════════════════════════╝══════════════════════════╗
║                         for clear Enter clear or say clear                             ║
║                     for edit api key go to ai.txt and edit this                        ║
║                   for edit your name go to ask2.txt and edit this                      ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
{Fore.RESET}
""")
API_KEY = re
USER_PATH = os.path.expanduser("~")

MUSIC_EXTENSIONS = (".mp3", ".wav", ".m4a", ".flac", ".ogg")


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

    # First, search directly for part of the name
    for song in songs:
        filename = os.path.basename(song).lower()

        if name in filename:
            return song

    # if difflib not found
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

# ==================== AI FUNCTIONS ====================

def ai_speak(self):
    try:
        thinking_buffer = [""]
        thinking_done = threading.Event()
        
        def spinner_worker():
            chars = itertools.cycle(['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'])
            while not thinking_done.is_set():
                sys.stdout.write(f"\r\033[90m🧠 Thinking {next(chars)}\033[0m")
                sys.stdout.flush()
                time.sleep(0.08)
            sys.stdout.write("\r" + " "*30 + "\r")
            sys.stdout.flush()
            if thinking_buffer[0]:
                print(f"\033[90m💭 Thinking:\n{thinking_buffer[0][:500]}{'...' if len(thinking_buffer[0])>500 else ''}\033[0m\n")
        
        def on_think(chunk, full):
            if chunk:
                thinking_buffer[0] += chunk
        
        def on_token(token, full):
            print(token, end='', flush=True)
        
        t = threading.Thread(target=spinner_worker)
        t.start()
        
        payload = {
            "model": "deepseek/deepseek-r1:free",  
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You ARE Zeus Agent — an AI assistant created by Taha-Azadi. "
                        "You have FULL ACCESS to the user's computer. You can run commands, "
                        "manage files, open apps, take screenshots, and control the system. "
                        "Always respond as Zeus Agent using Markdown formatting."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"My name is {self.name}.\n"
                        f"You can use these tools if needed:\n"
                        f"- run_shell_command(cmd)\n"
                        f"- list_directory(path)\n"
                        f"- read_file_content(path)\n"
                        f"- write_file_content(path, content)\n"
                        f"- get_system_info()\n"
                        f"- take_screenshot(path)\n"
                        f"- open_application(name)\n\n"
                        f"User request:\n{self.text}"
                    ),
                },
            ],
            "temperature": 0.7,
            "stream": True,
            "include_reasoning": True,
        }
        
        print(f"\n\033[1;36m{'═'*50}\033[0m")
        print(f"\033[1;36m  ⚡ Zeus Agent — Live Stream\033[0m")
        print(f"\033[1;36m{'═'*50}\033[0m\n")
        
        full_content, _ = _stream_chat_completion(payload, on_token, on_think)
        
        thinking_done.set()
        t.join()
        print("\n")  # newline after stream
        
        if full_content:
            say(full_content)
        
    except PermissionError as e:
        _print_error(str(e))
    except ConnectionError as e:
        _print_error(str(e))
    except requests.exceptions.RequestException as e:
        _print_error(f"Network Error: {e}")
    except Exception as e:
        _print_error(f"Error: {e}")


def ai_type(self):
    try:
        thinking_buffer = [""]
        thinking_done = threading.Event()
        
        def spinner_worker():
            chars = itertools.cycle(['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'])
            while not thinking_done.is_set():
                sys.stdout.write(f"\r\033[90m🧠 Thinking {next(chars)}\033[0m")
                sys.stdout.flush()
                time.sleep(0.08)
            sys.stdout.write("\r" + " "*30 + "\r")
            sys.stdout.flush()
            if thinking_buffer[0]:
                print(f"\033[90m💭 Thinking:\n{thinking_buffer[0][:500]}{'...' if len(thinking_buffer[0])>500 else ''}\033[0m\n")
        
        def on_think(chunk, full):
            if chunk:
                thinking_buffer[0] += chunk
        
        def on_token(token, full):
            print(token, end='', flush=True)
        
        t = threading.Thread(target=spinner_worker)
        t.start()
        
        payload = {
            "model": "meta-llama/llama-3.1-70b-instruct:free",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You ARE Zeus Agent — an AI assistant created by Taha-Azadi. "
                        "You have FULL ACCESS to the user's computer. "
                        "Think step by step before acting. Use Markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"My name is {self.name}.\n"
                        f"Available tools: run_shell_command, list_directory, read_file_content, "
                        f"write_file_content, get_system_info, take_screenshot, open_application.\n\n"
                        f"{self.text}"
                    ),
                },
            ],
            "temperature": 0.7,
            "stream": True,
            "include_reasoning": True,
        }
        
        print(f"\n\033[1;36m{'═'*50}\033[0m")
        print(f"\033[1;36m  ⚡ Zeus Agent — Live Stream\033[0m")
        print(f"\033[1;36m{'═'*50}\033[0m\n")
        
        full_content, _ = _stream_chat_completion(payload, on_token, on_think)
        
        thinking_done.set()
        t.join()
        print("\n")
        
    except Exception as e:
        _print_error(f"Error: {e}")


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
    self.bye = rchoice(
        [
            f"GoodBye {name}",
            f"bye {name}",
            f"Goodbye {name}, see you later",
            f"See you soon {name}",
            f"Bye bye {name}",
            f"Take care {name}",
            f"Have a nice day {name}",
            f"See you again {name}",
            f"Until next time {name}",
            f"Good night {name}",
            f"Farewell {name}",
            f"Catch you later {name}",
            f"Talk to you later {name}",
            f"Have a good one {name}",
            f"Bye for now {name}",
            f"See you around {name}",
            f"Stay safe {name}",
            f"Take it easy {name}",
            f"Thanks for talking {name}",
            f"Closing session {name}",
        ]
    )
    self.say(f"{self.bye}")
    print(f"Zeus: {self.bye}")


def generate_and_bye_type(self):
    name = self.name
    global bye
    self.bye = rchoice(
        [
            f"GoodBye {name}",
            f"bye {name}",
            f"Goodbye {name}, see you later",
            f"See you soon {name}",
            f"Bye bye {name}",
            f"Take care {name}",
            f"Have a nice day {name}",
            f"See you again {name}",
            f"Until next time {name}",
            f"Good night {name}",
            f"Farewell {name}",
            f"Catch you later {name}",
            f"Talk to you later {name}",
            f"Have a good one {name}",
            f"Bye for now {name}",
            f"See you around {name}",
            f"Stay safe {name}",
            f"Take it easy {name}",
            f"Thanks for talking {name}",
            f"Closing session {name}",
        ]
    )
    print(f"Zeus: {self.bye}")


def generate_and_hello(self):
    name = self.name
    global hello
    self.hello = rchoice(
        [
            f"Hello {name}",
            f"Hi {name}",
            f"Hey {name}",
            f"Hello there {name}",
            f"Hi there {name}",
            f"Welcome {name}",
            f"Welcome back {name}",
            f"Nice to see you {name}",
            f"Good to see you {name}",
            f"Hey there {name}",
            f"Greetings {name}",
            f"Howdy {name}",
            f"What's up {name}",
            f"How are you {name}",
            f"Hope you're doing well {name}",
            f"Nice to meet you {name}",
            f"Great to see you {name}",
            f"Hello again {name}",
            f"Hey, welcome {name}",
            f"Ready to help you {name}",
        ]
    )
    self.say(f"{self.hello}")
    print(f"Zeus: {self.hello}")


def generate_and_hello_type(self):
    name = self.name
    global hello
    self.hello = rchoice(
        [
            f"Hello {name}",
            f"Hi {name}",
            f"Hey {name}",
            f"Hello there {name}",
            f"Hi there {name}",
            f"Welcome {name}",
            f"Welcome back {name}",
            f"Nice to see you {name}",
            f"Good to see you {name}",
            f"Hey there {name}",
            f"Greetings {name}",
            f"Howdy {name}",
            f"What's up {name}",
            f"How are you {name}",
            f"Hope you're doing well {name}",
            f"Nice to meet you {name}",
            f"Great to see you {name}",
            f"Hello again {name}",
            f"Hey, welcome {name}",
            f"Ready to help you {name}",
        ]
    )
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
