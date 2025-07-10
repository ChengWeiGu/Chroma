# -*- coding: utf-8 -*-
import argparse
import DatabaseProcess
import OpenAIFunction


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Inference for chroma')
    parser.add_argument('-j','--js',type=str, help='jssdk inference, 請輸入query')
    parser.add_argument('-s','--spec', type=str, help='spec inference, 請輸入query')
    parser.add_argument('-m','--manual', type=str, help='manual inference, 請輸入query')
    args = parser.parse_args()
    
    # init working context and agent object
    working_context = ""
    summary_agent = OpenAIFunction.SummaryAgent()
    
    if args.js:
        '''**
        * js object demo
        * 1. 連線至 chroma
        * 2. 組合並獲取 Working Context 
        *'''
        chroma_login_info={
            "chromadb_path":"./jsobject_chroma",
            "collection_name":"test_collection",
            "embedding_function":DatabaseProcess.embedding_function}

        # test searching
        # query = "How to use mouse event for js object?"
        query = args.js
        js_chroma = DatabaseProcess.LangchainChromaDB(chroma_login_info)
        js_chroma.init_database()
        res_docs = js_chroma.lc_similarity_search_with_score(query)
        # working context for LLM later
        working_context = "\n".join([doc[0].page_content for doc in res_docs])
        print(working_context)
    

    if args.spec:
        '''**
        * spec (datasheet) demo
        * 1. 連線至 chroma
        * 2. 組合並獲取 Working Context 
        *'''
        chroma_login_info={
            "chromadb_path":"./spec_chroma",
            "collection_name":"test_collection",
            "embedding_function":DatabaseProcess.embedding_function}

        # test searching
        # query = "please show me the spec of cMT2158X"
        query = args.spec
        spec_chroma = DatabaseProcess.LangchainChromaDB(chroma_login_info)
        spec_chroma.init_database()
        res_docs = spec_chroma.lc_similarity_search_with_score(query)
        # working context for LLM later
        working_context = "\n".join([doc[0].page_content for doc in res_docs])
        print(working_context)
    
    if args.manual:
        '''**
        * manual demo
        * 1. 連線至 chroma
        * 2. 組合並獲取 Working Context
        *'''
        chroma_login_info={
            "chromadb_path":"./manual_chroma",
            "collection_name":"test_collection",
            "embedding_function":DatabaseProcess.embedding_function}

        # test searching
        # query = "please show me the spec of cMT2158X"
        query = args.manual
        manual_chroma = DatabaseProcess.LangchainChromaDB(chroma_login_info)
        manual_chroma.init_database()
        res_docs = manual_chroma.lc_similarity_search_with_score(query)
        # working context for LLM later
        working_context = "\n".join([doc[0].page_content for doc in res_docs])
        print(working_context)
    
    print("\n\n")
        
    # llm response
    if working_context.strip() != "" and query.strip() != "":
        for output in summary_agent.generate_answer(query, working_context):
            if output: print(output, end='')
        print("\n\n")