## 🧠 Digital Twin GCP

A cloud-hosted AI assistant with OpenAI backend using Flask, deployed on GCP.

### 🔧 Backend
- Flask API server
- Uses `OPENAI_API_KEY` from `.env`
- Route: `/` (POST)

### 🌐 Frontend
- Vite/React app
- `.env` points to GCP cloud function

### 🚀 Deployment
- Backend: GCP Cloud Functions (via `terraform`)
- Frontend: Vite build

---

More documentation in `/docs`.
