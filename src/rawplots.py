from trentodatalib import inquinamento

dfInqTrento = inquinamento.dfInqTrento

## adesso devo aggiungere i dati inquinamento di Trento, sono già stati importati in dfInqTrento_infraset
#tolgo i weekend
dfInqTrento_infraset = dfInqTrento[ ~dfInqTrento['isWeekend'] ]
# finalmente unisco con dati di meteo e consumi di Trento
dfMeteoInqCons = pd.merge( left=dfInqTrento_infraset, right=dfTrento, on=['TimeRange', 'isWeekend', 'date'])

### visuaizzaione della divisione in categorie di consumi in alto medio basso usando i quartili

dfMeteoInqCons.loc[:,'date'] = pd.to_datetime(dfMeteoInqCons['date']).dt.dayofyear
dfTrentoDay = dfMeteoInqCons[  dfMeteoInqCons['TimeRange'] == 'day' ]
dfTrentoEv = dfMeteoInqCons[ dfMeteoInqCons['TimeRange'] =='evening']
dfTrentoNight = dfMeteoInqCons[ dfMeteoInqCons['TimeRange'] =='night']
dfFasceOrarie = [dfTrentoDay, dfTrentoEv, dfTrentoNight]
fig, axs_hist = plt.subplots(1,1, figsize=(9,4))
fasce = ['giorno (08:00-19:00)', 'sera (19:00-24:00)', 'notte (00:00-08:00)']
colors=['skyblue', 'mediumblue', '#000013']
quartiles = []
ylims = [0,21]
fs = 14
for ii in range(3):
    firstQ = dfFasceOrarie[ii]['consumoOrarioUbicazione'].quantile(q=0.25, interpolation='linear')
    thirdQ = dfFasceOrarie[ii]['consumoOrarioUbicazione'].quantile(q=0.75, interpolation='linear')
    quartiles.append( (firstQ, thirdQ) ) 
    axs_hist.hist(dfFasceOrarie[ii]['consumoOrarioUbicazione'], color=colors[ii], alpha=0.5, label=fasce[ii])
    axs_hist.set_xlabel('consumo orario per ubicazione (ampere)', fontsize=fs)
    axs_hist.set_ylabel('N. giorni', fontsize=fs)
    axs_hist.grid(visible='True')
    axs_hist.legend(fontsize=fs, loc='upper left')
    axs_hist.set_ylim(0,21)
    for jj in range(2):
        axs_hist.plot( quartiles[ii][jj]*np.ones( (2,)), ylims, color=colors[ii] , linestyle='--')
        
        
### voglio visualizzare la matrice di correlazione anche per scegliere più coscientemente le feaures da dare al classificatore
import seaborn as sns
#rinomino le colonne per rendere più leggibile il plot della matrice
dict_nomicolonneita = {"date":"data", "Parco S. Chiara PM10": "PM10 (A)", "Parco S. Chiara PM2.5": "PM2.5 (A)", 
                       "Parco S. Chiara Biossido di Azoto": "NO2 (A)", "Parco S. Chiara Ozono": "O3 (A)",
                       "Parco S. Chiara Biossido Zolfo": "SO2 (A)", "Via Bolzano PM10":"PM10 (B)", 
                       "Via Bolzano PM10":"PM10 (B)", "Via Bolzano Biossido di Azoto":"NO2 (B)",
                       "Via Bolzano Ossido di Carbonio":"CO (B)", "meanTemperature":"T media", "FASCIA_CONSUMI":"Categoria", "meanWinds":"vento"}

figmat, axs_corr_mat = plt.subplots(1,2, figsize=(14,6))
#plot delle matrici di correlazione
for ii in range(2):
    dfFasceOrarie[ii].rename(columns=dict_nomicolonneita, inplace=True)
    features = ['data',] + list( dfFasceOrarie[ii].columns.values[3:11]) + ['T media',]
    target = list(['Categoria',])
    corr_columns = features + target + ['vento',]
    corr = dfFasceOrarie[ii][corr_columns].corr()
    sns.heatmap(corr, ax=axs_corr_mat[ii], cmap=plt.cm.RdYlGn, annot=True)
    axs_corr_mat[ii].set_title( fasce[ii] , fontsize=13)

