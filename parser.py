import re

class Time_parser:

    def get_total_seconds_from_transcript(self, file_path='transcript.txt'):
        pattern = re.compile(r'^SPEAKER\s+\d+\s+(\d+):(\d+):(\d+):\d+')
        last_timestamp = None
        with open(file_path, 'r') as f:
            for line in f:
                match = pattern.match(line.strip())
                if match:
                    hours, minutes, seconds = map(int, match.groups())
                    last_timestamp = hours * 3600 + minutes * 60 + seconds
        return last_timestamp
