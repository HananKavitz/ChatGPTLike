import { useChat } from '../../hooks/useChat'
import SessionItem from './SessionItem'
import { MessageSquare } from 'lucide-react'

const SessionSidebar = () => {
  const { sessions, currentSessionId, selectSession, removeSession, renameSession } = useChat()

  if (sessions.length === 0) {
    return (
      <div className="text-center text-text-secondary text-sm py-4">
        <MessageSquare className="mx-auto mb-2 opacity-50" size={32} />
        <p>No conversations yet</p>
        <p className="text-xs mt-1">Start a new chat to begin</p>
      </div>
    )
  }

  return (
    <div className="space-y-1">
      {sessions.map((session) => (
        <SessionItem
          key={session.id}
          session={session}
          isActive={currentSessionId === session.id}
          onSelect={() => selectSession(session.id)}
          onDelete={() => removeSession(session.id)}
          onRename={(name) => renameSession(session.id, name)}
        />
      ))}
    </div>
  )
}

export default SessionSidebar
