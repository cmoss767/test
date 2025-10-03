## SMS Meeting Summary MVP — Big Picture Plan

### Goal
Deliver concise AI summaries of Slack and Microsoft Teams meetings to a user’s phone via SMS shortly after meetings end.

### Non-Goals (for MVP)
- Real-time/live in-meeting transcription and push notifications.
- Mobile app or push notifications (SMS only).
- Deep admin dashboards or multi-tenant org management.

### Success Criteria
- User connects Slack and Microsoft 365 once (OAuth).
- Within ~5–10 minutes after a meeting ends, user receives an SMS with a useful summary: key topics, decisions, owners, deadlines, links.
- Handles meetings without transcripts gracefully (fall back to chat/calendar context).

## Architecture Overview
- Web App/API (backend):
  - Auth (Slack OAuth, Microsoft OAuth via Azure AD).
  - Webhooks: Microsoft Graph change notifications (meeting/chat), Slack Events (optional), or polling fallback.
  - Data fetchers: Graph (meetings, chats, transcripts when available), Slack (channels/threads).
  - Summarization service: composes context, redacts, chunks, calls LLM, formats output.
  - Notification service: sends SMS via Twilio.
  - Storage: users, connections, tokens, minimal meeting metadata, short-lived content cache.
  - Job queue/scheduler: to run post-meeting fetch and summarization asynchronously.

```
User → OAuth (Slack/MS) → Backend ← Webhooks/Timers
                                  ↓
                            Fetch Context (Graph/Slack)
                                  ↓
                          Summarize (LLM + policies)
                                  ↓
                               SMS (Twilio)
```

## Data Flow (Happy Path)
1) User completes OAuth for Slack and Microsoft 365; we store tokens securely.
2) We subscribe to Microsoft Graph change notifications (calendar or onlineMeetings/callRecords) to detect meeting end; fallback: polling.
3) On meeting end event, enqueue a job with meeting metadata (organizer, time, participants, chat IDs).
4) Job fetches: meeting chat messages, transcript (if enabled), calendar details, and any relevant Slack channel messages in the same time window (if mapped or user-specified channels).
5) Summarization pipeline:
   - Normalize inputs; redact PII/credentials; chunk long text.
   - Compose prompt with goals: topics, decisions, owners, deadlines, risks, follow-ups, links.
   - Call LLM; validate length and structure; retry on failure.
6) Delivery: Send SMS via Twilio to the user’s verified phone number; include an optional “View full recap” link (hosted page) if needed.

## Integrations
- Microsoft Graph
  - Scopes (least privilege for MVP): `Calendars.Read`, `Chat.Read`, `OnlineMeetings.Read`, `CallRecords.Read.All` (if call records/transcripts needed), `offline_access`.
  - Subscriptions: calendar events or chat messages associated with meetings.
  - Content: meeting metadata, meeting chat, transcript (if transcription policy enabled).

- Slack API
  - Scopes: `channels:read`, `channels:history`, `users:read`, `chat:write` (optional, for posting confirmations), `offline`.
  - Events or scheduled retrieval: collect channel/thread messages overlapping the meeting window for context.

- Twilio SMS
  - Messaging Service for sender management and compliance.
  - Webhook for delivery status (optional for reliability monitoring).

## Security & Compliance
- Store tokens encrypted at rest (KMS/KeyVault). Rotate/refresh with `offline_access`.
- Minimize content retention: cache raw transcripts/chats short-term (e.g., 7 days), store only structured summaries long-term.
- Redaction of sensitive strings (keys, passwords, numbers) before LLM calls; configurable regex and entropy-based detectors.
- Tenant admin policies respected; fail closed on insufficient permissions; log minimal metadata.
- Region pinning if required; audit trails for data access.

## Summarization Output (MVP format)
- 5 bullets: key topics/problems discussed.
- Decisions (who decided what).
- Action items with owners and due dates.
- Risks/blockers.
- Links back to meeting/chat (URL if available).
- Target length: ~600–900 characters to fit 1–2 SMS segments (or send as multipart if needed).

## Error Handling & Fallbacks
- No transcript: rely on chat + calendar + invite description/agenda.
- Long chats: hierarchical summarization (chunk → summarize → merge summarize) to control cost.
- Permissions missing: notify user via SMS that parts were inaccessible.
- Delivery failure: retry SMS; secondary email fallback (optional post-MVP).

## Observability
- Structured logs with correlation IDs per meeting.
- Metrics: events received, jobs queued/completed, LLM cost/time, SMS sent/delivered, failure rates.
- Alerts on webhook failures, token refresh failures, SMS delivery errors.

## Phased Delivery
### Phase 0 — Setup (0.5–1 day)
- Create Azure AD app registration and Slack app; configure OAuth, redirect URIs.
- Provision Twilio Messaging Service and phone number; verify.
- Bootstrap backend skeleton with auth flows and secure secret storage.

### Phase 1 — Teams-first MVP (1–2 days)
- Implement Microsoft OAuth and token storage.
- Subscribe to calendar/meeting end events (Graph change notifications); add polling fallback.
- Fetch meeting chat and transcript (when available).
- Summarization pipeline (LLM + formatting + redaction).
- Send SMS via Twilio; include link to meeting/chat when possible.

### Phase 2 — Slack context (0.5–1 day)
- Slack OAuth and token storage.
- Let user opt-in and select channels to include for time-window context.
- Retrieve and blend Slack messages for the meeting window; update summarization.

### Phase 3 — UX polish (0.5 day)
- Minimal web dashboard: connect/disconnect providers, set phone number, toggle Slack sources, view last 10 summaries.
- Reliability: retries, dead-letter queue, idempotency keys per meeting.

## Minimal Data Model (MVP)
- User: id, phone_number, email, created_at.
- Connection: user_id, provider (ms, slack), access_token, refresh_token, scopes, expires_at.
- Meeting: id, user_id, provider_meeting_id, start_at, end_at, status.
- Summary: meeting_id, short_text, full_text_url (optional), created_at, cost_metrics.

## Cost & Limits (rough)
- LLM: ~$0.002–$0.02 per summary depending on size/model.
- Twilio: per-SMS segment; multi-part if >160 GSM chars.
- Microsoft/Slack rate limits: batch requests and backoff; cache.

## Open Questions
- Should we store full transcripts for more than 7 days? (default: no)
- Do we need org-wide admin consent flows for enterprise tenants now or later?
- Which channels should Slack pull from by default? User-selected only?
- Preferred LLM vendor and region constraints?

