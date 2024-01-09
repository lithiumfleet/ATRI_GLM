from AtriIO.Text2Speech import TTS
from AtriIO.Speech2Text import WSP
from sounddevice import play
from numpy import ndarray


class VoiceIO:
    def __init__(self) -> None:
        self.tts = TTS()
        self.wsp = WSP()
    
    def ctrl_then_rec(self) -> str:
        # assuming ctrl is pressed
        return self.wsp.ctrl_rec()

    def voc_to_str(self, duration=10) -> str:
        recording = self.wsp.record(duration)
        return self.wsp.wav_to_text(recording)

    def str_to_voc(self, inputs:str) -> ndarray:
        return self.tts.zh_to_jp_wav(inputs)
    

    @staticmethod
    def play(audio:ndarray):
        play(audio, samplerate=22050)
