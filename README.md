# RAG System with Hono + Hugging Face - TODO Checklist

## 📌 Project Setup
- [x] Create project folder and initialize (npm / pnpm / yarn)
- [x] Install Hono for backend
- [x] Create a basic Hono server and health route
- [x] Add environment configuration (`.env`) and use Zod for validation
- [x] Decide storage method for uploaded files (local disk / MinIO / S3)

---

## 📂 File Upload & Parsing
- [x] Add `/upload` endpoint to accept files (PDF, DOCX, images)
- [x] Save uploaded files to storage (temp + persistent)
- [ ] Extract text from documents:
  - [ ] PDFs → `Unstructured`, `PyMuPDF`, `pdfplumber`
  - [ ] DOCX → `python-docx` or `Unstructured`
  - [ ] TXT → read directly
- [ ] Extract text from images/scanned PDFs → OCR:
  - [ ] Tesseract OCR
  - [ ] EasyOCR
  - [ ] PaddleOCR
- [ ] Normalize text and save as structured `Document` objects with metadata

---

## ✂️ Text Chunking & Metadata
- [ ] Split extracted text into chunks (500-1000 tokens)
- [ ] Add metadata for each chunk:
  - [ ] Source file name
  - [ ] Page number / paragraph id
  - [ ] Chunk index
  - [ ] Character offsets (for highlighting)
- [ ] Store original text mapping for later reference

---

## 🔍 Embeddings & Vector Store
- [ ] Choose open-source embedding model:
  - [ ] `sentence-transformers/all-MiniLM-L6-v2`
  - [ ] `BAAI/bge-base-en`
- [ ] Compute embeddings for each chunk
- [ ] Install vector DB (open-source):
  - [ ] ChromaDB (local dev)
  - [ ] Qdrant (production-ready)
  - [ ] Weaviate (optional)
- [ ] Insert embeddings + metadata into vector DB
- [ ] Validate retrieval by querying sample text

---

## 🤖 LLM Setup (Hugging Face)
- [ ] Choose open-source LLM for inference:
  - [ ] `tiiuae/falcon-7b-instruct`
  - [ ] `mistralai/Mistral-7B-Instruct`
  - [ ] `HuggingFaceH4/zephyr-7b-beta`
- [ ] Run model locally using `transformers` or Hugging Face Inference API
- [ ] Test simple prompts to verify responses

---

## 🔗 Retrieval-Augmented Generation (RAG) Flow
- [ ] Add `/query` endpoint in Hono
- [ ] Generate embedding for user query
- [ ] Retrieve top-k relevant chunks from vector DB
- [ ] Send context + query to LLM
- [ ] Return structured response:
  - [ ] `answer_normal`
  - [ ] `answer_simplified` (ELI10)
  - [ ] `answer_child_friendly` (ELI5)
  - [ ] `summary_short`
  - [ ] `summary_long`
  - [ ] `supporting_snippets` (with file & page info)

---

## 🖍 Highlighting
- [ ] Map retrieved chunks to original text using metadata
- [ ] Compute character offsets for exact highlight
- [ ] Return snippet(s) with highlighted text, file name, page number

---

## 💻 Frontend (Optional / Minimal)
- [ ] File upload component with progress
- [ ] Document list / viewer
- [ ] Chat-like Q&A input + response area
- [ ] Highlight viewer for supporting text
- [ ] Cards for simplified answers & summaries

---

## 🚀 Local Deployment & Testing
- [ ] Dockerize services:
  - [ ] Hono backend
  - [ ] Vector DB (Chroma / Qdrant)
  - [ ] Worker for embedding / text processing
  - [ ] LLM model server
- [ ] Docker Compose for local cluster
- [ ] Test end-to-end flow: upload → extract → embed → query → answer
- [ ] Validate logs and error handling

---

## 🔐 Security & Environment
- [ ] Validate env vars with Zod and fail fast
- [ ] Avoid logging secrets
- [ ] Use `.env.example` and `.env` for dev vs prod
- [ ] Limit file upload size and sanitize input

---

## 📈 Scaling & Future Improvements
- [ ] Add user authentication & per-user document isolation
- [ ] Add background workers for embedding large docs
- [ ] Add caching for frequent queries & summaries
- [ ] GPU inference for LLMs
- [ ] Monitor latency, usage, errors

---

## ⚡ MVP Minimum Flow Checklist
- [ ] Upload single PDF → extract text
- [ ] Split into chunks & embed
- [ ] Insert embeddings into vector DB
- [ ] Query embedding + retrieve top-k
- [ ] Send context + query to LLM
- [ ] Return answer + highlight snippet + simplified answer
