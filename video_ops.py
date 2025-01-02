import os
import shutil
import subprocess

class VideoOps:
    def __init__(self):
        pass

    def _get_next_video_name(self, output_folder):
        """
        Determines the next video file name in the sequence 
        (e.g., video1.mp4, video2.mp4, etc.)
        """
        existing_videos = [
            f for f in os.listdir(output_folder)
            if f.startswith("video") and f.endswith(('.mp4', '.avi', '.mov', '.mkv'))
        ]
        max_num = 0
        for video in existing_videos:
            try:
                # Extract the numeric part from "videoXYZ"
                num = int(''.join(filter(str.isdigit, os.path.splitext(video)[0])))
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
        next_num = max_num + 1
        return f"video{next_num}.mp4"

    def trim_video(self, input_path, output_folder='test', start_ms=None, end_ms=None, entire_clip=False):
        """
        Trims (precisely) a segment from the input video based on start and end times in milliseconds,
        or copies the entire video if `entire_clip` is True.
        Saves the processed video with a sequential name in the specified output folder.

        :param input_path: Path to the input video file.
        :param output_folder: Folder to save the processed video. Defaults to 'test'.
        :param start_ms: Start time in milliseconds (if trimming).
        :param end_ms: End time in milliseconds (if trimming).
        :param entire_clip: If True, copies the entire video. Defaults to False.
        """
        # Validate input file existence
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"The input video file '{input_path}' does not exist.")

        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)

        # Determine output file name
        output_filename = self._get_next_video_name(output_folder)
        output_path = os.path.join(output_folder, output_filename)

        # If entire_clip is True, just copy the file
        if entire_clip:
            try:
                shutil.copy2(input_path, output_path)
                print(f"[FFmpeg] Copied entire clip -> {output_path}")
            except Exception as e:
                print(f"[FFmpeg] Error copying file: {e}")
            return

        # Otherwise, we do a precise trim
        if start_ms is None or end_ms is None:
            raise ValueError("start_ms and end_ms must be provided if entire_clip=False.")

        if start_ms < 0 or end_ms < 0:
            raise ValueError("Start and end times must be >= 0.")
        if start_ms >= end_ms:
            raise ValueError("start_ms must be < end_ms.")

        start_sec = start_ms / 1000.0
        end_sec = end_ms / 1000.0
        duration_sec = end_sec - start_sec

        # We'll use FFmpeg to re-encode at 24 fps, H.264, AAC
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",                # overwrite output
            "-i", input_path,    # input
            "-ss", str(start_sec),
            "-t", str(duration_sec),
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18",
            "-c:a", "aac",
            "-r", "24",          # force 24 fps
            output_path
        ]

        try:
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"[FFmpeg] Trimmed {start_ms}ms to {end_ms}ms at 24fps -> {output_path}")
        except subprocess.CalledProcessError as e:
            print("[FFmpeg] Error during trimming:")
            print(e.stderr.decode('utf-8', errors='ignore'))



# # test 

# trim_test = VideoOps()
# trim_test.trim_video('/home/codered/Downloads/aipod/scripy_main/animations/man/yes_long/_without_lip_move.mp4', output_folder='test', start_ms=0, end_ms=3274)


# import cv2

# video_path = 'test/video1.mp4'

# cap = cv2.VideoCapture(video_path)
# fps = cap.get(cv2.CAP_PROP_FPS)
# frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

# duration_ms = (frame_count / fps) * 1000

# print(f"Video Duration: {int(duration_ms)} ms")

# cap.release()