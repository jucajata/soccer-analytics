import discord
from discord.ext import commands
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
from tabulate import tabulate
from bdfutbol import actualizar_bd_resultados_partidos
from datetime import datetime
from clasificacion_equipos import clasificacion_equipos

def update_db_rps(): # actualizar bd de resultados partidos
    # TODO: poner un timer para poder poner no, en caso de que se llegue a 0 en t actualizar db.
    actualizar_bd_rps = input('¿Actualizar base de datos de resultados partidos? (s/n): ').lower()

    if actualizar_bd_rps == 's':
        actualizar_bd_resultados_partidos()
    elif actualizar_bd_rps == 'n':
        pass
    else:
        update_db_rps()

update_db_rps() # actualizar db

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


def ultimos_cinco_enfrentamientos(local:str, visitante:str):

    # Execute a query
    cur.execute(f"SELECT * FROM resultados_partidos WHERE equipo_local='{local}' AND equipo_visitante='{visitante}' ORDER BY fecha DESC LIMIT 5;")

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
    df.index = df['Fecha']
    df = df.drop(columns=['Fecha', 'Estadio', 'Árbitro', 'Link Datos Partido', 'Competición'])
    return df


def historico_liga_actual(equipo:str=None):

    yi, m = datetime.now().year, datetime.now().month
    yj = yi + 1
    if m < 7:
        yj = yi
        yi = yj-1

    # Execute a query
    cur.execute(f'''
    SELECT * 
    FROM resultados_partidos 
    WHERE (equipo_local='{equipo}' OR equipo_visitante='{equipo}') AND competicion LIKE '%{str(yi)}-{str(yj)}%'
    ORDER BY fecha DESC;''')

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
    df.index = df['Fecha']
    df = df.drop(columns=['Fecha', 'Estadio', 'Árbitro', 'Link Datos Partido', 'Competición'])
    return df


intents = discord.Intents.all() # or .all() if you ticked all, that is easier
intents.members = True # If you ticked the SERVER MEMBERS INTENT

bot = commands.Bot(command_prefix='$$', intents=intents)
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content
  author = message.author
  channel = message.channel

  if msg.startswith('REPORTE'):

    sql = "INSERT INTO solicitudes_reporte (fecha, autor, mensaje, canal) VALUES (%s, %s, %s, %s)"
    val = (datetime.now(), str(author),str(msg), str(channel))
    cur.execute(sql, val)
    conn.commit()

    #msg = 'REPORTE L: Manchester United vs V: Tottenham' <--- EJEMPLO DE QUERY
    msg_split = msg.split()
    pos_vs = msg_split[3]
    if pos_vs != 'vs':
        pos_vs = msg_split[4]
        pos_vs_num = 4
        equipo_local = msg_split[2] + ' ' + msg_split[3] 
        if pos_vs != 'vs':
            pos_vs = msg_split[5]
            pos_vs_num = 5
            equipo_local = msg_split[2] + ' ' + msg_split[3] + ' ' + msg_split[4] 
    else:
        equipo_local = msg_split[2]
        pos_vs_num = 3
    
    if len(msg_split) == pos_vs_num+3:
        equipo_visitante = msg_split[pos_vs_num+2]
    elif len(msg_split) == pos_vs_num+4:
        equipo_visitante = msg_split[pos_vs_num+2] + ' ' + msg_split[pos_vs_num+3]
    else:
        equipo_visitante = msg_split[pos_vs_num+2] + ' ' + msg_split[pos_vs_num+3] + ' ' + msg_split[pos_vs_num+4]

    df = ultimos_cinco_enfrentamientos(local=equipo_local, visitante=equipo_visitante)
    pretty_table = tabulate(df, headers='keys', tablefmt='simple')

    await message.channel.send('Oistes mijo, te traigo un reporte bien cuca...')
    await message.channel.send(f'```Equipo local: {equipo_local} vs Equipo visitante: {equipo_visitante}```')
    await message.channel.send('```1) Últimos 5 partidos en la misma condición de local y visitante:```')
    await message.channel.send(f'```{pretty_table}```')

    # resultado promedio del local
    promedio_local_u5p = round(df['Gol local'].mean(),1)
    promedio_local_u4p = round(df['Gol local'].iloc[:-1].mean(),1)
    promedio_local_u3p = round(df['Gol local'].iloc[:-2].mean(),1)
    promedio_local_u2p = round(df['Gol local'].iloc[:-3].mean(),1)
    await message.channel.send(f'```Goles promedio {equipo_local} últimos (5, 4, 3, 2) partidos como local ante {equipo_visitante}: ({promedio_local_u5p}, {promedio_local_u4p}, {promedio_local_u3p}, {promedio_local_u2p})```')
    
    # victorias del local
    list_local = list(df['Gol local'])
    list_visitante = list(df['Gol visitante'])
    list_victorias_local = []
    list_victorias_visitante = []
    count_local = 0
    count_visitante = 0

    for i in range(1,len(list_local)+1):
        res_local = list_local[-i]
        res_visitante = list_visitante[-i]
        if res_local > res_visitante:
            list_victorias_local.append('✅')
            count_local+=1
            list_victorias_visitante.append('❌')
        elif res_local == res_visitante:
            list_victorias_local.append('⚪')
            list_victorias_visitante.append('⚪')
        else:
            list_victorias_local.append('❌')
            list_victorias_visitante.append('✅')
            count_visitante+=1

    try:
        await message.channel.send(f'```Victorias {equipo_local}: {list_victorias_local} = {count_local}/{len(list_victorias_local)} = {round(count_local*100/len(list_victorias_local),0)}%```')
    except:
        pass

    # resultado promedio del visitante
    promedio_visitante_u5p = round(df['Gol visitante'].mean(),1)
    promedio_visitante_u4p = round(df['Gol visitante'].iloc[:-1].mean(),1)
    promedio_visitante_u3p = round(df['Gol visitante'].iloc[:-2].mean(),1)
    promedio_visitante_u2p = round(df['Gol visitante'].iloc[:-3].mean(),1)
    await message.channel.send(f'```Goles promedio {equipo_visitante} últimos (5, 4, 3, 2) partidos como visitante ante {equipo_local}: ({promedio_visitante_u5p}, {promedio_visitante_u4p}, {promedio_visitante_u3p}, {promedio_visitante_u2p})```')
    
    try:
        await message.channel.send(f'```Victorias {equipo_visitante}: {list_victorias_visitante} = {count_visitante}/{len(list_victorias_visitante)} = {round(count_visitante*100/len(list_victorias_visitante),0)}%```')
    except:
        pass

    df_hla = historico_liga_actual(equipo=equipo_local)
    pretty_table = tabulate(df_hla, headers='keys', tablefmt='simple')

    await message.channel.send(f'```2) Histórico partidos del equipo {equipo_local} en la liga actual:```')
    await message.channel.send(f'```{pretty_table}```')

    df_hla = historico_liga_actual(equipo=equipo_visitante)
    pretty_table = tabulate(df_hla, headers='keys', tablefmt='simple')

    await message.channel.send(f'```3) Histórico partidos del equipo {equipo_visitante} en la liga actual:```')
    await message.channel.send(f'```{pretty_table}```')


  if msg.startswith('PREMIER'):

    sql = "INSERT INTO solicitudes_reporte (fecha, autor, mensaje, canal) VALUES (%s, %s, %s, %s)"
    val = (datetime.now(), str(author),str(msg), str(channel))
    cur.execute(sql, val)
    conn.commit()

    yi, m = datetime.now().year, datetime.now().month
    yj = yi + 1
    if m < 7:
        yj = yi
        yi = yj-1

    yi = str(yi)
    yj = str(yj)[2:]

    df = clasificacion_equipos(url=f'https://www.bdfutbol.com/es/t/teng{yi}-{yj}.html')
    df = df[["Posición", "Equipo", "Pts.", "PJ", "PG", "PE", "PP", "GF", "GC", "TA", "TR"]]
    df.index = df['Posición']
    df = df.drop(columns=['Posición'])
    pretty_table = tabulate(df, headers='keys', tablefmt='simple')

    await message.channel.send(f'```Premier League clasificación equipos {yi}-{yj}:```')
    await message.channel.send(f'```{pretty_table}```')
    #await message.channel.send(f'```{pretty_table[:int(len(pretty_table)/2)]}```')
    #await message.channel.send(f'```{pretty_table[int(len(pretty_table)/2):]}```')


  if msg.startswith('LA LIGA'):

    sql = "INSERT INTO solicitudes_reporte (fecha, autor, mensaje, canal) VALUES (%s, %s, %s, %s)"
    val = (datetime.now(), str(author),str(msg), str(channel))
    cur.execute(sql, val)
    conn.commit()

    yi, m = datetime.now().year, datetime.now().month
    yj = yi + 1
    if m < 7:
        yj = yi
        yi = yj-1

    yi = str(yi)
    yj = str(yj)[2:]

    df = clasificacion_equipos(url=f'https://www.bdfutbol.com/es/t/t{yi}-{yj}.html')
    df = df[["Posición", "Equipo", "Pts.", "PJ", "PG", "PE", "PP", "GF", "GC", "TA", "TR"]]
    df.index = df['Posición']
    df = df.drop(columns=['Posición'])
    pretty_table = tabulate(df, headers='keys', tablefmt='simple')

    await message.channel.send(f'```La Liga clasificación equipos {yi}-{yj}:```')
    await message.channel.send(f'```{pretty_table}```')
    #await message.channel.send(f'```{pretty_table[:int(len(pretty_table)/2)]}```')
    #await message.channel.send(f'```{pretty_table[int(len(pretty_table)/2):]}```')

my_secret = os.getenv('SPORTS_BOT_KEY')
client.run(my_secret)
conn.close()



