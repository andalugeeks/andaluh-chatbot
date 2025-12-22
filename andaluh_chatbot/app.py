import streamlit as st
import os
from langchain_core.messages import HumanMessage, AIMessage
try:
    # Try importing from local package if running from root
    from andaluh_chatbot.agents import get_agent
except ImportError:
    # Adjust path if running differently
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from andaluh_chatbot.agents import get_agent

# Configuración de la página
st.set_page_config(page_title="Andalûh EPA Chatbot", page_icon="🇳🇬")

# --- Autenticación Básica ---
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] == "admin" and st.session_state["password"] == "andaluh":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs
        st.text_input("Usuario", on_change=None, key="username")
        st.text_input("Contraseña", type="password", on_change=password_entered, key="password")
        if st.button("Entrar", on_click=password_entered):
            return False
        return False
        
    elif not st.session_state["password_correct"]:
        # Password incomplete or wrong
        st.text_input("Usuario", on_change=None, key="username")
        st.text_input("Contraseña", type="password", on_change=password_entered, key="password")
        if st.button("Entrar", on_click=password_entered):
            return False
        st.error("😕 Usuario o contraseña incorrectos")
        return False
        
    else:
        # Password correct
        return True

if not check_password():
    st.stop()

# --- Interfaz del Chat ---

st.title("🇳🇬 Andalûh EPA Chatbot")
st.markdown("Escribe en castellano estándar y te responderé en **Andalûh EPA**.")

# Inicializar Agente
@st.cache_resource
def load_agent():
    return get_agent()

try:
    agent = load_agent()
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
                final_state = agent.invoke(inputs)
                
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
