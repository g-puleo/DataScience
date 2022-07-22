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


'''from trentodatalib import meteo, consumi, inquinamento
from trentodatalib import funzioni as fz'''
from trentodatalib import Mappastazionimeteo as Msm


from pathlib import Path
from trentodatalib import trentopaths as tpath 
from trentodatalib import rawdatabase as rawdata
import json
import pandas as pd
from shapely.geometry import Point
from trentodatalib import funzioni as fz
from trentodatalib import meteo, consumi, inquinamento
df_mappa_stazioni = Msm.df_mappa_stazioni
df_mappa_stazioni = gpd.GeoDataFrame(df_mappa_stazioni, crs='EPSG:4326')
df_mappa_stazioni = df_mappa_stazioni.drop_duplicates().reset_index().drop(columns='index')
axmappastazioni = df_mappa_stazioni.plot(color='blue') 
cx.add_basemap(axmappastazioni, crs=df_mappa_stazioni.crs.to_string() ) 
#grid.plot(ax=axmappastazioni, color='aliceblue', alpha=0.4) 

axmappastazioni.set_xlim(11.0, 11.3)
axmappastazioni.set_ylim(45.9, 46.2)

axmappastazioni.annotate('T0129', (11.13565, 46.08))
axmappastazioni.annotate('T0135', (11.10131, 46.10))
#plt.savefig("mappaStazionimeteo.pdf", bbox_inches='tight' , dpi=300)
gdfLineCells = Msm.gdfLineCells
df_mappa_stazioni.to_crs(epsg=4326, inplace=True)
gdfLineCells.to_crs(epsg=4326, inplace=True)
axprova = gdfLineCells.plot('nearestStation', alpha=1)
df_mappa_stazioni.plot(color='blue', ax=axprova) 
cx.add_basemap(axprova, crs=df_mappa_stazioni.crs.to_string() )


plt.show()
