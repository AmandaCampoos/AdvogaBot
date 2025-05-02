from dotenv import load_dotenv
from pathlib import Path
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from logger.cloudwatch_logger import log_to_cloudwatch
from handlers.bot_handlers import start, responder

# Carrega variáveis do .env
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=dotenv_path)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Inicializa o bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("🚀 Bot está rodando...")
    log_to_cloudwatch("Bot iniciado com sucesso 🚀")

    app.run_polling()
