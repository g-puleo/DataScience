import pandas as pd 
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
try:
    dfInqTrento = pd.read_pickle( os.path.join(os.path.dirname(__file__),"../../data/interim/datiInquinamento.pkl"))
    df_inquinamento = pd.read_pickle(  os.path.join(os.path.dirname(__file__),"../../data/interim/datiTotInquinamento.pkl") )
except FileNotFoundError:
    print("Importazione dei file inquinamento non riuscita. Assicurarsi di aver creato i dataset dell'inquinamento usando make_dataset_inquinamento.py")
    
else: print("Dati inquinamento importati correttamente!")
