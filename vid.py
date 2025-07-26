import json
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip,
    CompositeVideoClip, CompositeAudioClip
)
import random

VIDEO_FILE = "gp.mp4"
AUDIO_FILE = "voice.mp3"
MUSIC_FILE = "music.mp3"
TIME_JSON = "time.json"
MEME_FILES = [f"meme{i}.png" for i in range(1, 6)]
KOFI_IMAGE = "Ko-Fi.png"
OUTPUT_FILE = "finish.mp4"

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

# Load meme durations
with open(TIME_JSON, "r") as f:
    time_data = json.load(f)

durations = []
for i in range(1, len(time_data) + 1):
    duration_str = time_data[i - 1][str(i)]
    durations.append(float(duration_str.replace("s", "")))

# Random start point in source video
start_time = random.uniform(0, 25 * 60)

# Load and resize main video
video = VideoFileClip(VIDEO_FILE).subclip(start_time)
video = video.resize(height=TARGET_HEIGHT)
if video.w < TARGET_WIDTH:
    x_margin = (TARGET_WIDTH - video.w) / 2.5
    video = video.margin(left=int(x_margin), right=int(x_margin), color=(0, 0, 0))
elif video.w > TARGET_WIDTH:
    x_crop = (video.w - TARGET_WIDTH) / 2.5
    video = video.crop(x1=x_crop, x2=x_crop)
video = video.set_position(("center", "center")).resize((TARGET_WIDTH, TARGET_HEIGHT))

# Load voice and music audio
voice_audio = AudioFileClip(AUDIO_FILE)
music_audio = AudioFileClip(MUSIC_FILE).volumex(0.2)

# Loop or trim music to voice length + 1 second (for Ko-Fi display)
total_duration = voice_audio.duration + 1
if music_audio.duration < total_duration:
    music_audio = music_audio.loop(duration=total_duration)
else:
    music_audio = music_audio.subclip(0, total_duration)

# Mix audios: voice_audio plays first part, music_audio plays entire duration (background)
# Create silent audio clip same length as voice_audio, so voice and music can be mixed properly
from moviepy.audio.AudioClip import CompositeAudioClip
final_audio = CompositeAudioClip([
    voice_audio.set_start(0),
    music_audio.set_start(0)
]).set_duration(total_duration)

# Set video duration and attach audio (video + memes only during voice length)
video = video.set_duration(voice_audio.duration).set_audio(final_audio)

# Create meme clips overlayed sequentially during voice_audio duration
clips = []
current_start = 0
for i, meme_path in enumerate(MEME_FILES):
    meme = ImageClip(meme_path).resize(width=int(TARGET_WIDTH * 0.8))
    meme = meme.set_position(("center", "center")).set_start(current_start).set_duration(durations[i])
    clips.append(meme)
    current_start += durations[i]

# Compose main video + memes (only during voice_audio duration)
main_clip = CompositeVideoClip([video, *clips], size=(TARGET_WIDTH, TARGET_HEIGHT)).set_duration(voice_audio.duration)

# Create Ko-Fi full screen image clip, duration 1 second, starting right after voice ends
kofi_clip = ImageClip(KOFI_IMAGE).resize((TARGET_WIDTH, TARGET_HEIGHT))
kofi_clip = kofi_clip.set_start(voice_audio.duration).set_duration(1)

# Compose final clip: main_clip first, then Ko-Fi image, audio plays full duration
final = CompositeVideoClip([main_clip, kofi_clip], size=(TARGET_WIDTH, TARGET_HEIGHT))
final = final.set_duration(total_duration).set_audio(final_audio)

# Write the output file
final.write_videofile(OUTPUT_FILE, codec="libx264", audio_codec="aac", fps=30)
