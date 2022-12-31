from clasificacion_equipos import clasificacion_equipos
from resultados_partidos import resultados_partidos
from resultado_partido import resultado_partido
from datetime import datetime
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, 'soccer-analytics/.env')
load_dotenv(dotenv_path)

# Connect to your postgres DB
conn = psycopg2.connect(
                dbname=os.getenv('POSTGRES_DBNAME'), 
                user=os.getenv('POSTGRES_USER'), 
                password=os.getenv('POSTGRES_PASSWORD'))

# Open a cursor to perform database operations
cur = conn.cursor()


def actualizar_bd_resultados_partidos():
        #alemana#francesa#alemana#italiana#portuguesa#holandesa#brasilera#española
    ligas = ['teng', 'tfra', 'tger', 'tita', 'tpor', 'thol', 'tbra', 't']

    try:
        years = range(datetime.now().year, datetime.now().year+1)
    except: # en caso de que la temporada esté en el último año y no en el primero
        years = range(datetime.now().year-1, datetime.now().year)

    for liga in ligas:
        for year in years:
            url = f'https://www.bdfutbol.com/es/t/{liga}{str(year)}-{str(year+1)[-2:]}.html?tab=results'
            resultados_partidos(url=url)
            print(url)


def actualizar_bd_resultado_partido():

    # selección del año para el filtro de la query
    try:
        years = list(range(datetime.now().year, datetime.now().year+2))
    except: # en caso de que la temporada esté en el último año y no en el primero
        years = list(range(datetime.now().year-1, datetime.now().year+1))

    # input para escoger la liga a actualizar
    print('Listado de ligas: ')
    cur.execute(f"SELECT DISTINCT(competicion) FROM resultados_partidos WHERE competicion LIKE '%{str(years[0])}-{str(years[1])}%'")
    competencias = [competencia[0] for competencia in cur.fetchall()]
    i = 1
    for competencia in competencias:
        print(i,': ',competencia)
        i += 1

    liga = competencias[int(input('¿Cuál liga quieres actualizar? (elige el número de la liga): '))-1]
    print(liga)
    
    # Execute a query
    cur.execute(f"SELECT * FROM resultados_partidos WHERE competicion LIKE '%{liga}%'")  # obtengo links con los que voy a actualizar

    # Retrieve query results
    records = cur.fetchall()
    df = pd.DataFrame(records, columns=[
        'Fecha', 
        'Local',
        'Gol local',
        'Gol visitante',
        'Visitante',
        'Estadio',
        'Árbitro',
        'Link Datos Partido',
        'Competición'
        ])
    list_links = list(df['Link Datos Partido'])

    cur.execute(f"SELECT DISTINCT(link_datos_partido) FROM resultado_partido")
    list_links_rp = [item[0] for item in cur.fetchall()]

    for link in list_links:
        if link in list_links_rp:
            continue
        else:
            resultado_partido(url=link)
            print(link)


actualizar_bd_resultado_partido()
conn.close()
