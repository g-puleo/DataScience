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
## qua faccio la prima mappa che plotta solamente il trentino su una carta geografica usanto la libreria contextily
axgrid = grid.plot(color='blue', alpha=0.3) #vediamo che la mappa si plotta decentemente
#sovrappongo mappa del trentino
cx.add_basemap(axgrid, crs=grid.crs.to_string() ) 

#per salvare la figura
#plt.savefig("mappaTrentinoBlu.pdf", bbox_inches='tight' , dpi=300) 


# Adesso plotto una mappa attraverso la funzione genera_mappa_consumi che sta nella libreria funzioni
#La mappa rappresenta i consumi loordi di tutto il mese ed evidenzia le zone a più alto consumo nella zona di trento
gdf_consumi_lordi = fz.genera_mappa_consumi(rawdata.df_consumiraw, rawdata.df_lineeraw, grid) 
MAX = gdf_consumi_lordi['consumo_per_cella'].max()
MIN = gdf_consumi_lordi['consumo_per_cella'].min()
ax_consumi_lordi = gdf_consumi_lordi.plot('consumo_per_cella', cmap='YlOrRd', alpha=0.5) 
cx.add_basemap(ax_consumi_lordi, crs=grid.crs.to_string() )
plt.colorbar(plt.cm.ScalarMappable( norm=ax_consumi_lordi._children[0].norm , cmap='YlOrRd'), ax=ax_consumi_lordi )
ax_consumi_lordi.set_xlim(11.05, 11.20)
ax_consumi_lordi.set_ylim(46.0, 46.15)
#plt.savefig("mappaConsumi1.pdf", bbox_inches='tight' , dpi=300)

# Adesso faccio delle mappe per capire se effettivamente ci sono variazioni di consumo fra 
# giorno e la notte e se quest'ultime correlano con le zone industriali del trentino


df_mappa_giorno = fz.genera_mappa_consumi( consumi.df_consumidiurni, consumi.df_linee , grid )
df_mappa_notte = fz.genera_mappa_consumi( consumi.df_consuminotturni, consumi.df_linee, grid )
#normalizzo i consumi per numero di ore nella giornata
df_mappa_giorno['consumo_per_cella']/=11
df_mappa_notte['consumo_per_cella']/=13
df_mappa_diff = df_mappa_giorno.copy()
df_mappa_diff['consumo_per_cella'] = +df_mappa_giorno['consumo_per_cella'] - df_mappa_notte['consumo_per_cella']

fig, axes = plt.subplots(1,1, figsize=(12,5) ) 
MAX = np.max(np.abs(df_mappa_diff['consumo_per_cella'] )  ) 
norm= plt.Normalize( -MAX, MAX ) 
#bwr: blue white red (in ordine crescente)
df_mappa_diff.plot('consumo_per_cella', cmap='bwr', alpha=0.5, ax = axes, norm=norm) 
df_mappa_diff.plot('consumo_per_cella', cmap='bwr', alpha=0.5, ax = axes, norm=norm) 
cx.add_basemap(axes, crs=grid.crs.to_string() )
cx.add_basemap(axes, crs=grid.crs.to_string() )
axes.set_xlim(10.8, 11.5) 
axes.set_ylim(45.84, 46.2)
#plt.colorbar(plt.cm.ScalarMappable( norm=ax_consumi_lordi._children[0].norm , cmap='bwr'), ax=axes[0] )
plt.colorbar(plt.cm.ScalarMappable( norm=ax_consumi_lordi._children[0].norm , cmap='bwr'), ax=axes )

#plt.savefig("mappaGiornonotte.pdf", bbox_inches='tight' , dpi=300)
plt.show()
