from dotenv import load_dotenv
import os
from pathlib import Path
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import logging 
import requests
from logger.cloudwatch_logger import log_to_cloudwatch

# Carrega variáveis do arquivo .env
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=dotenv_path)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Logging local
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🤖 /start chamado")
    log_to_cloudwatch("/start chamado")
    await update.message.reply_text("Olá! 🤖 Sou um AdvogaBot Jurídico. Pergunte algo sobre seu documento.")

# Função principal de resposta
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    print(f"📩 Pergunta recebida: {user_question}")
    log_to_cloudwatch(f"Pergunta recebida: {user_question}")

    try:
        response = requests.post("http://127.0.0.1:8001/query", json={"question": user_question})
        response.encoding = "utf-8"
        result = response.json()

        print(f"📦 Resposta recebida da API.")
        log_to_cloudwatch(f"Resposta da API: {result}")

        resposta = result.get("answer", "Desculpe, houve um erro ao buscar a resposta.")

        if len(resposta) > 4000:
            await enviar_resposta_em_partes(update, resposta)
        else:
            await update.message.reply_text(resposta)

        print("✅ Resposta enviada com sucesso.")
        log_to_cloudwatch("Resposta enviada com sucesso.")

    except Exception as e:
        print(f"🔥 Erro ao buscar resposta da API: {str(e)}")
        logging.error(f"Erro: {e}")
        log_to_cloudwatch(f"Erro no bot: {str(e)}", level="ERROR")
        await update.message.reply_text("⚠️ Ocorreu um erro ao consultar a resposta.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("🚀 Bot está rodando...")
    log_to_cloudwatch("Bot iniciado com sucesso 🚀")

    app.run_polling()
