import os
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from andaluh import epa

# Load environment variables
load_dotenv()

# Define State
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def get_chat_model():
    # Check for LLM Provider
    provider = os.getenv("LLM_PROVIDER", "google").lower()
    
    if provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
        print(f"Using Ollama: {model} at {base_url}")
        return ChatOllama(model=model, base_url=base_url, temperature=0.7)
    else:
        # Default to Google Gemini
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("Please set the GOOGLE_API_KEY environment variable in a .env file.")
        model = os.getenv("MODEL", "gemini-2.5-flash")
        return ChatGoogleGenerativeAI(model=model, temperature=0.7)

def get_agent():
    llm = get_chat_model()
    
    # Router Logic
    def route_intent(state: State) -> Literal["chatbot", "translator", "andalofilo"]:
        messages = state["messages"]
        last_message = messages[-1]
        
        prompt = f"""Analiza el último mensaje del usuario y clasifica su intención.
        
        1. Si el usuario quiere traducir un texto explícitamente a Andalûh EPA (e.g. "traduce esto...", "cómo se dice X en andaluz"), responde "translator".
        2. Si el usuario pregunta sobre el andaluz como lengua/dialecto, su ortografía, gramática, historia, o la propuesta EPA, responde "andalofilo".
        3. En cualquier otro caso (conversación normal, preguntas generales, saludos), responde "chatbot".
        
        Usuario: {last_message.content if isinstance(last_message, HumanMessage) else ""}
        
        Responde ÚNICAMENTE con una de las tres palabras: "translator", "andalofilo" o "chatbot"."""
        
        response = llm.invoke([SystemMessage(content="Eres un clasificador de intenciones."), HumanMessage(content=prompt)])
        intent = response.content.strip().lower()
        
        if "translator" in intent:
            return "translator"
        if "andalofilo" in intent:
            return "andalofilo"
        return "chatbot"

    # 1. Chat Node: Generates response in Spanish
    def chatbot(state: State):
        messages = state["messages"]
        system_prompt = SystemMessage(content="Eres un asistente útil y amable. Responde siempre en español estándar.")
        response = llm.invoke([system_prompt] + messages)
        return {"messages": [response]}

    # 2. Translator Node: Translates user text to Andalûh EPA
    def translator(state: State):
        from andaluh_chatbot.tools import translate_to_andaluh_epa
        messages = state["messages"]
        last_message = messages[-1] # User message requesting translation
        
        # Bind the translation tool to the LLM to extract the text to translate
        llm_with_tools = llm.bind_tools([translate_to_andaluh_epa])
        
        prompt = f"""El usuario quiere traducir un texto a Andalûh EPA.
        Invoca la herramienta 'translate_to_andaluh_epa' con el texto EXACTO que el usuario quiere traducir.
        Si el usuario dice "Traduce 'Hola mundo'", el texto es "Hola mundo".
        
        Mensaje del usuario: {last_message.content}
        """
        
        # Invoke LLM with tools
        decision = llm_with_tools.invoke([SystemMessage(content="Eres un traductor."), HumanMessage(content=prompt)])
        
        # Check if tool was called
        if decision.tool_calls:
            tool_call = decision.tool_calls[0]
            if tool_call["name"] == "translate_to_andaluh_epa":
                text_to_translate = tool_call["args"].get("text", "")
                if text_to_translate:
                    translated_text = epa(text_to_translate)
                    return {"messages": [AIMessage(content=translated_text)]}
        
        # Fallback if no specific text found or tool failure
        return {"messages": [AIMessage(content="No he entendido qué texto quieres traducir.")]}

    # 3. Andalofilo Node: Expert in Andalusian linguistics
    def andalofilo(state: State):
        messages = state["messages"]
        system_prompt = SystemMessage(content="Eres un experto lingüista en el dialecto andaluz y la propuesta ortográfica EPA (Êttandâ pal Andalûh). Responde a las dudas del usuario con rigor pero de forma divulgativa.")
        response = llm.invoke([system_prompt] + messages)
        return {"messages": [response]}

    # Build Graph
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("translator", translator)
    graph_builder.add_node("andalofilo", andalofilo)

    # Define edges with router
    graph_builder.add_conditional_edges(START, route_intent)
    graph_builder.add_edge("chatbot", END)
    graph_builder.add_edge("translator", END)
    graph_builder.add_edge("andalofilo", END)

    return graph_builder.compile()
