from typing import Dict
from bedrock_utils import get_claude_response
from knowledge_base import get_knowledge_base_response
import logging

logger = logging.getLogger(__name__)

def get_combined_response(runtime_client, kb_client, prompt: str) -> Dict[str, str]:
    """Combine knowledge base and Claude responses"""
    try:
        # First try to get relevant knowledge
        kb_context = get_knowledge_base_response(kb_client, prompt)
        logger.debug(f"Knowledge base context: {kb_context}")

        # Combine context with prompt
        full_prompt = f"""Context:
{kb_context if kb_context else 'No additional context available.'}

Customer Query:
{prompt}"""

        # Get Claude response
        return get_claude_response(runtime_client, full_prompt)

    except Exception as e:
        logger.error(f"Error getting combined response: {str(e)}")
        return get_claude_response(runtime_client, prompt)  # Fallback to just Claude 