from Pipeline import Pipe
from Memory import Memo
from AtriIO.VoiceIO import VoiceIO
from time import sleep

memo = Memo()
memo.init_kownledge_from_txt("knowledge.txt")
pipe = Pipe()
vocio = VoiceIO()


def main():
    rec_flag = False
    while True:
        # 输入
        if not rec_flag:
            query = input(">>>>> ")
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
        if query == 'rec' or rec_flag:
            rec_flag = True
            print("waiting for your voc...", end="")
            duration = input("secs to rec: ")
            if duration == "exit":
                rec_flag = False
                continue
            else:
                duration = int(duration)
            query = vocio.voc_to_str(duration)
            print(">>>>> " + query)
        if query == '':
            continue

        # 知识库和历史记录
        history:list[str] = memo.process_history(query)
        knowledge:list[str] = []#memo.search_knownledge(query)

        # 回复
        atri_response:list[str] = pipe.chat(query=query, history=history, knowledge=knowledge)

        # tts
        # wavout = vocio.str_to_voc(atri_response)
        # vocio.play(wavout)

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