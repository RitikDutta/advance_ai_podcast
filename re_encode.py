import os
import subprocess

def reencode_videos_in_folder(folder_path):
    """
    Re-encode all video files (mp4, mov, avi, mkv) in `folder_path` 
    (including subfolders) to a uniform format:
      - Video codec: libx264
      - Audio codec: aac
      - Frame rate: 24 fps
    This overwrites the original files.
    """
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            # Check if it's a video by extension
            if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                input_path = os.path.join(root, filename)
                temp_path = os.path.join(root, "tmp_" + filename)

                # Build the ffmpeg command
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-y",            # overwrite output if exists
                    "-i", input_path,
                    "-c:v", "libx264",
                    "-preset", "slow",
                    "-crf", "18",
                    "-c:a", "aac",
                    "-r", "24",      # force 24 fps
                    temp_path
                ]

                print(f"[Reencode] Processing: {input_path}")
                
                # Run ffmpeg
                subprocess.run(ffmpeg_cmd, check=True)

                # Remove the original file
                os.remove(input_path)
                # Rename temp file to original
                os.rename(temp_path, input_path)
                print(f"[Reencode] Replaced {input_path} with 24fps H.264 version.\n")


if __name__ == "__main__":
    # Example usage:
    animations_folder = "animations"  # or the absolute path
    reencode_videos_in_folder(animations_folder)
    print("[Reencode] Done re-encoding all videos in:", animations_folder)
