import streamlit as st
import os
from langchain_core.messages import HumanMessage, AIMessage
try:
    # Try importing from local package if running from root
    from andaluh_chatbot.agents import get_agent
    from langfuse.langchain import CallbackHandler
except ImportError:
    # Adjust path if running differently
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from andaluh_chatbot.agents import get_agent
    from langfuse.langchain import CallbackHandler

# Configuración de la página
st.set_page_config(page_title="Andalûh EPA Chatbot", page_icon="🇳🇬")

# --- Autenticación Básica ---
def check_password():
    """Returns `True` if the user had the correct password."""
    
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    with st.form("login_form"):
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", key="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            if st.session_state["username"] == "admin" and st.session_state["password"] == "andaluh":
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("😕 Usuario o contraseña incorrectos")
                
    return False

# Check if login is enabled
login_enabled = os.getenv("LOGIN_ENABLED", "true").lower() == "true"

if login_enabled:
    if not check_password():
        st.stop()

# --- Interfaz del Chat ---

st.title("🇳🇬 Andalûh EPA Chatbot")
st.markdown("Escribe en castellano estándar y te responderé en **Andalûh EPA**.")

# Inicializar Agente
@st.cache_resource
def load_agent():
    # Initialize Langfuse Callback Handler if credentials are present
    langfuse_handler = None
    if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
        # Langfuse v3 reads configuration from environment variables
        # LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST
        langfuse_handler = CallbackHandler()
    else:
        st.warning("Langfuse credentials not found. Langfuse will not be used.")
    return get_agent(), langfuse_handler

try:
    agent, langfuse_handler = load_agent()
    if not agent:
        st.error("No se pudo cargar el agente")
        st.stop()
    if not langfuse_handler:
        st.error("No se pudo cargar el langfuse handler")
        st.stop()
except Exception as e:
    st.error(f"Error al cargar el agente: {e}")
    st.stop()

# Inicializar Historia del Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes anteriores
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

# Input de usuario
if prompt := st.chat_input("Escribe algo..."):
    # Añadir mensaje de usuario a la UI
    st.chat_message("user").markdown(prompt)
    # Añadir a la historia del estado
    st.session_state.messages.append(HumanMessage(content=prompt))

    # Obtener respuesta
    with st.chat_message("assistant"):
        with st.spinner("Pençando y traduçiendô..."):
            try:
                # Invocar al grafo
                # Pasamos toda la historia
                inputs = {"messages": st.session_state.messages}
                
                config = {}
                if langfuse_handler:
                    config["callbacks"] = [langfuse_handler]
                    
                final_state = agent.invoke(inputs, config=config)
                
                # Obtener último mensaje (Respuesta EPA)
                ai_response = final_state["messages"][-1]
                response_text = ai_response.content
                
                st.markdown(response_text)
                
                # Guardar respuesta en historia
                st.session_state.messages.append(ai_response)
                
            except Exception as e:
                st.error(f"A ocurrido un error: {e}")

# Sidebar con Info
with st.sidebar:
    st.header("Configuración")
    provider = os.getenv("LLM_PROVIDER", "google").upper()
    st.info(f"Proveedor LLM: **{provider}**")
    if provider == "OLLAMA":
        st.caption(f"Modelo: {os.getenv('OLLAMA_MODEL')}")
        st.caption(f"URL: {os.getenv('OLLAMA_BASE_URL')}")
    else:
        st.caption(f"Modelo: {os.getenv('MODEL')}")
        
    if st.button("Borrar Chat"):
        st.session_state.messages = []
        st.rerun()
