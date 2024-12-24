import os
import re
from moviepy.editor import VideoFileClip, concatenate_videoclips

def natural_sort_key(s):
    """
    Generates a key for natural sorting.
    Splits the string into a list of integers and non-integer substrings.
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]

def concatenate_videos(folder_path, output_path):
    """
    Concatenates all .mp4 videos in the specified folder in natural order and saves the result.

    :param folder_path: Path to the folder containing .mp4 videos.
    :param output_path: Path where the concatenated video will be saved.
    """
    # Get list of all .mp4 files in the folder
    video_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp4')]

    if not video_files:
        print(f"No .mp4 files found in {folder_path}. Skipping...")
        return

    # Sort the video files using natural sorting
    video_files.sort(key=natural_sort_key)

    print(f"\nFound {len(video_files)} videos in '{folder_path}'. Processing in the following order:")
    for vf in video_files:
        print(f" - {vf}")

    clips = []
    for video in video_files:
        video_path = os.path.join(folder_path, video)
        try:
            clip = VideoFileClip(video_path)
            clips.append(clip)
            print(f"Loaded '{video_path}' successfully.")
        except Exception as e:
            print(f"Error loading '{video_path}': {e}")

    if not clips:
        print(f"No valid video clips to concatenate in '{folder_path}'. Skipping...")
        return

    # Concatenate clips
    try:
        print(f"Concatenating {len(clips)} clips...")
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        print(f"Saved concatenated video to '{output_path}'.")
    except Exception as e:
        print(f"Error concatenating videos in '{folder_path}': {e}")
    finally:
        # Close all clips to release resources
        for clip in clips:
            clip.close()
        if 'final_clip' in locals():
            final_clip.close()

def main():
    test_folder = "test"  # Adjust the path if necessary
    categories = ["male", "female"]

    for category in categories:
        input_folder = os.path.join(test_folder, category)
        output_video = os.path.join(test_folder, f"{category}.mp4")
        
        if not os.path.exists(input_folder):
            print(f"Folder '{input_folder}' does not exist. Skipping '{category}' category.")
            continue
        
        concatenate_videos(input_folder, output_video)

if __name__ == "__main__":
    main()
