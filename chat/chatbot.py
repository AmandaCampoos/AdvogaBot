import os
import streamlit as st
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_aws.llms import BedrockLLM
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import boto3

# Configuração da página
st.set_page_config(page_title="Assistente Jurídico", page_icon="⚖️")

# Título da aplicação
st.title("⚖️ Assistente Jurídico")

# Inicialização do sistema com tratamento robusto de erros
@st.cache_resource
def init_rag_system():
    try:
        # Configuração do cliente Bedrock
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

        embeddings = BedrockEmbeddings(
            client=bedrock_client,
            model_id="amazon.titan-embed-text-v1",
        )
        
        # Configuração do ChromaDB - com tratamento adicional
        vectorstore = Chroma(
            persist_directory="/rag_juridico/chroma_db/chroma.sqlite3",
            embedding_function=embeddings
        )
        
        # Template de prompt otimizado
        prompt_template = """
        Você é um assistente jurídico especializado em consulta de documentos legais. Baseie suas respostas estritamente nos documentos fornecidos.
        Se não souber a resposta, diga que não encontrou informações suficientes.
        
        Contexto: 
        {context}
        
        Pergunta: 
        {question}
        
        Resposta jurídica:
        """
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
    
    except Exception as e:
        st.error(f"Erro crítico durante inicialização: {str(e)}")
        return None
