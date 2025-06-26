# -*- coding: utf-8 -*-
import chromadb
from langchain_community.vectorstores.chroma import Chroma
from langchain.docstore.document import Document
from langchain_openai import AzureOpenAIEmbeddings

# create azure embedding function
embedding_function=AzureOpenAIEmbeddings(
        openai_api_version="2024-12-01-preview",
        openai_api_type="azure",
        openai_api_key="f2ca25bd197746b4ba281eec20369787",
        azure_endpoint="https://weintek-default-openai.openai.azure.com/",
        azure_deployment="text-embedding-3-large")


class LangchainChromaDB:
    
    def __init__(self,login_info):
        self.top_k = 10 # 搜索最相近k筆資料
        self.set_log_info(login_info) # chroma設定資料
        
    def set_log_info(self,new_login_info):
        self.login_info = new_login_info
        
    def set_topk(self,k:int):
        self.top_k = k
    
    # 初始化，必須先call一次
    def init_database(self):
        print("Init db...")
        self.client = chromadb.PersistentClient(
                                path=self.login_info['chromadb_path']
                            )
        self.collection = self.client.get_or_create_collection(
                                name=self.login_info['collection_name']
                            )
        print("Available Collections: ", self.client.list_collections())
        print("Init db done\n")
        
    def wrap_data2doc(self,ids=[],texts=[],metadatas=[]):
        documents=[]
        for id, text, metadata in zip(ids,texts,metadatas):
            page = Document(
                        page_content=text, 
                        metadata=metadata,
                        id=id
                    )
            documents.append(page)
        return documents
    
    def insert_data2db(self,documents):
        self.lcdb = Chroma.from_documents(
                                client=self.client,
                                documents=documents,
                                collection_name=self.login_info['collection_name'],
                                embedding=self.login_info['embedding_function']
                            )
        
    def lc_similarity_search_with_score(self,query):
        self.lcdb = Chroma(
                        client=self.client,
                        collection_name=self.login_info['collection_name'],
                        embedding_function=self.login_info['embedding_function']
                    )
        res_docs = self.lcdb.similarity_search_with_score(query,k=self.top_k)
        return res_docs
    
    def lc_similarity_search_with_score_topk(self,query,k):
        self.lcdb = Chroma(
                        client=self.client,
                        collection_name=self.login_info['collection_name'],
                        embedding_function=self.login_info['embedding_function']
                    )
        res_docs = self.lcdb.similarity_search_with_score(query,k)
        return res_docs



if __name__ == "__main__":
    
    chroma_login_info={
        "chromadb_path":".\jsobject_chroma",
        "collection_name":"test_collection",
        "embedding_function":embedding_function}

    # test searching
    query = "How to use"
    lcdb_chroma = LangchainChromaDB(chroma_login_info)
    lcdb_chroma.init_database()
    res_docs = lcdb_chroma.lc_similarity_search_with_score(query)
    print(res_docs)
