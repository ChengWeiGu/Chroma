# -*- coding: utf-8 -*-
import os
import chardet
import argparse
import requests
from tqdm import tqdm
import DatabaseProcess
from os.path import exists
from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter



class JsSDKScanner:
    
    def __init__(self,root_url = "https://dl.weintek.com/public/Document/JS_Object_SDK/Current/"):
        # 紀錄每一個網站分頁的詳細資訊
        self.metadatas = [
                    {"source": "index.html", "url": root_url + "index.html", "root_url": root_url, "class_name": "Home", "description": "JS Object was first released in EasyBuilder Pro v6.05.01 in 2020. Its goal is to help create user‑customizable widgets."},
                    {"source": "Canvas.html", "url": root_url + "Canvas.html", "root_url": root_url, "class_name": "Canvas","description": "Canvas is a widget that implements part of the CanvasRenderingContext2D interface and can be used to draw graphics via scripting."},
                    {"source": "CanvasGradient.html", "url": root_url + "CanvasGradient.html", "root_url": root_url, "class_name": "CanvasGradient","description": "The CanvasGradient interface represents an opaque object that describes a gradient. It is returned by Canvas.createLinearGradient() or Canvas.createRadialGradient()."},
                    {"source": "Console.html", "url": root_url + "Console.html", "root_url": root_url, "class_name": "Console","description": "The Console object provides access to the debugging console (cMT Diagnoser)."},
                    {"source": "Container.html", "url": root_url + "Container.html", "root_url": root_url, "class_name": "Container","description": "The Container widget acts as a container for other widgets. Users can insert any type of widget into the container, and the container becomes their parent."},
                    {"source": "driver.Address.html", "url": root_url + "driver.Address.html", "root_url": root_url, "class_name": "Address","description": "driver.Address API."},
                    {"source": "driver.Subscription.html", "url": root_url + "driver.Subscription.html", "root_url": root_url, "class_name": "Subscription","description": "driver.Subscription API."},
                    {"source": "ImageData.html", "url": root_url + "ImageData.html", "root_url": root_url, "class_name": "ImageData","description": "The ImageData interface represents the underlying pixel data of a Canvas area. It can be returned by Canvas.createImageData() or Canvas.getImageData() and can be applied with Canvas.putImageData()."},
                    {"source": "JsObject.html", "url": root_url + "JsObject.html", "root_url": root_url, "class_name": "JsObject","description": "The JsObject class represents the JS widget placed by the user inside a window of an EasyBuilder Pro project. The widget can be accessed in source code via the variable this."},
                    {"source": "MemoryStorage.html", "url": root_url + "MemoryStorage.html", "root_url": root_url, "class_name": "MemoryStorage","description": "The MemoryStorage class is designed with reference to the Web Storage API's Storage interface. Its purpose is to enable JS widgets to communicate across different windows."},
                    {"source": "MouseArea.html", "url": root_url + "MouseArea.html", "root_url": root_url, "class_name": "MouseArea","description": "MouseArea is an invisible widget that is usually used together with a visible widget to provide mouse‑event handling. Mouse position information is provided through click, mousedown, mousemove and mouseup events."},
                    {"source": "MouseEvent.html", "url": root_url + "MouseEvent.html", "root_url": root_url, "class_name": "MouseEvent","description": "The MouseEvent interface represents events that occur due to user interaction with a pointing device (e.g., mouse). Common events include click, mousedown, mousemove and mouseup."},
                    {"source": "net.Curl.Easy.html", "url": root_url + "net.Curl.Easy.html", "root_url": root_url, "class_name": "Easy","description": "net.Curl.Easy is used for configuration. Web requests are performed by net.Curl.Multi through net.Curl.Multi#addHandle."},
                    {"source": "net.Curl.Multi.html", "url": root_url + "net.Curl.Multi.html", "root_url": root_url, "class_name": "Multi","description": "The multi interface offers several abilities that the easy interface does not, including event‑driven 'pull' transfers, multiple concurrent transfers in the same thread, waiting on both application and curl file descriptors, and scalability to thousands of parallel connections."},
                    {"source": "Widget.html", "url": root_url + "Widget.html", "root_url": root_url, "class_name": "Widget","description": "The Widget class is the base class of all widget objects (e.g., Canvas, Container, and MouseArea)."},
                    {"source": "module-@weintek_filesystem.html", "url": root_url + "module-@weintek_filesystem.html", "root_url": root_url, "class_name": "weintek/filesystem","description": "The built‑in @weintek/filesystem module provides functions to perform file‑system operations such as creating directories and deleting files and directories."},
                    {"source": "module-@weintek_libc_errno.html", "url": root_url + "module-@weintek_libc_errno.html", "root_url": root_url, "class_name": "weintek/libc/errno","description": "When an error occurs while using FILE‑related functions, use the @weintek/libc/errno module to obtain the error code and determine the cause."},
                    {"source": "module-@weintek_libc_stdio.html", "url": root_url + "module-@weintek_libc_stdio.html", "root_url": root_url, "class_name": "weintek/libc/stdio","description": "@weintek/libc/stdio is mainly used to read and write external files."},
                    {"source": "module-@weintek_libc_string.html", "url": root_url + "module-@weintek_libc_string.html", "root_url": root_url, "class_name": "weintek/libc/string","description": "@weintek/libc/string can be used to convert a given error code into a text description."},
                    {"source": "module-@weintek_libc_unistd.html", "url": root_url + "module-@weintek_libc_unistd.html", "root_url": root_url, "class_name": "weintek/libc/unistd","description": "@weintek/libc/unistd provides access to POSIX operating‑system APIs."},
                    {"source": "driver.html", "url": root_url + "driver.html", "root_url": root_url, "class_name": "driver","description": "The driver namespace provides classes and functions to read and write device address data."},
                    {"source": "driver.promises.html", "url": root_url + "driver.promises.html", "root_url": root_url, "class_name": "promises","description": "The driver.promises API provides an alternative set of asynchronous driver methods that return Promise objects instead of using callbacks."},
                    {"source": "net.Curl.html", "url": root_url + "net.Curl.html", "root_url": root_url, "class_name": "Curl","description": "Curl contains classes and options for performing web requests."},
                    {"source": "os.html", "url": root_url + "os.html", "root_url": root_url, "class_name": "os","description": "The os namespace provides operating‑system‑related utility methods and properties."},
                    {"source": "tutorial-demo-chartjs.html", "url": root_url + "tutorial-demo-chartjs.html", "root_url": root_url, "class_name": "Chart.js Demo","description": "Chart.js demonstration."},
                    {"source": "tutorial-demo-memo.html", "url": root_url + "tutorial-demo-memo.html", "root_url": root_url, "class_name": "Memo Board Demo","description": "Memo board demonstration."},
                    {"source": "tutorial-demo-soap.html", "url": root_url + "tutorial-demo-soap.html", "root_url": root_url, "class_name": "SOAP Client Demo","description": "In this example we use the simple NumberToWords service provided by www.dataaccess.com to build a SOAP client."},
                    {"source": "tutorial-tutorial-mouse-area.html", "url": root_url + "tutorial-tutorial-mouse-area.html", "root_url": root_url, "class_name": "Mouse Area Demo","description": "Mouse Area demonstration."},
                    {"source": "tutorial-tutorial-webinar.html", "url": root_url + "tutorial-tutorial-webinar.html", "root_url": root_url, "class_name": "Webinar Demo","description": "Webinar demonstration."},
                    {"source": "tutorial-tutorial-webrequest.html", "url": root_url + "tutorial-tutorial-webrequest.html", "root_url": root_url, "class_name": "Web Request Demo","description": "Current web requests are made via our net.Curl classes, including net.Curl.Easy and net.Curl.Multi. We know you may want full control over requests, but we make it easier by using a library similar to request.js as follows."},
                    {"source": "tutorial-tutorial1_en.html", "url": root_url + "tutorial-tutorial1_en.html", "root_url": root_url, "class_name": "Tutorial 1","description": "This tutorial demonstrates how to retrieve parameters in Config from source code."},
                    {"source": "tutorial-tutorial2_en.html", "url": root_url + "tutorial-tutorial2_en.html", "root_url": root_url, "class_name": "Tutorial 2","description": "This tutorial demonstrates how to use MouseArea and a JS widget by creating a non‑functional button."},
                    {"source": "tutorial-tutorial3_en.html", "url": root_url + "tutorial-tutorial3_en.html", "root_url": root_url, "class_name": "Tutorial 3","description": "This tutorial demonstrates how to read device address data using the driver.getData function."},
                    {"source": "tutorial-tutorial4_en.html", "url": root_url + "tutorial-tutorial4_en.html", "root_url": root_url, "class_name": "Tutorial 4","description": "This tutorial demonstrates how to monitor device data changes with Subscription."},
                    {"source": "tutorial-tutorial5_en.html", "url": root_url + "tutorial-tutorial5_en.html", "root_url": root_url, "class_name": "Tutorial 5","description": "This tutorial demonstrates how to write data to device addresses using the driver.setData function."},
                    {"source": "tutorial-tutorial6_en.html", "url": root_url + "tutorial-tutorial6_en.html", "root_url": root_url, "class_name": "Tutorial 6","description": "This tutorial demonstrates how to create a **custom** object using a JS widget."},
                    {"source": "tutorial-tutorial7_en.html", "url": root_url + "tutorial-tutorial7_en.html", "root_url": root_url, "class_name": "Tutorial 7","description": "Based on Tutorial 6, this tutorial further enhances the **custom object**. It also introduces options so users can choose the most suitable settings for their scenario."},
                    {"source": "global.html", "url": root_url + "global.html", "root_url": root_url, "class_name": "global","description": "console is an instance of the Console class in the global scope. With it, users can output messages to the debugging console (cMT Diagnoser)."}
                ]
        # 必須移除的suffix文字
        self.remove_text = "HomeClassesCanvasarcarcTobeginPathbezierCurveToclearRectclipclosePathcreateImageDatacreateLinearGradientcreateRadialGradientfillfillRectfillTextgetImageDatagetLineDashisPointInPathlineTomeasureTextmoveToputImageDataquadraticCurveTorectrestorerotatesavescalesetLineDashsetTransformstrokestrokeRectstrokeTexttransformtranslateCanvasGradientaddColorStopConsoleasserterrorinfologtracewarnContaineradddriver.AddressDataTypedataTypegetDataTypeSizedriver.SubscriptiononResponseImageDataJsObjectplaySoundMouseAreaMouseEventnet.Curl.EasycodeoptionstrErrorgetInforesetsetOptnet.Curl.MulticodeoptionseekfuncstrErroraddHandlegetCountonMessageremoveHandlesetOptWidgetEventsMouseArea#clickMouseArea#mousedownMouseArea#mousemoveMouseArea#mouseupNamespacesdrivergetDatasetDatasetStringDatadriver.promisesgetDatasetDatasetStringDatanet.CurlinfooshostnamenetworkInterfacesplatformTutorialsChart.js DemoMemo Board DemoSOAP Client DemoMouse AreaWebinar (Dec 10, 2020)Web RequestGlobalcancelAnimationFrameclearIntervalclearTimeoutconsolenetrequestAnimationFramerequiresetIntervalsetTimeoutwindow"
    
    '''**
    * 建立Langchain Document列表
    * @params: NA
    * @return: List<langchain.docstore.document>
    *'''
    def scan_web_and_create_document(self) -> list:
        # 建立 text splitter 
        text_splitter_recur = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 300,
            length_function = len,
            is_separator_regex=False
        )
        
        print("start scaning....")
        # 儲存Document物件
        doc_list = []
        # 掃描所有 url進行網頁爬蟲
        for i, data in tqdm(enumerate(self.metadatas), 
                            total=len(self.metadatas), 
                            desc = "Processing JS Object URLs ", 
                            unit="url"):
            # 網站爬蟲抓取文字資料
            url = data["url"]
            resp = requests.get(url)
            encoding = chardet.detect(resp.content)['encoding']
            resp.encoding = encoding
            soup = BeautifulSoup(resp.text, 'html.parser')
            content_texts = soup.get_text().replace(self.remove_text,"")
            # 文字切割
            for chunk in text_splitter_recur.split_text(content_texts):
                doc_list.append(Document(page_content=chunk,metadata=data))
        # 顯示前幾筆Doc
        print(doc_list[:10])
        print("total len of docs: ",len(doc_list))
        return doc_list
    

def main():
    
    parser = argparse.ArgumentParser(description='JS Object SDK')
    parser.add_argument('-d','--dir',type=str,help='chromadb儲存的資料夾位置')
    parser.add_argument('-cn','--collection_name', type=str, default="test_collection", help='collection name of chroma db')
    args = parser.parse_args()
    
    if args.dir is not None:
        # check if the directory exists, if not create it
        if not exists(args.dir):
            os.makedirs(args.dir)
        
        # chroma setting
        chroma_login_info={
            "chromadb_path":args.dir,
            "collection_name":args.collection_name,
            "embedding_function":DatabaseProcess.embedding_function
            }
        
        # langchain chroma
        lcdb_chroma = DatabaseProcess.LangchainChromaDB(chroma_login_info)
        lcdb_chroma.init_database()
        
        # js scanner
        print("start creating documents....")
        scanner = JsSDKScanner()
        doc_list = scanner.scan_web_and_create_document()
        lcdb_chroma.insert_data2db(doc_list)
        print("done")



if __name__ == "__main__":
    main()