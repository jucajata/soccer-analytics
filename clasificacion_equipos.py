from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import date, datetime


def clasificacion_equipos(url:str=None):

    if url is None:
        url = 'https://www.bdfutbol.com/es/t/teng2022-23.html'

    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html5lib')

    # almacenamiento en df

    # obtención de la jornada actual
    jornadas=soup.find_all('option')
    date_today = datetime.now()
    list_jornadas = []
    for jornada in jornadas:
        primer_palabra = jornada.text.split()[0]
        if primer_palabra == 'Jornada':
            num_jornada = int(jornada.text.split()[1])
            d, m, y = jornada.text.split()[-1][1:-1].split(sep='/')
            d, m, y = int(d), int(m), int(y)
            date_jornada = datetime(y, m, d)
            if date_jornada <= date_today:
                list_jornadas.append((date_jornada, num_jornada))

    ja = list_jornadas[-1][0]
    nj = list_jornadas[-1][1]
    jornada_actual = date(ja.year, ja.month, ja.day)

    table_rows=soup.find_all('tr')
    clasificacion_data = pd.DataFrame(columns=["Posición", "Equipo", "Pts.", "PJ", "PG", "PE", "PP", "GF", "GC", "TA", "TR", "Jornada", "NumJornada"])

    for row in table_rows:
        col = row.find_all('td')
        if len(list(col)) == 13:
            posicion = col[1].text
            equipo = col[3].text
            puntos = col[4].text
            partidos_jugados = col[5].text
            partidos_ganados = col[6].text
            partidos_empatados = col[7].text
            partidos_perdidos = col[8].text
            goles_a_favor = col[9].text
            goles_en_contra = col[10].text
            tarjetas_amarillas = col[11].text
            tarjetas_rojas = col[12].text
            jornada = jornada_actual
            numero_jornada = nj

            row_data = pd.DataFrame({
                "Posición":posicion, 
                "Equipo":equipo, 
                "Pts.":puntos, 
                "PJ":partidos_jugados, 
                "PG":partidos_ganados, 
                "PE":partidos_empatados, 
                "PP":partidos_perdidos, 
                "GF":goles_a_favor, 
                "GC":goles_en_contra, 
                "TA":tarjetas_amarillas, 
                "TR":tarjetas_rojas,
                "Jornada":jornada,
                "NumJornada":numero_jornada,
                }.values()).T

            row_data.columns = ["Posición", "Equipo", "Pts.", "PJ", "PG", "PE", "PP", "GF", "GC", "TA", "TR", "Jornada", "NumJornada"]
            clasificacion_data = pd.concat([clasificacion_data, row_data], ignore_index=True)

    return clasificacion_data