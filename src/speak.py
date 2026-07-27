from src.utils import (
    generate_and_bye,
    generate_and_hello,
    open_any,
    sites,
    hey_Zeus,
    takeCommand,
    say,
    time,
    ai_speak,
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
                if "open" in self.text.lower():
                    open_any(self)
                if "bye" in self.text.lower():
                    generate_and_bye(self)
                    break
                if "the time" in self.text.lower() or "time is" in self.text.lower():
                    time(self)

                elif "hello" in self.text.lower() or "hi " in self.text.lower():
                    generate_and_hello(self)
                elif any(
                    x in self.text for x in ["hey Zeus", "Zeus", "hey z", "hello Zeus"]
                ):
                    hey_Zeus(self)
                elif "open" not in self.text.lower():
                    ai_speak(self)
