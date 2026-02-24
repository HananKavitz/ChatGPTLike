"""Test Anthropic API key verification."""
import asyncio
import os
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

load_dotenv()

async def test_api_key(api_key):
    """Test if an Anthropic API key works."""
    print(f"Testing API key: {api_key[:10]}...")

    client = AsyncAnthropic(api_key=api_key)

    try:
        # Make a minimal API call
        response = await client.messages.create(
            model="claude-3-haiku-20240307",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("Success! API key is valid.")
        print(f"Response: {response.content[0].text}")
        return True
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    # Test with the API key from user's input
    api_key = input("Enter your Anthropic API key: ")
    asyncio.run(test_api_key(api_key))