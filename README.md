# Farm Agents - AI Agent for Farmers

## Project Structure

app/
├── api/ # API routes & middleware
├── core/ # Agent, config, database
├── tools/ # LangChain tools (price, schemes)
├── models/ # schemas
├── services/ # LLM, analytics
└── utils/ # Helpers, validators


## Quick Start

```bash
# 1. Clone & setup
git clone <repo>
cd farm-agents

# 2. Setup environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and MONGODB_URI if needed

# 3. Run with Docker
make docker-run

# 4. Test API
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"tomato price in maharashtra","user_id":"test","session_id":"s1"}'

> Note: The service requires MongoDB to be available at `MONGODB_URI` for chat persistence. In Docker, MongoDB is started automatically via `deployments/docker/docker-compose.yml`.
```

## Bot Integration (Telegram & WhatsApp)

Farmers can interact with the AI via **Telegram** or **WhatsApp** directly.

### Telegram Bot
1. Chat with [@BotFather](https://t.me/botfather), send `/newbot` to create a bot
2. Add to `.env`: `TELEGRAM_BOT_TOKEN=<your-token>`
3. Run: `python scripts/run_telegram_bot.py`

### WhatsApp Bot (Twilio)
1. Create Twilio account and get Account SID, Auth Token, WhatsApp number
2. Add to `.env`:
   ```
   TWILIO_ACCOUNT_SID=<sid>
   TWILIO_AUTH_TOKEN=<token>
   TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
   ```
3. Set webhook in Twilio to `https://your-server.com/webhook/whatsapp`
4. Run backend and start chatting!

## Development

# Install dependencies
make install

# Run locally
make dev

# Run tests
make test

# Format code
make format


## Adding a New Tool

Create app/tools/new_tool.py

Implement @tool async function

Add to app/tools/__init__.py ALL_TOOLS list

Agent will auto-discover it

## Adding a New API Endpoint

Add route in app/api/routes/

Register in app/main.py

## Deployment

# Build image
make build

# Run with docker-compose
make docker-run

## Contributing

Follow existing structure

Add tests in tests/ (tests in the factory iteration mode.. soon added)

Run make lint before committing

Update docs if adding features