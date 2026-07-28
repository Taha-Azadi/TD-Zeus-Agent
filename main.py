import os
from colorama import Fore
import random
import time

WIDTH = 60
HEIGHT = 20


def clear():
    os.system("cls" if os.name == "nt" else "clear")


# ساخت مسیر صاعقه
path = []
x = WIDTH // 2
for y in range(HEIGHT):
    x += random.choice([-1, 0, 1])
    x = max(1, min(WIDTH - 2, x))
    path.append((x, y))

# انیمیشن صاعقه
for i in range(len(path)):
    clear()
    screen = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for j in range(i + 1):
        px, py = path[j]
        screen[py][px] = "⚡"

    print("\n".join("".join(row) for row in screen))
    time.sleep(0.05)

# انفجار
for _ in range(3):
    clear()
    screen = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for px, py in path:
        screen[py][px] = "⚡"

    gx, gy = path[-1]
    for _ in range(80):
        dx = random.randint(-5, 5)
        dy = random.randint(-2, 2)
        xx = max(0, min(WIDTH - 1, gx + dx))
        yy = max(0, min(HEIGHT - 1, gy + dy))
        screen[yy][xx] = "*"

    print("\n".join("".join(row) for row in screen))
    time.sleep(0.1)

# پاک شدن صفحه با نور سفید
for _ in range(3):
    clear()
    print(("█" * WIDTH + "\n") * HEIGHT)
    time.sleep(0.08)

clear()
print(f"""{Fore.YELLOW}
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
{Fore.RESET}
""")
if "ask2.txt" not in os.listdir():
    with open("ask2.txt", "a") as f:
        pass
if "ai.txt" not in os.listdir():
    with open("ai.txt", "a") as f:
        f.write
from src.speak import Speak
from src.type import Type

while True:
    with open("ai.txt", "r") as r:
        re = r.read()
    if re == "":
        askk = input("Enter openrouter api key: ")
        print("checking api key...")
        import requests

        API_KEY = askk

        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {API_KEY}"},
        )
        respcode = response.status_code
        if respcode == 200:
            with open("ai.txt", "a") as f:
                f.write(API_KEY)
            break
        elif respcode == 401:
            print("api key is not vaild")
        elif respcode == 402:
            print("you don't have enough credit")
        elif respcode == 429:
            print("You have reached your rate limit.")
        else:
            print("Unknown Error turn on vpn and reopen zeus agent")
            askk = input("if with reopen It didn't work Enter new openrouter api key: ")
    else:
        print("checking api key...")
        import requests

        API_KEY = re

        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {API_KEY}"},
        )
        respcode = response.status_code
        if respcode == 200:
            API_KEY == re
            break
        elif respcode == 401:
            print("api key is not vaild")
            askk = input("Enter openrouter api key: ")
        elif respcode == 402:
            print("you don't have enough credit")
            askk = input("Enter openrouter api key: ")
        elif respcode == 429:
            print("You have reached your rate limit.")
            askk = input("Enter openrouter api key: ")
        else:
            print("Unknown Error turn on vpn and reopen zeus agent")
            askk = input("if with reopen It didn't work Enter new openrouter api key: ")


while True:
    ask = input("Do you want speak or type your prompt (speak/type): ")

    with open("ask2.txt", "r") as r:
        a = r.read().strip()

    if a == "":
        ask2 = input("What's your name? (Press Enter for never ask you this): ")
        with open("ask2.txt", "w") as f:
            if ask2 == "":
                f.write("Never")
            else:
                f.write(ask2)

        if ask2 == "":
            if ask.lower().strip() == "speak":
                Speak()
            elif ask.lower().strip() == "type":
                Type()
        else:
            if ask.lower().strip() == "speak":
                Speak(name=ask2)
            elif ask.lower().strip() == "type":
                Type(name=ask2)

        break

    elif a != "Never":
        if ask == "speak":
            Speak(name=a)
            break
        elif ask == "type":
            Type(name=a)
            break

    else:
        if ask == "speak":
            Speak()
            break
        if ask == "type":
            Type()
            break
