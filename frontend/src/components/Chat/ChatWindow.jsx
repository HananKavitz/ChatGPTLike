import { useEffect, useRef } from 'react'
import ChatMessage from './ChatMessage'
import { useChat } from '../../hooks/useChat'

const ChatWindow = ({ messages }) => {
  const { streamingMessage } = useChat()
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingMessage])

  return (
    <div className="max-w-3xl mx-auto py-4 px-4">
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-text-secondary min-h-[400px]">
          <h2 className="text-2xl font-semibold mb-2">ChatGPTLike</h2>
          <p className="text-sm">Start a conversation by typing a message below</p>
          {streamingMessage && (
            <div className="mt-4 flex items-center gap-2 text-accent">
              <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-accent"></div>
              <span>Thinking...</span>
            </div>
          )}
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}

          {/* Streaming message */}
          {streamingMessage && (
            <ChatMessage
              message={{
                id: 'streaming',
                role: 'assistant',
                content: streamingMessage,
                is_edited: false,
                created_at: new Date().toISOString(),
              }}
              isStreaming={true}
            />
          )}

          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  )
}

export default ChatWindow
