from pynput.keyboard import Controller, Key
import time

class InputSimulator:
    def __init__(self):
        self.keyboard = Controller()

    def type_text(self, text):
        """
        Simulates typing of the given text.
        Handles Unicode characters automatically via pynput.
        """
        if not text:
            return

        # Slight delay to ensure focus is active if called immediately after a UI interaction
        # time.sleep(0.1) 
        
        for char in text:
            self.keyboard.type(char)
            # A tiny sleep might be needed for some applications to register key presses correctly
            # though pynput is usually fast enough.
            # time.sleep(0.005) 
        
        # Add a space after typing, as usually expected in voice typing
        self.keyboard.type(' ')
