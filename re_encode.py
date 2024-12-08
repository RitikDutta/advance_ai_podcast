import os
import subprocess
import tempfile

# Set the base directory containing the MP4 files you want to process
base_dir = "animations"

# FFmpeg command template (adjust codecs/parameters as needed)
# -y: overwrite without asking
# -c:v libx264: re-encode video using H.264
# -c:a aac: re-encode audio using AAC
# -preset fast: optional for faster encoding, can remove or adjust
# -crf 23: optional quality parameter for libx264 (lower = better quality, larger file)
ffmpeg_cmd_template = [
    "ffmpeg",
    "-y",  # overwrite output
    "-i", "",  # input (will be replaced)
    "-c:v", "libx264",
    "-c:a", "aac",
    "-strict", "experimental",  # may not be needed for modern ffmpeg
    "-preset", "fast",  # optional: faster encoding
    "-crf", "23",       # optional: control quality
    ""  # output (will be replaced)
]

for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.lower().endswith(".mp4"):
            input_path = os.path.join(root, f)
            # Create a temporary file to avoid overwriting input before checking success
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp4", dir=root)
            os.close(tmp_fd)  # close the file descriptor as ffmpeg will write to it
            
            cmd = ffmpeg_cmd_template[:]
            cmd[3] = input_path  # place input after -i
            cmd[-1] = tmp_path   # set output path
            
            print(f"Re-encoding: {input_path}")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                # Replace the original file with the converted one
                os.replace(tmp_path, input_path)
                print(f"Successfully re-encoded and replaced: {input_path}")
            else:
                # If ffmpeg failed, remove temp file and print error
                os.remove(tmp_path)
                print(f"Error re-encoding {input_path}: {result.stderr}")
