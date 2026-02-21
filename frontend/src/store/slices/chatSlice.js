import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

// Async thunks
export const fetchSessions = createAsyncThunk(
  'chat/fetchSessions',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/chat/sessions')
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch sessions')
    }
  }
)

export const createSession = createAsyncThunk(
  'chat/createSession',
  async (name, { rejectWithValue }) => {
    try {
      const response = await api.post('/chat/sessions', { name })
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create session')
    }
  }
)

export const updateSession = createAsyncThunk(
  'chat/updateSession',
  async ({ sessionId, name }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/chat/sessions/${sessionId}`, { name })
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update session')
    }
  }
)

export const deleteSession = createAsyncThunk(
  'chat/deleteSession',
  async (sessionId, { rejectWithValue }) => {
    try {
      await api.delete(`/chat/sessions/${sessionId}`)
      return sessionId
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete session')
    }
  }
)

export const fetchMessages = createAsyncThunk(
  'chat/fetchMessages',
  async (sessionId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/chat/sessions/${sessionId}`)
      return { sessionId, data: response.data }
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch messages')
    }
  }
)

export const fetchFiles = createAsyncThunk(
  'chat/fetchFiles',
  async (sessionId, { rejectWithValue }) => {
    try {
      const response = await api.get(`/files/sessions/${sessionId}/files`)
      return { sessionId, files: response.data }
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch files')
    }
  }
)

// Slice
const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    sessions: [],
    currentSessionId: null,
    messages: {}, // { sessionId: [messages] }
    uploadedFiles: {}, // { sessionId: [files] }
    loading: false,
    error: null,
  },
  reducers: {
    setCurrentSession: (state, action) => {
      state.currentSessionId = action.payload
    },
    clearCurrentSession: (state) => {
      state.currentSessionId = null
    },
    addMessage: (state, action) => {
      const { sessionId, message } = action.payload
      if (!state.messages[sessionId]) {
        state.messages[sessionId] = []
      }
      state.messages[sessionId].push(message)
    },
    updateMessage: (state, action) => {
      const { sessionId, messageId, content } = action.payload
      const messages = state.messages[sessionId]
      if (messages) {
        const message = messages.find(m => m.id === messageId)
        if (message) {
          message.content = content
          message.is_edited = true
        }
      }
    },
    setStreamingMessage: (state, action) => {
      const { sessionId, content } = action.payload
      state.streamingMessage = content
    },
    clearStreamingMessage: (state) => {
      state.streamingMessage = null
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Sessions
      .addCase(fetchSessions.pending, (state) => {
        state.loading = true
      })
      .addCase(fetchSessions.fulfilled, (state, action) => {
        state.loading = false
        state.sessions = action.payload
      })
      .addCase(fetchSessions.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      // Create Session
      .addCase(createSession.fulfilled, (state, action) => {
        state.sessions.unshift(action.payload)
        state.currentSessionId = action.payload.id
        state.messages[action.payload.id] = []
      })
      // Update Session
      .addCase(updateSession.fulfilled, (state, action) => {
        const index = state.sessions.findIndex(s => s.id === action.payload.id)
        if (index !== -1) {
          state.sessions[index] = action.payload
        }
      })
      // Delete Session
      .addCase(deleteSession.pending, (state) => {
        state.loading = true
      })
      .addCase(deleteSession.fulfilled, (state, action) => {
        state.loading = false
        state.sessions = state.sessions.filter(s => s.id !== action.payload)
        if (state.currentSessionId === action.payload) {
          state.currentSessionId = null
        }
        delete state.messages[action.payload]
        delete state.uploadedFiles[action.payload]
      })
      .addCase(deleteSession.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      // Fetch Messages
      .addCase(fetchMessages.fulfilled, (state, action) => {
        const { sessionId, data } = action.payload
        state.messages[sessionId] = data.messages || []
      })
      // Fetch Files
      .addCase(fetchFiles.fulfilled, (state, action) => {
        const { sessionId, files } = action.payload
        state.uploadedFiles[sessionId] = files
      })
  },
})

export const {
  setCurrentSession,
  clearCurrentSession,
  addMessage,
  updateMessage,
  setStreamingMessage,
  clearStreamingMessage,
  clearError,
} = chatSlice.actions

export default chatSlice.reducer
