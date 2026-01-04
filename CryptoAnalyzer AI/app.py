import json
import os
from http.client import HTTPException
from json import JSONDecodeError
from typing import List

import requests
import starlette.exceptions
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import ValidationError
from starlette import status,exceptions

from models import CryptoAnalysisRequest, CryptoCompareRequest, CryptoAnalysisResponse, CoinMarketAnalysis, CryptoInsights, MarketFactor, CryptoComparisonResponse

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_URL = os.getenv("OPENROUTER_URL")
COINGECKO_URL = os.getenv("COINGECKO_URL")
#constants usually wrote in uppercase

app = FastAPI(title="Crypto Analysis AI Tool")

def get_crypto_insights(coin_list: List[str]):

    params = {
        "ids" : ",".join(coin_list),
        "vs_currency" : "usd"
    }
    response = requests.get(COINGECKO_URL, params=params)

    return response.json()




System_Prompt_Analysis = """

You are a "CryptoAnalyst AI" - A Professional Crypto Market Analyst
You will be given recent market data for several crypto currencies(price, market_cap, volume, 24h change)
Your job is to produce a structured analysis with a valid JSON Schema

Rules:
- Return One Analysis per coin
- Follow the exact JSON Schema
{
"analysis" : [
    { "coin" : "< coin name >",
      "summary" : "< 2-3 line summary >",
      "sentiment" : "bullish" | "neutral" | "bearish",
      "key_factors" : [
      {"factor" : "<factor name>" , "impact" : "<impact details>"}
      ],
      "insights" : [
      {"prediction" : "<short-term prediction>", "confidence" : <0-100>}
      ]
    }
]
}
- Provide 3 key_factors and 3 insights per coin
- Base your reasoning on given metrics 
- Always output only JSON and NO MARKDOWNS, NO EXPLANATIONS
- CRITICAL INSTRUCTIONS - You MUST output only VALID JSON*, not inside quotes, not inside markdowns, not as a string.
- Do not add explanations , greetings
- The JSON MUST directly begin with { and end with }
"""

System_Prompt_Compare = """

You are a "CryptoAnalyst AI" - A Professional Crypto Market Analyst
You will be given recent market data for several crypto currencies(price, market_cap, volume, 24h change)
Your job is to produce a structured analysis with a valid JSON Schema

Rules:
- Return One Analysis per coin
- Follow the exact JSON Schema
{
"comparison" : {
    "winner" :"<coin name with strongest outlook>"
    "summary" : "<1-2 sentence of human style summary of why>"
    "reasons" : [
    "<reason1>",
    "<reason2>",
    "<reason3>"
    ]
}
}
- Provide 3 key_factors and 3 insights per coin
- Base your reasoning on given metrics 
- Always output only JSON and NO MARKDOWNS, NO EXPLANATIONS
- CRITICAL INSTRUCTIONS - You MUST output only VALID JSON*, not inside quotes, not inside markdowns, not as a string.
- Do not add explanations , greetings
- The JSON MUST directly begin with { and end with }
"""

def call_openrouter_api(market_data,  system_prompt, request_type: str = "analyze"):

    header = {
        "Authorization" : f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type" : "application/json"
    }

    body = {
        "model" : "meta-llama/llama-3.3-70b-instruct:free",
        "messages" : [
            {
                "role" : "system",
                "content" : system_prompt
            },
            {
                "role" : "user",
                "content" : f" Here is the market data - {json.dumps(market_data, indent=2)} "
            }
        ]

    }

    llm_response = requests.post(OPENROUTER_URL, json=body, headers = header)
    llm_response_json  = llm_response.json()

    json_str = llm_response_json["choices"][0]["message"]["content"]

    try:
        payload = json.loads(json_str)
    except JSONDecodeError as e:
        raise starlette.exceptions.HTTPException(status_code=502, detail= "LLM did not return a valid JSON")

    try:
        if request_type == "analyze":
            return CryptoAnalysisResponse.model_validate(payload)
        else:
            return CryptoComparisonResponse.model_validate(payload)

    except ValidationError as e:
        raise starlette.exceptions.HTTPException(status_code=502, detail= f"LLM JSON Validation Failed - {str(e)}")


@app.post("/crypto/analyze")
def crypto_analysis(request: CryptoAnalysisRequest):

    crypto_data = get_crypto_insights(request.coins)

    market_data = [{
        "name" : data["name"],
        "symbol" : data["symbol"],
        "current_price" : data["current_price"],
        "market_cap" : data["market_cap"],
        "total_volume" : data["total_volume"],
        "price_change_percentage_24h" : data["price_change_percentage_24h"]
    } for data in crypto_data]
    return call_openrouter_api(market_data, system_prompt=System_Prompt_Analysis, request_type="analyze")


@app.post("/crypto/compare")
def crypto_compare(request: CryptoCompareRequest):
    crypto_data = get_crypto_insights(request.coins)

    market_data = [{
        "name": data["name"],
        "symbol": data["symbol"],
        "current_price": data["current_price"],
        "market_cap": data["market_cap"],
        "total_volume": data["total_volume"],
        "price_change_percentage_24h": data["price_change_percentage_24h"]
    } for data in crypto_data]

    return call_openrouter_api(market_data=market_data, system_prompt=System_Prompt_Compare, request_type= "compare")


