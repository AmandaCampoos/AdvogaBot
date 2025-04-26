#!/bin/bash
set -e

echo "📦 Atualizando pacotes..."
sudo apt-get update -y
sudo apt-get upgrade -y

echo "🐳 Instalando Docker..."
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

echo "💻 Instalando Docker Compose..."
sudo apt-get install -y docker-compose

echo "🔑 Configurando permissões para o usuário atual..."
sudo usermod -aG docker $USER
newgrp docker

echo "📂 Clonando repositório..."
# colocar o repositorio correto em breve
git clone -b grupo-2 https://github.com 
cd SEU_REPOSITORIO/docker

echo "🚀 Subindo containers..."
docker-compose up -d --build

echo "✅ Tudo pronto! Bot rodando!"
