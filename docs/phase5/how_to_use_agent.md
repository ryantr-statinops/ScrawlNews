# How to Use the Agent

1. Ensure all environment variables are set (see `config/.env.example`).
2. Install dependencies: `make install`
3. Run the agent: `make run`
4. Run tests: `make test`

The agent will:
- Fetch news from Google News
- Summarize using LLM
- Send results to Telegram
