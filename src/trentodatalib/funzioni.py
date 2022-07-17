#questo file sarà come una libreria di funzioni editate e scritte da noi 

def genera_mappa_consumi( datiConsumi, df_linee, grid ):
    ''' Restituisce GeoDataFrame per il plot di una mappa in scala di colore a partire dai dati relativi ai consumi.
        Inputs:
            
            datiConsumi:pd.DataFrame che contiene colonna con i codici di linea (LINESET) e i rispettivi consumi
            registrati in un certo giorno e orario.
            
            df_linee: pd.DataFrame che contiene: codici linea, celle per cui passa la linea,
            e nr. di utenze in quella cella.
            
            grid: gpd.GeoDataFrame che contiene le celle in cui è suddiviso il territorio come istanze della classe
                  Polygon (from shapely.geometry)
            
         Returns: 
         
            df_mappa: gpd.GeoDataFrame con il consumo totale su ogni cella del territorio trentino. 
            Totale nel senso di sommato su tutto il periodo del DataFrame datiConsumi .
         '''
    #contiamo le ubicazioni per linea
    df_ubi_per_line = pd.DataFrame(df_linee.groupby('LINESET')['NR_UBICAZIONI'].sum()).reset_index()
    #contiamo i consumi per linea
    df_con_per_line = pd.DataFrame( datiConsumi.groupby('LINESET')['consumi'].sum() ).reset_index()
    #uniamo i due dataframe
    df_consperub = pd.merge(left = df_con_per_line, right = df_ubi_per_line, how = 'outer',on='LINESET' )
    df_consperub = df_consperub.fillna(0)
    #calcolo dei consumi per ubicazione
    df_consperub['cons_per_ubi'] = df_consperub['consumi'] / df_consperub['NR_UBICAZIONI']
    #unisco al dataframe con le linee e le rispettive celle
    df_cons_per_cella = pd.merge(left = df_linee, right = df_consperub[['LINESET','cons_per_ubi']], how = 'outer',on='LINESET')
    df_cons_per_cella['consumo_per_cella'] = df_cons_per_cella['NR_UBICAZIONI']*df_cons_per_cella['cons_per_ubi']
    #sommo i consumi della stessa cella (diverse linee)
    df_cons_per_cella = pd.DataFrame(df_cons_per_cella.groupby('SQUAREID')['consumo_per_cella'].sum() ).reset_index()
    #finalmente unisco tutto al dataframe della mappa che viene ritornato
    df_mappa = pd.merge(left = grid, right = df_cons_per_cella, how = 'left', left_on='id', right_on='SQUAREID')
    df_mappa['consumo_per_cella'] = df_mappa['consumo_per_cella'].fillna(0)
    return df_mappa



#### Creo funzione per assegnare ad ogni dataframe con dataeora delle ulteriori colonne, che mi dicono: 
#    Il giorno della settimana
#    La fascia oraria ('giorno', 'sera') 

def categorizza_tempo( df ):
    ''' Categorizza la serie temporale di un dataframe. 
        Prende in input un pd.DataFrame che deve avere una colonna 'datetime' nel formato datetime di pandas. Restituisce un dataframe con aggiunte le colonne:
        'TimeRange': 'day' se l'orario è tra le 8:00 (Incluse) e le 19:00 (escluse)
                     'evening' se tra le 19:00 (incluse) e le 24:00(escluse) 
                     'night' negli altri casi
        'isWeekend': bool che identifica se il giorno della settimana è weekend o meno '''
    
    #divido le fasce orarie
    df.loc[(df['datetime'].dt.hour >= 8) & (df['datetime'].dt.hour < 19), 'TimeRange'] = 'day'
    df.loc[(df['datetime'].dt.hour >= 19) & (df['datetime'].dt.hour < 24), 'TimeRange'] = 'evening'
    df['TimeRange'].fillna('night', inplace=True) 
    
    #distinguo giorni della settimana
    df.loc[df['datetime'].dt.weekday >=5, 'isWeekend'] = True
    df['isWeekend'].fillna(False, inplace=True)
    return df
    
def categorizza_consumi( df, consumiColName ):
    '''Categorizza le righe di un pd.DataFrame in base al consumo utilizzando primo e terzo quartile
        detti firstQ e thirdQ rispettivamente.
        Inputs:  

            df: dataframe da categorizzare        
            consumiColName: nome della colonna contenente i consumi
        
        Outputs:
        
        pd.DataFrame uguale a df con l'aggiunta di una colonna 'FASCIA_CONSUMI' che contiene
        0 se df[consumiColName]<firstQ
        1 se firstQ <= df[consumiColName] < thirdQ 
        2 se thirdQ <= df[consumiColName]'''
    
    firstQ = df[ consumiColName ].quantile(q=0.25, interpolation='linear')
    thirdQ = df[ consumiColName ].quantile(q=0.75, interpolation='linear')

    df.loc[(df[consumiColName] >= firstQ) & (df[consumiColName]< thirdQ) , 'FASCIA_CONSUMI'] = 1
    df.loc[(df[consumiColName] >= thirdQ), 'FASCIA_CONSUMI'] = 2
    df['FASCIA_CONSUMI'].fillna(0, inplace=True) 
    
    return df
    
    
def addNextDay( dfTN , cols2drop): 
    '''questa funzione serve per creare dedi database adatti ad essere sottoposti a classificazione o regressione Quello che fa è affiancare la riga x+1 alla riga x, così che il database restituito presenta i dati riferiti a coppie di giorni consecutivi'''
    dfTN['dayOfWeek'] = dfTN['date'].apply(datetime.weekday)
    #dataframe temporaneo che contiene dati da shiftare di una riga
    
    dfTN_xp1 = dfTN.copy()
    
    #preparo per join dei dataframes
    print('DEBUG')
    print(dfTN_xp1.iloc[0,:] )
    dfTN_xp1 = dfTN_xp1.drop(labels=0, axis=0).reset_index(drop=True)
    dfTN = dfTN.drop(dfTN.tail(1).index).reset_index(drop=True)
    
    #unisco i dataframe
    dfTN = dfTN.join(dfTN_xp1, lsuffix = '_x', rsuffix='_x+1')
    #tolgo righe brutte (x=venerdì, x+1=lunedì, non ci interessano)
    rowsToDrop = dfTN[ ( dfTN['dayOfWeek_x'] == 4 ) & ( dfTN['dayOfWeek_x+1']==0 )  ].index
    rowsToKeep = dfTN[ (( dfTN['dayOfWeek_x'] == 0 ) & ( dfTN['dayOfWeek_x+1']==1 ) )
                               | ( ( dfTN['dayOfWeek_x'] == 2) & ( dfTN['dayOfWeek_x+1']==3 ) )].index
    dfTN.drop( rowsToDrop , axis=0, inplace=True ) 
    #ora il df è pronto per il fit, o quasi (bisogna togliere colonne inutili) 
    
    dfTN.drop(columns = cols2drop , inplace=True)    
    
    return dfTN
## al momento decido di inserire anche le funzioni riguardante le regressione 

def regressioneLineare( df_in, feat, targ, talk=False ) : 

    Xtrain, Xtest, Ytrain, Ytest = train_test_split(df_in[feat], df_in[targ], test_size = 0.30, random_state = 7)
    #adesso scalo i dati con lo standard scaler
    ppl = Pipeline(  [ ('scaler', StandardScaler() ) , ('clf', LinearRegression() ) ] ) 
    ppl.fit(Xtrain, Ytrain) 
    #Ypred = ppl.predict(Xtest)
    trainScore= ppl.score(Xtrain, Ytrain)
    testScore = ppl.score(Xtest, Ytest)
    if talk:
        print(f"score on train is = {trainScore}")
        print(f"score on test is = {testScore}")
    return (trainScore, testScore)


