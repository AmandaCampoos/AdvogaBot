import os
import logging
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# ================== CONFIGURAÇÕES ================== #
class Config:
    """Configurações flexíveis para processamento local ou na AWS"""
    
    def __init__(self):
        # Configurações comuns
        self.DATASET_DIR = "dataset"          # Pasta com subpastas de PDFs
        self.PERSIST_DIR = "chroma_db"        # Armazenamento dos vetores
        self.CHUNK_SIZE = 1000                # Tamanho dos pedaços de texto
        self.CHUNK_OVERLAP = 200              # Sobreposição entre pedaços
        self.MAX_FILES_LOG = 2                # Limite de arquivos mostrados no log
        
        # Modo de operação (ALTERE AQUI)
        self.EMBEDDING_MODE = "LOCAL"         # "LOCAL" ou "BEDROCK"

# ================== PROCESSADOR DE DOCUMENTOS ================== #
class DocumentProcessor:
    """Processa documentos em modo local ou com AWS Bedrock"""
    
    def __init__(self, config: Config):
        self.config = config
        self._setup_logging()
        self.embedding_model = self._get_embedding_model()
        self.vectordb = None

    def _setup_logging(self):
        """Configura o sistema de logs"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _get_embedding_model(self):
        """Seleciona o método de geração de embeddings"""
        if self.config.EMBEDDING_MODE == "BEDROCK":
            self.logger.info("🔧 Modo AWS Bedrock ativado")
            from langchain_aws import BedrockEmbeddings
            return BedrockEmbeddings()
        else:
            self.logger.info("🔧 Modo local ativado (sem dependências externas)")
            from langchain_core.embeddings import FakeEmbeddings
            return FakeEmbeddings(size=384)  # Embeddings simulados

    def load_documents(self) -> List[Document]:
        """Carrega todos os PDFs, incluindo subpastas"""
        self.logger.info("📂 Carregando documentos...")
        pdf_files = list(Path(self.config.DATASET_DIR).rglob("*.pdf"))
        documents = []
        
        for i, pdf_path in enumerate(pdf_files[:self.config.MAX_FILES_LOG]):
            try:
                loader = PyPDFLoader(str(pdf_path))
                pages = loader.load()
                for page in pages:
                    page.metadata.update({
                        "source": str(pdf_path),
                        "file_name": pdf_path.name,
                        "folder": pdf_path.parent.name
                    })
                documents.extend(pages)
                self.logger.info(f"✅ Processado: {pdf_path.name}")
            except Exception as e:
                self.logger.error(f"❌ Erro em {pdf_path.name}: {e}")
        
        self.logger.info(f"📄 Total de páginas: {len(documents)}")
        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Divide os documentos em pedaços menores"""
        self.logger.info("✂️ Dividindo textos...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP
        )
        chunks = splitter.split_documents(documents)
        self.logger.info(f"🔖 Total de pedaços: {len(chunks)}")
        return chunks

    def create_vector_store(self, chunks: List[Document]):
        """Cria e armazena os vetores"""
        self.logger.info("🔄 Gerando embeddings...")
        self.vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=self.embedding_model,
            persist_directory=self.config.PERSIST_DIR
        )
        self.vectordb.persist()
        self.logger.info("📦 Base de conhecimento criada!")

    def show_results(self, query: str = "lei", k: int = 2):
        """Mostra exemplos dos resultados"""
        if not self.vectordb:
            self.logger.error("⚠️ Banco de vetores não criado!")
            return
        
        self.logger.info(f"\n🔍 Resultados para '{query}':")
        results = self.vectordb.similarity_search(query, k=k)
        
        for i, doc in enumerate(results, 1):
            print(f"\n📌 Documento {i}:")
            print(f"📂 Origem: {doc.metadata['file_name']}")
            print(f"📝 Conteúdo:\n{doc.page_content[:200]}...")

# ================== EXECUÇÃO ================== #
if __name__ == "__main__":
    config = Config()
    processor = DocumentProcessor(config)
    
    try:
        # Pipeline completo
        docs = processor.load_documents()
        chunks = processor.split_documents(docs)
        processor.create_vector_store(chunks)
        processor.show_results()
        
    except Exception as e:
        processor.logger.error(f"🚨 Erro no processamento: {e}")