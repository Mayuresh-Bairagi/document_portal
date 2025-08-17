from pydantic import BaseModel , RootModel
from typing import List , Union
from enum import Enum

class Metadata(BaseModel):
    Summary : List[str]
    Title : str
    Author : List[str]
    DataCreated : str
    LastModifiedData : str
    Publisher : str
    Language : str
    PageCount : Union[int,str]
    Sentiment : str

class ChangeFormate(BaseModel):
    Page: str
    Changes : str

class SummaryResponse(RootModel[List[ChangeFormate]]):
    pass


class PromptType(str,Enum):
    DOCUMENT_ANALYSIS = 'document_analysis'
    DOCUMENT_COMAPRISON = 'document_comparison'
    CONTEXTUALIZE_QUESTION = 'contextualize_question'
    CONTEXT_QA = 'context_qa'

    