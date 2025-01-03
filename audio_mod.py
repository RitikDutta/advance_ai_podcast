import os
from pydub import AudioSegment

class Audio_mod:

    def add_silence_gap(self, audio, gap_duration_ms=700, interval_ms=60000):
        """
        Inserts a silence gap into the audio after every interval.

        :param audio: The original AudioSegment.
        :param gap_duration_ms: Duration of the silence gap in milliseconds.
        :param interval_ms: Interval after which to insert the silence in milliseconds.
        :return: Modified AudioSegment with silence gaps.
        """
        silence = AudioSegment.silent(duration=gap_duration_ms)
        output = AudioSegment.empty()
        total_length = len(audio)
        current_position = 0

        while current_position < total_length:
            # Determine the end position for the current chunk
            end_position = current_position + interval_ms
            chunk = audio[current_position:end_position]
            output += chunk

            # Move the current position
            current_position += interval_ms

            # Check if there's more audio to process
            if current_position < total_length:
                output += silence

        return output

    def process_audio_files(input_folder='audio', output_suffix='_modified', gap_ms=200, interval_ms=60000):
        """
        Processes all WAV files in the specified folder by adding silence gaps.

        :param input_folder: Folder containing the WAV files.
        :param output_suffix: Suffix to add to the output file names.
        :param gap_ms: Duration of the silence gap in milliseconds.
        :param interval_ms: Interval after which to insert the silence in milliseconds.
        """
        # Ensure the input folder exists
        if not os.path.isdir(input_folder):
            print(f"Input folder '{input_folder}' does not exist.")
            return

        # List all WAV files in the input folder excluding those already modified
        wav_files = [
            f for f in os.listdir(input_folder)
            if f.lower().endswith('.wav') and not f.lower().endswith(f"{output_suffix.lower()}.wav")
        ]

        if not wav_files:
            print(f"No unmodified WAV files found in '{input_folder}' folder.")
            return

        for file_name in wav_files:
            input_path = os.path.join(input_folder, file_name)
            print(f"Processing '{input_path}'...")

            try:
                # Load the audio file
                audio = AudioSegment.from_wav(input_path)

                # Add silence gaps
                modified_audio = add_silence_gap(audio, gap_duration_ms=gap_ms, interval_ms=interval_ms)

                # Prepare the output file name
                name, ext = os.path.splitext(file_name)
                output_file_name = f"{name}{output_suffix}{ext}"
                output_path = os.path.join(input_folder, output_file_name)

                # Export the modified audio (overwrites if already exists)
                modified_audio.export(output_path, format="wav")
                print(f"Saved modified audio as '{output_path}'.\n")

            except Exception as e:
                print(f"Failed to process '{file_name}': {e}\n")

if __name__ == "__main__":
    process_audio_files(
        input_folder='audio',       # Folder containing WAV files
        output_suffix='_modified',  # Suffix for the output files
        gap_ms=200,                 # Gap duration in milliseconds
        interval_ms=60000           # Interval duration in milliseconds (1 minute)
    )
