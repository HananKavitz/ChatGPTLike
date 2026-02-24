"""Anthropic (Claude) provider implementation."""
import json
from typing import List, AsyncIterator, Dict, Any, Optional
from anthropic import AsyncAnthropic
from .base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic (Claude) API provider for chat completions."""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = AsyncAnthropic(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-opus-4-6",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = True
    ) -> AsyncIterator[str] | str:
        """
        Get chat completion from Anthropic API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Anthropic model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate (default 4096)
            stream: Whether to stream the response

        Returns:
            If stream=True: AsyncIterator yielding response chunks
            If stream=False: Complete response string
        """
        try:
            import logging
            logging.info(f"Anthropic API call: model={model}, stream={stream}, messages={len(messages)}")

            # Anthropic requires max_tokens to be specified
            if max_tokens is None:
                max_tokens = 4096

            # Extract system prompt if present
            system_prompt = None
            conversation_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                else:
                    # Convert 'user' and 'assistant' roles to Anthropic format
                    conversation_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

            # Create the message
            kwargs = {
                "model": model,
                "messages": conversation_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            if stream:
                stream_response = await self.client.messages.create(
                    **kwargs,
                    stream=True
                )

                async def response_generator():
                    async for event in stream_response:
                        if event.type == "content_block_delta" and hasattr(event.delta, 'text'):
                            yield event.delta.text

                return response_generator()
            else:
                response = await self.client.messages.create(**kwargs)
                return response.content[0].text

        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    def format_messages(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Format messages for Anthropic API with optional system prompt.

        Note: Anthropic handles system prompts differently than OpenAI.
        The system prompt is passed separately in the API call, not as a message.

        Args:
            messages: Raw messages from the application
            system_prompt: Optional system prompt to use

        Returns:
            Formatted messages list for Anthropic API
        """
        formatted = []

        # If system_prompt is provided, add it as the first message
        # It will be extracted in chat_completion method
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        else:
            formatted.append({"role": "system", "content": "You are Claude, a helpful AI assistant."})

        # Add user and assistant messages
        for msg in messages:
            # Ensure alternating user/assistant pattern for Anthropic
            formatted.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        return formatted

    async def verify_api_key(self) -> bool:
        """
        Verify that the Anthropic API key is valid.

        Returns:
            True if the API key is valid, False otherwise
        """
        try:
            # Make a minimal API call to verify the key
            # Use a simple completion with minimal tokens
            await self.client.messages.create(
                model="claude-3-haiku-20240307",  # Use a cheaper model for verification
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception:
            return False

    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get list of available Anthropic models.

        Returns:
            List of model dictionaries with 'id' and 'name' keys
        """
        return [
            {"id": "claude-opus-4-6", "name": "Claude Opus 4.6"},
            {"id": "claude-sonnet-4-6", "name": "Claude Sonnet 4.6"},
            {"id": "claude-haiku-4-5", "name": "Claude Haiku 4.5"},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet"},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"},
        ]