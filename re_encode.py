import os
import subprocess
import tempfile

def run_re_encode(base_dir="animations"):
    print("============================================================")
    print("[INFO] Re-encoding all .mp4 files in the directory.")
    print(f"[INFO] Base directory: {base_dir}")
    print("------------------------------------------------------------")

    ffmpeg_cmd_template = [
        "ffmpeg",
        "-y",  # overwrite output
        "-i", "",  # input placeholder
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "experimental", # may not be needed in modern ffmpeg
        "-preset", "fast",
        "-crf", "23",  # adjust as needed
        ""  # output placeholder
    ]

    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith(".mp4"):
                input_path = os.path.join(root, f)
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp4", dir=root)
                os.close(tmp_fd)

                cmd = ffmpeg_cmd_template[:]
                cmd[3] = input_path  # input after -i
                cmd[-1] = tmp_path   # output

                print(f"[INFO] Re-encoding: {input_path}")
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if result.returncode == 0:
                    # Replace the original file with the converted one
                    os.replace(tmp_path, input_path)
                    print(f"[SUCCESS] Re-encoded and replaced: {input_path}")
                else:
                    # If ffmpeg failed, remove temp file and print error
                    os.remove(tmp_path)
                    print(f"[ERROR] Failed to re-encode {input_path}: {result.stderr}")

    print("============================================================")
    print("[INFO] Re-encoding process completed!")
    print("============================================================")
