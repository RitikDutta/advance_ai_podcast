import os
from moviepy.editor import VideoFileClip, clips_array

class Combine_vids:

    def run_combine(self, girl_path='test/female.mp4', man_path='test/male.mp4', output_path='combined_video/combined_video.mp4'):
        print("============================================================")
        print("[INFO] Combining the two videos side by side.")
        print(f"[INFO] Girl Video: {girl_path}")
        print(f"[INFO] Man Video: {man_path}")
        print("------------------------------------------------------------")

        girl_clip = VideoFileClip(girl_path)
        man_clip = VideoFileClip(man_path)

        # Ensure both clips have the same duration
        min_duration = min(girl_clip.duration, man_clip.duration)
        girl_clip = girl_clip.subclip(0, min_duration)
        man_clip = man_clip.subclip(0, min_duration)

        # Crop each clip to half its width
        girl_half = girl_clip.crop(x1=0, y1=0, width=girl_clip.w / 2, height=girl_clip.h)
        man_half = man_clip.crop(x1=man_clip.w / 2, y1=0, width=man_clip.w / 2, height=man_clip.h)

        # Resize clips to ensure they have the same height
        if girl_half.h != man_half.h:
            min_height = min(girl_half.h, man_half.h)
            girl_half = girl_half.resize(height=min_height)
            man_half = man_half.resize(height=min_height)

        # Combine the two halves side by side
        final_clip = clips_array([[girl_half, man_half]])

        print("[INFO] Rendering combined video...")
        final_clip.write_videofile(output_path)

        girl_clip.close()
        man_clip.close()
        print("============================================================")
        print("[INFO] Combined video created successfully!")
        print(f"[INFO] Output: {output_path}")
        print("============================================================")
