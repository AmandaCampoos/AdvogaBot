import os
import boto3
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

def carregar_documentos():
    bucket_name = "amanda-rag-bucket"
    prefix = "dataset/"
    local_dir = Path(os.getenv("LOCAL_DATA_PATH", "./data/pdfs"))
    local_dir.mkdir(parents=True, exist_ok=True)

    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    pdf_files_s3 = [
        content["Key"]
        for content in response.get("Contents", [])
        if content["Key"].endswith(".pdf")
    ]

    print(f"🔍 Encontrados {len(pdf_files_s3)} arquivos PDF no S3.")

    for key in pdf_files_s3:
        local_path = local_dir / Path(key).name
        s3.download_file(bucket_name, key, str(local_path))
        print(f"⬇️  Baixado: {key} → {local_path}")

    pdf_files = list(local_dir.glob("*.pdf"))
    all_docs = []

    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        all_docs.extend(docs)

    print(f"\n✅ Total de documentos carregados: {len(all_docs)}")

    for i, doc in enumerate(all_docs[:2]):
        print(f"\n📄 Documento {i + 1}")
        print(f"Título: {doc.metadata.get('source')}")
        print(f"Conteúdo:\n{doc.page_content[:500]}...")

    return all_docs

if _name_ == "_main_":
    carregar_documentos()