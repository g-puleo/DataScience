from trentodatalib import meteo, consumi
from trentodatalib import funzioni as fz

def dummyprint( x, n=20):

	print(x.columns.values)
	print(x.head(n))
	print(x.tail(n))


dfcons =  consumi.grid
dummyprint(dfcons) 
#dummyprint( meteo.meteo_df )
#quello che restituisce il seguente print è inutile ma era per vedere se riuscivo a dimportare le funzioni 
#dummyprint(categorizza_tempo(dfcons))

a = fz.genera_mappa_consumi(consumi.df_consumi, consumi.df_linee, consumi.grid)
dummyprint(a)