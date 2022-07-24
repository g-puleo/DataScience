import pandas as pd
import numpy as np
import geopandas as gpd

#per vedere trentodatalib aggiungo la parent directory al percorso
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from trentodatalib import rawdatabase as rawdata
from trentodatalib import funzioni as fz
from trentodatalib import consumi

#### PARTE 1: DAI DATI RAWDATA SI OTTIENE UN DF CHIAMATO meteo_df, CHE CONTIENE LE SEGUENTI COLONNE:
## STAZIONE, DATA, ORA, VENTO, PRECIPITAZIONI, TEMPERATURA MEDIA (E ALTRI DATI METEO)

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
meteo_df.reset_index(inplace=True, drop=True)
meteo_df = fz.categorizza_tempo(meteo_df)

#funzione ad hoc sistema la colonna vento (ci sono delle stringhe vuote non riconosciute come nan)
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

#medio temperature e venti, sommo le precipitazioni.
meanTempGb  = meteo_df.groupby(['station', meteo_df['datetime'].dt.date,'TimeRange']  )['temperatures'].mean() 
sumPrecipGb = meteo_df.groupby(['station', meteo_df['datetime'].dt.date,'TimeRange']  )['precipitations'].sum() 
meanWindsGb = meteo_df.groupby(['station', meteo_df['datetime'].dt.date,'TimeRange']  )['windSpeed'].mean()

# unisco in un dataframe e rinomino colonne
dicttmp = { 'meanTemperature': meanTempGb, 'precipitations': sumPrecipGb, 'meanWinds': meanWindsGb}
df_tmp_gb = pd.DataFrame(dicttmp).reset_index()
df_tmp_gb.rename(columns={'datetime':'date'} , inplace=True) 

#voglio unirlo con i dati di geometry, e altri dati giornalieri non usati nel groupby
df_tmp_tomerge = meteo_df[['station', 'geometry','elevation', 'minTemperature', 'maxTemperature', 'datetime', 'isWeekend', 'TimeRange']]
#il seguente comando genera una warning ma a quanto pare è un falso positivo. 
#serve a tenere solo le date e a buttare le ore
df_tmp_tomerge['date'] =df_tmp_tomerge['datetime'].dt.date
#togliendo datetime ho un df con un sacco di righe uguali, le butto con .drop_duplicates()
df_tmp_tomerge.drop(columns='datetime', inplace=True)
df_tmp_tomerge  = df_tmp_tomerge.loc[df_tmp_tomerge.astype(str).drop_duplicates().index].reset_index()
df_tmp_tomerge.drop(columns='index', inplace=True)
#finalmente unisco i due dataframe
meteo_df = pd.merge(left=df_tmp_tomerge, right=df_tmp_gb, on=['station', 'date', 'TimeRange'])

meteo_df.to_pickle(os.path.join(os.path.dirname(__file__),"../../data/interim/datiMeteo.pkl"))




#### PARTE 2 : In questa parte creo la mappa delle stazioni
df_mappa_stazioni = meteo_df[['station', 'geometry']]
#la metto in un gdf
df_mappa_stazioni = gpd.GeoDataFrame(df_mappa_stazioni, crs='EPSG:4326')
df_mappa_stazioni = df_mappa_stazioni.drop_duplicates().reset_index().drop(columns='index')

gdfLineCells = pd.merge(left=rawdata.gridraw, right=consumi.df_linee, left_on='id', right_on='SQUAREID', how='right').drop(columns='id')
gdfLineCells[['geometry', 'SQUAREID']].drop_duplicates().reset_index().drop(columns='index')

gdfLineCells.to_crs(epsg=3035, inplace=True)
df_mappa_stazioni.to_crs(epsg=3035, inplace=True)

gdfLineCells['centroid'] = gdfLineCells['geometry'].centroid

#abbasso il livello della programmazione per assocciare ad ogni cella la stazione meteo più vicina
#probabilmente esistono modi più eleganti di farlo, ma questo funziona.

meteo_stations = list(df_mappa_stazioni['geometry']) 
cell_centroids = list(gdfLineCells['centroid'] )

#questo array conterrà gli indici corrispondenti alle stazioni meteo più vicine a ogni centroide
nearest_ms_to_cells = np.zeros( (len(cell_centroids),) ) 
#scorro su tutte le celle del territorio
for i_cell, pt_cell in enumerate(cell_centroids):
    #di default imposto come stazione più vicina la prima dell'elenco
    nearest_index = 0
    #segno anche la sua distanza dal punto centrale della cella i_cell
    nearest_distance = pt_cell.distance(meteo_stations[nearest_index])
    #scorro tutte le stazioni misurando le loro distanze dalla cella i_cell
    for i_st, pt_st in enumerate(meteo_stations):
        current_distance = pt_cell.distance(pt_st)
        #quando trovo una distanza più piccola di tutte quelle che ho visto fin'ora, aggiorno il valore di nearest_distance
        #e segno anche quale stazione corrisponde a questa distanza
        if current_distance <nearest_distance:
            
            nearest_distance=current_distance
            nearest_index = i_st
    
    #fatto il loop sulle stazioni meteo, segno qual è la più vicina
    nearest_ms_to_cells[i_cell] = nearest_index
    stationcodes = df_mappa_stazioni['station'].to_list()

#creo una lista tale che l'i-esimo elemento della lista è il codice della stazione meteo 
#più vicina alla i-esima cella di territorio (nell'ordine in cui appaiono nei dataframe sopra)
codelist = [stationcodes[int(nearest_ms_to_cells[ii])] for ii, p in enumerate(nearest_ms_to_cells)]
gdfLineCells['nearestStation'] = codelist
df_mappa_stazioni.to_crs(epsg=4326, inplace=True)
gdfLineCells.to_crs(epsg=4326, inplace=True)

df_mappa_stazioni.to_pickle( os.path.join(os.path.dirname(__file__),"../../data/interim/mappaStazioni.pkl")  )
gdfLineCells.to_pickle( os.path.join(os.path.dirname(__file__),"../../data/interim/divisioneTerritori.pkl")  )






