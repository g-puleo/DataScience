from trentodatalib import meteo, consumi

def dummyprint( x, n=20):

	print(x.columns.values)
	print(x.head(n))
	print(x.tail(n))


dfcons =  consumi.df_consumi
dummyprint(dfcons) 
#dummyprint( meteo.meteo_df )