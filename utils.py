from pydub import AudioSegment
import os
from pydub.silence import detect_leading_silence

def preprocess_song(input_file, output_file):
    """Removes leading and trailing silence from a song."""
    trim_leading_silence = lambda x: x[detect_leading_silence(x):]
    trim_trailing_silence = lambda x: trim_leading_silence(x.reverse()).reverse()
    strip_silence = lambda x: trim_trailing_silence(trim_leading_silence(x))
    
    audio = AudioSegment.from_file(input_file)
    audio = strip_silence(audio)
    
    audio.export(output_file, format="wav")
    
    return output_file


