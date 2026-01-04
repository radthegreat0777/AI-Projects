# 🪙 Crypto Analysis AI Tool

A FastAPI-based backend service that uses live cryptocurrency market data and a large language model (via OpenRouter) to generate **structured AI-driven crypto market analysis and comparisons**.

---

## ✨ Features

- 🔍 **Crypto Market Analysis** per coin (sentiment, key factors, predictions)
- ⚖️ **Crypto Comparison** to identify the strongest asset among a group
- 📊 Uses **real-time market data** from CoinGecko
- 🤖 AI-powered insights via **OpenRouter (LLaMA 3.3 70B)**
- ✅ Strict **JSON schema validation** using Pydantic

---

## 🧠 Architecture Overview

```
Client
  │
  ▼
FastAPI Server
  ├── CoinGecko API (Market Data)
  ├── OpenRouter API (LLM Analysis)
  └── Pydantic Models (Validation)
```

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **FastAPI** – API framework
- **Pydantic** – Request & response validation
- **Requests** – HTTP client
- **CoinGecko API** – Crypto market data
- **OpenRouter API** – LLM inference
- **dotenv** – Environment configuration

---

## 📁 Project Structure

```
.
├── crypto.py              # Main FastAPI application
├── models.py              # Pydantic request/response schemas
├── .env                   # Environment variables
└── README.md
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_URL=https://openrouter.ai/api/v1/chat/completions
COINGECKO_URL=https://api.coingecko.com/api/v3/coins/markets
```

---

## 🚀 Running the Server

```bash
pip install -r requirements.txt
uvicorn crypto:app --reload
```

Server will start at:

```
http://127.0.0.1:8000
```

Interactive API docs:

- Swagger UI → `/docs`
- ReDoc → `/redoc`

---

## 📌 API Endpoints

### 🔍 Analyze Cryptocurrencies

**POST** `/crypto/analyze`

#### Request Body
```json
{
  "coins": ["bitcoin", "ethereum", "solana"]
}
```

#### Response (Example)
```json
{
  "analysis": [
    {
      "coin": "Bitcoin",
      "summary": "Market shows steady accumulation...",
      "sentiment": "bullish",
      "key_factors": [
        {"factor": "Volume", "impact": "Rising interest"}
      ],
      "insights": [
        {"prediction": "Short-term breakout", "confidence": 78}
      ]
    }
  ]
}
```

---

### ⚖️ Compare Cryptocurrencies

**POST** `/crypto/compare`

#### Request Body
```json
{
  "coins": ["bitcoin", "ethereum"]
}
```

#### Response (Example)
```json
{
  "comparison": {
    "winner": "Bitcoin",
    "summary": "BTC shows stronger market dominance",
    "reasons": [
      "Higher market cap",
      "Stable volume",
      "Lower volatility"
    ]
  }
}
```

---

## 🧪 Validation & Error Handling

- ✅ AI output **must be valid JSON**
- ❌ Invalid LLM responses return **502 Bad Gateway**
- 📐 Strict schema validation using `model_validate()`

---

## 🔒 Prompt Safety Rules

The system prompts enforce:

- JSON-only output
- No markdown or explanations
- Fixed schema structure
- Per-coin analysis constraints

This guarantees machine-readable and reliable responses.

---

## 📈 Future Improvements

- Async HTTP calls (`httpx`)
- Caching with Redis
- Historical trend analysis
- Frontend dashboard (React / Next.js)
- Multi-timeframe predictions

---

## 📜 License

MIT License

---

## 👨‍💻 Author
Radin Punchihewa 
Built for AI-powered financial intelligence and experimentation with LLM-driven market reasoning.

