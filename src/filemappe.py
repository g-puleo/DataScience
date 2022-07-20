# questo file serve per generare varie mappe da usare nella presentazione
# permette di avere una idea di come si distribuiscono i consumi sul territorio 

import pandas as pd
import geopandas as gpd
import numpy as np
from datetime import time, timedelta, datetime, date 
import contextily as cx
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point


from trentodatalib import meteo, consumi, inquinamento
from trentodatalib import funzioni as fz
from trentodatalib import rawdatabase as rawdata
grid = rawdata.gridraw
# ## qua faccio la prima mappa che plotta solamente il trentino su una carta geografica usanto la libreria contextily
# axgrid = grid.plot(color='blue', alpha=0.3) #vediamo che la mappa si plotta decentemente
# #sovrappongo mappa del trentino
# cx.add_basemap(axgrid, crs=grid.crs.to_string() ) 

# #per salvare la figura
# #plt.savefig("mappaTrentinoBlu.pdf", bbox_inches='tight' , dpi=300) 


# Adesso plotto una mappa attraverso la funzione genera_mappa_consumi che sta nella libreria funzioni
#La mappa rappresenta i consumi lordi di tutto il mese ed evidenzia le zone a più alto consumo nella zona di trento
def plot_mappa_consumi_lordi():
	gdf_consumi_lordi = fz.genera_mappa_consumi(rawdata.df_consumiraw, rawdata.df_lineeraw, grid) 
	MAX = gdf_consumi_lordi['consumo_per_cella'].max()
	MIN = gdf_consumi_lordi['consumo_per_cella'].min()
	ax_consumi_lordi = gdf_consumi_lordi.plot('consumo_per_cella', cmap='YlOrRd', alpha=0.5) 
	cx.add_basemap(ax_consumi_lordi, crs=grid.crs.to_string() )
	plt.colorbar(plt.cm.ScalarMappable( norm=ax_consumi_lordi._children[0].norm , cmap='YlOrRd'), ax=ax_consumi_lordi )
	#zoom sull'area di trento
	ax_consumi_lordi.set_xlim(11.05, 11.20)
	ax_consumi_lordi.set_ylim(46.0, 46.15)
#plt.savefig("mappaConsumi1.pdf", bbox_inches='tight' , dpi=300)

# Adesso faccio delle mappe per capire se effettivamente ci sono variazioni di consumo fra 
# giorno e la notte e se quest'ultime correlano con le zone industriali del trentino

def plot_mappa_diff_giorno_notte():

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


def plot_mappa_diff_wknd():
	# faccio una mappa per vedere la differenza fra i consumi dei giorni infrasettimanali e i week-end

	df_mappa_settimana = fz.genera_mappa_consumi( consumi.df_consumisettimana, consumi.df_linee , grid)
	df_mappa_weekend = fz.genera_mappa_consumi( consumi.df_consumiweekend, consumi.df_linee, grid)
	#normalizzo
	Nset = len(consumi.df_consumisettimana.index)
	Ntot = len(consumi.df_consumi.index)
	df_mappa_settimana['consumo_per_cella']/=Nset*144
	df_mappa_weekend['consumo_per_cella']/=(Ntot-Nset)*144
	# ci sono 144 righe ogni giorno (ogni riga è un quarto d'ora)
	df_mappa_diff2 = df_mappa_settimana.copy()
	df_mappa_diff2['consumo_per_cella'] = df_mappa_settimana['consumo_per_cella']-df_mappa_weekend['consumo_per_cella']
	MAX = np.max(np.abs(df_mappa_diff2['consumo_per_cella'] )  ) 
	norm= plt.Normalize( -MAX, MAX )
	axs_diff2 = df_mappa_diff2.plot('consumo_per_cella', cmap='bwr', alpha=0.5, norm=norm) 
	cx.add_basemap(axs_diff2, crs=grid.crs.to_string() )

	plt.colorbar(plt.cm.ScalarMappable( norm=ax_consumi_lordi._children[0].norm , cmap='bwr'), ax=axs_diff2 )
	axs_diff2.set_xlim(10.8, 11.5) 
	axs_diff2.set_ylim(45.84, 46.2)
#plt.savefig("mappasettimanaweekend.pdf", bbox_inches='tight' , dpi=300)
#plt.show()
