from transcript_helper import TranscriptHelper
from video_ops import VideoOps
from scan_path import ScanPath
import random
from common_utils import CommonUtils

scan_path = ScanPath()
helper = TranscriptHelper('transcript/transcript.txt')
video_ops = VideoOps()
picker = CommonUtils()

class Sequencer:
    def __init__(self, is_speaker1_man, iterations=0):
        self.iterations = iterations #using iterations to check temp
        self.is_speaker1_man = is_speaker1_man

    def aggregate_numbers(self, lst):
        result = []
        current_sum = 0
        for num in lst:
            current_sum += num
            result.append(current_sum)
        return result

    def get_turn_time(self):
        a = speaker1_durations = helper.duration_of_speaking_ms('Speaker 1')
        b = speaker2_durations = helper.duration_of_speaking_ms('Speaker 2')
        c = []
        def concat_turn_by_turn(a, b):
            for i in range(len(b)):
                c.append(a[i])
                c.append(b[i])
            return c

        turn_time = concat_turn_by_turn(a,b)

        turn_time = self.aggregate_numbers(turn_time)
        return turn_time

    def create_sequence(self, role):
        animations_dict = scan_path.scan_animations_directory_with_duration_ms('animations')

        # Initializations
        current_timings = 0
        timeline = []
        command = ''
        i = 0
        extra_time = 0

        trim_trigger = False
        speaker_timing = 0
        remaning_clip = 0

        # We’ll keep picking choice from these 4 options:

        if role=='male':
            possible_choices = ['yes_long', 'fill', 'sip_coffee', 'nod']
            weights = [0.10, 0.70, 0.10, 0.10]
        else:
            possible_choices = ['yes_long', 'fill', 'nod']
            weights = [0.10, 0.80, 0.10]
        clip_left = 0

        turn_time = self.get_turn_time()

        if self.iterations==0:
            self.iterations = len(turn_time)


        if self.is_speaker1_man:
            with_lip = 0
            without_lip = 1
        else:
            with_lip = 1
            without_lip = 0

        while i < len(turn_time): #and i < self.iterations:
            print('-' * 20)

            # 1) Pick an animation or use remaining clipped video:
            if remaning_clip != 0:
                # Continue using the last remaining video
                animation_duration = remaning_clip
                print(f"picked {choice} of {animation_duration} ms (the last remaining video)\n")
            else:
                # Otherwise pick a new random (or fixed index) choice
                choice = picker.run_weighted_picker(possible_choices, weights)  
                animation_duration = animations_dict[role][choice]['duration_ms']
                print(f"picked {choice} of {animation_duration} ms through random choice\n")

            #setting a variable to track how much of clip is used
            if clip_left==0:
                clip_left = animation_duration

            # 2) Print the remaining speaking time
            print(f"remaining speaking time of speaker1 to switch actions "
                  f"{turn_time[i]} - {current_timings} = {turn_time[i] - current_timings}\n")
            print("now going inside the condition...\n")

            # 3) If the entire animation fits before the speaker switches
            if current_timings + animation_duration < turn_time[i]:
                current_timings += animation_duration

                # Determine if speaker i is “with lip move” or “without lip move”
                if i % 2 == 0:
                    if remaning_clip==0:
                        print(f"adding {choice} with lip move from {remaning_clip} to {animations_dict[role][choice]['duration_ms']}, current time is now {current_timings}\n")
                        print('remaining clip ', remaning_clip)
                        # Now adding the the actual video to workspace folder
                        video_ops.trim_video(output_folder = f'test/{role}', input_path=animations_dict[role][choice]['paths'][with_lip], entire_clip=True)
                    else:
                        print(f"adding {choice} with lip move from {animations_dict[role][choice]['duration_ms'] - remaning_clip} to {animations_dict[role][choice]['duration_ms']}, current time is now {current_timings}\n")
                        print('remaining clip ', remaning_clip)
                        # Now adding the the actual video to workspace folder
                        video_ops.trim_video(output_folder = f'test/{role}', input_path=animations_dict[role][choice]['paths'][with_lip], start_ms=animations_dict[role][choice]['duration_ms'] - remaning_clip, end_ms=animations_dict[role][choice]['duration_ms'])
                else:
                    if remaning_clip==0:
                        print(f"adding {choice} without lip move from {remaning_clip} to {animations_dict[role][choice]['duration_ms']}, current time is now {current_timings}\n")
                        print('remaining clip ', remaning_clip)
                        # Now adding the the actual video to workspace folder
                        video_ops.trim_video(output_folder = f'test/{role}', input_path=animations_dict[role][choice]['paths'][without_lip], entire_clip=True)
                    else:
                        print(f"adding {choice} without lip move from {animations_dict[role][choice]['duration_ms'] - remaning_clip} to {animations_dict[role][choice]['duration_ms']}, current time is now {current_timings}\n")
                        print('remaining clip ', remaning_clip)
                        # Now adding the the actual video to workspace folder
                        video_ops.trim_video(output_folder = f'test/{role}', input_path=animations_dict[role][choice]['paths'][without_lip], start_ms=animations_dict[role][choice]['duration_ms'] - remaning_clip, end_ms=animations_dict[role][choice]['duration_ms'])


                print(f"and remaining time is {turn_time[i] - current_timings}\n")
                
                # Since we used the full clip, reset remaning_clip
                remaning_clip = 0
                trim_trigger = False

            else:
                # 4) The animation does NOT fit fully => we do “trimming” logic

                # We will trim the part that fits until speaker switch
                # leftover clip is what remains after the speaker switches
                leftover_time = turn_time[i] - current_timings
                new_remaning_clip = animation_duration - leftover_time

                # Print out the trimming info
                if i % 2 == 0: #determine if speaker 1 is speaking 
                    if trim_trigger==True:
                        print(f"trimming the with lip move video from ({animations_dict[role][choice]['duration_ms']}-{remaning_clip}) = {animations_dict[role][choice]['duration_ms']-remaning_clip} to {leftover_time + (animations_dict[role][choice]['duration_ms']-remaning_clip)} "
                              f"\n and {'setting' if not trim_trigger else 'unsetting'} the trim trigger "
                              f"\n and increment turn_time (i += 1)\n")

                        # Now Trimming the actual video
                        # Now adding the the actual video to workspace folder
                        video_ops.trim_video(output_folder = f'test/{role}', input_path=animations_dict[role][choice]['paths'][with_lip], start_ms=animations_dict[role][choice]['duration_ms']-remaning_clip, end_ms=(leftover_time + (animations_dict[role][choice]['duration_ms']-remaning_clip)))
                    else:
                        print(f"trimming the with lip move video from {remaning_clip} to {leftover_time + remaning_clip} "
                              f"\n and {'setting' if not trim_trigger else 'unsetting'} the trim trigger "
                              f"\n and increment turn_time (i += 1)\n")

                        # Now Trimming the actual video
                        # Now adding the the actual video to workspace folder
                        video_ops.trim_video(output_folder = f'test/{role}', input_path=animations_dict[role][choice]['paths'][with_lip], start_ms=remaning_clip, end_ms=(leftover_time + remaning_clip))

                else:
                    if trim_trigger==True:
                        print(f"trimming the without lip move video from ({animations_dict[role][choice]['duration_ms']}-{remaning_clip}) = {animations_dict[role][choice]['duration_ms']-remaning_clip} to {leftover_time + (animations_dict[role][choice]['duration_ms']-remaning_clip)} "
                              f"\n and {'setting' if not trim_trigger else 'unsetting'} the trim trigger "
                              f"\n and increment turn_time (i += 1)\n")

                        # Now Trimming the actual video
                        # Now adding the the actual video to workspace folder
                        video_ops.trim_video(output_folder = f'test/{role}', input_path=animations_dict[role][choice]['paths'][without_lip], start_ms=animations_dict[role][choice]['duration_ms']-remaning_clip, end_ms=(leftover_time + (animations_dict[role][choice]['duration_ms']-remaning_clip)))
                    else:
                        print(f"trimming the without lip move video from {remaning_clip} to {leftover_time + remaning_clip} "
                              f"\n and {'setting' if not trim_trigger else 'unsetting'} the trim trigger "
                              f"\n and increment turn_time (i += 1)\n")

                        # Now Trimming the actual video
                        # Now adding the the actual video to workspace folder
                        video_ops.trim_video(output_folder = f'test/{role}', input_path=animations_dict[role][choice]['paths'][without_lip], start_ms=remaning_clip, end_ms=(leftover_time + remaning_clip))


                remaning_clip = new_remaning_clip

                clip_left-=remaning_clip
                print(f"\n\n total clip used remain  = {clip_left - remaning_clip} \n\n")



                
                trim_trigger=True
                
                # Add the trimmed portion up to the speaker switch
                current_timings += leftover_time

                # “with lip move” or “without lip move”
                if i % 2 == 0:
                    print(f"adding {choice} with lip move, current time is now {current_timings}\n")
                else:
                    print(f"adding {choice} without lip move, current time is now {current_timings}\n")

                # Print the leftover
                print(f"setting the choice and animation duration = {remaning_clip} "
                      f"of remaining clip of {choice}\n")

                # Move to the next turn
                i += 1
                # Continue to the next iteration of the while loop
                # (We do not want to re-check the if/else with the same i)
                continue

            # 5) If we finished a turn exactly, you may want to increment i
            #    (depends on how you want to handle partial overlaps).
            if current_timings == turn_time[i]:
                i += 1

            # Move to the next iteration
            # If there's more turn_time left, the loop continues
