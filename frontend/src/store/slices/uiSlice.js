import { createSlice } from '@reduxjs/toolkit'

const uiSlice = createSlice({
  name: 'ui',
  initialState: {
    isLoading: false,
    isStreaming: false,
    error: null,
    sidebarOpen: true,
  },
  reducers: {
    setLoading: (state, action) => {
      state.isLoading = action.payload
    },
    setStreaming: (state, action) => {
      state.isStreaming = action.payload
    },
    setError: (state, action) => {
      state.error = action.payload
    },
    clearError: (state) => {
      state.error = null
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen
    },
    setSidebarOpen: (state, action) => {
      state.sidebarOpen = action.payload
    },
  },
})

export const {
  setLoading,
  setStreaming,
  setError,
  clearError,
  toggleSidebar,
  setSidebarOpen,
} = uiSlice.actions

export default uiSlice.reducer
