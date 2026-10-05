# EduNexus Frontend

This frontend is wired to the current EduNexus FastAPI contract:
- POST /api/auth/login (application/x-www-form-urlencoded)
- GET /api/student/dashboard
- GET /api/student/attendance
- GET /api/student/marks
- GET /api/student/results
- GET /api/student/resources
- GET /api/student/achievements
- POST /api/faculty/attendance/parse|validate|confirm
- POST /api/faculty/marks/parse|validate|confirm

Run:

```powershell
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

Aadhi has a 2D reference and a generated 3D-style asset. The chat UI is ready; it is intentionally not wired to a nonexistent backend chat endpoint yet.
