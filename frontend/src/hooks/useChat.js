import { useDispatch, useSelector } from 'react-redux'
import { useCallback } from 'react'
import {
  fetchSessions,
  createSession,
  updateSession,
  deleteSession,
  fetchMessages,
  fetchFiles,
  setCurrentSession,
  addMessage,
  setStreamingMessage,
  clearStreamingMessage,
} from '../store/slices/chatSlice'
import { setLoading, setStreaming } from '../store/slices/uiSlice'
import { sendStreamingMessage, regenerateStreamingMessage } from '../services/stream'

export const useChat = () => {
  const dispatch = useDispatch()
  const {
    sessions,
    currentSessionId,
    messages,
    uploadedFiles,
    loading,
    error,
  } = useSelector((state) => state.chat)

  const { streaming: isStreaming } = useSelector((state) => state.ui)

  const loadSessions = useCallback(() => {
    dispatch(fetchSessions())
  }, [dispatch])

  const newSession = useCallback(async (name = null) => {
    const result = await dispatch(createSession(name))
    return result.payload
  }, [dispatch])

  const renameSession = useCallback(async (sessionId, name) => {
    await dispatch(updateSession({ sessionId, name }))
  }, [dispatch])

  const removeSession = useCallback(async (sessionId) => {
    await dispatch(deleteSession(sessionId))
  }, [dispatch])

  const selectSession = useCallback(async (sessionId) => {
    dispatch(setCurrentSession(sessionId))
    if (sessionId && !messages[sessionId]) {
      await dispatch(fetchMessages(sessionId))
      await dispatch(fetchFiles(sessionId))
    }
  }, [dispatch, messages])

  const loadMessages = useCallback(async (sessionId) => {
    if (sessionId) {
      await dispatch(fetchMessages(sessionId))
    }
  }, [dispatch])

  const loadFiles = useCallback(async (sessionId) => {
    if (sessionId) {
      await dispatch(fetchFiles(sessionId))
    }
  }, [dispatch])

  const sendMessage = useCallback(async (sessionId, content) => {
    if (!sessionId || !content.trim()) return

    dispatch(setLoading(true))
    dispatch(setStreaming(true))

    // Add user message
    dispatch(
      addMessage({
        sessionId,
        message: {
          id: Date.now(),
          role: 'user',
          content,
          is_edited: false,
          created_at: new Date().toISOString(),
        },
      })
    )

    // Create placeholder for assistant message
    const assistantMessageId = Date.now() + 1
    dispatch(
      addMessage({
        sessionId,
        message: {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
          is_edited: false,
          created_at: new Date().toISOString(),
        },
      })
    )

    let assistantContent = ''

    try {
      await sendStreamingMessage(sessionId, content, (chunk) => {
        if (chunk.error) {
          throw new Error(chunk.error)
        }

        if (chunk.content) {
          assistantContent += chunk.content
          dispatch(setStreamingMessage(assistantContent))
        }
      })
    } catch (error) {
      console.error('Failed to send message:', error)
      throw error
    } finally {
      dispatch(setStreaming(false))
      dispatch(setLoading(false))

      // Update the assistant message with final content
      dispatch(
        addMessage({
          sessionId,
          message: {
            id: Date.now() + 2,
            role: 'assistant',
            content: assistantContent,
            is_edited: false,
            created_at: new Date().toISOString(),
          },
        })
      )

      dispatch(clearStreamingMessage())
    }
  }, [dispatch, currentSessionId])

  const regenerateMessage = useCallback(async (messageId) => {
    if (!currentSessionId) return

    dispatch(setStreaming(true))

    // Find the session that contains this message
    const sessionMessages = messages[currentSessionId] || []
    const messageIndex = sessionMessages.findIndex((m) => m.id === messageId)

    // Only assistant messages can be regenerated
    if (messageIndex === -1 || sessionMessages[messageIndex].role !== 'assistant') {
      return
    }

    // Remove all messages after the target message
    const messagesToKeep = sessionMessages.slice(0, messageIndex)
    messages[currentSessionId] = messagesToKeep

    let assistantContent = ''

    try {
      await regenerateStreamingMessage(messageId, (chunk) => {
        if (chunk.error) {
          throw new Error(chunk.error)
        }

        if (chunk.content) {
          assistantContent += chunk.content
          dispatch(setStreamingMessage(assistantContent))
        }
      })
    } catch (error) {
      console.error('Failed to regenerate message:', error)
      throw error
    } finally {
      dispatch(setStreaming(false))

      // Add the regenerated message
      dispatch(
        addMessage({
          sessionId: currentSessionId,
          message: {
            id: Date.now(),
            role: 'assistant',
            content: assistantContent,
            is_edited: false,
            created_at: new Date().toISOString(),
          },
        })
      )

      dispatch(clearStreamingMessage())
    }
  }, [dispatch, currentSessionId, messages])

  return {
    sessions,
    currentSessionId,
    messages,
    uploadedFiles,
    loading,
    error,
    isStreaming,
    loadSessions,
    newSession,
    renameSession,
    removeSession,
    selectSession,
    loadMessages,
    loadFiles,
    sendMessage,
    regenerateMessage,
  }
}

export default useChat
