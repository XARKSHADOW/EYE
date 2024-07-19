import tkinter as tk
from tkinter import font
from gtts import gTTS
import pyttsx3
import os


class TextToSpeech:
    def __init__(self, root):
        self.root = root

    def text_to_speech_gtts(self, text, language='en'):
        tts = gTTS(text=text, lang=language)
        tts.save("output.mp3")


    def text_to_speech_pyttsx3(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def process_text_to_speech(self, engine, text):
        if engine == 'gtts':
            self.text_to_speech_gtts(text)
        elif engine == 'pyttsx3':
            self.text_to_speech_pyttsx3(text)

    def open_tts_window(self):
        tts_window = tk.Toplevel(self.root)
        tts_window.title("Text to Speech")

        # Create a frame for better layout management
        frame = tk.Frame(tts_window)
        frame.pack(expand=True, fill='both')

        # Define a larger font
        large_font = font.Font(size=14)

        # Add widgets to the frame
        tk.Label(frame, text="Enter text:", font=large_font).pack(pady=50)
        text_entry = tk.Entry(frame, width=80, font=large_font)
        text_entry.pack(pady=5, fill='x', padx=5)

        tk.Label(frame, text="Choose engine:", font=large_font).pack(pady=5)
        engine_var = tk.StringVar(value="gtts")
        tk.Radiobutton(frame, text="gTTS", variable=engine_var, value="gtts", font=large_font).pack()
        tk.Radiobutton(frame, text="pyttsx3", variable=engine_var, value="pyttsx3", font=large_font).pack()

        convert_button = tk.Button(frame, text="Convert to Speech", font=large_font,
                                   command=lambda: self.process_text_to_speech(engine_var.get(), text_entry.get()))
        convert_button.pack(pady=10)

        # Center the frame contents
        frame.pack_propagate(True)
        frame.update_idletasks()

        # Calculate center position
        screen_width = tts_window.winfo_screenwidth()
        screen_height = tts_window.winfo_screenheight()
        window_width = frame.winfo_width()
        window_height = frame.winfo_height()

        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        tts_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Make the window resizable
        tts_window.resizable(True, True)


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeech(root)
    app.open_tts_window()  # Open the TTS window directly for testing
    root.mainloop()
