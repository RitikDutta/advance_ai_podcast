from moviepy.editor import VideoFileClip, clips_array

# Load the video clips
girl_clip = VideoFileClip('girl.mp4')
man_clip = VideoFileClip('man.mp4')

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

# Write the result to a file
final_clip.write_videofile('combined_video.mp4')

print("Videos have been combined and saved as 'combined_video.mp4'.")
