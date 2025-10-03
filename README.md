## SMS Meeting Summary MVP

### Quick Start
1. Create and fill `.env` from `.env.example`.
2. Install deps: `pip install -r requirements.txt`.
3. Run server: `uvicorn app.main:app --reload --port ${PORT:-8000}`.
4. Expose public URL for callbacks (e.g., `ngrok http 8000`) and set `PUBLIC_BASE_URL`.

### Services
- FastAPI backend: OAuth, webhooks, summarization stub, SMS send.
- Twilio: SMS delivery.
- Microsoft Graph: meeting/chats/transcripts (where allowed).
- Slack: optional channel context.

### Dev Notes
- Tokens are stored in-memory for now; replace with a DB/secret store later.
- Summarization is a stub; swap for your preferred LLM.
# hello world
