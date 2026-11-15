# SalesMind AI — Premium frontend starter

A responsive React + TypeScript frontend prototype for SalesMind AI.

## Stack
- React + Vite + TypeScript
- Tailwind CSS (utility layer) + custom design tokens
- React Three Fiber / Drei for the floating 3D AI orb
- Framer Motion for restrained UI motion
- Recharts for analytics charts
- SheetJS (`xlsx`) for local CSV/Excel preview

## Run locally
```bash
npm install
npm run dev
```
Open the local URL printed by Vite.

## Build
```bash
npm run build
npm run preview
```

## Important data-integrity note
The Overview uses clearly illustrative sample figures. They are not real business metrics and must not be presented as calculated results. The Data workspace currently parses the selected spreadsheet locally to preview its row and column count. It does not yet send files to a server or calculate business KPIs.

The AI Advisor is a UI preview. Its assistant response explicitly states that the backend is not connected; it does not fabricate dataset-specific answers.

## Backend integration contract
Set `VITE_API_BASE_URL` to the FastAPI service origin. The API adapter in `src/api.ts` expects:
- `POST /api/datasets/upload` — multipart form field `file`; return a dataset ID and detected column metadata.
- `POST /api/advisor/ask` — JSON `{ "dataset_id": "...", "question": "..." }`; return answer, evidence, and optional chart payload.

Recommended next endpoints:
- `GET /api/datasets/{dataset_id}/summary`
- `GET /api/datasets/{dataset_id}/charts/revenue`
- `POST /api/datasets/{dataset_id}/review`
- `GET /api/health`

## Existing SalesMind integration
Keep the existing Python analytics modules as the source of truth. Wrap their deterministic Pandas functions and AI provider call in FastAPI routes. Do not duplicate KPI calculations in React. Validate uploaded files, column mappings, missing values and profit/cost availability on the backend. Never return profit when neither profit nor cost data exists.

## Deployment
Deploy the frontend to Vercel, Netlify, or another static host. Deploy the Python API separately (for example, Render or another Python-capable host), configure `VITE_API_BASE_URL`, and enable CORS for the frontend origin. Keep API keys only in backend environment variables; never expose them through `VITE_` variables.
