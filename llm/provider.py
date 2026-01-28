"""
LLM Provider for Business Backend.

Simple OpenAI provider using LangChain for tool calling.
"""

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from business_backend.config import get_business_settings


class LLMProvider:
    """Provider for LLM interactions using LangChain."""

    def __init__(self, model: BaseChatModel) -> None:
        """
        Initialize LLM Provider.

        Args:
            model: LangChain chat model instance
        """
        self.model = model

    def get_model(self) -> BaseChatModel:
        """Get the underlying LangChain model."""
        return self.model

    def bind_tools(self, tools: list) -> BaseChatModel:
        """
        Bind tools to the model for function calling.

        Args:
            tools: List of LangChain tools

        Returns:
            Model with tools bound
        """
        return self.model.bind_tools(tools)


def create_llm_provider() -> LLMProvider | None:
    """
    Create LLM provider from settings.

    Returns:
        LLMProvider instance or None if disabled/not configured
    """
    settings = get_business_settings()

    if not settings.llm_enabled:
        return None

    if not settings.openai_api_key:
        return None

    model = ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        max_tokens=settings.openai_max_tokens,
        temperature=0,  # Deterministic for tool calling
    )

    return LLMProvider(model)
