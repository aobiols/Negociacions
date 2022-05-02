#########################################################################################
#  PRIMER VIDEO PARA LA OBTENCIÓN DE LOS DATOS DE NEGOCIACION DE LA BOLSA DE MADRID
#  PARTE 1:  Las operaciones tal qual, sin agregar
#########################################################################################

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

url_borsa_madrid = 'https://www.bolsamadrid.es/esp/aspx/Empresas/Negociaciones.aspx?ISIN='
fichero_empresas = 'empresas.json'


if __name__ == '__main__':

    # Cargamos el fichero de JSON de empresas
    empresas = pd.read_json(fichero_empresas)

    # Iteramos para cada una de las empresas
    for index, empresa in empresas.iterrows():

        # Contruimos la URL de la que queremos obtener la información
        url_actual = url_borsa_madrid + empresa['isin']
        ticker = empresa['ticker']
        print("VOY A BUSCAR LA INFO DE " + ticker + '--->' + url_actual)

        # Hacemos la peticion de la pagina de la que queremos obtener la información
        page = requests.get(url_actual)

        # Si la petición es correcta, nos esperaremos 5 segundos, sino salimos del bucle
        if page.status_code == 200:
            time.sleep(5)
            page = requests.get(url_actual)

        if page.status_code != 200:
            break

        # Preparamos el  dataframe donde almacenaremos los datos
        df = []
        siguiente = [1, 2]

        # MIENTRAS NOS QUEDEN PAGINAS A PARSEAR
        while len(siguiente) > 0:

            # Parseamos la pagina web
            soup = BeautifulSoup(page.content, 'html.parser')

            # Para cada una de las Table Rows  (TR) obtenemos los Table Data (TD)
            for fila in soup.find_all('tr', align="right"):
                tds = fila.find_all('td')
                if len(tds) > 5:
                    print('Data: ' + tds[0].text + '---' + tds[1].text + '---' + tds[2].text + '----' + tds[5].text)
                    df_row = [tds[0].text, tds[1].text, tds[2].text, tds[5].text]
                    df.append(df_row)

            #  Buscamos si existe la flecha de Siguiente contenido
            siguiente = soup.find_all('a', id='ctl00_Contenido_SiguientesArr')

            # Cogemos campos para poder hacer un POST y pedir la siguiente página, en caso de que exista

            if len(siguiente) > 0:
                __EVENTTARGET = 'ctl00$Contenido$SiguientesArr'
                __EVENTARGUMENT = ''
                __VIEWSTATE = soup.find('input', id='__VIEWSTATE')['value']
                __VIEWSTATEGENERATOR = soup.find_all('input', id='__VIEWSTATEGENERATOR')[0]['value']
                __EVENTVALIDATION = soup.find_all('input', id='__EVENTVALIDATION')[0]['value']

                payload = {'__EVENTTARGET': __EVENTTARGET, '__EVENTARGUMENT': __EVENTARGUMENT, '__VIEWSTATE': __VIEWSTATE,
                           '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR, '__EVENTVALIDATION': __EVENTVALIDATION}
                page = requests.post(url_actual, data=payload)


        # Ya hemos obtenido todos los datos necesarios para la empresa actual
        # Definimos el nombre de las columnas que hemos obtenido i cambiamos a notación inglesa para PANDAS los números
        # obtenidos para el precio i el volumen

        df_pandas = pd.DataFrame(df, columns=["Hora", "Precio", "Volumen", "Id"])
        df_pandas['Precio'] = pd.to_numeric(df_pandas['Precio'].str.replace(',', '.'), errors='coerce')
        df_pandas['Volumen'] = pd.to_numeric(df_pandas['Volumen'].str.replace('.', ''), errors='coerce')
        df_pandas['Id'] = pd.to_numeric(df_pandas['Id'])

        # Ordenamos segun el ID
        df_pandas = df_pandas.sort_values(by=['Id'])
        df_pandas = df_pandas.reset_index(drop=True)

        dia = df_pandas['Hora'][0].split(" ")[0].replace('/', '_')

        # GENERAMOS FICHERO EXCEL
        with pd.ExcelWriter('RESULTADOS/operaciones_simples_' + ticker + '_' + dia + '.xlsx') as writer:
            df_pandas.to_excel(writer, sheet_name='Todas', engine='xlsxwriter')

