# Job Application System with Semantic Search - Development Plan

## Overview

Build an experimentation app for job posting and applicant matching using semantic search. Features include job creation, resume submission (text/PDF), vector embeddings for semantic matching, and conversational AI for querying applicants.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL with pgvector)
- **Embeddings**: Supabase built-in embeddings or pgvector
- **LLM**: OpenAI GPT or Google Gemini (for conversational AI)
- **Frontend**: React + Vite
- **File Storage**: Supabase Storage (for PDF resumes)

## Database Schema (Supabase)

### Tables

1. **jobs**
   - `id` (uuid, primary key)
   - `title` (text)
   - `description` (text)
   - `requirements` (text)
   - `created_at` (timestamp)
   - `embedding` (vector, 1536 dimensions for OpenAI or configurable)

2. **applications**
   - `id` (uuid, primary key)
   - `job_id` (uuid, foreign key to jobs)
   - `applicant_name` (text)
   - `applicant_email` (text, optional)
   - `resume_text` (text)
   - `resume_file_url` (text, optional - Supabase Storage URL)
   - `created_at` (timestamp)
   - `embedding` (vector, same dimensions as jobs)

## Backend Implementation

### 1. Database Models
- **vembedding/jobs/model.py**: Pydantic models for Job (create, response)
- **vembedding/application/model.py**: Pydantic models for Application (create, response)

### 2. Vector Store & Embeddings
- **vembedding/ai/vector_store.py**:
  - `generate_embedding(text: str) -> List[float]`: Generate embeddings using Supabase client or OpenAI
  - `store_job_embedding(job_id: str, embedding: List[float])`: Store job embedding
  - `store_application_embedding(application_id: str, embedding: List[float])`: Store application embedding
  - `find_similar_applicants(job_id: str, top_k: int = 10) -> List[dict]`: Semantic search using cosine similarity

### 3. Conversational AI Service
- **vembedding/ai/conversational.py** (new file):
  - `chat_about_applicants(job_id: str, query: str, conversation_history: List[dict]) -> str`: 
    - Retrieve relevant applicants using semantic search
    - Build context with job details and applicant resumes
    - Call GPT/Gemini API with RAG context
    - Return conversational response

### 4. Services
- **vembedding/jobs/service.py**:
  - `create_job(job_data: dict) -> dict`: Create job, generate embedding, store in DB
  - `get_job(job_id: str) -> dict`: Retrieve job details
  - `list_jobs() -> List[dict]`: List all jobs

- **vembedding/application/service.py**:
  - `submit_application(job_id: str, application_data: dict, resume_file: Optional[File]) -> dict`: 
    - Extract text from PDF if file provided
    - Generate embedding for resume text
    - Store application and embedding in DB
    - Upload PDF to Supabase Storage if provided
  - `get_applications_for_job(job_id: str) -> List[dict]`: List applications for a job
  - `get_top_applicants(job_id: str, top_k: int = 10) -> List[dict]`: Use vector store to find top matches

### 5. API Routes
- **vembedding/jobs/routes.py**:
  - `POST /jobs`: Create job
  - `GET /jobs`: List all jobs
  - `GET /jobs/{job_id}`: Get job details

- **vembedding/application/routes.py**:
  - `POST /jobs/{job_id}/applications`: Submit application (multipart/form-data for PDF)
  - `GET /jobs/{job_id}/applications`: List applications for a job
  - `GET /jobs/{job_id}/applications/top`: Get top N applicants (semantic search)

- **vembedding/ai/routes.py** (new file):
  - `POST /jobs/{job_id}/chat`: Conversational AI endpoint
    - Request: `{ "query": "Give me top 10 applicants", "history": [...] }`
    - Response: `{ "response": "...", "applicants": [...] }`

### 6. Main App
- **vembedding/main.py**: 
  - Include routers for jobs, applications, and AI
  - CORS configuration for React frontend
  - Supabase client initialization

## Frontend Implementation (React + Vite)

### Components Structure