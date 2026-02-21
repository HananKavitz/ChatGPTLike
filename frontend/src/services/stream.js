/**
 * Parse Server-Sent Events (SSE) stream
 * @param {Response} response - Fetch response
 * @param {Function} onChunk - Callback for each chunk
 * @returns {Promise<void>}
 */
export async function parseStream(response, onChunk) {
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()

    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6)

        if (data === '[DONE]') {
          continue
        }

        try {
          const parsed = JSON.parse(data)
          onChunk(parsed)

          if (parsed.done) {
            return
          }
        } catch (e) {
          console.error('Failed to parse SSE data:', data, e)
        }
      }
    }
  }
}

/**
 * Send a streaming message
 * @param {number} sessionId - Session ID
 * @param {string} content - Message content
 * @param {Function} onChunk - Callback for each chunk
 * @returns {Promise<void>}
 */
export async function sendStreamingMessage(sessionId, content, onChunk) {
  const token = localStorage.getItem('token')
  const response = await fetch(`/api/chat/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ content, stream: true }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to send message')
  }

  await parseStream(response, onChunk)
}

/**
 * Regenerate a message with streaming
 * @param {number} messageId - Message ID
 * @param {Function} onChunk - Callback for each chunk
 * @returns {Promise<void>}
 */
export async function regenerateStreamingMessage(messageId, onChunk) {
  const token = localStorage.getItem('token')
  const response = await fetch(`/api/chat/messages/${messageId}/regenerate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to regenerate message')
  }

  await parseStream(response, onChunk)
}
