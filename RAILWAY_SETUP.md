# Railway Deployment Guide

This project should be deployed as **two Railway services** from the same GitHub repo.

## 1. Service: `rehmat-agent` (Python)

- New Service -> Deploy from GitHub repo
- Root Directory: `/` (repo root)
- Railway will use `railway.toml`

### Required Variables (`rehmat-agent`)

```env
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
GOOGLE_API_KEY=your_google_api_key
```

## 2. Service: `rehmat-web` (Next.js)

- Add another service from the same repo
- Root Directory: `web`
- Railway will use `web/railway.toml`

### Required Variables (`rehmat-web`)

```env
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
NEXT_PUBLIC_LIVEKIT_URL=wss://your-livekit-url
```

## 3. Connect both services

1. Deploy `rehmat-agent`
2. Deploy `rehmat-web`
3. Open `rehmat-web` public URL and test call flow

## 4. Remove Vercel setup

- `vercel.json` has been removed from this repo
- No Vercel-specific build config remains

## 5. Common issues

### Frontend build fails
- Ensure service root is exactly `web`
- Confirm Node install uses lockfile (`npm ci`)

### Token API returns 500
- In `rehmat-web`, verify:
  - `LIVEKIT_API_KEY`
  - `LIVEKIT_API_SECRET`
  - `NEXT_PUBLIC_LIVEKIT_URL`

### Agent not joining room
- In `rehmat-agent`, verify:
  - `LIVEKIT_URL`
  - `LIVEKIT_API_KEY`
  - `LIVEKIT_API_SECRET`
  - `GOOGLE_API_KEY`

## 6. Optional hardening

- Set Railway environment to Production
- Enable log drains/alerts
- Add custom domain to `rehmat-web`
