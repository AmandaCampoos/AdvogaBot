# Importações principais da biblioteca python-telegram-bot
from telegram import Update
from telegram.ext import ContextTypes
import requests
from logger.cloudwatch_logger import log_to_cloudwatch
from config import API_URL  # URL da API FastAPI para envio das perguntas

# Função que responde ao comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🤖 /start chamado")
    log_to_cloudwatch("/start chamado")  # Loga o uso do /start no CloudWatch

    # Envia uma mensagem de boas-vindas ao usuário
    await update.message.reply_text("Olá! 🤖 Sou um AdvogaBot Jurídico. Pergunte algo sobre seu documento.")

# Função principal para responder perguntas dos usuários
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text  # Captura a pergunta feita pelo usuário
    print(f"📩 Pergunta recebida: {user_question}")
    log_to_cloudwatch(f"Pergunta recebida: {user_question}")  # Log da pergunta recebida

    try:
        # Envia a pergunta para a API FastAPI via POST
        response = requests.post(API_URL, json={"question": user_question})
        response.raise_for_status()  # Lança exceção se a resposta for erro HTTP

        result = response.json()  # Converte a resposta da API para JSON

        print("📦 Resposta recebida da API.")
        log_to_cloudwatch(f"Resposta da API: {result}")  # Log da resposta

        # Extrai a resposta da API ou uma mensagem de erro padrão
        resposta = result.get("answer", "Desculpe, houve um erro ao buscar a resposta.")

        # Se a resposta for muito longa para o Telegram, divide em partes
        if len(resposta) > 4000:
            await enviar_resposta_em_partes(update, resposta)
        else:
            # Envia a resposta diretamente
            await update.message.reply_text(resposta, parse_mode="HTML")

        print("✅ Resposta enviada com sucesso.")
        log_to_cloudwatch("Resposta enviada com sucesso.")  # Log de sucesso

    except requests.exceptions.RequestException as e:
        # Caso ocorra erro de conexão ou timeout
        print(f"⚠️ Erro na requisição HTTP: {str(e)}")
        log_to_cloudwatch(f"Erro na requisição HTTP: {str(e)}", level="ERROR")
        await update.message.reply_text("⚠️ Não foi possível obter uma resposta da API.")

    except Exception as e:
        # Captura qualquer outro erro inesperado
        print(f"🔥 Erro inesperado: {str(e)}")
        log_to_cloudwatch(f"Erro inesperado: {str(e)}", level="ERROR")
        await update.message.reply_text("⚠️ Ocorreu um erro ao consultar a resposta.")

# Função auxiliar para enviar respostas muito longas em partes
async def enviar_resposta_em_partes(update: Update, resposta: str):
    # Divide o texto da resposta em blocos de até 4000 caracteres
    partes = [resposta[i:i+4000] for i in range(0, len(resposta), 4000)]
    for parte in partes:
        await update.message.reply_text(parte)  # Envia cada parte individualmente
