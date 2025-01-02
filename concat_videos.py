import os
import re
import uuid
import shutil
from math import ceil
from moviepy.editor import VideoFileClip, concatenate_videoclips

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

    def concatenate_videos_in_chunks(self, video_paths, output_path, progress_prefix=""):
        """
        Concatenate the given list of video_paths into output_path using chunked approach.
        """
        if not video_paths:
            print(f"{progress_prefix}No videos to concatenate.")
            return

        # If the number of videos <= chunk_size, do a direct merge:
        if len(video_paths) <= self.chunk_size:
            self._merge_clips(video_paths, output_path, progress_prefix=progress_prefix)
            return

        # Otherwise, merge in chunks to limit memory usage:
        # 1) Create temp folder for intermediate chunks
        temp_folder = f"temp_merge_{uuid.uuid4()}"
        os.makedirs(temp_folder, exist_ok=True)

        # 2) Merge each chunk to an intermediate file
        chunk_files = []
        total_chunks = ceil(len(video_paths) / self.chunk_size)
        chunk_count = 0

        for chunk_index, chunk in enumerate(self._chunkify(video_paths, self.chunk_size), start=1):
            chunk_output = os.path.join(temp_folder, f"chunk_{chunk_index}.mp4")
            chunk_files.append(chunk_output)

            chunk_count += 1
            print(f"{progress_prefix}Processing chunk {chunk_count}/{total_chunks}...")
            self._merge_clips(chunk, chunk_output, 
                              progress_prefix=f"{progress_prefix}  -> ")

        # 3) Merge the resulting chunk files into the final output (recursive approach)
        #    We reuse this same function, so it can again chunk if chunk_files are still too many.
        if len(chunk_files) == 1:
            # We only have 1 chunk file, just rename/move it to final output
            shutil.move(chunk_files[0], output_path)
        else:
            # Merge intermediate chunk files into final output
            self.concatenate_videos_in_chunks(chunk_files, output_path, 
                                              progress_prefix=f"{progress_prefix}(intermediate) ")

        # 4) Cleanup temp folder
        shutil.rmtree(temp_folder, ignore_errors=True)
        print(f"{progress_prefix}Final merged video saved: {output_path}")

    def _merge_clips(self, video_paths, output_path, progress_prefix=""):
        """
        Merge given video_paths at once and write to output_path.
        """
        clips = []
        total = len(video_paths)
        print(f"{progress_prefix}Merging {total} clip(s) into '{output_path}'...")

        for i, vp in enumerate(video_paths, start=1):
            print(f"{progress_prefix}  Loading clip {i}/{total}: {vp}")
            try:
                clip = VideoFileClip(vp)
                clips.append(clip)
            except Exception as e:
                print(f"{progress_prefix}  Error loading '{vp}': {e}")

        if not clips:
            print(f"{progress_prefix}No valid clips found, skipping merge.")
            return

        try:
            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        except Exception as e:
            print(f"{progress_prefix}Error during concatenation: {e}")
        finally:
            # Release resources
            for c in clips:
                c.close()
            if 'final_clip' in locals():
                final_clip.close()

    def concatenate_videos(self, folder_path, output_path):
        """
        Concatenates all .mp4 videos in the specified folder in natural order
        (via chunked merging) and saves the result to output_path.
        """
        # Get list of all .mp4 files in the folder
        video_files = [os.path.join(folder_path, f) 
                       for f in os.listdir(folder_path) 
                       if f.lower().endswith('.mp4')]

        if not video_files:
            print(f"No .mp4 files found in {folder_path}. Skipping...")
            return

        # Sort the video files using natural sorting
        video_files.sort(key=self.natural_sort_key)

        print(f"\nFound {len(video_files)} videos in '{folder_path}'.")
        for vf in video_files:
            print(f" - {os.path.basename(vf)}")

        # Concatenate in chunks to optimize memory usage
        self.concatenate_videos_in_chunks(video_files, output_path)

    def concat_vids(self):
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


