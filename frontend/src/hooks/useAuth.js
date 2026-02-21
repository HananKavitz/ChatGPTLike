import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, useLocation } from 'react-router-dom'
import { getMe, logout } from '../store/slices/authSlice'

export const useAuth = () => {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const location = useLocation()

  const { user, token, isAuthenticated, loading, error } = useSelector(
    (state) => state.auth
  )

  useEffect(() => {
    // Check if we have a token but no user data
    if (token && !user && !loading) {
      dispatch(getMe())
    }
  }, [token, user, loading, dispatch])

  const handleLogout = async () => {
    await dispatch(logout())
    navigate('/login')
  }

  const requireAuth = () => {
    if (!isAuthenticated && !loading) {
      // Redirect to login with return URL
      navigate('/login', { state: { from: location } })
      return false
    }
    return true
  }

  return {
    user,
    token,
    isAuthenticated,
    loading,
    error,
    handleLogout,
    requireAuth,
  }
}

export default useAuth
