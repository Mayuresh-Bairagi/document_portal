from __future__ import annotations
import os
import fitz
import uuid
import json
from typing import Iterable, List, Optional, Dict, Any
import shutil
from langchain_community.vectorstores import FAISS
from datetime import datetime
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from logger.customlogger import CustomLogger
from exception.customexpection import DocumentPortalException
from utils.file_io import generate_session_id
from utils.model_loader import ModelLoader
import hashlib
import shutil
from langchain.schema import Document
from typing import Optional

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

class BaseSessionManager:
    def __init__(self, base_dir: str, session_id: Optional[str] = None):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.session_id = session_id or f"Session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.session_path = self.base_dir / self.session_id
        self.session_path.mkdir(parents=True, exist_ok=True)

        self.log.info("Session initialized",
                      base_dir=str(self.base_dir),
                      session_id=self.session_id,
                      session_path=str(self.session_path))

    def clean_old_sessions(self, keep_latest: int = 3):
        try:
            sessions = sorted(
                [f for f in self.base_dir.iterdir() if f.is_dir()],
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            for folder in sessions[keep_latest:]:
                shutil.rmtree(folder, ignore_errors=True)
                self.log.info("Old session folder deleted", path=str(folder))
        except Exception as e:
            self.log.error("Error cleaning old sessions", error=str(e))
            raise DocumentPortalException("Error cleaning old sessions", e) from e


class FaissManager(BaseSessionManager):
    def __init__(self,index_dir :Path, model_loader : Optional[ModelLoader] = None):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True,exist_ok =True)

        self.meta_path = self.index_dir / "ingested_meta.json"
        self._meta : Dict[str,Any] = {"rows": {}}

        if self.meta_path.exists():
            try:
                self._meta = json.loads(self.meta_path.read_text(encoding='utf-8')) or {"rpws":{}}
            except Exception :
                self._meta = {"rows":{}}
        
        self.model_loader = model_loader or ModelLoader()
        self.emb = self.model_loader.load_embeddings()
        self.vs :Optional[FAISS] = None
    
    def _exists(self):
        return (self.index_dir / "index.faiss").exists() and (self.index_dir / "index.pkl")
    
    @staticmethod
    def _fingerprint(text:str, md:Dict[str,Any]):
        src = md.get("source") or md.get("file_path")
        rid = md.get("row_id")

        if src is not None:
            return f"{src}::{'' if rid is None else rid}"
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    
    def _save_meta(self):
        self.meta_path.write_text(json.dumps(self._meta, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def add_documents(self,docs:List[Document]):

        if self.vs is None:
            raise RuntimeError("Call load_or_create() before add_documents_idempotent().")
        
        new_docs:List[Document] = []

        for d in docs:
            key = self._fingerprint(d.page_content, d.metadata or {})
            if key in self._meta["rows"]:
                continue
            self._meta['rows'][key] = True
            new_docs.append(d)
        if new_docs:
            self.vs.add_documents(new_docs)
            self.vs.save_local(str(self.index_dir))
            self._save_meta()
        return len(new_docs)

    def load_or_create(self,texts:Optional[List[str]]=None, metadatas: Optional[List[dict]] = None):
        if self._exists():
            self.vs = FAISS.load_local(
                str(self.index_dir),
                embeddings=self.emb,
                allow_dangerous_deserialization=True,
            )
            return self.vs
        
        
        if not texts:
            raise DocumentPortalException("No existing FAISS index and no data to create one", sys)
        self.vs = FAISS.from_texts(texts=texts, embedding=self.emb, metadatas=metadatas or [])
        self.vs.save_local(str(self.index_dir))
        return self.vs

class DocumentHandler(BaseSessionManager):
    def __init__(self, data_dir: Optional[str] = None, session_id: Optional[str] = None) -> None:
        base_dir = data_dir or os.getenv(
            'DATA_STORAGE_PATH',
            os.path.join(os.getcwd(), 'data', 'document_analysis')
        )
        super().__init__(base_dir, session_id)

    def save_pdf(self, uploaded_file):
        try:
            filename = os.path.basename(uploaded_file.name)
            if not filename.lower().endswith(".pdf"):
                raise DocumentPortalException("Invalid file type. Only PDFs are allowed.")

            save_path = self.session_path / filename
            with open(save_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            self.log.info("PDF saved successfully",
                          filename=filename,
                          save_path=str(save_path),
                          session_id=self.session_id)
            return save_path
        except Exception as e:
            self.log.error("Error saving PDF", error=str(e))
            raise DocumentPortalException("Error saving PDF", e) from e

    def read_pdf(self, pdf_path: str):
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            self.log.info("PDF read successfully",
                          pdf_path=pdf_path,
                          session_id=self.session_id,
                          pages=len(documents))
            return documents
        except Exception as e:
            self.log.error("Error reading PDF", error=str(e))
            raise DocumentPortalException("Error reading PDF", e) from e


class DocumentComparator(BaseSessionManager):
    def __init__(self, base_dir: str = "data/document_compare", session_id: Optional[str] = None):
        super().__init__(base_dir, session_id)

    def save_uploaded_files(self, reference_file, actual_file):
        try:
            ref_path = self.session_path / reference_file.name
            act_path = self.session_path / actual_file.name

            for fobj, out in ((reference_file, ref_path), (actual_file, act_path)):
                if not fobj.name.lower().endswith(".pdf"):
                    raise ValueError("Only PDF files are allowed.")
                with open(out, "wb") as f:
                    if hasattr(fobj, "read"):
                        f.write(fobj.read())
                    else:
                        f.write(fobj.getbuffer())

            self.log.info("Files saved",
                          reference=str(ref_path),
                          actual=str(act_path),
                          session=self.session_id)
            return ref_path, act_path
        except Exception as e:
            self.log.error("Error saving PDF files", error=str(e))
            raise DocumentPortalException("Error saving files", e) from e

    def read_pdf(self, pdf_path: Path) -> str:
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError(f"PDF is encrypted: {pdf_path.name}")
                parts = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    if text.strip():
                        parts.append(f"\n --- Page {page_num + 1} --- \n{text}")
            self.log.info("PDF read successfully", file=str(pdf_path), pages=len(parts))
            return "\n".join(parts)
        except Exception as e:
            self.log.error("Error reading PDF", file=str(pdf_path), error=str(e))
            raise DocumentPortalException("Error reading PDF", e) from e

    def combine_documents(self) -> str:
        try:
            doc_parts = []
            for file in sorted(self.session_path.iterdir()):
                if file.is_file() and file.suffix.lower() == ".pdf":
                    content = self.read_pdf(file)
                    doc_parts.append(f"Document: {file.name}\n{content}")
            combined_text = "\n\n".join(doc_parts)
            self.log.info("Documents combined", count=len(doc_parts), session=self.session_id)
            return combined_text
        except Exception as e:
            self.log.error("Error combining documents", error=str(e), session=self.session_id)
            raise DocumentPortalException("Error combining documents", e) from e


if __name__ == '__main__':
    handler = DocumentHandler(session_id='test_session')
    comparator = DocumentComparator()

    handler.clean_old_sessions(keep_latest=3)
    comparator.clean_old_sessions(keep_latest=3)
