import sys, os    
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from trentodatalib import trentopaths as tpath
from trentodatalib import rawdatabase as rawdata
from trentodatalib import funzioni as fz
import pandas as pd
import numpy as np

df_inquinamento = rawdata.df_inquinamentoraw.copy()
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
dfInqTrento=fz.categorizza_tempo(dfInqTrento)

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

dfInqTrento.to_pickle(os.path.join(os.path.dirname(__file__),"../../data/interim/datiInquinamento.pkl")  )


df_inquinamento.to_pickle( os.path.join(os.path.dirname(__file__),"../../data/interim/datiTotInquinamento.pkl") )

