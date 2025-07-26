import tkinter as tk
from PIL import Image, ImageTk
import time
import threading
import pyaudio
import wave
from pydub import AudioSegment
import os
import json

image_files = ["meme1.png", "meme2.png", "meme3.png", "meme4.png", "meme5.png"]
timings = []

# Audio settings
AUDIO_FILENAME = "voice.wav"
MP3_FILENAME = "voice.mp3"
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

recording = True

def record_voice():
    global recording
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    frames = []

    while recording:
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(AUDIO_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # Convert to MP3
    sound = AudioSegment.from_wav(AUDIO_FILENAME)
    sound.export(MP3_FILENAME, format="mp3")
    os.remove(AUDIO_FILENAME)


class MemeViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Meme Viewer")
        self.index = 0
        self.start_time = time.time()

        self.label = tk.Label(root)
        self.label.pack()

        self.button = tk.Button(root, text="Next", command=self.next_image)
        self.button.pack()

        self.images = [ImageTk.PhotoImage(Image.open(img).resize((600, 600))) for img in image_files]
        self.label.config(image=self.images[self.index])

        self.last_switch = time.time()

    def next_image(self):
        now = time.time()
        delta = round(now - self.last_switch, 2)
        timings.append({str(self.index + 1): f"{delta}s"})
        self.last_switch = now

        self.index += 1
        if self.index < len(self.images):
            self.label.config(image=self.images[self.index])
            if self.index == len(self.images) - 1:
                self.button.config(text="Finish")
        else:
            global recording
            recording = False
            self.root.destroy()
            with open("time.json", "w") as f:
                json.dump(timings, f, indent=4)


if __name__ == "__main__":
    threading.Thread(target=record_voice).start()

    root = tk.Tk()
    viewer = MemeViewer(root)
    root.mainloop()
