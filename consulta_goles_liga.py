import os
import pandas as pd

import psycopg2
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, 'soccer-analytics/.env')
load_dotenv(dotenv_path)


def consulta_goles_liga():

    # Connect to your postgres DB
    conn = psycopg2.connect(
                    dbname=os.getenv('POSTGRES_DBNAME'), 
                    user=os.getenv('POSTGRES_USER'), 
                    password=os.getenv('POSTGRES_PASSWORD'))

    # Open a cursor to perform database operations
    cur = conn.cursor()

    cur.execute(f''' SELECT subquery.fecha,
                            subquery.equipo,
                            subquery.jugador,
                            subquery.accion,
                            subquery.minuto,
                            subquery.minuto_complementario,
                            subquery.titular,
                            S.equipo_local,
                            S.resultado_local,
                            S.resultado_visitante,
                            S.equipo_visitante,
                            S.competicion 
                        FROM (SELECT * 
                            FROM resultado_partido
                            WHERE accion IS NOT NULL
                            AND (accion LIKE '%Gol%')
                            ORDER BY link_datos_partido, minuto DESC) AS subquery 
                        INNER JOIN 
                            (SELECT *
                            FROM resultados_partidos) AS S
                        ON subquery.link_datos_partido = S.link_datos_partido;''')

    # Retrieve query results
    data = cur.fetchall()
    df = pd.DataFrame(data, columns=[
        'fecha', 
        'equipo', 
        'jugador', 
        'accion', 
        'minuto', 
        'minuto_complementario', 
        'titular', 
        'equipo_local', 
        'resultado_local', 
        'resultado_visitante', 
        'equipo_visitante', 
        'competicion' ])

    df.to_csv('consulta_goles_liga.csv', index=False)
    print('Datos cargados en el csv')

consulta_goles_liga()