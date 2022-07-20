## QUESTO SCRIPT ESEGUE I PLOT DELLA MATRICE DI CORRELAZIONE DI INQUINAMENTO METEO E CONSUMI
## INOLTRE MOSTRA QUALI SONO I CONSUMI NELLE DIVERSE FASCE ORARIE. (CATEGORIZZAZIONE USANDO QUARTILI)
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

dfTrentoZoneDay = pd.read_pickle("../data/interim/datiTrentoDay.pkl")
dfTrentoZoneEv = pd.read_pickle("../data/interim/datiTrentoEv.pkl")
dfTrentoZoneNight = pd.read_pickle("../data/interim/datiTrentoNight.pkl")

dfFasceOrarie = [dfTrentoZoneDay, dfTrentoZoneEv, dfTrentoZoneNight]

########## visuaizzaione della divisione in categorie di consumi in alto medio basso usando i quartili ###########
def histplotconsumi():
    fig, axs_hist = plt.subplots(2,1, figsize=(9,14))
    fasce = ['giorno (08:00-19:00)', 'sera (19:00-24:00)', 'notte (00:00-08:00)']
    colors=['skyblue', 'mediumblue', '#000013']
    quartiles_A = [] 
    quartiles_B = []
    ylims = [0,21]
    xlims = [0.2,0.8]
    fs = 11
    station_names = ["Zona Laste", "Zona Roncafort"]


    for ii in range(3):
        idxA = dfFasceOrarie[ii]['consumoOrarioUbicazione_x'][ dfFasceOrarie[ii]['station_x'] == "T0129"].index
        idxB = dfFasceOrarie[ii]['consumoOrarioUbicazione_x'][ dfFasceOrarie[ii]['station_x'] == "T0135"].index
        idx = [idxA, idxB]
        firstQ_A = dfFasceOrarie[ii]['consumoOrarioUbicazione_x'][idxA].quantile(q=0.25, interpolation='linear')
        thirdQ_A = dfFasceOrarie[ii]['consumoOrarioUbicazione_x'][idxA].quantile(q=0.75, interpolation='linear')
        firstQ_B = dfFasceOrarie[ii]['consumoOrarioUbicazione_x'][idxB].quantile(q=0.25, interpolation='linear')
        thirdQ_B = dfFasceOrarie[ii]['consumoOrarioUbicazione_x'][idxB].quantile(q=0.75, interpolation='linear')

        quartiles_A.append( (firstQ_A, thirdQ_A) ) 
        quartiles_B.append( (firstQ_B, thirdQ_B) ) 
        quartiles = [quartiles_A, quartiles_B]
        
        for kk in range(2):
            axs_hist[kk].hist(dfFasceOrarie[ii]['consumoOrarioUbicazione_x'][idx[kk]], color=colors[ii],
                 alpha=0.7, label=fasce[ii])
            #plot quartiles vertical lines for each axes
            for jj in range(2):
                axs_hist[kk].plot( quartiles[kk][ii][jj]*np.ones( (2,)), ylims, color=colors[ii] , linestyle='--')

    for kk in range(2):
        if kk==1:
            axs_hist[kk].set_xlabel('consumo orario per ubicazione (ampere)', fontsize=fs)
        axs_hist[kk].set_ylabel('N. giorni', fontsize=fs)
        axs_hist[kk].grid(visible='True')
        axs_hist[kk].legend(fontsize=fs, loc='upper left')
        axs_hist[kk].set_ylim(ylims)
        axs_hist[kk].set_xlim(xlims)
        axs_hist[kk].set_title(station_names[kk], fontsize=fs+2)
    
# ### voglio visualizzare la matrice di correlazione anche per scegliere più coscientemente le feaures da dare al classificatore

# #rinomino le colonne per rendere più leggibile il plot della matrice
# dict_nomicolonneita = {"date":"data", "Parco S. Chiara PM10": "PM10 (A)", "Parco S. Chiara PM2.5": "PM2.5 (A)", 
#                        "Parco S. Chiara Biossido di Azoto": "NO2 (A)", "Parco S. Chiara Ozono": "O3 (A)",
#                        "Parco S. Chiara Biossido Zolfo": "SO2 (A)", "Via Bolzano PM10":"PM10 (B)", 
#                        "Via Bolzano PM10":"PM10 (B)", "Via Bolzano Biossido di Azoto":"NO2 (B)",
#                        "Via Bolzano Ossido di Carbonio":"CO (B)", "meanTemperature":"T media", "FASCIA_CONSUMI":"Categoria", "meanWinds":"vento"}

# figmat, axs_corr_mat = plt.subplots(1,2, figsize=(14,6))
# #plot delle matrici di correlazione
# for ii in range(2):
#     dfFasceOrarie[ii].rename(columns=dict_nomicolonneita, inplace=True)
#     features = ['data',] + list( dfFasceOrarie[ii].columns.values[3:11]) + ['T media',]
#     target = list(['Categoria',])
#     corr_columns = features + target + ['vento',]
#     corr = dfFasceOrarie[ii][corr_columns].corr()
#     sns.heatmap(corr, ax=axs_corr_mat[ii], cmap=plt.cm.RdYlGn, annot=True)
#     axs_corr_mat[ii].set_title( fasce[ii] , fontsize=13)

#plt.show()