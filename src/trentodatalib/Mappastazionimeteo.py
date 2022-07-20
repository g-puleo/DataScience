# questo file serve per generare le mappe iniziali che poi useremo nella presentazione
# di fatto queste mappe servono per avere una idea di come è fatto il territorio 
# vengono utilizzate anche per fare considerazioni qualitative importanti 
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


'''from trentodatalib import meteo, consumi, inquinamento
from trentodatalib import funzioni as fz
from trentodatalib import rawdatabase as rawdata'''


from pathlib import Path
from trentodatalib import trentopaths as tpath 
from trentodatalib import rawdatabase as rawdata
import pandas as pd
from shapely.geometry import Point
from trentodatalib import funzioni as fz
from trentodatalib import meteo, consumi, inquinamento

grid = rawdata.gridraw

df_mappa_stazioni = meteo.meteo_df[['station', 'geometry']]
#df_mappa_stazioni = df_mappa_stazioni.loc[df_mappa_stazioni.astype(str).drop_duplicates().index]
#df_mappa_stazioni.reset_index(inplace=True)
#df_mappa_stazioni.drop(columns='index', inplace=True)
df_mappa_stazioni = gpd.GeoDataFrame(df_mappa_stazioni, crs='EPSG:4326')
df_mappa_stazioni = df_mappa_stazioni.drop_duplicates().reset_index().drop(columns='index')

# axmappastazioni = df_mappa_stazioni.plot(color='blue') 
# cx.add_basemap(axmappastazioni, crs=df_mappa_stazioni.crs.to_string() ) 
# #grid.plot(ax=axmappastazioni, color='aliceblue', alpha=0.4) 

# axmappastazioni.set_xlim(11.0, 11.3)
# axmappastazioni.set_ylim(45.9, 46.2)

# axmappastazioni.annotate('T0129', (11.13565, 46.08))
# axmappastazioni.annotate('T0135', (11.10131, 46.10))



#plt.savefig("mappaStazionimeteo.pdf", bbox_inches='tight' , dpi=300)
## righe preparatorie per fare la mappa 
gdfLineCells = pd.merge(left=rawdata.gridraw, right=consumi.df_linee, left_on='id', right_on='SQUAREID', how='right').drop(columns='id')
gdfLineCells[['geometry', 'SQUAREID']].drop_duplicates().reset_index().drop(columns='index')
#per calcolare il centroide è tecnicamente opportuno trasformare coordinate sferiche in coordinate chilometriche
#anche se non dovrebbe fare molta differenza
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









#questo è un semplice plot di prova
axprova = gdfLineCells.plot('nearestStation', alpha=1)
df_mappa_stazioni.plot(color='blue', ax=axprova) 
cx.add_basemap(axprova, crs=df_mappa_stazioni.crs.to_string() ) 
#per salvare
#plt.savefig('mappaStazioniZone.pdf', dpi=400, bbox_inches='tight') 





#plt.show()





