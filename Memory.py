from DataBase import HistoryDB, KnowledgeDB

class Memo:
    def __init__(self) -> None:
        self.historydb = HistoryDB()
        self.knowledgedb = KnowledgeDB()
        self.default_history:list[str] = ["你好,我是夏生.","夏生先生好~我是ATRI!"]
        self.all_history:list[str] = self.default_history.copy()
        self.split_window_size:tuple(int) = (1,50)   # 前后滑动窗口大小

    def process_history(self, query:str) -> list[str]:
        pre_dialogs:list[str] = self.historydb.search_history(query_texts=[query],n_results=4) if self.split_window_size[0] != 0 else []
        # 对话是两句两句来的, 所以要乘2
        history = pre_dialogs[-self.split_window_size[0]*2:] \
            + self.all_history[-self.split_window_size[1]*2:]
        return history
    
    def clear_history(self):
        self.all_history = self.default_history.copy()

    def update_history(self, query:str, atri_response:list[str], chosen:int=0) -> None:
        # 去掉短回复
        # if len(atri_response[chosen]) <= 10:
        #     return

        # 更新history
        self.all_history.append(query)
        self.all_history.append(atri_response[chosen])
    
    def add_history_to_db(self, query:str, atri_response:list[str], chosen:int=0) -> None:
        self.historydb.update_history(query,atri_response[chosen])

    def search_knownledge(self,query:list[str]) -> list[str]:
        # 防止前面的对话盖掉query的语义, 设置最近2个句子能搜到和query更相关的knowledge
        query_texts = ''.join(self.all_history[-2:]) + query
        return self.knowledgedb.search_knownledge(query_texts=query_texts,n_results=4)

    def clear_historydb(self):
        # FIXME: 我觉得得加点logger
        self.historydb.chromadb_client.delete_collection("atri_history_db")
        self.historydb.collection = self.historydb.chromadb_client.get_or_create_collection('atri_history_db',embedding_function=self.historydb.embedding_fn)

    def init_kownledge_from_txt(self, fpath:str):
        chunks = []
        with open(fpath,encoding='utf8',mode='r') as knowledge_file:
            for line in knowledge_file.readlines():
                chunks.append(line.rstrip())
                
        if len(chunks) == 0: return
        ids = [str(i) for i in range(len(chunks))] 
        self.knowledgedb.chromadb_client.delete_collection("atri_knowledge_db")
        self.knowledgedb.collection = self.knowledgedb.chromadb_client.get_or_create_collection("atri_knowledge_db",embedding_function=self.knowledgedb.embedding_fn)
        self.knowledgedb.collection.add(ids=ids,documents=chunks)