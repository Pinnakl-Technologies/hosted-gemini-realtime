# Rehmat-e-Shereen Voice Agent - Setup Guide

## Quick Start (Local)

```bash
cd web
npm install
npm run dev
```

## Environment Variables

### Root `.env.local` (Python Agent)

```env
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
GOOGLE_API_KEY=your_google_api_key
```

### `web/.env.local` (Next.js Frontend)

```env
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
NEXT_PUBLIC_LIVEKIT_URL=wss://your-livekit-url
```

## Deployment

This project is configured for Railway only.

1. Deploy Python agent service from repo root `/`
2. Deploy Next.js web service from `web/`
3. Follow `RAILWAY_SETUP.md` for exact Railway steps

## Useful Dev Commands

```bash
# from web/
npm run dev
npm run build
npm run start
```

```bash
# from repo root
uv run python src/agent.py dev
uv run python src/agent.py start
```
