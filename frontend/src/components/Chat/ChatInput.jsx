import { useState, useRef, useEffect } from 'react'
import { useChat } from '../../hooks/useChat'
import { Send, Square } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'

const ChatInput = ({ sessionId, disabled = false }) => {
  const { sendMessage, isStreaming } = useChat()
  const { user } = useAuth()
  const [input, setInput] = useState('')
  const textareaRef = useRef(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px'
    }
  }, [input])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || !sessionId || isStreaming) return

    await sendMessage(sessionId, input)
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleStop = () => {
    // TODO: Implement stop streaming functionality
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      {!user?.openai_api_key && (
        <div className="mb-2 p-2 bg-yellow-900/20 border border-yellow-500 text-yellow-400 rounded text-sm text-center">
          Please add your OpenAI API key in{' '}
          <a href="/settings" className="underline hover:text-yellow-300">
            Settings
          </a>
        </div>
      )}

      <div className="relative flex items-end gap-2 bg-bg-input rounded-lg border border-border focus-within:ring-2 focus-within:ring-accent">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Message ChatGPTLike..."
          className="flex-1 px-4 py-3 bg-transparent text-text-primary placeholder-text-secondary resize-none focus:outline-none max-h-48 min-h-[56px]"
          rows={1}
        />

        <button
          type="button"
          onClick={isStreaming ? handleStop : undefined}
          className={isStreaming ? 'mr-2' : ''}
        >
          {isStreaming ? (
            <button
              type="button"
              onClick={handleStop}
              className="p-2 text-text-secondary hover:text-text-primary transition-colors"
            >
              <Square size={20} fill="currentColor" />
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim() || disabled}
              className="mr-2 p-2 bg-accent hover:bg-accent/90 disabled:bg-bg-input disabled:text-text-secondary text-white rounded-md transition-colors"
            >
              <Send size={20} />
            </button>
          )}
        </button>
      </div>

      <p className="text-xs text-text-secondary mt-2 text-center">
        ChatGPTLike can make mistakes. Consider checking important information.
      </p>
    </form>
  )
}

export default ChatInput
