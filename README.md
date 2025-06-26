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
  Note that any source files are not needed, because web crawler is applied in this case.   
  Then, you will see a chroma folder `jsobject_chroma` created as follows:   
  ```bash
  jsobject_chroma/
  ├── 97f45d8c-711b-4793-8c20-34214b890302/*.*
  └── chroma.sqlite3 // the collection name is `test_collection`
  ```
  To use the chroma db for vector search, please run   
  ```bash
  python Inference.py -j <query>
  ```
  where `<query>` is any question you want to ask. For example, "How to use mouse event for js object?"

- For Weintek Datasheets, please build chroma db by
  ```bash
  python run_spec.py -d ./spec_chroma -cn test_collection -s ./SVN_datasheet
  ```
  Note you need to prepare datasheets in `./SVN_datasheet` at first.   
  In this case, we only process files with extension `.docx` in order to extract tables from files.
  For inference,
  ```bash
  Inference.py -s "please show me the spec of cMT2158X"
  ```
