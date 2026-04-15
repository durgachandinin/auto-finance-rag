# DriveFinance AI

An automotive finance RAG (Retrieval-Augmented Generation) assistant that answers questions about loan rates, eligibility, fees, and refinancing — grounded in your official finance documents.

---

## Features

- **RAG pipeline** — answers are retrieved from and grounded in your uploaded finance documents
- **Conversational chat UI** — clean dark-mode interface similar to ChatGPT/Claude
- **Landing page** — full-screen car-themed login screen
- **Document ingestion** — ingest PDFs/text files into a FAISS vector index
- **Chat history** — maintains context across a conversation

---

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React 18, Tailwind CSS, Vite |
| Backend | Python, Streamlit |
| Vector store | FAISS |
| Embeddings / LLM | OpenAI / configurable |

---

## Project Structure

```
auto_finance_rag/
├── app.py                  # Streamlit app (backend + UI)
├── chain.py                # RAG chain logic
├── retriever.py            # FAISS retriever
├── ingest.py               # Document ingestion script
├── generate_sample_data.py # Generate sample finance docs
├── data/                   # Source documents
├── faiss_index/            # Generated vector index
├── frontend/               # React + Tailwind frontend
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   │       ├── LoginPage.jsx
│   │       ├── ChatPage.jsx
│   │       └── MessageBubble.jsx
│   ├── public/
│   └── package.json
└── requirements.txt
```

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/durgachandinin/auto-finance-rag.git
cd auto-finance-rag
```

### 2. Set up Python environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Ingest documents

Place your finance PDFs or text files in the `data/` folder, then run:

```bash
python ingest.py
```

This builds the FAISS vector index used for retrieval.

### 5. Run the Streamlit app

```bash
streamlit run app.py
```

---

## Running the React Frontend

```bash
cd frontend
npm install
npm run dev       # http://localhost:3000
```

> The Vite dev server proxies `/api/*` requests to `http://localhost:8000`. Update `vite.config.js` if your backend runs on a different port.

### Connecting the frontend to your backend

In [frontend/src/components/ChatPage.jsx](frontend/src/components/ChatPage.jsx), replace the mock API call with a real fetch:

```js
const res = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question, history: messages }),
})
const data = await res.json()
const answer = data.answer
```

---

## Sample Questions

- What APR can I get with a 750 credit score?
- What is the minimum down payment required?
- Can I pay off my loan early without a penalty?
- What documents do I need to apply?
- How does refinancing work?
