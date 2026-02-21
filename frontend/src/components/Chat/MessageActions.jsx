import { Copy, Edit2, RotateCcw } from 'lucide-react'

const MessageActions = ({ isUser, copied, onCopy, onEdit, onRegenerate }) => {
  return (
    <div className="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
      <button
        onClick={onCopy}
        className="p-1.5 hover:bg-bg-hover rounded text-text-secondary hover:text-text-primary transition-colors"
        title={copied ? 'Copied!' : 'Copy'}
      >
        <Copy size={16} />
      </button>

      {isUser && (
        <button
          onClick={onEdit}
          className="p-1.5 hover:bg-bg-hover rounded text-text-secondary hover:text-text-primary transition-colors"
          title="Edit"
        >
          <Edit2 size={16} />
        </button>
      )}

      {!isUser && (
        <button
          onClick={onRegenerate}
          className="p-1.5 hover:bg-bg-hover rounded text-text-secondary hover:text-text-primary transition-colors"
          title="Regenerate"
        >
          <RotateCcw size={16} />
        </button>
      )}
    </div>
  )
}

export default MessageActions
