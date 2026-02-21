import { useState } from 'react'
import MarkdownRenderer from '../../utils/markdown.jsx'
import ChartView from '../Chart/ChartView'
import { User, Bot, Copy, Edit2, RotateCcw, Check, X } from 'lucide-react'
import { useChat } from '../../hooks/useChat'
import { cn } from '../../utils/cn'
import MessageActions from './MessageActions'

const ChatMessage = ({ message, isStreaming = false }) => {
  const { regenerateMessage } = useChat()
  const [copied, setCopied] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editContent, setEditContent] = useState(message.content)
  const [showActions, setShowActions] = useState(false)

  const isUser = message.role === 'user'

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleEdit = () => {
    setIsEditing(true)
    setEditContent(message.content)
  }

  const handleSaveEdit = () => {
    // TODO: Implement edit functionality
    setIsEditing(false)
  }

  const handleCancelEdit = () => {
    setIsEditing(false)
    setEditContent(message.content)
  }

  const handleRegenerate = () => {
    regenerateMessage(message.id)
  }

  return (
    <div
      className={cn(
        'py-6 px-4 group',
        isUser ? 'bg-bg-primary' : 'bg-bg-ai-msg'
      )}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <div className="max-w-3xl mx-auto flex gap-4">
        {/* Avatar */}
        <div
          className={cn(
            'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
            isUser ? 'bg-gradient-to-br from-purple-500 to-pink-500' : 'bg-accent'
          )}
        >
          {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {isEditing && isUser ? (
            <div className="space-y-2">
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                className="w-full px-3 py-2 bg-bg-input border border-border rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-accent resize-none"
                rows={3}
              />
              <div className="flex gap-2">
                <button
                  onClick={handleSaveEdit}
                  className="px-3 py-1 bg-accent hover:bg-accent/90 text-white rounded text-sm"
                >
                  Save
                </button>
                <button
                  onClick={handleCancelEdit}
                  className="px-3 py-1 bg-bg-input hover:bg-bg-hover text-text-primary rounded text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="prose prose-invert max-w-none">
              <MarkdownRenderer content={message.content} />
              {message.visualizations && message.visualizations.length > 0 && (
                <div className="mt-4 space-y-4">
                  {message.visualizations.map((viz) => (
                    <ChartView key={viz.id} visualization={viz} />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Actions */}
          {showActions && !isStreaming && (
            <MessageActions
              isUser={isUser}
              copied={copied}
              onCopy={handleCopy}
              onEdit={handleEdit}
              onRegenerate={handleRegenerate}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default ChatMessage
