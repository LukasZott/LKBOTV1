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

# Configuração inicial da página
st.set_page_config(
    page_title="LKBOT",
    page_icon="⚙️",
    layout="wide",
)

# CSS personalizado para estilizar a interface
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
    div[data-testid="stFileUploaderDropzone"] {
        color: white !important;
    }
    div[data-testid="stNotification"] > div > div {
        background-color: white !important;
        color: black !important;
        border-radius: 10px !important;
        padding: 10px !important;
        border: 1px solid #ccc !important;
    }
    .subtitulo {
        font-size: 16px !important;
        color: white !important;
    }
    .stSidebar h2, .stSidebar h3 {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Caminho para o ícone personalizado
ICON_PATH = "assets/icon_cade.png"

# Verificar se o arquivo do ícone existe
if os.path.exists(ICON_PATH):
    try:
        col1, col2 = st.columns([1.5, 4])
        with col1:
            st.image(ICON_PATH, width=100)
        with col2:
            st.title("LKBOT")
    except Exception as e:
        st.error(f"Erro ao carregar o ícone: {e}")
else:
    st.title("LKBOT")

# Subtítulo
st.markdown(
    '<p class="subtitulo">Pronto para ajudar!</p>',
    unsafe_allow_html=True
)

# Interface para a chave da OpenAI
api_key = st.sidebar.text_input("🔑 Chave API OpenAI", type="password", placeholder="Insira sua chave API")
if not api_key:
    st.warning("Por favor, insira sua chave de API para continuar.")
else:
    openai.api_key = api_key

# Interface para upload de arquivos
st.sidebar.subheader("📤 Upload de Documentos")
arquivos = st.sidebar.file_uploader(
    "Carregue arquivos (PDF, CSV, XLSX, PPTX)",
    type=["pdf", "csv", "xlsx", "pptx"],
    accept_multiple_files=True
)

# Processar arquivos carregados
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

# Processa os arquivos e adiciona ao contexto
contexto_documentos = processar_arquivos(arquivos) if arquivos else ""

# Função para gerar resposta usando GPT-4o
def gerar_resposta(pergunta):
    if not contexto_documentos:
        return "Nenhum documento carregado para análise."

    contexto_pergunta = f"Baseado nos documentos carregados, responda: {pergunta}\n\n"
    contexto_pergunta += contexto_documentos[:2000]  # Limita o contexto para evitar excesso de tokens

    mensagens = [
        {"role": "system", "content": "Você é uma IA criada para ser um assistente pessoal. Responda com precisão e criatividade."},
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

# Entrada para perguntas no chat
user_input = st.chat_input("💬 Sua pergunta:")
if user_input and user_input.strip():
    resposta = gerar_resposta(user_input)
    st.write(f"**LKBOT:** {resposta}")
