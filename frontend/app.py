import streamlit as st 
import datetime 
import requests
import pandas as pd

#-- HEADER --#
#OPCION 1
st.image("https://upload.wikimedia.org/wikipedia/commons/f/f4/Logo_Sernac_2017.png",  
         width=120)
st.markdown("## Due Diligence :mag_right:")
#-- HEADER --#

st.divider()

#-- FORM --#
with st.form("form_key"):    
    # Empresa
    empresa = st.text_input("Nombre de la compañia", placeholder="Falabella")

    # Fechas
    fecha_inicio = st.date_input("Fecha de Inicio ", datetime.date(2024, 4, 20))
    fecha_termino = st.date_input("Fecha de Termino", datetime.date(2024, 5, 1))

    # Palabras claves
    palabras_claves = st.text_input("Palabras claves", placeholder="colusión, huelga, robo")
    
    # Submit
    submit_btn = st.form_submit_button("Submit")

if empresa:
    st.markdown(f""" 
                La empresa a ser investigada es **{empresa}**
                entre las fechas **{fecha_inicio}** y **{fecha_termino}**.
                Las palabras claves en la busqueda son: **{palabras_claves}**
                """)
#-- FORM --#

st.divider()

#-- DEVOP --#
if submit_btn:
    palabras_claves = palabras_claves.split()
    st.write("Procesando Web Scrapping de Noticias ...")
    
    # Hacer la solicitud a la API para scrapear noticias
    url = "http://127.0.0.1:8000/news/scrape"
    payload = {
        "company": empresa,
        "start_date": str(fecha_inicio),
        "end_date": str(fecha_termino),
        "keywords": palabras_claves
    }

    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        noticias = pd.DataFrame(response.json())
        st.session_state['noticias'] = noticias
        
        st.dataframe(noticias)
    else:
        st.write("Error al procesar las noticias")
        st.write(response.text)

if st.button("Run Model"):
    if 'noticias' in st.session_state:
        noticias = st.session_state['noticias']
        
        # Hacer la solicitud a la API para resumir noticias
        url = "http://127.0.0.1:8000/news/summarize"
        payload = noticias.to_dict(orient="records")

        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            noticias_con_resumen = pd.DataFrame(response.json())
            st.dataframe(noticias_con_resumen)
        else:
            st.write("Error al resumir las noticias")
            st.write(response.text)
    else:
        st.write("No hay datos de noticias disponibles. Por favor, procesa las noticias primero.")
