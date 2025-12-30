# Andalûh EPA Translation System and Chatbot 🇳🇬

This project implements an intelligent agent system using **LangChain** and **LangGraph** capable of maintaining a conversation (Chatbot) and automatically translating its responses to the **Andalûh EPA** (Êttandâ pal Andalûh) orthographic proposal.

It allows interaction both via command line (CLI) and through a modern web interface built with **Streamlit**, and supports multiple LLM providers (Google Gemini and Ollama).

## Features

*   **Agent Architecture**: Intelligent pipeline `Chatbot -> Translator` using LangGraph.
*   **Multi-Model**: Native support for:
    *   **Google Gemini** (via API).
    *   **Ollama** (Local models like Llama 3, Mistral, etc.).
*   **Interfaces**:
    *   🖥️ **CLI**: Simple terminal interface.
    *   🌐 **Web App**: Full application with Streamlit, including basic authentication.
*   **Dockerized**: Easy deployment with Docker Compose (including Ollama).

## Project Structure

*   `agents.py`: LangGraph graph definition and agent logic.
*   `tools.py`: Custom tools (wrapper for the `andaluh` library).
*   `app.py`: Streamlit web application.
*   `main.py`: CLI entry point.
*   `tests/`: Unit test suite to verify translation rules.

---

## 🚀 Quick Deployment with Docker (Recommended)

The easiest way to run the full stack (Web App + Local Ollama) is using Docker Compose.

1.  **Start the services**:
    ```bash
    docker compose up --build -d
    ```

2.  **Download model (First time only)**:
    If using Ollama, you need to download the model inside the container:
    ```bash
    docker exec -it andaluh-ollama ollama run llama3.2
    ```

3.  **Access**:
    Open your browser at [http://localhost:8501](http://localhost:8501).
    *   **User**: `admin`
    *   **Password**: `andaluh`

---

## 🛠️ Local Installation and Usage (Development)

### Requirements
*   Python 3.11+
*   (Optional) Ollama installed locally or Google API Key.

### 1. Environment Setup

1.  Create virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  Install dependencies:
    ```bash
    pip install -r andaluh_chatbot/requirements.txt
    ```

3.  Configure environment variables:
    Create a `.env` file in `andaluh_chatbot/.env` based on the following example:

    **To use Ollama (Local):**
    ```env
    LLM_PROVIDER=ollama
    OLLAMA_BASE_URL=http://127.0.0.1:11434
    OLLAMA_MODEL=llama3.2:latest
    ```

    **To use Google Gemini (Cloud):**
    ```env
    LLM_PROVIDER=google
    GOOGLE_API_KEY=your_api_key_here
    MODEL=gemini-2.5-flash
    ```

### 2. Run Application

**Command Line Interface (CLI):**
```bash
python -m andaluh_chatbot.main
```

**Web Interface (Streamlit):**
```bash
streamlit run andaluh_chatbot/app.py
```

---

## ✅ Tests

The project includes tests to verify that translation rules (seseo, ceceo, vowel opening, etc.) are applied correctly.

Run tests:
```bash
python -m unittest andaluh_chatbot/tests/test_translation.py
```
