import subprocess

# Run scrape
subprocess.run(["python", "scrape.py"], check=True)

# Run OCR
subprocess.run(["python", "ocr.py"], check=True)

# Convert numbers
subprocess.run(["python", "numconv.py"] , check=True)

# Run TTS
# subprocess.run(["python", "tts.py"], check=True)

# Run show
subprocess.run(["python", "show.py"], check=True)

subprocess.run(["python", "vid.py"], check=True)
