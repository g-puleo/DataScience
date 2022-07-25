
import sys, os    
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from trentodatalib import trentopaths as tpath
from trentodatalib import rawdatabase as rawdata
from trentodatalib import funzioni as fz
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#divido il database in train e test
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Lasso, Ridge, LassoCV, RidgeCV
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from joblib import dump, load



def plotregr(): 
	df_giornoprov = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiRegrProvDay.pkl"))
	df_seraprov = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiRegrProvEv.pkl"))

	# queste sono tutte le colonne che si hanno a disposizione per le features
	'''['Parco S. Chiara PM10_x', 'Parco S. Chiara PM2.5_x',
	 'Parco S. Chiara Biossido di Azoto_x' ,'Parco S. Chiara Ozono_x'
	 'Parco S. Chiara Biossido Zolfo_x', 'Via Bolzano PM10_x'
	 'Via Bolzano Biossido di Azoto_x', 'Via Bolzano Ossido di Carbonio_x'
	 'Rovereto PM10_x', 'Rovereto PM2.5_x', 'Rovereto Biossido di Azoto_x'
	 'Rovereto Ozono_x', 'Borgo Valsugana PM10_x' 'Borgo Valsugana PM2.5_x'
	 'Borgo Valsugana Biossido di Azoto_x' 'Borgo Valsugana Ozono_x'
	 'meanTemperaturemean_x' 'precipitationsmean_x' 'meanWindsmean_x'
	 'consumoOrarioUbicazionemean_x' 'Parco S. Chiara PM10_x+1'
	 'Parco S. Chiara PM2.5_x+1' 'Parco S. Chiara Biossido di Azoto_x+1'
	 'Parco S. Chiara Ozono_x+1' 'Parco S. Chiara Biossido Zolfo_x+1'
	 'Via Bolzano PM10_x+1' 'Via Bolzano Biossido di Azoto_x+1'
	 'Via Bolzano Ossido di Carbonio_x+1' 'Rovereto PM10_x+1'
	 'Rovereto PM2.5_x+1' 'Rovereto Biossido di Azoto_x+1'
	 'Rovereto Ozono_x+1' 'Borgo Valsugana PM10_x+1'
	 'Borgo Valsugana PM2.5_x+1' 'Borgo Valsugana Biossido di Azoto_x+1'
	 'Borgo Valsugana Ozono_x+1' 'meanTemperaturemean_x+1'
	 'precipitationsmean_x+1' 'meanWindsmean_x+1'
	 'consumoOrarioUbicazionemean_x+1']'''


	# per uno dei modelli si può vedere come cambia lo score di test e train al variare delle features 
	# attenzione c'è un inquinante ( 'Parco S. Chiara PM10_x') che un giorno ha un Nan non inserire quello nella featuresList
	featuresList = [ 'consumoOrarioUbicazionemean_x','meanTemperaturemean_x', 'precipitationsmean_x', 'meanTemperaturemean_x+1', 'precipitationsmean_x+1','Parco S. Chiara PM2.5_x','Parco S. Chiara Biossido Zolfo_x', 'Parco S. Chiara PM2.5_x+1','Parco S. Chiara Biossido Zolfo_x+1', 'Borgo Valsugana PM10_x', 'Borgo Valsugana PM2.5_x','Borgo Valsugana PM10_x+1', 'Borgo Valsugana PM2.5_x+1','Via Bolzano Biossido di Azoto_x'
	  ]

	N = len(featuresList) 
	ygTest = np.zeros( (N,)  ) 
	ysTrain = np.zeros( (N,)  )
	ygTrain = np.zeros( (N )  )
	ysTest = np.zeros( (N,)  )
	Nfeatures = np.zeros( (N) ) 
	target =  'consumoOrarioUbicazionemean_x+1'
	for jj, feats in enumerate(featuresList):
	    Nfeatures[jj] = jj+1
	    ygTrain[jj], ygTest[jj] = fz.regressioneLineare(df_giornoprov, featuresList[0:jj+1], target)
	    ysTrain[jj], ysTest[jj] = fz.regressioneLineare(df_seraprov, featuresList[0:jj+1], target)

	fig, axs = plt.subplots(1, 2, figsize=(16,8) )
	colors = ['gold', 'darkblue']
	testscore  = [ygTest, ysTest]
	trainscore = [ygTrain, ysTrain]
	titles = ['Giorno', 'Sera']
	xlabels = ['Number of features', 'Number of features']
	ylabels = ['Score','Score']
	for ii  in range(2):
	    axs[ii].plot( Nfeatures, testscore[ii], label='Test score', color=colors[ii])
	    axs[ii].plot( Nfeatures, trainscore[ii], label='Train score', color=colors[ii], linestyle='-.')
	    axs[ii].legend(fontsize=14)
	    axs[ii].grid(visible=True)
	    axs[ii].set_title( titles[ii], fontsize = 'x-large' ) 
	    axs[ii].set_xlabel( xlabels[ii], fontsize = 'large' )
	    axs[ii].set_ylabel( ylabels[ii], fontsize = 'large' )
	#fig.set_size_inches(18.5, 10.5) 
	    
	#plt.show()
	return
	
