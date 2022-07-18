import sqlalchemy
import pandas as pd
import sqlalchemy
import numpy as np

def main():
    x= checkIfDatesAlreadyExists('stockdata','2022-06-13','AAPL','30m')
    print(x)

######################################## Erstellt Connection zu Datenbankschema: featuresdatabase
def createConnectionTodatabase():
    connectionToDB = sqlalchemy.create_engine('mysql://root@127.0.0.1/featuresdatabase')
    return connectionToDB

######################################## Methode mit der Daten des eines DataFrames in eine MySQL Tabelle überführen kann
def insertIntoMysqlDatabase(df,table,status):
    mydb = createConnectionTodatabase()
    df.to_sql(table, con=mydb, if_exists=status)

######################################## Methode überprüft, ob bestimmte Tabellen existiern und wenn sie existieren, ob bestimmte Werte breits in der Tabelle vorhanden sind
def checkIfDatesAlreadyExists(table,date,keyword,inter):
    mydb = createConnectionTodatabase()
    mycursor = mydb.execute("SHOW TABLES LIKE '"+table+"';")
    myresult = mycursor.all()
    if not myresult:
        return False
    else: 
        mycursor = mydb.execute("select date from "+table+" where date = '"+date+"' and keyword = '"+keyword+"' and inter = '"+inter+"';")
        myresult = mycursor.all()
        if not myresult:
            return False
        else:
            return True

######################################## Returned einen DataFrame  der asu der Tabelle: scrapingresults erstellt wird. Dieser DF wird im weiteren verwendet um eine Übersicht des letzten Scraping-Ergebnisses zu schaffen. 
def getInfoAboutNewScrapingResult():
    mydb = createConnectionTodatabase()
    df = pd.read_sql('SELECT * FROM scrapingresults;', con=mydb)
    return df

if __name__ == "__main__":
    main()