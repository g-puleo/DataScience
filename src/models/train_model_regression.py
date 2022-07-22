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
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from joblib import dump, load


# devo importare i database della zona di Trento dalla cartella data processed

df_giornoTN= pd.read_pickle( os.path.join(os.path.dirname(__file__),"../../data/processed/datiregrcomuneday.pkl"))
df_seraTN = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiregrcomuneev.pkl"))
df_giornoprov = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiregrprovday.pkl"))
df_seraprov = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiregrprovev.pkl"))


def regressioneLineare( df_in, feat, targ): 
	Xtrain, Xtest, Ytrain, Ytest = train_test_split(df_in[feat], df_in[targ], test_size = 0.30, random_state = 7)
	ppl = Pipeline(  [ ('scaler', StandardScaler() ) , ('clf', LinearRegression() ) ] ) 
	ppl.fit(Xtrain, Ytrain)
	trainScore= ppl.score(Xtrain, Ytrain)
	testScore = ppl.score(Xtest, Ytest)
	print(f"score on train is = {trainScore}")
	print(f"score on test is = {testScore}")
	return ppl
# class sklearn.linear_model.Lasso(alpha=1.0, *, fit_intercept=True, normalize='deprecated', precompute=False, copy_X=True, max_iter=1000, tol=0.0001, warm_start=False, positive=False, random_state=None, selection='cyclic'
def regressionelasso( df_in, feat, targ, alpha): 
	Xtrain, Xtest, Ytrain, Ytest = train_test_split(df_in[feat], df_in[targ], test_size = 0.30, random_state = 7)
	ppl = Pipeline(  [ ('scaler', StandardScaler() ) , ('clf', Lasso(alpha) ) ] ) 
	ppl.fit(Xtrain, Ytrain)
	trainScore= ppl.score(Xtrain, Ytrain)
	testScore = ppl.score(Xtest, Ytest)
	print(f"score on train is = {trainScore}")
	print(f"score on test is = {testScore}")
	return ppl

def regressioneridge(df_in, feat, targ, alpha):
	Xtrain, Xtest, Ytrain, Ytest = train_test_split(df_in[feat], df_in[targ], test_size = 0.30, random_state = 7)
	ppl = Pipeline(  [ ('scaler', StandardScaler() ) , ('clf', Ridge(alpha) ) ] ) 
	ppl.fit(Xtrain, Ytrain)
	trainScore= ppl.score(Xtrain, Ytrain)
	testScore = ppl.score(Xtest, Ytest)
	print(f"score on train is = {trainScore}")
	print(f"score on test is = {testScore}")
	return ppl

def savemodel( model, namemodel):
	filename = '../../models/modelreg_'+namemodel+'.sav'
	dump(model, filename)


#ora definisco le features e il target 
features= ['consumoOrarioUbicazione_x', 'meanTemperature_x', 'Parco S. Chiara Biossido Zolfo_x']
target =  'consumoOrarioUbicazione_x+1'

model1 = regressioneLineare(df_giornoTN, features, target)

savemodel(model1, 'giornoTN')
model2 = regressioneLineare(df_seraTN, features, target)
savemodel(model2, 'seraTN')
# ora definisco le features e il target 
features= ['consumoOrarioUbicazionemean_x', 'meanTemperaturemean_x', 'Parco S. Chiara Biossido Zolfo_x']
target =  'consumoOrarioUbicazionemean_x+1'
#target = df_giornoTN.columns.values[-1]]
model3 = regressioneLineare(df_giornoprov, features, target)
savemodel(model3, 'giornoprov')
model4 = regressioneLineare(df_seraprov, features, target)
savemodel(model4, 'seraprov')
# per uno dei modelli si può vedere come cambia lo score di test e train al variare delle features 
# scelgo i database del modello 1 
print(df_giornoprov)

'''
# queste sono tutte le colonne che hai a disposizione
['Parco S. Chiara PM10_x', 'Parco S. Chiara PM2.5_x',
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
 'consumoOrarioUbicazionemean_x+1']

# queste sono le features che puoi aggiungere 
Parco S. Chiara PM10_x', 'Parco S. Chiara PM2.5_x','Parco S. Chiara Biossido di Azoto_x' ,'Parco S. Chiara Ozono_x','Parco S. Chiara Biossido Zolfo_x',

'''
featuresList = [ 'consumoOrarioUbicazionemean_x','meanTemperaturemean_x', 'precipitationsmean_x', 'meanTemperaturemean_x+1', 'precipitationsmean_x+1','Parco S. Chiara PM2.5_x']

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
trainscore = [ygTrain, ygTrain]
titles = ['giorno', 'sera']
for ii  in range(2):
    axs[ii].plot( Nfeatures, testscore[ii], label='Test score', color=colors[ii])
    axs[ii].plot( Nfeatures, trainscore[ii], label='Train score', color=colors[ii], linestyle='-.')
    axs[ii].legend(fontsize=14)
    axs[ii].grid(visible=True)
    axs[ii].set_title( titles[ii] ) 


plt.show()


