## QUESTO SCRIPT ESEGUE I PLOT DELLA MATRICE DI CORRELAZIONE DI INQUINAMENTO METEO E CONSUMI
## INOLTRE MOSTRA QUALI SONO I CONSUMI NELLE DIVERSE FASCE ORARIE. (CATEGORIZZAZIONE USANDO QUARTILI)

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

dfTrentoZoneDay = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiTrentoDay.pkl"))
dfTrentoZoneEv = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiTrentoEv.pkl"))
dfTrentoZoneNight = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiTrentoNight.pkl"))

dfFasceOrarie = [dfTrentoZoneDay, dfTrentoZoneEv, dfTrentoZoneNight]

########## visuaizzazione della divisione in categorie di consumi in alto medio basso usando i quartili ###########
def histplotconsumi():
    fig, axs_hist = plt.subplots(2,1, figsize=(9,14))
    fasce = ['giorno (08:00-19:00)', 'sera (19:00-24:00)', 'notte (00:00-08:00)']
    colors=['skyblue', 'mediumblue', '#000013']
    quartiles_A = [] 
    quartiles_B = []
    ylims = [0,21]
    xlims = [0.7,2.7]
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
            axs_hist[kk].set_xlabel('consumo orario per ubicazione (kWh)', fontsize=fs)
        axs_hist[kk].set_ylabel('N. giorni', fontsize=fs)
        axs_hist[kk].grid(visible='True')
        axs_hist[kk].legend(fontsize=fs, loc='upper left')
        axs_hist[kk].set_ylim(ylims)
        axs_hist[kk].set_xlim(xlims)
        axs_hist[kk].set_title(station_names[kk], fontsize=fs+2)

    plt.show()
    return
# ### voglio visualizzare la matrice di correlazione anche per scegliere più coscientemente le feaures da dare al classificatore

# #rinomino le colonne per rendere più leggibile il plot della matrice

def edaConsumiZoneTrento(mode="corr"):
    '''Questa funzione prende un argomento che può essere
        "corr": (default) plotta matrici delle correlazioni per i dataframe delle due zone di trento.
        "season": plotta l'andamento stagionale dei consumi orari per ubicazione nelle due diverse zone. 
        Se l'argomento è diverso non plotta nulla. 
        '''
    dict_nomicolonneita = {'date_x':'data', 'consumoOrarioUbicazione_x':'consumo', 'meanTemperature_x':'T media',
    'precipitations_x':'precipitazioni', 'meanWinds_x':'vento', 'consumoOrarioUbicazione_x+1':'consumo\ngiorno\nsuccessivo'}

    fasce = ['giorno (08:00-19:00)', 'sera (19:00-24:00)', 'notte (00:00-08:00)']
    # #plot delle matrici di correlazione

    stations = ["T0129", "T0135"]
    station_names = ["Laste", "Roncafort"]

    if mode == "corr":
        figmatA, axs_corr_matA = plt.subplots(1,2, figsize=(14,6))
        figmatB, axs_corr_matB = plt.subplots(1,2, figsize=(14,6))
        figmat = [figmatA, figmatB]
        axs_corr_mat = [axs_corr_matA, axs_corr_matB]

    if mode == "season":
        fig_stagione = plt.figure()
        ax_stagione = plt.axes()
    
    for jj, station in enumerate(stations):

        for ii in range(2):
            
            df = dfFasceOrarie[ii][dfFasceOrarie[ii]['station_x']==station]
            df.rename(columns=dict_nomicolonneita, inplace=True)
            df['data'] = pd.to_datetime(df['data']).dt.dayofyear
            if mode == "corr":
                corr_cols = list(dict_nomicolonneita.values())
                corr = df[corr_cols].corr()
                sns.heatmap(corr, ax=axs_corr_mat[jj][ii], cmap=plt.cm.RdYlGn)
                axs_corr_mat[jj][ii].set_title( fasce[ii] , fontsize=13)
            if ii==0 and mode == "season":
                ax_stagione.scatter(df['data'], df['consumo'], label=station_names[jj])


        if mode == "season":
            ax_stagione.legend(fontsize=13)
            ax_stagione.grid(visible=True)
            ax_stagione.set_xlabel("giorno dell'anno")
            ax_stagione.set_ylabel("consumo")
        if mode == "corr":
            figmat[jj].suptitle(station_names[jj])
        
    plt.show()
    
    return
