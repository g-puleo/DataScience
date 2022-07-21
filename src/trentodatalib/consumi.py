import pandas as pd 
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from trentodatalib import trentopaths as tpath

df_linee = pd.read_csv(os.path.join( os.path.dirname(__file__), tpath.raw_data_path , tpath.filenames['SET-lines']) ) 


try:
    df_consumidiurni = pd.read_pickle( os.path.join(os.path.dirname(__file__),"../../data/interim/datiConsumiDiurniLordi.pkl"))
    df_consuminotturni = pd.read_pickle( os.path.join(os.path.dirname(__file__),"../../data/interim/datiConsumiNotturniLordi.pkl"))
    df_consumisettimana = pd.read_pickle( os.path.join(os.path.dirname(__file__),"../../data/interim/datiConsumiInfrasetLordi.pkl" ) )
    df_consumiweekend = pd.read_pickle( os.path.join(os.path.dirname(__file__), "../../data/interim/datiConsumiWkndLordi.pkl" ) )
    df_consumi = pd.read_pickle(  os.path.join(os.path.dirname(__file__),"../../data/interim/datiConsumi.pkl") )
except FileNotFoundError:
    print("Importazione dei file consumi non riuscita. Assicurarsi di aver creato i dataset usando make_dataset_consumi.py")
else:
    print("Dati consumi importati correttamente!")

