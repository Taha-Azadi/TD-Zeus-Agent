from src.utils import (
    generate_and_bye_type,
    generate_and_hello_type,
    open_any_type,
    sites,
    hey_Zeus_type,
    time_type,
    ai_type,
    clear,
)


class Type:
    def __init__(self, name="dear user"):
        self.name = name
        print("Zeus: hello I'm Zeus Agent")

        while True:

            self.text = input("ask Anything: ")

            if self.text != None:
                print(f"user: {self.text}")
                if "open" in self.text.lower():
                    open_any_type(self)
                if "bye" in self.text.lower():
                    generate_and_bye_type(self)
                    break
                if "the time" in self.text.lower() or "time is" in self.text.lower():
                    time_type(self)

                elif "hello" in self.text.lower() or "hi " in self.text.lower():
                    generate_and_hello_type(self)
                elif "clear" in self.text.lower() or "cls " in self.text.lower():
                    clear()
                elif any(
                    x in self.text for x in ["hey Zeus", "Zeus", "hey z", "hello Zeus"]
                ):
                    hey_Zeus_type(self)
                elif "open" not in self.text.lower():
                    ai_type(self)
