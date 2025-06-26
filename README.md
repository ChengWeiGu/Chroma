# Chroma
Here shows some simple methods to prep chroma db from files or webiste

## Platform
- Windows X64, Anaconda, Python3.11.11
- Please install packages with
  ```bash
  pip install -r requirements.txt
  ```
  
## Scripts   

- For Weintek JS Object SDK, please run the following cmd   
  ```bash
  python run_jssdk.py -d ./jsobject_chroma -cn test_collection
  ```
  You will see a chroma folder `jsobject_chroma` created.   
  ```bash
  jsobject_chroma/
  ├── 97f45d8c-711b-4793-8c20-34214b890302/*.*
  └── chroma.sqlite3
  ```
  To use the chroma db for vector search, please run   
  ```bash
  python Inference.py -j <query>
  ```
  where <query> is any question you want to ask. For example, "How to use mouse event for js object?"   
