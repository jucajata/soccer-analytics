from bs4 import BeautifulSoup
import requests
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

from utils_scripts.u_busqueda_competicion import busqueda_competicion

def resultados_partidos(url:str=None):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv_path = os.path.join(BASE_DIR, 'sports/.env')
    load_dotenv(dotenv_path)


    # Connect to your postgres DB
    conn = psycopg2.connect(
                    dbname=os.getenv('POSTGRES_DBNAME'), 
                    user=os.getenv('POSTGRES_USER'), 
                    password=os.getenv('POSTGRES_PASSWORD'))

                

    # Open a cursor to perform database operations
    cur = conn.cursor()
    

    if url is None:
        url = 'https://www.bdfutbol.com/es/t/teng2022-23.html?tab=results'
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html5lib')


    # almacenamiento en df
    table_rows=soup.find_all('tr')
    results_data = pd.DataFrame(columns=["Fecha", "Local", "ResLocal", "ResVisitante", "Visitante", "Estadio", "Árbitro", "LinkDatosPartido", "Competición"])

    for row in table_rows:
        col = row.find_all('td')
        if len(list(col)) == 6 and len(col[0].text) == 10:
            fecha = col[0].text
            local = col[1].text
            try:
                resultado_local = int(col[2].text[0])
                resultado_visitante = int(col[2].text[1])
            except:
                resultado_local = col[2].text[0]
                resultado_visitante = col[2].text[0]
                if resultado_local == '—':
                    resultado_local = None
                if resultado_visitante == '—':
                    resultado_visitante = None
            visitante = col[3].text
            estadio = col[4].text
            arbitro = col[5].text
            try:
                link_datos_partido = 'https://www.bdfutbol.com/es' + col[1].a['href'][2:]
            except:
                link_datos_partido = None
            competicion = busqueda_competicion(url=url)

            row_data = pd.DataFrame({
                "Fecha":fecha, 
                "Local":local, 
                "ResLocal":resultado_local, 
                "ResVisitante":resultado_visitante, 
                "Visitante":visitante, 
                "Estadio":estadio,
                "Árbitro":arbitro,
                "LinkDatosPartido":link_datos_partido,
                "Competición":competicion,
                }.values()).T

            row_data.columns = ["Fecha", "Local", "ResLocal", "ResVisitante", "Visitante", "Estadio", "Árbitro", "LinkDatosPartido", "Competición"]
            results_data = pd.concat([results_data, row_data], ignore_index=True)

            if link_datos_partido is None: #si está en None no se puede guardar en base de datos por ser primary key
                continue

            sql = "INSERT INTO resultados_partidos (fecha, equipo_local, resultado_local, resultado_visitante, equipo_visitante, estadio, arbitro, link_datos_partido, competicion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (fecha, local, resultado_local, resultado_visitante, visitante, estadio, arbitro, link_datos_partido, competicion)
            try:  # identificamos si ya existe en la bd
                cur.execute(sql, val)
                conn.commit()
            except:
                continue

    conn.close()

    return results_data


#TODO: ¿Qué hacer con los partidos donde hay más de 10 goles?