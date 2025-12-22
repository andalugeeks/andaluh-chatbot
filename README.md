# Sistema de Traducción y Chatbot Andalûh EPA 🇳🇬

Este proyecto implementa un sistema de agentes inteligentes utilizando **LangChain** y **LangGraph** capaz de mantener una conversación (Chatbot) y traducir automáticamente sus respuestas a la propuesta ortográfica **Andalûh EPA** (Êttandâ pal Andalûh).

Permite interactuar tanto por línea de comandos (CLI) como a través de una interfaz web moderna construida con **Streamlit**, y soporta múltiples proveedores de LLM (Google Gemini y Ollama).

## Características

*   **Arquitectura de Agentes**: Pipeline inteligente `Chatbot -> Traductor` usando LangGraph.
*   **Multi-Modelo**: Soporte nativo para:
    *   **Google Gemini** (vía API).
    *   **Ollama** (Modelos locales como Llama 3, Mistral, etc.).
*   **Interfaces**:
    *   🖥️ **CLI**: Interfaz de terminal sencilla.
    *   🌐 **Web App**: Aplicación completa con Streamlit, incluyendo autenticación básica.
*   **Dockerizado**: Despliegue sencillo con Docker Compose (incluyendo Ollama).

## Estructura del Proyecto

*   `agents.py`: Definición del grafo de LangGraph y lógica de los agentes.
*   `tools.py`: Herramientas personalizadas (wrapper de la librería `andaluh`).
*   `app.py`: Aplicación web Streamlit.
*   `main.py`: Punto de entrada CLI.
*   `tests/`: Suite de tests unitarios para verificar las reglas de traducción.

---

## 🚀 Despliegue Rápido con Docker (Recomendado)

La forma más sencilla de ejecutar todo el stack (App Web + Ollama Local) es usando Docker Compose.

1.  **Levantar los servicios**:
    ```bash
    docker compose up --build -d
    ```

2.  **Descargar modelo (Solo primera vez)**:
    Si usas Ollama, necesitas bajar el modelo dentro del contenedor:
    ```bash
    docker exec -it andaluh-ollama ollama run llama3.2
    ```

3.  **Acceder**:
    Abre tu navegador en [http://localhost:8501](http://localhost:8501).
    *   **Usuario**: `admin`
    *   **Contraseña**: `andaluh`

---

## 🛠️ Instalación y Uso Local (Desarrollo)

### Requisitos
*   Python 3.11+
*   (Opcional) Ollama instalado localmente o API Key de Google.

### 1. Configuración de Entorno

1.  Crear entorno virtual:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  Instalar dependencias:
    ```bash
    pip install -r andaluh_chatbot/requirements.txt
    ```

3.  Configurar variables de entorno:
    Crea un archivo `.env` en `andaluh_chatbot/.env` basado en el siguiente ejemplo:

    **Para usar Ollama (Local):**
    ```env
    LLM_PROVIDER=ollama
    OLLAMA_BASE_URL=http://127.0.0.1:11434
    OLLAMA_MODEL=llama3.2:latest
    ```

    **Para usar Google Gemini (Cloud):**
    ```env
    LLM_PROVIDER=google
    GOOGLE_API_KEY=tu_api_key_aqui
    MODEL=gemini-2.5-flash
    ```

### 2. Ejecutar Aplicación

**Interfaz de Comandos (CLI):**
```bash
python -m andaluh_chatbot.main
```

**Interfaz Web (Streamlit):**
```bash
streamlit run andaluh_chatbot/app.py
```

---

## ✅ Tests

El proyecto incluye tests para verificar que las reglas de traducción (seseo, ceceo, apertura de vocales, etc.) se aplican correctamente.

Ejecutar tests:
```bash
python -m unittest andaluh_chatbot/tests/test_translation.py
```
