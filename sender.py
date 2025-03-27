import pyaudio
import subprocess

# Set up audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
DEVICE_INDEX = 1  # Set according to your system

# Set up PyAudio
p = pyaudio.PyAudio()

# Open stream for capturing audio
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=DEVICE_INDEX,
                frames_per_buffer=CHUNK)

# FFmpeg command to stream audio
ffmpeg_command = [
    'ffmpeg', '-y', '-f', 's16le', '-ar', '16000', '-ac', '1', '-i', '-',
    '-acodec', 'pcm_mulaw', '-f', 'rtp', 'udp://<RECEIVER_IP>:<PORT>'
]

# Create FFmpeg process for streaming
ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

print("Start speaking...")

# Continuously capture and send audio to FFmpeg
try:
    while True:
        audio_data = stream.read(CHUNK)
        ffmpeg_process.stdin.write(audio_data)

except KeyboardInterrupt:
    print("Stream stopped")

finally:
    # Clean up
    stream.stop_stream()
    stream.close()
    p.terminate()
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()
