from langchain_core.tools import tool
from andaluh import epa

@tool
def translate_to_andaluh_epa(text: str) -> str:
    """
    Translates a Spanish text into Andalûh EPA (Êttandâ pal Andalûh).
    Use this tool when you need to convert standard Spanish to the Andalusian dialect orthography.
    """
    return epa(text)
