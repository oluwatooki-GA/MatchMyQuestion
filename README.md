# MatchMyQuestion

<div align="center">

**AI-Powered Semantic Search for Past Exam Questions**

[![GitHub](https://img.shields.io/badge/GitHub-View%20Repository-181717?style=for-the-badge&logo=github)](https://github.com/oluwatooki-GA/MatchMyQuestion)

A full-stack web application that uses vector embeddings and semantic search to help students find relevant past exam questions instantly.

</div>

---

## Overview

MatchMyQuestion transforms how students prepare for exams by leveraging AI to find semantically similar questions from a database of thousands of past exam papers. Instead of keyword matching, it understands the *meaning* behind queries to deliver the most relevant results.

### Key Features

- **Semantic Search**: Uses sentence-transformers and Qdrant vector database for intelligent query matching
- **Multi-Subject Support**: Covers 30+ subjects across various disciplines
- **Year Filtering**: Filter results by specific exam years
- **Instant Answers**: View explanations and correct answers for each question
- **Fast & Responsive**: Built with React + FastAPI for optimal performance
- **Redis Caching**: Speeds up repeated queries

---

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **Lucide React** for icons

### Backend
- **FastAPI** for REST API
- **Qdrant** as vector database
- **Redis** for caching
- **sentence-transformers** (all-MiniLM-L6-v2) for embeddings
- **Pydantic** for data validation
- **slowapi** for rate limiting

### Scraper
- **BeautifulSoup4** for web scraping
- **CLI tool** for data collection and Qdrant upload

---

## Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   Backend   │─────▶│   Qdrant    │
│  (React)    │      │  (FastAPI)  │      │  (Vectors)  │
└─────────────┘      └─────────────┘      └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   Redis     │
                     │  (Cache)    │
                     └─────────────┘

┌─────────────┐
│   Scraper   │─────▶ Updates Qdrant with new questions
│   (Python)  │
└─────────────┘
```

---

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed

### 1. Clone & Start Services

```bash
git clone https://github.com/oluwatooki-GA/MatchMyQuestion.git
cd MatchMyQuestion
docker-compose up -d --build
```

This starts all services:
- **Frontend** (port 3000) — React + TypeScript
- **Backend** (port 8000) — FastAPI
- **Qdrant** (port 6333) — Vector database
- **Redis** (port 6379) — Caching

### 2. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

### 3. Stop Services

```bash
docker-compose down
```

---

## Project Structure

```
MatchMyQuestion/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── config/         # Settings & configuration
│   │   ├── schemas/        # Pydantic models
│   │   ├── services/       # Business logic (search, embeddings)
│   │   └── main.py         # FastAPI application entry
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks (useSearchForm)
│   │   ├── lib/            # API client
│   │   ├── types/          # TypeScript types
│   │   └── data/           # Static data (subjects)
│   ├── package.json
│   └── Dockerfile
│
├── scraper/                 # Data collection tool
│   ├── app/
│   │   ├── commands/       # CLI commands
│   │   ├── config/         # Scraper configuration
│   │   ├── qdrant/         # Qdrant uploader
│   │   └── services/       # Scraping logic
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml       # Service orchestration
├── .env.dev                 # Development environment
└── .env.prod                # Production environment
```

---

## API Endpoints

### Search Endpoint

```http
POST /api/v1/search
Content-Type: application/json

{
  "q": "photosynthesis process in plants",
  "search_items": [
    {"subject": "Biology", "years": ["2023", "2022"]}
  ]
}
```

**Response:**

```json
{
  "result": [
    {
      "question": "Which of the following occurs during photosynthesis?",
      "options": ["A. Carbon dioxide is released", "B. Oxygen is produced", ...],
      "correct_answer": "Correct Answer: Option B",
      "correct_answer_letter": "B",
      "explanation_html": "<div>...</div>",
      "subject": "Biology",
      "exam_type": "JAMB",
      "year": "2023",
      "image_url": "N/A"
    }
  ]
}
```

---

## Configuration

### Environment Variables (.env.dev)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Frontend API URL | `http://localhost:8000` |
| `QDRANT_URL` | Qdrant instance URL | `http://qdrant:6333` |
| `QDRANT_API_KEY` | Qdrant API key | (empty) |
| `QDRANT_COLLECTION_NAME` | Collection name | `questions` |
| `REDIS_HOST` | Redis host | `redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `CORS_ORIGIN` | Allowed CORS origin | `http://localhost:3000` |

---

## How It Works

1. **Embedding Generation**: Exam questions are converted to 384-dimensional vectors using sentence-transformers
2. **Vector Storage**: Vectors are stored in Qdrant with metadata (subject, year, exam type)
3. **Semantic Search**: User queries are embedded and compared using cosine similarity
4. **Filtering**: Results are filtered by selected subjects and years
5. **Caching**: Redis caches search results for 30 minutes

---

## Available Subjects

Accounts, Agricultural Science, Animal Husbandry, Arabic, Biology, Book Keeping, Catering, Chemistry, Christian Religious Knowledge, Civic Education, Commerce, Computer Studies, Data Processing, Economics, English, Fine Arts, French, Further Mathematics, Geography, Government, Hausa, History, Home Economics, Igbo, Insurance, Islamic Religious Knowledge, Literature, Marketing, Mathematics, Music, Office Practice, Physical Education, Physics, Yoruba

---

## License

MIT License - feel free to use this project for learning or portfolio purposes.

---

<div align="center">

Built with ❤️ by [oluwatooki-GA](https://github.com/oluwatooki-GA)

[![GitHub](https://img.shields.io/badge/GitHub-oluwatooki--GA-181717?style=flat-square&logo=github)](https://github.com/oluwatooki-GA)

</div>
