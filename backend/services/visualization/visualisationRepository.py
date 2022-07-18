import sqlalchemy
import pandas as pd
import sqlalchemy
import numpy as np


def createConnectionTodatabase():
    connectionToDB = sqlalchemy.create_engine('mysql://root@127.0.0.1/featuresdatabase')
    return connectionToDB

def getListOfKeywordsInTable(table):
    mydb = createConnectionTodatabase()
    mycursor = mydb.execute("select keyword from "+table+" group by keyword;")
    myresult = mycursor.all()
    if not myresult:
        return False
    else:
        result = []
        for re in myresult:
            result.append(re[0])
        return  list(dict.fromkeys(result))

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

def getKeywordsByDatelist(table,datelist):
    mydb = createConnectionTodatabase()
    q = str(datelist)
    q = q[1:len(q)-1]
    mycursorTwo = mydb.execute("select keyword from "+table+" where date in ("+q+");")
    myresult = mycursorTwo.all()
    if not myresult:
        return False
    else:
        result = []
        for re in myresult:
            result.append(re[0])
        return  list(dict.fromkeys(result))

def selectColumnsForVisualisation(columns, table):
    mydb = createConnectionTodatabase()
    col = ','.join(columns)
    query = 'SELECT '+col +' FROM '+table+';'
    df = pd.read_sql(query, con=mydb)
    return df

def selectAllDataForVisuModeltraining():
    mydb = createConnectionTodatabase()
    df = pd.read_sql('SELECT * FROM modelhistory;', con=mydb)
    return df
