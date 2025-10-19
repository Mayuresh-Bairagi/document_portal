# import os
# from pathlib import Path
# from DataIngestion.data_ingestion import DocumentHandler       # Your PDFHandler class
# from src.documentAnalys.data_analysis import DocumentAnalyzer  # Your DocumentAnalyzer class

# # Path to the PDF you want to test
# PDF_PATH = r"D:\College\LLMOPS\document_portal\data\document_analysis\HC-Verma-Concepts-of-Physics-Volume-1.pdf"

# # Dummy file wrapper to simulate uploaded file (Streamlit style)
# class DummyFile:
#     def __init__(self, file_path):
#         self.name = Path(file_path).name
#         self._file_path = file_path

#     def getbuffer(self):
#         return open(self._file_path, "rb").read()

# def main():
#     try:
#         # ---------- STEP 1: DATA INGESTION ----------
#         print("Starting PDF ingestion...")
#         dummy_pdf = DummyFile(PDF_PATH)

#         handler = DocumentHandler(session_id="test_ingestion_analysis")
        
#         saved_path = handler.save_pdf(dummy_pdf)
#         print(f"PDF saved at: {saved_path}")

#         text_content = handler.read_pdf(saved_path)
#         print(f"Extracted text length: {len(text_content)} chars\n")

#         # ---------- STEP 2: DATA ANALYSIS ----------
#         print("Starting metadata analysis...")
#         analyzer = DocumentAnalyzer()  # Loads LLM + parser
        
#         analysis_result = analyzer.analyze_document(text_content)

#         # ---------- STEP 3: DISPLAY RESULTS ----------
#         print("\n=== METADATA ANALYSIS RESULT ===")
#         for key, value in analysis_result.items():
#             print(f"{key}: {value}")

#     except Exception as e:
#         print(f"Test failed: {e}")

# if __name__ == "__main__":
#     main()





# import io
# from pathlib import Path

# from src.DataIngestion.data_ingestion import DocumentComparator
# from src.documentcompare.document_comparator import DocumentComparatorLLM


# class FakeUpload:
#     def __init__(self, file_path: Path):
#         self.name = file_path.name
#         self._buffer = file_path.read_bytes()

#     def getbuffer(self):
#         return self._buffer


# def test_compare_documents():
#     ref_path = Path(r"D:\College\resume\MayureshBairagi_Resume.pdf")
#     act_path = Path(r"D:\College\resume\MayureshBairagiVIIT.pdf")

#     comparator = DocumentComparator()

#     ref_upload = FakeUpload(ref_path)
#     act_upload = FakeUpload(act_path)
#     ref_file, act_file = comparator.save_uploaded_files(ref_upload, act_upload)

#     combined_text = comparator.combine_documents()

#     print("\n✅ Combined Text Preview (First 1000 chars):\n")
#     print(combined_text[:1000]) 


#     llm_comparator = DocumentComparatorLLM()
#     df = llm_comparator.compare_documents(combined_text)
#     print("Comparison DataFrame:\n")
#     print(df)

#     comparator.clean_old_sessions(keep_latest=3)


# if __name__ == "__main__":
#     test_compare_documents()



import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from src.DataIngestion.data_ingestion import FaissManager
from src.document_chat.retrieval import ConversationalRAG



def main():
    docs = []
    pdf_file = Path("data/document_analysis/HC-Verma-Concepts-of-Physics-Volume-1.pdf")

    loader = PyPDFLoader(str(pdf_file))
    file_docs = loader.load() 
    for d in file_docs:
        d.metadata["source"] = pdf_file.name
    docs.extend(file_docs)
    index_dir = Path("data/faiss_index")
    faiss_mgr = FaissManager(index_dir)

    if not faiss_mgr._exists():
        print("Creating new FAISS index...")
        texts = [d.page_content for d in docs]
        metadatas = [d.metadata for d in docs]
        faiss_mgr.load_or_create(texts=texts, metadatas=metadatas)
        faiss_mgr.add_documents(docs)
    else:
        print("FAISS index already exists. Loading it...")
        faiss_mgr.load_or_create()

    print("FAISS setup complete!")

    rag = ConversationalRAG(session_id="test-session")
    rag.load_retriever_from_faiss(index_path=str(index_dir))

    print("Testing question...")
    question = "who is the author of the document?"
    answer = rag.invoke(question)
    print("Answer:\n", answer)


if __name__ == "__main__":
    main()
