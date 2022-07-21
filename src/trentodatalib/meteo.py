import pandas as pd 
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
try:
    meteo_df = pd.read_pickle( os.path.join(os.path.dirname(__file__),"../../data/interim/datiMeteo.pkl"))
    df_mappa_stazioni = pd.read_pickle( os.path.join(os.path.dirname(__file__),"../../data/interim/mappaStazioni.pkl"))
    gdfLineCells = pd.read_pickle( os.path.join(os.path.dirname(__file__),"../../data/interim/divisioneTerritori.pkl"))
except FileNotFoundError:
    print("Importazione dei file meteo non riuscita. Assicurarsi di aver creato i dataset di meteo e stazioni usando make_dataset_meteo.py")
else:
    print("Dati meteo importati correttamente!")
