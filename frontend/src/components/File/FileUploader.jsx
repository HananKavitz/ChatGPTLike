import { useState, useRef } from 'react'
import api from '../../services/api'
import { useChat } from '../../hooks/useChat'
import { Paperclip, X, FileText, Trash2 } from 'lucide-react'
import { cn } from '../../utils/cn'

const FileUploader = ({ sessionId, files }) => {
  const { loadFiles } = useChat()
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleFileUpload(e.dataTransfer.files[0])
    }
  }

  const handleFileInput = async (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      await handleFileUpload(e.target.files[0])
    }
    e.target.value = ''
  }

  const handleFileUpload = async (file) => {
    // Validate file type
    const validTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']
    const validExtensions = ['.xlsx', '.xls']

    const extension = '.' + file.name.split('.').pop().toLowerCase()
    if (!validExtensions.includes(extension)) {
      alert('Please upload an Excel file (.xlsx or .xls)')
      return
    }

    // Validate file size (50MB)
    const maxSize = 50 * 1024 * 1024
    if (file.size > maxSize) {
      alert('File size must be less than 50MB')
      return
    }

    setUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('session_id', sessionId)

      const response = await api.post('/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        params: { session_id: sessionId },
      })

      await loadFiles(sessionId)
    } catch (error) {
      console.error('Failed to upload file:', error)
      alert('Failed to upload file. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteFile = async (fileId) => {
    if (!window.confirm('Delete this file?')) return

    try {
      await api.delete(`/files/${fileId}`)
      await loadFiles(sessionId)
    } catch (error) {
      console.error('Failed to delete file:', error)
      alert('Failed to delete file. Please try again.')
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="space-y-2">
      {/* File list */}
      {files && files.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {files.map((file) => (
            <div
              key={file.id}
              className="flex items-center gap-2 px-3 py-1.5 bg-bg-secondary border border-border rounded-full text-sm text-text-primary"
            >
              <FileText size={14} />
              <span className="max-w-[150px] truncate">{file.original_filename}</span>
              <button
                onClick={() => handleDeleteFile(file.id)}
                className="hover:text-red-400 transition-colors"
              >
                <X size={14} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Upload area */}
      <div
        className={cn(
          'relative flex items-center gap-2 px-3 py-2 rounded-lg border-2 border-dashed transition-colors',
          dragActive
            ? 'border-accent bg-accent/10'
            : 'border-border hover:border-border/80 hover:bg-bg-hover'
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx,.xls"
          onChange={handleFileInput}
          className="hidden"
        />

        {uploading ? (
          <div className="flex items-center gap-2 text-text-secondary text-sm">
            <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-accent"></div>
            <span>Uploading...</span>
          </div>
        ) : (
          <>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center gap-2 px-3 py-1.5 bg-bg-input hover:bg-bg-hover rounded-lg text-text-primary text-sm transition-colors"
            >
              <Paperclip size={16} />
              <span>Attach Excel file</span>
            </button>
            <span className="text-xs text-text-secondary">
              Drag & drop or click to upload (max 50MB)
            </span>
          </>
        )}
      </div>
    </div>
  )
}

export default FileUploader
