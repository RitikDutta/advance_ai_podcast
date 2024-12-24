import os
import re
from moviepy.editor import VideoFileClip, concatenate_videoclips

def get_sorted_video_files(folder_path, prefix='video', extension='.mp4'):
    """
    Retrieves and sorts video files from the specified folder based on numerical order.

    :param folder_path: Path to the folder containing video files.
    :param prefix: Prefix of the video files (default is 'video').
    :param extension: Extension of the video files (default is '.mp4').
    :return: Sorted list of video file paths.
    """
    # List all files in the folder
    all_files = os.listdir(folder_path)
    
    # Regex pattern to extract the number from filenames like 'video1.mp4'
    pattern = re.compile(rf'^{prefix}(\d+){re.escape(extension)}$')
    
    video_files = []
    for file in all_files:
        match = pattern.match(file)
        if match:
            number = int(match.group(1))
            video_files.append((number, os.path.join(folder_path, file)))
    
    # Sort the list based on the extracted number
    video_files.sort(key=lambda x: x[0])
    
    # Return only the file paths in order
    return [file_path for _, file_path in video_files]

def combine_videos(folder_path, output_path, prefix='video', extension='.mp4'):
    """
    Combines all videos in the specified folder into a single video file.

    :param folder_path: Path to the folder containing video files.
    :param output_path: Path for the output combined video.
    :param prefix: Prefix of the video files (default is 'video').
    :param extension: Extension of the video files (default is '.mp4').
    """
    print("Gathering video files...")
    video_files = get_sorted_video_files(folder_path, prefix, extension)
    
    if not video_files:
        print("No video files found with the specified naming convention.")
        return
    
    print(f"Found {len(video_files)} video files. Loading clips...")
    
    # Load all video clips
    clips = []
    for video_file in video_files:
        try:
            clip = VideoFileClip(video_file)
            clips.append(clip)
            print(f"Loaded {video_file}")
        except Exception as e:
            print(f"Error loading {video_file}: {e}")
    
    if not clips:
        print("No clips to concatenate.")
        return
    
    print("Concatenating clips...")
    try:
        final_clip = concatenate_videoclips(clips, method="compose")
    except Exception as e:
        print(f"Error during concatenation: {e}")
        return
    
    print(f"Writing the final video to {output_path}...")
    try:
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
        print("Video successfully combined!")
    except Exception as e:
        print(f"Error writing the video file: {e}")
    finally:
        # Close all clips to release resources
        for clip in clips:
            clip.close()
        if 'final_clip' in locals():
            final_clip.close()

if __name__ == "__main__":
    # Define the folder containing the videos and the output file name
    animations_folder = 'test'
    output_video = 'combined_video.mp4'
    
    combine_videos(animations_folder, output_video)
