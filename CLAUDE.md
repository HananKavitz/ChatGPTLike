# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ChatGPTLike is a React-based frontend application that mimics ChatGPT's chat interface, integrating with OpenAI's API for AI responses. The project uses Tailwind CSS for styling.

## Common Commands

```bash
# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

## Architecture

### Component Structure

- **ChatMessage** (`src/components/ChatMessage.js`): Displays individual chat messages with user/AI styling differences
  - User messages: Light gray background, right-aligned
  - AI messages: Blue background, left-aligned
  - Supports Markdown rendering for AI responses

- **ChatWindow** (`src/components/ChatWindow.js`): Main chat interface component
  - Renders the list of messages
  - Handles scroll behavior
  - Passes callbacks for message sending

- **ChatInput** (`src/components/ChatInput.js`): Input component for user messages
  - Text input with Enter key support
  - Send button for message submission
  - Handles loading state (disabled during API calls)

### Data Flow

```
User Input → ChatInput → onSendMessage callback
                              ↓
                        App Component
                              ↓
                    Add message to state → Call OpenAI API
                              ↓
                    Add AI response to state → Save to localStorage
```

### State Management

The application uses React's `useState` for local state management:
- `messages`: Array of message objects `{ role, content }`
- `inputText`: Current user input
- `isLoading`: Loading state during API calls
- `error`: Error state for API failures

### API Integration

- Endpoint: OpenAI's chat completions API (`https://api.openai.com/v1/chat/completions`)
- Model: `gpt-3.5-turbo` (default, can be configured)
- Headers: `Authorization: Bearer YOUR_API_KEY`
- Request body includes `messages` array with conversation history

### Persistence

Chat history is persisted to `localStorage` under the key `'chatHistory'` to maintain conversation across page reloads.

### Styling

- **User messages**: `bg-gray-200 rounded-lg ml-auto max-w-xs`
- **AI messages**: `bg-blue-500 text-white rounded-lg mr-auto max-w-xs`
- **Input area**: Fixed at bottom with send button
- **Message list**: Scrollable with padding for last message

## Environment Setup

The project requires an OpenAI API key to function. Configure it in `.env` or pass directly to the API call during development.
