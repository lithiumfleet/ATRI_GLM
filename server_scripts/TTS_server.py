# put it in MoeTTS dir
import torch
import numpy as np
from text import text_to_sequence
import cutlet

from main import initialization 
import json
from fastapi import FastAPI, Request
import uvicorn


class TTS_Module():
    def __init__(self) -> None:
        self.tacotron2_checkpoint="models/atri_v2_40000"
        self.hifi_gan_checkpoint="models/g_atri_hifigan_02510000"
        self.hifi_gan_config="models/config.json"
        self.device="cuda"
        self.cleaners = "basic_cleaners"
        self.tacotron2_model, self.hifi_gan_gen = initialization(self.tacotron2_checkpoint, self.hifi_gan_checkpoint, self.hifi_gan_config, self.device)


    def text_to_speech(self, input_text: str):
        cut = cutlet.Cutlet("kunrei")
        input_text = [input_text]
        with torch.no_grad():
            for idx, text in enumerate(input_text, start=1):
                romaji = cut.romaji(text).replace(" ","")
                romaji = romaji if romaji.endswith(".") else romaji+"."
                sequence = np.array(text_to_sequence(romaji, [self.cleaners]))[None, :]
                sequence = torch.autograd.Variable(torch.from_numpy(sequence)).cpu().long() if self.device == "cpu" else torch.autograd.Variable(torch.from_numpy(sequence)).cuda().long()

                mel_outputs, *_ = self.tacotron2_model.inference(sequence)
                
                raw_audio = self.hifi_gan_gen(mel_outputs.float())
                audio = raw_audio.squeeze()
                audio = audio * 32768.0
                audio = audio.cpu().numpy().astype('int16') # if self.device == "cpu" else audio.cuda().numpy().astype('int16')
        return audio


tts = TTS_Module()
app = FastAPI()

@app.get("/jp_tts/{sentence}")
async def get_audio(sentence:str):
    res:np.ndarray = tts.text_to_speech(sentence)
    return json.dumps(res.tolist())



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7888)