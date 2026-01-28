"""Business Backend LLM Module (Optional).

This module can be removed if LLM functionality is not needed.
Set LLM_ENABLED=false in environment to disable.
"""

from business_backend.llm.provider import LLMProvider, create_llm_provider

__all__ = ["LLMProvider", "create_llm_provider"]
