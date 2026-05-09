import { useState, useRef, useEffect } from 'react'
import { renderMarkdown } from '@a2ui/markdown-it'
import { MarkdownContext } from '@a2ui/react/v0_9'
import { useChat } from './hooks/useChat'
import Header from './components/Header'
import Welcome from './components/Welcome'
import Footer from './components/Footer'
import DebugPanel from './components/DebugPanel'
import A2UISurfaceMessage from './components/A2UISurfaceMessage'

export default function App() {
  const { messages, isLoading, showWelcome, debugMessages, sendText, sendAction } = useChat()
  const [debugOpen, setDebugOpen] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <MarkdownContext.Provider value={renderMarkdown}>
      <div id="app">
        <Header />
        <main id="chat-area">
          {showWelcome && <Welcome onSuggestionClick={sendText} />}
          <div id="chat-flow">
            {messages.map(msg => {
              if (msg.type === 'user') {
                return <div key={msg.id} className="user-message">{msg.text}</div>
              }
              if (msg.type === 'agent-a2ui' && msg.a2uiMessages) {
                return <A2UISurfaceMessage key={msg.id} messages={msg.a2uiMessages} onAction={sendAction} />
              }
              if (msg.type === 'error') {
                return <div key={msg.id} className="agent-message error-message">{msg.text}</div>
              }
              return <div key={msg.id} className="agent-message text-message">{msg.text}</div>
            })}
            {isLoading && (
              <div className="loading">
                <span className="dots"><span>.</span><span>.</span><span>.</span></span>
                {' '}Thinking...
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
        </main>
        <Footer onSubmit={sendText} isLoading={isLoading} />
      </div>

      <div className="debug-toggle" onClick={() => setDebugOpen(!debugOpen)}>
        <span className="material-icons">code</span> A2UI JSON
      </div>
      <DebugPanel open={debugOpen} onClose={() => setDebugOpen(false)} messages={debugMessages} />
    </MarkdownContext.Provider>
  )
}
