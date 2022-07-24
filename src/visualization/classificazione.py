import matplotlib.pyplot as plt 
import pandas as pd
import seaborn as sns 
import os
from joblib import load
import json
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler

def confMat(classifier_name = "RF", subset="train"):
	'''plot confusion matrices of trained classifiers.
		Inputs:
			classifier_name: name of the classifier used. Possible names are:
			"RF": RandomForest classifier
			"NNW": NeuralNetwork classifier
			"LR": LogisticRegression classifier.
			subset:	choose wether to use train or test data to generate the plot. 
			"train": use the train data
			"test": use the test data
	'''
	print(f"Performance del classificatore {classifier_name} sull'insieme {subset}.")
	nomi_fasce_orarie = ['Day', 'Ev']
	fasce = ['giorno (08:00-19:00)', 'sera (19:00-24:00)', 'notte (00:00-08:00)']

	idx = []
	dfFasceOrarie = []
	clf = []
	X =  []
	Y = []


	# loop per importare indici (relativi a train e test), dati  e modelli già allenati. 
	# se non ci riesco restituisco messaggio di errore.
	for ii in range(2):
		#setto i nomi file 
		filename = "../../models/" + classifier_name + "Classifier" + nomi_fasce_orarie[ii] + ".joblib"
		idxfilename = "../../models/splitIndexClassificazione" + nomi_fasce_orarie[ii] + "_" + subset + ".csv"
		#print(os.path.join(os.path.dirname(__file__),filename))
		try:
			idxSeries = pd.read_csv(os.path.join(os.path.dirname(__file__), idxfilename ))
			clf.append( load(os.path.join(os.path.join(os.path.dirname(__file__),filename)) ) )
			dfFasceOrarie.append( pd.read_pickle( os.path.join(os.path.dirname(__file__),
				"../../data/processed/datiTrento"+nomi_fasce_orarie[ii]+".pkl")))
			#importo anche un dizionario che contiene una lista di features.
			with open(os.path.join(os.path.dirname(__file__),'../../models/features.json') ) as fp:
				feat_target_dict = json.load( fp )

		except FileNotFoundError:
			print("Impossibile trovare modelli del classificatore " + classifier_name + 
				". Assicurarsi di aver allenato i classificatori con src/models/trainModelClassification.py")
		
		#salvo gli indici nel formato giusto
		idx.append(pd.Index(idxSeries.iloc[:,1]))

		#riscalo dati X usando insieme di train
		scaler = StandardScaler()
		
		if subset=="train":
			X_tmp = dfFasceOrarie[ii][feat_target_dict['features']].loc[idx[ii]]   
		if subset=="test":
			X_tmp = dfFasceOrarie[ii][feat_target_dict['features']].loc[~dfFasceOrarie[ii].index.isin(idx[ii])]   

		scaler.fit(X_tmp)
		#assegno a X[ii] e Y[ii] la parte di dataframe che mi interessa
		X.append( scaler.transform( dfFasceOrarie[ii][feat_target_dict['features']].loc[idx[ii]] )  )
		Y.append( dfFasceOrarie[ii][feat_target_dict['target']].loc[idx[ii]] )

## finita l'importazione dei files e degli indici corretti, plotto le matrici di confusione. 
	fig, axs = plt.subplots(1, 2, figsize=(14,6) ) 

	for ii in range(2):
		ypredicted = clf[ii].predict(X[ii])
		cmat = confusion_matrix( ypredicted, Y[ii])
		sns.heatmap(cmat, cmap=plt.cm.Greens, ax=axs[ii], annot=True)
		axs[ii].set_title(fasce[ii])
		print(f"Lo score sui dati della fascia oraria {fasce[ii]} è {round(clf[ii].score(X[ii],Y[ii]),2)}")

	fig.suptitle(f"Matrici di confusione classificatore {classifier_name} su insieme {subset}")
	
	plt.show()
	return
	#print(idx_test)
