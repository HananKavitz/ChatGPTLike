"""Factory for creating LLM provider instances."""
from typing import Optional
from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider


class LLMProviderFactory:
    """Factory class for creating LLM provider instances."""

    @staticmethod
    def create(provider_name: str, api_key: str) -> BaseLLMProvider:
        """
        Create an LLM provider instance.

        Args:
            provider_name: Name of the provider ('openai', 'anthropic', or 'openrouter')
            api_key: API key for the provider

        Returns:
            Instance of the requested provider

        Raises:
            ValueError: If the provider name is not supported
        """
        if provider_name == "openai":
            return OpenAIProvider(api_key)
        elif provider_name == "anthropic":
            from .anthropic_provider import AnthropicProvider
            return AnthropicProvider(api_key)
        elif provider_name == "openrouter":
            from .openrouter_provider import OpenRouterProvider
            return OpenRouterProvider(api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

    @staticmethod
    def get_supported_providers() -> list[str]:
        """Get list of supported provider names."""
        return ["openai", "anthropic", "openrouter"]