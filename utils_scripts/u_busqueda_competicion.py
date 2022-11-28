

def busqueda_competicion(url:str=None):

    if url is None:
        url = 'https://www.bdfutbol.com/es/t/teng2022-23.html?tab=results'

    competicion = url[30:41]

    # únicamente equipos de primera división masculinos
    x = True
    if competicion[:4] == 'teng':
        liga = 'Premier League'
    elif competicion[:4] == 'tger':
        liga = 'Bundesliga'
    elif competicion[:4] == 'tita':
        liga = 'Serie A'
    elif competicion[:4] == 'tfra':
        liga = 'Ligue 1'
    elif competicion[:4] == 'tpor':
        liga = 'Primeira Liga'
    elif competicion[:4] == 'thol':
        liga = 'Eredivisie'
    elif competicion[:4] == 'tbra':
        liga = 'Brasileirão'
    else:
        x = False
        competicion = url[30:38]
        liga = 'La Liga'

    if x:
        year_i = competicion[4:8]
        year_j = competicion[4:6] + competicion[-2:]
    else:
        year_i = competicion[1:5]
        year_j = competicion[1:3] + competicion[-2:]

    return f'{liga}/{year_i}-{year_j}'