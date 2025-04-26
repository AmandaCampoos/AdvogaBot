<div align="justify">

# ⚖️ AdvogaBot

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-000000?style=for-the-badge&logo=langchain&logoColor=white)
![Telegram Bot](https://img.shields.io/badge/Telegram_Bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Amazon AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white)
![Amazon EC2](https://img.shields.io/badge/EC2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white)
![Amazon S3](https://img.shields.io/badge/S3-569A31?style=for-the-badge&logo=amazons3&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)

<div align="center">
  <img src="assets/AdvogaBot-2.jpg" alt="AdvogaBot" width="300" height="300">
</div>

**AdvogaBot** é um chatbot jurídico impulsionado por Inteligência Artificial que aplica RAG (Retrieval-Augmented Generation) para fornecer respostas precisas a partir de documentos legais hospedados na AWS.

> 🚧 **Projeto em construção**  
> Este repositório está em desenvolvimento ativo. Algumas funcionalidades ainda estão sendo implementadas ou testadas.

---

## 🚀 Como rodar o bot do Telegram:

### 1. Clone este repositório
```bash
git clone -b grupo-2 https://github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro.git
cd bot_telegram
```
### 2. Crie e ative um ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate # Para Linux
.venv\Scripts\activate # Para Windows
```
### 3. Instale as dependências
```bash
pip install -r requirements.txt
```
### 4. Configure as variáveis de ambiente
Crie um arquivo .env no diretório onde o bot está com o seguinte conteúdo:
```bash
TELEGRAM_BOT_TOKEN=seu_token_aqui
```
🔐 Como obter o token do Telegram?

#####  1. Abra o Telegram e procure por @BotFather

##### 2. Inicie uma conversa e envie o comando /newbot

##### 3.Siga as instruções para nomear seu bot

##### 4. O BotFather fornecerá um token de acesso, copie e cole no seu .env

### 5. Execute o bot
```bash
python bot.py
```
## 👥 Time de Desenvolvimento

<div align="center">

<table style="width:90%; border-collapse: collapse;">
  <tr>
    <td align="center" style="padding: 25px; border: 1px solid #ddd;">
      <img src="assets/Amanda-Ximenes.png" alt="Amanda Ximenes" width="200" height="200" style="border-radius: 50%; display: block; margin: auto;"><br>
      <strong>Amanda Ximenes</strong><br>
      <em>Infraestrutura e EC2</em><br><br>
      <a href="https://github.com/AmandaCampoos" target="_blank" title="GitHub de Amanda">
        <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub da Amanda">
      </a>
      <a href="https://linkedin.com/in/amanda-ximenes-a02ab8266" target="_blank" title="LinkedIn de Amanda">
        <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn da Amanda">
      </a>
    </td>
    <td align="center" style="padding: 25px; border: 1px solid #ddd;">
      <img src="assets/José-Carlos.png" alt="José Carlos" width="200" height="200" style="border-radius: 50%; display: block; margin: auto;"><br>
      <strong>José Carlos</strong><br>
      <em>Processamento de Dados e Embeddings</em><br><br>
      <a href="https://github.com/josecarlosjccf" target="_blank" title="GitHub de José">
        <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub do José">
      </a>
      <a href="https://www.linkedin.com/in/jos%C3%A9-carlos-candido-73b723235" target="_blank" title="LinkedIn de José">
        <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn do José">
      </a>
    </td>
  </tr>
  <tr>
    <td align="center" style="padding: 25px; border: 1px solid #ddd;">
      <img src="assets/Carlos-Vital.png" alt="Carlos Vital" width="200" height="200" style="border-radius: 50%; display: block; margin: auto;"><br>
      <strong>Carlos Eduardo</strong><br>
      <em>Implementação do Chatbot (LangChain + RAG)</em><br><br>
      <a href="https://github.com/CarlosEduardo-067" target="_blank" title="GitHub de Carlos">
        <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub do Carlos">
      </a>
      <a href="https://www.linkedin.com/in/carlos-eduardo-dos-santos-vital-9335612b1" target="_blank" title="LinkedIn de Carlos">
        <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn do Carlos">
      </a>
    </td>
    <td align="center" style="padding: 25px; border: 1px solid #ddd;">
      <img src="assets/Roberta-Oliveira.png" alt="Roberta Oliveira" width="200" height="200" style="border-radius: 50%; display: block; margin: auto;"><br>
      <strong>Roberta Oliveira</strong><br>
      <em>Interface com o Telegram e Logging</em><br><br>
      <a href="https://github.com/RobertakOliveira" target="_blank" title="GitHub de Roberta">
        <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub da Roberta">
      </a>
      <a href="https://linkedin.com/in/roberta-oliveira-b9a0961a4" target="_blank" title="LinkedIn de Roberta">
        <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn da Roberta">
      </a>
    </td>
  </tr>
</table>

</div>

</div>
