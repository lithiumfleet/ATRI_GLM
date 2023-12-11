from Pipeline import Pipe
from Memory import Memo
memo = Memo()
pipe = Pipe()
memo.init_kownledge_from_txt("knowledge.txt")
def main():
    while True:
        # 输入
        query = input(">>>>> ")
        if query == 'exit':
            break
        if query == 'clear':
            memo.clear_history()
            continue
        if query == 'clear all':
            memo.clear_historydb()
            continue
        if query == '':
            continue

        # 知识库和历史记录
        history:list[str] = memo.process_history(query)
        knowledge:list[str] = memo.search_knownledge(query)

        # 回复
        atri_response:list[str] = pipe.chat(query=query, history=history, knowledge=knowledge)

        # 展示
        for line in atri_response:
            print("ATRI: " + line)

        # 更新历史记录
        memo.update_history(query, atri_response)

main()