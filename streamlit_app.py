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
    page_title="LBOT V1",
    page_icon="⚙️",
    layout="wide",
)

# CSS personalizado para estilizar o layout e os títulos
st.markdown(
    """
    <style>
    /* Estilo para o texto na sidebar */
    .stSidebar .stMarkdown, .stSidebar .stTextInput, .stSidebar .stTextArea, .stSidebar .stButton, .stSidebar .stExpander {
        color: white !important;
    }
    
    /* Deixar os títulos em branco */
    .stSidebar h2, .stSidebar h3 {
        color: white !important;
    }
    
    /* Estilo para o container de upload de arquivos */
    .stFileUploader > div > div {
        background-color: white;
        color: black;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #ccc;
    }

    /* Estilo para o texto dentro do balão de upload */
    .stFileUploader label {
        color: black !important;
    }

    /* Estilo para o botão de upload */
    .stFileUploader button {
        background-color: #8dc50b;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 8px 16px;
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
        col1, col2 = st.columns([1.5, 4])  # Ajuste as proporções conforme necessário
        with col1:
            st.image(ICON_PATH, width=100)
        with col2:
            st.title("LKBOT")
    except Exception as e:
        st.error(f"Erro ao carregar o ícone: {e}")
else:
    st.title("LKBOT")

# Subtítulo com fonte reduzida e texto branco
st.markdown(
    '<p class="subtitulo">Pronto para ajudar!</p>',
    unsafe_allow_html=True
)

# Criar uma opção de seleção para armazenar arquivos
st.sidebar.subheader("📂 Configuração de Arquivos")

# Interface para upload de arquivos
st.sidebar.subheader("📤 Upload de Documentos")
arquivos = st.sidebar.file_uploader(
    "Carregue arquivos (PDF, CSV, XLSX, PPTX)",
    type=["pdf", "csv", "xlsx", "pptx"],
    accept_multiple_files=True
)

api_key = st.sidebar.text_input("🔑 Chave API OpenAI", type="password", placeholder="Insira sua chave API")
if api_key:
    openai.api_key = api_key

    # Botão para limpar o histórico do chat
    if st.sidebar.button("🧹 Limpar Histórico do Chat", key="limpar_historico"):
        st.sidebar.success("Histórico do chat limpo com sucesso!")
else:
    st.warning("Por favor, insira sua chave de API para continuar.")

# Processar e armazenar os arquivos carregados
documentos_carregados = []
if arquivos:
    for arquivo in arquivos:
        caminho = salvar_arquivo(arquivo)
        documentos_carregados.append(caminho)
    st.sidebar.success(f"Arquivos armazenados em: {UPLOAD_FOLDER}")

# Função para processar os arquivos armazenados
def processar_arquivos():
    contexto = ""
    
    for caminho in documentos_carregados:
        if caminho.endswith(".pdf"):
            with pdfplumber.open(caminho) as pdf:
                for page in pdf.pages:
                    contexto += page.extract_text() + "\n"
        elif caminho.endswith(".csv"):
            df = pd.read_csv(caminho)
            contexto += df.to_string() + "\n"
        elif caminho.endswith(".xlsx"):
            df = pd.read_excel(caminho)
            contexto += df.to_string() + "\n"
        elif caminho.endswith(".pptx"):
            prs = pptx.Presentation(caminho)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        contexto += shape.text + "\n"
    
    return contexto

# Processa os arquivos e adiciona ao contexto
contexto_documentos = processar_arquivos()

# Função para gerar resposta usando GPT-4o
def gerar_resposta(pergunta):
    if not contexto_documentos:
        return "Nenhum documento carregado para análise."

    contexto_pergunta = f"Baseado nos documentos carregados, responda: {pergunta}\n\n"
    contexto_pergunta += contexto_documentos[:2000]

    mensagens = [
        {"role": "system", "content": "Você é um assistente inteligente."},
        {"role": "user", "content": contexto_pergunta}
    ]

    resposta = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=mensagens,
        temperature=0.3,
        max_tokens=800
    )
    return resposta["choices"][0]["message"]["content"]

# Entrada para perguntas no chat
user_input = st.chat_input("💬 Sua pergunta:")
if user_input and user_input.strip():
    resposta = gerar_resposta(user_input)
    st.write(f"**LKBOT:** {resposta}")
