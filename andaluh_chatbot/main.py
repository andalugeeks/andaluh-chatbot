import sys
from langchain_core.messages import HumanMessage, AIMessage
from andaluh_chatbot.agents import get_agent

def main():
    print("Andalûh EPA Chatbot System (Pipeline: Chat -> Translator)")
    print("---------------------------------------------------------")
    
    try:
        agent = get_agent()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please check your .env file configuration.")
        return

    print("Agent ready. Type 'exit' to quit.")
    
    # Maintain local chat history
    chat_history = []
    
    while True:
        try:
            user_input = input("\nTú: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            
            # Add user message to history
            chat_history.append(HumanMessage(content=user_input))
            
            inputs = {"messages": chat_history}
            
            # We use invoke for simplicity to get the final result, 
            # but we could stream intermediate steps if desired.
            # Since the translator node replaces/adds the final message, 
            # we just want the last message of the final state.
            final_state = agent.invoke(inputs)
            
            # The last message in the state should be the translated response
            final_response = final_state["messages"][-1]
            
            print(f"EPA: {final_response.content}")
            
            # Update history with the final response (so the bot remembers what it 'said')
            # Note: The intermediate Spanish response is practically 'lost' or overwritten 
            # in the graph output if we don't return it.
            # Our graph returns all messages.
            # We should probably keep the history clean.
            # To keep context consistent, the bot should ideally remember what it outputted (EPA).
            # Although passing EPA back to a Spanish LLM might confuse it slightly, 
            # modern LLMs handle dialects reasonably well. 
            # Alternatively, we could keep the 'Spanish' hidden response in history if we had access to it,
            # but for this simple pipeline, appending the EPA response is fine.
            
            chat_history.append(final_response)
            
        except Exception as e:
            print(f"An error occurred: {e}")
            # import traceback; traceback.print_exc()

if __name__ == "__main__":
    main()
