import os
import subprocess
import json
import sys

class Combine_vids:

    def get_video_resolution(self, video_path):
        """
        Retrieves the width and height of the video using FFprobe.

        Args:
            video_path (str): Path to the video file.

        Returns:
            tuple: (width, height) of the video.

        Raises:
            Exception: If FFprobe fails or the video stream is not found.
        """
        command = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'json',
            video_path
        ]
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            info = json.loads(result.stdout)
            width = info['streams'][0]['width']
            height = info['streams'][0]['height']
            return width, height
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFprobe error for file {video_path}: {e.stderr}") from e
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise Exception(f"Unable to parse FFprobe output for file {video_path}") from e

    def crop_and_join_videos(self, female_path, male_path, output_path):
        """
        Crops the left half of the female video and the right half of the male video,
        then joins them side-by-side into the output video.

        Args:
            female_path (str): Path to female.mp4.
            male_path (str): Path to male.mp4.
            output_path (str): Path to save the joined output video.

        Raises:
            ValueError: If video resolutions are incompatible.
        """
        # Get resolutions
        female_width, female_height = self.get_video_resolution(female_path)
        male_width, male_height = self.get_video_resolution(male_path)

        print(f"Female video resolution: {female_width}x{female_height}")
        print(f"Male video resolution: {male_width}x{male_height}")

        # Ensure both videos have the same height
        if female_height != male_height:
            raise ValueError("Both videos must have the same height. Please resize them to match.")

        # Calculate crop parameters
        female_crop_width = female_width // 2
        female_crop_height = female_height
        female_crop_x = 0  # Left half starts at x=0
        female_crop_y = 0

        male_crop_width = male_width // 2
        male_crop_height = male_height
        male_crop_x = male_width // 2  # Right half starts at x=width/2
        male_crop_y = 0

        print(f"Cropping female.mp4: width={female_crop_width}, height={female_crop_height}, x={female_crop_x}, y={female_crop_y}")
        print(f"Cropping male.mp4: width={male_crop_width}, height={male_crop_height}, x={male_crop_x}, y={male_crop_y}")

        # Construct FFmpeg filter_complex string
        filter_complex = (
            f"[0:v]crop={female_crop_width}:{female_crop_height}:{female_crop_x}:{female_crop_y}[left];"
            f"[1:v]crop={male_crop_width}:{male_crop_height}:{male_crop_x}:{male_crop_y}[right];"
            f"[left][right]hstack=inputs=2[output]"
        )

        # Construct the full FFmpeg command
        command = [
            'ffmpeg',
            '-i', female_path,
            '-i', male_path,
            '-filter_complex', filter_complex,
            '-map', '[output]',
            '-c:v', 'libx264',  # Video codec
            '-crf', '23',        # Quality parameter (lower is better quality)
            '-preset', 'veryfast',# Encoding speed vs compression trade-off
            '-c:a', 'copy',      # Copy audio streams directly
            output_path
        ]

        print("Executing FFmpeg command:")
        print(' '.join(command))

        try:
            # Execute the FFmpeg command
            subprocess.run(command, check=True)
            print(f"Successfully saved the joined video to {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg failed with error: {e.stderr}")
            sys.exit(1)

    def run_combine(self):
        # Define paths
        input_folder = 'test'
        female_video = os.path.join(input_folder, 'female.mp4')
        male_video = os.path.join(input_folder, 'male.mp4')
        output_video = os.path.join('combined_video', 'combined_video.mp4')

        # Check if input files exist
        if not os.path.isfile(female_video):
            print(f"Error: File {female_video} does not exist.")
            sys.exit(1)
        if not os.path.isfile(male_video):
            print(f"Error: File {male_video} does not exist.")
            sys.exit(1)

        # Perform cropping and joining
        try:
            self.crop_and_join_videos(female_video, male_video, output_video)
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)
