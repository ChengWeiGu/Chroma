# -*- coding: utf-8 -*-
import os
import time
import pickle
import argparse
import configparser
from tqdm import tqdm
import DatabaseProcess
from os import listdir, walk
from langchain.docstore.document import Document
from os.path import basename, join, exists, dirname
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader



class DEM:
    def __init__(self, directory):
        # 定義類別資訊
        self.info = {
            'path' : directory + "/DEM",
            'class_name': "DEM",
            'class_desc':"Example Projects for Product Users/Customers"
        }
        # 允許可以處理的語言
        self.lang_list = ['en','tw','eng','cht']
        # 允許可以處理的附檔名
        self.extension_list = ['pdf','docx']
        self.get_end_list() # _en.pdf, _tw.docx...
    
    # 將語言+副檔名進行排列組合
    def get_end_list(self) -> None:
        self.end_list = []
        for lang in self.lang_list:
            for ext in self.extension_list:
                self.end_list.append("_"+lang+"."+ext)
    
    # 依副檔名判斷檔案是否可以處理            
    def isin_extension_list(self, file) -> tuple[bool,str]:
        isin_extension = False
        extension = ''
        for ext in self.extension_list:
            if ext in file:
                isin_extension = True
                extension = ext
        return isin_extension, extension
    
    # 依檔名排列組合判斷檔案是否可以被處理
    def isin_end_list(self,file) -> tuple[bool,str]:
        isin_end = False
        end_text = ''
        for end in self.end_list:
            if end in file:
                isin_end = True
                end_text = end
        return isin_end, end_text
    
    '''**掃描檔案+建立metadaat
    * 1. 排除不正確的檔名+副檔名, 優先處理PDF格式
    * 2. 將可以處理的檔案一一建立metadata
    * 3. 使用 RecursiveCharacterTextSplitter 切割文檔
    * 4. 用langchain.docstore.document封裝
    * @params: None
    * @return: list[langchain.docstore.document]
    *'''
    def scan_folder_and_create_document(self) -> list:
        filenames = [] # 紀錄可以處理的檔案路徑+檔名
        prefix_filenames = []
        extension_list = []
        for root,dirs,files in walk(self.info['path']):
            for file in files:
                filename = join(root,file)
                # filter1: 副檔名要正確
                isin_end, end_text = self.isin_end_list(file=file)
                if isin_end:
                    # filter2: do not consider duplicate prefix filename
                    isin_extension, extension = self.isin_extension_list(file=file)
                    prefix_filename = filename.replace(extension,"") # XX_en.pdf -> XX_en, XX_tw.docx -> XX_tw
                    if prefix_filename not in prefix_filenames:
                        # 優先處理PDF格式，避免重複處理
                        pdf_filename = prefix_filename + "pdf"
                        # priority pdf > docx
                        if exists(pdf_filename):
                            filenames.append(pdf_filename)
                            extension_list.append('pdf')
                        else:
                            filenames.append(filename)
                            extension_list.append(extension)
                        prefix_filenames.append(prefix_filename)
        
        # create lc document
        metadta_list = []
        doc_list = []
        text_splitter_recur = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 300,
            length_function = len,
            is_separator_regex=False
        )
        for i, filename in enumerate(filenames):
            print(filename)
            metadata = {
                'source':basename(filename),
                'filename':filename,
                'parent_folder':basename(dirname(filename)),
                'extension':extension_list[i],
                'class_name':self.info['class_name'],
                'class_desc':self.info['class_desc']
                }
            metadta_list.append(metadata)
            content_texts = ""
            if extension_list[i].lower() == 'docx':
                loader = Docx2txtLoader(filename)
                data = loader.load() # 只有一個document包含全部內容
                content_texts = data[0].page_content #取出內容
            else: # pdf
                loader = PyPDFLoader(filename)
                pages = loader.load_and_split() # page by page data
                for page in pages:
                    content_texts += (page.page_content + " ")
            # split and add metadata
            for chunk in text_splitter_recur.split_text(content_texts):
                doc_list.append(Document(page_content=chunk,metadata=metadata))
        
        # print(doc_list[-20:])
        print("total files: ", len(filenames))
        print("total len of docs: ",len(doc_list))
        return doc_list

    """逐筆插入文件到 ChromaDB"""
    def insert_documents_for_each(self, lcdb_obj, doc_list):
        for document in tqdm(doc_list,
                             total=len(doc_list), 
                             desc="Inserting documents one by one",
                             unit="pcs"):
            #失敗重試
            try_cnt = 0
            max_retry = 3
            while try_cnt < max_retry:
                try:
                    lcdb_obj.insert_data2db([document])  # 逐筆插入，避免觸發存取速率限制
                    break
                except Exception as e:
                    try_cnt += 1
                    print(f"Error inserting document: {document.metadata['source']}, Error: {e}\n Wait for a min...")
                    time.sleep(60) # 休息 1 min
            else:
                print(f"Failed to insert document after {max_retry} attempts: {document.metadata['source']}")
    
    
'''**
* 1. 繼承DEM
* 2. 改寫info
*'''          
class FAQ(DEM):
    def __init__(self, directory):
        self.info = {
            'path' : directory + "/FAQ",
            'class_name': "FAQ",
            'class_desc':"Frequently Asked Questions for Product Users/Customers"
        }
        self.lang_list = ['en','tw','eng','cht','ENG']
        self.extension_list = ['pdf','docx']
        self.get_end_list() # _en.pdf, _tw.docx...


'''**
* 1. 繼承DEM
* 2. 改寫info, scan_folder_and_create_document
* 3. scan_folder_and_create_document中改寫可以處理的檔名
*'''  
class EBP(DEM):
    def __init__(self, directory):
        self.info = {
            'path' : directory + "/EBP",
            'class_name': "EBP",
            'class_desc':"This is EBPro User-Guide Manual for All Chapters"
        }
    
    def scan_folder_and_create_document(self):
        # 規定只能處理的檔案+副檔名
        files = ['EasyBuilder-Pro-V61001-UserManual-cht.pdf','EasyBuilder-Pro-V61001-UserManual-eng.pdf']
        filenames = [(self.info['path'] + '/' + f) for f in files]
        extension_list = ['pdf','pdf']
        
        # create lc document
        metadta_list = []
        doc_list = []
        text_splitter_recur = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 300,
            length_function = len,
            is_separator_regex=False
        )
        for i, filename in enumerate(filenames):
            print(filename)
            metadata = {'source':basename(filename),
                        'filename':filename,
                        'parent_folder':basename(dirname(filename)),
                        'extension':extension_list[i],
                        'class_name':self.info['class_name'],
                        'class_desc':self.info['class_desc']}
            metadta_list.append(metadata)
            content_texts = ""
            if extension_list[i] == 'docx':
                loader = Docx2txtLoader(filename)
                data = loader.load() # 只有一個document包含全部內容
                content_texts = data[0].page_content #取出內容
            else: # pdf
                loader = PyPDFLoader(filename)
                pages = loader.load_and_split() # page by page data
                for page in pages:
                    content_texts += (page.page_content + " ")
            # split and add metadata
            for chunk in text_splitter_recur.split_text(content_texts):
                doc_list.append(Document(page_content=chunk,
                                            metadata=metadata))
        
        # print(doc_list[:10])
        print("total files: ", len(filenames))
        print("total len of docs: ",len(doc_list))
        return doc_list


'''**
* 1. 繼承DEM
* 2. 改寫info
*'''      
class UM0(DEM):
    def __init__(self, directory):
        self.info = {
            'path' : directory + "/UM0",
            'class_name': "UM0",
            'class_desc':"Operation Manual for All Products"
        }
        self.lang_list = ['en','tw','eng','cht']
        self.extension_list = ['pdf','docx']
        self.get_end_list() # _en.pdf, _tw.docx...


'''**
* 1. 繼承DEM
* 2. 改寫info, get_end_list
* 3. get_end_list當中檔案名稱不含 "_" (特殊)
*'''   
class FBA(DEM):
    def __init__(self, directory):
        self.info = {
            'path' : directory + "/FBA",
            'class_name': "FBA",
            'class_desc':"Official Video Explanation for Weintek"
        }
        self.lang_list = [''] # 不卡控
        # self.extension_list = ['pdf','docx']
        self.extension_list = ['DOCX','PDF']
        self.get_end_list() # .pdf, .docx...
        
    def get_end_list(self):
        self.end_list = []
        for lang in self.lang_list:
            for ext in self.extension_list:
                self.end_list.append(lang+"."+ext)



def main():
    parser = argparse.ArgumentParser(description='FAE document')
    parser.add_argument('-d','--dir',type=str,help='chromadb儲存的資料夾位置')
    parser.add_argument('-cn','--collection_name', type=str, default="test_collection", help='collection name of chroma db')
    parser.add_argument('-s', '--src', type=str, default="./SVN_manual", help='User Guide Manual 資料夾位置')
    args = parser.parse_args()
    
    if args.dir is not None:
        # check if the directory exists, if not create it
        if not exists(args.dir):
            os.makedirs(args.dir)                    

        chroma_login_info={
            "chromadb_path":args.dir,
            "collection_name":args.collection_name,
            "embedding_function":DatabaseProcess.embedding_function
            }
        
        # chroma db obj
        lcdb_chroma = DatabaseProcess.LangchainChromaDB(chroma_login_info)
        lcdb_chroma.init_database()
        
        print("start creating documents....")
        
        # for dem scanner
        print("\nstart dem scanning....")
        dem_scanner = DEM(args.src)
        dem_doc_list = dem_scanner.scan_folder_and_create_document()
        dem_scanner.insert_documents_for_each(lcdb_chroma, dem_doc_list) # 逐筆插入文件到 ChromaDB
        print("done\n")
        
        # for faq scanner
        print("\nstart faq scanning....")
        faq_scanner = FAQ(args.src)
        faq_doc_list = faq_scanner.scan_folder_and_create_document()
        faq_scanner.insert_documents_for_each(lcdb_chroma, faq_doc_list) # 逐筆插入文件到 ChromaDB
        print("done\n")
        
        # for ebp scanner
        print("\nstart ebp scanning....")
        ebp_scanner = EBP(args.src)
        ebp_doc_list = ebp_scanner.scan_folder_and_create_document()
        ebp_scanner.insert_documents_for_each(lcdb_chroma, ebp_doc_list) # 逐筆插入文件到 ChromaDB
        print("done\n")
        
        # for um0 scanner
        print("\nstart um0 scanning....")
        um0_scanner = UM0(args.src)
        um0_doc_list = um0_scanner.scan_folder_and_create_document()
        um0_scanner.insert_documents_for_each(lcdb_chroma, um0_doc_list) # 逐筆插入文件到 ChromaDB
        print("done\n")
        
        # for FBA scanner
        print("\nstart fba scanning....")
        fba_scanner = FBA(args.src)
        fba_doc_list = fba_scanner.scan_folder_and_create_document()
        fba_scanner.insert_documents_for_each(lcdb_chroma, fba_doc_list) # 逐筆插入文件到 ChromaDB
        print("done\n")
               
        
if __name__ == "__main__":
    main()
    