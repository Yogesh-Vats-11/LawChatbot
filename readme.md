# LawChatbot — AI-Powered Legal Assistance Platform

A full-stack legal assistance platform focused on Indian law (primarily the Bharatiya Nyaya Sanhita – BNS 2023). Combines semantic search over legal provisions with specialized legal utilities — going beyond a general chatbot to provide practical legal assistance: case analysis, judgment summarization, FIR/RTI drafting, consumer complaint preparation, and legal document generation.


## Features

- **Legal Chat** — ask questions in natural language ("What is theft?", "Punishment for robbery?"); semantic search retrieves the most relevant BNS section and returns a concise or detailed answer
- **Case Analysis** — describe an incident in plain language; the system maps it to relevant BNS provisions and related offences via a legal knowledge graph
- **Judgment Summarization** — paste a lengthy judgment and get a transformer-generated summary
- **FIR Assistant** — guided FIR drafting with applicable BNS sections, FIR reference number, and next legal steps; downloadable as PDF
- **RTI Guide** — filing guide, fees, timelines, exemptions, and full RTI application drafting; downloadable as PDF
- **Consumer Court Assistant** — recommends the correct forum (District/State/National Commission) based on claim amount and generates a complete complaint draft as PDF
- **Legal Document Generator** — guided forms for Rent Agreement, Affidavit, Legal Notice, Power of Attorney, and Partnership Deed, exportable as PDF
- **Legal Sections Browser** — browse all indexed BNS sections via the API

## Tech Stack

**Backend:** Python, Flask (Blueprint architecture), Flask-CORS
**Frontend:** HTML5, CSS3, Vanilla JavaScript — single-page application, no framework
**AI / ML:**
- Semantic embeddings via `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- FAISS (Facebook AI Similarity Search) as an in-memory vector index for retrieval
- `facebook/bart-large-cnn` for judgment summarization
**Document generation:** ReportLab (PDF export)
**Knowledge base:** JSON datasets (BNS legal sections + legal knowledge graph) — no SQL database currently required

## How It Works

```
User → Frontend → Flask API → Sentence Transformer → FAISS Search
     → Relevant Legal Sections → Business Logic → Response
```

For judgment summarization specifically:
```
Judgment → BART → Summary
```

**Note on architecture:** this is a semantic search–based legal assistant with transformer-based summarization, not Retrieval-Augmented Generation (RAG) — it does not use a conversational LLM (GPT, Gemini, Claude, Llama, etc.) to generate answers from retrieved context. Transformer models are used only for embeddings and summarization. This is a solid foundation for future RAG integration.

## API Endpoints

```
POST /chat
POST /analyze_case
POST /summarize
POST /fir/assistant
POST /rti/draft
POST /consumer/complaint
POST /documents/generate
```

## Project Structure

```
LawChatbot/
├── backend/
│   ├── routes/          # chat_routes, fir_routes, rti_routes, consumer_routes, document_routes
│   ├── services/
│   ├── models/
│   └── datasets/         # BNS sections, legal knowledge graph (JSON)
├── frontend/              # HTML/CSS/vanilla JS single-page app
└── .gitignore
```

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend

Open `frontend/index.html` in your browser, or serve it via the Flask backend if configured to do so.

## Current Status

Works end-to-end. Implemented: Legal Chat, Case Analysis, Judgment Summarizer, FIR Assistant, RTI Assistant, Consumer Court Assistant, Legal Document Generator, PDF downloads, semantic search, FAISS retrieval, modular Flask backend.

## Strengths

- Modular backend architecture using Flask Blueprints
- Semantic search rather than keyword matching
- Multiple legal utilities integrated into one platform
- Fully local AI models — no paid API dependency
- Clean single-page frontend

## Current Limitations

- Relies on a local JSON knowledge base rather than a comprehensive legal database
- Chat responses are based on semantic retrieval, not reasoning by a conversational LLM
- Does not currently cite judgments or precedents beyond the provided data
- No user authentication or persistent storage
- Document generator uses predefined templates rather than AI-generated drafting

## What I'd Improve Next

- Integrate a conversational LLM over the retrieved context to move from semantic search toward true RAG
- Expand the legal knowledge base beyond BNS 2023
- Add user authentication and persistent history
- Add citation/source display for chat answers

## What This Project Demonstrates

- Semantic search system design with sentence embeddings and FAISS
- Applying transformer models (summarization) to a real-world, domain-specific problem
- Modular full-stack architecture — Flask Blueprint backend + vanilla JS frontend
- Practical AI product design — going beyond a single chatbot into multiple integrated legal utilities (FIR, RTI, consumer complaints, document generation)

## Author

**Yogesh** — B.Tech, AI & Machine Learning, Amity University Gurugram
[GitHub](https://github.com/Yogesh-Vats-11) · [LinkedIn](https://www.linkedin.com/in/yogesh-22a62b27a/)