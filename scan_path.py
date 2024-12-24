#trying the duration calculatiuon with ffprobe



import os
import subprocess
import json

class ScanPath:
    def __init__(self):
        pass

    def get_video_duration_ffprobe(self, path):
        """
        Retrieve the duration of a video file using ffprobe.

        :param path: Path to the video file
        :return: Duration in seconds (float) or None if failed
        """
        try:
            # Run ffprobe command to get duration in JSON format
            result = subprocess.run(
                [
                    'ffprobe',
                    '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'json',
                    path
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                print(f"ffprobe error for '{path}': {result.stderr.strip()}")
                return None

            # Parse JSON output
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])
            return duration
        except Exception as e:
            print(f"Exception while getting duration for '{path}': {e}")
            return None

    def scan_animations_directory_with_duration_ms(self, base_path='animations'):
        """
        Scan the animations directory and collect video paths and durations.

        :param base_path: Base directory to scan
        :return: Dictionary with animation data
        """
        # Mapping from directory names to desired dictionary keys
        gender_map = {
            'man': 'male',
            'girl': 'female'
        }

        # Initialize the result dictionary
        animations_dict = {
            'male': {},
            'female': {}
        }

        # Verify that the base_path exists and is a directory
        if not os.path.isdir(base_path):
            raise ValueError(f"The directory '{base_path}' does not exist.")

        # Iterate over each gender directory (e.g., 'man', 'girl')
        for gender_dir in os.listdir(base_path):
            gender_path = os.path.join(base_path, gender_dir)

            # Skip if not a directory
            if not os.path.isdir(gender_path):
                continue

            # Map the directory name to 'male' or 'female'
            gender_key = gender_map.get(gender_dir.lower())
            if not gender_key:
                print(f"Warning: Unrecognized gender directory '{gender_dir}'. Skipping.")
                continue

            # Iterate over each animation type within the gender directory
            for animation_type in os.listdir(gender_path):
                animation_path = os.path.join(gender_path, animation_type)

                # Skip if not a directory
                if not os.path.isdir(animation_path):
                    continue

                # Initialize dictionary to hold paths and duration
                animation_info = {
                    'paths': [],
                    'duration_ms': None
                }

                # Define expected filenames
                with_lip_filename = '_with_lip_move.mp4'
                without_lip_filename = '_without_lip_move.mp4'

                # Construct full paths
                with_lip_path = os.path.join(animation_path, with_lip_filename)
                without_lip_path = os.path.join(animation_path, without_lip_filename)

                # Check if files exist and add to the list
                if os.path.isfile(with_lip_path):
                    animation_info['paths'].append(os.path.abspath(with_lip_path))
                else:
                    print(f"Warning: '{with_lip_filename}' not found in '{animation_path}'.")

                if os.path.isfile(without_lip_path):
                    animation_info['paths'].append(os.path.abspath(without_lip_path))
                else:
                    print(f"Warning: '{without_lip_filename}' not found in '{animation_path}'.")

                # Only proceed if both videos are found
                if len(animation_info['paths']) == 2:
                    durations = []
                    for path in animation_info['paths']:
                        duration = self.get_video_duration_ffprobe(path)
                        if duration is not None:
                            durations.append(duration)
                            print(f"Duration of '{os.path.basename(path)}': {duration} seconds")
                        else:
                            print(f"Error: Could not retrieve duration for '{path}'.")
                            durations.append(None)

                    # Check if both durations were successfully retrieved
                    if all(d is not None for d in durations):
                        if durations[0] == durations[1]:
                            animation_info['duration_ms'] = int(durations[0] * 1000)
                        else:
                            print(f"Warning: Durations for videos in '{animation_path}' do not match.")
                            # Decide on how to handle discrepancies
                            # Example: Use the maximum duration
                            max_duration = max(durations)
                            animation_info['duration_ms'] = int(max_duration * 1000)
                            print(f"Using maximum duration: {animation_info['duration_ms']} ms")
                    else:
                        print(f"Error: Could not retrieve both durations for '{animation_path}'. Setting duration_ms to None.")

                    # Add to the dictionary if duration is set
                    if animation_info['duration_ms'] is not None:
                        animations_dict[gender_key][animation_type] = animation_info
                    else:
                        print(f"Info: Duration not set for '{animation_type}' in '{gender_key}'. Skipping.")
                else:
                    print(f"Info: Incomplete videos for '{animation_type}' in '{gender_key}'. Skipping.")

        return animations_dict