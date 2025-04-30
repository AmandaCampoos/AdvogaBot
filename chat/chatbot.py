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

        if not docs:
            print("⚠️ Nenhum documento relevante encontrado para a consulta.")
            return "Nenhum documento relevante encontrado.", []

        # [DEBUG] Informações detalhadas dos documentos recuperados
        print("\n[DEBUG] Documentos recuperados e relevância:")
        for i, doc in enumerate(docs):
            print(f"Documento {i + 1}:")
            print(f"📂 Origem: {doc.metadata.get('file_name', 'Desconhecida')}")
            print(f"📝 Conteúdo: {doc.page_content[:500]}...")
            print(f"📊 Metadados: {doc.metadata}")
            print(f"{'-' * 50}")

        context = "\n\n".join([doc.page_content for doc in docs])

        # Verifica o conteúdo do contexto antes de enviar ao Bedrock
        print("\n[DEBUG] Contexto gerado para o Bedrock:")
        print(context)

        # Criação da mensagem no formato esperado
        input_text = f"""
        Você é um assistente jurídico especializado em legislação brasileira que responde consultas com base em documentos legais fornecidos.

        Siga estas etapas ao analisar cada consulta:
        1. Identifique os pontos legais principais da pergunta
        2. Localize as informações relevantes no contexto fornecido
        3. Analise como a lei se aplica ao caso específico
        4. Formule uma resposta completa citando artigos pertinentes

        Se a pergunta se referir a artigos de lei, cite o artigo completo, incluindo número e fonte (exemplo: "Art. 5º da Constituição Federal"), mantendo a formatação original.

        Exemplo 1:
        Pergunta: Quais são os requisitos para aposentadoria por idade no regime geral?
        Contexto: [Trecho da Lei 8.213/91]
        Art. 48. A aposentadoria por idade será devida ao segurado que, cumprida a carência exigida nesta Lei, completar 65 (sessenta e cinco) anos de idade, se homem, e 60 (sessenta), se mulher.
        § 1º Os limites fixados no caput são reduzidos para sessenta e cinquenta e cinco anos no caso de trabalhadores rurais.

        Pensamento: A pergunta solicita os requisitos para aposentadoria por idade. No contexto fornecido, encontro o Art. 48 da Lei 8.213/91 que estabelece estes requisitos. Preciso citar o artigo completo e explicar cada requisito.

        Resposta: De acordo com a legislação previdenciária, os requisitos para aposentadoria por idade são:

        "Art. 48. A aposentadoria por idade será devida ao segurado que, cumprida a carência exigida nesta Lei, completar 65 (sessenta e cinco) anos de idade, se homem, e 60 (sessenta), se mulher.
        § 1º Os limites fixados no caput são reduzidos para sessenta e cinquenta e cinco anos no caso de trabalhadores rurais." (Lei 8.213/91)

        Portanto, os requisitos são:
        1. Cumprimento do período de carência
        2. Idade mínima: 65 anos para homens e 60 anos para mulheres
        3. Para trabalhadores rurais: 60 anos para homens e 55 anos para mulheres

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
