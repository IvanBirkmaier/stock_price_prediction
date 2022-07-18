import sqlalchemy
import pandas as pd
import sqlalchemy
import numpy as np

def main():
    x = stocknameForTicker(getListOfKeywordsInTable(table='stockdata'))
    y= 1

def createConnectionTodatabase():
    connectionToDB = sqlalchemy.create_engine('mysql://root@127.0.0.1/featuresdatabase')
    return connectionToDB

def getTablesFromDb():
    mydb = createConnectionTodatabase()
    tables = mydb.table_names()
    return tables
  
############################# Df aus Stocktickern + Stockname  
def getStocks():
    mydb = createConnectionTodatabase()
    df = pd.read_sql('SELECT * FROM stockinformation', con=mydb)
    return df

############################# StocksTicker für die OHCV-Daten in DB vorhanden sind und mehr als 50 Einträge hat  
def getListOfKeywordsInTable(table):
    mydb = createConnectionTodatabase()
    mycursor = mydb.execute("select keyword from (select keyword, count(keyword) as sum from "+table+" group by keyword having sum > 50) as resulttable;")
    myresult = mycursor.all()
    if not myresult:
        return False
    else:
        result = []
        for re in myresult:
            result.append(re[0])
        return  list(dict.fromkeys(result))

############################# Gets the stocknames out of a list of stocktickers
def stocknameForTicker(listOfTickers):
    mydb = createConnectionTodatabase()
    q = str(listOfTickers)
    q = q[1:len(q)-1]
    mycursor = mydb.execute("select name from stockinformation where symbol in ("+q+");")
    myresult = mycursor.all()
    if not myresult:
        return False
    else:
        result = []
        for re in myresult:
            result.append(re[0])
        return  list(dict.fromkeys(result))

if __name__ == "__main__":
    main()