from dotenv import load_dotenv
import os
from pathlib import Path
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging 
import requests

# Carrega variáveis do arquivo .env
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=dotenv_path)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Comando /start - inicialização do bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! 🤖 Sou um AdvogaBot Jurídico. Pergunte algo sobre seu documento.")

# Responde perguntas do usuário
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    logging.info(f"Pergunta recebida: {user_question}")

    try:
        # Chamada para a API
        response = requests.post("http://127.0.0.1:8001/query", json={"question": user_question})
        response.encoding = "utf-8"  # Garante encoding correto
        result = response.json()
        logging.info(f"Resposta bruta da API: {result}")

        # Extrai resposta
        resposta = result.get("answer", "Desculpe, houve um erro ao buscar a resposta.")

        # Tratamento para resposta muito longa
        if len(resposta) > 4000:
            await enviar_resposta_em_partes(update, resposta)
        else:
            await update.message.reply_text(resposta)

    except Exception as e:
        logging.error(f"Erro ao buscar resposta da API: {e}")
        await update.message.reply_text("⚠️ Ocorreu um erro ao consultar a resposta.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("Bot está rodando...")
    app.run_polling()
