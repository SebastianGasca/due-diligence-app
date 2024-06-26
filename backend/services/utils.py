# backend/services/utils.py

# Aquí puedes reutilizar las funciones ya definidas, asegurándote de importar correctamente las dependencias.
#Generales
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import re
import time
import unicodedata
from pprint import pprint
from tqdm import tqdm
from tqdm.notebook import tqdm_notebook
from collections import defaultdict
import warnings

# #Extracción de noticias
import feedparser
from newspaper import Article
from datetime import datetime, timedelta, date
import urllib.parse

# #Traductor
# from googletrans import Translator

# #Sentimientos y Resumen
from transformers import pipeline
from transformers import AutoModelForMaskedLM, AutoTokenizer
from transformers import BertTokenizerFast, EncoderDecoderModel
from safetensors.torch import load_file
import torch

def web_scrapping_st(company, one_day_ago, now):
    # Tu código existente...
    news_data = []
    total_progress = 0
    
    query = urllib.parse.quote_plus(f"{company} Chile")
    search_url = f"https://news.google.com/rss/search?q={query}&hl=es-419&gl=CL&ceid=CL%3Aes-419"
    
    news_feed = feedparser.parse(search_url)
    df = pd.DataFrame(news_feed.entries)
    df["fecha"] = df.published_parsed.apply(lambda x: date(*x[:3]))
    df_filtrado = df[(df["fecha"] > one_day_ago) & (df["fecha"] < now)]
    
    i = 0
    total_steps = df_filtrado.shape[0]
    for index, row in df_filtrado.iterrows():
        try:
            article = Article(row["link"], language='es')
            article.download()
            article.parse()

            news_data.append({
                'Empresa': company,
                'Título': row.title,
                'Enlace': row.link,
                'Fecha de la noticia': row.fecha,
                'Contenido de la noticia': article.text
            })
            noticia = pd.DataFrame(news_data)
            noticia["Texto completo"] = noticia["Título"] +". "+ noticia["Contenido de la noticia"]
            
        except Exception as e:
            print(f"Error al procesar la noticia: {e}")
        
        i += 1
        total_progress = (i) / total_steps
        
        try: 
            yield noticia, total_progress
        except:
            yield pd.DataFrame([]), total_progress    

def estandarizar_texto(texto):
    texto = texto.lower()     # Convertir a minúsculas
    texto = re.sub(r'[^\w\s]', '', texto)     # Eliminar signos de puntuación utilizando expresiones regulares
    texto = ''.join( (c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn') )     # Eliminar tildes y diacríticos
    return texto

def contar_palabras(documento, palabras_clave):
    contador = 0
    palabras_encontradas = []
    for palabra_clave in palabras_clave:
        palabra_clave = estandarizar_texto(palabra_clave)
        if palabra_clave in documento.split():
            contador += 1
            palabras_encontradas.append(palabra_clave)
    return contador, palabras_encontradas

def palabras_en_noticias(noticias, palabras_clave):
    # Tu código existente...
    tqdm.pandas()
    noticias["Texto estandarizado"] = noticias["Texto completo"].apply(estandarizar_texto)
    
    # Aplicar la función contar_palabras a cada elemento de la columna "Texto estandarizado"
    c , p = zip(*noticias["Texto estandarizado"].progress_apply(lambda x: contar_palabras(x, palabras_clave)))
    noticias["N Palabras Encontradas"], noticias["Palabras Encontradas"] = c , p
    
    print("\n CONTADOR DE PALABRAS COMPLETADO CON ÉXITO")
    return noticias    

def resumir_noticias_bert2bert_st(noticias, model, tokenizer):
    # Tu código existente...
    print("RESUMIENDO NOTICIAS CON -bert2bert-")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    def generate_summary(text):
        inputs = tokenizer([text],
                           padding="max_length",
                           truncation=True,
                           max_length=512,
                           return_tensors="pt")
        input_ids = inputs.input_ids.to(device)
        attention_mask = inputs.attention_mask.to(device)
        output = model.generate(input_ids, attention_mask=attention_mask)
        return tokenizer.decode(output[0], skip_special_tokens=True)
    
    resumenes_noticias = []
    progress_bar = tqdm(total=noticias.shape[0])
    for index, noticia in enumerate(noticias.iterrows()):
        texto = noticia[1]["Texto completo"]
        resumen = generate_summary(texto)
        resumenes_noticias.append(resumen)
        progress_bar.update(1)
    
    noticias["resumen"] = resumenes_noticias    
    return noticias