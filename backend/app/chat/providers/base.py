"""Base class for LLM providers."""
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, List, Any, Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str):
        """Initialize the provider with an API key."""
        self.api_key = api_key

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> AsyncIterator[str] | str:
        """
        Generate a chat completion.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: The model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            If stream=True: AsyncIterator yielding response chunks
            If stream=False: Complete response string
        """
        pass

    @abstractmethod
    def format_messages(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Format messages according to the provider's requirements.

        Args:
            messages: Raw messages from the application
            system_prompt: Optional system prompt to prepend

        Returns:
            Formatted messages for the provider's API
        """
        pass

    @abstractmethod
    async def verify_api_key(self) -> bool:
        """
        Verify that the API key is valid.

        Returns:
            True if the API key is valid, False otherwise
        """
        pass

    @abstractmethod
    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get list of available models for this provider.

        Returns:
            List of model dictionaries with 'id' and 'name' keys
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider."""
        pass