import os
import sys
import fitz
import uuid
from datetime import datetime
from pathlib import Path
from io import BytesIO  
from logger.customlogger import CustomLogger
from exception.customexpection import DocumentPortalException
from typing import List
from langchain_community.document_loaders import PyPDFLoader


class DocumentHandler:

    def __init__(self,data_dir = None, session_id = None) -> None:
        try : 
            self.log = CustomLogger().get_logger(__name__)
            self.data_dir = data_dir or os.getenv(
                'DATA_STORAGE_PATH', 
                os.path.join(os.getcwd(), 'data','document_analysis')
            )
            self.session_id = session_id or f"Session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

            self.session_path = os.path.join(self.data_dir,self.session_id)
            os.makedirs(self.session_path, exist_ok=True)
            self.log.info("PDF Handler initialized ",session_id = self.session_id,session_path = self.session_path)

        except Exception as e :
            self.log.error(f"Error initializing DocumentHandler : {e}")
            raise DocumentPortalException("Error initializing DocumentHandler", e) from e
        
    def save_pdf(self,uploaded_file):
        try:
            filename = os.path.basename(uploaded_file.name)
            if not filename.lower().endswith(".pdf"):
                raise DocumentPortalException("Invalid file type.only PDF's are allowed")
            
            save_path = os.path.join(self.session_path,filename)
            with open(save_path,'wb') as f:
                f.write(uploaded_file.getbuffer())
            self.log.info(f"PDF saved successfully" ,filename=filename, save_path=save_path,session_id=self.session_id)
            return save_path
        except Exception as e:
            self.log.error(f"Error saving PDF: {e}")
            raise DocumentPortalException("Error saving PDF", e) from e
        
    def read_pdf(self,pdf_path:str):
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            self.log.info("Pdf read successfully",pdf_path = pdf_path,session_id = self.session_id,pages = len(documents))
            return documents
        except Exception as e :
            self.log.error(f"Error reading PDF : {e}")
            raise DocumentPortalException("Error reading PDF", e) from e


if __name__ == '__main__':
    handler  = DocumentHandler(session_id='test_session')
    pdf_path = r'D:\College\LLMOPS\document_portal\data\document_analysis\HC-Verma-Concepts-of-Physics-Volume-1.pdf'

    class DummnyFile:
        def __init__(self,file_path) -> None:
            self.name = Path(file_path).name
            self._file_path = file_path
        
        def getbuffer(self):
            return open(self._file_path,'rb').read()
    
    dummy_pdf = DummnyFile(pdf_path)

    try:
        saved_path = handler.save_pdf(dummy_pdf)
        content = handler.read_pdf(saved_path)

        # print(f"PDF Content:\n{content}")
        # print(f"Length of PDF content : {len(content)}")
    except Exception as e:
        print(f"Error :{e}")
                
    print(f"Session id : {handler.session_id}")
    print(f"Session path : {handler.session_path}")