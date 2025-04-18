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
        vectorstore = Chroma(
            persist_directory="/rag_juridico/chroma_db/chroma.sqlite3",
            embedding_function=embeddings
        )

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
            "inputText": input_text,
            "textGenerationConfig": {
                "maxTokenCount": 8192,
                "stopSequences": [],
                "temperature": 0,
                "topP": 1
            }
        }

        # Envia a mensagem para o Bedrock usando o cliente boto3
        response = bedrock_client.invoke_model( 
            modelId="amazon.titan-text-express-v1",  
            body=json.dumps(body),  
            contentType="application/json", 
            accept="application/json" 
        )

        # A resposta virá em formato JSON
        response_content = json.loads(response['body'].read().decode('utf-8'))

        # Retorna a resposta e os documentos de origem
        generated_text = response_content.get("results", [{}])[0].get("outputText", "Sem resposta.")

        # Retorna a resposta e os documentos de origem
        return generated_text, docs
    except Exception as e:
        raise ValueError(f"Erro ao processar a consulta: {str(e)}")


# Endpoint para consulta
@app.post("/query")
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
