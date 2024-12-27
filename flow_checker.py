import os
from moviepy.editor import VideoFileClip

# Define the root directory
ROOT_DIR = 'animations'

# Define output directories
OUTPUT_DIR_MALE = 'flow/male'
OUTPUT_DIR_FEMALE = 'flow/female'

# Create output directories if they don't exist
os.makedirs(OUTPUT_DIR_MALE, exist_ok=True)
os.makedirs(OUTPUT_DIR_FEMALE, exist_ok=True)

def extract_frames(video_path, output_prefix):
    """
    Extract the first and last frames from the video and save them as PNG images.

    :param video_path: Path to the video file.
    :param output_prefix: Prefix for the output image files.
    """
    try:
        with VideoFileClip(video_path) as clip:
            # Extract first frame
            first_frame = clip.get_frame(0)
            first_frame_image = os.path.join(os.path.dirname(video_path), f"{output_prefix}_first.png")
            # Save first frame
            clip.save_frame(first_frame_image, t=0)
            
            # Extract last frame
            duration = clip.duration
            last_frame_image = os.path.join(os.path.dirname(video_path), f"{output_prefix}_last.png")
            # Save last frame
            clip.save_frame(last_frame_image, t=duration - 0.01)  # Slightly before the end to ensure frame capture

            print(f"Extracted frames for {video_path}")
    except Exception as e:
        print(f"Error processing {video_path}: {e}")

def process_videos():
    """
    Traverse the ROOT_DIR, process each video, and save frames to the appropriate output directories.
    """
    for gender_folder in os.listdir(ROOT_DIR):
        gender_path = os.path.join(ROOT_DIR, gender_folder)
        if not os.path.isdir(gender_path):
            continue

        # Determine output directory based on gender
        if gender_folder.lower() == 'man':
            output_dir = OUTPUT_DIR_MALE
        elif gender_folder.lower() == 'girl':
            output_dir = OUTPUT_DIR_FEMALE
        else:
            print(f"Unknown gender folder: {gender_folder}. Skipping...")
            continue

        # Traverse subdirectories
        for subdir, _, files in os.walk(gender_path):
            for file in files:
                if file.endswith('.mp4'):
                    video_path = os.path.join(subdir, file)
                    
                    # Extract action and lip movement from the file path
                    # Example path: animations/girl/nod/_with_lip_move.mp4
                    relative_path = os.path.relpath(video_path, ROOT_DIR)
                    parts = relative_path.split(os.sep)
                    
                    if len(parts) < 3:
                        print(f"Unexpected file structure: {video_path}. Skipping...")
                        continue
                    
                    action = parts[1]  # e.g., 'nod'
                    lip_move = parts[2].replace('.mp4', '')  # e.g., '_with_lip_move'

                    # Clean up the name
                    action_clean = action
                    lip_move_clean = lip_move.strip('_')  # remove leading underscore

                    # Create the output filename
                    output_prefix = f"{action_clean}_{lip_move_clean}"
                    
                    # Define the destination for images
                    # Example: male/nod_with_lip_move_first.png
                    first_image_path = os.path.join(output_dir, f"{output_prefix}_first.png")
                    last_image_path = os.path.join(output_dir, f"{output_prefix}_last.png")

                    # Extract and save frames
                    try:
                        with VideoFileClip(video_path) as clip:
                            # Save first frame
                            clip.save_frame(first_image_path, t=0)
                            
                            # Save last frame
                            duration = clip.duration
                            # Ensure t is within the duration
                            t_last = max(duration - 0.01, 0)
                            clip.save_frame(last_image_path, t=t_last)
                            
                            print(f"Saved frames for {video_path} to {output_dir}")
                    except Exception as e:
                        print(f"Failed to process {video_path}: {e}")

if __name__ == "__main__":
    process_videos()
    print("Frame extraction completed.")
