from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import date, datetime


#url = 'https://www.bdfutbol.com/es/p/p.php?id=668827'
#url = 'https://www.bdfutbol.com/es/p/p.php?id=668819'
url = 'https://www.bdfutbol.com/es/p/p.php?id=668894'
#url = 'https://www.bdfutbol.com/es/p/p.php?id=668902'

data = requests.get(url).text
soup = BeautifulSoup(data, 'html5lib')

table_rows=soup.find_all('tr')
for i,row in enumerate(table_rows):

    cells=row.find_all('td')      
    if len(list(cells))==6 and i>100:
        #print("row",i)
        print(cells[3].text)  
        for j,cell in enumerate(cells):
            try:
                divisions = cell.find_all('div')
                for division in divisions:
                    if division['class'][0]=='cosa':
                        print('------------------------>' +division.div['title'], division.text)
            except:
                continue


equipo_local = soup.find_all("span", {"class": "mr-3"})[0].text
equipo_visitante = soup.find_all("span", {"class": "ml-3"})[0].text
print(equipo_local, 'vs', equipo_visitante)

datos_partido = soup.find_all("div", {"class": "f13"})
list_datos = []
for dato_partido in datos_partido:
    list_datos.append(dato_partido.text)

d, m, y = list_datos[:4][-1].split()[1].split(sep='/')
d, m, y = int(d), int(m), int(y)
fecha = date(y, m, d)

print(fecha)    