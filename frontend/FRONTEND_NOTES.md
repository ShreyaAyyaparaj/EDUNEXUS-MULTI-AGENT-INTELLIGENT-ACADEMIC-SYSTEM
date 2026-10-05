# EduNexus frontend implementation notes

## Wired backend endpoints
- POST /api/auth/login — form-urlencoded, current FastAPI OAuth2 password flow
- GET /api/student/dashboard
- GET /api/student/attendance
- GET /api/student/marks
- GET /api/student/results
- GET /api/student/resources
- GET /api/student/achievements
- POST /api/faculty/attendance/parse
- POST /api/faculty/attendance/validate
- POST /api/faculty/attendance/confirm
- POST /api/faculty/marks/parse
- POST /api/faculty/marks/validate
- POST /api/faculty/marks/confirm

## Safety model represented in UI
Gemini interpretation -> deterministic backend validation -> human confirmation -> database commit.
The frontend never writes marks or attendance directly.

## Aadhi
- `public/aadhi.png` is the supplied 2D campus mascot reference.
- `public/aadhi-3d.png` is a generated 3D-style companion asset based on the mascot reference.
- The floating Aadhi widget is fully implemented visually.
- It currently does not call a nonexistent chat endpoint. The UI is ready for the Academic/University Copilot endpoint once the RAG backend is implemented.

## Run
```powershell
npm install
npm run dev
```
The Vite proxy maps `/api` to `http://127.0.0.1:8000`.
