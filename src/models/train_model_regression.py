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


# devo importare i database della zona di Trento dalla cartella data processed

df_giornoTN= pd.read_pickle( os.path.join(os.path.dirname(__file__),"../../data/processed/datiRegrComuneDay.pkl"))
df_seraTN = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiRegrComuneEv.pkl"))
df_giornoprov = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiRegrProvDay.pkl"))
df_seraprov = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiRegrProvEv.pkl"))

#funzione che effettua la regressione lineare 
def regressioneLineare( df_in, feat, targ): 
	Xtrain, Xtest, Ytrain, Ytest = train_test_split(df_in[feat], df_in[targ], test_size = 0.30, random_state = 7)
	ppl = Pipeline(  [ ('scaler', StandardScaler() ) , ('clf', LinearRegression() ) ] ) 
	ppl.fit(Xtrain, Ytrain)
	trainScore= ppl.score(Xtrain, Ytrain)
	testScore = ppl.score(Xtest, Ytest)
	print(f"score Linear Regression on train is = {trainScore}")
	print(f"score Linear Regression on test is = {testScore}")
	return ppl
# funzione che effettua la regressione con regolarizzatore lasso
def regressionelassoCV( df_in, feat, targ): 
	Xtrain, Xtest, Ytrain, Ytest = train_test_split(df_in[feat], df_in[targ], test_size = 0.30, random_state = 7)
	scaler = StandardScaler()
	scaler.fit(Xtrain[feat])
	lcv = LassoCV(eps=0.001, n_alphas=100, alphas=None)
	lcv.fit(Xtrain, Ytrain)
	trainScore= lcv.score(Xtrain, Ytrain)
	testScore = lcv.score(Xtest, Ytest)
	print ( f"la penalty lasso alpha scelta = {lcv.alpha_}")
	print(f"score LassoCV on train is = {trainScore}")
	print(f"score LassoCV on test is = {testScore}")
	return lcv
# funzione che effettua la regressione con regolarizzatore ridge 
def regressioneridgeCV( df_in, feat, targ): 
	Xtrain, Xtest, Ytrain, Ytest = train_test_split(df_in[feat], df_in[targ], test_size = 0.30, random_state = 7)
	scaler = StandardScaler()
	scaler.fit(Xtrain[feat])
	lcv = RidgeCV(alphas=[1e-5, 1e-4, 1e-3, 1e-2])
	lcv.fit(Xtrain, Ytrain)
	trainScore= lcv.score(Xtrain, Ytrain)
	testScore = lcv.score(Xtest, Ytest)
	print ( f"la penalty ridge alpha scelta = {lcv.alpha_}")
	print(f"score RidgeCV on train is = {trainScore}")
	print(f"score RidgeCV on test is = {testScore}")
	return lcv
# funzione che salva i modelli
def savemodel( model, namemodel):
	filename = '../../models/modelreg_'+namemodel+'.sav'
	dump(model, filename)


#ora definisco le features e il target nel caso del comune di Trento
features= ['consumoOrarioUbicazione_x', 'meanTemperature_x', 'Parco S. Chiara Biossido Zolfo_x']
target =  'consumoOrarioUbicazione_x+1'

model1 = regressioneLineare(df_giornoTN, features, target)
savemodel(model1, 'giornoTN')

modellasso1 = regressionelassoCV(df_giornoTN, features, target)
savemodel(modellasso1, 'lassogiornoTN')

modelRidge1 = regressioneridgeCV(df_giornoTN, features, target)
savemodel(modelRidge1, 'ridgegiornoTN')

model2 = regressioneLineare(df_seraTN, features, target)
savemodel(model2, 'seraTN')

modellasso2 = regressionelassoCV(df_seraTN, features, target)
savemodel(modellasso2, 'lassoseraTN')

modelRidge2 = regressioneridgeCV(df_seraTN, features, target)
savemodel(modelRidge2, 'ridgeseraTN')

# ora definisco le features e il target nel caso della provincia di Trento
features= ['consumoOrarioUbicazionemean_x', 'meanTemperaturemean_x', 'Parco S. Chiara Biossido Zolfo_x']
target =  'consumoOrarioUbicazionemean_x+1'

model3 = regressioneLineare(df_giornoprov, features, target)
savemodel(model3, 'giornoprov')

modellasso3 = regressionelassoCV(df_giornoprov, features, target)
savemodel(modellasso3, 'lassogiornoprov')

modelridge3 = regressioneridgeCV(df_giornoprov, features, target)
savemodel(modelridge3, 'ridgegiornoprov')

model4 = regressioneLineare(df_seraprov, features, target)
savemodel(model4, 'seraprov')

modellasso4 = regressionelassoCV(df_seraprov, features, target)
savemodel(modellasso4, 'lassoseraprov')

modelridge4 = regressioneridgeCV(df_seraprov, features, target)
savemodel(modelridge4, 'ridgeseraprov')


