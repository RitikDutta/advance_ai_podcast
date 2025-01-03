from sequencer import Sequencer
from concat_videos import Concat_vids
from combine import Combine_vids
from audio_mixer import Audio_mixer
from generate_title_desc import Generate_title
from youtube_upload import YouTubeUploader
from parser import Time_parser
from audio_mod import Audio_mod
import sys

# total_time = Time_parser().get_total_seconds_from_transcript() * 1000

# print('\ntotal_time\n', total_time)


sequencer = Sequencer(2, True)
sequencer.create_sequence('female')

sequencer2 = Sequencer(2, False)
sequencer2.create_sequence('male')

Concat_vids(200).concat_vids()

Combine_vids().run_combine()

Audio_mod().process_audio_files()

Audio_mixer().mix_audio()

title, desc = Generate_title().generate_content()

print(f'Uploading to Youtube ... \n\n {title} \n\n\n {desc}')

uploader = YouTubeUploader()
uploader.authenticate()
try:
    uploader.upload_video(
        file_path="output/test.mp4",  # Required
        title=title,            # Required
        description=desc,  # Required
        category="24",                       # 24 Entertainment"
        keywords="python,youtube,upload",     # Optional, default is ""
        privacy_status="public",             # Optional, default is "public"
    )
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)