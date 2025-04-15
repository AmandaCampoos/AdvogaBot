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
        
        # Configuração do LLM com parâmetros otimizados
        llm = BedrockLLM(
            client=bedrock_client,
            model_id="anthropic.claude-v2",                                                #adicionar modelo do LLM                            
            model_kwargs={
                "max_tokens_to_sample": 2048,
                "temperature": 0.3,
                "top_p": 0.9
            }
        )
        
        # Criação da cadeia RAG com configuração robusta
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        return qa_chain
    
    except Exception as e:
        st.error(f"Erro crítico durante inicialização: {str(e)}")
        return None

# Interface do chat simplificada e robusta
def main():
    st.markdown("""
    Sistema de consulta jurídica com RAG usando:
    - **Amazon Bedrock** (Claude v2)
    - **ChromaDB** para busca vetorial
    """)
    
    qa_chain = init_rag_system()
    
    if qa_chain is None:
        st.error("⚠️ O sistema não pôde ser inicializado. Verifique os logs para detalhes.")
        return
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Faça sua pergunta jurídica"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Processando consulta..."):
                try:
                    result = qa_chain.invoke({"query": prompt})
                    response = result["result"]
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    with st.expander("📄 Ver documentos de referência"):
                        for doc in result["source_documents"]:
                            st.markdown(f"**Fonte:** {doc.metadata.get('source', 'Desconhecida')}")
                            st.markdown(f"**Trecho relevante:**\n{doc.page_content[:300]}...")
                
                except Exception as e:
                    st.error(f"Erro ao processar sua pergunta: {str(e)}")

if __name__ == "__main__":
    main()