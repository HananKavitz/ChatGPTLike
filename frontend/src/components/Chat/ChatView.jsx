import { useEffect } from 'react'
import { useChat } from '../../hooks/useChat'
import { useAuth } from '../../hooks/useAuth'
import ChatWindow from './ChatWindow'
import ChatInput from './ChatInput'
import FileUploader from '../File/FileUploader'

const ChatView = () => {
  const { user } = useAuth()
  const {
    currentSessionId,
    messages,
    uploadedFiles,
    loadSessions,
    loadMessages,
    selectSession,
    newSession,
    isStreaming,
  } = useChat()

  useEffect(() => {
    loadSessions()
  }, []) // Only run on mount

  useEffect(() => {
    if (!currentSessionId) {
      // Create a new session if none exists
      newSession('New Chat')
    }
  }, [currentSessionId, newSession])

  // Load messages when current session changes (but not for newly created sessions)
  useEffect(() => {
    if (currentSessionId && !messages[currentSessionId]) {
      loadMessages(currentSessionId)
    }
  }, [currentSessionId, loadMessages, messages])

  if (!currentSessionId) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent"></div>
      </div>
    )
  }

  const sessionMessages = messages[currentSessionId] || []
  const sessionFiles = uploadedFiles[currentSessionId] || []

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      {/* Chat Window */}
      <div className="flex-1 overflow-y-auto">
        <ChatWindow messages={sessionMessages} />
      </div>

      {/* File Upload */}
      <div className="px-4 py-2 border-t border-border bg-bg-primary">
        <FileUploader sessionId={currentSessionId} files={sessionFiles} />
      </div>

      {/* Chat Input */}
      <div className="px-4 pb-4 bg-bg-primary">
        <ChatInput sessionId={currentSessionId} disabled={isStreaming || !user?.has_api_key} />
      </div>
    </div>
  )
}

export default ChatView
