import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

// Async thunks
export const register = createAsyncThunk(
  'auth/register',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const response = await api.post('/auth/register', { email, password })
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Registration failed')
    }
  }
)

export const login = createAsyncThunk(
  'auth/login',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const response = await api.post('/auth/login', { email, password })
      localStorage.setItem('token', response.data.access_token)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Login failed')
    }
  }
)

export const getMe = createAsyncThunk(
  'auth/getMe',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/auth/me')
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to get user info')
    }
  }
)

export const updateMe = createAsyncThunk(
  'auth/updateMe',
  async (userData, { rejectWithValue }) => {
    try {
      const response = await api.put('/auth/me', userData)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update user')
    }
  }
)

export const logout = createAsyncThunk(
  'auth/logout',
  async () => {
    localStorage.removeItem('token')
    return null
  }
)

// Slice
const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: !!localStorage.getItem('token'),
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // Register
      .addCase(register.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false
        state.token = action.payload.access_token
        state.isAuthenticated = true
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      // Get Me
      .addCase(getMe.pending, (state) => {
        state.loading = true
      })
      .addCase(getMe.fulfilled, (state, action) => {
        state.loading = false
        // Merge the response with existing user data, preserving existing fields that aren't in response
        if (state.user) {
          state.user = {
            ...state.user,
            ...action.payload
          }
        } else {
          state.user = action.payload
        }
        state.isAuthenticated = true
      })
      .addCase(getMe.rejected, (state) => {
        state.loading = false
        state.isAuthenticated = false
        state.user = null
        state.token = null
        localStorage.removeItem('token')
      })
      // Update Me
      .addCase(updateMe.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(updateMe.fulfilled, (state, action) => {
        state.loading = false
        // Merge the response with existing user data, preserving openai_api_key from request
        if (state.user) {
          state.user = {
            ...state.user,
            ...action.payload,
            // Preserve the openai_api_key from the request since backend doesn't return it
            ...(action.meta.arg?.openai_api_key ? { openai_api_key: action.meta.arg.openai_api_key } : {})
          }
        } else {
          state.user = {
            ...action.payload,
            ...(action.meta.arg?.openai_api_key ? { openai_api_key: action.meta.arg.openai_api_key } : {})
          }
        }
      })
      .addCase(updateMe.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.user = null
        state.token = null
        state.isAuthenticated = false
      })
  },
})

export const { clearError } = authSlice.actions
export default authSlice.reducer
