Consumi Elettrici del Trentino
==============================

Progetto sull'analisi dati dei consumi elettrici della provincia di Trento e del comune di Trento.
Relativo all'esame del corso "Introduzione alla Data Science per fisici" dell'Università di Trento.
Autori del progetto: Anna Saiani, Gianmarco Puleo

## Riproduzione dei risultati

Clonare la repository ed eseguire i seguenti comandi su terminale bash. È necessario aver installato conda.

1. Per creare un ambiente conda con i pacchetti necessari eseguire il comando

		make requirements
		
   Questo crea un ambiente chiamato `DS_2022`. Attivarlo con
   
		conda activate DS_2022
   	
2. Eseguire 

		make data
	
per generare diversi file nel formato .pkl che contengono diversi dataframe 
relativi dati di meteo, consumi e inquinamento, separati. Vengono salvati nella cartella `data/interim`.
Una volta creati, essi possono essere velocemente importati eseguendo

		from trentodatalib import meteo, consumi, inquinamento
		
nello script python dove si vogliono usare.

3. Poi si possono creare i dataset per la classificazione e per la regressione eseguendo

		make features

   Questo crea i dataset desiderati e pronti per il training nella cartella `data/processed`, sempre nel formato .pkl
   
4. Una volta creati tutti i dataset si possono visualizzare i risultati, in un notebook o in una console iPython si possono importare i moduli contenuti in `src/visualization` ed eseguire le funzioni che sono contenute in essi. In particolare:
	+ `EDA_Trento.py` contiene due funzioni che plottano analisi dei consumi nelle due zone in cui è suddiviso trento
	+ `EDA_Provincia.py `mostra le correlazioni tra dati di meteo, consumi, inquinamento, su tutta la provincia.
	+ `mappe.py` contiene varie funzioni per il plot di mappe
	+ `classificazione.py` contiene funzioni per plot delle matrici di confusione dei classificatori
	+ `plotregression.py` esegue regressione lineare diverse volte variando il numero di features e visualizza i risultati.

5. Per allenare i modelli relativi a classificazione e regressione eseguire

		make train
		
   I modelli ricavati in questo training vengono esportati nel formato joblib nella cartella `./models`

## Repo structure
```
.
├── data
│   ├── external 
│   │   ├── APPA_inquinamento_aria_Nov_Dec_2013.csv
│   │   ├── Com01012013_WGS84.cpg
│   │   ├── Com01012013_WGS84.dbf
│   │   ├── Com01012013_WGS84.prj
│   │   ├── Com01012013_WGS84.shp
│   │   └── Com01012013_WGS84.shx
│   ├── interim
│   ├── processed
│   └── raw
│       ├── line.csv
│       ├── meteotrentino-weather-station-data.json
│       ├── SET-dec-2013.csv
│       ├── SET-nov-2013.csv
│       └── trentino-grid.geojson
├── DS_2022.yml  <-- conda image to reproduce result
├── LICENSE
├── Makefile
├── models
├── notebooks
│   ├── PresentazioneEDA.ipynb
│   ├── PresentazioneEDA.slides.html
├── requirements.txt
├── setup.py
├── src
│   ├── build_features_classification.py
│   ├── build_features_regression.py
│   ├── data
│   │   ├── make_dataset_consumi.py
│   │   ├── make_dataset_inquinamento.py
│   │   ├── make_dataset_meteo.py
│   │ 
│   ├── models
│   │   ├── predict_Model_Regression.py
│   │   ├── train_model_classification.py
│   │   └── train_model_regression.py
│   ├
│   ├── trentodatalib
│   │   ├── consumi.py
│   │   ├── funzioni.py
│   │   ├── __init__.py
│   │   ├── inquinamento.py
│   │   ├── meteo.py
│   │   ├── rawdatabase.py
│   │   ├── readme.txt
│   │   └── trentopaths.py
│   └── visualization
│       ├── classificazione.py
│       ├── EDA_provincia.py
│       ├── EDA_Trento.py
│       ├── __init__.py
│       ├── mappe.py
│       └── plotregression.py
└── test_environment.py
```

+ `data/external` contiene 
	1. dati dell'inquinamento scaricabili dal sito di **Agenzia Provinciale per la Protezione dell'Ambiente** (APPA)
	al link <https://bollettino.appa.tn.it/aria/scarica> . I dati partono dal 1 novembre 2013 e arrivano al 31 dicembre 2013.
	2. dati ISTAT relativi ai confini dei comuni italiani da cui si può estrarre il perimetro del comune di Trento. Disponibili su 
	<https://www.istat.it/it/archivio/222527> 

+ `data/raw` contiene dati provenienti dal dataset descritto nell'articolo **A multi-source dataset of urban life in the city of Milan and the Province of Trentino** (Barlacchi et al., Nature, 2015). Si possono scaricare liberamente da <https://dataverse.harvard.edu/dataverse/bigdatachallenge>


+ `src` contiene codice python per la riproduzione dei risultati
	1. `/data`: prima elaborazione dei dati corrispondente a `make data`
	2. `build_features_*.py` riproducono i dataset per training dei modelli. Eseguiti da `make features`.
	3. `/models` codici classificazione e regressione. Eseguiti da `make train`
	4. `/trentodatalib` è una libreria capace di importare facilmente i dataframe preparati con `make data` in uno script python.
	5. `/visualization` contiene diversi script per la visualizzazione di alcuni risultati

**NB**: Per l'esecuzione di alcuni codici in `/visualization` è necessario il pacchetto python `contextily`. Esso richiede una connessione a internet attiva per il download delle mappe al momento dell'esecuzione dei codici. Il pacchetto è presente nella conda image ma richiede anche altre librerie di sistema e potrebbe generare errori di tipo `ImportError`. Potrebbe essere necessario installare nel conda environment DS_2022 anche:

		conda install -c conda-forge libiconv

+ `notebooks` Contiene una breve presentazione del progetto con diversi grafici per visualizzare i risultati.


<p><small>Repository basata sul template <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project</a>. #cookiecutterdatascience</small></p>
