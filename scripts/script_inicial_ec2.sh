#!/bin/bash

set -e

# Atualiza os pacotes
echo "📦 Atualizando pacotes..."
sudo yum update -y

# Instala o Docker
echo "🐳 Instalando Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# Instala o Docker Compose manualmente
echo "💻 Instalando Docker Compose (manual)..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verifica versão do Docker Compose
docker-compose version

# Configura permissões para o usuário atual
echo "🔑 Configurando permissões para o usuário atual..."
sudo usermod -aG docker $USER
# newgrp docker   

# Clona o repositório com ssh -
# OBS : voce precisa ter configurado o ssh-agent e adicionado a chave privada para conseguir clonar o repósitorio

echo "📂 Clonando repositório..."
git clone -b grupo-2 git@github.com:Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro.git

cd sprints-7-8-pb-aws-janeiro/docker

# Sobe os containers
echo "🚀 Subindo containers..."
docker compose up -d --build

echo "✅ Tudo pronto! Bot rodando!"

# comentarios
# 1. O script atualiza os pacotes do sistema , instala o Docker e o Docker Compose, configura as permissões do usuário atual para usar o Docker
# 2. Clona o repositório do projeto e sobe os containers do Docker.
# 3. depois de mandar o script com 'scp -i "suachave.pem" ...scripts/script_inicial_ec2.sh ec2-user@SEU_IP_PUBLICO.compute-1.amazonaws.com:~/'
# 4. você pode executar o script com 'chmod +x script_inicial_ec2.sh
#./script_inicial_ec2.sh'