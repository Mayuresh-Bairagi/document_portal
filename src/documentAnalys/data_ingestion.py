import os
import sys
import fitz
import uuid
from datetime import datetime
from logger.customlogger import CustomLogger
from exception.customexpection import DocumentPortalException
from typing import List

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
        except Exception as e:
            self.log.error(f"Error saving PDF: {e}")
            raise DocumentPortalException("Error saving PDF", e) from e
        
    def read_pdf(self):
        try:
            pass
        except Exception as e :
            self.log.error(f"Error reading PDF : {e}")
            raise DocumentPortalException("Error reading PDF", e) from e


if __name__ == '__main__':
    handler  = DocumentHandler()
    print(f"Session id : {handler.session_id}")
    print(f"Session path : {handler.session_path}")