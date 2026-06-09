# Farm Agents - AI Assistant for Farmers

An intelligent AI agent that helps farmers get real-time crop prices, government scheme information, and agricultural advice via API, Telegram, or WhatsApp.

## Features

- **Real-time Crop Prices** - Get current mandi prices for any crop in any state
- **Government Schemes** - Query available subsidies, loans, and farmer programs
- **Multi-channel Access** - Use via REST API, Telegram bot, or WhatsApp
- **Conversation Memory** - Chat history persists across sessions
- **Easy to Extend** - Add new tools or API endpoints quickly

## Tech Stack

- FastAPI - REST API framework
- LangChain - AI agent orchestration
- OpenAI GPT - Language model
- MongoDB - Chat history storage
- Python 3.10+

## Quick Start

### Prerequisites
- Python 3.10+
- MongoDB (local or cloud)
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/farm-agents.git
cd farm-agents

# Copy environment variables
cp .env.example .env

# Edit .env with your keys
# Add OPENAI_API_KEY and MONGODB_URI

# Run with Docker (easiest)
make docker-run

# Or run locally
make install
make dev
