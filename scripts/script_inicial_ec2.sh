#!/bin/bash

set -e

echo "📦 Atualizando pacotes..."
sudo yum update -y

echo "🐳 Instalando Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

echo "🔑 Adicionando usuário ao grupo docker..."
sudo usermod -aG docker $USER

echo "📂 Clonando repositório..."
git clone -b grupo-2 git@github.com:Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro.git

cd sprints-7-8-pb-aws-janeiro

echo "🛠️ Construindo imagem Docker..."
docker build -t bot-rag .

echo "🚀 Rodando container..."
docker run -d --name bot-rag-container bot-rag

echo "✅ Bot está rodando no container!"
