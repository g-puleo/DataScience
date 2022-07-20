import pandas as pd 

dfTrentoZoneDay = pd.read_pickle("datiTrentoDay.pkl")
print(dfTrentoZoneDay.columns.values)
print(type(dfTrentoZoneDay["geometry_x"][12]))
