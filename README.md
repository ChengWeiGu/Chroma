# Chroma
Here shows some simple methods to prep chroma db from svn files or webiste

## Platform
- Windows X64, Anaconda, Python3.11.11
- Please install packages with
  ```bash
  pip install -r requirements.txt
  ```

## Data Scope  
- Data1 : Weintek JSSDK   
  Source: https://dl.weintek.com/public/Document/JS_Object_SDK/Current/   
  Descr: The Weintek JSSDK (JavaScript Software Development Kit) is a toolkit provided by Weintek to enable advanced scripting capabilities in its HMI products using JavaScript. It allows developers to create custom functionalities, user-defined widgets, and integrate external APIs or data sources into their HMI projects. The JSSDK provides various modules, such as file system operations, web requests, and error handling, to enhance the flexibility and interactivity of HMI applications.   

- Data2: Datasheets (HMI Spec)   
  Descr: Weintek provides datasheets for its HMI models including detailed specifications and features of each device   
  Source: internal SVN or from our official website https://www.weintek.com/globalw/   
  Take internal SVN for an example, the source would be:   
  ```markdown
  SVN_datasheet/
  ├── Accessory 
  ├── cMT 
  ├── eMT600 
  ├── eMT3000
  ├── ...
  └── mTV
  ``` 
  
- Data3: Manuals   
  Descr: Weintek offer many kind of manuals for user about EBPro, trouble shooting, FAQs, demo projects, ...etc.   
  Source: internal SVN or from https://www.weintek.com/globalw/   
  Take internal SVN for an example, the source would be:   
  ```markdown
  SVN_manual/
  ├── EDM // Example Projects for Product Users/Customers
  ├── EBP // This is EBPro User-Guide Manual for All Chapters
  ├── FAQ // Frequently Asked Questions for Product Users/Customers
  ├── FBA // Official Video Explanation for Weintek
  └── UM0 // Operation Manual for All Products
  ``` 
  
## Scripts of ETL for Langchain Chroma   
- Preparation Work of Embedding:   
  In `DatabaseProcess.py` (line 8-13), please properly set azure endpoint, api version, api key, ...etc. before running scripts.   
  ```python
  # create azure embedding function
  embedding_function=AzureOpenAIEmbeddings(
          openai_api_version="<your api version>",
          openai_api_type="azure",
          openai_api_key="<your api key>",
          azure_endpoint="<your endpoint>",
          azure_deployment="<your model name of embedding>")
  ```

- ETL of Weintek JS Object SDK:   
  ```bash
  python run_jssdk.py -d ./jsobject_chroma -cn test_collection
  ```
  Where `-d` means target folder of chroma and `-cn` is the collection name regarding the DB.   
  Note that any files are not needed, because web crawler is applied in this case.   
  Finally, you will see the target chroma `jsobject_chroma` created as follows:   
  ```markdown
  jsobject_chroma/
  ├── 97f45d8c-711b-4793-8c20-34214b890302/*.*
  └── chroma.sqlite3 // In the db, the collection name is "test_collection"
  ```
  To use the chroma db for vector search, please run   
  ```bash
  python run_inference.py -j <query>
  ```
  where the flag `-j` means inference of jssdk and `<query>` is any question you want to ask. For example, "How to use mouse event for js object?"   

- ETL of Weintek Datasheets:   
  ```bash
  python run_spec.py -d ./spec_chroma -cn test_collection -s ./SVN_datasheet
  ```
  Where `-d` means target folder of chroma, `-cn` is the collection name regarding the DB and `-s` represents the path of source data.   
  Note you need to prepare datasheets in `./SVN_datasheet` at first as mentioned in data2.   
  In this case, we only process files with extension `.docx` in order to extract tables from word.   
  To use the chroma db for vector search, please run   
  ```bash
  python run_inference.py -s "please show me the spec of cMT2158X"
  ```
  Where your `<query>` comes after the flag `-s` which means implementing inference for datasheets.   

- ETL of Weintek Manuals:   
  ```bash
  python run_manual.py -d ./manual_chroma -cn test_collection -s ./SVN_manual
  ```
  Where `-d` means target folder of chroma, `-cn` is the collection name and `-s` represents the path of source data.   
  This is our most complicated case to tackle five different kinds of manuals. For each of them, extension and language of files should be considered.   
  To use the chroma db for vector search:   
  ```bash
  python run_inference.py -m "how to install ebpro on windows?"
  ```
  Where flag `-m` represents vector searching on manual scope.   
  
  
