const SUGGESTIONS = [
  'Show my account balances',
  'What are my recent transactions?',
  'Where do I spend the most?',
  'Show my business loans',
  'Show my business cards',
  'Merchant services summary',
  'Show FX exchange rates',
  'What products do you offer?',
]

interface Props {
  onSuggestionClick: (text: string) => void
}

export default function Welcome({ onSuggestionClick }: Props) {
  return (
    <div className="welcome">
      <h2>Welcome to your Bank Assistant</h2>
      <p>Ask me about accounts, transactions, loans, cards, merchant services, international payments, and more.</p>
      <div className="suggestions">
        {SUGGESTIONS.map(s => (
          <button key={s} className="suggestion" onClick={() => onSuggestionClick(s)}>
            {s}
          </button>
        ))}
      </div>
    </div>
  )
}
