from bs4 import BeautifulSoup
import requests
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from datetime import date

def resultado_partido(url:str=None):

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


    if url is None:
        url = 'https://www.bdfutbol.com/es/p/p.php?id=668819'
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html5lib')

    equipo_local = soup.find_all("span", {"class": "mr-3"})[0].text
    equipo_visitante = soup.find_all("span", {"class": "ml-3"})[0].text

    datos_partido = soup.find_all("div", {"class": "f13"})
    list_datos = []
    for dato_partido in datos_partido:
        list_datos.append(dato_partido.text)

    d, m, y = list_datos[:4][-1].split()[1].split(sep='/')
    d, m, y = int(d), int(m), int(y)
    fecha = date(y, m, d)

    # almacenamiento en df
    table_rows=soup.find_all('tr')
    results_match_data = pd.DataFrame(columns=[
        "Fecha",
        "Equipo",
        "NumCamiseta", 
        "Jugador", 
        "Acción", 
        "Minuto",
        "MinutoComplementario",
        "Titular",
        "LinkDatosJugador", 
        "LinkDatosPartido"])


    i=-1
    titular=1
    titular_bool=True
    equipo = equipo_local
    for row in table_rows:
        col = row.find_all('td')
        i+=1
        if len(list(col)) == 6 and i>100:
            num_camiseta = int(col[0].text)
            jugador = col[3].text

            for j,cell in enumerate(col):
                try:
                    divisions = cell.find_all('div')
                    for division in divisions:
                        if division['class'][0]=='cosa':
                            accion = division.div['title']
                            minuto = division.text.strip()
                            minuto_complementario = None

                            if len(minuto)>3:
                                if minuto[2] == '+':
                                    minuto_complementario = minuto
                                    minuto = None
                            else:
                                minuto = int(minuto)

                            try:
                                link_datos_jugador = 'https://www.bdfutbol.com/es' + col[3].a['href'][2:]
                            except:
                                link_datos_jugador = None
                            
                            
                            if equipo is None:
                                list_equipos_temporadas = []
                                _data = requests.get(link_datos_jugador).text
                                _soup = BeautifulSoup(_data, 'html5lib')
                                cur.execute(f"SELECT DISTINCT(competicion) FROM resultados_partidos WHERE link_datos_partido='{url}'")
                                # Retrieve query results
                                _records = cur.fetchall()[0][0]
                                tc= _records.split(sep='/')[-1]
                                temporada_competicion = tc[:4] + '-' + tc[-2:]                                

                                # almacenamiento en df
                                _table_rows = list(reversed(_soup.find_all('tr')))
                                for _row in _table_rows:
                                    _col = _row.find_all('td')
                                    try:
                                        _equipo = _col[1].a.text
                                        if _equipo is None or _equipo[0]=='2':
                                            continue
                                        else:
                                            _temporada_equipo = _col[0].text.split()[-1]
                                            list_equipos_temporadas.append((_temporada_equipo, _equipo))
                                    except:
                                        continue

                                
                                for let in list(reversed(list_equipos_temporadas)):
                                    if let[0] == temporada_competicion:
                                        equipo = let[1]

                            link_datos_partido = url
                            
                            row_data = pd.DataFrame({
                                "Fecha":fecha,
                                "Equipo":equipo,
                                "NumCamiseta":num_camiseta, 
                                "Jugador":jugador, 
                                "Acción":accion, 
                                "Minuto":minuto,
                                "MinutoComplementario":minuto_complementario,
                                "Titular":titular_bool,
                                "LinkDatosJugador":link_datos_jugador,
                                "LinkDatosPartido":link_datos_partido,
                                }.values()).T

                            row_data.columns = [
                                "Fecha",
                                "Equipo",
                                "NumCamiseta", 
                                "Jugador", 
                                "Acción", 
                                "Minuto",
                                "MinutoComplementario",
                                "Titular",
                                "LinkDatosJugador", 
                                "LinkDatosPartido"]

                            results_match_data = pd.concat([results_match_data, row_data], ignore_index=True)

                            sql = "INSERT INTO resultado_partido (fecha, equipo, num_camiseta, jugador, accion, minuto, minuto_complementario, titular, link_datos_jugador, link_datos_partido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            val = (fecha, equipo, num_camiseta, jugador, accion, minuto, minuto_complementario, titular_bool, link_datos_jugador, link_datos_partido)
                            query = f'''
                            SELECT * 
                            FROM resultado_partido 
                            WHERE fecha = '{fecha}'
                            AND equipo = '{equipo}'
                            AND num_camiseta = '{num_camiseta}'
                            AND jugador = '{jugador}'
                            AND accion = '{accion}'
                            AND minuto = '{minuto}'
                            AND minuto_complementario = '{minuto_complementario}'
                            AND titular = '{titular_bool}'
                            AND link_datos_jugador = '{link_datos_jugador}'
                            AND link_datos_partido = '{link_datos_partido}';
                            '''

                            if minuto is None or minuto_complementario is None:
                                query = f'''
                                SELECT * 
                                FROM resultado_partido 
                                WHERE fecha = '{fecha}'
                                AND equipo = '{equipo}'
                                AND num_camiseta = '{num_camiseta}'
                                AND jugador = '{jugador}'
                                AND accion = '{accion}'
                                AND titular = '{titular_bool}'
                                AND link_datos_jugador = '{link_datos_jugador}'
                                AND link_datos_partido = '{link_datos_partido}';
                                '''

                            cur.execute(query)
                            r = len(cur.fetchall())
                            if r == 0:
                                cur.execute(sql, val)
                                conn.commit()

                except:
                    accion = None
                    minuto = None
                    minuto_complementario = None
        
                    try:
                        link_datos_jugador = 'https://www.bdfutbol.com/es' + col[3].a['href'][2:]
                    except:
                        link_datos_jugador = None
                    link_datos_partido = url

                
                    if equipo is None:
                        list_equipos_temporadas = []
                        _data = requests.get(link_datos_jugador).text
                        _soup = BeautifulSoup(_data, 'html5lib')
                        cur.execute(f"SELECT DISTINCT(competicion) FROM resultados_partidos WHERE link_datos_partido='{url}'")
                        # Retrieve query results
                        _records = cur.fetchall()[0][0]
                        tc= _records.split(sep='/')[-1]
                        temporada_competicion = tc[:4] + '-' + tc[-2:]                                

                        # almacenamiento en df
                        _table_rows = list(reversed(_soup.find_all('tr')))
                        for _row in _table_rows:
                            _col = _row.find_all('td')
                            try:
                                _equipo = _col[1].a.text
                                if _equipo is None or _equipo[0]=='2':
                                    continue
                                else:
                                    _temporada_equipo = _col[0].text.split()[-1]
                                    list_equipos_temporadas.append((_temporada_equipo, _equipo))
                            except:
                                continue

                        
                        for let in list(reversed(list_equipos_temporadas)):
                            if let[0] == temporada_competicion:
                                equipo = let[1]


                    row_data = pd.DataFrame({
                        "Fecha":fecha,
                        "Equipo":equipo,    
                        "NumCamiseta":num_camiseta, 
                        "Jugador":jugador, 
                        "Acción":accion, 
                        "Minuto":minuto,
                        "MinutoComplementario":minuto_complementario, 
                        "Titular":titular_bool,
                        "LinkDatosJugador":link_datos_jugador,
                        "LinkDatosPartido":link_datos_partido,
                        }.values()).T

                    row_data.columns = [
                        "Fecha",
                        "Equipo",
                        "NumCamiseta", 
                        "Jugador", 
                        "Acción", 
                        "Minuto",
                        "MinutoComplementario",
                        "Titular",
                        "LinkDatosJugador", 
                        "LinkDatosPartido"]

                    results_match_data = pd.concat([results_match_data, row_data], ignore_index=True)

                    sql = "INSERT INTO resultado_partido (fecha, equipo, num_camiseta, jugador, accion, minuto, minuto_complementario, titular, link_datos_jugador, link_datos_partido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (fecha, equipo, num_camiseta, jugador, accion, minuto, minuto_complementario, titular_bool, link_datos_jugador, link_datos_partido)
                    
                    query = f'''
                    SELECT * 
                    FROM resultado_partido 
                    WHERE fecha = '{fecha}'
                    AND equipo = '{equipo}'
                    AND num_camiseta = '{num_camiseta}'
                    AND jugador = '{jugador}'
                    AND accion = '{accion}'
                    AND minuto = '{minuto}'
                    AND minuto_complementario = '{minuto_complementario}'
                    AND titular = '{titular_bool}'
                    AND link_datos_jugador = '{link_datos_jugador}'
                    AND link_datos_partido = '{link_datos_partido}';
                    '''

                    if minuto is None or minuto_complementario is None:
                        query = f'''
                        SELECT * 
                        FROM resultado_partido 
                        WHERE fecha = '{fecha}'
                        AND equipo = '{equipo}'
                        AND num_camiseta = '{num_camiseta}'
                        AND jugador = '{jugador}'
                        AND accion = '{accion}'
                        AND titular = '{titular_bool}'
                        AND link_datos_jugador = '{link_datos_jugador}'
                        AND link_datos_partido = '{link_datos_partido}';
                        '''

                    cur.execute(query)
                    r = len(cur.fetchall())
                    if r == 0:
                        cur.execute(sql, val)
                        conn.commit()
                    
            titular+=1
            if titular > 22:
                titular_bool = False
                equipo=None

            if titular > 11 and titular <= 22:
                equipo = equipo_visitante

    conn.close()
    return results_match_data