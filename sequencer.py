from transcript_helper import TranscriptHelper
from video_ops import VideoOps
from scan_path import ScanPath
import random

scan_path = ScanPath()
helper = TranscriptHelper('transcript.txt')
video_ops = VideoOps()


class Sequencer:
    def __init__(self, iterations, is_speaker1_man):
        self.iterations = iterations  # using iterations to check temp
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

        turn_time = concat_turn_by_turn(a, b)
        turn_time = self.aggregate_numbers(turn_time)
        return turn_time

    def create_sequence(self, role):
        animations_dict = scan_path.scan_animations_directory_with_duration_ms('animations')

        # ------------------------------
        #  A list to store each segment
        # ------------------------------
        timeline_segments = []
        segment_count = 1
        # ------------------------------

        current_timings = 0
        command = ''
        i = 0
        extra_time = 0

        trim_trigger = False
        speaker_timing = 0
        remaning_clip = 0

        # We’ll keep picking choice from these possible options:
        if role == 'male':
            possible_choices = ['yes_long', 'fill', 'sip_coffee', 'nod']
        else:
            possible_choices = ['yes_long', 'fill', 'nod']

        clip_left = 0
        turn_time = self.get_turn_time()

        if self.is_speaker1_man:
            with_lip = 0
            without_lip = 1
        else:
            with_lip = 1
            without_lip = 0

        # -------------------------
        while i < len(turn_time): # or i < self.iterations:
            print('-' * 20)

            # 1) Pick an animation or use remaining clipped video:
            if remaning_clip != 0:
                # Continue using the last remaining video
                animation_duration = remaning_clip
                print(f"picked {choice} of {animation_duration} ms (the last remaining video)\n")
            else:
                # Otherwise pick a new random choice
                choice = random.choice(possible_choices)
                animation_duration = animations_dict[role][choice]['duration_ms']
                print(f"picked {choice} of {animation_duration} ms through random choice\n")

            # setting a variable to track how much of clip is used
            if clip_left == 0:
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
                    # with lip
                    if remaning_clip == 0:
                        print(f"adding {choice} with lip move from 0 to {animations_dict[role][choice]['duration_ms']}, current time is now {current_timings}\n")
                        print('remaining clip ', remaning_clip)

                        # Now adding the actual video to workspace folder
                        video_ops.trim_video(
                            output_folder=f'test/{role}',
                            input_path=animations_dict[role][choice]['paths'][with_lip],
                            entire_clip=True
                        )

                        # ------------------------------
                        # Save segment info
                        timeline_segments.append({
                            'segment_number': segment_count,
                            'clip': choice,
                            'withLip': 'WithLip',
                            'src': animations_dict[role][choice]['paths'][with_lip],
                            'start_ms': 0,
                            'end_ms': animations_dict[role][choice]['duration_ms']
                        })
                        segment_count += 1
                        # ------------------------------

                    else:
                        start_trim_val = animations_dict[role][choice]['duration_ms'] - remaning_clip
                        end_trim_val = animations_dict[role][choice]['duration_ms']
                        print(f"adding {choice} with lip move from {start_trim_val} to {end_trim_val}, current time is now {current_timings}\n")
                        print('remaining clip ', remaning_clip)
                        video_ops.trim_video(
                            output_folder=f'test/{role}',
                            input_path=animations_dict[role][choice]['paths'][with_lip],
                            start_ms=start_trim_val,
                            end_ms=end_trim_val
                        )

                        # ------------------------------
                        timeline_segments.append({
                            'segment_number': segment_count,
                            'clip': choice,
                            'withLip': 'WithLip',
                            'src': animations_dict[role][choice]['paths'][with_lip],
                            'start_ms': start_trim_val,
                            'end_ms': end_trim_val
                        })
                        segment_count += 1
                        # ------------------------------

                else:
                    # without lip
                    if remaning_clip == 0:
                        print(f"adding {choice} without lip move from 0 to {animations_dict[role][choice]['duration_ms']}, current time is now {current_timings}\n")
                        print('remaining clip ', remaning_clip)
                        video_ops.trim_video(
                            output_folder=f'test/{role}',
                            input_path=animations_dict[role][choice]['paths'][without_lip],
                            entire_clip=True
                        )

                        # ------------------------------
                        timeline_segments.append({
                            'segment_number': segment_count,
                            'clip': choice,
                            'withLip': 'NoLip',
                            'src': animations_dict[role][choice]['paths'][without_lip],
                            'start_ms': 0,
                            'end_ms': animations_dict[role][choice]['duration_ms']
                        })
                        segment_count += 1
                        # ------------------------------

                    else:
                        start_trim_val = animations_dict[role][choice]['duration_ms'] - remaning_clip
                        end_trim_val = animations_dict[role][choice]['duration_ms']
                        print(f"adding {choice} without lip move from {start_trim_val} to {end_trim_val}, current time is now {current_timings}\n")
                        print('remaining clip ', remaning_clip)
                        video_ops.trim_video(
                            output_folder=f'test/{role}',
                            input_path=animations_dict[role][choice]['paths'][without_lip],
                            start_ms=start_trim_val,
                            end_ms=end_trim_val
                        )

                        # ------------------------------
                        timeline_segments.append({
                            'segment_number': segment_count,
                            'clip': choice,
                            'withLip': 'NoLip',
                            'src': animations_dict[role][choice]['paths'][without_lip],
                            'start_ms': start_trim_val,
                            'end_ms': end_trim_val
                        })
                        segment_count += 1
                        # ------------------------------

                print(f"and remaining time is {turn_time[i] - current_timings}\n")

                # Since we used the full clip, reset remaning_clip
                remaning_clip = 0
                trim_trigger = False

            else:
                # 4) The animation does NOT fit fully => we do "trimming" logic
                leftover_time = turn_time[i] - current_timings
                new_remaning_clip = animation_duration - leftover_time

                if i % 2 == 0:  # with lip
                    if trim_trigger:
                        start_trim_val = animations_dict[role][choice]['duration_ms'] - remaning_clip
                        end_trim_val = leftover_time + start_trim_val
                        print(f"trimming the with lip move video from {start_trim_val} to {end_trim_val} ... \n and increment turn_time (i += 1)\n")

                        video_ops.trim_video(
                            output_folder=f'test/{role}',
                            input_path=animations_dict[role][choice]['paths'][with_lip],
                            start_ms=start_trim_val,
                            end_ms=end_trim_val
                        )

                        # ------------------------------
                        timeline_segments.append({
                            'segment_number': segment_count,
                            'clip': choice,
                            'withLip': 'WithLip',
                            'src': animations_dict[role][choice]['paths'][with_lip],
                            'start_ms': start_trim_val,
                            'end_ms': end_trim_val
                        })
                        segment_count += 1
                        # ------------------------------

                    else:
                        start_trim_val = remaning_clip
                        end_trim_val = leftover_time + start_trim_val
                        print(f"trimming the with lip move video from {start_trim_val} to {end_trim_val} ... \n and increment turn_time (i += 1)\n")

                        video_ops.trim_video(
                            output_folder=f'test/{role}',
                            input_path=animations_dict[role][choice]['paths'][with_lip],
                            start_ms=start_trim_val,
                            end_ms=end_trim_val
                        )

                        # ------------------------------
                        timeline_segments.append({
                            'segment_number': segment_count,
                            'clip': choice,
                            'withLip': 'WithLip',
                            'src': animations_dict[role][choice]['paths'][with_lip],
                            'start_ms': start_trim_val,
                            'end_ms': end_trim_val
                        })
                        segment_count += 1
                        # ------------------------------

                else:  # without lip
                    if trim_trigger:
                        start_trim_val = animations_dict[role][choice]['duration_ms'] - remaning_clip
                        end_trim_val = leftover_time + start_trim_val
                        print(f"trimming the without lip move video from {start_trim_val} to {end_trim_val} ... \n and increment turn_time (i += 1)\n")

                        video_ops.trim_video(
                            output_folder=f'test/{role}',
                            input_path=animations_dict[role][choice]['paths'][without_lip],
                            start_ms=start_trim_val,
                            end_ms=end_trim_val
                        )

                        # ------------------------------
                        timeline_segments.append({
                            'segment_number': segment_count,
                            'clip': choice,
                            'withLip': 'NoLip',
                            'src': animations_dict[role][choice]['paths'][without_lip],
                            'start_ms': start_trim_val,
                            'end_ms': end_trim_val
                        })
                        segment_count += 1
                        # ------------------------------

                    else:
                        start_trim_val = remaning_clip
                        end_trim_val = leftover_time + start_trim_val
                        print(f"trimming the without lip move video from {start_trim_val} to {end_trim_val} ... \n and increment turn_time (i += 1)\n")

                        video_ops.trim_video(
                            output_folder=f'test/{role}',
                            input_path=animations_dict[role][choice]['paths'][without_lip],
                            start_ms=start_trim_val,
                            end_ms=end_trim_val
                        )

                        # ------------------------------
                        timeline_segments.append({
                            'segment_number': segment_count,
                            'clip': choice,
                            'withLip': 'NoLip',
                            'src': animations_dict[role][choice]['paths'][without_lip],
                            'start_ms': start_trim_val,
                            'end_ms': end_trim_val
                        })
                        segment_count += 1
                        # ------------------------------

                remaning_clip = new_remaning_clip

                clip_left -= remaning_clip
                print(f"\n\n total clip used remain  = {clip_left - remaning_clip} \n\n")

                trim_trigger = True
                current_timings += leftover_time

                if i % 2 == 0:
                    print(f"adding {choice} with lip move, current time is now {current_timings}\n")
                else:
                    print(f"adding {choice} without lip move, current time is now {current_timings}\n")

                print(f"setting the choice and animation duration = {remaning_clip} "
                      f"of remaining clip of {choice}\n")

                i += 1
                continue

            # 5) If we finished a turn exactly, you may want to increment i
            if current_timings == turn_time[i]:
                i += 1

            # end while loop

        # -----------------------------------
        # After building the timeline, save it
        # -----------------------------------
        with open("timeline_data.txt", "w", encoding="utf-8") as f:
            for seg in timeline_segments:
                f.write(
                    f"Segment {seg['segment_number']}: "
                    f"Clip='{seg['clip']}', {seg['withLip']}, "
                    f"Src='{seg['src']}', "
                    f"Start_ms={seg['start_ms']}, "
                    f"End_ms={seg['end_ms']}\n"
                )

        # The original code ends here
        # -----------------------------------
