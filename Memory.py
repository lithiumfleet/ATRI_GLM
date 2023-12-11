from DataBase import HistoryDB, KnowledgeDB

class Memo:
    def __init__(self) -> None:
        self.historydb = HistoryDB()
        self.knowledgedb = KnowledgeDB()
        self.default_history:list[str] = ["你好","你好~我是ATRI!"]
        self.all_history:list[str] = self.default_history.copy()
        self.split_window_size:tuple(int) = (4,8)   # 前后滑动窗口大小

    def process_history(self, query:str) -> list[str]:
        pre_dialogs:list[str] = self.historydb.search_history(query_texts=[query],n_results=4)
        # 对话是两句两句来的, 所以要乘2
        history = pre_dialogs[-self.split_window_size[0]*2:] \
            + self.all_history[-self.split_window_size[1]*2:]
        return history
    
    def clear_history(self):
        self.all_history = self.default_history.copy()

    def update_history(self, query:str, atri_response:list[str], chosen:int=0) -> None:
        # 更新history
        self.all_history.append(query)
        self.all_history.append(atri_response[chosen])
        self.historydb.update_history(query=query,atri_response=atri_response[chosen])

    def search_knownledge(self,query:list[str]) -> list[str]:
        query_texts = ''.join(self.all_history[-self.split_window_size[1]*2:]) + query
        return self.knowledgedb.search_knownledge(query_texts=query_texts,n_results=4)

    def clear_historydb(self):
        # FIXME: 我觉得得加点logger
        self.historydb.chromadb_client.delete_collection("atri_history_db")
        self.historydb.collection = self.historydb.chromadb_client.get_or_create_collection('atri_history_db',embedding_function=self.historydb.embedding_fn)

    def init_kownledge_from_txt(self, fpath:str):
        chunks = []
        with open(fpath,encoding='utf8',mode='r') as knowledge_file:
            cnt = 0
            while True:
                chunk = knowledge_file.read(50).strip()
                if chunk == '':
                        break
                chunks.append(chunk)
                
        if len(chunks) == 0: return
        ids = [str(i) for i in range(len(chunks))] 
        self.knowledgedb.chromadb_client.delete_collection("atri_knowledge_db")
        self.knowledgedb.collection = self.knowledgedb.chromadb_client.get_or_create_collection("atri_knowledge_db",embedding_function=self.knowledgedb.embedding_fn)
        self.knowledgedb.collection.add(ids=ids,documents=chunks)