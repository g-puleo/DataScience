import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from sklearn.neural_network import MLPClassifier
from joblib import dump
import json
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from trentodatalib import funzioni as fz
import numpy as np

dfTrentoZoneDay = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiTrentoDay.pkl"))
dfTrentoZoneEv = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiTrentoEv.pkl"))
dfTrentoZoneNight = pd.read_pickle(os.path.join(os.path.dirname(__file__),"../../data/processed/datiTrentoNight.pkl"))

dfFasceOrarie = [dfTrentoZoneDay, dfTrentoZoneEv]

#stabiliamo quali sono le features
Nfeatures = 5
features = ['consumoOrarioUbicazione_x', 'meanTemperature_x', 'precipitations_x', 'meanTemperature_x+1', 'precipitations_x+1']
target = 'FASCIA_CONSUMI_x+1'
feat_target_dict = {'features':features, 'target':target}
#e salviamo un dizionario .json per poterle passare ad altri file 
with open(os.path.join(os.path.dirname(__file__),'../../models/features.json') , 'w') as fp:
    json.dump(feat_target_dict, fp)

#preparo list da riempire con dataframe di giorno e sera
Xtrain = []
Xtest =  []
ytrain = []
ytest = []

#lista di comodo per renaming files
nomi_fasce_orarie = ['Day', 'Ev']

#divido in train e test
for ii in range(2):
	dfFasceOrarie[ii].reset_index()

	#divisione in train e test
	Xtr, Xts, ytr, yts = train_test_split( dfFasceOrarie[ii][features[0:Nfeatures]], dfFasceOrarie[ii][target], test_size=0.30 , random_state=ii)
	fname = "splitIndexClassificazione" + nomi_fasce_orarie[ii] 
	fz.exportTrainTestSplit(Xtr, Xts, os.path.join( os.path.dirname(__file__), "../../models/", fname) )
	#riscalo i dati
	scaler = StandardScaler()
	scaler.fit(Xtr)
	#aggiungo i dataframe a delle liste
	Xtrain.append(scaler.transform(Xtr))
	Xtest.append(scaler.transform(Xts))
	ytrain.append(ytr)
	ytest.append(yts)


#funzioni che allenano diversi tipi di classificatore. 
def trainRF():
	print("Alleno classificatore Random Forest cercando i migliori iperparametri utilizzando Cross Validation")
	#creo un classificatore Random Forest
	rfc = RandomForestClassifier(oob_score=True, criterion='entropy')

	#voglio usare gridsearchCV per ottimizzare gli iperparametri nell'insieme definito da questa griglia
	maxfeat = [i for i in range(1,Nfeatures+1)]
	param_grid = {'n_estimators':[100, 200], 'max_depth':[10,50, 100], 'max_features':maxfeat}
	#inizializzo un oggetto gridSearch per la ricerca dei migliori parametri con CV
	gs_CV = GridSearchCV(estimator=rfc, param_grid=param_grid)

	for ii in range(2):
		gs_CV.fit(Xtrain[ii], np.ravel(ytrain[ii]) )
		filename = "../../models/RFClassifier" + nomi_fasce_orarie[ii] + ".joblib"
		print(f"Score on test set: {gs_CV.score(Xtest[ii], ytest[ii])}")
		print(f"Score on train set: {gs_CV.score(Xtrain[ii], ytrain[ii])}")
		dump(gs_CV.best_estimator_, os.path.join(os.path.dirname(__file__),filename) )
	return 


def trainMLP():
	hls = (16,16)
	print(f"Alleno rete neurale di {len(hls)} layer. \nIl numero di neuroni in ogni layer è, in ordine:\n{hls}")
	NNW = MLPClassifier(hidden_layer_sizes=hls, solver='sgd' ) 
	
	for ii in range(2):
		filename = "../../models/NNWClassifier" + nomi_fasce_orarie[ii] + ".joblib"
		NNW.fit(Xtrain[ii], ytrain[ii])
		print(f"Score on test set: {NNW.score(Xtest[ii], ytest[ii])}")
		print(f"Score on train set: {NNW.score(Xtrain[ii], ytrain[ii])}")

		dump(NNW, os.path.join(os.path.dirname(__file__),filename) )
	return



def trainLogReg():
	print(f"Eseguo regressione logistica per classificazione")
	logreg = LogisticRegression()
	for ii in range(2):
		filename = "../../models/LRClassifier" + nomi_fasce_orarie[ii] + ".joblib"
		logreg.fit(Xtrain[ii], ytrain[ii])
		print(f"Score on test set: {logreg.score(Xtest[ii], ytest[ii])}")
		print(f"Score on train set: {logreg.score(Xtrain[ii], ytrain[ii])}")

		dump(logreg, os.path.join(os.path.dirname(__file__), filename) )
	return

def main():
	trainLogReg()
	trainMLP()
	trainRF()
	
	return


main()
