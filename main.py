import os
import shutil
from man import run_man
from girl import run_girl
from combine import run_combine
from re_encode import run_re_encode
from parser import get_total_seconds_from_transcript

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def read_checkpoint(checkpoint_file):
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            line = f.read().strip()
            if line.isdigit():
                return int(line)
    return 0

def write_checkpoint(checkpoint_file, segment_index):
    with open(checkpoint_file, 'w') as f:
        f.write(str(segment_index))

def concatenate_segments(segment_files, output_file):
    # Create a text file with the list of segment files for ffmpeg concat
    list_file = output_file + "_list.txt"
    with open(list_file, 'w') as f:
        for seg in segment_files:
            f.write(f"file '{seg}'\n")

    # Use ffmpeg to concatenate
    cmd = f"ffmpeg -y -f concat -safe 0 -i {list_file} -c copy {output_file}"
    print(f"[DEBUG] Running command: {cmd}")
    os.system(cmd)
    os.remove(list_file)

if __name__ == "__main__":
    transcript_file = 'transcript.txt'
    total_seconds = get_total_seconds_from_transcript(transcript_file)
    print("TOTAL SECONDS", total_seconds)

    # Determine number of segments
    segment_length = 60
    full_segments = total_seconds // segment_length
    remainder = total_seconds % segment_length

    if remainder > 0:
        total_segments = full_segments + 1
    else:
        total_segments = full_segments

    ensure_dir("segments")
    checkpoint_file = "segments/checkpoint.txt"
    start_segment = read_checkpoint(checkpoint_file)

    print(f"Computed segments: full_segments={full_segments}, remainder={remainder}, total_segments={total_segments}")
    print(f"Starting from segment {start_segment+1}")

    # Probabilities for man:
    sip_coffee_prob = 0.20
    nod_prob = 0.30
    yes_long_prob = 0.25
    fill_prob = 0.75

    # Probabilities for girl (no sip_coffee):
    girl_nod_prob = 0.30
    girl_yes_long_prob = 0.25
    girl_fill_prob = 0.75

<<<<<<< HEAD
    # # Re-encode animations if needed
    # print("Running re-encoding of animations...")
    # run_re_encode(base_dir="animations")
=======
    transcript_path = "transcript.txt"
    man_segments = []
    girl_segments = []
>>>>>>> my-temporary-work

    for i in range(start_segment, total_segments):
        seg_num = i + 1
        if i < full_segments:
            seg_duration = segment_length
        else:
            seg_duration = remainder

        # If total_seconds is a multiple of 60, remainder = 0, last segment won't exist
        # But since we already calculated total_segments accordingly, seg_duration should never be 0 here
        if seg_duration == 0:
            print(f"[DEBUG] Segment {seg_num} has zero duration. This shouldn't happen if total_segments is correct.")
            break

        print(f"Processing segment {seg_num}/{total_segments}, Duration: {seg_duration}s")

        # Run man segment
        run_man(seg_duration, transcript_path, "animations/man",
                sip_coffee_prob, nod_prob, yes_long_prob, fill_prob)
        man_segment_file = f"segments/man_segment_{seg_num}.mp4"
        if not os.path.exists("man.mp4"):
            print(f"[ERROR] man.mp4 not found after run_man for segment {seg_num}. Aborting.")
            break
        if os.path.exists(man_segment_file):
            os.remove(man_segment_file)
        shutil.move("man.mp4", man_segment_file)
        man_segments.append(man_segment_file)

        # Run girl segment
        run_girl(seg_duration, transcript_path, "animations",
                 girl_nod_prob, girl_yes_long_prob, girl_fill_prob)
        girl_segment_file = f"segments/girl_segment_{seg_num}.mp4"
        if not os.path.exists("girl.mp4"):
            print(f"[ERROR] girl.mp4 not found after run_girl for segment {seg_num}. Aborting.")
            break
        if os.path.exists(girl_segment_file):
            os.remove(girl_segment_file)
        shutil.move("girl.mp4", girl_segment_file)
        girl_segments.append(girl_segment_file)

        # Update checkpoint
        write_checkpoint(checkpoint_file, seg_num)
        print(f"[CHECKPOINT] Segment {seg_num} completed and checkpoint updated.")

    # After loop, print debug info about segments
    print("[DEBUG] Finished processing loop.")
    print(f"[DEBUG] man_segments found: {len(man_segments)}/{total_segments}")
    print(f"[DEBUG] girl_segments found: {len(girl_segments)}/{total_segments}")

    if len(man_segments) == total_segments and len(girl_segments) == total_segments:
        # Concatenate man segments
        print("Concatenating all man segments...")
        concatenate_segments(man_segments, "man.mp4")

        print("Concatenating all girl segments...")
        concatenate_segments(girl_segments, "girl.mp4")

        # Combine final videos
        print("Running video combination...")
        run_combine(girl_path='girl.mp4', man_path='man.mp4', output_path='combined_video.mp4')
        print("All segments combined successfully!")
    else:
        print("Process not completed. Some segments are missing or failed. Check the logs.")
