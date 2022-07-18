from cProfile import label
from sqlalchemy import column
from visualisationRepository import selectAllDataForVisuModeltraining
#from backend.services.visualization.visualisationRepository import selectAllDataForVisuModeltraining
import matplotlib.pyplot as plt, mpld3
import numpy as np
import pandas as pd

def main():
    plotNewTrainedLSTM()
    
def plotNewTrainedLSTM():
    df = selectAllDataForVisuModeltraining()
    df.drop("index", axis=1,inplace=True)
    xlabel = "Epoche"
    ylabel = "Loss"
    visuPlot(ylabel, xlabel, df)
    
def visuPlot(ylabel,xlabel, df):  
    i = 0
    for colum in df.columns:
        if i == 1:
            r = "r"
            plt.plot(df[colum].index, df[colum],r+"-o", label=colum)
            mean = np.mean(df[colum])
            plt.axhline(mean,color=r, linestyle='dashed',label = "Mean of "+colum)
            i = i+1
        else:
            plt.plot(df[colum].index, df[colum],"-o", label=colum)
            mean = np.mean(df[colum])
            plt.axhline(mean, linestyle='dashed',label = "Mean of "+colum)
    plt.style.use('fivethirtyeight')
    plt.xlabel(xlabel, {'color': 'orange', 'fontsize':15})
    plt.ylabel(ylabel, {'color': 'orange', 'fontsize':15})
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.show()
    
if __name__ == "__main__":
    main()