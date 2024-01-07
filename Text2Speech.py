from typing import Optional
from sounddevice import play
from requests import get
import numpy as np
import json
from warnings import warn
from Translate import trans


class TTS:
    def __init__(self) -> None:
        self.url = 'http://localhost:8000/jp_tts/'

    def zh_to_jp_wav(self,inputs:Optional[str|list[str]],need_trans2jp=True):
        # 从api接口拿
        if type(inputs) == list:
            inputs = inputs[0]

        if need_trans2jp:
            inputs = self.tran2jp(inputs)

        resp = get(url=self.url+inputs)
        audio = np.asarray(json.loads(resp.json())).astype('int16')
        return audio

    @staticmethod
    def tran2jp(inputs:str):
        return trans(inputs)
    
    @staticmethod
    def play(audio:np.ndarray):
        play(audio, samplerate=22050)
