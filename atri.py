from Pipeline import Pipe
from Memory import Memo
from AtriIO.VoiceIO import VoiceIO
from time import sleep
import keyboard
import sounddevice as sd
import os

memo = Memo()
# memo.init_kownledge_from_txt("knowledge.txt") # 考虑到现在sentence to vector对短文本效果差, 不启用
pipe = Pipe()
vocio = VoiceIO()


def main():
    rec_flag = False
    print("Have chat with ATRI :)")
    while True:
        # 输入
        sleep(0.1)
        if keyboard.read_key() == "ctrl":
            if rec_flag:
                query = vocio.ctrl_then_rec()
                print(">>>>> " + query, end="")
            else:
                continue
        else:
            query = input(">>>>> ")

        if query == 'open rec':
            rec_flag = True
            print("hold ctrl and waiting for your voc...")
            continue

        if query == 'close rec':
            rec_flag = False
            print("audio is closed now.")
            continue 

        if query == 'exit':
            break
        if query == 'clear':
            memo.clear_history()
            continue
        if query == 'clear all':
            memo.clear_historydb()
            continue
        if query == 'add':
            memo.add_history_to_db(*previous)
            continue
        if query == '':
            continue

        # 知识库和历史记录
        history:list[str] = memo.process_history(query)
        knowledge:list[str] = [] # memo.search_knownledge(query) # 不启用

        # 回复
        atri_response:list[str] = pipe.chat(query=query, history=history, knowledge=knowledge)

        # tts
        wavout = vocio.str_to_voc(atri_response[0]+" .")
        vocio.play(wavout)

        # 更新历史记录
        memo.update_history(query, atri_response)
        previous = (query, atri_response)

        # 展示
        print("ATRI: ",end='')
        for c in atri_response[0]:
            print(c,end='',flush=True)
            sleep(0.05)
        print()

if __name__ == '__main__':
    main()