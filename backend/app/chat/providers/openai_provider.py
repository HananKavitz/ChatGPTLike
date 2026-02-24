"""OpenAI provider implementation."""
import json
from typing import List, AsyncIterator, Dict, Any, Optional
from openai import AsyncOpenAI
from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider for chat completions."""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = AsyncOpenAI(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "openai"

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = True
    ) -> AsyncIterator[str] | str:
        """
        Get chat completion from OpenAI API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: OpenAI model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            If stream=True: AsyncIterator yielding response chunks
            If stream=False: Complete response string
        """
        try:
            import logging
            logging.info(f"OpenAI API call: model={model}, stream={stream}, messages={len(messages)}")

            kwargs = {
                "model": model,
                "messages": messages,
                "stream": stream,
                "temperature": temperature
            }

            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens

            response = await self.client.chat.completions.create(**kwargs)

            if stream:
                async def response_generator():
                    async for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            yield chunk.choices[0].delta.content
                return response_generator()
            else:
                return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def format_messages(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Format messages for OpenAI API with optional system prompt.

        Args:
            messages: Raw messages from the application
            system_prompt: Optional system prompt to use

        Returns:
            Formatted messages list for OpenAI API
        """
        formatted = []

        # Add system message if provided or use default
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        else:
            formatted.append({"role": "system", "content": "You are a helpful AI assistant."})

        # Add user and assistant messages
        for msg in messages:
            formatted.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        return formatted

    async def verify_api_key(self) -> bool:
        """
        Verify that the OpenAI API key is valid.

        Returns:
            True if the API key is valid, False otherwise
        """
        try:
            # Make a minimal API call to verify the key
            await self.client.models.list()
            return True
        except Exception:
            return False

    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get list of available OpenAI models.

        Returns:
            List of model dictionaries with 'id' and 'name' keys
        """
        return [
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
            {"id": "gpt-4", "name": "GPT-4"},
            {"id": "gpt-4-turbo-preview", "name": "GPT-4 Turbo"},
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
        ]


def format_messages_for_openai(
    messages: List[Dict[str, str]],
    file_context: str = ""
) -> List[Dict[str, str]]:
    """
    Format messages for OpenAI API with optional file context.

    This function is kept for backward compatibility.
    Use OpenAIProvider.format_messages() for new code.

    Args:
        messages: List of message objects with 'role' and 'content'
        file_context: Context from uploaded files

    Returns:
        Formatted messages list for OpenAI API
    """
    formatted = []

    # Add system message with file context if available
    system_content = "You are a helpful AI assistant."
    if file_context:
        system_content += f"\n\nYou have access to the following data from uploaded files:\n{file_context}\n\n"
        system_content += "When asked about charts or visualizations:"
        system_content += "- Directly analyze the data and provide insights"
        system_content += "- Describe what the visualization would show"
        system_content += "- Explain patterns and trends you observe"
        system_content += "- DO NOT provide code, tutorials, or instructions on how to create charts"
        system_content += "- The system will automatically generate the actual chart visualization for you"
        system_content += "- Focus on interpreting the data, not explaining how to visualize it"
        system_content += "\n\nExample of how to respond:"
        system_content += "User: 'Create a pie chart showing sales by region'"
        system_content += "Response: 'Here's a pie chart showing sales distribution by region. The West region has the highest sales at 45%, followed by the East region at 30%. The North and South regions contribute 15% and 10% respectively. This suggests the Western market is our strongest performing area.'"

    formatted.append({"role": "system", "content": system_content})

    # Add user and assistant messages
    for msg in messages:
        formatted.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    return formatted


def parse_chart_config(ai_response: str) -> List[Dict[str, Any]]:
    """
    Parse chart configurations from AI response.

    This function is kept here for backward compatibility.

    Args:
        ai_response: The AI's text response

    Returns:
        List of chart configuration dicts
    """
    charts = []

    # Look for chart markers like ```chart or specific patterns
    # This is a simple implementation - can be enhanced
    lines = ai_response.split('\n')
    current_chart = None
    in_chart_block = False

    for line in lines:
        if '```chart' in line:
            in_chart_block = True
            current_chart = {"lines": []}
            continue
        elif in_chart_block and '```' in line and 'chart' not in line:
            in_chart_block = False
            # Try to parse accumulated chart data
            try:
                chart_data = json.loads('\n'.join(current_chart["lines"]))
                charts.append(chart_data)
            except json.JSONDecodeError:
                pass
            current_chart = None
        elif in_chart_block:
            current_chart["lines"].append(line)

    return charts