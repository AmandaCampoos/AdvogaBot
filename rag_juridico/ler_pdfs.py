from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

# Caminho da pasta dataset(ainda localmente)
pdf_dir = Path("dataset/")

# Lista todos os PDFs em subpastas
pdf_files = list(pdf_dir.rglob("*.pdf"))

all_docs = []

for pdf_path in pdf_files:
    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()
    all_docs.extend(docs)

print(f"✅ Total de documentos carregados: {len(all_docs)}")

# Exemplo: mostra os primeiros 2 documentos carregados.(em fase de teste)(título e conteúdo resumido)
for i, doc in enumerate(all_docs[:2]):
    print(f"\n📄 Documento {i + 1}")
    print(f"Título: {doc.metadata.get('source')}")
    print(f"Conteúdo:\n{doc.page_content[:500]}...")
