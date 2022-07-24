# in questo file importiamo i database dalle cartelle data/raw e data/external
# utile per successive elaborazioni
import pandas as pd
import geopandas as gpd
import json
from pathlib  import Path
from shapely.geometry import Polygon, Point
from fiona.crs import from_epsg 
from trentodatalib import funzioni as fz
from trentodatalib import trentopaths as tpath

# estraggo il database riguardante i consumi e il database riguardante le linee 
current_path = Path(__file__).parent.resolve()
df_lineeraw =  pd.read_csv(current_path / tpath.raw_data_path / tpath.filenames['SET-lines'])
nomi = ['LINESET', 'time', 'consumi']
df_nov   =  pd.read_csv(current_path / tpath.raw_data_path / tpath.filenames['NOV-DATA' ], names = nomi)
df_dec   =  pd.read_csv(current_path / tpath.raw_data_path / tpath.filenames['DEC-DATA' ], names = nomi)
#unisco dati 
df_consumiraw = pd.concat([df_nov, df_dec])

# estraggo il database riguardante l'inquinamento 
current_path = Path(__file__).parent.resolve()
with open(current_path/ tpath.raw_data_path / tpath.filenames['meteo'] ) as file:
    dati_meteo_json = json.load(file)

meteo_rawdata = pd.DataFrame(dati_meteo_json['features'])
#convertiamo la colonna geometry nel formato di shapely
meteo_rawdata['geomPoint.geom'] = meteo_rawdata['geomPoint.geom'].apply(lambda x:Point(x['coordinates']) )
meteo_rawdata.rename(columns={'geomPoint.geom':'geometry'} , inplace=True) 
meteo_rawdata = meteo_rawdata.melt( id_vars=meteo_rawdata.columns.values[:10]) 
#aggiusto la colonna degli orari
meteo_rawdata[['variable', 'rawtime']] = meteo_rawdata['variable'].str.split('.', expand=True) 
meteo_rawdata['datetime'] = pd.to_datetime( meteo_rawdata['date']+meteo_rawdata['rawtime'], format='%Y-%m-%d%H%M' ) 
#e butto quelle vecchie
meteo_rawdata.drop(columns=['rawtime','date'], inplace=True)

#Estraggo i dati inquinamento 
df_inquinamentoraw= pd.read_csv(current_path/ tpath.ext_data_path / tpath.filenames['inquinamento'] , encoding='latin-1')

# Estraggo anche la griglia 
with open(current_path / tpath.raw_data_path / tpath.filenames['grid']) as f:
	grid_json=json.load(f)

gridraw = gpd.GeoDataFrame(grid_json['features'])

#converto la colonna geometry nel formato Polygon di shapely
gridraw['geometry'] = gridraw['geometry'].apply(lambda x:Polygon(x['coordinates'][0]))

#### Questa parte imposta il crs del geoDataFrame ######
gridraw.crs = from_epsg(code = 4326)

gridraw['id'] = gridraw['properties'].apply(lambda x: x['cellId'])
gridraw.drop(columns=['type', 'properties'], inplace=True) 

# Estraggo i dati dei comuni, serviranno solo per plot 

dati_comuni = gpd.read_file(current_path/ tpath.ext_data_path / tpath.filenames['comuni'] )
gdf_comuniTN = dati_comuni[ dati_comuni['COD_PROV'] == 22 ].reset_index(drop=True)

