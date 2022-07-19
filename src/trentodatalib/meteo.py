#importo modulo con percorsi e nomi files
from pathlib import Path
from trentodatalib import trentopaths as tpath 
from trentodatalib import rawdatabase as rawdata
import json
import pandas as pd
from shapely.geometry import Point
from trentodatalib import funzioni as fz
#importo dati meteo 

###Commento la parte che ho salvato in rawdatabase
'''current_path = Path(__file__).parent.resolve()
with open(current_path/ tpath.raw_data_path / tpath.filenames['meteo'] ) as file:
    dati_meteo_json = json.load(file)

meteo_rawdata = pd.DataFrame(dati_meteo_json['features'])
#convertiamo la colonna geometry nel formato di shapely
meteo_rawdata['geomPoint.geom'] = meteo_rawdata['geomPoint.geom'].apply(lambda x:Point(x['coordinates']) )
meteo_rawdata.rename(columns={'geomPoint.geom':'geometry'} , inplace=True) 
meteo_rawdata = meteo_rawdata.melt( id_vars=meteo_rawdata.columns.values[:10]) 
#aggiusto la colonna degli orari
meteo_rawdata[['variable', 'rawtime']] = meteo_rawdata['variable'].str.split('.', expand=True) 
meteo_rawdata['datetime'] = pd.to_datetime( meteo_rawdata['date']+meteo_rawdata['rawtime'], format='%Y-%m-%d%H%M' ) 
#e butto quelle vecchie
meteo_rawdata.drop(columns=['rawtime','date'], inplace=True)
##############'''
#creo un df temporaneo per riorganizzare la colonna con temperature, vento e precipitazioni
temp_df = rawdata.meteo_rawdata[['station', 'datetime', 'variable', 'value']]

#questo pivot() mi permette di ottenere tre distinte colonne con i valori che mi interessano
temp_df = temp_df.pivot(index=['station', 'datetime'], columns='variable', values='value').reset_index() 
#unisco il df con le tre nuove colonne a quello con i dati raw
meteo_df = pd.merge(left=rawdata.meteo_rawdata, right=temp_df, how='right', on=['station', 'datetime'] ) 
meteo_df = meteo_df[meteo_df.variable=='temperatures']
#come ultima cosa separo in due la colonna del vento
meteo_df[['winds', 'windDir']] =  meteo_df['winds'].str.split('@', expand=True)
meteo_df.rename(columns={'winds':'windSpeed'}, inplace=True  ) 
meteo_df.drop(columns=[ 'variable', 'value', 'timestamp' ], inplace=True ) 
#butto le colonne ora inutili
meteo_df.reset_index(inplace=True)
meteo_df.drop(columns='index', inplace=True) 

def adjust_wind( x ):
    if type(x)==str:
        if x=='':
            return float('NaN')
        else:
            return float(x)
    elif type(x)==float:
        return x
    else:
        return float('NaN')

meteo_df[ 'windSpeed' ] = meteo_df[ 'windSpeed' ].apply(adjust_wind)
meteo_df[ 'windDir' ] = meteo_df[ 'windDir' ].apply(adjust_wind)
meteo_df
#del temp_df, dati_meteo_json
