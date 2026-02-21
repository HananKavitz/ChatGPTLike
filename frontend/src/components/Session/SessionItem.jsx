import { useState, useRef, useEffect } from 'react'
import { Trash2, Edit2, Check, X } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { cn } from '../../utils/cn'

const SessionItem = ({ session, isActive, onSelect, onDelete, onRename }) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editName, setEditName] = useState(session.name || 'New Chat')
  const [showMenu, setShowMenu] = useState(false)
  const menuRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    setEditName(session.name || 'New Chat')
  }, [session.name])

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus()
      inputRef.current.select()
    }
  }, [isEditing])

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleStartEdit = (e) => {
    e.stopPropagation()
    setIsEditing(true)
    setShowMenu(false)
  }

  const handleSaveEdit = () => {
    if (editName.trim()) {
      onRename(editName.trim())
    }
    setIsEditing(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSaveEdit()
    } else if (e.key === 'Escape') {
      setIsEditing(false)
      setEditName(session.name || 'New Chat')
    }
  }

  const handleDelete = (e) => {
    e.stopPropagation()
    if (window.confirm('Delete this conversation?')) {
      onDelete()
      setShowMenu(false)
    }
  }

  return (
    <div
      className={cn(
        'group relative flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors',
        isActive
          ? 'bg-bg-hover text-text-primary'
          : 'text-text-secondary hover:bg-bg-hover hover:text-text-primary'
      )}
      onClick={() => !isEditing && onSelect()}
    >
      {isEditing ? (
        <input
          ref={inputRef}
          type="text"
          value={editName}
          onChange={(e) => setEditName(e.target.value)}
          onKeyDown={handleKeyDown}
          onClick={(e) => e.stopPropagation()}
          className="flex-1 px-2 py-1 bg-bg-input border border-border rounded text-sm focus:outline-none focus:ring-1 focus:ring-accent"
        />
      ) : (
        <>
          <span className="flex-1 truncate text-sm">
            {session.name || 'New Chat'}
          </span>

          {/* Date indicator */}
          <span className="text-xs opacity-50">
            {formatDistanceToNow(new Date(session.updated_at), { addSuffix: true })}
          </span>

          {/* Menu button */}
          <button
            onClick={(e) => {
              e.stopPropagation()
              setShowMenu(!showMenu)
            }}
            className="opacity-0 group-hover:opacity-100 p-1 hover:bg-bg-primary rounded transition-all"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="1" />
              <circle cx="12" cy="5" r="1" />
              <circle cx="12" cy="19" r="1" />
            </svg>
          </button>

          {/* Dropdown menu */}
          {showMenu && (
            <div
              ref={menuRef}
              className="absolute right-0 top-full mt-1 w-36 bg-bg-secondary border border-border rounded-lg shadow-lg z-10"
            >
              <button
                onClick={handleStartEdit}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-text-primary hover:bg-bg-hover transition-colors"
              >
                <Edit2 size={14} />
                Rename
              </button>
              <button
                onClick={handleDelete}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-bg-hover transition-colors"
              >
                <Trash2 size={14} />
                Delete
              </button>
            </div>
          )}
        </>
      )}

      {/* Edit buttons */}
      {isEditing && (
        <div className="flex items-center gap-1">
          <button
            onClick={(e) => {
              e.stopPropagation()
              handleSaveEdit()
            }}
            className="p-1 text-green-400 hover:text-green-300"
          >
            <Check size={16} />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              setIsEditing(false)
              setEditName(session.name || 'New Chat')
            }}
            className="p-1 text-red-400 hover:text-red-300"
          >
            <X size={16} />
          </button>
        </div>
      )}
    </div>
  )
}

export default SessionItem
