from exception.customexpection import DocumentPortalException
from model.model import * 
from utils.model_loader import ModelLoader
from logger.customlogger import CustomLogger
import os 
import sys
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from propmt.propmt_lib import PROMPT_REGISTRY
from typing import List,Dict


class DocumentAnalyzer:
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        try :
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()

            self.parser = JsonOutputParser(pydantic_object=Metadata)
            self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser,llm =self.llm)

            self.propmt = PROMPT_REGISTRY['document_analysis']

            self.log.info("DocumentAnalyzer Initialized successfully")

        
        except Exception as e :
            self.log.error(f"Error initializing DocumentAnalyzer :{e}")
            raise DocumentPortalException(f"Error initializing DocumentAnalyzer :{e}")
        

    
    def analyze_document(self,document_text) -> dict:

        try:
            chain = self.propmt | self.llm | self.fixing_parser

            self.log.info("Meta-data analysis chain initalized")

            response = chain.invoke({
                    'format_instructions' : self.parser.get_format_instructions(),
                    'document_text': document_text
                })
            
            self.log.info("Metadata extraction successful",keys = list(response.keys()))

            return response
        
        except Exception as e : 
            self.log.error('Metadata analysis falied',error = str(e))
            raise DocumentPortalException(f"Metadata analysis failed: {e}")

