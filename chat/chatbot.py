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
