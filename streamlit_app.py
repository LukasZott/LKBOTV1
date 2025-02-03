import streamlit as st
import openai
import os
import time
import json
import pandas as pd
import pdfplumber
import pptx
import openpyxl
from PIL import Image

# Configurações iniciais da página
st.set_page_config(
    page_title="CADE IA",
    page_icon="💛",
    layout="wide",
)

# CSS personalizado para a interface
st.markdown(
    """
    <style>
    .stSidebar .stMarkdown, .stSidebar .stTextInput, .stSidebar .stTextArea, .stSidebar .stButton, .stSidebar .stExpander {
        color: white !important;
    }
    .stMarkdown, .stTextInput, .stTextArea, .stButton, .stExpander {
        color: black !important;
    }
    .stFileUploader > div > div {
        background-color: white;
        color: black;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #ccc;
    }
    .stFileUploader label {
        color: black !important;
    }
    .stFileUploader button {
        background-color: #8dc50b;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 8px 16px;
    }
    div[data-testid="stNotification"] > div > div {
        background-color: white !important;
        color: black !important;
        border-radius: 10px !important;
        padding: 10px !important;
        border: 1px solid #ccc !important;
    }
    .stChatInput input {
        color: white !important;
    }
    .stChatInput input::placeholder {
        color: white !important;
    }
    div.stChatInput textarea {
        color: white !important;
    }
    div.stChatInput textarea::placeholder {
        color: white !important;
        opacity: 1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Caminho para a logo do bot
LOGO_BOT_PATH = "assets/Logo_bot.png"
if os.path.exists(LOGO_BOT_PATH):
    try:
        LOGO_BOT = Image.open(LOGO_BOT_PATH)
    except Exception as e:
        st.error(f"Erro ao carregar a logo: {e}")
        LOGO_BOT = None
else:
    LOGO_BOT = None

# Caminho para o ícone personalizado
ICON_PATH = "assets/icon_cade.png"
if os.path.exists(ICON_PATH):
    try:
        col1, col2 = st.columns([1.5, 4])
        with col1:
            st.image(ICON_PATH, width=100)
        with col2:
            st.title("CADE IA")
    except Exception as e:
        st.error(f"Erro ao carregar o ícone: {e}")
else:
    st.title("CADE IA")

# Subtítulo
st.markdown(
    '<p class="subtitulo">Sou uma IA especialista em Administração Pública desenvolvida pelo Instituto Publix em parceria com o Conselho Administrativo de Defesa Econômica CADE.</p>',
    unsafe_allow_html=True
)

# Inicialização segura das variáveis de estado
if "mensagens_chat" not in st.session_state:
    st.session_state.mensagens_chat = []

if "documentos" not in st.session_state:
    st.session_state.documentos = []

# Função para salvar o estado
def salvar_estado():
    estado = {"mensagens_chat": st.session_state.mensagens_chat}
    with open("estado_bot.json", "w") as f:
        json.dump(estado, f)

# Função para carregar o estado
def carregar_estado():
    if os.path.exists("estado_bot.json"):
        with open("estado_bot.json", "r") as f:
            estado = json.load(f)
            st.session_state.mensagens_chat = estado.get("mensagens_chat", [])

# Carregar o estado ao iniciar o aplicativo
carregar_estado()

# Função para limpar o histórico do chat
def limpar_historico():
    st.session_state.mensagens_chat = []
    salvar_estado()

# Função para processar arquivos carregados
def processar_arquivos(arquivos):
    contexto = ""
    
    for arquivo in arquivos:
        if arquivo.name.endswith(".pdf"):
            with pdfplumber.open(arquivo) as pdf:
                for page in pdf.pages:
                    contexto += page.extract_text() + "\n"
        elif arquivo.name.endswith(".csv"):
            df = pd.read_csv(arquivo)
            contexto += df.to_string() + "\n"
        elif arquivo.name.endswith(".xlsx"):
            df = pd.read_excel(arquivo)
            contexto += df.to_string() + "\n"
        elif arquivo.name.endswith(".pptx"):
            prs = pptx.Presentation(arquivo)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        contexto += shape.text + "\n"
    
    return contexto

# Interface para upload de arquivos
st.sidebar.subheader("📂 Upload de Documentos")
arquivos = st.sidebar.file_uploader(
    "Carregue arquivos (PDF, CSV, XLSX, PPTX)",
    type=["pdf", "csv", "xlsx", "pptx"],
    accept_multiple_files=True
)

if arquivos:
    st.session_state.documentos = processar_arquivos(arquivos)
    st.sidebar.success("Arquivos carregados com sucesso!")

# Função para gerar resposta com base nos arquivos
def gerar_resposta(texto_usuario):
    contexto = st.session_state.documentos

    if not contexto:
        return "Nenhum documento foi carregado para análise."

    contexto_pergunta = f"Baseado nos documentos fornecidos, responda: {texto_usuario}\n\n"
    contexto_pergunta += contexto[:2000]  # Limita o contexto para evitar excesso de tokens

    mensagens = [
        {"role": "system", "content": "Você é uma IA especializada em Administração Pública."},
        {"role": "user", "content": contexto_pergunta}
    ]

    tentativas = 3
    for tentativa in range(tentativas):
        try:
            time.sleep(1)
            resposta = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=mensagens,
                temperature=0.3,
                max_tokens=800
            )
            return resposta["choices"][0]["message"]["content"]
        except Exception as e:
            if tentativa < tentativas - 1:
                time.sleep(2)
                continue
            else:
                return f"Erro ao gerar a resposta: {str(e)}"

# Exibir a logo na sidebar
if LOGO_BOT:
    st.sidebar.image(LOGO_BOT, width=300)
else:
    st.sidebar.markdown("**Logo não encontrada**")

# Interface para a chave da OpenAI
api_key = st.sidebar.text_input("🔑 Chave API OpenAI", type="password", placeholder="Insira sua chave API")
if api_key:
    openai.api_key = api_key
    if st.sidebar.button("🧹 Limpar Histórico do Chat"):
        limpar_historico()
        st.sidebar.success("Histórico do chat limpo com sucesso!")
else:
    st.warning("Por favor, insira sua chave de API para continuar.")

# Entrada de perguntas no chat
user_input = st.chat_input("💬 Sua pergunta:")
if user_input and user_input.strip():
    st.session_state.mensagens_chat.append({"user": user_input, "bot": None})
    resposta = gerar_resposta(user_input)
    st.session_state.mensagens_chat[-1]["bot"] = resposta
    salvar_estado()

# Exibição do histórico do chat
with st.container():
    for mensagem in st.session_state.mensagens_chat:
        if mensagem["user"]:
            with st.chat_message("user"):
                st.write(f"*Você:* {mensagem['user']}")
        if mensagem["bot"]:
            with st.chat_message("assistant"):
                st.write(f"*CADE IA:* {mensagem['bot']}")
