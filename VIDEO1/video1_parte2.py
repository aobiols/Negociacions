#########################################################################################
#  PRIMER VIDEO PARA LA OBTENCIÓN DE LOS DATOS DE NEGOCIACION DE LA BOLSA DE MADRID
#  PARTE 2:  Agregación de  operaciones
#########################################################################################

import math
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

        #  Inicializamos las variables para hacer la agregación de las operaciones
        df_grandes_ops = []
        precio_inicial = 0
        precio_anterior = 0
        suma_volumen = 0
        ultima_hora = df_pandas['Hora'][0]
        operaciones = 0
        operacion_realizada = 'Subhasta Inicial'

        for index_ops, row in df_pandas.iterrows():
            if row['Hora'] == ultima_hora:
                suma_volumen = suma_volumen + row['Volumen']
                precio_anterior = row['Precio']
                operaciones = operaciones + 1
            else:
                if precio_inicial == 0:
                    operacion_realizada = 'Subhasta Inicial'
                elif precio_anterior > precio_inicial:
                    operacion_realizada = 'Compra'
                elif precio_anterior < precio_inicial:
                    operacion_realizada = 'Venta'
                    # Si el precio es el mismo y estabamos comprando suponemos que será una intención de compra
                    # y se estabamos vendiendo será otra venta

                df_row = [operacion_realizada, ultima_hora, precio_anterior, suma_volumen, operaciones]
                operaciones = 1
                precio_inicial = precio_anterior

                # Si es una operacion por bloques mantenemos el precio
                if not math.isnan(row['Precio']):
                    precio_anterior = row['Precio']
                    if 'BLOCS' in operacion_realizada:
                        operacion_realizada = operacion_realizada.split(" ")[0]
                else:
                    operacion_realizada = operacion_realizada + ' BLOQUES'

                suma_volumen = row['Volumen']
                ultima_hora = row['Hora']
                df_grandes_ops.append(df_row)

        # Grabamos la última Iteración
        df_row = ['Subhasta Final', ultima_hora, precio_anterior, suma_volumen, operaciones]
        df_grandes_ops.append(df_row)

        # Hacemos dataframe de agregación de operaciones
        df_pandas_agrega_ops = pd.DataFrame(df_grandes_ops, columns=["Operación", "Hora", "Precio", "Volumen", "Operacionrs"])
        print('ACABO DE AGREGAR LAS OPERACIONES DE ' + ticker)

        dia = df_pandas['Hora'][0].split(" ")[0].replace('/', '_')

        # ESCRIBIM EXCEL
        with pd.ExcelWriter('RESULTADOS/operaciones_' + ticker + '_' + dia + '.xlsx') as writer:
            df_pandas_agrega_ops.to_excel(writer, sheet_name='Resum', engine='xlsxwriter')
            df_pandas.to_excel(writer, sheet_name='Todas', engine='xlsxwriter')

