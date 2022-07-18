from datetime import date
from unittest import result
import sqlalchemy
import pandas as pd
import numpy as np
from numbers import Number

def createConnectionTodatabase():
    connectionToDB = sqlalchemy.create_engine('mysql://root@127.0.0.1/featuresdatabase')
    return connectionToDB

def main():
    choosedquery = 'AAPL'
    scrapetable = 'twitterdata'

    stocktable = 'stockdata'
    choosedstock = 'MSFT'

    x=  getDatesFromSelectedTableByKeyword(scrapetable ,choosedquery)
    y= getKeywordsByDatelist(stocktable,x)
    z = getDatesFromSelectedTableByKeyword(stocktable,choosedstock)
    a = decideWhichDatelistForBuildingDf(x, z)
    l = list()
    for date in a:
        b = selectDataFromTableOnDateAndKeyword(stocktable, date, choosedstock)
        c= selectDataFromTableOnDateAndKeyword(scrapetable, date, choosedquery)
        d=mergeTwoDataframeOnInterval(b,c)
        l.append(d)
    
    e= pd.concat(l) 
    insertIntoMysqlDatabase(e,table='dataforrunninglstm',status='replace')
    f= 1

######################## Liste Aller Dates die in bestimmter table (Stock oder Twitter), für bestimmtes keyword vorhanden sind
def getDatesFromSelectedTableByKeyword(table,keyword):
    mydb = createConnectionTodatabase()
    mycursor = mydb.execute("select date from "+table+" where keyword = '"+keyword+"';")
    myresult = mycursor.all()
    if not myresult:
        return False
    else:
        result = []
        for re in myresult:
            result.append(re[0])
        return  list(dict.fromkeys(result))

######################################### Liste aller keywords (welche Stock, welche Scrapingkeyword) für eine bestimmte Liste an dates (datelist) vorhanden sind.
######################################### Sprich für welche Keywords gibt es für definierten Zeitraum (datelist) auch Daten in der DB.
def getKeywordsByDatelist(table,datelist):
    mydb = createConnectionTodatabase()
    q = str(datelist)
    q = q[1:len(q)-1]
    mycursorOne = mydb.execute("select keyword, count(keyword) as sum from "+table+" group by keyword having sum > 50;")
    myresultOne = mycursorOne.all()
    resultOne = []
    for re in myresultOne:
        resultOne.append(re[0])
    p = str(resultOne)
    p = p[1:len(p)-1]
    mycursorTwo = mydb.execute("select keyword from "+table+" where date in ("+q+") and keyword in ("+p+");")
    myresult = mycursorTwo.all()
    if not myresult:
        return False
    else:
        result = []
        for re in myresult:
            result.append(re[0])
        return  list(dict.fromkeys(result))

######################################### Überprüft anhand welcher Datelist ein DataFrame gebaut werden soll, mit dem man später das LSTM trainieren kann.
def decideWhichDatelistForBuildingDf(datelistOne, datelistTwo):
    if len(datelistOne) == len(datelistTwo):
        return datelistOne
    if len(datelistOne) < len(datelistTwo):
        return datelistOne
    if len(datelistOne) > len(datelistTwo):
        return datelistTwo

######################################## Erstellt einen DataFrame aus einer Tabelle für ein bestimmtes Datum und ein bestimmtes keyword. 
def selectDataFromTableOnDateAndKeyword(table, date, keyword):
    mydb = createConnectionTodatabase()
    query = "SELECT * FROM "+table+" where date = '"+date+"' and keyword = '"+keyword+"';"
    df = pd.read_sql(query, con=mydb)
    return df
    
########################################### Merged aus zwei Dataframes (Stock und Twitterdaten) einen auf timestamp conditon, damit Daten konsistenz bleiben. 
def mergeTwoDataframeOnInterval(dfOne,dfTwo):
    df = pd.merge(dfOne,dfTwo, on='timestamp')
    df.drop(df.filter(regex='_y$').columns, axis=1, inplace=True)
    df.drop(df.filter(regex='_x$').columns, axis=1, inplace=True)
    return df

######################################## Methode mit der Daten des eines DataFrames in eine MySQL Tabelle überführen kann
def insertIntoMysqlDatabase(df,table,status):
    mydb = createConnectionTodatabase()
    df.to_sql(table, con=mydb, if_exists=status)

def selectAllDataFromDbToDf(tabel):
    mydb = createConnectionTodatabase()
    df = pd.read_sql('SELECT * FROM '+tabel+';', con=mydb)
    for column in df:
        u = df[column].dtype
        if not (u == np.float16) and not (u == np.float32)and not (u == np.float64)and not (u == np.int0)and not (u == np.int8)and not (u == np.int16)and not (u == np.int32)and not (u == np.int64)and not (u == np.double):
            df.drop(column, axis=1, inplace=True)
        else:
            if not (u == np.float64):
                df[column] = df[column].astype(np.float64)
    return df

def selectSertainColumnsFromTable(columns, table):
    mydb = createConnectionTodatabase()
    col = ', '.join(columns)
    query = 'SELECT '+col +' FROM '+table+';'
    df = pd.read_sql(query, con=mydb)
    for column in df:
        u = df[column].dtype
        if not (u == np.float16) and not (u == np.float32)and not (u == np.float64)and not (u == np.int0)and not (u == np.int8)and not (u == np.int16)and not (u == np.int32)and not (u == np.int64)and not (u == np.double):
            df.drop(column, axis=1, inplace=True)
        else:
            if not (u == np.float64):
                df[column] = df[column].astype(np.float64)
    return df

if __name__ == "__main__":
    main()




