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
    
    # 1. Chat Node: Generates response in Spanish
    def chatbot(state: State):
        messages = state["messages"]
        # Ensure system message is present or implicit. 
        # For simplicity, we prepend a system instruction if not present, 
        # or we just rely on the LLM's ability to answer.
        # Let's add a system prompt to ensure Spanish output.
        system_prompt = SystemMessage(content="Eres un asistente útil y amable. Responde siempre en español estándar.")
        
        # Invoke LLM
        response = llm.invoke([system_prompt] + messages)
        return {"messages": [response]}

    # 2. Translator Node: Translates the last AI message to Andalûh EPA
    def translator(state: State):
        messages = state["messages"]
        last_message = messages[-1]
        
        if isinstance(last_message, AIMessage) and last_message.content:
            # Translate content
            translated_text = epa(last_message.content)
            
            # We replace the last message content or create a new one?
            # User wants "the system to behave like a chat... final step allows translation".
            # Usually replacing the content makes it look like the bot speaks Andalûh.
            # Let's update the content of the AI message effectively.
            # In LangGraph with add_messages, simply returning a message with same ID would update it, 
            # but usually unique IDs are auto-generated. 
            # Let's just return a NEW message that represents the final output, 
            # OR we can manually construct the response.
            
            # Construct a new AI Message with the translated text.
            # Ideally, we want the user to see the Andaluh version.
            return {"messages": [AIMessage(content=translated_text)]}
            
        return {}

    # Build Graph
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("translator", translator)

    # Define edges
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", "translator")
    graph_builder.add_edge("translator", END)

    return graph_builder.compile()
