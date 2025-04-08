import boto3
import json

s3 = boto3.client('s3')
textract = boto3.client('textract')

BUCKET_NAME = "jose-rag-bucket" # nome do bucket s3
PREFIX = "dataset/"
DEST_PREFIX = "extraidos/"

def lambda_handler(event, context):
    # Lista os objetos dentro da pasta dataset/
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)
    
    if "Contents" not in response:
        return {"status": "Nenhum arquivo encontrado"}

    for obj in response["Contents"]:
        key = obj["Key"]
        
        if key.endswith("/"):  # ignora "pastas"
            continue
        
        print(f"Processando: {key}")

        try:
            # Processa com Textract
            textract_response = textract.analyze_document(
                Document={'S3Object': {'Bucket': BUCKET_NAME, 'Name': key}},
                FeatureTypes=["FORMS", "TABLES"]
            )

            output_key = key.replace(PREFIX, DEST_PREFIX) + ".json"

            # Salva resultado no S3
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=output_key,
                Body=json.dumps(textract_response, indent=2),
                ContentType="application/json"
            )

            print(f"Resultado salvo em: {output_key}")
        
        except Exception as e:
            print(f"Erro ao processar {key}: {str(e)}")

    return {"status": "Concluído"}