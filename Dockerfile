FROM python:3.11-slim

WORKDIR /app

# Copia tudo do projeto para o container (exceto o que estiver no .dockerignore)
COPY . .

# Instala as dependências da raiz
RUN pip install --no-cache-dir -r requirements.txt

# Comando para iniciar o bot
CMD ["python", "bot_telegram/src/bot.py"]
