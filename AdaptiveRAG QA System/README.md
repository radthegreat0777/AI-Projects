# Adaptive RAG System for HR Manual (LangGraph)

This document describes an **Adaptive Retrieval-Augmented Generation (RAG)** system implemented using **LangGraph** to answer HR-related questions from an internal **HR Manual PDF**.  
If the local document does not contain a relevant answer, the system automatically falls back to **web search**.

---

## 🧠 Architecture Overview

The system follows an adaptive decision flow:

1. **User Question**
2. **Query Enrichment**
3. **Document Retrieval (Vector Search)**
4. **Relevance Validation**
   - ✅ If relevant → Answer from HR Manual
   - ❌ If not relevant → Web Search + Answer
5. **Final Answer Returned**

This logic is orchestrated using **LangGraph's state-based DAG**.

---

## 🧰 Tech Stack

- **LangGraph** – control flow & decision graph
- **LangChain**
- **OpenAI (ChatOpenAI)** – LLM reasoning & validation
- **Ollama Embeddings** – document embeddings
- **Tavily Search** – web fallback search
- **PyPDFLoader** – PDF ingestion
- **InMemoryVectorStore** – vector similarity search

---

## 📂 Document Ingestion & Indexing

```python
loader = PyPDFLoader("./hr_manual.pdf")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

splits = text_splitter.split_documents(docs)

vector_store = InMemoryVectorStore(embedding=embedding_model)
vector_store.add_documents(splits)
```

- HR manual is split into overlapping chunks
- Stored in-memory for fast similarity search
- Uses `nomic-embed-text` embeddings or you can use `OPENAI Embeddings` by the API KEY

---

## 🧾 State Definition

```python
class RAGState(TypedDict):
    question: str
    enriched_question: str
    context: str
    is_relevant: bool
    web_results: str
    answer: str
```

This shared state is passed between nodes in the graph.

## 🧭 Graph Flow (LangGraph)

```text
START
  ↓
enrich_query
  ↓
retrieve
  ↓
validate
  ├── YES → answer → END
  └── NO  → web_search → web_answer → END
```

This enables **adaptive decision-making** based on document relevance.

---

## 🖥️ CLI Usage

```bash
python adaptive_rag.py
```

```text
Enter your question (or 'exit'): What is the leave policy?
Answer:
Employees are entitled to ...
```

---

## ✅ Key Benefits

- 📄 Uses internal HR manual as primary source
- 🧠 Avoids hallucination via strict validation
- 🌐 Falls back to web only when needed
- 🔁 Modular & extensible LangGraph design

---

## 🚀 Possible Enhancements

- Persistent vector store (FAISS / Chroma)
- Source citations in answers
- Confidence scoring instead of YES/NO
- Multi-document HR knowledge base
- UI integration (Streamlit / Next.js)

---

## 📌 Summary

This Adaptive RAG system ensures **accurate, grounded HR answers** by dynamically choosing between **internal documents** and **web knowledge**, making it ideal for enterprise HR assistants.

---
