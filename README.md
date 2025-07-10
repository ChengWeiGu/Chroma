# Chroma
Here shows some simple methods to prep chroma db from svn files or webiste

## Platform
- Windows X64, Anaconda, Python3.11.11
- Please install packages with
  
  ```bash
  pip install -r requirements.txt
  ```

## Data Scopes   
- Summary Tables
  | **Scope**  | **Description**                                                                                                                                       | **Source**                                                                                         |
  |-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
  | **Data1** | The Weintek JSSDK (JavaScript Software Development Kit) is a toolkit provided by Weintek to enable advanced scripting capabilities in its HMI products using JavaScript. | [Weintek JSSDK](https://dl.weintek.com/public/Document/JS_Object_SDK/Current/)    |
  | **Data2** | Weintek provides datasheets for its HMI models including detailed specifications and features of each device.                                          | Internal SVN or [Official Website](https://www.weintek.com/globalw/)                               |
  | **Data3** | Weintek offer many kind of manuals for user about EBPro, trouble shooting, FAQs, demo projects, ...etc.                                               | Internal SVN or [Official Website](https://www.weintek.com/globalw/)                               |
  
- Folder structure from SVN
  
  1. Take **Data2** for an example, the schema of source is:   
      ```markdown
      SVN_datasheet/
      ├── Accessory 
      ├── cMT 
      ├── eMT600 
      ├── eMT3000
      ├── ...
      └── mTV
      ```
  
  2. Take **Data3** for an example, the schema of source is:   
      ```markdown
      SVN_manual/
      ├── EDM // Example Projects for Product Users/Customers
      ├── EBP // This is EBPro User-Guide Manual for All Chapters
      ├── FAQ // Frequently Asked Questions for Product Users/Customers
      ├── FBA // Official Video Explanation for Weintek
      └── UM0 // Operation Manual for All Products
      ``` 

## Preparation Work   
In `DatabaseProcess.py`, please properly set azure endpoint, api version, api key, ...etc. before running ETL.   
```python
# create azure embedding function
embedding_function=AzureOpenAIEmbeddings(
        openai_api_version="<your api version>",
        openai_api_type="azure",
        openai_api_key="<your api key>",
        azure_endpoint="<your endpoint>",
        azure_deployment="<your model name of embedding>")
```

Similarily, one should also prepare the azure settings for ChatGPT API in `OpenAIFunction.py` before running inference:   
```python
## default setting
chat_settings = {
    'endpoint':"<your endpoint>",
    'api_key1':"<your api key1>",
    'api_key2':"<your api key2>",
    'region':"eastus",           # e.g. as swedencentral, westus, ...
    'api_version':"<your api version>",
    'chat_model':"<your model name of chatgpt>",
    'api_type':"azure"
}
```
  
## ETL Scripts   
- Data1-JSSDK:   
  ```bash
  python run_jssdk.py -d ./jsobject_chroma -cn test_collection
  ```
  Where `-d` means target folder of chroma and `-cn` is the collection name in the DB.   
  Note that files are not needed because web crawler method is applied in this case.   
  Finally, you will see the target chroma `jsobject_chroma` created as follows:   
  ```markdown
  jsobject_chroma/
  ├── 97f45d8c-711b-4793-8c20-34214b890302/*.* // uuid auto created by chroma
  └── chroma.sqlite3 // In the db, there is a collection called "test_collection" 

- Data2-Datasheets:   
  ```bash
  python run_spec.py -d ./spec_chroma -cn test_collection -s ./SVN_datasheet
  ```
  Where `-d` means target folder of chroma, `-cn` is the collection name and `-s` represents the path of source data.   
  Note you need to prepare datasheets in `./SVN_datasheet` at first as mentioned in **data2**. In this case, we only process files with extension `.docx` in order to extract tables from files.   

- Data3-Manuals:   
  ```bash
  python run_manual.py -d ./manual_chroma -cn test_collection -s ./SVN_manual
  ```
  Where `-d` means target folder of chroma, `-cn` is the collection name and `-s` represents the path of source data.   
  This is our most complicated case to tackle five different kinds of manuals. For each of them, extension and language of files should be considered.   

## Inference   
To use each chroma db for vector search, please run   
```bash
python run_inference.py <flag> <query>
```
Where `<flag>` is one of   

`-j`: vector search on jssdk scope   
`-s`: vector search on datasheets scope   
`-m`: vector search on manual scope   

and `<query>` is any question you want to ask.   

Try the following examples:   

- JSSDK   
```markdown
// Example 1: jssdk
python run_inference.py -j "How to use mouse event for js object?"

// Retrieval Output (working context)
Please refer to the demo image under ./demo_imgs/demo_retrieval_jssdk.png
You will see the ground truth document is at top 1 (top5 hit rate = 1)

// LLM Output:
Please refer to the demo image under ./demo_imgs/demo_llm_jssdk.png
You will see the summary from an agent.
```

- Spec   
```markdown
// Example 2: spec
python run_inference.py -s "please show me the spec of cMT2158X"

// Retrieval Output (working context)
Please refer to the demo image under ./demo_imgs/demo_retrieval_spec.png
You will see the ground truth document is at top 1 (top5 hit rate = 1)

// LLM Output:
Please refer to the demo image under ./demo_imgs/demo_llm_spec.png
You will see the summary from an agent.
```

- Manual   
```markdown
// Example 3: manual
python run_inference.py -m "how to install ebpro on windows?"

// Retrieval Output (working context)
Please refer to the demo image under ./demo_imgs/demo_retrieval_manual.png
You will see the ground truth document is at top 1 (top5 hit rate = 1)

// LLM Output:
Please refer to the demo image under ./demo_imgs/demo_llm_manual.png
You will see the summary from an agent.
```
