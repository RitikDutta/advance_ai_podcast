import subprocess
from pathlib import Path
import argparse
import sys


class Audio_mixer:
    def join_audio_video_ffmpeg(self, video_path, audio_path, output_path, audio_start_time=0):
        """
        Joins a WAV audio file with a video file using FFmpeg.

        :param video_path: Path to the input video file.
        :param audio_path: Path to the input WAV audio file.
        :param output_path: Path where the output video will be saved.
        :param audio_start_time: Time (in seconds) at which the audio should start in the video.
        """
        try:
            # Build the FFmpeg command
            ffmpeg_cmd = [
                'ffmpeg',
                '-y',                       # Overwrite output files without asking
                '-i', str(video_path),      # Input video
                '-i', str(audio_path),      # Input audio
                '-c:v', 'copy',             # Copy the video stream without re-encoding
                '-c:a', 'aac',              # Encode audio to AAC
                '-strict', 'experimental',  # Allow experimental codecs (if needed)
                '-map', '0:v:0',            # Map the first video stream
                '-map', '1:a:0',            # Map the first audio stream
                '-shortest',                # Finish encoding when the shortest input ends
                str(output_path)            # Output file
            ]

            # If audio_start_time is specified, add the -ss parameter for audio input
            if audio_start_time > 0:
                # Insert the -ss parameter before the audio input
                ffmpeg_cmd.insert(4, '-ss')
                ffmpeg_cmd.insert(5, str(audio_start_time))

            print(f"\n[Info] Running FFmpeg command for '{audio_path.name}':")
            print(' '.join(ffmpeg_cmd))

            # Execute the FFmpeg command
            process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Capture and print FFmpeg output in real-time
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())

            return_code = process.poll()
            if return_code != 0:
                print(f"[Error] FFmpeg exited with code {return_code} for '{audio_path.name}'.")
            else:
                print(f"[Success] Created '{output_path.name}' successfully.")

        except Exception as e:
            print(f"[Exception] An error occurred while processing '{audio_path.name}': {e}")

    def mix_audio(self):
        parser = argparse.ArgumentParser(description="Join a '_modified' WAV audio file from 'audio' folder with 'combined_video/combined_video.mp4'.")
        parser.add_argument(
            '--video',
            type=str,
            default='combined_video/combined_video.mp4',
            help="Path to the input video file (default: 'combined_video/combined_video.mp4')."
        )
        parser.add_argument(
            '--audio_folder',
            type=str,
            default='audio',
            help="Path to the folder containing WAV audio files (default: 'audio')."
        )
        parser.add_argument(
            '--output_folder',
            type=str,
            default='output',
            help="Path to the folder where output videos will be saved (default: 'output')."
        )
        parser.add_argument(
            '--audio_start',
            type=float,
            default=0,
            help="Start time for the audio in the video (in seconds, default: 0)."
        )
        parser.add_argument(
            '--audio_extension',
            type=str,
            default='.wav',
            help="Audio file extension to look for (default: '.wav')."
        )

        args = parser.parse_args()

        video_path = Path(args.video)
        audio_folder = Path(args.audio_folder)
        output_folder = Path(args.output_folder)
        audio_start_time = args.audio_start
        audio_extension = args.audio_extension.lower()

        # Validate video file
        if not video_path.is_file():
            print(f"[Error] The video file '{video_path}' does not exist.")
            sys.exit(1)

        # Validate audio folder
        if not audio_folder.is_dir():
            print(f"[Error] The audio folder '{audio_folder}' does not exist.")
            sys.exit(1)

        # Create output folder if it doesn't exist
        if not output_folder.exists():
            print(f"[Info] The output folder '{output_folder}' does not exist. Creating it.")
            output_folder.mkdir(parents=True, exist_ok=True)

        # Search for the '_modified' audio file
        modified_audio_files = sorted(audio_folder.glob(f'*_modified{audio_extension}'))

        if not modified_audio_files:
            print(f"[Error] No audio files with suffix '_modified{audio_extension}' found in '{audio_folder}'.")
            sys.exit(1)
        elif len(modified_audio_files) > 1:
            print(f"[Error] Multiple audio files with suffix '_modified{audio_extension}' found in '{audio_folder}'. Please ensure only one exists.")
            sys.exit(1)

        modified_audio_file = modified_audio_files[0]
        print(f"\n[Info] Found modified audio file: '{modified_audio_file.name}'")
        print(f"[Info] Output videos will be saved in '{output_folder}'.")

        # Define the output video filename
        # Example: name_modified -> name_modified_output.mp4
        base_name = modified_audio_file.stem  # e.g., 'name_modified'
        output_filename = f"{base_name}_output.mp4"
        output_path = output_folder / output_filename

        # Join audio and video
        self.join_audio_video_ffmpeg(video_path, modified_audio_file, output_path, audio_start_time)


if __name__ == "__main__":
    mixer = AudioMixer()
    mixer.mix_audio()
