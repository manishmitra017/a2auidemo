# A2UI Bank Assistant Demo

A multi-agent business banking assistant built with [A2UI](https://a2ui.org/) (Agent-to-UI protocol) and Google's [Agent Development Kit (ADK)](https://google.github.io/adk-docs/).

The agent generates rich, interactive UIs as declarative JSON — no HTML or frontend code is executed by the AI. A renderer converts the JSON into native web components in the browser.

## Architecture

```
Browser (localhost:8080)
    │  A2A Protocol + X-A2A-Extensions header
    ▼
Orchestrator Agent (localhost:10002)
    ├── Account Agent       → GET /api/customers/{id}/accounts
    ├── Transaction Agent   → GET /api/customers/{id}/transactions
    ├── Analytics Agent     → GET /api/customers/{id}/spending-analytics
    ├── Loans Agent         → GET /api/customers/{id}/loans
    ├── Cards Agent         → GET /api/customers/{id}/cards
    ├── Merchant Agent      → GET /api/customers/{id}/merchant-services
    ├── International Agent → GET /api/customers/{id}/international-payments + /api/fx-rates
    └── Products Agent      → GET /api/products
                                    │
                                    ▼
                          Mock Banking API (localhost:8001)
```

### 8 Specialized Agents

| Agent | Domain | Mock API Endpoint |
|-------|--------|-------------------|
| Account Agent | Business Transaction Account, Business Online Saver, Savings & Term Deposits | `/api/customers/{id}/accounts` |
| Transaction Agent | Transaction history, filtering by account or category | `/api/customers/{id}/transactions` |
| Analytics Agent | Spending breakdown, top merchants, month-over-month trends | `/api/customers/{id}/spending-analytics` |
| Loans Agent | BetterBusiness Loan, Car & Equipment Finance, Business Overdraft | `/api/customers/{id}/loans` |
| Cards Agent | Low Rate Credit Card, Business Awards Credit Card, Business Visa Debit Card | `/api/customers/{id}/cards` |
| Merchant Agent | EFTPOS terminals, online payments, merchant summary | `/api/customers/{id}/merchant-services` |
| International Agent | International Money Transfers, Foreign Currency Account, FX rates | `/api/customers/{id}/international-payments` |
| Products Agent | All available banking products and industry solutions | `/api/products` |

### How A2UI Works

1. You send a message via the web UI
2. The orchestrator routes to the right specialist agent
3. The agent calls the mock banking API for data
4. Gemini generates **A2UI JSON** describing UI components (cards, lists, forms, tabs)
5. The JSON is streamed back via the **A2A protocol**
6. The browser renderer converts JSON into interactive web components
7. Button clicks send action events back to the agent for the next step

The key insight: the LLM generates **declarative JSON**, not executable code. The A2UI protocol ensures security — agents can only use pre-approved components from a trusted catalog.

## Prerequisites

- **Python** >= 3.13
- **uv** (Python package manager) — [install](https://docs.astral.sh/uv/getting-started/installation/)
- **Node.js** >= 18 (for npm, used only to check package versions)
- **Gemini API key** — [get one here](https://aistudio.google.com/apikey)

## Setup

```bash
# Clone the repo
git clone <repo-url>
cd a2auidemo

# Add your Gemini API key
cp agent/.env.example agent/.env.local
# Edit agent/.env.local and paste your key
```

## Run

```bash
./start.sh
```

This kills any existing processes on ports 8001/10002/8080, then starts:

1. **Mock Banking API** at `http://localhost:8001` (FastAPI — docs at `/docs`)
2. **A2A Agent** at `http://localhost:10002` (8 sub-agents, A2UI rendering)
3. **Web Client** at `http://localhost:8080` (open this in your browser)

## Try These Queries

- "Show my account balances"
- "What are my recent transactions?"
- "Where do I spend the most?"
- "Show my business loans"
- "Show my business cards"
- "Merchant services summary"
- "Show FX exchange rates"
- "What products do you offer?"

Click the **A2UI JSON** button (bottom-right) to see the raw JSON the agent generates.

## Project Structure

```
a2auidemo/
├── agent/                      # Python A2A agent server
│   ├── __main__.py             # Server entry point (port 10002)
│   ├── agent.py                # Orchestrator with A2UI rendering
│   ├── agent_executor.py       # Request handling and action routing
│   ├── sub_agents.py           # 8 specialized LlmAgent definitions
│   ├── tools.py                # Tools that call the mock API (no local data)
│   ├── prompt_builder.py       # System prompts for the orchestrator
│   ├── examples/0.9/           # A2UI JSON templates for Gemini
│   ├── pyproject.toml          # Python dependencies
│   ├── .env.example            # Template for API key
│   └── .env.local              # Your API key (gitignored)
├── mock_server/                # FastAPI mock banking API
│   ├── main.py                 # All endpoints and mock data
│   └── pyproject.toml
├── client/                     # Web frontend
│   ├── index.html              # Chat interface
│   ├── styles.css              # Banking theme
│   ├── a2ui-renderer.js        # A2UI v0.9 JSON → DOM renderer
│   └── app.js                  # A2A protocol client
├── start.sh                    # One-command launcher
└── README.md
```

## Key Technologies

- **[A2UI v0.9](https://a2ui.org/specification/v0.9-a2ui/)** — Declarative UI protocol for agent-driven interfaces
- **[A2A Protocol](https://google.github.io/A2A/)** — Agent-to-Agent communication protocol
- **[Google ADK](https://google.github.io/adk-docs/)** — Agent Development Kit with sub-agent routing
- **[Gemini 2.5 Flash](https://ai.google.dev/)** — LLM that generates A2UI JSON
- **[FastAPI](https://fastapi.tiangolo.com/)** — Mock banking API server

## Notes

- All banking data comes exclusively from the mock server — no hardcoded data in the agent
- The `@a2ui/react` package (v0.9.1) is available on npm for a production React renderer
- The vanilla JS renderer in `client/a2ui-renderer.js` is intentionally simple for learning
