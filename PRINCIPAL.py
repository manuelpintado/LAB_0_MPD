# -- ------------------------------------------------------------------------------------ -- #
# -- Proyecto: Repaso de python 3 y analisis de precios OHLC                              -- #
# -- Codigo: principal.py - script principal de proyecto                                  -- #
# -- Rep: https://github.com/ITESOIF/MyST/tree/master/Notas_Python/Notas_RepasoPython     -- #
# -- Autor: Francisco ME                                                                  -- #
# -- ------------------------------------------------------------------------------------ -- #

# -- ------------------------------------------------------------- Importar con funciones -- #

import funciones as fn  # Para procesamiento de datos
import visualizaciones as vs  # Para visualizacion de datos
import pandas as pd  # Procesamiento de datos
from datos import token as OA_Ak  # Importar token para API de OANDA
import plotly.graph_objects as go

# -- --------------------------------------------------------- Descargar precios de OANDA -- #

# token de OANDA
OA_In = "EUR_USD"  # Instrumento
OA_Gn = "H4"  # Granularidad de velas
fini = pd.to_datetime("2018-07-06 00:00:00").tz_localize('GMT')  # Fecha inicial
ffin = pd.to_datetime("2019-12-06 00:00:00").tz_localize('GMT')  # Fecha final

# Descargar precios masivos
df_pe = fn.f_precios_masivos(p0_fini=fini, p1_ffin=ffin, p2_gran=OA_Gn,
                             p3_inst=OA_In, p4_oatk=OA_Ak, p5_ginc=4900)

# -- --------------------------------------------------------------- Graficar OHLC plotly -- #

vs_grafica1 = vs.g_velas(p0_de=df_pe.iloc[0:120, :])
vs_grafica1.show()

# -- ------------------------------------------------------------------- Conteno de velas -- #

# multiplicador de precios
pip_mult = 10000

# -- 0A.1: Hora
df_pe['hora'] = [df_pe['TimeStamp'][i].hour for i in range(0, len(df_pe['TimeStamp']))]
df_pe['hora'].astype(int)

# -- 0A.2: Dia de la semana.
df_pe['dia'] = [df_pe['TimeStamp'][i].weekday() for i in range(0, len(df_pe['TimeStamp']))]

# -- 0B: Boxplot de amplitud de velas (close - open).
df_pe['co'] = (df_pe['Close'] - df_pe['Open']) * pip_mult

# -- ------------------------------------------------------------ Graficar Boxplot plotly -- #
vs_grafica2 = vs.g_boxplot_varios(p0_data=df_pe[['co']], p1_norm=False)
vs_grafica2.show()

# -- 01: (1pt) ['mes'] : Mes en el que ocurrió la vela.
df_pe['mes'] = [df_pe['TimeStamp'][i].month for i in range(0, len(df_pe['TimeStamp']))]

# -- 02: (1pt) ['sesion'] : Sesion de la vela
"""
'asia':  si en la columna ['hora'] tiene alguno de estos valores -> 22, 23, 0, 1, 2, 3, 4, 5, 6, 7
'asia_europa': si en la columna ['hora'] tiene alguno de estos valores -> 8
'europa': si en la columna ['hora'] tiene alguno de estos valores -> 9, 10, 11, 12 
'europa_america': si en la columna ['hora'] tiene alguno de estos valores -> 13, 14, 15, 16
'america': si en la columna ['hora'] tiene alguno de estos valores -> 17, 18, 19, 20, 21
"""

# Condiciones para encontrat la sesion de la vela en base a la hora del movimiento con tupla (condicion, respuesta)
conditions = [(lambda i: i == 22 or i == 23 or i == 0 or i == 1 or i == 2 or i == 3 or i == 4 or i == 5 or i == 6 or
                         i == 7, 'asia'),
              (lambda i: i == 8, 'asia_europa'),
              (lambda i: i == 9 or i == 10 or i == 11 or i == 12, 'europa'),
              (lambda i: i == 13 or i == 14 or i == 15 or i == 16, 'europa_america'),
              (lambda i: i == 17 or i == 18 or i == 19 or i == 20 or i == 21, 'america')]


# Funcion para iterar la lista de horas con la tupla de condiciones y respuestas
def apply_conditions(i):
    for condition, replacement in conditions:
        if condition(i):
            return replacement
    return i


# Asignar la sesion en base a la funcion
df_pe['sesion'] = list(map(apply_conditions, df_pe['hora']))

# -- 03: (1pt) ['oc']: Amplitud de vela (en pips).
"""
Calcular la diferencia entre las columnas ['Open'] y ['Close'], expresarla en pips.
"""
df_pe['oc'] = (df_pe['Open'] - df_pe['Close']) * pip_mult

# -- 04: (1pt) ['hl']: Amplitud de extremos (en pips).
"""
Calcular la diferencia entre las columnas ['High'] y ['Low'], expresarla en pips.
"""
df_pe['hl'] = (df_pe['High'] - df_pe['Low']) * pip_mult

# -- 05: (.5pt) ['sentido'] : Sentido de la vela (alcista o bajista)
"""
En esta columna debes de asignarle el valor de 'alcista' para cuando ['Close'] >= ['Open'] y 'bajista' 
en el caso contrario.
"""
df_pe['sentido'] = ["alcista" if df_pe['Close'][i] >= df_pe['Open'][i] else "bajista"
                      for i in range(0, len(df_pe['Close']))]

# -- 06: (.5pt) ['sentido_c'] Conteo de velas consecutivas alcistas/bajistas.
"""
En el DataFrame de los precios OHLC, para cada renglon, ir acumulando el valor de velas consecutivas ALCISTAS o BAJISTAS
e ir haciendo el conteo de ocurrencia para cada caso. Se comienza el conteo a partir de la primera repetición, por 
ejemplo, ['sentido_c'] tendrá un 2  en el tiempo t cuando en el tiempo t-2 y tiempo t-1 haya sido el mismo valor que en 
el tiempo t. En este ejemplo ['sentido_c'] tendría un 2 (en el tiempo t-2 fue la primera vela, y la vela en tiempo t-1 
y en tiempo t fueron 2 velas fueron consecutivamente en el mismo sentido).
"""

# -- 07: (1pt) Ventanas móviles de volatilidad
"""
Utiliza la columna de ['hl'] como una medida de "volatilidad" en pips de las velas. Con esta columna, genera las 
siguientes columnas haciendo una "ventana móvil" del máximo de esos últimos n valores. Las columnas serán 3, una para 
cada valor de la "volatilidad móvil" para 5, 25 y 50 velas de histórico respectivamente.

* ['volatilidad_5']: Utilizando la información de las 5 anteriores velas.
* ['volatilidad_25']: Utilizando la información de las 25 anteriores velas.
* ['volatilidad_50']: Utilizando la información de las 50 anteriores velas.

Recuerda que la "volatilidad" en una serie de tiempo financiera es, usualmente, la desviación estándar de los 
rendimientos, sin embargo, uno puede proponer otros "estadísticos" para representar la "variabilidad" entre los datos. 
En este caso, probaremos generar esta información sólo tomando en cuenta la columna ['hl']. Así que, no es necesario 
calcular rendimientos en esta ocasión.
"""
x = df_pe.columns.get_loc('hl')
df_pe['variabilidad_5'] = df_pe.iloc[:, x].rolling(window=5).mean()
df_pe['variabilidad_25'] = df_pe.iloc[:, x].rolling(window=25).mean()
df_pe['variabilidad_50'] = df_pe.iloc[:, x].rolling(window=50).mean()

# -- 08: (1pt) Gráfica con Plotly
"""
Realiza una propuesta de gráfica utilizando alguna de las columnas que has generado y la librería plotly. 
Las reglas son las siguientes:
1. Tiene que tener título de gráfica
2. Tiene que tener título de eje x y etiquetas de eje x
3. Tiene que tener título de eje y y etiquetas de eje y
4. Se debe de poder visualizar una leyenda (en cualquier posición).
"""

vs_grafica3 = go.Figure()
vs_grafica3.add_trace(go.Scatter(x=df_pe['TimeStamp'], y=df_pe['variabilidad_5'], name="MA 5"))
vs_grafica3.add_trace(go.Scatter(x=df_pe['TimeStamp'], y=df_pe['variabilidad_25'], name="MA 25"))
vs_grafica3.add_trace(go.Scatter(x=df_pe['TimeStamp'], y=df_pe['variabilidad_50'], name="MA 50"))
vs_grafica3.update_layout(title={'text': "Moving Average Variabilidad HighLow",
                                 'y': 0.9,
                                 'x': 0.5,
                                 'xanchor': 'center',
                                 'yanchor': 'middle'},
                          xaxis_title="Fecha", yaxis_title="Pips",
                          font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"))
vs_grafica3.show()
