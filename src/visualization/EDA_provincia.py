import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
dfgiorno = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiRegrProvDay.pkl"))
dfsera = pd.read_pickle(os.path.join(os.path.dirname(__file__), "../../data/processed/datiRegrProvEv.pkl"))
dfFasceOrarie = [dfgiorno, dfsera]

columnNames = ['(A) PM10',
       '(A) PM2.5', '(A) NO2',
       '(A) O3', '(A) SO2',
       '(B) PM10', '(B) NO2',
       '(B) CO', '(C) PM10',
       '(C) PM2.5', '(C) NO2', '(C) O3',
       '(D) PM10', '(D) PM2.5',
       '(D) NO2', '(D) O3', 'T media',
       'Precipitazioni', 'Vento',
       'consumo']
       
OriginalcolumnNames = ['Parco S. Chiara PM10_x',
       'Parco S. Chiara PM2.5_x', 'Parco S. Chiara Biossido di Azoto_x',
       'Parco S. Chiara Ozono_x', 'Parco S. Chiara Biossido Zolfo_x',
       'Via Bolzano PM10_x', 'Via Bolzano Biossido di Azoto_x',
       'Via Bolzano Ossido di Carbonio_x', 'Rovereto PM10_x',
       'Rovereto PM2.5_x', 'Rovereto Biossido di Azoto_x', 'Rovereto Ozono_x',
       'Borgo Valsugana PM10_x', 'Borgo Valsugana PM2.5_x',
       'Borgo Valsugana Biossido di Azoto_x', 'Borgo Valsugana Ozono_x', 'meanTemperaturemean_x',
       'precipitationsmean_x', 'meanWindsmean_x',
       'consumoOrarioUbicazionemean_x', 'consumoOrarioUbicazionemean_x']


dictnomicolonne = dict(zip(OriginalcolumnNames,columnNames) ) 
fasce = ['giorno (08:00-19:00)', 'sera (19:00-24:00)', 'notte (00:00-08:00)']

for ii in range(2):
       dfFasceOrarie[ii].rename(columns = dictnomicolonne, inplace=True)


def corrMatrix():
       figmat, axs_corr_mat = plt.subplots(1,2, figsize=(18,5))
       fasce = ['giorno (08:00-19:00)', 'sera (19:00-24:00)', 'notte (00:00-08:00)']

       for ii in range(2):
              corr = dfFasceOrarie[ii][columnNames].corr()
              sns.heatmap(corr, ax=axs_corr_mat[ii], cmap=plt.cm.RdYlGn)
              axs_corr_mat[ii].set_title( fasce[ii] , fontsize=13)

       figmat.suptitle("Correlazioni di dati meteo, consumi e inquinamento di tutta la provincia")
       plt.show()
       return

def corrPlots():
       gr = sns.pairplot(dfFasceOrarie[0], vars=["T media", "consumo", "(A) NO2", "(A) O3"])
       
       plt.show()
       return