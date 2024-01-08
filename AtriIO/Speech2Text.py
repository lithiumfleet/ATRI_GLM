from faster_whisper import WhisperModel
from numpy import ndarray
import sounddevice as sd
from typing import Optional
import numpy as np


class WSP:
    def __init__(self) -> None:
        self.model= WhisperModel(model_size_or_path="small", device="cpu", compute_type="default")

    def wav_to_text(self, inputs:Optional[str|ndarray]) -> str:
        # if inputs is str, it must be a wav file path
        segments, _ = self.model.transcribe(inputs, beam_size=5, language="zh")
        # segment is a namedtuple
        texts = [seg.text for seg in segments]
        return '.'.join(texts)
    
    def record(self,duration:Optional[int|float]=20) -> ndarray:
        # FIXME
        fs = 44100
        recording = None

        recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
        sd.wait()
        recording = np.asarray(recording).astype('float32')

        return recording

if __name__ == '__main__':
    w = WSP()
    i = w.record(3)
    print(i.shape)
    print()