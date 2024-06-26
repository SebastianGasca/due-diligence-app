# backend/routers/news.py

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from pydantic import BaseModel
from datetime import date, datetime, timedelta
from backend.services.utils import web_scrapping_st, palabras_en_noticias, resumir_noticias_bert2bert_st
import pandas as pd

router = APIRouter()

class NewsRequest(BaseModel):
    company: str
    start_date: date
    end_date: date
    keywords: List[str]

@router.post("/scrape")
async def scrape_news(request: NewsRequest):
    news_data = []
    for noticia, progress in web_scrapping_st(request.company, request.start_date, request.end_date):
        news_data.append(noticia)
    noticias = pd.concat(news_data)
    noticias = palabras_en_noticias(noticias, request.keywords)
    return noticias.to_dict(orient="records")

@router.post("/summarize")
async def summarize_news(noticias: List[dict], request: Request):
    df_noticias = pd.DataFrame(noticias)
    model = request.app.state.model
    tokenizer = request.app.state.tokenizer
    summarized_news = resumir_noticias_bert2bert_st(df_noticias, model, tokenizer)
    return summarized_news.to_dict(orient="records")