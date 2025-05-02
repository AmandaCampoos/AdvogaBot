FROM python:3.11-slim

WORKDIR /app

# Copia tudo do projeto para o container (exceto o que estiver no .dockerignore)
COPY . .

# Instala as dependências da raiz
RUN pip install --no-cache-dir -r requirements.txt

# Roda a API FastAPI (ajuste o caminho se o FastAPI estiver em outro arquivo)
CMD ["uvicorn", "chat.chatbot.py", "--host", "0.0.0.0", "--port", "8000"]