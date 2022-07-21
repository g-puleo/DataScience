DataScience
==============================

Progetto sull'analisi dati dei consumi elettrici della provincia di Trento

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be im
    │
    └─ src                <- Source code for use in this project.
       ├── __init__.py    <- Makes src a Python module
       │
       ├── data           <- Scripts to download or generate data
       │   └── make_dataset_meteo.py
       | 
       │
       ├── features       <- Scripts to turn raw data into features for modeling
       │   └── build_features.py
       │
       ├── models         <- Scripts to train models and then use trained models to make
       │   │                 predictions
       │   ├── predict_model.py
       │   └── train_model.py
       │
       └── visualization  <- Scripts to create exploratory and results oriented visualizations
           └── visualize.py


--------

## Riproduzione dei risultati

1. Prima di tutto eseguire 
	`python3 src/data/make_dataset_meteo.py`
	`python3 src/data/make_dataset_consumi.py`
	`python3 src/data/make_dataset_inquinamento.py`

   Questo salva dei dataframe elaborati in formato .pkl nella cartella data/interim.
   Una volta creati, essi possono essere velocemente importati usando
   	`from trentodatalib import meteo, consumi, inquinamento`

2. Poi si può creare il dataset per la classificazione eseguendo
	`python3 src/make_dataset_classification.py` .
   Questo crea il dataset nella cartella data/processed, sempre nel formato .pkl
   
3. Una volta creati tutti i dataset la visualizzazione dei risultati, in un notebook o in una console iPython, si possono importare i moduli contenuti in src/visualization ed eseguire le funzioni che sono contenute in essi. In particolare:
	+ EDA_Trento.py contiene due funzioni che plottano analisi dei consumi nelle due zone in cui è suddiviso trento
	+ mappe.py contiene varie funzioni che plottano le mappe
	
<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
