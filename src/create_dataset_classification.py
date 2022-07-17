import pandas as pd
import geopandas as gpd
from datetime import time, timedelta, datetime, date
import numpy as np
import json
import numpy as np
from pathlib  import Path
from shapely.geometry import Polygon, Point

#ho cambiato il percorso così da lavorare direttamente nella repo
data_path = Path('.././data/raw')
data_path2 = Path('.././data/external')
files = {'grid':'trentino-grid.geojson',
         'adm_reg':'administrative_regions_Trentino.json',        
         'NOV-DATA':'SET-nov-2013.csv',
         'DEC-DATA':'SET-dec-2013.csv',
         'SET-lines':'line.csv',
         'inquinamento' :  'APPA_inquinamento_aria_Nov_Dec_2013.csv',
         'meteo': 'meteotrentino-weather-station-data.json'
        }


#dati griglia provincia trento
with open(data_path / files['grid']) as f:
    grid_json = json.load(f)

grid = gpd.GeoDataFrame(grid_json['features'])

#consumi sulle linee e dati geografici linee
nomi = ['LINESET', 'time', 'consumi']
df_consumi = pd.read_csv(data_path / files['NOV-DATA'], names = nomi)
df_linee = pd.read_csv(data_path / files['SET-lines'])

#dati meteo
with open(data_path / files['meteo'] ) as file:
    dati_meteo_json = json.load(file)

#converto la colonna geometry nel formato Polygon di shapely
grid['geometry'] = grid['geometry'].apply(lambda x:Polygon(x['coordinates'][0]))

#### Questa parte imposta il crs del geoDataFrame ######
# Import specific function 'from_epsg' from fiona module
from fiona.crs import from_epsg
# Set the GeoDataFrame's coordinate system to WGS84
grid.crs = from_epsg(code = 4326)

grid['id'] = grid['properties'].apply(lambda x: x['cellId'])
grid.drop(columns=['type', 'properties'], inplace=True) 




############ IMPORTAZIONE DATI METEO ####################
meteo_rawdata = pd.DataFrame(dati_meteo_json['features'])
#convertiamo la colonna geometry nel formato di shapely
meteo_rawdata['geomPoint.geom'] = meteo_rawdata['geomPoint.geom'].apply(lambda x:Point(x['coordinates']) )
meteo_rawdata.rename(columns={'geomPoint.geom':'geometry'} , inplace=True) 
columnlist = meteo_rawdata.columns.tolist()
meteo_rawdata = meteo_rawdata.melt( id_vars=columnlist[:10]) 
#aggiusto la colonna degli orari
meteo_rawdata[['variable', 'rawtime']] = meteo_rawdata['variable'].str.split('.', expand=True) 
meteo_rawdata['datetime'] = pd.to_datetime( meteo_rawdata['date']+meteo_rawdata['rawtime'], format='%Y-%m-%d%H%M' ) 
#e butto quelle vecchie
meteo_rawdata.drop(columns=['rawtime','date'], inplace=True)
#creo un df temporaneo per riorganizzare la colonna con temperature, vento e precipitazioni
temp_df = meteo_rawdata[['station', 'datetime', 'variable', 'value']]

#questo pivot() mi permette di ottenere tre distinte colonne con i valori che mi interessano
temp_df = temp_df.pivot(index=['station', 'datetime'], columns='variable', values='value').reset_index() 
#unisco il df con le tre nuove colonne a quello con i dati raw
meteo_df = pd.merge(left=meteo_rawdata, right=temp_df, how='right', on=['station', 'datetime'] ) 
meteo_df = meteo_df[meteo_df.variable=='temperatures']
#come ultima cosa separo in due la colonna del vento
meteo_df[['winds', 'windDir']] =  meteo_df['winds'].str.split('@', expand=True)
meteo_df.rename(columns={'winds':'windSpeed'}, inplace=True  ) 
meteo_df.drop(columns=[ 'variable', 'value', 'timestamp' ], inplace=True ) 
#butto le colonne ora inutili
meteo_df.reset_index(inplace=True)
meteo_df.drop(columns='index', inplace=True) 



df_mappa_stazioni = meteo_df[['station', 'geometry']]
#df_mappa_stazioni = df_mappa_stazioni.loc[df_mappa_stazioni.astype(str).drop_duplicates().index]
#df_mappa_stazioni.reset_index(inplace=True)
#df_mappa_stazioni.drop(columns='index', inplace=True)
df_mappa_stazioni = gpd.GeoDataFrame(df_mappa_stazioni, crs='EPSG:4326')
df_mappa_stazioni = df_mappa_stazioni.drop_duplicates().reset_index().drop(columns='index')


#### Creo funzione per assegnare ad ogni dataframe con dataeora delle ulteriori colonne, che mi dicono: 
#    Il giorno della settimana
#    La fascia oraria ('giorno', 'sera') 

def categorizza_tempo( df ):
    ''' Categorizza la serie temporale di un dataframe. 
        Prende in input un pd.DataFrame che deve avere una colonna 'datetime' nel formato datetime di pandas. Restituisce un dataframe con aggiunte le colonne:
        'TimeRange': 'day' se l'orario è tra le 8:00 (Incluse) e le 19:00 (escluse)
                     'evening' se tra le 19:00 (incluse) e le 24:00(escluse) 
                     'night' negli altri casi
        'isWeekend': bool che identifica se il giorno della settimana è weekend o meno '''
    
    #divido le fasce orarie
    df.loc[(df['datetime'].dt.hour >= 8) & (df['datetime'].dt.hour < 19), 'TimeRange'] = 'day'
    df.loc[(df['datetime'].dt.hour >= 19) & (df['datetime'].dt.hour < 24), 'TimeRange'] = 'evening'
    df['TimeRange'].fillna('night', inplace=True) 
    
    #distinguo giorni della settimana
    df.loc[df['datetime'].dt.weekday >=5, 'isWeekend'] = True
    df['isWeekend'].fillna(False, inplace=True)
    return df
    
def categorizza_consumi( df, consumiColName ):
    '''Categorizza le righe di un pd.DataFrame in base al consumo utilizzando primo e terzo quartile
        detti firstQ e thirdQ rispettivamente.
        Inputs:  

            df: dataframe da categorizzare        
            consumiColName: nome della colonna contenente i consumi
        
        Outputs:
        
        pd.DataFrame uguale a df con l'aggiunta di una colonna 'FASCIA_CONSUMI' che contiene
        0 se df[consumiColName]<firstQ
        1 se firstQ <= df[consumiColName] < thirdQ 
        2 se thirdQ <= df[consumiColName]'''
    
    firstQ = df[ consumiColName ].quantile(q=0.25, interpolation='linear')
    thirdQ = df[ consumiColName ].quantile(q=0.75, interpolation='linear')

    df.loc[(df[consumiColName] >= firstQ) & (df[consumiColName]< thirdQ) , 'FASCIA_CONSUMI'] = 1
    df.loc[(df[consumiColName] >= thirdQ), 'FASCIA_CONSUMI'] = 2
    df['FASCIA_CONSUMI'].fillna(0, inplace=True) 
    
    return df


meteo_df = categorizza_tempo(meteo_df)
#volendo rimpiazzare i vuoti con dei NaN, ma per ora non serve
#meteo_df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
def adjust_wind( x ):
    if type(x)==str:
        if x=='':
            return float('NaN')
        else:
            return float(x)
    else:
        return float('NaN')

meteo_df[ 'windSpeed' ] = meteo_df[ 'windSpeed' ].apply(adjust_wind)
meteo_df[ 'windDir' ] = meteo_df[ 'windDir' ].apply(adjust_wind)

#creo due pd.Series che contengono dati raggruppati e mediati/sommati come voglio
meanTempGb = meteo_df.groupby(['station', meteo_df['datetime'].dt.date,'TimeRange'] )['temperatures'].mean() 
sumPrecipGb = meteo_df.groupby(['station', meteo_df['datetime'].dt.date, 'TimeRange'] )['precipitations'].sum() 
meanWindsGb = meteo_df.groupby(['station', meteo_df['datetime'].dt.date,'TimeRange'])['windSpeed'].mean()

# unisco in un dataframe e lo aggiusto
dicttmp = { 'meanTemperature': meanTempGb, 'precipitations': sumPrecipGb, 'meanWinds': meanWindsGb}
df_tmp_gb = pd.DataFrame(dicttmp).reset_index()
df_tmp_gb.rename(columns={'datetime':'date'} , inplace=True) 



#voglio unirlo con i dati di geometry, e altri dati giornalieri non usati nel groupby
df_tmp_tomerge = meteo_df[['station', 'geometry','elevation', 'minTemperature', 'maxTemperature', 'datetime', 'isWeekend', 'TimeRange']]
#il seguente comando genera una warning ma a quanto pare è un falso positivo. 
#serve a tenere solo le date e a buttare le ore
df_tmp_tomerge['date'] =df_tmp_tomerge['datetime'].dt.date
#togliendo datetime ho un df con un sacco di righe uguali, le butto con .drop_duplicates()
df_tmp_tomerge.drop(columns='datetime', inplace=True)
df_tmp_tomerge  = df_tmp_tomerge.loc[df_tmp_tomerge.astype(str).drop_duplicates().index].reset_index()
df_tmp_tomerge.drop(columns='index', inplace=True)
#finalmente unisco i due dataframe
meteo_df = pd.merge(left=df_tmp_tomerge, right=df_tmp_gb, on=['station', 'date', 'TimeRange'])

#aggiusto le colonne relative al vento

gdfLineCells = pd.merge(left=grid, right=df_linee, left_on='id', right_on='SQUAREID', how='right').drop(columns='id')
gdfLineCells[['geometry', 'SQUAREID']].drop_duplicates().reset_index().drop(columns='index')
#per calcolare il criordiniamoentroide è tecnicamente opportuno trasformare coordinate sferiche in km
#anche se non dovrebbe fare molta differenza
gdfLineCells.to_crs(epsg=3035, inplace=True)
gdfLineCells['centroid'] = gdfLineCells['geometry'].centroid
df_mappa_stazioni.to_crs(epsg=3035, inplace=True)


## SI ASSOCIA LA STAZIONE PIÙ VICINA A OGNI CELLA DI TERRITORIO 

meteo_stations = list(df_mappa_stazioni['geometry']) 
cell_centroids = list(gdfLineCells['centroid'] )
#creo array che conterrà gli indici corrispondenti alle stazioni meteo più vicine a ogni centroide
nearest_ms_to_cells = np.zeros( (len(cell_centroids),) ) 
for i_cell, pt_cell in enumerate(cell_centroids):
    nearest_index = 0
    nearest_distance = pt_cell.distance(meteo_stations[nearest_index])
    for i_st, pt_st in enumerate(meteo_stations):
        current_distance = pt_cell.distance(pt_st)
        if current_distance <nearest_distance:
            
            nearest_distance=current_distance
            nearest_index = i_st
    
    #fatto il loop sulle stazioni meteo, segno qual è la più vicina
    nearest_ms_to_cells[i_cell] = nearest_index
    stationcodes = df_mappa_stazioni['station'].to_list()

#creo una lista tale che l'i-esimo elemento della lista è il codice della stazione meteo 
#più vicina alla i-esima cella di territorio (nell'ordine in cui appaiono nei dataframe sopra)
codelist = [stationcodes[int(nearest_ms_to_cells[ii])] for ii, p in enumerate(nearest_ms_to_cells)]
gdfLineCells['nearestStation'] = codelist




#######CREO DATAFRAME CON CELLE E CONSUMI SUDDIVISI PER REGIONE E FASCE ORARIE

#sebbene non sia il massimo dell'eleganza, importo di nuovo df_consumi per comodità
#e per evitare conflitti
df_nov = pd.read_csv(data_path / files['NOV-DATA'], names = nomi)
df_dec = pd.read_csv(data_path / files['DEC-DATA'], names = nomi)
df_consumi = pd.concat([df_nov, df_dec])
#prima aggiusto la colonna time convertendola nel formato di pandas
df_consumi['time'] = pd.to_datetime(df_consumi['time'], format='%Y-%m-%d %H:%M')
df_consumi.rename(columns={'time':'datetime'}, inplace=True) 
#suddivido in categorie di tempi
df_consumi = categorizza_tempo( df_consumi ) 
#sommo i consumi fissando linea giorno e fascia oraria
gb = df_consumi.groupby(['LINESET', df_consumi.datetime.dt.date, 'TimeRange', 'isWeekend'])['consumi'].sum()
df_consumi = pd.DataFrame(gb).reset_index()
#contiamo le ubicazioni per linea
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
df_consumi=df_consumi.groupby([ 'SQUAREID','datetime', 'TimeRange', 'isWeekend'])['consumo_della_cella'].sum().reset_index()
### creo un dataframe con SQUAREID e codici stazioni:
df_suddivisione = gdfLineCells[['SQUAREID', 'nearestStation']].drop_duplicates().reset_index().drop(columns='index')
# unisco dati dei consumi sulle celle con quelli della suddivisione in zone
# in modo da suddividere i consumi in zone
df_consumi = pd.merge(left=df_consumi, right=df_suddivisione, on='SQUAREID', how='left')
# sommo i consumi di ogni zona
df_consumi = df_consumi.groupby(['nearestStation', 'datetime', 'TimeRange', 'isWeekend'])['consumo_della_cella'].sum().reset_index()
#rinomino un po' di colonne per comodità nell'uso di merge
df_consumi.rename(columns={'nearestStation':'station', 'datetime':'date', 'consumo_della_cella':'consumoTerritorio'} , inplace=True)
#segno la durata di ogni fascia oraria così da poter normalizzare il consumo
durataFasce = {'day':11, 'evening':5, 'night':8}
#ad ogni time range associo la sua durata in ore con .map
df_consumi['N_ORE'] = df_consumi['TimeRange'].map(durataFasce)
#finalmente merge tra dati di consumi e meteo
df_meteo_consumi = pd.merge(left=df_consumi, right=meteo_df, on=['station', 'date', 'TimeRange', 'isWeekend'])
#conto le ubicazioni in ogni squareid
df_ubi_squareid = df_linee.groupby('SQUAREID')['NR_UBICAZIONI'].sum().reset_index()
#e unisco il df appena ottenuto con quello contenente SQUAREID e codicistazione
df_ubi_territori = pd.merge(left=df_ubi_squareid, right=df_suddivisione, on='SQUAREID')
#così posso sommare le ubicazioni su ogni territorio
df_ubi_territori = df_ubi_territori.groupby('nearestStation')['NR_UBICAZIONI'].sum().reset_index()
df_ubi_territori.rename(columns={'nearestStation':'station'}, inplace=True) 
#unisco le ubicazioniperterritorio al df con tutti i dati
df_meteo_consumi = pd.merge(left=df_meteo_consumi, right=df_ubi_territori, how='left', on='station')
#in ultimo, aggiungo una colonna per indicare quanto è il consumo/(ora*ubicazione) in quel territorio
df_meteo_consumi['consumoOrarioUbicazione'] = df_meteo_consumi['consumoTerritorio']/(df_meteo_consumi['NR_UBICAZIONI']*df_meteo_consumi['N_ORE'])
#la stazione meteo di trento è T0129 , vedi mappa sopra
dfTrento = df_meteo_consumi[ (df_meteo_consumi['station']=='T0129')
                            & (df_meteo_consumi['isWeekend']==False)  ]                           

#####IMPORTO E RIORDINO DATI INQUINAMENTO 
# dati inquinamento
df_inquinamento= pd.read_csv(data_path2 / files['inquinamento'] , encoding='latin-1')
dfInqTrento = df_inquinamento[ (df_inquinamento['Stazione'] =='Parco S. Chiara' ) | (df_inquinamento['Stazione'] ==  'Via Bolzano' )]
#convertiamo in datetime.
#notiamo che le ore vanno da 1 a 24 mentre vorremmo che andassero da 0 a 23.
#decidiamo per ora di convertirle nel formato adeguato semplicemente sottraendo 1.
#per essere precisi si dovrebbe modificare la funzione che categorizza i tempi in fasce orarie
#in modo da far sì che "sera" sia : dalle 18 alle 23 anzichè dalle 19 alle 24
#(idem per "giorno")
dfInqTrento['Ora'] = dfInqTrento['Ora'].apply( lambda x: f"{x-1:02d}:00" ) 
dfInqTrento['datetime'] = pd.to_datetime( dfInqTrento['Data']+ dfInqTrento['Ora'],format='%Y-%m-%d%H:%M' )
dfInqTrento = dfInqTrento.drop(columns=['Data','Ora'])
#separo le colonne di diversi inquinanti riferiti a stazioni diverse
dfInqTrento =  dfInqTrento.pivot(index=[ 'Unità di misura', 'datetime'], columns=['Stazione','Inquinante'], values='Valore').reset_index()
#riduco a un solo livello di nomi colonne
dfInqTrento.columns=[' '.join(col).strip() for col in dfInqTrento.columns.values]
#divido in fasce orarie
dfInqTrento=categorizza_tempo(dfInqTrento)

#noto che alcune misure di inquinanti sono salvate in stringhe (errore quando si applica mean() ) 
#eseguo dunque conversione in float usando .apply. 
#noto anche che in alcune caselle dell'Ossido di carbonio appare la stringa 'n.d.' e la 
#convertiamo in NaN usando la seguente funzione. 
def aggiusta_float(x):
    '''definisco una funzione per trasformare le stringhe in float e, qualora esse siano 'n.d', trasformarle in NaN'''
    if x=='n.d.':
        return float('NaN')
        
    else:
        return float(x)

columns_inquinanti = list(dfInqTrento.columns[2:10])

for c in columns_inquinanti:

    dfInqTrento[c] = dfInqTrento[c].apply(aggiusta_float)
    

#finalmente pronti per fare la media degli inquinanti nelle varie fasce orarie di ogni giorno

dfInqTrento = dfInqTrento.groupby([dfInqTrento['datetime'].dt.date,
                     'Unità di misura', 'TimeRange','isWeekend'])[columns_inquinanti].mean().reset_index()

dfInqTrento.rename(columns={'datetime':'date'}, inplace=True)

#attenzione: necessario .groupby.agg(np.nanmean) perché ogni riga è sdoppiata
#np.nanmean restituisce nan se entrambi gli elementi sono nan, altrimenti restituisce l'unico che non è nan
#cioè per ogni giorno e fascia oraria (es. 1 novembre sera) ci sono due righe e non una:
#una riga contiene solo dati di S.Chiara, l'altra solo di Via Bolzano

dfInqTrento = dfInqTrento.groupby( ['date', 'TimeRange', 'isWeekend']).agg(np.nanmean).reset_index()
#tolgo i weekend
dfInqTrento_infraset = dfInqTrento[ ~dfInqTrento['isWeekend'] ]
#e finalmente unisco con dati di meteo e consumi
dfMeteoInqCons = pd.merge( left=dfInqTrento_infraset, right=dfTrento, on=['TimeRange', 'isWeekend', 'date'])

dfMeteoInqCons.loc[:,'date'] = pd.to_datetime(dfMeteoInqCons['date']).dt.dayofyear
dfTrentoDay = dfMeteoInqCons[  dfMeteoInqCons['TimeRange'] == 'day' ]
dfTrentoEv = dfMeteoInqCons[ dfMeteoInqCons['TimeRange'] =='evening']
dfTrentoNight = dfMeteoInqCons[ dfMeteoInqCons['TimeRange'] =='night']
dfFasceOrarie = [dfTrentoDay, dfTrentoEv, dfTrentoNight]

for ii in range(3):
    
    
    dfFasceOrarie[ii] = categorizza_consumi (dfFasceOrarie[ii], 'consumoOrarioUbicazione')

dfMeteoInqCons = pd.concat(dfFasceOrarie)


path_to_save  = Path('.././data/interim')
dfMeteoInqCons.to_csv( path_to_save / "datiMeteoInquinamentoConsumi.csv" ) 