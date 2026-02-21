import { Outlet } from 'react-router-dom'
import SessionSidebar from '../Session/SessionSidebar'
import ChatView from '../Chat/ChatView'
import { useAuth } from '../../hooks/useAuth'
import { Settings, LogOut } from 'lucide-react'
import { useState } from 'react'

const ChatLayout = () => {
  const { user, handleLogout, requireAuth } = useAuth()
  const [showSettings, setShowSettings] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  requireAuth()

  if (!user) return null

  return (
    <div className="flex h-screen bg-bg-primary">
      {/* Sidebar */}
      {sidebarOpen && (
        <aside className="w-64 bg-bg-secondary flex flex-col border-r border-border flex-shrink-0">
          {/* New Chat Button */}
          <div className="p-3">
            <button
              onClick={() => window.location.reload()}
              className="w-full flex items-center gap-3 px-3 py-3 bg-bg-input hover:bg-bg-hover rounded-lg border border-border text-text-primary transition-colors"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>New chat</span>
            </button>
          </div>

          {/* Session List */}
          <div className="flex-1 overflow-y-auto px-2">
            <SessionSidebar />
          </div>

          {/* User Menu */}
          <div className="p-3 border-t border-border">
            <button
              onClick={() => setShowSettings(true)}
              className="w-full flex items-center gap-3 px-3 py-3 hover:bg-bg-hover rounded-lg text-text-primary transition-colors"
            >
              <Settings size={20} />
              <span className="text-sm">Settings</span>
            </button>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-3 py-3 hover:bg-bg-hover rounded-lg text-text-primary transition-colors"
            >
              <LogOut size={20} />
              <span className="text-sm">Log out</span>
            </button>
          </div>
        </aside>
      )}

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-border bg-bg-primary">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-bg-hover rounded-lg text-text-primary"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </header>

        {/* Content */}
        <Outlet />
      </main>
    </div>
  )
}

export default ChatLayout
