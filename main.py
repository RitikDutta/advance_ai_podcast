from man import run_man
from girl import run_girl
from combine import run_combine
from re_encode import run_re_encode

if __name__ == "__main__":
    # Take user input in main.py
    video_duration_str = input("Enter the desired final video duration in seconds (e.g., 60): ")
    total_duration = float(video_duration_str)

    transcript_path = "transcript.txt"
    
    # Run re-encoding of animations
    print("Running re-encoding of animations...")
    run_re_encode(base_dir="animations")

    # Run 'man' video generation
    print("Running man video creation...")
    run_man(total_duration, transcript_path, "animations/man")

    # Run 'girl' video generation
    print("Running girl video creation...")
    run_girl(total_duration, transcript_path, "animations")

    # Run combine
    print("Running video combination...")
    run_combine(girl_path='girl.mp4', man_path='man.mp4', output_path='combined_video.mp4')

