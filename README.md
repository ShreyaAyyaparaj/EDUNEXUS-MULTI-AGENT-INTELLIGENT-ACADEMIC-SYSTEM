# EduNexus — Multi-Agent Intelligent Academic System

> **An Agentic AI Decision-Support Layer for Higher Education Institutions**

EduNexus is a **multi-agent AI system designed for higher education institutions**. It works alongside existing academic ERP systems to transform stored academic data into **personalized recommendations, proactive interventions, intelligent workflows, and institutional insights**.

Unlike a conventional ERP that primarily stores and displays information, EduNexus uses specialized AI agents to **analyze context, coordinate tasks, recommend actions, and assist students, faculty, and administrators**.

---

## 🎯 Problem Statement

Traditional higher-education ERP systems efficiently manage academic and administrative information such as attendance, marks, student records, and requests. However, they generally depend on predefined rules and do not provide comprehensive, context-aware decision support.

For example, an ERP may detect that a student's attendance has fallen below 75% and send an alert. EduNexus goes further by combining attendance with **internal marks, quiz performance, assignments, skills, and academic history** to identify broader patterns and recommend appropriate interventions.

---

## 💡 Proposed Solution

EduNexus introduces an **Agentic AI layer** on top of existing academic systems.

The system consists of specialized agents, each responsible for a particular academic or institutional function. These agents can operate:

- **Proactively** — triggered by academic events, scheduled analysis, or changes in student data.
- **Reactively** — when students, faculty, or administrators submit queries or requests.

A central agent-orchestration layer coordinates the agents and enables them to access the required data and AI capabilities.

---

## 🤖 Multi-Agent Architecture

EduNexus currently consists of **7 specialized agents**:

### 1. Student Success Agent

Monitors student academic performance using:

- Attendance
- Internal marks
- Quiz performance
- Assignments
- GPA/CGPA
- Academic history

**Responsibilities:**

- Identify students who may require academic intervention
- Detect performance trends
- Generate alerts
- Recommend suitable interventions
- Provide student progress summaries

---

### 2. Academic Guidance Agent

Provides personalized academic recommendations based on:

- Academic performance
- Skills
- Interests
- Career goals
- Certifications

**Provides recommendations for:**

- Courses
- Electives
- Certifications
- Internships
- Research opportunities
- Academic improvement plans

---

### 3. Mentor Discovery Agent

Recommends suitable faculty mentors based on **semantic similarity** rather than simple keyword matching.

It considers:

**Student:**
- Project domain
- Skills
- Interests
- Technologies

**Faculty:**
- Expertise
- Research interests
- Publications
- Previous projects
- Availability
- Mentoring workload

Embeddings are used to identify faculty whose expertise is semantically aligned with the student's requirements.

---

### 4. Workflow & Notification Agent

Assists with institutional workflows such as:

- Leave requests
- Internship approvals
- Project approvals
- OD requests
- Bonafide requests

The agent can:

- Route requests
- Track request status
- Send reminders
- Escalate delayed requests
- Notify relevant stakeholders

> **Important:** EduNexus does not replace faculty/HOD decision-making. AI assists and coordinates the workflow while final approval remains with authorized human personnel.

---

### 5. Placement Assistant Agent

Provides placement-oriented assistance including:

- Resume guidance
- Technical interview preparation
- HR interview preparation
- Aptitude preparation
- Placement roadmaps
- Company eligibility guidance

The agent provides personalized guidance based on the student's profile and skills.

---

### 6. Admin Analytics & Report Agent

Converts institutional data into actionable reports and insights.

Examples:

- Attendance analytics
- Student performance reports
- Placement statistics
- Department-level insights
- Mentor workload
- Student skill distributions
- Achievement reports

---

### 7. SkillFolio Agent

Maintains a verified digital record of student achievements.

Examples:

- Certifications
- Hackathons
- Internships
- Workshops
- Competitions
- Club activities
- Leadership activities
- Research publications

Faculty verification is required before achievements become officially recognized in the student's profile.

---

# 🔄 How EduNexus Works

```text
                    Existing Academic ERP
                           │
                           │
             Attendance / Marks / Records
                           │
                           ▼
                  ┌─────────────────┐
                  │   FastAPI API   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │    LangGraph    │
                  │ Agent Orchestrator│
                  └────────┬────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
 Student Success     Academic Guidance    Mentor Discovery
       │                   │                   │
       ├───────────────┬───┴───────────────┬───┤
       │               │                   │
       ▼               ▼                   ▼
 Workflow          Placement            SkillFolio
 Agent             Assistant              Agent
       │
       ▼
 Admin Analytics & Reports
       │
       ▼
 Students / Faculty / Administrators
```

---

# 💬 Student Query Flow

Students can interact with EduNexus through an AI assistant integrated into the web application.

For example:

> **"Which faculty member would be suitable for my AI project?"**

The request follows:

```text
Student
   ↓
React Frontend
   ↓
FastAPI REST API
   ↓
LangGraph
   ↓
Mentor Discovery Agent
   ↓
PostgreSQL + ChromaDB
   ↓
Gemini
   ↓
Recommendation + Explanation
   ↓
Student Dashboard
```

The student does **not** need to manually select an agent. The system identifies the request and routes it to the appropriate agent.

---

# ⚡ Proactive Agent Flow

Agents are not limited to chatbot queries.

For example:

```text
Faculty updates attendance
          ↓
Academic data changes
          ↓
Student Success Agent
          ↓
Analyzes:
Attendance + Marks + Quizzes + Assignments
          ↓
Identifies academic risk
          ↓
Recommendation / Alert
          ↓
Student + Faculty
```

This is one of the key differences between EduNexus and a conventional ERP.

### Conventional ERP

```text
Attendance < 75%
       ↓
Predefined rule
       ↓
Send notification
```

### EduNexus

```text
Attendance
    +
Internal Marks
    +
Quiz Performance
    +
Assignments
    +
Academic History
       ↓
AI-based contextual analysis
       ↓
Risk / Pattern Identification
       ↓
Personalized Recommendation
```

---

# 🏗️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | **React + Vite** | Interactive web interface and dashboards |
| Backend | **FastAPI + Python** | REST APIs and application logic |
| Database | **PostgreSQL** | Structured academic and institutional data |
| AI Orchestration | **LangGraph** | Multi-agent workflow and coordination |
| LLM | **Google Gemini API** | Reasoning, generation, summarization, and recommendations |
| Embeddings | **Sentence Transformers / Gemini Embeddings** | Semantic representation of text |
| Vector Database | **ChromaDB** | Semantic search and similarity matching |
| Authentication | **JWT** | Secure authentication and role-based access |
| ORM | **SQLAlchemy** | Python–PostgreSQL interaction |
| Frontend Deployment | **Vercel** | Web application hosting |
| Backend Deployment | **Render** | API/backend hosting |
| Database Hosting | **Neon PostgreSQL** | Cloud PostgreSQL deployment |
| Version Control | **Git + GitHub** | Source control and collaboration |

---

# 🗄️ Database Architecture

EduNexus uses different storage technologies for different purposes.

### PostgreSQL

PostgreSQL is the **primary structured database**.

It stores:

- Student profiles
- Faculty profiles
- Attendance
- Marks
- Courses
- Requests
- SkillFolio records
- Workflow information
- User roles

### ChromaDB

ChromaDB is used for **vector-based semantic search**.

It stores embeddings related to information such as:

- Faculty expertise
- Faculty research interests
- Student interests
- Project descriptions
- Knowledge-base documents

This enables searches based on **meaning rather than exact keywords**.

For example:

```text
Student:
"AI and image analysis"

Faculty:
"Deep Learning and Computer Vision"

        ↓

Semantic similarity

        ↓

Potential mentor match
```

PostgreSQL remains the source of structured institutional data, while ChromaDB supports semantic retrieval.

---

# 🔐 User Roles

EduNexus supports role-based access for:

### Student

- View academic performance
- Ask AI questions
- Find mentors
- Receive recommendations
- Access placement assistance
- Manage SkillFolio
- Submit institutional requests

### Faculty

- View student performance
- Manage academic information
- Verify SkillFolio achievements
- Handle requests
- Receive intervention alerts
- Access relevant analytics

### Administrator

- Manage institutional information
- Monitor system analytics
- View reports
- Monitor workflows
- Manage users and system-level information

---

# 🔒 Security

The system uses role-based authentication and authorization.

Current security approach includes:

- JWT authentication
- Password hashing
- Role-based access control
- Environment variables for API credentials
- Separation of frontend and backend services

Sensitive credentials such as API keys and database passwords are **not stored in the GitHub repository**.

---

# 📁 Project Structure

```text
EDUNEXUS/
│
├── agents/
│   ├── graph.py
│   ├── llm.py
│   ├── state.py
│   │
│   ├── nodes/
│   │   ├── admin_predictions.py
│   │   ├── mentor_discovery.py
│   │   ├── placement_assistant.py
│   │   └── student_success.py
│   │
│   └── retrievers/
│       └── vector_store.py
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── scheduler/
│   │   └── services/
│   │
│   └── requirements.txt
│
├── database/
│   ├── docs/
│   └── seed/
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── context/
│       └── pages/
│
├── docker-compose.yml
└── README.md
```

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/ShreyaAyyaparaj/EDUNEXUS-MULTI-AGENT-INTELLIGENT-ACADEMIC-SYSTEM.git
cd EDUNEXUS-MULTI-AGENT-INTELLIGENT-ACADEMIC-SYSTEM
```

## 2. Backend setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

## 3. Environment variables

Create a `.env` file locally.

Example:

```env
GEMINI_API_KEY=your_api_key
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
```

> Never commit the actual `.env` file to GitHub.

## 4. Start the backend

From the project root:

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

If your package configuration runs Uvicorn from inside the `backend` directory:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 5. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at the local Vite development URL shown in the terminal.

---

# 🧪 Testing & Evaluation

The system can be evaluated using metrics such as:

### Agent Performance

- Student-risk detection performance
- Mentor recommendation accuracy
- Recommendation relevance
- Response accuracy

### System Performance

- API response time
- Agent execution time
- Workflow processing time
- Report-generation time

### Scalability

- Concurrent users
- Increasing academic records
- Vector database growth
- Agent workload
- API throughput

### Usability

- Student interaction success rate
- Faculty workflow completion time
- Recommendation usefulness
- User feedback

---

# 🔬 Research Contribution

The research focus of EduNexus is not simply building another ERP.

The project investigates how **multi-agent AI can act as an intelligent decision-support layer for higher education systems**.

Key research areas include:

- Multi-agent collaboration
- Proactive academic intervention
- Semantic faculty-mentor recommendation
- Human-in-the-loop institutional workflows
- Personalized academic guidance
- AI-assisted institutional analytics

---

# 📚 Research Foundation

The primary research direction is inspired by recent work on **multi-agent academic advising**, particularly:

**TartanMaroon: Multi-Agent Academic Advising with Iterative Negotiation and Transparent Collaboration — ACL 2026**

TartanMaroon focuses primarily on multi-agent academic advising and degree planning.

EduNexus extends the multi-agent concept toward a broader higher-education decision-support architecture involving:

- Student success monitoring
- Mentor discovery
- Academic guidance
- Institutional workflows
- Placement assistance
- Skill verification
- Administrative analytics

Thus, the project focuses on **extending agentic academic assistance from advising toward broader institutional decision support**.

---

# 🌱 Future Scalability

The current implementation focuses specifically on **higher education institutions**.

The architecture can potentially be extended in the future to:

### Schools

- Parent communication
- Student progress monitoring
- Teacher assistance

### Corporate Learning

- Employee mentoring
- Skill development
- Internal learning recommendations
- Project/team recommendations

These domains are considered **future extensions** and are not part of the current implementation scope.

---

# 🛡️ Design Principles

EduNexus follows several important principles:

**Human-in-the-loop**

AI recommends and assists; authorized humans retain final decision-making authority.

**Modular agents**

Each agent has a specialized responsibility, making the system easier to extend and maintain.

**ERP integration**

EduNexus is designed as an intelligent layer that can work with existing academic systems rather than replacing them.

**Data-driven decisions**

Recommendations are generated using available academic and institutional context.

**Privacy and security**

Sensitive credentials and personal information should be protected through secure authentication, authorization, and environment-based configuration.

---

# 👩‍💻 Project

**EduNexus — Multi-Agent Intelligent Academic System**

**Domain:** Agentic AI • Generative AI • Higher Education • Intelligent Decision Support

**Current Scope:** Higher Education Institutions

**Repository:**  
https://github.com/ShreyaAyyaparaj/EDUNEXUS-MULTI-AGENT-INTELLIGENT-ACADEMIC-SYSTEM

---

## ⭐ Vision

> **Transform the traditional academic ERP from a system that only records information into an intelligent system that understands academic context, proactively identifies opportunities and risks, and assists students, faculty, and administrators in making better decisions.**