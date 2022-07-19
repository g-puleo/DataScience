# questo file serve per generare le mappe iniziali che poi useremo nella presentazione
# di fatto queste mappe servono per avere una idea di come è fatto il territorio 
# vengono utilizzate anche per fare considerazioni qualitative importanti 
import pandas as pd
import geopandas as gpd
from datetime import time, timedelta, datetime, date 
import contextily as cx
import numpy as np
import json
import numpy as np
from pathlib  import Path
import matplotlib.pyplot as plt
import matplotlib as mpl
from shapely.geometry import Polygon, Point
from fiona.crs import from_epsg
import fiona


from trentodatalib import meteo, consumi, inquinamento
from trentodatalib import funzioni as fz
from trentodatalib import rawdatabase as rawdata


grid = rawdata.gridraw

df_mappa_stazioni = meteo.meteo_df[['station', 'geometry']]
#df_mappa_stazioni = df_mappa_stazioni.loc[df_mappa_stazioni.astype(str).drop_duplicates().index]
#df_mappa_stazioni.reset_index(inplace=True)
#df_mappa_stazioni.drop(columns='index', inplace=True)
df_mappa_stazioni = gpd.GeoDataFrame(df_mappa_stazioni, crs='EPSG:4326')
df_mappa_stazioni = df_mappa_stazioni.drop_duplicates().reset_index().drop(columns='index')
axmappastazioni = df_mappa_stazioni.plot(color='blue') 
cx.add_basemap(axmappastazioni, crs=df_mappa_stazioni.crs.to_string() ) 
#grid.plot(ax=axmappastazioni, color='aliceblue', alpha=0.4) 

axmappastazioni.set_xlim(11.0, 11.3)
axmappastazioni.set_ylim(45.9, 46.2)


#plt.savefig("mappaStazionimeteo.pdf", bbox_inches='tight' , dpi=300)





plt.show()
