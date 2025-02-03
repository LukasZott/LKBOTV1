import streamlit as st
import streamlit as st
import openai
import os
from PIL import Image
import time
import json

# Configurações iniciais
st.set_page_config(
    page_title="CADE IA",
    page_icon="💛",
    layout="wide",
)

# CSS personalizado para estilizar o balão de upload e o aviso
st.markdown(
    """
    <style>
    /* Estilo para o texto na sidebar */
    .stSidebar .stMarkdown, .stSidebar .stTextInput, .stSidebar .stTextArea, .stSidebar .stButton, .stSidebar .stExpander {
        color: white !important;  /* Cor do texto na sidebar */
    }

    /* Estilo para o texto na parte principal */
    .stMarkdown, .stTextInput, .stTextArea, .stButton, .stExpander {
        color: black !important;  /* Cor do texto na parte principal */
    }

    /* Estilo para o container de upload de arquivos */
    .stFileUploader > div > div {
        background-color: white;  /* Fundo branco */
        color: black;  /* Texto preto */
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #ccc;  /* Borda cinza para destacar */
    }

    /* Estilo para o texto dentro do balão de upload */
    .stFileUploader label {
        color: black !important;  /* Texto preto */
    }

    /* Estilo para o botão de upload */
    .stFileUploader button {
        background-color: #8dc50b;  /* Verde */
        color: white;  /* Texto branco */
        border-radius: 5px;
        border: none;
        padding: 8px 16px;
    }

    /* Estilo para o texto de drag and drop */
    .stFileUploader div[data-testid="stFileUploaderDropzone"] {
        color: black !important;  /* Texto preto */
    }

    /* Estilo para o container de avisos (st.warning) */
    div[data-testid="stNotification"] > div > div {
        background-color: white !important;  /* Fundo branco */
        color: black !important;  /* Texto preto */
        border-radius: 10px !important;
        padding: 10px !important;
        border: 1px solid #ccc !important;  /* Borda cinza para destacar */
    }

    /* Estilo para o ícone de aviso */
    div[data-testid="stNotification"] > div > div > div:first-child {
        color: #8dc50b !important;  /* Cor do ícone (verde) */
    }

    /* Estilo para o subtítulo */
    .subtitulo {
        font-size: 16px !important;  /* Tamanho da fonte reduzido */
        color: black !important;  /* Cor do texto alterada para preto */
    }

    /* Estilo para o rótulo do campo de entrada na sidebar */
    .stSidebar label {
        color: white !important;  /* Cor do texto branco */
    }

    /* Estilo para o texto na caixa de entrada do chat */
    .stChatInput input {
        color: white !important;  /* Cor do texto branco */
    }

    /* Estilo para o placeholder na caixa de entrada do chat */
    .stChatInput input::placeholder {
        color: white !important;  /* Cor do placeholder branco */
    }

    /* Estilo para o texto na caixa de entrada do chat */
div.stChatInput textarea {
    color: white !important;  /* Cor do texto branco */
}

/* Estilo para o placeholder na caixa de entrada do chat */
div.stChatInput textarea::placeholder {
    color: white !important;  /* Cor do placeholder branco */
    opacity: 1;  /* Garante que o placeholder seja totalmente visível */
}
    
     /* Estilo para o ícone */
    .stImage > img {
        filter: drop-shadow(0 0 0 #8dc50b);  /* Aplica a cor #8dc50b ao ícone */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Caminho para a logo do bot
LOGO_BOT_PATH = "assets/Logo_bot.png"

# Verificar se o arquivo da logo existe
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

# Verificar se o arquivo do ícone existe
if os.path.exists(ICON_PATH):
    try:
        # Usar st.columns para posicionar o ícone ao lado do título
        col1, col2 = st.columns([1.5, 4])  # Ajuste as proporções conforme necessário
        with col1:
            st.image(ICON_PATH, width=10000000)  # Exibe o ícone com largura de 30px
        with col2:
            st.title("CADE IA")  # Exibe o título
    except Exception as e:
        st.error(f"Erro ao carregar o ícone: {e}")
else:
    st.title("CADE IA")  # Fallback se o ícone não existir

# Subtítulo com fonte reduzida e texto preto
st.markdown(
    '<cp class="subtitulo">Sou uma IA especialista em Administração Pública desenvolvida pelo Instituto Publix em parceria com o Conselho Administrativo de Defesa Econômica CADE, estou aqui para ajudar.</p>',
    unsafe_allow_html=True
)

# Inicialização segura das variáveis de estado
if "mensagens_chat" not in st.session_state:
    st.session_state.mensagens_chat = []

# Função para salvar o estado em um arquivo JSON
def salvar_estado():
    estado = {
        "mensagens_chat": st.session_state.mensagens_chat
    }
    with open("estado_bot.json", "w") as f:
        json.dump(estado, f)

# Função para carregar o estado de um arquivo JSON
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

# Carregar arquivos de texto nativos como contexto
def carregar_contexto():
    contexto = ""
    # Adicione aqui os arquivos de texto que você deseja usar como contexto
    arquivos_contexto = [
        "contexto1.txt",
        "contexto2.txt",
        "contexto3.txt",
        "contexto4.txt",
        "contexto5.txt"
    ]

    for arquivo in arquivos_contexto:
        if os.path.exists(arquivo):
            with open(arquivo, "r", encoding="utf-8") as f:
                contexto += f.read() + "\n\n"
        else:
            st.error(f"Arquivo de contexto não encontrado: {arquivo}")
    
    return contexto

# Carregar o contexto ao iniciar o aplicativo
contexto = carregar_contexto()

# Função para dividir o texto em chunks
def dividir_texto(texto, max_tokens=800):  # Chunks menores (800 tokens)
    palavras = texto.split()
    chunks = []
    chunk_atual = ""
    for palavra in palavras:
        if len(chunk_atual.split()) + len(palavra.split()) <= max_tokens:
            chunk_atual += palavra + " "
        else:
            chunks.append(chunk_atual.strip())
            chunk_atual = palavra + " "
    if chunk_atual:
        chunks.append(chunk_atual.strip())
    return chunks

# Função para selecionar chunks relevantes com base na pergunta
def selecionar_chunks_relevantes(pergunta, chunks):
    # Lógica simples para selecionar chunks com base em palavras-chave
    palavras_chave = pergunta.lower().split()
    chunks_relevantes = []
    for chunk in chunks:
        if any(palavra in chunk.lower() for palavra in palavras_chave):
            chunks_relevantes.append(chunk)
    return chunks_relevantes[:4]  # Limita a 4 chunks para evitar excesso de tokens

# Função para gerar resposta com OpenAI usando GPT-4
def gerar_resposta(texto_usuario):
    if not contexto:
        return "Erro: Nenhum contexto carregado."

    chunks = dividir_texto(contexto)  # Divide o texto em chunks
    chunks_relevantes = selecionar_chunks_relevantes(texto_usuario, chunks)  # Seleciona chunks relevantes

    contexto_pergunta = "Você é uma IA feita pelo Publix em parceria com o CADE, que busca dar respostas especializadas sobre a Administração Pública e a instituição CADE, e. Responda com base no seguinte contexto:\n\n"
    for i, chunk in enumerate(chunks_relevantes):
        contexto_pergunta += f"--- Parte {i+1} do Contexto ---\n{chunk}\n\n"

    mensagens = [
        {"role": "system", "content": contexto_pergunta},
        {"role": "user", "content": texto_usuario}
    ]

    tentativas = 3  # Número de tentativas
    for tentativa in range(tentativas):
        try:
            # Implementar controle de taxa
            time.sleep(1)  # Adiciona um atraso de 1 segundo entre as solicitações
            resposta = openai.ChatCompletion.create(
                model="gpt-4o",  # Usando o GPT-4o
                messages=mensagens,
                temperature=0.3,
                max_tokens=800  # Limita a resposta a 800 tokens
            )
            return resposta["choices"][0]["message"]["content"]
        except Exception as e:
            if tentativa < tentativas - 1:  # Se não for a última tentativa
                time.sleep(2)  # Aguarda 2 segundos antes de tentar novamente
                continue
            else:
                return f"Erro ao gerar a resposta: {str(e)}"

# Adicionar a logo na sidebar
if LOGO_BOT:
    st.sidebar.image(LOGO_BOT, width=300)  # Ajuste o tamanho conforme necessário
else:
    st.sidebar.markdown("**Logo não encontrada**")

# Interface do Streamlit
api_key = st.sidebar.text_input("🔑 Chave API OpenAI", type="password", placeholder="Insira sua chave API")
if api_key:
    openai.api_key = api_key

    # Botão para limpar o histórico do chat
    if st.sidebar.button("🧹 Limpar Histórico do Chat", key="limpar_historico"):
        limpar_historico()
        st.sidebar.success("Histórico do chat limpo com sucesso!")
else:
    st.warning("Por favor, insira sua chave de API para continuar.")

user_input = st.chat_input("💬 Sua pergunta:")
if user_input and user_input.strip():
    st.session_state.mensagens_chat.append({"user": user_input, "bot": None})
    resposta = gerar_resposta(user_input)
    st.session_state.mensagens_chat[-1]["bot"] = resposta
    salvar_estado()  # Salva o estado após cada interação

with st.container():
    if st.session_state.mensagens_chat:
        for mensagem in st.session_state.mensagens_chat:
            if mensagem["user"]:
                with st.chat_message("user"):
                    st.write(f"*Você:* {mensagem['user']}")
            if mensagem["bot"]:
                with st.chat_message("assistant"):
                    st.write(f"*CADE IA:* {mensagem['bot']}")
    else:
        with st.chat_message("assistant"):
            st.write("*CADE IA:* Nenhuma mensagem ainda.")