from trentodatalib import meteo, consumi, inquinamento
from trentodatalib import funzioni as fz
from trentodatalib import rawdatabase as rawdata
from trentodatalib import Mappastazionimeteo 
def dummyprint( x, n=20):

	print(x.columns.values)
	print(x.head(n))
	print(x.tail(n))


dfcons =  Mappastazionimeteo.gdfLineCells
#dummyprint(dfcons) 
#dummyprint( meteo.meteo_df )
#quello che restituisce il seguente print è inutile ma era per vedere se riuscivo a dimportare le funzioni 
#dummyprint(categorizza_tempo(dfcons))

#a = fz.genera_mappa_consumi(rawdata.df_consumiraw, rawdata.df_lineeraw, rawdata.grid)
#dummyprint(a)
