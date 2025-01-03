import os
import re
import uuid
import shutil
import subprocess
from math import ceil
from tqdm import tqdm  # pip install tqdm

class Concat_vids:

    def __init__(self, chunk_size=5):
        """
        :param chunk_size: Number of videos to concatenate at a time
                           before writing intermediate output. Adjust
                           based on your available RAM and video sizes.
        """
        self.chunk_size = chunk_size

    def natural_sort_key(self, s):
        """
        Generates a key for natural sorting.
        Splits the string into a list of integers and non-integer substrings.
        """
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', s)]

    def _chunkify(self, lst, n):
        """
        Yield successive n-sized chunks from list lst.
        """
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def concatenate_videos_in_chunks(self, video_paths, output_path):
        """
        Concatenate the given list of video_paths into output_path using chunked approach.
        Uses a recursive approach to handle large sets of videos.
        """
        if not video_paths:
            print("No videos to concatenate.")
            return

        # If the number of videos <= chunk_size, do a direct merge:
        if len(video_paths) <= self.chunk_size:
            self._merge_clips(video_paths, output_path)
            return

        # Otherwise, merge in chunks to limit memory usage:
        temp_folder = f"temp_merge_{uuid.uuid4()}"
        os.makedirs(temp_folder, exist_ok=True)

        chunk_files = []
        total_chunks = ceil(len(video_paths) / self.chunk_size)

        for chunk_index, chunk in enumerate(self._chunkify(video_paths, self.chunk_size), start=1):
            chunk_output = os.path.join(temp_folder, f"chunk_{chunk_index}.mp4")
            chunk_files.append(chunk_output)
            self._merge_clips(chunk, chunk_output)

        # If there's only one intermediate file after chunk-merge, just move it
        if len(chunk_files) == 1:
            shutil.move(chunk_files[0], output_path)
        else:
            # Merge intermediate chunk files into final output
            self.concatenate_videos_in_chunks(chunk_files, output_path)

        shutil.rmtree(temp_folder, ignore_errors=True)

    def _merge_clips(self, video_paths, output_path):
        """
        Merge given video_paths at once and write to output_path using ffmpeg.
        This uses the concat demuxer for precise timing and re-encodes
        using libx264 (veryfast preset) and AAC to ensure consistent output.
        """
        if not video_paths:
            return

        list_file = os.path.join(
            os.path.dirname(os.path.abspath(output_path)) or '.',
            f"concat_list_{uuid.uuid4()}.txt"
        )

        # Generate the concat list file
        with open(list_file, 'w', encoding='utf-8') as f:
            for vp in video_paths:
                f.write(f"file '{os.path.abspath(vp)}'\n")

        # We can show a short progress bar for reading each clip's path
        # even though ffmpeg's internal progress isn't easily trackable
        with tqdm(total=len(video_paths), desc=f"Merging to {os.path.basename(output_path)}", unit="videos") as pbar:
            for _ in video_paths:
                # We won't individually re-encode each file here,
                # but let's simulate progress for user feedback
                pbar.update(1)

        cmd = [
            'ffmpeg',
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file,
            '-c:v', 'libx264',
            '-preset', 'veryfast',   # Faster encoding preset
            '-crf', '18',            # Adjust for desired quality (lower=better, bigger files)
            '-c:a', 'aac',
            '-movflags', '+faststart',
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print(f"Error during ffmpeg concatenation: {e}")
        finally:
            if os.path.exists(list_file):
                os.remove(list_file)

    def concatenate_videos(self, folder_path, output_path):
        """
        Concatenates all .mp4 videos in the specified folder in natural order
        (via chunked merging) and saves the result to output_path.
        """
        # Gather mp4 files
        video_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith('.mp4')
        ]

        if not video_files:
            print(f"No .mp4 files found in {folder_path}. Skipping...")
            return

        video_files.sort(key=self.natural_sort_key)
        print(f"Found {len(video_files)} .mp4 files to concatenate.")
        self.concatenate_videos_in_chunks(video_files, output_path)
        print(f"Final merged video saved at: {output_path}")

    def concat_vids(self):
        """
        Example usage for testing across 'male' and 'female' folders.
        Adjust 'test_folder' as needed.
        """
        test_folder = "test"  # Adjust if necessary
        categories = ["male", "female"]

        for category in categories:
            input_folder = os.path.join(test_folder, category)
            output_video = os.path.join(test_folder, f"{category}.mp4")

            if not os.path.exists(input_folder):
                print(f"Folder '{input_folder}' does not exist. Skipping '{category}' category.")
                continue

            print(f"\n--- Concatenating videos for: {category} ---")
            self.concatenate_videos(input_folder, output_video)
