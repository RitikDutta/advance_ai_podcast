import os
import shutil
from moviepy.editor import VideoFileClip

class VideoOps:
    def __init__(self):
        pass

    def _get_next_video_name(self, output_folder):
        """
        Determines the next video file name in the sequence (e.g., video1.mp4, video2.mp4, etc.)
        
        :param output_folder: The folder where videos are saved.
        :return: A string representing the next video file name.
        """
        existing_videos = [f for f in os.listdir(output_folder) if f.startswith("video") and f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
        max_num = 0
        for video in existing_videos:
            try:
                num = int(''.join(filter(str.isdigit, os.path.splitext(video)[0])))
                if num > max_num:
                    max_num = num
            except ValueError:
                continue
        next_num = max_num + 1
        return f"video{next_num}.mp4"

    def trim_video(self, input_path, output_folder='test', start_ms=None, end_ms=None, entire_clip=False):
        """
        Trims a segment from the input video based on start and end times in milliseconds,
        or copies the entire video if `entire_clip` is set to True.
        Saves the processed video with a sequential name in the specified output folder.

        :param input_path: Path to the input video file.
        :param output_folder: Folder to save the processed video. Defaults to 'test'.
        :param start_ms: Start time in milliseconds. Required if entire_clip is False.
        :param end_ms: End time in milliseconds. Required if entire_clip is False.
        :param entire_clip: If True, copies the entire video without processing. Defaults to False.
        """
        # Validate input file existence
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"The input video file '{input_path}' does not exist.")

        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)

        # Determine output file name
        output_filename = self._get_next_video_name(output_folder)
        output_path = os.path.join(output_folder, output_filename)

        if entire_clip:
            try:
                shutil.copy2(input_path, output_path)
                print(f"Entire video copied to '{output_path}'")
            except Exception as e:
                print(f"An error occurred while copying the video: {e}")
            return

        # If not copying the entire clip, proceed with trimming
        if start_ms is None or end_ms is None:
            raise ValueError("start_ms and end_ms must be provided if entire_clip is False.")

        # Validate time inputs
        if start_ms < 0 or end_ms < 0:
            raise ValueError("Start and end times must be non-negative integers representing milliseconds.")
        if start_ms >= end_ms:
            raise ValueError("Start time must be less than end time.")

        # Convert milliseconds to seconds for moviepy
        start_time = start_ms / 1000.0
        end_time = end_ms / 1000.0

        try:
            # Load the video clip
            with VideoFileClip(input_path) as video:
                video_duration = video.duration  # in seconds

                # Validate end_time against video duration
                if start_time > video_duration:
                    raise ValueError("Start time exceeds video duration.")
                if end_time > video_duration:
                    print("End time exceeds video duration. Trimming up to the video's end.")
                    end_time = video_duration

                # Trim the video
                trimmed_clip = video.subclip(start_time, end_time)

                # Write the trimmed clip to the output path
                trimmed_clip.write_videofile(
                    output_path,
                    codec="libx264",          # Video codec
                    audio_codec="aac",        # Audio codec
                    temp_audiofile="temp-audio.m4a",
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )

            print(f"Trimmed video {start_ms} - {end_ms} saved to '{output_path}'")

        except Exception as e:
            print(f"An error occurred while processing the video: {e}")
