#!/bin/bash
set -e

echo "📦 Atualizando pacotes..."
sudo yum update -y

echo "🐳 Instalando Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

echo "💻 Instalando Docker Compose..."
sudo yum install -y docker-compose-plugin

echo "🔑 Configurando permissões para o usuário atual..."
sudo usermod -aG docker $USER
newgrp docker

echo "📂 Clonando repositório..."
git clone -b grupo-2 https://github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro.git

cd sprints-7-8-pb-aws-janeiro/docker

echo "🚀 Subindo containers..."
docker compose up -d --build

echo "✅ Tudo pronto! Bot rodando!"
