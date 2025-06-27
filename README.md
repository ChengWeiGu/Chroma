# Chroma
Here shows some simple methods to prep chroma db from files or webiste

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
  Source: https://www.weintek.com/globalw/ (download from our official website)   
  Descr: Weintek provides datasheets for its HMI models, which include detailed specifications and features of each device

- Data3: Guide Manuals    
  Source: https://www.weintek.com/globalw/ (download from our official website)
  Schema:   
  ```markdown
  SVN_manual/
  ├── EDM // Example Projects for Product Users/Customers
  ├── EBP // This is EBPro User-Guide Manual for All Chapters
  ├── FAQ // Frequently Asked Questions for Product Users/Customers
  ├── FBA // Official Video Explanation for Weintek
  └── UM0 // Operation Manual for All Products
  ```
  Descr: Weintek offer many kind of manuals for user about EBPro, trouble shooting, demo projects, ...,etc.   
  
## Scripts of Langchain Chroma   
- Preparation Work (Embedding):
  In `DatabaseProcess.py` within line 8-13, please properly set azure endpoint, api version, api key, ...etc.
  ```python
  # create azure embedding function
  embedding_function=AzureOpenAIEmbeddings(
          openai_api_version="<your api version>",
          openai_api_type="azure",
          openai_api_key="<your api key>",
          azure_endpoint="<your endpoint>",
          azure_deployment="<your model name of embedding>")
  ```

- For Weintek JS Object SDK, please run the following cmd
  ```bash
  python run_jssdk.py -d ./jsobject_chroma -cn test_collection
  ```
  Note that any source files are not needed, because web crawler is applied in this case.   
  Then, you will see a chroma folder `jsobject_chroma` created as follows:   
  ```markdown
  jsobject_chroma/
  ├── 97f45d8c-711b-4793-8c20-34214b890302/*.*
  └── chroma.sqlite3 // the collection name is `test_collection`
  ```
  To use the chroma db for vector search, please run   
  ```bash
  python run_inference.py -j <query>
  ```
  where `<query>` is any question you want to ask. For example, "How to use mouse event for js object?"   
  The flag `-j` means doing inference for weintek js sdk.

- For Weintek Datasheets, please build chroma db by
  ```bash
  python run_spec.py -d ./spec_chroma -cn test_collection -s ./SVN_datasheet
  ```
  Note you need to prepare datasheets in `./SVN_datasheet` at first.   
  In this case, we only process files with extension `.docx` in order to extract tables from word file.   
  To use the chroma db for vector search, please run   
  ```bash
  python run_inference.py -s "please show me the spec of cMT2158X"
  ```
  Where your `<query>` comes after the flag `-s` which means doing inference for datasheets.
