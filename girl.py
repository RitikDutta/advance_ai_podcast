import os
import random
from moviepy.editor import VideoFileClip, concatenate_videoclips

def parse_timestamp(ts_str):
    h, m, s, ms = ts_str.strip().split(':')
    total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + float(ms) / 1000.0
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

def get_duration(video_path):
    clip = VideoFileClip(video_path)
    duration = clip.duration
    clip.close()
    return duration

def get_animations(root_dir):
    animations = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        with_lip_videos = [f for f in filenames if f.endswith('_with_lip_move.mp4')]
        for wl_file in with_lip_videos:
            # Skip coffee sip clips if any
            if "sip_coffee" in wl_file:
                continue
            without_lip_file = wl_file.replace('_with_lip_move.mp4', '_without_lip_move.mp4')
            if without_lip_file in filenames:
                with_lip_path = os.path.join(dirpath, wl_file)
                without_lip_path = os.path.join(dirpath, without_lip_file)

                with_lip_move_duration = get_duration(with_lip_path)

                animations.append({
                    'with_lip_move': with_lip_path,
                    'without_lip_move': without_lip_path,
                    'duration': with_lip_move_duration
                })
    return animations

def print_progress_bar(current, total, length=30):
    filled_len = int(length * current / total)
    bar = '=' * filled_len + '-' * (length - filled_len)
    return f"[{bar}] {current:.2f}/{total:.2f}s"

def run_girl(total_duration, transcript_path, animation_path):
    print("============================================================")
    print("                  VIDEO CREATION TOOL                      ")
    print("============================================================")
    print(f"[INFO] Using total_duration={total_duration}, transcript={transcript_path}, animations={animation_path}")
    print("------------------------------------------------------------")

    print("[INFO] Parsing transcript...")
    segments = parse_transcript(transcript_path, total_duration)

    print("[INFO] Collecting animations...")
    animations = get_animations(animation_path)

    if not animations:
        print("[ERROR] No animations found. Exiting.")
        return

    print("[INFO] Animations loaded successfully.")
    print("------------------------------------------------------------")

    # Assign equal probability to all animations
    num_animations = len(animations)
    weights = [1.0 / num_animations] * num_animations

    print("[INFO] Assigned equal probability to each animation:")
    for i, anim in enumerate(animations):
        print(f"Animation {i+1}: {os.path.basename(anim['with_lip_move'])} & "
              f"{os.path.basename(anim['without_lip_move'])}, Probability: {weights[i]:.4f}")

    print("[INFO] Building the video timeline...")
    current_time = 0
    # Initially pick a random animation based on probability
    current_animation = random.choices(animations, weights=weights, k=1)[0]
    print(f"[INFO] Initial animation chosen: {os.path.basename(current_animation['with_lip_move'])} / "
          f"{os.path.basename(current_animation['without_lip_move'])}")
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
        if current_speaker == 'SPEAKER 1':
            video_path = current_animation['with_lip_move']
            clip_type = "_with_lip_move"
        else:
            video_path = current_animation['without_lip_move']
            clip_type = "_without_lip_move"

        print(f"[CLIP] Adding from {current_time:.2f}s to {next_event_time:.2f}s "
              f"({duration:.2f}s) using {os.path.basename(video_path)} [{clip_type}]")

        clip = VideoFileClip(video_path).subclip(current_animation_position, current_animation_position + duration)
        video_clips.append(clip)

        current_time = next_event_time
        current_animation_position += duration

        # Handle speaker change
        if abs(current_time - next_speaker_change_time) < 0.001:
            if current_segment_index < len(segments):
                old_speaker = current_speaker
                current_segment_index += 1
                if current_segment_index < len(segments):
                    current_speaker = segments[current_segment_index]['speaker']
                else:
                    current_speaker = 'SPEAKER 2'
                print("------------------------------------------------------------")
                print(f"[SPEAKER CHANGE] {old_speaker} --> {current_speaker} at {current_time:.2f}s")
                print("------------------------------------------------------------")
            else:
                current_speaker = 'SPEAKER 2'

        # Handle animation end (pick new animation based on probability)
        if abs(current_time - next_animation_end_time) < 0.001:
            print("------------------------------------------------------------")
            print(f"[ANIMATION ENDED] Switching to a new animation at {current_time:.2f}s")
            print("------------------------------------------------------------")
            current_animation = random.choices(animations, weights=weights, k=1)[0]
            print(f"[INFO] New animation chosen: {os.path.basename(current_animation['with_lip_move'])} / "
                  f"{os.path.basename(current_animation['without_lip_move'])}")
            current_animation_position = 0

        # Print progress every 10 seconds
        if int(current_time) % 10 == 0:
            progress = print_progress_bar(current_time, total_duration)
            print(f"[PROGRESS] {progress}")

    print("------------------------------------------------------------")
    print("[INFO] Concatenating video clips...")
    final_clip = concatenate_videoclips(video_clips, method="compose")

    print("[INFO] Rendering final video...")
    final_clip.write_videofile('girl.mp4', codec='libx264', audio_codec='aac')

    # Close all loaded clips
    for anim in animations:
        # Animations here were loaded as paths, no preopened clips,
        # if you adapt to preopen them like in man.py, then close them similarly.
        pass

    print("============================================================")
    print("          PROCESS COMPLETED SUCCESSFULLY!                   ")
    print("           Your video: girl.mp4 is ready!                   ")
    print("============================================================")
