# Deployment Guide

## Backend (FastAPI) on Render

1. Push code to GitHub (already done).
2. On Render, choose "Blueprint" and point to this repo. It will auto-detect `render.yaml`.
3. Confirm the service `travel-agentai-backend` deploys from Dockerfile at `travel-agent-ai/backend/Dockerfile`.
4. Set any required env vars in Render (e.g., database URL, JWT secret). Defaults included: `ENV=production`, `PORT=8000`.
5. After deploy, verify health at `/docs` on the Render URL.

## Frontend (Next.js)

Option A: Vercel
- Import the repo on Vercel.
- It will use `travel-agent-ai/frontend/vercel.json`.
- Set `NEXT_PUBLIC_API_BASE_URL` to your Render backend URL.
- Deploy.

Option B: Render Static Site (if using `next export`)
- Ensure `npm run build` performs `next build && next export` to generate `out/`.
- Render will publish the static site from `travel-agent-ai/frontend/out` per `render.yaml`.

## Local commands

Backend:
```bash
cd travel-agent-ai/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Frontend:
```bash
cd travel-agent-ai/frontend
npm ci
npm run dev
```

## Notes
- Do not commit `node_modules`.
- Keep secrets (API keys, DB URLs) in environment variables.
