from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_chroma import Chroma
import boto3
import os
import json
from dotenv import load_dotenv

# Configuração do ambiente
load_dotenv()

# Inicialização da API
app = FastAPI()

# Modelo para entrada do usuário
class QueryRequest(BaseModel):
    question: str

# Modelo para resposta da API
class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]

# Inicialização dos componentes RAG
def initialize_system():
    try:
        # Configuração do cliente Bedrock
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN")
        )

        # Configuração do ChromaDB para recuperação
        embeddings = BedrockEmbeddings(
            client=bedrock_client,
            model_id="amazon.titan-embed-text-v2:0"
        )

        persist_dir = "/mnt/data/chroma_db"
        collection_name = "juridico_chatbot"

        vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings,
            collection_name=collection_name
        )

        # Verificar se o banco foi carregado corretamente
        indexed_docs = vectorstore._collection.count()
        print(f"📂 Diretório de persistência: {persist_dir}")
        print(f"✅ Total de documentos indexados: {indexed_docs}")

        return vectorstore, bedrock_client
    except Exception as e:
        raise RuntimeError(f"Erro ao inicializar o sistema: {str(e)}")

# Inicializar os componentes no início
vectorstore, bedrock_client = initialize_system()

# Função para processar a consulta
def process_query(user_query):
    try:
        # Recupera documentos relevantes do ChromaDB
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        docs = retriever.invoke(user_query)

        context = "\n\n".join([doc.page_content for doc in docs])

        # Criação da mensagem no formato esperado
        input_text = f"""
        Você é um assistente jurídico especializado em consulta de documentos legais. 
        Baseie suas respostas estritamente nos documentos fornecidos.
        Se não encontrar documentos relevantes, responda somente com "Desculpe, não consegui encontrar informações relevantes nos documentos fornecidos." e não mostre mais nada.
        Pergunta: {user_query}
        Contexto: {context}
        """

        body = {
            "modelId": "amazon.nova-pro-v1:0",
            "contentType": "application/json",
            "accept": "application/json",
            "body": {
                "inferenceConfig": {
                    "max_new_tokens": 1000,
                    "temperature": 0.0,
                },
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": input_text
                            }
                        ]
                    }
                ]
            }
        }

        # Envia a mensagem para o Bedrock usando o cliente boto3
        response = bedrock_client.invoke_model( 
            modelId="amazon.nova-pro-v1:0",
            body=json.dumps(body["body"]),  
            contentType="application/json", 
            accept="application/json" 
        )

         # Parse da resposta
        response_content = json.loads(response['body'].read().decode('utf-8'))
        generated_text = response_content.get("messages", [{}])[0].get("content", [{}])[0].get("text", "Sem resposta.")

        # Retorna a resposta e os documentos de origem
        return generated_text, docs
    except Exception as e:
        raise ValueError(f"Erro ao processar a consulta: {str(e)}")


# Endpoint para consulta
@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        response, docs = process_query(request.question)

        # Montando as fontes
        sources = [
            {
                "source": doc.metadata.get("source", "Desconhecida"),
                "content_excerpt": doc.page_content[:300] + "..."
            }
            for doc in docs
        ]

        return {
            "answer": response,
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
