import sqlalchemy
import pandas as pd
from sympy import symarray
import mysql.connector

def main():
    initialize()
########################### Initialisiert die Datenbank 
def initialize():
    sdf = pd.read_csv("data\\nasdaqstockticker.csv")
    symbolAndNameOfStock = sdf.iloc[:, [0,1]]
    idb = sqlalchemy.create_engine('mysql://root@127.0.0.1')
    idb.execute("CREATE DATABASE featuresdatabase;")
    mydb = sqlalchemy.create_engine('mysql://root@127.0.0.1/featuresdatabase')
    symbolAndNameOfStock.to_sql('stockinformation', con=mydb, if_exists='replace')

if __name__ == "__main__":
    main()

