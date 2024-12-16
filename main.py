from man import run_man
from girl import run_girl
from combine import run_combine
from re_encode import run_re_encode

from parser import get_total_seconds_from_transcript


if __name__ == "__main__":

    transcript_file = 'transcript.txt'
    total_seconds = get_total_seconds_from_transcript(transcript_file)
    print("TOTAL SECONDS", total_seconds)

    video_duration_str = total_seconds
    total_duration = float(video_duration_str)
    transcript_path = "transcript.txt"

    # Probabilities for man:
    sip_coffee_prob = 0.20
    nod_prob = 0.30
    yes_long_prob = 0.25
    fill_prob = 0.75

    # Probabilities for girl (no sip_coffee):
    girl_nod_prob = 0.30
    girl_yes_long_prob = 0.25
    girl_fill_prob = 0.75

    # # Re-encode animations if needed
    # print("Running re-encoding of animations...")
    # run_re_encode(base_dir="animations")

    # Run 'man' video generation with probabilities
    print("Running man video creation...")
    run_man(total_duration, transcript_path, "animations/man",
            sip_coffee_prob, nod_prob, yes_long_prob, fill_prob)

    # Run 'girl' video generation with probabilities (no sip_coffee)
    print("Running girl video creation...")
    run_girl(total_duration, transcript_path, "animations",
             girl_nod_prob, girl_yes_long_prob, girl_fill_prob)

    # Combine the two videos
    print("Running video combination...")
    run_combine(girl_path='girl.mp4', man_path='man.mp4', output_path='combined_video.mp4')

