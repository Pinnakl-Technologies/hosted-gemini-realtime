# Rehmat-e-Shereen Voice Agent (Web)

Next.js frontend for the voice assistant.

## Local Development

```bash
npm install
npm run dev
```

## Required Environment (`web/.env.local`)

```env
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
NEXT_PUBLIC_LIVEKIT_URL=wss://your-livekit-url
```

## Deploy (Railway)

This frontend is configured for Railway using `web/railway.toml`.

- Service root directory: `web`
- Build command: `npm ci && npm run build`
- Start command: `npm run start -- --hostname 0.0.0.0 --port $PORT`

Use `RAILWAY_SETUP.md` in the repo root for complete frontend + agent deployment.
