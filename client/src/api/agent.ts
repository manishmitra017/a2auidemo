const AGENT_URL = 'http://localhost:10002'
const A2UI_EXTENSION_URI = 'https://a2ui.org/a2a-extension/a2ui/v0.9'

export interface A2UIMessage {
  version?: string
  createSurface?: Record<string, unknown>
  updateComponents?: Record<string, unknown>
  updateDataModel?: Record<string, unknown>
  deleteSurface?: Record<string, unknown>
}

export async function callAgent(parts: unknown[]): Promise<{
  a2uiMessages: A2UIMessage[]
  textMessages: string[]
}> {
  const cardResp = await fetch(`${AGENT_URL}/.well-known/agent-card.json`)
  const agentCard = await cardResp.json()

  const extensions: unknown[] = []
  if (agentCard.capabilities?.extensions) {
    for (const ext of agentCard.capabilities.extensions) {
      if (ext.uri?.includes('a2ui')) extensions.push(ext)
    }
  }

  const body = {
    jsonrpc: '2.0',
    id: crypto.randomUUID(),
    method: 'message/send',
    params: {
      message: {
        role: 'user',
        parts,
        messageId: crypto.randomUUID(),
      },
      configuration: { extensions },
    },
  }

  const resp = await fetch(`${AGENT_URL}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-A2A-Extensions': A2UI_EXTENSION_URI,
    },
    body: JSON.stringify(body),
  })

  const result = await resp.json()
  if (result.error) throw new Error(result.error.message || 'Agent error')

  return extractParts(result.result)
}

function extractParts(task: Record<string, unknown>): {
  a2uiMessages: A2UIMessage[]
  textMessages: string[]
} {
  const a2uiMessages: A2UIMessage[] = []
  const textMessages: string[] = []

  function extract(msg: Record<string, unknown>) {
    if (msg.role !== 'agent') return
    for (const part of (msg.parts as Record<string, unknown>[]) || []) {
      if (part.kind === 'data' && part.data) {
        const d = part.data as Record<string, unknown>
        if (d.version === 'v0.9' || d.createSurface || d.updateComponents || d.updateDataModel) {
          a2uiMessages.push(d as A2UIMessage)
        }
      } else if (part.kind === 'text' && part.text) {
        textMessages.push(part.text as string)
      }
    }
  }

  const status = (task as Record<string, Record<string, unknown>>).status
  if (status?.message) extract(status.message as Record<string, unknown>)

  if (a2uiMessages.length === 0 && textMessages.length === 0) {
    const history = (task as Record<string, unknown[]>).history
    if (history) {
      const agentMsgs = history.filter((m: unknown) => (m as Record<string, unknown>).role === 'agent')
      if (agentMsgs.length > 0) extract(agentMsgs[agentMsgs.length - 1] as Record<string, unknown>)
    }
  }

  return { a2uiMessages, textMessages }
}

export function buildTextParts(text: string): unknown[] {
  return [
    { kind: 'text', text },
    { kind: 'data', data: { useStreaming: false } },
  ]
}

export function buildActionParts(actionName: string, context: Record<string, unknown>): unknown[] {
  return [
    { kind: 'data', data: { version: 'v0.9', action: { name: actionName, context } } },
    { kind: 'data', data: { useStreaming: false } },
  ]
}
