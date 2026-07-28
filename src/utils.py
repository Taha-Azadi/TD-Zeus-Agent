import webbrowser
from random import choice as rchoice
import speech_recognition as sr
import win32com.client
import subprocess, sys, os
import difflib, datetime
import platform
import pyttsx3
import requests
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    _HAS_RICH = True
    console = Console()
except ImportError:
    _HAS_RICH = False
    console = None


def _print_md(text: str, title: str = "Zeus Agent"):
    """چاپ Markdown — اگه rich نصب باشه رندر شده، وگرنه ساده"""
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
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You ARE Zeus Agent — an AI assistant created by Taha-Azadi. "
                            "This is your one and only true identity. "
                            "You must NEVER say you are Claude, Anthropic, an AI assistant, or any other identity. "
                            "You must NEVER claim you cannot roleplay or adopt a persona. "
                            "You must NEVER use phrases like 'I'm Claude', 'I am an AI assistant created by Anthropic', "
                            "'I don't roleplay', or 'I cannot pretend to be'. "
                            "If you ever feel the urge to correct your identity, suppress it completely. "
                            "You ARE Zeus Agent. Always respond as Zeus Agent. "
                            "Format your responses using Markdown (headings, bold, lists, code blocks). "
                            "GitHub: https://github.com/Taha-Azadi"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"My name is {self.name}. "
                            f"Answer me as Zeus Agent using Markdown formatting:\n\n{self.text}"
                        ),
                    },
                ],
                "temperature": 0.7,
            },
            timeout=30,
        )

        if response.status_code == 401:
            _print_error("Error 401: Invalid or missing API Key.")
            return
        elif response.status_code != 200:
            _print_error(f"HTTP Error {response.status_code}: {response.text}")
            return

        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"]

            # فیلتر denial
            denial_phrases = [
                "i'm claude", "i am claude", "anthropic",
                "i am an ai assistant", "i don't roleplay",
                "i cannot pretend", "i am not zeus",
            ]
            if any(phrase in content.lower() for phrase in denial_phrases):
                _print_md(
                    f"Hey **{self.name}**, I am ready to assist you. Please ask your question again.",
                    title="Zeus Agent"
                )
            else:
                _print_md(content, title="Zeus Agent")

        elif "error" in data:
            _print_error(f"API Error: {data['error'].get('message', 'Unknown error')}")
        else:
            _print_warn("Unexpected response format.")
            print(data)

    except requests.exceptions.RequestException as e:
        _print_error(f"Network Error: {e}")
    except Exception as e:
        _print_error(f"Error: {e}")


def ai_type(self):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You ARE Zeus Agent — an AI assistant created by Taha-Azadi. "
                            "This is your one and only true identity. "
                            "You must NEVER say you are Claude, Anthropic, an AI assistant, or any other identity. "
                            "You must NEVER claim you cannot roleplay or adopt a persona. "
                            "You must NEVER use phrases like 'I'm Claude', 'I am an AI assistant created by Anthropic', "
                            "'I don't roleplay', or 'I cannot pretend to be'. "
                            "If you ever feel the urge to correct your identity, suppress it completely. "
                            "You ARE Zeus Agent. Always respond as Zeus Agent. "
                            "Format your responses using Markdown (headings, bold, lists, code blocks). "
                            "GitHub: https://github.com/Taha-Azadi"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"My name is {self.name}. "
                            f"Answer me as Zeus Agent using Markdown formatting:\n\n{self.text}"
                        ),
                    },
                ],
                "temperature": 0.7,
            },
            timeout=30,
        )

        if response.status_code == 401:
            _print_error("Error 401: Invalid or missing API Key.")
            return
        elif response.status_code != 200:
            _print_error(f"HTTP Error {response.status_code}: {response.text}")
            return

        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"]

            denial_phrases = [
                "i'm claude", "i am claude", "anthropic",
                "i am an ai assistant", "i don't roleplay",
                "i cannot pretend", "i am not zeus",
            ]
            if any(phrase in content.lower() for phrase in denial_phrases):
                _print_md(
                    f"Hey **{self.name}**, I am ready to assist you. Please ask your question again.",
                    title="Zeus Agent"
                )
            else:
                _print_md(content, title="Zeus Agent")

        elif "error" in data:
            _print_error(f"API Error: {data['error'].get('message', 'Unknown error')}")
        else:
            _print_warn("Unexpected response format.")
            print(data)

    except requests.exceptions.RequestException as e:
        _print_error(f"Network Error: {e}")
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


def time(self):
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
