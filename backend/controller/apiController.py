from datetime import date
from xmlrpc.client import boolean
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import backend.services.featureEningering.featureEningering 
import backend.services.featureEningering.featureEningeringRepository
import backend.services.database.initDatabase
import backend.services.database.initFrontend 
import backend.services.neuronalNetworks.neuronalNetworkRepository
import backend.services.neuronalNetworks.pytorchlstm
import backend.services.visualization.visualisationRepository
import backend.services.database.overviewRepository

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

################## Klassenvariablen
stockdatelist = []
visudatelist = []
stocktickers = []
visutickers = []
features = []
visucolumn = []
goalvariable = []
randomColumns = []
randomHyperparams = []
overviewTable =  []


################################################################################################################################
############################# ONLOAD CALLS (ALLGEMEIN) #########################################################################
###################################################################################################################################
########################## Man muss die CSV local am richtigen Ort haben. pyDrive hätte den Rahmen gesprengt.
@app.get("/initdatabase")
def initDatabase():
    backend.services.database.initDatabase.initialize()

########################### Tabelle 
@app.get("/tables")
def tables():
   return {"tables":list(backend.services.database.initFrontend.getTablesFromDb())}

############################ für dropdown menue
@app.get("/stockinformation")
def stockinfo():
    df =  backend.services.database.initFrontend.getStocks()
    c = df.columns
    symbols = df[c[1]]
    stocknames = df[c[2]]
    return {"symbols":list(symbols) ,"stocknames":list(stocknames)}
    
###########################################################################################################################    
############ SCRAPING FORM REST CALLS ######################################################################################
############################################################################################################################
########## Scrapeformular mit Returnwert  Scraping Results
@app.get("/scrape/{queryForTwitterScraper}/{stock}/{start_date}/{end_date}")
async def read_item(queryForTwitterScraper: str, stock: str, start_date: str, end_date: str):
    inter = "30m"
    print("Datenbeschaffung gestartet.")
    backend.services.featureEningering.featureEningering.generateTwitterAndStockData(queryForTwitterScraper, stock, inter, start_date,end_date)
    return overviewForOnload()

#http://127.0.0.1:8000/overview
### Rest-Call für erstes Laden der Seite 
@app.get("/overview")
def overviewForOnload():
    df = backend.services.featureEningering.featureEningeringRepository.getInfoAboutNewScrapingResult()
    if not df.empty:
        stock = df.at[0, "stock"]
        keyword = df.at[0, "keyword"]
        days = int(df.at[0, "days"])
        rows = int(df.at[0, "rows"])
        return {"stock": stock,"keyword":keyword, "days":str(days), "rows":str(rows)}
    else:
        return {"stock": " ","keyword":" ", "days":" ", "rows":" "}

###########################################################################################################################    
############ LSTM FORM REST CALLS ######################################################################################
############################################################################################################################

################### Diese Methode auch bei Onload. Return Liste aller Tickers die mehr als 50 Einträge(ca 1 Woche an Daten) in DB haben 
#http://localhost:8000/getstocks
@app.get("/getstocks")
def getstocks():
    stockticker = backend.services.database.initFrontend.getListOfKeywordsInTable(table='stockdata')
    if stockticker:
        stockname = backend.services.database.initFrontend.stocknameForTicker(stockticker)
        y = list(stockname)
        y.reverse()
        if stockticker:
            return {"symbols":list(stockticker), "stocknames":y}
    else:
        replacementTicker = ["NAN"]
        replacementName = ["Your database is empty, please scrape first!"]
        y = list(replacementName)
        return {"symbols":list(replacementTicker), "stocknames":y}

####################################### Returned liste aus Tweetdatensätzen, die für gewählte stock zur verfügung stehen könnten
#http://localhost:8000/getscrape/MSFT
@app.get("/getscrape/{stockticker}")
def getscrape(stockticker: str):
    stocktickers.append(stockticker)
    datelist = backend.services.neuronalNetworks.neuronalNetworkRepository.getDatesFromSelectedTableByKeyword(table='stockdata',keyword=stockticker)
    stockdatelist.append(datelist)
    scrapelist = backend.services.neuronalNetworks.neuronalNetworkRepository.getKeywordsByDatelist(table='twitterdata',datelist=datelist)
    if scrapelist:
        return {"scrapekeywords":list(scrapelist)}
    else:
        replacementKeyword = ["Your database is empty, please scrape first!"]
        return {"scrapekeywords":list(replacementKeyword)}
    
########################################### Return Liste aus 
#http://localhost:8000/createdataframeformodel/AAPL
@app.get("/createdataframeformodel/{scrapekeyword}")
async def createdataframeformodel(scrapekeyword: str):
    scrapedatelist = backend.services.neuronalNetworks.neuronalNetworkRepository.getDatesFromSelectedTableByKeyword(table='twitterdata',keyword=scrapekeyword)
    datelistForDf = backend.services.neuronalNetworks.neuronalNetworkRepository.decideWhichDatelistForBuildingDf(scrapedatelist, stockdatelist[len(stockdatelist)-1])
    listOfDataframes = list()
    for date in datelistForDf:
        dfStockPerDate = backend.services.neuronalNetworks.neuronalNetworkRepository.selectDataFromTableOnDateAndKeyword('stockdata', date, stocktickers[len(stocktickers)-1])
        dfScrapePerDate= backend.services.neuronalNetworks.neuronalNetworkRepository.selectDataFromTableOnDateAndKeyword('twitterdata', date, scrapekeyword)
        merge=backend.services.neuronalNetworks.neuronalNetworkRepository.mergeTwoDataframeOnInterval(dfStockPerDate,dfScrapePerDate)
        listOfDataframes.append(merge)
    df = pd.concat(listOfDataframes) 
    backend.services.neuronalNetworks.neuronalNetworkRepository.insertIntoMysqlDatabase(df,table='dataforrunninglstm',status='replace')
    return {"columns":list(df.columns)}

@app.get("/selectecolumn/{colum}")
def selectecolumn(colum: str):
    features.append(colum)
    print(features)
    return {"lenght": len(features)}

@app.get("/dropcolumlist")
def dropcolumlist():
    if features:
        features.clear()

@app.get("/selectegoalvariable/{colum}")
def selectecolumn(colum: str):
    goalvariable.append(colum)
    print(goalvariable)

######################### beachten das liste entweder leer oder letzter eintrag false sein kann.
@app.get("/randomcolums/{column}")
def randomcolums(column: boolean):
    randomColumns.append(column)
    print(randomColumns)

######################### beachten das liste entweder leer oder letzter eintrag false sein kann.
@app.get("/randomhyperparams/{column}")
def randomcolums(column: boolean):
    randomHyperparams.append(column)
    print(randomHyperparams)

@app.get("/trainmodel/{epochs}/{layers}/{dropout}/{lerning}/{hidden}")
def trainmodel(epochs: int, layers: int, dropout: str,lerning: str, hidden: int):
    drop = float(dropout)
    lern = float(lerning)
    if (randomColumns and (randomColumns[len(randomColumns)-1]== False)) and (randomHyperparams and (randomHyperparams[len(randomHyperparams)-1]== False)):
        backend.services.neuronalNetworks.pytorchlstm.runLSTMdefinedFeaturesDefinedHyperpar(features,"dataforrunninglstm",goalvariable[len(goalvariable)-1],hidden,layers,drop,lern,epochs)
        print("Es wird ein Model trainiert mit ausgewählte Features und ausgewählten Hyperparametern.")
    if (not randomColumns) and (not randomHyperparams):
        backend.services.neuronalNetworks.pytorchlstm.runLSTMdefinedFeaturesDefinedHyperpar(features,"dataforrunninglstm",goalvariable[len(goalvariable)-1],hidden,layers,drop,lern,epochs)
        print("Es wird ein Model trainiert mit ausgewählte Features und ausgewählten Hyperparametern.")  
    if (randomColumns and (randomColumns[len(randomColumns)-1]== False)) and (not randomHyperparams):
        backend.services.neuronalNetworks.pytorchlstm.runLSTMdefinedFeaturesDefinedHyperpar(features,"dataforrunninglstm",goalvariable[len(goalvariable)-1],hidden,layers,drop,lern,epochs)
        print("Es wird ein Model trainiert mit ausgewählte Features und ausgewählten Hyperparametern.")
    if (not randomColumns) and (randomHyperparams and (randomHyperparams[len(randomHyperparams)-1]== False)):
        backend.services.neuronalNetworks.pytorchlstm.runLSTMdefinedFeaturesDefinedHyperpar(features,"dataforrunninglstm",goalvariable[len(goalvariable)-1],hidden,layers,drop,lern,epochs)
        print("Es wird ein Model trainiert mit ausgewählte Features und ausgewählten Hyperparametern.")
    if (randomColumns and (randomColumns[len(randomColumns)-1]== True)) and (randomHyperparams and (randomHyperparams[len(randomHyperparams)-1]== True)):
        backend.services.neuronalNetworks.pytorchlstm.runLstmRandomFeatureAndRandomHyperparameters("dataforrunninglstm")
        print("Es wird ein Model trainiert mit zufälligen Features und zufälligen Hyperparametern.")
    if (randomColumns and (randomColumns[len(randomColumns)-1]== True)) and (randomHyperparams and (randomHyperparams[len(randomHyperparams)-1]== False)):
        backend.services.neuronalNetworks.pytorchlstm.runLstmRandomFeaturesDefinedHyperpar("dataforrunninglstm",hidden,layers,drop,lern,epochs)
        print("Es wird ein Model trainiert mit zufälligen Features und ausgewählten Hyperparametern.")
    if (randomColumns and (randomColumns[len(randomColumns)-1]== True)) and (not randomHyperparams):
        backend.services.neuronalNetworks.pytorchlstm.runLstmRandomFeaturesDefinedHyperpar("dataforrunninglstm",hidden,layers,drop,lern,epochs)
        print("Es wird ein Model trainiert mit zufälligen Features und ausgewählten Hyperparametern.")
    if (randomColumns and (randomColumns[len(randomColumns)-1]== False)) and (randomHyperparams and (randomHyperparams[len(randomHyperparams)-1]== True)):
        backend.services.neuronalNetworks.pytorchlstm.runLstmSelectedFeatureAndRandomHyperparameters(features,"dataforrunninglstm",goalvariable[len(goalvariable)-1])
        print("Es wird ein Model trainiert mit zufälligen Hyperparametern und ausgewählten Features.")
    if (not randomColumns) and (randomHyperparams and (randomHyperparams[len(randomHyperparams)-1]== True)):
        backend.services.neuronalNetworks.pytorchlstm.runLstmSelectedFeatureAndRandomHyperparameters(features,"dataforrunninglstm",goalvariable[len(goalvariable)-1])
        print("Es wird ein Model trainiert mit zufälligen Hyperparametern und ausgewählten Features.")
    # backend.services.visualization.visuNN.plotNewTrainedLSTM()
    # ValueError: signal only works in main thread Has something to do with the threading of the application
    # thing the fast api runs on main thread and hast to stop, so matlibplot can use this thread for plt.show()
    features.clear()
    goalvariable.clear()
    randomColumns.clear()
    randomHyperparams.clear()

#######################################################################################################################################################################
#################################################################### Visualisation ####################################################################################
#######################################################################################################################################################################

#http://localhost:8000/getstocksvisu
@app.get("/getstocksvisu")
def getstocksvisu():
    stockticker = backend.services.visualization.visualisationRepository.getListOfKeywordsInTable(table='stockdata')
    if stockticker:
        stockname = backend.services.database.initFrontend.stocknameForTicker(stockticker)
        y = list(stockname)
        y.reverse()
        return {"symbols":list(stockticker), "stocknames":y}
    else:
        replacementTicker = ["NAN"]
        replacementName = ["Your database is empty, please scrape first!"]
        y = list(replacementName)
        return {"symbols":list(replacementTicker), "stocknames":y}

#http://localhost:8000/getscrapevisu/APLE
@app.get("/getscrapevisu/{stockticker}")
def getscrapevisu(stockticker: str):
    visutickers.append(stockticker)
    datelist = backend.services.visualization.visualisationRepository.getDatesFromSelectedTableByKeyword(table='stockdata',keyword=stockticker)
    visudatelist.append(datelist)
    scrapelist = backend.services.visualization.visualisationRepository.getKeywordsByDatelist(table='twitterdata',datelist=datelist)
    if scrapelist:
        return {"scrapekeywords":list(scrapelist)}
    else:
        replacementKeyword = ["Your database is empty, please scrape first!"]
        return {"scrapekeywords":list(replacementKeyword)}

@app.get("/createdataframeforvisu/{scrapekeyword}")
async def createdataframeforvisu(scrapekeyword: str):
    scrapedatelist = backend.services.neuronalNetworks.neuronalNetworkRepository.getDatesFromSelectedTableByKeyword(table='twitterdata',keyword=scrapekeyword)
    datelistForDf = backend.services.neuronalNetworks.neuronalNetworkRepository.decideWhichDatelistForBuildingDf(scrapedatelist, visudatelist[len(visudatelist)-1])
    listOfDataframes = list()
    for date in datelistForDf:
        dfStockPerDate = backend.services.neuronalNetworks.neuronalNetworkRepository.selectDataFromTableOnDateAndKeyword('stockdata', date, visutickers[len(visutickers)-1])
        dfScrapePerDate= backend.services.neuronalNetworks.neuronalNetworkRepository.selectDataFromTableOnDateAndKeyword('twitterdata', date, scrapekeyword)
        merge=backend.services.neuronalNetworks.neuronalNetworkRepository.mergeTwoDataframeOnInterval(dfStockPerDate,dfScrapePerDate)
        listOfDataframes.append(merge)
    df = pd.concat(listOfDataframes) 
    backend.services.neuronalNetworks.neuronalNetworkRepository.insertIntoMysqlDatabase(df,table='dataforvisu',status='replace')
    return {"columns":list(df.columns)}

@app.get("/dropcolumlistvisu")
def dropcolumlistvisu():
    if visucolumn:
        visucolumn.clear()


######################################################################################################################################################################################
############################################ Database Overview #######################################################################################################
##########################################################################################################################################################

@app.get("/table/{table}")
def keywordsFromTable(table:str):
    overviewTable.append(table)
    stockticker = backend.services.visualization.visualisationRepository.getListOfKeywordsInTable(table)
    if table == "stockdata":
        if stockticker:
            stockname = backend.services.database.initFrontend.stocknameForTicker(stockticker)
            y = list(stockname)
            y.reverse()
            return {"symbols":list(stockticker), "stockname":y}
        else:
            replacementTicker = ["NAN"]
            replacementName = ["Your database is empty, please scrape first!"]
            y = list(replacementName)
            return {"symbols":list(replacementTicker), "stockname":y}
    else:
        if stockticker:
            return {"symbols":list(stockticker), "stockname":list(stockticker)}
        else:
            replacementTicker = ["NAN"]
            replacementName = ["Your database is empty, please scrape first!"]
            y = list(replacementName)
            return {"symbols":list(replacementTicker), "stockname":y}


@app.get("/table/information/{keyword}")
def getInformationOv(keyword:str):
    days, rows, values = backend.services.database.overviewRepository.info(overviewTable[len(overviewTable)-1], keyword)
    return{"keywo":keyword,"days":days, "rows": rows, "values":values}














        
