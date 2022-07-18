import sqlalchemy
import pandas as pd
import sqlalchemy


def main():
    x,y,z= info("Sstockdata", "AAPL")
    x =1

def createConnectionTodatabase():
    connectionToDB = sqlalchemy.create_engine('mysql://root@127.0.0.1/featuresdatabase')
    return connectionToDB

def info(table, keyword):
    mydb = createConnectionTodatabase()
    days = pd.read_sql("select date, count(date) as alldates from "+table+" where keyword = '"+keyword+"'  group by date;", con=mydb)
    days = len(days.index)
    mycursor = mydb.execute("select count(keyword) as allkey from "+table+" where keyword = '"+keyword+"'  group by keyword;")
    myresult = mycursor.all()
    rows = myresult[0][0]
    values = pd.read_sql("select*from "+table+" where keyword = '"+keyword+"';", con=mydb)
    values = len(values.columns)
    values = rows*values
    return days, rows, values


if __name__ == "__main__":
    main()