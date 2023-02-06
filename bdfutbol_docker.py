from clasificacion_equipos import clasificacion_equipos
from resultados_partidos_docker import resultados_partidos
from resultado_partido_docker import resultado_partido
from datetime import datetime
import pandas as pd
import psycopg2

# Connect to your postgres DB
conn = psycopg2.connect(
                    host="127.0.0.1",
                    port=5440,
                    dbname='my_db_in_docker',
                    user='postgres', 
                    password='mypassword')

# Open a cursor to perform database operations
cur = conn.cursor()


def actualizar_bd_resultados_partidos():
        #alemana#francesa#alemana#italiana#portuguesa#holandesa#brasilera#española
    ligas = ['teng', 'tfra', 'tger', 'tita', 'tpor', 'thol', 'tbra', 't']

    years = range(datetime.now().year, datetime.now().year+1)

    for liga in ligas:
        for year in years:
            url = f'https://www.bdfutbol.com/es/t/{liga}{str(year)}-{str(year+1)[-2:]}.html?tab=results'
            results_data = resultados_partidos(url=url)
            if len(results_data) == 0:
                url = f'https://www.bdfutbol.com/es/t/{liga}{str(year-1)}-{str(year)[-2:]}.html?tab=results'
                results_data = resultados_partidos(url=url)
            print(url)


def update_db_rps(): # actualizar bd de resultados partidos
    # TODO: poner un timer para poder poner no, en caso de que se llegue a 0 en t actualizar db.
    actualizar_bd_rps = input('¿Actualizar base de datos de resultados partidos? (s/n): ').lower()

    if actualizar_bd_rps == 's':
        actualizar_bd_resultados_partidos()
    elif actualizar_bd_rps == 'n':
        pass
    else:
        update_db_rps()


def actualizar_bd_resultado_partido():

    update_db_rps()

    # selección del año para el filtro de la query
    years = list(range(datetime.now().year, datetime.now().year+2))

    # input para escoger la liga a actualizar
    print('Listado de ligas: ')
    cur.execute(f"SELECT DISTINCT(competicion) FROM resultados_partidos WHERE competicion LIKE '%{str(years[0])}-{str(years[1])}%'")
    competencias = [competencia[0] for competencia in cur.fetchall()]

    if len(competencias)==0:
        years = list(range(datetime.now().year-1, datetime.now().year+1))
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


#actualizar_bd_resultado_partido()
update_db_rps()
conn.close()
