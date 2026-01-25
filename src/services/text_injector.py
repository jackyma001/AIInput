from pynput.keyboard import Controller

class TextInjector:
    def __init__(self):
        self.keyboard = Controller()

    def type_text(self, text):
        if not text:
            return
        
        # Simple injection for now
        self.keyboard.type(text)
        # self.keyboard.type(" ") # Optional: add space after
