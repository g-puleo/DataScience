import sys, os    
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from trentodatalib import trentopaths as tpath
from trentodatalib import rawdatabase as rawdata
from trentodatalib import funzioni as fz
import pandas as pd
import numpy as np

#divido il database in train e test
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from joblib import dump, load


# devo importare i modelli salvati con load 

modello1 = load('../../models/modelreg_giornoTN.sav')
modello2 = load('../../models/modelreg_seraTN.sav')
modello3 = load('../../models/modelreg_giornoprov.sav')
modello4 = load('../../models/modelreg_seraprov.sav')

# adesso dovrei provare a vedere lo score sui dati di test, ma i dati di test sono nell'altro file... 

