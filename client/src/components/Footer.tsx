import { useState, type FormEvent } from 'react'

interface Props {
  onSubmit: (text: string) => void
  isLoading: boolean
}

export default function Footer({ onSubmit, isLoading }: Props) {
  const [input, setInput] = useState('')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || isLoading) return
    setInput('')
    onSubmit(text)
  }

  return (
    <footer>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask about your accounts, transactions, transfers..."
          autoComplete="off"
        />
        <button type="submit" disabled={isLoading}>
          <span className="material-icons">send</span>
        </button>
      </form>
    </footer>
  )
}
