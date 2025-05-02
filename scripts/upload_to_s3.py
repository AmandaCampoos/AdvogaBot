import boto3
import os
import argparse
from zipfile import ZipFile
# Esse script faz o upload de arquivos para um bucket s3 da AWS.
# Ele descompacta arquivos zip 
# === Argumentos CLI ===
parser = argparse.ArgumentParser(description="Upload de arquivos para o S3")
parser.add_argument('--profile', type=str, help="Nome do perfil AWS para usar", required=False)
args = parser.parse_args()

# === Configuração da sessão AWS ===
if args.profile:
    session = boto3.Session(profile_name=args.profile)
else:
    session = boto3.Session()  # Usa padrão

s3 = session.client('s3')

# === CONFIGURAÇÕES ===
BUCKET_NAME = "amanda-rag-bucket" # colocar o nome do seu bucket aqui
LOCAL_FOLDER = "../dataset"
PREFIX = "dataset/"

# === Descompactar arquivos zip ===
zip_path = os.path.join(LOCAL_FOLDER, "juridicos.zip")
if os.path.exists(zip_path):
    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(LOCAL_FOLDER)
    print("✔️ Arquivos descompactados com sucesso!")

# === Upload dos arquivos ===
upload_count = 0
for root, _, files in os.walk(LOCAL_FOLDER):
    for file in files:
        if file.endswith(".zip") or file.startswith('.'):
            continue
        local_path = os.path.join(root, file)
        relative_path = os.path.relpath(local_path, LOCAL_FOLDER)
        s3_key = os.path.join(PREFIX, relative_path).replace("\\", "/")
        print(f"Tentando enviar: {local_path} -> s3://{BUCKET_NAME}/{s3_key}")
        try:
            s3.upload_file(local_path, BUCKET_NAME, s3_key)
            print(f"📤 Enviado: {file} -> s3://{BUCKET_NAME}/{s3_key}")
            upload_count += 1
        except Exception as e:
            print(f"❌ Erro ao enviar {file}: {e}")

print(f"✅ Upload finalizado. Total de arquivos enviados: {upload_count}")
