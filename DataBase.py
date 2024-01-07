import chromadb
from chromadb.utils import embedding_functions

class DataBase:
    def __init__(self) -> None:
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction("D:/models/m3e-base")
        # self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.chromadb_client = chromadb.PersistentClient(path='./chroma')
        self.collection:chromadb.Collection=None
        # 限制搜索结果
        self.query_limit = -1
        
    def _search(self, query_texts:list[str], n_results:int):
        result = self.collection.query(query_texts=query_texts, n_results=n_results)
        n_results = min(n_results, len(result['documents'][0]))
        ans = []
        for i in range(n_results):
            # 限制不相干向量
            if result['distances'][0][i] > self.query_limit and self.query_limit != -1:
                continue
            ans.append(result['documents'][0][i])
        return ans



    def _update(self, documents:list[str]):
        # ids:list[str]
        self.collection.add(ids=[str(self.collection.count())],documents=documents)


class HistoryDB(DataBase):
    # history db里面存的是完整的句子, 格式为xxx\nyyy. 外面用的都是list[str], 所以要处理
    def __init__(self) -> None:
        super().__init__()
        self.collection = self.chromadb_client.get_or_create_collection('atri_history_db',embedding_function=self.embedding_fn)

    def search_history(self, query_texts:list[str], n_results:int) -> list[str]:
        result = self.collection.query(query_texts=query_texts, n_results=n_results)
        pre_dialogs = []
        
        n_results = min(n_results, len(result['documents'][0]))
        for i in range(n_results):
            if result['distances'][0][i] > self.query_limit and self.query_limit != -1:
                continue
            # 数据储存格式: useruseruser \n atriatriatri.一方面是为了兼容外部的[user,atri,user....]的history格式,另一方面是为了兼容数据集格式方便后续训练
            # result['documents'][0]的0是因为len(query_texts)==1
            user, atri = result['documents'][0][i].split('\n')
            pre_dialogs.append(user)
            pre_dialogs.append(atri)
        return pre_dialogs

    def update_history(self, query:str, atri_response:str):
        return self._update([query+'\n'+atri_response])


class KnowledgeDB(DataBase):
    def __init__(self) -> None:
        super().__init__()
        self.collection = self.chromadb_client.get_or_create_collection('atri_knowledge_db',embedding_function=self.embedding_fn)

    def search_knownledge(self, query_texts:list[str], n_results:int):
        return self._search(query_texts, n_results)

    def update_knowledge(self, news:str):
        # FIXME: 没写,我觉得更新知识应该从文件里读入.目前只能一条一条读入
        return self._update(documents=[news])
        