import { useEffect, useRef, useState } from 'react'
import { MessageProcessor } from '@a2ui/web_core/v0_9'
import { A2uiSurface, basicCatalog } from '@a2ui/react/v0_9'
import type { A2UIMessage } from '../api/agent'
import type { SurfaceModel } from '@a2ui/web_core/v0_9'

interface Props {
  messages: A2UIMessage[]
  onAction: (name: string, context: Record<string, unknown>) => void
}

export default function A2UISurfaceMessage({ messages, onAction }: Props) {
  const [surfaces, setSurfaces] = useState<Array<{ id: string; model: SurfaceModel<never> }>>([])
  const processorRef = useRef<MessageProcessor<never> | null>(null)
  const processedRef = useRef(false)

  useEffect(() => {
    if (processedRef.current) return
    processedRef.current = true

    const processor = new MessageProcessor([basicCatalog]) as MessageProcessor<never>
    processorRef.current = processor

    // Collect surface IDs from messages
    const surfaceIds: string[] = []
    for (const msg of messages) {
      if (msg.createSurface) {
        const sid = (msg.createSurface as { surfaceId: string }).surfaceId
        if (sid && !surfaceIds.includes(sid)) surfaceIds.push(sid)
      }
    }
    if (surfaceIds.length === 0) surfaceIds.push('default')

    // Process all messages
    // @ts-expect-error processMessages is accessible at runtime
    processor.processMessages(messages)

    // Build surface list
    const result: Array<{ id: string; model: SurfaceModel<never> }> = []
    for (const id of surfaceIds) {
      const surface = processor.model.getSurface(id)
      if (surface) {
        // Wire action handler on each surface
        (surface.onAction as unknown as {
          subscribe: (cb: (action: Record<string, unknown>) => void) => { unsubscribe: () => void }
        }).subscribe((action: Record<string, unknown>) => {
          onAction(action.name as string, (action.context || {}) as Record<string, unknown>)
        })
        result.push({ id, model: surface as SurfaceModel<never> })
      }
    }
    setSurfaces(result)
  }, [messages, onAction])

  if (surfaces.length === 0) return null

  return (
    <div className="agent-message a2ui-response">
      {surfaces.map(({ id, model }) => (
        <A2uiSurface key={id} surface={model} />
      ))}
    </div>
  )
}
