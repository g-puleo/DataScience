from pathlib import Path
from trentodatalib import trentopaths as tpath
from trentodatalib import rawdatabase as rawdata
import pandas as pd
import geopandas as gpd
import json
from fiona.crs import from_epsg
from shapely.geometry import Polygon, Point
from trentodatalib import funzioni as fz
'''
current_path = Path(__file__).parent.resolve()
df_linee =  pd.read_csv(current_path / tpath.raw_data_path / tpath.filenames['SET-lines'])
nomi = ['LINESET', 'time', 'consumi']
df_nov   =  pd.read_csv(current_path / tpath.raw_data_path / tpath.filenames['NOV-DATA' ], names = nomi)
df_dec   =  pd.read_csv(current_path / tpath.raw_data_path / tpath.filenames['DEC-DATA' ], names = nomi)

#unisco dati 
df_consumi = pd.concat([df_nov, df_dec])
#converto colonna time nel formato di pandas
df_consumi['time'] = pd.to_datetime(df_consumi['time'], format='%Y-%m-%d %H:%M')
df_consumi.rename(columns={'time':'datetime'}, inplace=True) 
################'''
#contiamo le ubicazioni per linea
df_linee = rawdata.df_lineeraw.copy()
df_consumi = rawdata.df_consumiraw.copy()
df_ubi_per_linea = pd.DataFrame(df_linee.groupby('LINESET')['NR_UBICAZIONI'].sum()).reset_index()
df_consumi = pd.merge(left=df_consumi , right=df_ubi_per_linea, on='LINESET', how='left')
#a questo punto le righe di df_consumi corrispondono solo alle linee che hanno avuto dei consumi cioè le linee
# che appaiono nel dataframe di consumi iniziale 
df_consumi.rename(columns={'NR_UBICAZIONI':'TOT_UBICAZIONI'}, inplace=True ) 
#poiché esistono linee nel df_linee dove non sono registrati consumi in df_consumi,
#questo mi da dei nan che decido di ignorare completamente
df_consumi = pd.merge(left=df_consumi, right=df_linee, on='LINESET', how='outer').dropna()
#per ogni cella sommo i consumi di tutte le linee che vi passano
df_consumi['consumo_della_cella'] = df_consumi['consumi']/df_consumi['TOT_UBICAZIONI']*df_consumi['NR_UBICAZIONI']
df_consumi=df_consumi.groupby([ 'SQUAREID','datetime','NR_UBICAZIONI'])['consumo_della_cella'].sum().reset_index()




##importo anche la griglia 
'''with open(current_path / tpath.raw_data_path / tpath.filenames['grid']) as f:
	grid_json=json.load(f)

grid = gpd.GeoDataFrame(grid_json['features'])

#converto la colonna geometry nel formato Polygon di shapely
grid['geometry'] = grid['geometry'].apply(lambda x:Polygon(x['coordinates'][0]))

#### Questa parte imposta il crs del geoDataFrame ######
# Import specific function 'from_epsg' from fiona module

# Set the GeoDataFrame's coordinate system to WGS84
grid.crs = from_epsg(code = 4326)

grid['id'] = grid['properties'].apply(lambda x: x['cellId'])
grid.drop(columns=['type', 'properties'], inplace=True) 
'''
#del df_ubi_per_linea, df_nov, df_dec
