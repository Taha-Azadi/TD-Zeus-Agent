from src.utils import (
    generate_and_bye,
    generate_and_hello,
    open_any,
    sites,
    hey_Zeus,
    takeCommand,
    say,
    wtime,
    ai_speak,
    clear,
)


class Speak:
    def __init__(self, name="dear user"):
        self.name = name
        self.takeCommand = takeCommand
        self.say = say
        self.say("Welcome to Zeus Agent")
        print("Zeus: hello I'm Zeus Agent")

        while True:
            self.text = self.takeCommand(self)

            if self.text != None:
                print(f"user: {self.text}")
                if "bye" in self.text.lower():
                    generate_and_bye(self)
                    break
                if "the time" in self.text.lower() or "time is" in self.text.lower():
                    wtime(self)
                elif "clear" in self.text.lower() or "cls " in self.text.lower():
                    clear()
                elif any(
                    x in self.text for x in ["hey Zeus", "Zeus", "hey z", "hello Zeus"]
                ):
                    hey_Zeus(self)
                else:
                    ai_speak(self)
