from faster_whisper import WhisperModel
from numpy import ndarray, concatenate, zeros
import sounddevice as sd
from typing import Optional
import numpy as np
import keyboard
import pyaudio
import wave
import os


class WSP:
    def __init__(self) -> None:
        self.model= WhisperModel(model_size_or_path="small", device="cpu", compute_type="default")
        self.p = pyaudio.PyAudio()

    def wav_to_text(self, inputs:Optional[str|ndarray]) -> str:
        # if inputs is str, it must be a wav file path
        segments, _ = self.model.transcribe(inputs, beam_size=5, language="zh")
        # segment is a namedtuple
        texts = [seg.text for seg in segments]
        return '.'.join(texts)

    def ctrl_rec(self) -> str:
        stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        wf = wave.open('input.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        if keyboard.is_pressed("ctrl"):
            while keyboard.is_pressed("ctrl"):
                data = stream.read(1024)
                wf.writeframes(data)

            wf.close()
            res = self.wav_to_text('./input.wav')
            os.remove("./input.wav")
            stream.close()
        else:
            res = ""
        return res

    # @staticmethod
    # def record(duration:int|float) -> ndarray:
    #     # FIXME: 错了
    #     fs = 16000
    #     audio = sd.rec(int(duration*fs), samplerate=fs, channels=1)
    #     sd.wait()
    #     # audio.shape = (88200,1)
    #     audio = np.squeeze(audio)
    #     audio = audio.astype(np.float32)/32768.0
    #     return audio

    # def ctrl_rec(self) -> ndarray|int:
    #     # FIXME: 错了
    #     fs = 44100
    #     frame_shape = (int(1*fs),1)
    #     audio = None
    #     while keyboard.is_pressed('ctrl'):
    #         cur = sd.rec(frame_shape[0], samplerate=fs, channels=1,blocking=True)
    #         cur = np.squeeze(cur)
    #         cur = cur.astype(np.float32)/32768.0
    #         if not isinstance(audio, ndarray):
    #             audio = cur
    #         else:
    #             audio = concatenate([audio,cur],axis=0)
    #     if not isinstance(audio, ndarray):
    #         return None
    #     return audio

if __name__ == '__main__':
    from time import sleep
    w = WSP()
    res = w.record(3) 
    res.tofile('output.wav')
    print(w.wav_to_text(res))