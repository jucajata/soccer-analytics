from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import date, datetime

url = 'https://www.bdfutbol.com/es/t/teng2021-22.html?tab=results'
data = requests.get(url).text
soup = BeautifulSoup(data, 'html5lib')

table_rows=soup.find_all('tr')
for i,row in enumerate(table_rows):
    cells=row.find_all('td')      
    if len(list(cells))==6:
        print("row",i)  
        for j,cell in enumerate(cells):
            print('column',j,"cell",cell.text)