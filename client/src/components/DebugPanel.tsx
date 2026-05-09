interface Props {
  open: boolean
  onClose: () => void
  messages: unknown[]
}

export default function DebugPanel({ open, onClose, messages }: Props) {
  return (
    <div className={`debug-panel ${open ? '' : 'hidden'}`}>
      <div className="debug-header">
        <h3>Raw A2UI Messages (from agent)</h3>
        <button onClick={onClose}>Close</button>
      </div>
      <pre>{JSON.stringify(messages, null, 2)}</pre>
    </div>
  )
}
