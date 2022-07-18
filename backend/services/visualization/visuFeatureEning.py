from cProfile import label
from turtle import left, right
from sqlalchemy import column
from visualisationRepository import selectColumnsForVisualisation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import numpy.ma as ma

def main():
    columns = ['timestamp','High','close', 'open']
    table = "dataforvisu" 
    df, dateInDf, timestampInDF = prepaireDfForPloting(columns, table)
    #visuBarlogical(df, dateInDf, timestampInDF)
    visuPlotlogical(df, dateInDf, timestampInDF)

def prepaireDfForPloting(columns, table):
    df = selectColumnsForVisualisation(columns, table)
    if 'date' in df.columns and 'timestamp' in df.columns:
        #visuDf = prepairTimestampForPloting(df)
        return df, True, True
    if 'date' in df.columns:
        return df, True, False
    if 'timestamp' in df.columns:
       # visuDf = prepairTimestampForPloting(df)
        return df, False, True
    return df, False, False
    
# def prepairTimestampForPloting(df):
#     intervals = df['timestamp']
#     for i,interval in enumerate(intervals):
#         interval = interval.split()
#         intervals[i] = interval[1]
#         if intervals[i] == "09:30:00":
#             intervals[i] = "16:00:00"
#     return df

def visuDefineIndex(df, dateInDf, timestampInDF):
    if ((dateInDf == True) and (timestampInDF==True)):
        index = []
        for i, dat in  enumerate(df['date']):
            ind = dat+" "+df.at[i,'timestamp']
            index.append(ind)
        df.drop("date", axis=1, inplace=True)
        df.drop("timestamp", axis=1, inplace=True)
        xlabel = "Timestamp"
        return index, xlabel,df
    if ((dateInDf == True) and (timestampInDF==False)):
        index = df["date"]
        df.drop("date", axis=1, inplace=True)
        xlabel = "Date"
        return index, xlabel,df
    if ((dateInDf == False) and (timestampInDF==True)):
        index = df["timestamp"]
        df.drop("timestamp", axis=1, inplace=True)
        xlabel = "timestamp"
        return index, xlabel,df
    index =  df.iloc[:, 0]
    heads = df.columns
    xlabel = heads[0]
    df.drop(xlabel, axis=1, inplace=True)
    return index, xlabel,df

def visuPlot(index, xlabel, df):
    i = 0
    for colum in df.columns:
        if i == 0:
            r = "r"
            plt.plot( df[colum].index, df[colum],r+"-o", label=colum)
            mean = np.mean(df[colum])
            plt.axhline(mean,color=r, linestyle='dashed',label = "Mean of "+colum)
            i = i+1
        else:
            plt.plot(df[colum].index, df[colum],"-o", label=colum)
            mean = np.mean(df[colum])
            plt.axhline(mean, linestyle='dashed',label = "Mean of "+colum)
    plt.style.use('fivethirtyeight')
    plt.xlabel(xlabel, {'color': 'orange', 'fontsize':15})
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.show()

def visuPlotlogical(odf, dateInDf, timestampInDF):
    index, xlabel,df = visuDefineIndex(odf, dateInDf, timestampInDF)
    visuPlot(index, xlabel, df)

def visuBarlogical(odf, dateInDf, timestampInDF):
    index, xlabel,df = visuDefineIndex(odf, dateInDf, timestampInDF)
    visubar(index, xlabel, df)

def visubar(index, xlabel, df):
    barvis = []
    vis = 0
    dif = 0.2
    for column in df.columns:
            b = vis +dif 
            barvis.append(b)
    i = 0
    su = df.sum()
    k = su.sort_values(ascending=False)
    for i, v in k.items():
        if i == 0:
            r = "r"
            df[i]
            plt.bar(index,df[i],color = r, label=i)
            mean = np.mean(df[i])
            plt.axhline(mean,color=r, linestyle='dashed',label = "Mean of "+i)
            i = i+1
        else:
            plt.bar(index, df[i], label=i)
            mean = np.mean(df[i])
            plt.axhline(mean, linestyle='dashed',label = "Mean of "+i)
    plt.style.use('fivethirtyeight')
    plt.xlabel(xlabel, {'color': 'orange', 'fontsize':15})
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.show()
    
if __name__ == "__main__":
    main()