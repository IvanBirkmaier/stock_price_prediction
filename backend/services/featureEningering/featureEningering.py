#Quelle:https://medium.com/dataseries/how-to-scrape-millions-of-tweets-using-snscrape-195ee3594721
from ast import keyword
from  backend.services.featureEningering.featureEningeringRepository import insertIntoMysqlDatabase,checkIfDatesAlreadyExists
#from  featureEningeringRepository import insertIntoMysqlDatabase, checkIfDatesAlreadyExists
import snscrape.modules.twitter as sntwitter
import pandas as pd
import re
import os
import statistics as st
from datetime import date, datetime
import numpy as np 
from textblob import TextBlob
import yfinance as yf
pd.options.mode.chained_assignment = None  

######################################### Klassenvariablen 
listOfDates = []
listInterval = []
listTotalnumbreOfTweetsPerInterval = []
listAverageNumbreOfTweetsPerMinutePerInterval = []
listMinTweetsPerMinute = []
listMaxTweetsPerMinute = []
listVarianceOfIntervall = []
listAverageCharacerPerTweet = []
listAverageSubjectivityPerTweet =[]
listAveragePolitarityPerTweet =[]
listOfNumbreOfPositivTweets = []
listOfNumbreOfNegativTweets = []
listShareOfPositiveTweets = []
listShareOfNegativTweets = []
listIntervalForwhichDataIsgenerate = []
listKeywordForWhatDataIsScraped = []

####################################### Main Methode um Scripte einzelnt ausführen zu können
def main():
    start_dt = "2022-06-06"
    end_dt = "2022-06-07"
    queryForTwitterScraper = 'Apple'
    stock = 'AAPL'    #Inputdaten für den Scraper und die                              
    inter='30m'       #yFinace-API um Daten zu generieren.    
    generateTwitterAndStockData(queryForTwitterScraper, stock, inter, start_dt,end_dt)

###############################     Scrapted Tweets nach AAPL Schlagwort     
#NOTIZ: Mit Array arbeiten in dem Strings vom BSP:'AAPL since:2022-05-04 until:2022-05-05' von verschiedenen Tagen drin liegen um werte mit Schleife
#dann dem enumerate Befehl zu übergeben. Eventuell String aus mehreren Bausteinen zusammenbauen vllt mit Datetim.datetime.date().now() und dann nur Wochentage beachten
def generateTwitterAndStockData(queryForTwitterScraper, stock, inter, start_date,end_date):
    stockData = yf.download(stock, start=start_date, end= end_date, interval=inter, auto_adjust= True, prepost=True)
    stockData = stockData[:-1]
    if not stockData.empty:
        days = list(stockData.index.strftime("%Y-%m-%d")) 
        listOfInterval = list(stockData.index.strftime("%H:%M:%S"))
        daysAndIntervals = pd.DataFrame({'date': days, 'timestamp':listOfInterval})
        stocksDf = daysAndIntervals.reset_index(drop=True).merge(stockData.reset_index(drop=True), left_index=True, right_index=True)
        stocksDf["keyword"] = stock
        stocksDf["inter"] = inter
        datesForIterate = list(dict.fromkeys(days))
        tweets = []
        listOfStocksDfsPerDay = list()
        if not datesForIterate:
            print("Vom "+start_date+" bis zum "+end_date+" war die Amerikanische Börse geschlossen. Daher wurden keine Daten für diesen Zeitraum erhoben.")
        else:
            for elem in datesForIterate:
                stocktable = 'stockdata'
                stockExist = checkIfDatesAlreadyExists(stocktable,elem,stock,inter)
                if not stockExist:
                    listOfStocksDfsPerDay.append(stocksDf.loc[(stocksDf['date'] == elem)&(stocksDf['timestamp']>='09:30:00')&(stocksDf['timestamp']<='16:00:00')].reset_index(drop=True))
                scrapeTable = 'twitterdata'
                scrapeExist = checkIfDatesAlreadyExists(scrapeTable,elem,queryForTwitterScraper,inter)
                if not scrapeExist:
                    listForIntervals = daysAndIntervals.loc[(daysAndIntervals['date'] == elem)&(daysAndIntervals['timestamp']>='09:00:00')&(daysAndIntervals['timestamp']<='16:00:00')].reset_index(drop=True)
                    listForIntervals = listForIntervals['timestamp']
                    end_d = addEndScrapeDay(elem)
                    scrape = queryForTwitterScraper+' since:'+elem+' until:'+end_d
                    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(scrape).get_items()):
                        tweets.append([tweet.date.strftime("%H:%M:%S"),tweet.content])
                    df = pd.DataFrame(tweets, columns=['timestamp', 'tweet'])
                    createAllFeatures(splitIntoIntervale(regexTweetsDeleteEmptyTweets(prepareDataframeForTraidingDay(df, listForIntervals)),listForIntervals), elem,inter,queryForTwitterScraper)
            datadf = generateFeatureDf()
            if not datadf.empty:
                createFeatureCsvAndInsertToDb(datadf)
                informationAboutGeneratedData(datadf, inter,stock, start_date, end_date, queryForTwitterScraper)
                listOfDates.clear()
                listInterval.clear()
                listTotalnumbreOfTweetsPerInterval.clear()
                listAverageNumbreOfTweetsPerMinutePerInterval.clear()
                listMinTweetsPerMinute.clear()
                listMaxTweetsPerMinute.clear()
                listVarianceOfIntervall.clear()
                listAverageCharacerPerTweet.clear()
                listAverageSubjectivityPerTweet.clear()
                listAveragePolitarityPerTweet.clear()
                listOfNumbreOfPositivTweets.clear()
                listOfNumbreOfNegativTweets.clear()
                listShareOfPositiveTweets.clear()
                listShareOfNegativTweets.clear()
                listIntervalForwhichDataIsgenerate.clear()
                listKeywordForWhatDataIsScraped.clear()
                print("Twitter-Datenerhebung für das Keyword: "+queryForTwitterScraper+" und den Zeitraum von "+start_date+" bis "+end_date+" würden erfogreich abgeschlossen!") 
            else:
                print("Twitterdaten für das Keyword: "+queryForTwitterScraper+" und den Zeitraum von "+start_date+" bis "+end_date+"  sind bereits in Datenbank vorhanden. Kein Duplikat erstellt") 
            if listOfStocksDfsPerDay:
                insertStockToDb(listOfStocksDfsPerDay)
                print("Aktien-Datenerhebung für die Aktie mit dem Ticker: "+stock+" und den Zeitraum von "+start_date+" bis "+end_date+" würden erfogreich abgeschlossen!")
            else:
                print("Aktiendaten für die Aktie mit dem Ticker: "+stock+" und den Zeitraum von "+start_date+" bis "+end_date+"  sind bereits in Datenbank vorhanden. Kein Duplikat erstellt") 
    else:    
         print("Für die von Ihnen gwählte Aktzie mit dem Ticker: "+stock+" und den Zeitraum von "+start_date+" bis "+end_date+"  liegen uns keine Daten vor. Bitte versuchen Sie eine andere Aktzie aus.") 

#############################################################################################################################################
####################################################### STOCK ###############################################################################
#############################################################################################################################################

############################# Speichert Stockdaten in Datenbank
def insertStockToDb(listOfStocksDfsPerDay):
    for elem in listOfStocksDfsPerDay:
        insertIntoMysqlDatabase(elem, table='stockdata', status='append')

##################################################################################################################################################
####################################################################### TWITTER ##################################################################
##################################################################################################################################################

################################     Erstellt Dataframe aus Tweets und schneidet diesen für 1 Tag zurecht.                  
def prepareDataframeForTraidingDay(dftweets, listForIntervals):
    allTweets_cutAllTweetsOversixtheenOClock = dftweets.loc[(dftweets['timestamp']<= listForIntervals[len(listForIntervals)-1])]
    tweets = allTweets_cutAllTweetsOversixtheenOClock.loc[(allTweets_cutAllTweetsOversixtheenOClock['timestamp']>= listForIntervals[0])]
    return tweets

################################     Entfernt aus einheitlichen Dataframes     
################################     alle Links, Hashtags und @Mentions.       
def regexTweetsDeleteEmptyTweets(tweets):
    listlenghtOfTweetsCharcer = []
    listsubjectivityScoreOfTweets = []
    listpolitarityScoreOfTweets = []
    listpositvOrnegativ = []
    for tweet in tweets['tweet']:
        clean_tweet = re.sub(r"(?:\@|https?\://)\S+", "", tweet)
        clean_tweet = re.sub("#","", clean_tweet)
        if not clean_tweet.isspace():
            tweets.loc[tweets['tweet']==tweet, 'tweet']=clean_tweet
    
    for tweet in tweets['tweet']:
        lenghtOfTweetsCharcer, subjectivityScoreOfTweets, politarityScoreOfTweets, positvOrnegativ = sentimelAnalyseAndLenghtOfTweet(tweet)
        listlenghtOfTweetsCharcer.append(lenghtOfTweetsCharcer)
        listsubjectivityScoreOfTweets.append(subjectivityScoreOfTweets)
        listpolitarityScoreOfTweets.append(politarityScoreOfTweets)
        listpositvOrnegativ.append(positvOrnegativ)                              
    tweets = tweets.assign(charactersPerTweet=listlenghtOfTweetsCharcer)
    tweets = tweets.assign(subjectivityScoreOfTweet=listsubjectivityScoreOfTweets)
    tweets = tweets.assign(politarityScoreOfTweet=listpolitarityScoreOfTweets)
    tweets = tweets.assign(positvOrnegativScore=listpositvOrnegativ)
    return tweets

###############################     Errechnet Columne "LängeDerTweets", sowie mit Textblob weitere Kennzahlen hinzu, aus denen später ein Durchschnitt           
###############################     errechnet wird.  
def sentimelAnalyseAndLenghtOfTweet(newtweet):
    lenghtOfTweetsCharcer = len(newtweet)
    blob = TextBlob(newtweet)
    po = blob.sentiment.polarity
    subjectivityScoreOfTweets = blob.sentiment.subjectivity
    politarityScoreOfTweets =po 
    if po < 0:
        positvOrnegativ ="Negativ"
    elif po > 0:
        positvOrnegativ= "Positiv"
    elif po == 0:
        positvOrnegativ ="Neutral"
    return   lenghtOfTweetsCharcer, subjectivityScoreOfTweets, politarityScoreOfTweets, positvOrnegativ 
  
############################# Erstellt aus in Methode: defineTimeIntervalsForTraidingDay definierte 30min Intervale eine Liste aus Dataframes pro Interval    
def splitIntoIntervale(tweets, intervals):
    dfs = {}
    for index, interval in enumerate(intervals):
        if (index+1 < len(intervals)):
            cutTweetsInIntervall = tweets.loc[(tweets['timestamp']>= interval)]
            nextinterval = intervals[index+1]
            dfs[nextinterval] = cutTweetsInIntervall.loc[(cutTweetsInIntervall['timestamp']< nextinterval)]
    return dfs

######     Zählt alle Tweets in einem 30min Intervall und leitet Durchschnittstweets pro 1 Minute ab.                   
######     Errechnet den Max. und Min. Wert für alle kleinen 1 Minuten "SubIntervalle". Berechnet den Durchschnittslänge aller    
######     Tweets in einem 30 min Intervall. Berechnet die Varianz der 1 Min Intervalle.                               
######     Erstellt aus diesen Werten einen neuen Datframe mit den Featurewerten.           
def createAllFeatures(dfs, start_date,inter,queryForTwitterScraper):
    for df in dfs:
        if not dfs[df].empty: 
            listOfDates.append(start_date)
            listInterval.append(df)
            totalnumbreOfTweetsPerInterval = len(dfs[df]) 
            listTotalnumbreOfTweetsPerInterval.append(totalnumbreOfTweetsPerInterval)
            averageNumbreOfTweetsPerMinutePerInterval = totalnumbreOfTweetsPerInterval/30
            listAverageNumbreOfTweetsPerMinutePerInterval.append(averageNumbreOfTweetsPerMinutePerInterval)
            dfs[df]['timestamp'] = pd.to_datetime(dfs[df]['timestamp'])
            minutesplit = [g for n, g in dfs[df].groupby(pd.Grouper(key='timestamp',freq='1Min'))]
            listForCheckingMaxandMin = []
            for split in minutesplit:
                if split.empty:
                    minTweetsPerMinute = 0
                    listForCheckingMaxandMin.append(minTweetsPerMinute)
                else:
                    sizeOfDataFrame = len(split)
                    listForCheckingMaxandMin.append(sizeOfDataFrame)
            positivTweets = []
            negativTweets = []
            listMinTweetsPerMinute.append(min(listForCheckingMaxandMin))
            listMaxTweetsPerMinute.append(max(listForCheckingMaxandMin))
            averageCharacerPerTweet = st.mean(dfs[df]['charactersPerTweet'])
            averageSubPerTweet = st.mean(dfs[df]['subjectivityScoreOfTweet'])
            averagePobPerTweet = st.mean(dfs[df]['politarityScoreOfTweet'])
            positivTweets = dfs[df][dfs[df]['positvOrnegativScore'] == 'Positiv']
            negativTweets = dfs[df][dfs[df]['positvOrnegativScore']== 'Negativ']
            numberOfNegativTweets = len(negativTweets)
            numberOfPositivTweets=len(positivTweets)
            divPoWithTotal = numberOfPositivTweets/totalnumbreOfTweetsPerInterval
            sharePoToTotal = divPoWithTotal * 100
            divNegWithTotal = numberOfNegativTweets/totalnumbreOfTweetsPerInterval
            shareNegToTotal = divNegWithTotal * 100
            varianceOfIntervall = np.var(listForCheckingMaxandMin)
            listVarianceOfIntervall.append(varianceOfIntervall)
            listAverageCharacerPerTweet.append(averageCharacerPerTweet)
            listAverageSubjectivityPerTweet.append(averageSubPerTweet)
            listAveragePolitarityPerTweet.append(averagePobPerTweet)
            listOfNumbreOfPositivTweets.append(numberOfPositivTweets)
            listOfNumbreOfNegativTweets.append(numberOfNegativTweets)
            listShareOfPositiveTweets.append(sharePoToTotal)
            listShareOfNegativTweets.append(shareNegToTotal)
            listIntervalForwhichDataIsgenerate.append(inter)
            listKeywordForWhatDataIsScraped.append(queryForTwitterScraper)

########################### Dataframe für Twitter Daten
def generateFeatureDf():
    featureDatas = pd.DataFrame(list(zip(listOfDates,listInterval,listKeywordForWhatDataIsScraped,listIntervalForwhichDataIsgenerate,listTotalnumbreOfTweetsPerInterval,listAverageNumbreOfTweetsPerMinutePerInterval,listMinTweetsPerMinute,listMaxTweetsPerMinute,listVarianceOfIntervall,
                    listAverageCharacerPerTweet, listAverageSubjectivityPerTweet, listAveragePolitarityPerTweet,listOfNumbreOfPositivTweets,listShareOfPositiveTweets,listOfNumbreOfNegativTweets,listShareOfNegativTweets)), 
                                            columns = ['date','timestamp','keyword','inter','total_number_of_tweets_in_interval', 'average_tweets_per_minute_in_interval', 'min_tweets_per_minute', 'max_tweets_per_minute', 'volatility_of_amount_of_tweets_per_minute',
                                            'average_lenght_of_character_of_tweets_in_interval', 'average_subjectivity_of_tweets_in_intervall', 'average_polarity_of_tweets_in_interval', 'numbre_of_all_positiv_tweets_per_interval', 'share_of_positiv_tweets_from_total_tweets_per_interval', 'numbre_of_all_negativ_tweets_per_interval', 'share_of_negativ_tweets_from_total_tweets_per_interval'])
    return featureDatas
    
#############################      Erstellt eine CSV aus allen Featurelisten. BITTE PATH VATIABLE ANPASSEN
def createFeatureCsvAndInsertToDb(featureDatas):
    #path = '/Users/Ivan/Desktop/stock-price-predictions-with-lstm-neural-networks-and-twitter-sentiment/data/test.csv' 
    #featureDatas.to_csv(path, mode='a', header=not os.path.exists(path))
    insertIntoMysqlDatabase(featureDatas, table='twitterdata', status='append')

################################################################################################################################################################
######################################################## Allgemein ###########################################################################################
################################################################################################################################################################

################################### Dataframe für Stock result
def informationAboutGeneratedData(df, inter,stock, froM, to, query):
    days = len(df.groupby("date"))
    rows = len(df)
    #features = len(df.columns)
    inter = inter
    froM = froM
    to = to
    dflist= [stock,query,days,rows]
    dfinfonewscrapingresult = pd.DataFrame([dflist], 
     columns=["stock", "keyword", "days","rows"])
    insertIntoMysqlDatabase(dfinfonewscrapingresult, table='scrapingresults', status='replace')

#################################### Fügt ein extra Datum hinzu um Scrapingzeitraum an Stockapi call anzupassen.
def addEndScrapeDay(elem):
    c = len(elem)
    c2 = c - 2
    c3 = elem[c2:c]
    c4 = int(c3) + 1
    c5 = str(c4)
    c6 = elem[0:c2]+c5
    return c6

if __name__ == "__main__":
    main()
