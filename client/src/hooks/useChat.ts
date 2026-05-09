import { useState, useCallback } from 'react'
import { callAgent, buildTextParts, buildActionParts, type A2UIMessage } from '../api/agent'

export interface ChatMessage {
  id: string
  type: 'user' | 'agent-text' | 'agent-a2ui' | 'error'
  text?: string
  a2uiMessages?: A2UIMessage[]
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showWelcome, setShowWelcome] = useState(true)
  const [debugMessages, setDebugMessages] = useState<A2UIMessage[]>([])

  const addMessage = useCallback((msg: ChatMessage) => {
    setMessages(prev => [...prev, msg])
  }, [])

  const sendText = useCallback(async (text: string) => {
    setShowWelcome(false)
    addMessage({ id: crypto.randomUUID(), type: 'user', text })
    setIsLoading(true)

    try {
      const { a2uiMessages, textMessages } = await callAgent(buildTextParts(text))

      if (a2uiMessages.length > 0) {
        setDebugMessages(prev => [...prev, ...a2uiMessages])
        addMessage({ id: crypto.randomUUID(), type: 'agent-a2ui', a2uiMessages })
      } else if (textMessages.length > 0) {
        addMessage({ id: crypto.randomUUID(), type: 'agent-text', text: textMessages.join('\n') })
      } else {
        addMessage({ id: crypto.randomUUID(), type: 'agent-text', text: 'No response from agent.' })
      }
    } catch (err) {
      addMessage({
        id: crypto.randomUUID(),
        type: 'error',
        text: err instanceof Error ? err.message : 'Failed to reach agent',
      })
    } finally {
      setIsLoading(false)
    }
  }, [addMessage])

  const sendAction = useCallback(async (actionName: string, context: Record<string, unknown>) => {
    setIsLoading(true)

    try {
      const { a2uiMessages, textMessages } = await callAgent(buildActionParts(actionName, context))

      if (a2uiMessages.length > 0) {
        setDebugMessages(prev => [...prev, ...a2uiMessages])
        addMessage({ id: crypto.randomUUID(), type: 'agent-a2ui', a2uiMessages })
      } else if (textMessages.length > 0) {
        addMessage({ id: crypto.randomUUID(), type: 'agent-text', text: textMessages.join('\n') })
      }
    } catch (err) {
      addMessage({
        id: crypto.randomUUID(),
        type: 'error',
        text: err instanceof Error ? err.message : 'Action failed',
      })
    } finally {
      setIsLoading(false)
    }
  }, [addMessage])

  return { messages, isLoading, showWelcome, debugMessages, sendText, sendAction }
}
