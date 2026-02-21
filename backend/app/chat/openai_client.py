"""OpenAI API client wrapper"""
import json
from typing import List, AsyncIterator, Dict, Any
from openai import AsyncOpenAI
from ..config import settings


class OpenAIClient:
    """OpenAI API client for chat completions"""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        stream: bool = True
    ) -> AsyncIterator[str]:
        """
        Get chat completion from OpenAI API

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: OpenAI model to use
            stream: Whether to stream the response

        Yields:
            Response content chunks if streaming, full content if not
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,
                temperature=0.7
            )

            if stream:
                async for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")


def format_messages_for_openai(
    messages: List[Dict[str, str]],
    file_context: str = ""
) -> List[Dict[str, str]]:
    """
    Format messages for OpenAI API with optional file context

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
        system_content += f"\n\nYou have access to the following data from uploaded files:\n{file_content}\n\nWhen asked about data, analyze it and provide insights. For visualizations, suggest appropriate chart types and configurations."

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
    Parse chart configurations from AI response

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
