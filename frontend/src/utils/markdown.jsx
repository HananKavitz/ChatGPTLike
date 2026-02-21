import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

// Custom components for markdown rendering
const CodeBlock = ({ className, children, ...props }) => {
  const match = /language-(\w+)/.exec(className || '')
  const language = match ? match[1] : ''

  if (match) {
    return (
      <SyntaxHighlighter
        style={vscDarkPlus}
        language={language}
        PreTag="div"
        {...props}
      >
        {String(children).replace(/\n$/, '')}
      </SyntaxHighlighter>
    )
  }

  return (
    <code className={className} {...props}>
      {children}
    </code>
  )
}

const Paragraph = ({ children }) => {
  // Check if paragraph contains a chart
  const text = String(children)
  if (text.includes('```chart') || text.includes('CHART_CONFIG')) {
    return null // Charts are handled separately
  }
  return <p>{children}</p>
}

const MarkdownRenderer = ({ content }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code: CodeBlock,
        p: Paragraph,
        a: ({ node, ...props }) => (
          <a
            {...props}
            target="_blank"
            rel="noopener noreferrer"
            className="text-accent hover:underline"
          />
        ),
        table: ({ node, ...props }) => (
          <div className="overflow-x-auto my-2">
            <table
              className="min-w-full border border-border"
              {...props}
            />
          </div>
        ),
        th: ({ node, ...props }) => (
          <th
            className="px-4 py-2 text-left border-b border-border bg-bg-secondary"
            {...props}
          />
        ),
        td: ({ node, ...props }) => (
          <td
            className="px-4 py-2 border-b border-border"
            {...props}
          />
        ),
        ul: ({ node, ...props }) => (
          <ul className="list-disc list-inside my-2" {...props} />
        ),
        ol: ({ node, ...props }) => (
          <ol className="list-decimal list-inside my-2" {...props} />
        ),
        li: ({ node, ...props }) => (
          <li className="my-1" {...props} />
        ),
        blockquote: ({ node, ...props }) => (
          <blockquote
            className="border-l-4 border-accent pl-4 my-2 text-text-secondary italic"
            {...props}
          />
        ),
        h1: ({ node, ...props }) => (
          <h1 className="text-2xl font-bold mt-4 mb-2" {...props} />
        ),
        h2: ({ node, ...props }) => (
          <h2 className="text-xl font-bold mt-3 mb-2" {...props} />
        ),
        h3: ({ node, ...props }) => (
          <h3 className="text-lg font-bold mt-2 mb-1" {...props} />
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  )
}

export default MarkdownRenderer
