import os
import random
from moviepy.editor import VideoFileClip, concatenate_videoclips

def parse_timestamp(ts_str):
    h, m, s, ms = ts_str.strip().split(':')
    total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0
    return total_seconds

def parse_transcript(filename, total_duration):
    segments = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('SPEAKER'):
            parts = line.split()
            speaker = parts[0] + ' ' + parts[1]
            timestamp = parts[2]
            start_time = parse_timestamp(timestamp)
            i += 1
            text = ''
            while i < len(lines) and not lines[i].startswith('SPEAKER'):
                text += lines[i]
                i += 1
            segments.append({'speaker': speaker, 'start_time': start_time, 'text': text})
        else:
            i += 1

    # Set end times
    for j in range(len(segments)-1):
        segments[j]['end_time'] = segments[j+1]['start_time']
    if segments:
        segments[-1]['end_time'] = total_duration
    return segments

def get_animations(root_dir):
    """
    Collect pairs of animations (with and without lip move) from the folder.
    We'll store them in a dictionary keyed by their base name: coffee, nod, fill, yes_long.
    """
    animations_by_name = {
        'coffee': None,
        'nod': None,
        'yes_long': None,
        'fill': None
    }

    # Look through the directory and find the pairs
    for filename in os.listdir(root_dir):
        if filename.endswith('_with_lip_move.mp4'):
            base_name = filename.replace('_with_lip_move.mp4', '')
            without_name = base_name + '_without_lip_move.mp4'
            with_path = os.path.join(root_dir, filename)
            without_path = os.path.join(root_dir, without_name)
            
            # Ensure we have the corresponding without_lip_move file
            if os.path.exists(without_path):
                with_clip = VideoFileClip(with_path)
                without_clip = VideoFileClip(without_path)
                
                # Assign to the correct key
                if base_name in animations_by_name:
                    animations_by_name[base_name] = {
                        'with_lip_move': with_clip,
                        'without_lip_move': without_clip,
                        'duration': with_clip.duration
                    }

    # Filter out any entries that didn't get properly assigned
    animations = [val for val in animations_by_name.values() if val is not None]
    return animations_by_name

# Ask user for the final video duration
video_duration_str = 60
total_duration = float(video_duration_str)

print("Parsing transcript...")
segments = parse_transcript('transcript.txt', total_duration)

print("Collecting animations...")
animations_by_name = get_animations('animations')

# Verify we have at least one animation
available_animations = [name for name, val in animations_by_name.items() if val is not None]
if not available_animations:
    print("No animations found. Exiting.")
    exit()

print("Building the video timeline...")

# Weights for each animation type (treating given percentages as weights)
animation_types = ['coffee', 'nod', 'yes_long', 'fill']
weights = [0.1, 0.25, 0.2, 0.9]  # coffee=10%, nod=25%, yes_long=20%, fill=90% (relative weights)

def pick_new_animation():
    # Pick a type based on the provided probabilities
    chosen_type = random.choices(animation_types, weights=weights, k=1)[0]
    # Ensure the chosen type is available. If not, pick again until we get an available one.
    # (In case some animations aren't available)
    while chosen_type not in available_animations:
        chosen_type = random.choices(animation_types, weights=weights, k=1)[0]
    return animations_by_name[chosen_type]

current_time = 0
current_animation = pick_new_animation()
current_animation_position = 0
current_segment_index = 0
current_speaker = segments[current_segment_index]['speaker'] if segments else 'SPEAKER 1'
video_clips = []

while current_time < total_duration:
    # Determine the next speaker change time
    if current_segment_index < len(segments):
        next_speaker_change_time = segments[current_segment_index]['end_time']
    else:
        next_speaker_change_time = total_duration

    # Determine when the current animation ends
    current_animation_duration = current_animation['duration']
    time_remaining_in_animation = current_animation_duration - current_animation_position
    next_animation_end_time = current_time + time_remaining_in_animation

    # Determine the next event time
    next_event_time = min(next_speaker_change_time, next_animation_end_time, total_duration)
    duration = next_event_time - current_time

    # Select the appropriate video version based on who is speaking
    if current_speaker == 'SPEAKER 2':
        source_clip = current_animation['with_lip_move']
    else:
        source_clip = current_animation['without_lip_move']

    print(f"Adding clip from {current_time:.2f}s to {next_event_time:.2f}s using {os.path.basename(source_clip.filename)}")

    clip = source_clip.subclip(current_animation_position, current_animation_position + duration)
    video_clips.append(clip)

    current_time = next_event_time
    current_animation_position += duration

    # Handle speaker change
    if abs(current_time - next_speaker_change_time) < 0.001:
        if current_segment_index < len(segments):
            print(f"Speaker changed at {current_time:.2f}s")
            current_segment_index += 1
            if current_segment_index < len(segments):
                current_speaker = segments[current_segment_index]['speaker']
            else:
                current_speaker = 'SPEAKER 1'

    # Handle animation end
    if abs(current_time - next_animation_end_time) < 0.001:
        print(f"Animation ended at {current_time:.2f}s, switching animation.")
        current_animation = pick_new_animation()
        current_animation_position = 0

    if int(current_time) % 10 == 0:
        print(f"Progress: {current_time:.2f}/{total_duration:.2f} seconds")

print("Concatenating video clips...")
final_clip = concatenate_videoclips(video_clips, method="compose")

print("Saving final video...")
final_clip.write_videofile('man.mp4', codec='libx264', audio_codec='aac')

# Close all clips after the video is saved
for anim in animations_by_name.values():
    if anim is not None:
        anim['with_lip_move'].close()
        anim['without_lip_move'].close()

print("Process completed.")
