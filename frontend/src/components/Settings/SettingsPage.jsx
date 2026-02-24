import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { updateMe } from '../../store/slices/authSlice'
import { Eye, EyeOff, Save, Key, Building2, Lock, CheckCircle, XCircle, Loader2 } from 'lucide-react'

const SettingsPage = () => {
  const dispatch = useDispatch()
  const { user, loading } = useSelector((state) => state.auth)

  const [llmProvider, setLlmProvider] = useState(user?.llm_provider || 'openai')

  // OpenAI settings
  const [openaiApiKey, setOpenaiApiKey] = useState('')
  const [showOpenaiApiKey, setShowOpenaiApiKey] = useState(false)
  const [openaiModel, setOpenaiModel] = useState(user?.openai_model || 'gpt-4')
  const [openaiKeyStatus, setOpenaiKeyStatus] = useState(null)

  // Anthropic settings
  const [anthropicApiKey, setAnthropicApiKey] = useState('')
  const [showAnthropicApiKey, setShowAnthropicApiKey] = useState(false)
  const [anthropicModel, setAnthropicModel] = useState(user?.anthropic_model || 'claude-opus-4-6')
  const [anthropicKeyStatus, setAnthropicKeyStatus] = useState(null)

  // OpenRouter settings
  const [openrouterApiKey, setOpenrouterApiKey] = useState('')
  const [showOpenrouterApiKey, setShowOpenrouterApiKey] = useState(false)
  const [openrouterModel, setOpenrouterModel] = useState(user?.openrouter_model || 'anthropic/claude-3.5-sonnet-20241022')
  const [openrouterKeyStatus, setOpenrouterKeyStatus] = useState(null)

  // General
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [message, setMessage] = useState(null)
  const [verifyingKey, setVerifyingKey] = useState(false)

  const handleApiKeyKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      // Don't submit form on Enter in API key field
    }
  }

  const verifyApiKey = async (provider) => {
    const apiKey = provider === 'openai' ? openaiApiKey : provider === 'anthropic' ? anthropicApiKey : openrouterApiKey
    if (!apiKey || apiKey === '••••••••••••••••') {
      setMessage({ type: 'error', text: `Please enter a ${provider === 'openai' ? 'OpenAI' : provider === 'anthropic' ? 'Anthropic' : 'OpenRouter'} API key to verify` })
      return
    }

    setVerifyingKey(true)
    if (provider === 'openai') {
      setOpenaiKeyStatus(null)
    } else {
      setAnthropicKeyStatus(null)
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/auth/verify-api-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          api_key: apiKey,
          provider: provider
        })
      })

      const data = await response.json()

      if (data.valid) {
        if (provider === 'openai') {
          setOpenaiKeyStatus('valid')
        } else if (provider === 'anthropic') {
          setAnthropicKeyStatus('valid')
        } else {
          setOpenrouterKeyStatus('valid')
        }
        setMessage({ type: 'success', text: data.message })
      } else {
        if (provider === 'openai') {
          setOpenaiKeyStatus('invalid')
        } else if (provider === 'anthropic') {
          setAnthropicKeyStatus('invalid')
        } else {
          setOpenrouterKeyStatus('invalid')
        }
        setMessage({ type: 'error', text: data.message })
      }
    } catch (error) {
      if (provider === 'openai') {
        setOpenaiKeyStatus('invalid')
      } else if (provider === 'anthropic') {
        setAnthropicKeyStatus('invalid')
      } else {
        setOpenrouterKeyStatus('invalid')
      }
      setMessage({ type: 'error', text: 'Failed to verify API key. Please try again.' })
    } finally {
      setVerifyingKey(false)
    }
  }

  const handleSave = async (e) => {
    e.preventDefault()
    setMessage(null)

    const updates = {}

    // Add provider selection
    updates.llm_provider = llmProvider

    // Add OpenAI settings if provided (and not the placeholder)
    if (openaiApiKey && openaiApiKey !== '••••••••••••••••') {
      updates.openai_api_key = openaiApiKey
    }
    updates.openai_model = openaiModel

    // Add Anthropic settings if provided (and not the placeholder)
    if (anthropicApiKey && anthropicApiKey !== '••••••••••••••••') {
      updates.anthropic_api_key = anthropicApiKey
    }
    updates.anthropic_model = anthropicModel

    // Add OpenRouter settings if provided (and not the placeholder)
    if (openrouterApiKey && openrouterApiKey !== '••••••••••••••••') {
      updates.openrouter_api_key = openrouterApiKey
    }
    updates.openrouter_model = openrouterModel


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

      // Clear password and API key fields
      setPassword('')
      setConfirmPassword('')
      setOpenaiApiKey('')
      setAnthropicApiKey('')
      setOpenrouterApiKey('')
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
          {/* Provider Selection */}
          <div className="p-4 bg-bg-secondary rounded-lg border border-border">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Building2 size={20} className="text-accent" />
              AI Provider
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Select your preferred AI provider
                </label>
                <div className="space-y-2">
                  <label className="flex items-center p-3 border border-border rounded-lg cursor-pointer hover:bg-bg-input transition-colors">
                    <input
                      type="radio"
                      name="provider"
                      value="openai"
                      checked={llmProvider === 'openai'}
                      onChange={(e) => setLlmProvider(e.target.value)}
                      className="mr-3 text-accent"
                    />
                    <div className="flex-1">
                      <span className="font-medium">OpenAI</span>
                      <p className="text-sm text-text-secondary">Use OpenAI's GPT models</p>
                    </div>
                  </label>

                  <label className="flex items-center p-3 border border-border rounded-lg cursor-pointer hover:bg-bg-input transition-colors">
                    <input
                      type="radio"
                      name="provider"
                      value="anthropic"
                      checked={llmProvider === 'anthropic'}
                      onChange={(e) => setLlmProvider(e.target.value)}
                      className="mr-3 text-accent"
                    />
                    <div className="flex-1">
                      <span className="font-medium">Claude (Anthropic)</span>
                      <p className="text-sm text-text-secondary">Use Anthropic's Claude models including Opus 4.6</p>
                    </div>
                  </label>

                  <label className="flex items-center p-3 border border-border rounded-lg cursor-pointer hover:bg-bg-input transition-colors">
                    <input
                      type="radio"
                      name="provider"
                      value="openrouter"
                      checked={llmProvider === 'openrouter'}
                      onChange={(e) => setLlmProvider(e.target.value)}
                      className="mr-3 text-accent"
                    />
                    <div className="flex-1">
                      <span className="font-medium">OpenRouter</span>
                      <p className="text-sm text-text-secondary">Access multiple AI models including Claude, GPT-4, and more</p>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* OpenAI API Key */}
          {llmProvider === 'openai' && (
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
                  id="openaiApiKey"
                  type={showOpenaiApiKey ? 'text' : 'password'}
                  value={user?.openai_api_key && openaiApiKey.length === 0 ? '••••••••••••••••' : openaiApiKey}
                  onChange={(e) => {
                    setOpenaiApiKey(e.target.value)
                    setOpenaiKeyStatus(null) // Reset status when typing
                  }}
                  onKeyDown={handleApiKeyKeyDown}
                  placeholder="sk-..."
                  className="w-full px-4 py-3 pr-28 bg-bg-input border border-border rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent"
                />
                <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => setShowOpenaiApiKey(!showOpenaiApiKey)}
                    className="text-text-secondary hover:text-text-primary p-1"
                  >
                    {showOpenaiApiKey ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                  <button
                    type="button"
                    onClick={() => verifyApiKey('openai')}
                    disabled={verifyingKey || !openaiApiKey || openaiApiKey === '••••••••••••••••'}
                    className="text-text-secondary hover:text-accent disabled:opacity-50 disabled:cursor-not-allowed p-1"
                    title="Verify API Key"
                  >
                    {verifyingKey ? (
                      <Loader2 size={18} className="animate-spin" />
                    ) : openaiKeyStatus === 'valid' ? (
                      <CheckCircle size={18} className="text-green-500" />
                    ) : openaiKeyStatus === 'invalid' ? (
                      <XCircle size={18} className="text-red-500" />
                    ) : (
                      <CheckCircle size={18} />
                    )}
                  </button>
                </div>
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
                . Click the checkmark icon to verify your key before saving.
              </p>
            </div>
          </div>
          )}

          {/* OpenAI Model Selection */}
          {llmProvider === 'openai' && (
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
                id="openaiModel"
                value={openaiModel}
                onChange={(e) => setOpenaiModel(e.target.value)}
                className="w-full px-4 py-3 bg-bg-input border border-border rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-accent"
              >
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo-preview">GPT-4 Turbo</option>
                <option value="gpt-4o">GPT-4o</option>
                <option value="gpt-4o-mini">GPT-4o Mini</option>
              </select>
              <p className="text-xs text-text-secondary">
                Choose the OpenAI model to use for chat responses. GPT-4 provides the best quality but is more expensive.
              </p>
            </div>
          </div>
          )}

          {/* Anthropic API Key */}
          {llmProvider === 'anthropic' && (
          <div className="p-4 bg-bg-secondary rounded-lg border border-border">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Key size={20} className="text-accent" />
              Anthropic API Key
            </h2>
            <div className="space-y-2">
              <label htmlFor="anthropicApiKey" className="block text-sm font-medium text-text-primary">
                API Key
              </label>
              <div className="relative">
                <input
                  id="anthropicApiKey"
                  type={showAnthropicApiKey ? 'text' : 'password'}
                  value={user?.anthropic_api_key && anthropicApiKey.length === 0 ? '••••••••••••••••' : anthropicApiKey}
                  onChange={(e) => {
                    setAnthropicApiKey(e.target.value)
                    setAnthropicKeyStatus(null) // Reset status when typing
                  }}
                  onKeyDown={handleApiKeyKeyDown}
                  placeholder="sk-ant-..."
                  className="w-full px-4 py-3 pr-28 bg-bg-input border border-border rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent"
                />
                <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => setShowAnthropicApiKey(!showAnthropicApiKey)}
                    className="text-text-secondary hover:text-text-primary p-1"
                  >
                    {showAnthropicApiKey ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                  <button
                    type="button"
                    onClick={() => verifyApiKey('anthropic')}
                    disabled={verifyingKey || !anthropicApiKey || anthropicApiKey === '••••••••••••••••'}
                    className="text-text-secondary hover:text-accent disabled:opacity-50 disabled:cursor-not-allowed p-1"
                    title="Verify API Key"
                  >
                    {verifyingKey ? (
                      <Loader2 size={18} className="animate-spin" />
                    ) : anthropicKeyStatus === 'valid' ? (
                      <CheckCircle size={18} className="text-green-500" />
                    ) : anthropicKeyStatus === 'invalid' ? (
                      <XCircle size={18} className="text-red-500" />
                    ) : (
                      <CheckCircle size={18} />
                    )}
                  </button>
                </div>
              </div>
              <p className="text-xs text-text-secondary">
                Your API key is stored securely and used to make requests to Anthropic. Get your key from{' '}
                <a
                  href="https://console.anthropic.com/account/keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent hover:underline"
                >
                  Anthropic Console
                </a>
                . Click the checkmark icon to verify your key before saving.
              </p>
            </div>
          </div>
          )}

          {/* Anthropic Model Selection */}
          {llmProvider === 'anthropic' && (
            <div className="p-4 bg-bg-secondary rounded-lg border border-border">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Building2 size={20} className="text-accent" />
                Model
              </h2>
              <div className="space-y-2">
                <label htmlFor="anthropicModel" className="block text-sm font-medium text-text-primary">
                  Default Model
                </label>
                <select
                  id="anthropicModel"
                  value={anthropicModel}
                  onChange={(e) => setAnthropicModel(e.target.value)}
                  className="w-full px-4 py-3 bg-bg-input border border-border rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-accent"
                >
                  <option value="claude-opus-4-6">Claude Opus 4.6</option>
                  <option value="claude-sonnet-4-6">Claude Sonnet 4.6</option>
                  <option value="claude-haiku-4-5">Claude Haiku 4.5</option>
                  <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                  <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                  <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
                </select>
                <p className="text-xs text-text-secondary">
                  Choose the Claude model to use for chat responses. Opus provides the best quality, Sonnet balances quality and speed, and Haiku is fastest.
                </p>
              </div>
            </div>
          )}

          {/* OpenRouter API Key */}
          {llmProvider === 'openrouter' && (
          <div className="p-4 bg-bg-secondary rounded-lg border border-border">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Key size={20} className="text-accent" />
              OpenRouter API Key
            </h2>
            <div className="space-y-2">
              <label htmlFor="openrouterApiKey" className="block text-sm font-medium text-text-primary">
                API Key
              </label>
              <div className="relative">
                <input
                  id="openrouterApiKey"
                  type={showOpenrouterApiKey ? 'text' : 'password'}
                  value={user?.openrouter_api_key && openrouterApiKey.length === 0 ? '••••••••••••••••••••' : openrouterApiKey}
                  onChange={(e) => {
                    setOpenrouterApiKey(e.target.value)
                    setOpenrouterKeyStatus(null) // Reset status when typing
                  }}
                  onKeyDown={handleApiKeyKeyDown}
                  placeholder="sk-or-..."
                  className="w-full px-4 py-3 pr-28 bg-bg-input border border-border rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-accent"
                />
                <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => setShowOpenrouterApiKey(!showOpenrouterApiKey)}
                    className="text-text-secondary hover:text-text-primary p-1"
                  >
                    {showOpenrouterApiKey ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                  <button
                    type="button"
                    onClick={() => verifyApiKey('openrouter')}
                    disabled={verifyingKey || !openrouterApiKey || openrouterApiKey === '••••••••••••••••••••'}
                    className="text-text-secondary hover:text-accent disabled:opacity-50 disabled:cursor-not-allowed p-1"
                    title="Verify API Key"
                  >
                    {verifyingKey ? (
                      <Loader2 size={18} className="animate-spin" />
                    ) : openrouterKeyStatus === 'valid' ? (
                      <CheckCircle size={18} className="text-green-500" />
                    ) : openrouterKeyStatus === 'invalid' ? (
                      <XCircle size={18} className="text-red-500" />
                    ) : (
                      <CheckCircle size={18} />
                    )}
                  </button>
                </div>
              </div>
              <p className="text-xs text-text-secondary">
                Your API key is stored securely and used to make requests to OpenRouter. Get your key from{' '}
                <a
                  href="https://openrouter.ai/keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent hover:underline"
                >
                  OpenRouter
                </a>
                . Click the checkmark icon to verify your key before saving.
              </p>
            </div>
          </div>
          )}

          {/* OpenRouter Model Selection */}
          {llmProvider === 'openrouter' && (
            <div className="p-4 bg-bg-secondary rounded-lg border border-border">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Building2 size={20} className="text-accent" />
                Model
              </h2>
              <div className="space-y-2">
                <label htmlFor="openrouterModel" className="block text-sm font-medium text-text-primary">
                  Default Model
                </label>
                <select
                  id="openrouterModel"
                  value={openrouterModel}
                  onChange={(e) => setOpenrouterModel(e.target.value)}
                  className="w-full px-4 py-3 bg-bg-input border border-border rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-accent"
                >
                  <option value="anthropic/claude-opus-4-20250219">Claude Opus 4.6</option>
                  <option value="anthropic/claude-3.5-sonnet-20241022">Claude 3.5 Sonnet</option>
                  <option value="anthropic/claude-3-haiku-20240307">Claude 3 Haiku</option>
                  <option value="openai/gpt-4o">GPT-4o</option>
                  <option value="openai/gpt-4-turbo-preview">GPT-4 Turbo</option>
                  <option value="google/gemini-pro-1.5">gemini Pro 1.5</option>
                  <option value="meta-llama/llama-3.1-405b-instruct">llama 3.1 405B</option>
                  <option value="databricks/dbrx-instruct">dbrx</option>
                </select>
                <p className="text-xs text-text-secondary">
                  Choose the model to use for chat responses. OpenRouter provides access to models from multiple providers.
                </p>
              </div>
            </div>
          )}

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
