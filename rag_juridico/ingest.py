import os
import logging
import boto3
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma


class Config:
    def _init_(self):
        self.S3_BUCKET = "roberta-rag-bucket"
        self.S3_PREFIX = "dataset/"
        self.LOCAL_DATASET_DIR = "/mnt/data/dataset"
        self.PERSIST_DIR = "/mnt/data/chroma_db"
        self.COLLECTION_NAME = "juridico_chatbot"
        self.CHUNK_SIZE = 1000
        self.CHUNK_OVERLAP = 200
        self.MAX_FILES_LOG = 2
        self.EMBEDDING_MODE = "BEDROCK"


class DocumentProcessor:
    def extract_processo_number(self, text: str) -> str:
        import re
        match = re.search(r'(?:n[ºo.]?\s*|processo[^\d]*)(\d{12})', text, re.IGNORECASE)
        return match.group(1) if match else "desconhecido"

    def _init_(self, config: Config):
        self.config = config
        self._setup_logging()
        self.embedding_model = self._get_embedding_model()
        self.vectordb = None

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(_name_)

    def _get_embedding_model(self):
        if self.config.EMBEDDING_MODE == "BEDROCK":
            from langchain_aws import BedrockEmbeddings
            return BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", region_name="us-east-1")
        from langchain_core.embeddings import FakeEmbeddings
        return FakeEmbeddings(size=384)

    def download_pdfs_from_s3(self):
        self.logger.info("⬇ Baixando PDFs do S3...")
        s3 = boto3.client('s3')
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.config.S3_BUCKET, Prefix=self.config.S3_PREFIX)
        for page in pages:
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if key.endswith(".pdf"):
                    relative_path = Path(key).relative_to(self.config.S3_PREFIX)
                    dest_path = Path(self.config.LOCAL_DATASET_DIR) / relative_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    s3.download_file(self.config.S3_BUCKET, key, str(dest_path))
                    self.logger.info(f"📥 Baixado: {key} → {dest_path}")

    def load_documents(self) -> List[Document]:
        self.logger.info("📂 Carregando documentos...")
        pdf_files = list(Path(self.config.LOCAL_DATASET_DIR).rglob("*.pdf"))
        documents = []
        for i, pdf_path in enumerate(pdf_files):
            try:
                loader = PyPDFLoader(str(pdf_path))
                pages = loader.load()
                for page in pages:
                    processo_num = self.extract_processo_number(page.page_content)
                    page.metadata.update({
                        "source": str(pdf_path),
                        "file_name": pdf_path.name,
                        "folder": str(pdf_path.parent.relative_to(self.config.LOCAL_DATASET_DIR)),
                        "processo": processo_num
                    })
                documents.extend(pages)
                if i < self.config.MAX_FILES_LOG:
                    self.logger.info(f"✅ Processado: {pdf_path}")
            except Exception as e:
                self.logger.error(f"❌ Erro em {pdf_path.name}: {e}")
        self.logger.info(f"📄 Total de páginas: {len(documents)}")
        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        self.logger.info("✂ Dividindo textos...")
        splitter = RecursiveCharacterTextSplitter(chunk_size=self.config.CHUNK_SIZE, chunk_overlap=self.config.CHUNK_OVERLAP)
        chunks = splitter.split_documents(documents)
        self.logger.info(f"🔖 Total de pedaços: {len(chunks)}")
        return chunks

    def create_vector_store(self, chunks: List[Document]):
        self.logger.info("🔄 Gerando embeddings...")
        self.vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=self.embedding_model,
            persist_directory=self.config.PERSIST_DIR,
            collection_name=self.config.COLLECTION_NAME
        )
        self.vectordb.persist()
        self.logger.info(f"📦 Base criada com {self.vectordb._collection.count()} vetores")

    def show_results(self, query: str = "lei", k: int = 2):
        if not self.vectordb:
            self.logger.error("⚠ Banco de vetores não criado!")
            return
        self.logger.info(f"\n🔍 Resultados para '{query}':")
        results = self.vectordb.similarity_search(query, k=k)
        for i, doc in enumerate(results, 1):
            print(f"\n📌 Documento {i}:")
            print(f"📂 Origem: {doc.metadata['file_name']}")
            print(f"📁 Pasta: {doc.metadata['folder']}")
            print(f"📝 Conteúdo:\n{doc.page_content[:200]}...")


if _name_ == "_main_":
    config = Config()
    processor = DocumentProcessor(config)
    try:
        processor.download_pdfs_from_s3()
        docs = processor.load_documents()
        chunks = processor.split_documents(docs)
        processor.create_vector_store(chunks)
        processor.show_results()
    except Exception as e:
        processor.logger.error(f"🚨 Erro no processamento: {e}")
