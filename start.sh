#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Killing any existing processes on ports 8001, 10002, 8080..."
lsof -ti :8001 | xargs kill -9 2>/dev/null || true
lsof -ti :10002 | xargs kill -9 2>/dev/null || true
lsof -ti :8080 | xargs kill -9 2>/dev/null || true
sleep 1

echo ""
echo "=== Starting Bank Assistant (A2UI Multi-Agent Demo) ==="
echo ""
echo "  8 Agents:"
echo "    1. Account Agent       - Bank accounts, balances"
echo "    2. Transaction Agent   - Transaction history"
echo "    3. Analytics Agent     - Spending breakdown"
echo "    4. Loans Agent         - Business loans & finance"
echo "    5. Cards Agent         - Credit & debit cards"
echo "    6. Merchant Agent      - EFTPOS, online payments"
echo "    7. International Agent - FX rates, wire transfers"
echo "    8. Products Agent      - Product catalog"
echo ""
echo "  Services:"
echo "    Mock API: http://localhost:8001  (FastAPI docs: http://localhost:8001/docs)"
echo "    Agent:    http://localhost:10002"
echo "    Client:   http://localhost:8080"
echo ""

# 1. Start mock banking API
cd "$SCRIPT_DIR/mock_server"
uv run python main.py &
MOCK_PID=$!
sleep 2

# Verify mock is up
if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
  echo "ERROR: Mock server failed to start"
  kill $MOCK_PID 2>/dev/null
  exit 1
fi
echo "  [OK] Mock API running"

# 2. Start A2A agent
cd "$SCRIPT_DIR/agent"
uv run . &
AGENT_PID=$!
sleep 5

# Verify agent is up
if ! curl -s http://localhost:10002/.well-known/agent-card.json > /dev/null 2>&1; then
  echo "ERROR: Agent failed to start. Check your GEMINI_API_KEY in agent/.env.local"
  kill $MOCK_PID $AGENT_PID 2>/dev/null
  exit 1
fi
echo "  [OK] Agent running (8 sub-agents loaded)"

# 3. Start web client (Vite + React)
cd "$SCRIPT_DIR/client"
npm run dev > /dev/null 2>&1 &
CLIENT_PID=$!
sleep 3
echo "  [OK] Client running (React + @a2ui/react)"

echo ""
echo "  All systems go! Open http://localhost:8080"
echo "  Press Ctrl+C to stop everything."
echo ""

trap "echo ''; echo 'Shutting down...'; kill $MOCK_PID $AGENT_PID $CLIENT_PID 2>/dev/null; exit" INT TERM
wait
