from pydub import AudioSegment
import os

# song = AudioSegment.from_mp3("audio/base.mp3")
# song.export("test.flac", format="flac")


for file in os.listdir('audio/'):
    title, ext = os.path.splitext(file)
    if ext == ".mp3":
        song = AudioSegment.from_mp3(f"audio/{file}")
        song.export(f"audio/{title}.flac", format="flac")
