import { useEffect, useRef, useState, memo } from 'react'
import { MessageProcessor } from '@a2ui/web_core/v0_9'
import { A2uiSurface } from '@a2ui/react/v0_9'
import { basicCatalog } from '../catalog'
import type { A2UIMessage } from '../api/agent'
import type { SurfaceModel } from '@a2ui/web_core/v0_9'

interface Props {
  messages: A2UIMessage[]
  onAction: (name: string, context: Record<string, unknown>) => void
}

function A2UISurfaceMessageInner({ messages, onAction }: Props) {
  const [surfaces, setSurfaces] = useState<Array<{ id: string; model: SurfaceModel<never> }>>([])
  const processorRef = useRef<MessageProcessor<never> | null>(null)

  useEffect(() => {
    const processor = new MessageProcessor([basicCatalog]) as MessageProcessor<never>
    processorRef.current = processor

    const surfaceIds: string[] = []
    for (const msg of messages) {
      if (msg.createSurface) {
        const sid = (msg.createSurface as { surfaceId: string }).surfaceId
        if (sid && !surfaceIds.includes(sid)) surfaceIds.push(sid)
      }
    }
    if (surfaceIds.length === 0) surfaceIds.push('default')

    // @ts-expect-error processMessages is accessible at runtime
    processor.processMessages(messages)

    const result: Array<{ id: string; model: SurfaceModel<never> }> = []
    for (const id of surfaceIds) {
      const surface = processor.model.getSurface(id)
      if (surface) {
        (surface.onAction as unknown as {
          subscribe: (cb: (action: Record<string, unknown>) => void) => { unsubscribe: () => void }
        }).subscribe((action: Record<string, unknown>) => {
          onAction(action.name as string, (action.context || {}) as Record<string, unknown>)
        })
        result.push({ id, model: surface as SurfaceModel<never> })
      }
    }
    setSurfaces(result)

    return () => {
      processor.model.dispose()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (surfaces.length === 0) return null

  return (
    <div className="agent-message a2ui-response">
      {surfaces.map(({ id, model }) => (
        <A2uiSurface key={id} surface={model} />
      ))}
    </div>
  )
}

export default memo(A2UISurfaceMessageInner)
