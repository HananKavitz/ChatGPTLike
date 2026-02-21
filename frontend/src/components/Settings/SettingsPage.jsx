import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { updateMe } from '../../store/slices/authSlice'
import { Eye, EyeOff, Save, Key, Building2, Lock } from 'lucide-react'

const SettingsPage = () => {
  const dispatch = useDispatch()
  const { user, loading } = useSelector((state) => state.auth)

  const [apiKey, setApiKey] = useState('')
  const [showApiKey, setShowApiKey] = useState(false)
  const [model, setModel] = useState(user?.openai_model || 'gpt-4')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [message, setMessage] = useState(null)

  const handleSave = async (e) => {
    e.preventDefault()
    setMessage(null)

    const updates = {}

    if (apiKey && apiKey !== '••••••••••••••••') {
      updates.openai_api_key = apiKey
    }

    if (model !== user?.openai_model) {
      updates.openai_model = model
    }

    if (password) {
      if (password !== confirmPassword) {
        setMessage({ type: 'error', text: 'Passwords do not match' })
        return
      }
      if (password.length < 6) {
        setMessage({ type: 'error', text: 'Password must be at least 6 characters' })
        return
      }
      updates.password = password
    }

    if (Object.keys(updates).length === 0) {
      setMessage({ type: 'info', text: 'No changes to save' })
      return
    }

    try {
      await dispatch(updateMe(updates)).unwrap()
      setMessage({ type: 'success', text: 'Settings saved successfully' })

      // Clear password fields
      setPassword('')
      setConfirmPassword('')
      setApiKey('')
    } catch (error) {
      setMessage({ type: 'error', text: error || 'Failed to save settings' })
    }
  }

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Settings</h1>

        {/* Message */}
        {message && (
          <div
            className={`mb-4 p-4 rounded-lg ${
              message.type === 'success'
                ? 'bg-green-900/20 border border-green-500 text-green-400'
                : message.type === 'error'
                ? 'bg-red-900/20 border border-red-500 text-red-400'
                : 'bg-blue-900/20 border border-blue-500 text-blue-400'
            }`}
          >
            {message.text}
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          {/* OpenAI API Key */}
          <div className="p-4 bg-bg-secondary rounded-lg border border-border">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Key size={20} className="text-accent" />
              OpenAI API Key
            </h2>
            <div className="space-y-2">
              <label htmlFor="apiKey" className="block text-sm font-medium text-text-primary">
                API Key
              </label>
              <div className="relative">
                <input
                  id="apiKey"
                  type={showApiKey ? 'text' : 'password'}
                  value={user?.openai_api_key ? (apiKey || '••••••••••••••••') : ''}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full px-4 py-3 pr-12 bg-bg-input border border-border rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent"
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary hover:text-text-primary"
                >
                  {showApiKey ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              <p className="text-xs text-text-secondary">
                Your API key is stored securely and used to make requests to OpenAI. Get your key from{' '}
                <a
                  href="https://platform.openai.com/api-keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent hover:underline"
                >
                  OpenAI Platform
                </a>
                .
              </p>
            </div>
          </div>

          {/* Model Selection */}
          <div className="p-4 bg-bg-secondary rounded-lg border border-border">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Building2 size={20} className="text-accent" />
              Model
            </h2>
            <div className="space-y-2">
              <label htmlFor="model" className="block text-sm font-medium text-text-primary">
                Default Model
              </label>
              <select
                id="model"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full px-4 py-3 bg-bg-input border border-border rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-accent"
              >
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              </select>
              <p className="text-xs text-text-secondary">
                Choose the OpenAI model to use for chat responses. GPT-4 provides the best quality but is more expensive.
              </p>
            </div>
          </div>

          {/* Change Password */}
          <div className="p-4 bg-bg-secondary rounded-lg border border-border">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Lock size={20} className="text-accent" />
              Change Password
            </h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-text-primary mb-2">
                  New Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-4 py-3 pr-12 bg-bg-input border border-border rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary hover:text-text-primary"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-text-primary mb-2">
                  Confirm New Password
                </label>
                <div className="relative">
                  <input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-4 py-3 pr-12 bg-bg-input border border-border rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary hover:text-text-primary"
                  >
                    {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <button
            type="submit"
            disabled={loading}
            className="flex items-center justify-center gap-2 w-full px-4 py-3 bg-accent hover:bg-accent/90 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                Saving...
              </>
            ) : (
              <>
                <Save size={20} />
                Save Settings
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

export default SettingsPage
