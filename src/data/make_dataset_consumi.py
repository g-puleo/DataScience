import pandas as pd
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from trentodatalib import trentopaths as tpath
from trentodatalib import rawdatabase as rawdata
from trentodatalib import funzioni as fz
from datetime import time, timedelta, datetime, date 
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

df_linee = rawdata.df_lineeraw.copy()
df_consumi = rawdata.df_consumiraw.copy()


# A questo punto del codice genero i database dei consumi lordi riguardanti i consumi diurni e notturni che mi serviranno per fare considerazioni su eventuali variazioni fra giorno e notte 

# divisione della colonna time in data e ora
df_consumi[['giorno','ora']] = df_consumi.time.str.split(" ",expand=True)
df_consumi.time = df_consumi.time.apply(datetime.fromisoformat)

#NOTA BENE: SI PUÒ RISISTEMARE QUESTA PARTE E LA FUNZIONE GENERAMAPPACONSUMI USANDO IL FORMATO DATETIME DI PANDAS ( solo per uniformità di codice)
#df_consumi['datetime'] = pd.to_datetime(df_consumi['time'], format='%Y-%m-%d %H:%M')
# divido il database in due database uno con i consumi diurni e uno con i consumi notturni 
mask = ( pd.to_timedelta(df_consumi['ora'].astype(str).add(':00')).between(pd.Timedelta('08:00:00'), pd.Timedelta('19:00:00')) )
df_consumidiurni = df_consumi[mask]
df_consuminotturni = df_consumi[~mask]

df_consumidiurni.to_pickle(os.path.join(os.path.dirname(__file__),"../../data/interim/datiConsumiDiurniLordi.pkl"))
df_consuminotturni.to_pickle(os.path.join(os.path.dirname(__file__),"../../data/interim/datiConsumiNotturniLordi.pkl"))

################
# Adesso faccio dei Database per fare un confronto fra i consumi durante il week-end e i giorni infrasettimanali 
# ho aggiunto una colonna che mi enumera i giorni della settimana 
df_consumi["giorno"] = pd.to_datetime(df_consumi["giorno"])
df_consumi["DayOfWeek"] = df_consumi["giorno"].dt.weekday
# ho aggiunto un altra colonna che mi dice se il giorno è un week end o meno
df_consumi["isweekend"] = df_consumi["giorno"].dt.weekday > 4
# creazione di due database filtrando con la condizione sulla colonna DayOfweek molto più comoda di isweekend 
df_consumisettimana = df_consumi[df_consumi.DayOfWeek < 5]
df_consumiweekend = df_consumi[df_consumi.DayOfWeek > 4]

df_consumisettimana.to_pickle(os.path.join(os.path.dirname(__file__),"../../data/interim/datiConsumiInfrasetLordi.pkl"))
df_consumiweekend.to_pickle(os.path.join(os.path.dirname(__file__),"../../data/interim/datiConsumiWkndLordi.pkl"))


'''#contiamo le ubicazioni per linea
df_consumi['time'] = pd.to_datetime(df_consumi['time'], format='%Y-%m-%d %H:%M')
df_consumi.rename(columns={'time':'datetime'}, inplace=True) 
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
df_consumi=df_consumi.groupby([ 'SQUAREID','datetime','NR_UBICAZIONI'])['consumo_della_cella'].sum().reset_index()'''

################################################################

#prima aggiusto la colonna time convertendola nel formato di pandas
df_consumi['time'] = pd.to_datetime(df_consumi['time'], format='%Y-%m-%d %H:%M')
df_consumi.rename(columns={'time':'datetime'}, inplace=True) 
#suddivido in categorie di tempi
df_consumi = fz.categorizza_tempo( df_consumi ) 
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

df_consumi.to_pickle( os.path.join(os.path.dirname(__file__),"../../data/interim/datiConsumi.pkl") )

















