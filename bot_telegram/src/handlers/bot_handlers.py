from telegram import Update
from telegram.ext import ContextTypes
import requests
from logger.cloudwatch_logger import log_to_cloudwatch
from config import API_URL

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🤖 /start chamado")
    log_to_cloudwatch("/start chamado")
    await update.message.reply_text("Olá! 🤖 Sou um AdvogaBot Jurídico. Pergunte algo sobre seu documento.")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    print(f"📩 Pergunta recebida: {user_question}")
    log_to_cloudwatch(f"Pergunta recebida: {user_question}")

    try:
        response = requests.post(API_URL, json={"question": user_question})
        response.raise_for_status()
        result = response.json()

        print("📦 Resposta recebida da API.")
        log_to_cloudwatch(f"Resposta da API: {result}")

        resposta = result.get("answer", "Desculpe, houve um erro ao buscar a resposta.")

        if len(resposta) > 4000:
            await enviar_resposta_em_partes(update, resposta)
        else:
            await update.message.reply_text(resposta, parse_mode="HTML")

        print("✅ Resposta enviada com sucesso.")
        log_to_cloudwatch("Resposta enviada com sucesso.")
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Erro na requisição HTTP: {str(e)}")
        log_to_cloudwatch(f"Erro na requisição HTTP: {str(e)}", level="ERROR")
        await update.message.reply_text("⚠️ Não foi possível obter uma resposta da API.")
    
    except Exception as e:
        print(f"🔥 Erro inesperado: {str(e)}")
        log_to_cloudwatch(f"Erro inesperado: {str(e)}", level="ERROR")
        await update.message.reply_text("⚠️ Ocorreu um erro ao consultar a resposta.")

async def enviar_resposta_em_partes(update: Update, resposta: str):
    partes = [resposta[i:i+4000] for i in range(0, len(resposta), 4000)]
    for parte in partes:
        await update.message.reply_text(parte)
