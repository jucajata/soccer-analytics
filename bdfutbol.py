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

    years = range(datetime.now().year, datetime.now().year+1)

    for liga in ligas:
        for year in years:
            url = f'https://www.bdfutbol.com/es/t/{liga}{str(year)}-{str(year+1)[-2:]}.html?tab=results'
            resultados_partidos(url=url)
            print(url)


def actualizar_bd_resultado_partido():
    
    # Execute a query
    cur.execute(f"SELECT * FROM resultados_partidos WHERE competicion LIKE '%La Liga/2022-2023%'")  # obtengo links con los que voy a actualizar

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
