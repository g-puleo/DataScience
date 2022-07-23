# Nella prima parte di questo script divido la provincia di Trento in zone riferendole alla stazione meteo più vicina. Abbiamo considerato solo le zone in cui è presente almeno una linea. 
from trentodatalib import consumi, meteo, inquinamento 
from trentodatalib import rawdatabase as rawdata
from trentodatalib import funzioni as fz 
from trentodatalib import Mappastazionimeteo 


import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))




import pandas as pd
import geopandas as gpd
from datetime import time, timedelta, datetime, date
import contextily as cx
import numpy as np
import json
from pathlib  import Path
import matplotlib.pyplot as plt
import matplotlib as mpl
from shapely.geometry import Polygon, Point
from fiona.crs import from_epsg
import fiona
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression

#funzione per sistemare le colonne degli inquinanti 
def aggiusta_float(x):
    '''definisco una funzione per trasformare le stringhe in float e, qualora esse siano 'n.d', trasformarle in NaN'''
    if x=='n.d.':
        return float('NaN')
        
    else:
        return float(x)




df_inquinamentoprov = inquinamento.df_inquinamento.copy()
df_inquinamentoprov['Ora'] = df_inquinamentoprov['Ora'].apply( lambda x: f"{x-1:02d}:00" ) 
df_inquinamentoprov['datetime'] = pd.to_datetime( df_inquinamentoprov['Data']+ df_inquinamentoprov['Ora'],format='%Y-%m-%d%H:%M' )
df_inquinamentoprov = df_inquinamentoprov.drop(columns=['Data','Ora'])
#separo le colonne di diversi inquinanti riferiti a stazioni diverse
df_inquinamentoprov =  df_inquinamentoprov.pivot(index=[ 'Unità di misura', 'datetime'], columns=['Stazione','Inquinante'], values='Valore').reset_index()
#riduco a un solo livello di nomi colonne
df_inquinamentoprov.columns=[' '.join(col).strip() for col in df_inquinamentoprov.columns.values]
#divido in fasce orarie
df_inquinamentoprov=fz.categorizza_tempo(df_inquinamentoprov)
# anche qui sistemo il database in modo da non avere n.d. e trasformarlo in Nan attraverso la funzione aggiusta float 
columns_inquinanti_tot = df_inquinamentoprov.columns[2:18]



for c in columns_inquinanti_tot:

    df_inquinamentoprov[c] = df_inquinamentoprov[c].apply(aggiusta_float)
# anche qui facciamo la media sulle fasce orarie 
df_inquinamentoprov = df_inquinamentoprov.groupby([df_inquinamentoprov['datetime'].dt.date,
                     'Unità di misura', 'TimeRange','isWeekend'])[columns_inquinanti_tot].mean().reset_index()

df_inquinamentoprov.rename(columns={'datetime':'date'}, inplace=True)

#print(df_inquinamentoprov)
# qui inizia una parte da aggiustare perchè devo fare il database dfmeteo_consumi che al momento non ho da nessuna parte 
#  a me interessano i consumi sull'intero territorio non mi interessa quale sia la stazione più vicina in realtà
df_inquinamentoprov = df_inquinamentoprov.groupby( ['date', 'TimeRange', 'isWeekend']).agg(np.nanmean).reset_index()


df_consumi = consumi.df_consumi
meteo_df = meteo.meteo_df
df_meteo_consumi = pd.read_pickle(  os.path.join(os.path.dirname(__file__),"../data/interim/datimeteoconsumi.pkl") )

df_meteo_consumi_tot = df_meteo_consumi.copy()
# voglio solo i dati infrasettimanali 
df_meteo_consumi_tot = df_meteo_consumi_tot[~df_meteo_consumi_tot['isWeekend']]
# voglio ora però i consumi totali di fatto dell'intera provincia di trento 
df_meteo_consumi_tot.drop(['station', 'elevation'], inplace = True, axis = 1)
# ora cercherò di eseguire un groupby 
## df_ubi_per_line = pd.DataFrame(df_linee.groupby('LINESET')['NR_UBICAZIONI'].sum()).reset_index()
colonnedaraggruppare = ['consumoTerritorio', 'meanTemperature','precipitations', 'meanWinds', 'NR_UBICAZIONI','consumoOrarioUbicazione']
#prova = pd.DataFrame(df_meteo_consumi_tot.groupby(['date', 'TimeRange', 'isWeekend'])[colonnedaraggruppare].mean()).reset_index()
# per sicurezza lo faccio anche su df_inquinamentoprov
df_inquinamentoprov = df_inquinamentoprov[~df_inquinamentoprov['isWeekend']]
df_inquinamentoprov = df_inquinamentoprov.groupby( ['date', 'TimeRange', 'isWeekend']).agg(np.nanmean).reset_index()


# in questa cella ho cercato di fare un groupby sui consumi delle tre fasce orarie e sono riuscita
# a dirgli quali colonne sommare e quali invece mediare, purtroppo non riesco a dirglielo in maniera più elegante di così
# è un po' grezzo, ma in qualche modo funziona 
#df = df.groupby(['Symbol']).agg({'Profit': ['sum'], 'Volume': ['sum'], 'Commission': ['sum'], 'Time': pd.Series.mode})
colonnedamediare = tuple(['meanTemperature','precipitations','meanWinds', 'consumoOrarioUbicazione'])
df_meteo_consumi_tot= pd.DataFrame(df_meteo_consumi_tot.groupby(['date', 'TimeRange', 'isWeekend']).agg({'consumoTerritorio' : ['sum'],'NR_UBICAZIONI' : ['sum'] ,'meanTemperature': ['mean'], 'precipitations' : ['mean'], 'meanWinds': ['mean'], 'consumoOrarioUbicazione': ['mean']}))


# tolgo il multindice dalle colonne 
df_meteo_consumi_tot.columns = list(map(''.join, df_meteo_consumi_tot.columns.values))
# resetto l'indice 
df_meteo_consumi_tot = df_meteo_consumi_tot.reset_index()
# ora dovrei essere pronta a fare un merge con il database dell'inquinamento 
df_meteo_consumi_inq_tot = pd.merge( left=df_inquinamentoprov, right=df_meteo_consumi_tot, on=['TimeRange', 'isWeekend', 'date'])


df_giornoprov = df_meteo_consumi_inq_tot[ df_meteo_consumi_inq_tot['TimeRange'] == 'day' ].reset_index().drop(columns='index')
df_seraprov = df_meteo_consumi_inq_tot[ df_meteo_consumi_inq_tot['TimeRange'] == 'evening' ].reset_index().drop(columns='index')

columns_to_drop = ['date_x', 'date_x+1' , 'TimeRange_x', 'isWeekend_x', 'consumoTerritoriosum_x', 'NR_UBICAZIONIsum_x', 'dayOfWeek_x',
                      'TimeRange_x+1', 'isWeekend_x+1', 'consumoTerritoriosum_x+1', 'NR_UBICAZIONIsum_x+1', 'dayOfWeek_x+1']

df_giornoprov = fz.addNextDay(df_giornoprov, columns_to_drop)
df_seraprov = fz.addNextDay(df_seraprov, columns_to_drop)
# questi sono i database per fare la regressione sull'intera provincia di trento, in cui abbiamo i consumi totali e tutti gli inquinanti e una media del meteo 
#print(df_giornoprov.columns.values)
#print(df_seraprov.columns.values)


# adesso devo fare la stessa cosa ma solo con i dati del comune di Trento: 
dfInqTrento = inquinamento.dfInqTrento

dfTrento = df_meteo_consumi[ (df_meteo_consumi['station']=='T0129')
                            & (df_meteo_consumi['isWeekend']==False) ]
dfInqTrento_infraset = dfInqTrento[ ~dfInqTrento['isWeekend'] ]
#e finalmente unisco con dati di meteo e consumi
dfMeteoInqCons = pd.merge( left=dfInqTrento_infraset, right=dfTrento, on=['TimeRange', 'isWeekend', 'date'])

# ora dovrei avere il database con tutti i dati che mi interessano della zona centrale di Trento


df_giornoTN = dfMeteoInqCons[ dfMeteoInqCons['TimeRange'] == 'day' ].reset_index().drop(columns='index')
df_seraTN = dfMeteoInqCons[ dfMeteoInqCons['TimeRange'] == 'evening' ].reset_index().drop(columns='index')

columns_to_drop = ['date_x', 'date_x+1','TimeRange_x', 'isWeekend_x','TimeRange_x+1', 'isWeekend_x+1','consumoTerritorio_x', 'NR_UBICAZIONI_x', 'consumoTerritorio_x+1', 'NR_UBICAZIONI_x+1','dayOfWeek_x','dayOfWeek_x+1']
df_giornoTN = fz.addNextDay(df_giornoTN, columns_to_drop)
df_seraTN = fz.addNextDay(df_seraTN, columns_to_drop)
# questi sono i database per effettuare la regressione sul territorio comunale di Trento 
#print(df_giornoTN.columns.values)
#print(df_seraTN)


#salvo in file esterni usando pickle
df_giornoprov.to_pickle(os.path.join(os.path.dirname(__file__),"../data/processed/datiRegrProvDay.pkl"))
df_seraprov.to_pickle(os.path.join(os.path.dirname(__file__),"../data/processed/datiRegrProvEv.pkl"))
df_giornoTN.to_pickle(os.path.join(os.path.dirname(__file__),"../data/processed/datiRegrComuneDay.pkl"))
df_seraTN.to_pickle(os.path.join(os.path.dirname(__file__),"../data/processed/datiRegrComuneEv.pkl"))
	
	
print(df_inquinamentoprov)
	
	
	
	
	
	
	
	
	

