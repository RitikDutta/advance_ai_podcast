import re
from datetime import timedelta

class TranscriptHelper:
    def __init__(self, filepath):
        """
        Initialize the TranscriptHelper by reading and parsing the transcript file.

        :param filepath: Path to the transcript.txt file.
        """
        self.filepath = filepath
        self.segments = []  # List to hold each speaking segment
        self._parse_transcript()

    def get_total_seconds_from_transcript(self, file_path='transcript.txt'):
        """
        return the total time in second
        """
        pattern = re.compile(r'^SPEAKER\s+\d+\s+(\d+):(\d+):(\d+):\d+')
        last_timestamp = None
        with open(file_path, 'r') as f:
            for line in f:
                match = pattern.match(line.strip())
                if match:
                    hours, minutes, seconds = map(int, match.groups())
                    last_timestamp = hours * 3600 + minutes * 60 + seconds
        return last_timestamp

    def _parse_transcript(self):
        """
        Parse the transcript file and populate the segments list with dictionaries
        containing speaker, start_time, end_time, and text.
        """
        # Adjusted regex pattern to match the timestamp format accurately
        speaker_pattern = re.compile(r'^SPEAKER (\d+) (\d+):(\d+):(\d+):(\d+)$')
        current_segment = None

        with open(self.filepath, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue  # Skip empty lines

                speaker_match = speaker_pattern.match(line)
                if speaker_match:
                    # If there's an ongoing segment, set its end_time to the current speaker's start_time
                    if current_segment:
                        current_segment['end_time'] = self._format_time(
                            speaker_match.group(2),
                            speaker_match.group(3),
                            speaker_match.group(4),
                            speaker_match.group(5)
                        )
                        self.segments.append(current_segment)

                    speaker_id = f"Speaker {speaker_match.group(1)}"
                    start_time = self._format_time(
                        speaker_match.group(2),
                        speaker_match.group(3),
                        speaker_match.group(4),
                        speaker_match.group(5)
                    )
                    current_segment = {
                        'speaker': speaker_id,
                        'start_time': start_time,
                        'end_time': None,
                        'text': ""
                    }
                else:
                    if current_segment:
                        current_segment['text'] += line + " "

            # After the loop, add the last segment with end_time same as start_time (or handle differently)
            if current_segment:
                # Assuming the last segment ends at its start time; adjust if you have a known end time
                current_segment['end_time'] = current_segment['start_time']
                self.segments.append(current_segment)

        # Now, update end_time for each segment based on the next segment's start_time
        for i in range(len(self.segments) - 1):
            self.segments[i]['end_time'] = self.segments[i + 1]['start_time']
        # For the last segment, end_time remains as start_time (zero duration)

    def _format_time(self, hours, minutes, seconds, milliseconds):
        """
        Convert time components to total milliseconds.

        :return: Total milliseconds as an integer.
        """
        td = timedelta(
            hours=int(hours),
            minutes=int(minutes),
            seconds=int(seconds),
            milliseconds=int(milliseconds)
        )
        return int(td.total_seconds() * 1000)  # Convert to milliseconds

    def talking_speaker(self):
        """
        Returns a list of all unique speakers in the transcript.

        :return: List of unique speakers.
        """
        return list(set(segment['speaker'] for segment in self.segments))

    def duration_of_speaking_ms(self, speaker=None):
        """
        Calculate the total duration of speaking for each speaker or a specific speaker
        in milliseconds.

        :param speaker: (Optional) Specific speaker to calculate duration for.
        :return: Total duration in milliseconds or a dictionary of durations per speaker.
        """
        durations = {}
        for segment in self.segments:
            current_speaker = segment['speaker']
            start = segment['start_time']
            end = segment['end_time'] if segment['end_time'] else start
            duration = end - start  # Duration in milliseconds
            if current_speaker in durations:
                durations[current_speaker].append(duration)
            else:
                durations[current_speaker] = [duration]

        if speaker:
            return durations.get(speaker, [])
        return durations

    def total_duration_ms(self):
        """
        Calculate the total duration of the transcript in milliseconds.

        :return: Total duration in milliseconds.
        """
        if not self.segments:
            return 0
        start = self.segments[0]['start_time']
        end = self.segments[-1]['end_time'] if self.segments[-1]['end_time'] else self.segments[-1]['start_time']
        return end - start

    def get_conversation(self):
        """
        Retrieve the entire conversation as a list of dictionaries.

        :return: List of segments with speaker, start_time, end_time, and text.
        """
        return self.segments

    def get_speech_at_time_ms(self, query_time_ms):
        """
        Retrieve the speech segment at a specific time in milliseconds.

        :param query_time_ms: Time in milliseconds.
        :return: The segment dictionary if found, else None.
        """
        for segment in self.segments:
            start = segment['start_time']
            end = segment['end_time']
            if end is None:
                end = start
            if start <= query_time_ms < end:
                return segment
        return None

    def speaker_durations_ms(self):
        """
        Retrieve a dictionary where each key is a speaker and the value is a list of
        durations (in milliseconds) for each time the speaker spoke.

        :return: Dictionary with speakers as keys and lists of durations in milliseconds as values.
        """
        return self.duration_of_speaking_ms()


