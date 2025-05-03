import os
from dotenv import load_dotenv
from pathlib import Path

# Sobe um nível para buscar o .env ao lado do docker-compose.yml
dotenv_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=dotenv_path)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://fastapi-api:8000")
