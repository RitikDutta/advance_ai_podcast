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

    # Set end times for each segment
    for j in range(len(segments)-1):
        segments[j]['end_time'] = segments[j+1]['start_time']
    if segments:
        segments[-1]['end_time'] = total_duration
    return segments

def get_animations(root_dir):
    """
    Get animations, excluding 'sip_tea' for SPEAKER 1.
    """
    animations = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        with_lip_videos = [f for f in filenames if f.endswith('_with_lip_move.mp4')]
        for wl_file in with_lip_videos:
            without_lip_file = wl_file.replace('_with_lip_move.mp4', '_without_lip_move.mp4')
            if without_lip_file in filenames:
                with_lip_path = os.path.join(dirpath, wl_file)
                without_lip_path = os.path.join(dirpath, without_lip_file)

                with_lip_clip = VideoFileClip(with_lip_path)
                without_lip_clip = VideoFileClip(without_lip_path)

                anim_name = os.path.basename(wl_file).split("_with_lip_move.mp4")[0]
                if anim_name == 'sip_tea':  # Exclude sip_tea
                    continue

                if anim_name not in animations:
                    animations[anim_name] = []

                animations[anim_name].append({
                    'with_lip_move': with_lip_clip,
                    'without_lip_move': without_lip_clip,
                    'duration': with_lip_clip.duration
                })
    return animations

def weighted_random_choice(animations_dict, weights):
    """
    Selects an animation based on weighted probabilities.
    """
    weighted_list = []
    for anim_name, anim_list in animations_dict.items():
        weight = weights.get(anim_name, 1)
        weighted_list.extend(anim_list * weight)  # Extend list by weight
    return random.choice(weighted_list)

# Ask user for the final video duration
video_duration_str = input("Enter the desired final video duration in seconds (e.g., 60): ")
total_duration = float(video_duration_str)

print("Parsing transcript...")
segments = parse_transcript('transcript.txt', total_duration)

print("Collecting animations...")
animations = get_animations('animations')

if not animations:
    print("No animations found. Exiting.")
    exit()

# Define weights for each animation type (excluding 'sip_tea')
weights = {
    'yes_long': 2,  # 30%
    'nod': 2,       # 30%
    'fill': 7       # 70%
}

print("Building the video timeline...")
current_time = 0
current_animation = weighted_random_choice(animations, weights)
current_animation_position = 0
current_segment_index = 0
current_speaker = segments[current_segment_index]['speaker'] if segments else 'SPEAKER 2'
video_clips = []

while current_time < total_duration:
    if current_segment_index < len(segments):
        next_speaker_change_time = segments[current_segment_index]['end_time']
    else:
        next_speaker_change_time = total_duration

    current_animation_duration = current_animation['duration']
    time_remaining_in_animation = current_animation_duration - current_animation_position
    next_animation_end_time = current_time + time_remaining_in_animation

    next_event_time = min(next_speaker_change_time, next_animation_end_time, total_duration)
    duration = next_event_time - current_time

    # Syncing animations with SPEAKER 1
    if current_speaker == 'SPEAKER 1':
        source_clip = current_animation['with_lip_move']
    else:
        source_clip = current_animation['without_lip_move']

    # Extract subclip
    clip = source_clip.subclip(current_animation_position, current_animation_position + duration)
    video_clips.append(clip)

    current_time = next_event_time
    current_animation_position += duration

    if abs(current_time - next_speaker_change_time) < 0.001:
        if current_segment_index < len(segments):
            print(f"Speaker changed at {current_time:.2f}s")
            current_segment_index += 1
            if current_segment_index < len(segments):
                current_speaker = segments[current_segment_index]['speaker']
            else:
                current_speaker = 'SPEAKER 2'

    if abs(current_time - next_animation_end_time) < 0.001:
        print(f"Animation ended at {current_time:.2f}s, switching animation.")
        current_animation = weighted_random_choice(animations, weights)
        current_animation_position = 0

    if int(current_time) % 10 == 0:
        print(f"Progress: {current_time:.2f}/{total_duration:.2f} seconds")

print("Concatenating video clips...")
final_clip = concatenate_videoclips(video_clips, method="compose")

print("Saving final video...")
final_clip.write_videofile('girl.mp4', codec='libx264', audio_codec='aac')

# Close all animation clips
for anim_name, anim_list in animations.items():
    for anim in anim_list:
        anim['with_lip_move'].close()
        anim['without_lip_move'].close()

print("Process completed.")
