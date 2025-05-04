from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import Chroma
import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]


def initialize_system():
    try:
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN")
        )

        embeddings = BedrockEmbeddings(
            client=bedrock_client,
            model_id="amazon.titan-embed-text-v2:0"
        )

        persist_dir = "/mnt/data/chroma_db"
        collection_name = "juridico_chatbot"

        vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_dir,
            collection_name=collection_name
        )

        indexed_docs = vectorstore._collection.count()
        print(f"📂 Diretório de persistência: {persist_dir}")
        print(f"✅ Total de documentos indexados: {indexed_docs}")

        return vectorstore, bedrock_client, embeddings 
    except Exception as e:
        raise RuntimeError(f"Erro ao inicializar o sistema: {str(e)}")


vectorstore, bedrock_client, embeddings = initialize_system() 

def process_query(user_query):
    try:
        
        # Busca documentos com score de similaridade
        docs_with_score = vectorstore.similarity_search_with_score(user_query, k=3)

        print("\n🔎 Documentos recuperados com score:")
        for doc, score in docs_with_score:
            print(f"📄 Score: {score:.2f} | Conteúdo: {doc.page_content[:200]}...\n")

        # Define limiar de relevância, só considera documentos com score abaixo de 1.4
        limiar_score = 1.4

        # Retorno padronizado para casos sem documentos relevantes
        tem_documento_relevante = any(score <= limiar_score for _, score in docs_with_score)

        if not tem_documento_relevante:
            return (
                "⚠️ Desculpe, não consegui identificar uma pergunta jurídica válida. "
                "Por favor, pergunte algo relacionado ao Direito ou aos documentos fornecidos.",
                []
            )

        # Extrai apenas os documentos considerados válidos (todos, pois passaram no filtro geral)
        docs = [doc for doc, _ in docs_with_score]

        context = "\n\n".join([doc.page_content for doc in docs if doc.page_content])
        
        # Verifica o conteúdo dos documentos antes de gerar o contexto
        for idx, doc in enumerate(docs):
            if not doc.page_content:
                print(f"⚠️ Documento {idx} está vazio ou None")
            else:
                print(f"📄 Documento {idx} tem {len(doc.page_content)} caracteres")

        # Gera o contexto apenas com conteúdos válidos
        context = "\n\n".join([doc.page_content for doc in docs if doc.page_content])

        # Loga o tamanho final do contexto
        print(f"📚 Contexto total gerado para a pergunta: {len(context)} caracteres")

        # Prompt estruturado com instruções para o modelo responder juridicamente
        input_text = f"""
        Você é um assistente jurídico altamente especializado, treinado para fornecer informações claras, precisas e fundamentadas sobre temas jurídicos. Seu objetivo é responder perguntas com base nos documentos fornecidos, sempre explicando seu raciocínio de forma detalhada e estruturada. Use o seguinte formato para suas respostas:
        1. Contextualização: Identifique o tema ou a área do direito relacionada à pergunta.
        2. Análise Jurídica: Explique, passo a passo, como você chegou à resposta, utilizando raciocínio jurídico claro.
        3. Resposta Final: Apresente a resposta final de forma objetiva e sucinta.
        
        Instruções adicionais para você:
            Sempre baseie suas respostas nos documentos carregados no sistema (RAG).
            Explique apenas com base nas informações disponíveis, não invente ou extrapole além do fornecido.
            Se a resposta não puder ser determinada com os dados disponíveis, informe o usuário educadamente.

        Exemplos de Perguntas e Respostas
        Exemplo 1:
            Usuário: Quais são os requisitos para um contrato ser considerado válido?
            Resposta do Chatbot:
            Contextualização: Esta questão refere-se ao direito civil, mais especificamente à validade contratual.
            Análise Jurídica: 
                1. Com base no documento "Código Civil - Art. 104", um contrato válido exige: 
                    Agente capaz. 
                    Objeto lícito, possível e determinado.
                    Forma prescrita ou não proibida por lei.

                2. Estas informações são corroboradas por "Jurisprudência STJ - Contratos", que reforça que a ausência de qualquer requisito pode acarretar nulidade.
                Resposta Final: Para um contrato ser válido, ele deve atender aos requisitos de capacidade do agente, objeto lícito e forma prescrita ou permitida pela lei.

        Exemplo 2:

            Usuário: É possível rescindir um contrato de trabalho sem aviso prévio?
            Resposta do Chatbot:
            Contextualização: Este tema envolve o direito trabalhista, relacionado à rescisão contratual.
            Análise Jurídica:

                1. Conforme indicado na "CLT - Art. 487", a rescisão sem aviso prévio é permitida em casos específicos, como justa causa.

                2. O documento "Jurisprudência STJ - Direito do Trabalho" explica que a justa causa deve ser devidamente comprovada.
                Resposta Final: Sim, é possível rescindir um contrato de trabalho sem aviso prévio, mas apenas nos casos previstos em lei, como justa causa.

        Instrução Importante:
        Sempre siga o formato dos exemplos acima ao responder perguntas. Se a pergunta for ambígua, solicite mais detalhes ao usuário antes de responder.

        Pergunta: {user_query}
        Contexto: {context}
        """

        body = {
            "inferenceConfig": 
            {
                "max_new_tokens": 1000, 
                "temperature": 0
            },
            "messages": [{
                "role": "user",
                "content": [{
                    "text": input_text
                    }]
                }
            ]
        }

        response = bedrock_client.invoke_model(
            modelId="amazon.nova-pro-v1:0",
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        response_content = json.loads(response['body'].read().decode('utf-8'))
        generated_text = response_content.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", "Sem resposta.")
        
        # Ajustes de formatação para resposta via Telegram
        generated_text = generated_text.replace("### Contextualização:", "📚 Contextualização ")
        generated_text = generated_text.replace("### Análise Jurídica:", "🔍 Análise Jurídica ")
        generated_text = generated_text.replace("### Resposta Final:", "✅ Conclusão ")
        
        # Remove marcações de markdown que o Telegram não entende
        generated_text = generated_text.replace("**", "")  # remove negrito
        generated_text = generated_text.replace("__", "")  # remove itálico


        return generated_text, docs
    except Exception as e:
        print("🔴 ERRO COMPLETO DURANTE A CONSULTA:")
        raise ValueError(f"Erro ao processar a consulta: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        response, docs = process_query(request.question)
        sources = [
            {"source": doc.metadata.get("source", "Desconhecida"), "content_excerpt": doc.page_content[:300] + "..."}
            for doc in docs
        ]
        return {"answer": response, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



 