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
    # For last segment, set end time to total_duration
    if segments:
        segments[-1]['end_time'] = total_duration
    return segments

def get_duration(video_path):
    clip = VideoFileClip(video_path)
    duration = clip.duration
    clip.close()
    return duration

def get_animations(root_dir):
    animations = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if any(fname.endswith('_with_lip_move.mp4') for fname in filenames):
            for filename in filenames:
                if filename.endswith('_with_lip_move.mp4'):
                    without_lip_move = filename.replace('_with_lip_move.mp4', '_without_lip_move.mp4')
                    with_lip_move_path = os.path.join(dirpath, filename)
                    without_lip_move_path = os.path.join(dirpath, without_lip_move)
                    if os.path.exists(without_lip_move_path):
                        with_lip_move_duration = get_duration(with_lip_move_path)
                        animations.append({
                            'with_lip_move': with_lip_move_path,
                            'without_lip_move': without_lip_move_path,
                            'duration': with_lip_move_duration
                        })
    return animations

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

print("Building the video timeline...")
current_time = 0
current_animation = random.choice(animations)
current_animation_position = 0
current_segment_index = 0
current_speaker = segments[current_segment_index]['speaker'] if segments else 'SPEAKER 2'
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

    # Select the appropriate video version
    if current_speaker == 'SPEAKER 1':
        video_path = current_animation['with_lip_move']
    else:
        video_path = current_animation['without_lip_move']

    print(f"Adding clip from {current_time:.2f}s to {next_event_time:.2f}s using {os.path.basename(video_path)}")

    clip = VideoFileClip(video_path).subclip(current_animation_position, current_animation_position + duration)
    video_clips.append(clip)

    current_time = next_event_time
    current_animation_position += duration

    # Handle speaker change
    if current_time >= next_speaker_change_time:
        if current_segment_index < len(segments):
            print(f"Speaker changed at {current_time:.2f}s")
            current_segment_index += 1
            if current_segment_index < len(segments):
                current_speaker = segments[current_segment_index]['speaker']
            else:
                current_speaker = 'SPEAKER 2'  # Default to SPEAKER 2
        else:
            current_speaker = 'SPEAKER 2'  # Default to SPEAKER 2

    # Handle animation end
    if current_time >= next_animation_end_time:
        print(f"Animation ended at {current_time:.2f}s")
        current_animation = random.choice(animations)
        current_animation_position = 0

print("Concatenating video clips...")
final_clip = concatenate_videoclips(video_clips, method="compose")

print("Saving final video...")
final_clip.write_videofile('girl.mp4')

print("Process completed.")
