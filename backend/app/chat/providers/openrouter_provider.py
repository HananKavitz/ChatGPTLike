"""OpenRouter provider implementation for accessing multiple LLM models including Claude."""
import json
from typing import List, AsyncIterator, Dict, Any, Optional
from openai import AsyncOpenAI  # OpenRouter uses OpenAI-compatible API
from .base import BaseLLMProvider


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter API provider for chat completions (supports Claude and other models)."""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        # OpenRouter uses OpenAI-compatible API
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

    @property
    def provider_name(self) -> str:
        return "openrouter"

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "anthropic/claude-3.5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = True
    ) -> AsyncIterator[str] | str:
        """
        Get chat completion from OpenRouter API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (e.g., 'anthropic/claude-3.5-sonnet-20241022')
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            If stream=True: AsyncIterator yielding response chunks
            If stream=False: Complete response string
        """
        try:
            import logging
            logging.info(f"OpenRouter API call: model={model}, stream={stream}, messages={len(messages)}")

            # Create the chat completion
            if stream:
                stream_response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True
                )

                async def response_generator():
                    async for chunk in stream_response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content

                return response_generator()
            else:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False
                )
                return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")

    def format_messages(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Format messages for OpenRouter API.

        Args:
            messages: Raw messages from the application
            system_prompt: Optional system prompt to use

        Returns:
            Formatted messages list for OpenRouter API
        """
        formatted = []

        # Add system prompt if provided
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})

        # Add user and assistant messages
        for msg in messages:
            formatted.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        return formatted

    async def verify_api_key(self) -> bool:
        """
        Verify that the OpenRouter API key is valid.

        Returns:
            True if the API key is valid, False otherwise
        """
        try:
            # Make a minimal API call to verify the key
            # Use a cheap model for verification
            await self.client.chat.completions.create(
                model="openai/gpt-3.5-turbo",  # Cheapest model on OpenRouter
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            import logging
            logging.error(f"OpenRouter API key verification failed: {str(e)}")
            return False

    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get list of available Claude models on OpenRouter.

        Returns:
            List of model dictionaries with 'id' and 'name' keys
        """
        return [
            # Claude models on OpenRouter
            {"id": "anthropic/claude-opus-4-20250219", "name": "Claude Opus 4.6 (via OpenRouter)"},
            {"id": "anthropic/claude-3.5-sonnet-20241022", "name": "Claude 3.5 Sonnet (via OpenRouter)"},
            {"id": "anthropic/claude-3-haiku-20240307", "name": "Claude 3 Haiku (via OpenRouter)"},
            {"id": "anthropic/claude-3-opus-20240229", "name": "Claude 3 Opus (via OpenRouter)"},
            {"id": "anthropic/claude-3-sonnet-20240229", "name": "Claude 3 Sonnet (via OpenRouter)"},

            # Other models available on OpenRouter
            {"id": "openai/gpt-4o", "name": "GPT-4o (via OpenRouter)"},
            {"id": "openai/gpt-4-turbo", "name": "GPT-4 Turbo (via OpenRouter)"},
            {"id": "google/gemini-pro-1.5", "name": "Gemini Pro 1.5 (via OpenRouter)"},
        ]