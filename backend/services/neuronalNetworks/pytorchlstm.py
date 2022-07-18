from asyncio import run_coroutine_threadsafe
from cgi import test
from copyreg import pickle
from fileinput import filename
from itertools import count
from operator import length_hint
from re import A
from sympy import O
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
import random
import os
from torch.utils.data import DataLoader,  TensorDataset
#from neuronalNetworkRepository import selectAllDataFromDbToDf, selectSertainColumnsFromTable, insertIntoMysqlDatabase
from backend.services.neuronalNetworks.neuronalNetworkRepository import selectAllDataFromDbToDf, selectSertainColumnsFromTable, insertIntoMysqlDatabase
import copy
from statistics import mean
###########################################################################################################################################################################################################
##########################################                                 Klassenvariablen                ################################################################################################ 
###########################################################################################################################################################################################################
loss_vals_per_model  = list()
testloss_vals_per_model = list()
meanLossforPlotingTrain = list()
meanLossforPlotingTest = list()

##################################################################################################################################################################################################################
###############################    Main Methode liest die erstellten Featuredaten als Datensatz ein und leitet den Prozess ein.         ##########################################################################
##################################################################################################################################################################################################################
def main():
    # ############################## Möglichkeit 1: Random Hyperparameter, ausgewählte Features #############################################
    columns = ['timestamp','total_number_of_tweets_in_interval', 'average_tweets_per_minute_in_interval', 'min_tweets_per_minute', 'max_tweets_per_minute', 'close']
    table = "dataforrunninglstm"
    goalvariable = 'close' ##### Values die später vom Frontend übergeben werden können 
    #runLstmSelectedFeatureAndRandomHyperparameters(columns,table,goalvariable)

    ############################## Möglichkeit 2: Ausgewählte Hyperparameter, random Features #############################################
    # table = "testinsert"
    #runLstmRandomFeaturesDefinedHyperpar(table,300, 2, 0.25, 0.01, 10)

    ############################## Möglichkeit 3: Ausgewählte Hyperparameter, ausgwählte Features #############################################
    #runLSTMdefinedFeaturesDefinedHyperpar(columns, table,goalvariable, 100, 2, 0.25, 0.01, 10)
    
    
    ############################## Möglichkeit 4: Random Hyperparameter, random Features ############################################# 
    # table = "testinsert"
    runLstmRandomFeatureAndRandomHyperparameters(table)

#### braucht noch table sonst setzt aus der die daten gezogen werden sollen
def runLstmRandomFeatureAndRandomHyperparameters(table):
    trainLoader , testLoader, trainForInitRandomFeatures = generateLstmWithRandomFeatures(table)
    input_size, hidden_size, num_layers, input_sizeForLayerTwo, dropout, leraning_rate, num_epochs = randomHyperparm(trainForInitRandomFeatures)
    print("Variablen:")
    print("Input for Layer 2: ",input_sizeForLayerTwo)   
    print("Dropoutrate: ",dropout)    
    print("Hiddensize: ",hidden_size)    
    print("Epochs: ",num_epochs)           
    print("Lerningrate: ",leraning_rate)
    print("Input_size: ",input_size)
    print("Num_layerOne: ", num_layers)
    net = Net(input_size, hidden_size, num_layers, input_sizeForLayerTwo, dropout)
    net = net.float()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(net.parameters(), lr=leraning_rate)
    epochsWithLogic(num_epochs, optimizer,net,trainLoader,criterion,testLoader)
    insertIntoMysqlDatabase(createDfForDb(),table='modelhistory',status='replace')
    deleteAllModelsWhichArentTheBest()
    meanLossforPlotingTest.clear()
    meanLossforPlotingTrain.clear()
    testloss_vals_per_model.clear()
    loss_vals_per_model.clear()

##### braucht die im Methodenkopfdefinierten Inputs nur einzelne variablen
def runLstmRandomFeaturesDefinedHyperpar(table, hidden_size, num_layers,dropout, leraning_rate, num_epochs):
    trainLoader , testLoader, trainForInitRandomFeatures = generateLstmWithRandomFeatures(table)
    input_size,_,_,_,_,_,_ = randomHyperparm(trainForInitRandomFeatures)
    input_sizeForLayerTwo = hidden_size*2
    print("Variablen:")
    print("Input for Layer 2: ",input_sizeForLayerTwo)   
    print("Dropoutrate: ",dropout)    
    print("Hiddensize: ",hidden_size)    
    print("Epochs: ",num_epochs)           
    print("Lerningrate: ",leraning_rate)
    print("Input_size: ",input_size)
    print("Num_layerOne: ", num_layers)
    net = Net(input_size, hidden_size, num_layers, input_sizeForLayerTwo, dropout)
    net = net.float()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(net.parameters(), lr=leraning_rate)
    epochsWithLogic(num_epochs, optimizer,net,trainLoader,criterion,testLoader)
    insertIntoMysqlDatabase(createDfForDb(),table='modelhistory',status='replace')
    deleteAllModelsWhichArentTheBest()
    meanLossforPlotingTest.clear()
    meanLossforPlotingTrain.clear()
    testloss_vals_per_model.clear()
    loss_vals_per_model.clear()

def runLSTMdefinedFeaturesDefinedHyperpar(columns, table,goalvariable, hidden_size, num_layers, dropout, leraning_rate, num_epochs):
    originalDataframe =selectSertainColumnsFromTable(columns, table) 
    trainLoader , testLoader, trainForInitRandomFeatures = generateLstmWithSelectedFeatures(originalDataframe,goalvariable)
    input_size,_,_,_,_,_,_ = randomHyperparm(trainForInitRandomFeatures)
    input_sizeForLayerTwo = hidden_size*2
    print("Variablen:")
    print("Input for Layer 2: ",input_sizeForLayerTwo)   
    print("Dropoutrate: ",dropout)    
    print("Hiddensize: ",hidden_size)    
    print("Epochs: ",num_epochs)           
    print("Lerningrate: ",leraning_rate)
    print("Input_size: ",input_size)
    print("Num_layerOne: ", num_layers)
    net = Net(input_size, hidden_size, num_layers, input_sizeForLayerTwo, dropout)
    net = net.float()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(net.parameters(), lr=leraning_rate)
    epochsWithLogic(num_epochs, optimizer,net,trainLoader,criterion,testLoader)
    insertIntoMysqlDatabase(createDfForDb(),table='modelhistory',status='replace')
    deleteAllModelsWhichArentTheBest()
    meanLossforPlotingTest.clear()
    meanLossforPlotingTrain.clear()
    testloss_vals_per_model.clear()
    loss_vals_per_model.clear()

##### braucht die im Methodenkopfdefinierten Inputs: colum liste aus Strings der table columns von. table: String: um welche tabelle in der DB handelt
##### goalvariable: String Tabellenkopf der die zielvariable geben soll
def runLstmSelectedFeatureAndRandomHyperparameters(columns,table,goalvariable):
    originalDataframe =selectSertainColumnsFromTable(columns, table) 
    trainLoader , testLoader, trainForInitRandomFeatures = generateLstmWithSelectedFeatures(originalDataframe,goalvariable)
    input_size, hidden_size, num_layers, input_sizeForLayerTwo, dropout, leraning_rate, num_epochs = randomHyperparm(trainForInitRandomFeatures)
    print("Variablen:")
    print("Input for Layer 2: ",input_sizeForLayerTwo)   
    print("Dropoutrate: ",dropout)    
    print("Hiddensize: ",hidden_size)    
    print("Epochs: ",num_epochs)           
    print("Lerningrate: ",leraning_rate)
    print("Input_size: ",input_size)
    print("Num_layerOne: ", num_layers)
    net = Net(input_size, hidden_size, num_layers, input_sizeForLayerTwo, dropout)
    net = net.float()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(net.parameters(), lr=leraning_rate)
    epochsWithLogic(num_epochs, optimizer,net,trainLoader,criterion,testLoader)
    insertIntoMysqlDatabase(createDfForDb(),table='modelhistory',status='replace')
    deleteAllModelsWhichArentTheBest()
    meanLossforPlotingTest.clear()
    meanLossforPlotingTrain.clear()
    testloss_vals_per_model.clear()
    loss_vals_per_model.clear()
   
def generateLstmWithSelectedFeatures(df,goalvariable):
    train,test =  trainAndtestSplits(df)
    batch_sizeTrain = defineBatchsize(len(train))
    batch_sizeTest = defineBatchsize(len(test))
    trainDatadf,trainLabelDf,testDatadf,testLabelDf=deleteGoalVariable(train,test,goalvariable)
    trainDataTorch, trainLabelTorch = createInputTorches(trainDatadf.to_numpy(), trainLabelDf.to_numpy())
    testDataTorch, testLabelTorch = createInputTorches(testDatadf.to_numpy(), testLabelDf.to_numpy())
    trainLoader = buildDataloader(trainDataTorch,trainLabelTorch,batch_sizeTrain)
    testLoader = buildDataloader(testDataTorch,testLabelTorch,batch_sizeTest)
    return trainLoader , testLoader, train

#set label-variable to close-price by default
def generateLstmWithRandomFeatures(table):
    originalDataframe = selectAllDataFromDbToDf(table)
    goalvariable = 'Close'
    randomFeatureDf = decideHowManyFeatures(originalDataframe)
    print("Features die Gwählt worden sind", str(randomFeatureDf.columns))
    train,test =  trainAndtestSplits(randomFeatureDf)
    batch_sizeTrain = defineBatchsize(len(train))
    batch_sizeTest = defineBatchsize(len(test))
    trainDatadf,trainLabelDf,testDatadf,testLabelDf=deleteGoalVariable(train,test,goalvariable)
    trainDataTorch, trainLabelTorch = createInputTorches(trainDatadf.to_numpy(), trainLabelDf.to_numpy())
    testDataTorch, testLabelTorch = createInputTorches(testDatadf.to_numpy(), testLabelDf.to_numpy())
    trainLoader = buildDataloader(trainDataTorch,trainLabelTorch,batch_sizeTrain)
    testLoader = buildDataloader(testDataTorch,testLabelTorch,batch_sizeTest)
    return trainLoader , testLoader, train

def trainAndtestSplits(df):
    length_totalDataset = len(df)
    calculate_eightyPercentTrainVali = length_totalDataset * 0.8
    length_trainAndValiDataset = round(calculate_eightyPercentTrainVali)
    train = df.iloc[:length_trainAndValiDataset,:]
    test = df.iloc[length_trainAndValiDataset:,:]
    return train,test

def deleteGoalVariable(train,test,goalvariable):
    trainlabel = train[goalvariable]
    testlabel = test[goalvariable]
    train.drop(goalvariable, axis=1, inplace=True)
    test.drop(goalvariable, axis=1, inplace=True)
    return train,trainlabel,test,testlabel

def createInputTorches(data, label):
    inputs = torch.tensor(data)
    labels = torch.tensor(label)
    return inputs.unsqueeze(1), labels.unsqueeze(1)

def buildDataloader(data,labels,batch_size):
    dataset = TensorDataset(data, labels)
    loader = DataLoader(dataset,batch_size)
    return loader

def defineBatchsize(lenDf):
    batch_size = lenDf*0.1
    return round(batch_size)

def randomHyperparm(df):
    leraning_rate = 0.01
    input_size = len(df.columns)
    sequence_length = 1
    num_layers = numOfLayer()
    num_epochs = numOfEpochs()
    hidden_size = numOfHiddenSize()
    dropout = numOfDropoutRate()
    input_sizeForLayerTwo = hidden_size*2  
    return input_size, hidden_size, num_layers, input_sizeForLayerTwo, dropout, leraning_rate, num_epochs
  
def numOfLayer():
    num =  random.randrange(1,6)
    return num
def numOfEpochs():
    num =  random.randrange(10,50)
    return num
def numOfHiddenSize():
    num =  random.randrange(50,500)
    return num
def numOfDropoutRate():
    dropoutRates = [0.75,0.5,0.25]
    num = random.choice(dropoutRates)
    return num

####################################################################################################################################################################################
######################################## decideHowManyFeatures. erstellt ein Dataframe von zufällig vielen Features     ############################################################
####################################################################################################################################################################################
def decideHowManyFeatures(dataf):
    goal = dataf['Close']
    dataf.drop('Close', axis=1, inplace=True)
    howManyFeautures = generateRandomNumbre(3, dataf) #minimum was ich an Features haben will für ein Model
    
    dfWitchCoumns = []
    count = 0
    for i in range(howManyFeautures):
        if count >= 1:
            t = randomFeatures(dataf,dfWitchCoumns)
            dfWitchCoumns.append(t)
        else:
            count = count+1
            pickRandomColums = generateRandomNumbre(1,dataf)
            dfWitchCoumns.append(pickRandomColums)
    dataframeForTensor = []
    dataframeForTensor.append(goal)
    for i in dfWitchCoumns:
        dataframeForTensor.append(dataf.iloc[:,i])
    datafForTensorPrepared = pd.DataFrame(dataframeForTensor)
    datafForTensorPrepared = datafForTensorPrepared.swapaxes("index", "columns")
    return datafForTensorPrepared

####################################################################################################################################################################################
######################################## generateRandomNumbre. Gibt eine Zufallszahl zurück die von einer startNumbre      #########################################################
######################################## bis zum Max. der möglichen features geht, um eine Anzahl an Features zu bestimmen #########################################################
######################################## die Später als Inputs verwendet werden können.                                     ########################################################
####################################################################################################################################################################################
def generateRandomNumbre(startNumbre, dataf):
    randomNumber = random.randrange(startNumbre, dataf.shape[1])
    if randomNumber <= dataf.shape[1]:
        return randomNumber
    else:
        newRandomNumber = generateRandomNumbre(dataf)
        return newRandomNumber

###################################################################################################################################################################################
########################################  randomFeatures. Überwacht dass bei der Erstellung des in der oberen Methode  #############################################################
########################################  erstellten Dataframe keine Features zwei Mal Auftauchen.                    #############################################################
###################################################################################################################################################################################
def randomFeatures(dataf,dfWitchCoumns):
    pickRandomColums = generateRandomNumbre(1,dataf)
    if not (pickRandomColums in dfWitchCoumns):
        return  pickRandomColums
    else:
        return randomFeatures(dataf,dfWitchCoumns)

##################################################################################################################################################################
###################################             Inizialisierung des LSTM Modells                ###################################################################
###################################################################################################################################################################
class Net(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, input_sizeForLayerTwo, dropout):
        super(Net, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.input_sizeForLayerTwo = input_sizeForLayerTwo
        self.layer_1 = nn.LSTM(input_size,hidden_size, num_layers, batch_first=True, dropout = 1,
                                bidirectional  = True) # input_size, hidden_size
        self.dropout = nn.Dropout(dropout)
        self.layer_L2 = nn.LSTM(input_sizeForLayerTwo ,hidden_size, num_layers, batch_first=True, dropout = 1,
                                bidirectional  = True) # input_size, hidden_size
        self.dropout2 = nn.Dropout(dropout)
        self.layer_2 = nn.Linear(hidden_size*2, 1) # input_size, output_size
    def forward(self, x):
        h0 = torch.zeros(self.num_layers*2,x.size(0),self.hidden_size)
        c0 = torch.zeros(self.num_layers*2,x.size(0),self.hidden_size)
        out, (h_n, c_n) = self.layer_1(x, (h0, c0))
        dropout = self.dropout(out)
        out, _ = self.layer_L2(dropout,(h_n, c_n))
        dropout2 = self.dropout(out)
        output = torch.relu(self.layer_2(dropout2))
        changedia = torch.squeeze(output)
        return changedia

################################################################################################################################
##################################                Neuronales Netzwerk          #################################################
################################################################################################################################

def epochsWithLogic(num_epochs, optimizer,net,trainloaderinputs,criterion,testloaderinputs):
    for epoch in range(num_epochs):
        for data, label in trainloaderinputs:
            optimizer.zero_grad()
            outputs = net(data.float())
            loss = criterion(outputs, label.float())
            loss.backward()
            optimizer.step()
            loss_vals_per_model.append(loss.item())
        for data, label in testloaderinputs:
            modelForTest=copy.deepcopy(net)
            testoutput = modelForTest(data.float())
            testloss = criterion(testoutput, label.float())
            testloss_vals_per_model.append(testloss.item())
        meantrainloss,meantestloss = calculateMeanLossesPerModel()
        if epoch > 1 :
                checkIfearlyStopping = early_stopping(meanLossforPlotingTest[epoch -2], meanLossforPlotingTest[epoch -1 ], meantestloss)
                if checkIfearlyStopping ==True:
                    eralyepo = epoch-2
                    print("Training abgebrochen. Da sich die Loss Werte von Epoche ",eralyepo," bis Epoche ", epoch, " nicht verändert haben. "+
                    "Bitte Modelanpassungen vornehmen.")
                    break
        itemToString = str(meantestloss)
        path = "models/models_with_mean_test_loss_"+itemToString+".path.tar"
        saveModel(net, path)
        print("Epoche ",epoch+1," durchgelaufen! Mit einem Trainloss von: ", meantrainloss," und einem Testloss von: ", meantestloss)

def calculateMeanLossesPerModel():
    x =mean(loss_vals_per_model)
    y = mean(testloss_vals_per_model)
    meanLossforPlotingTrain.append(x)  
    meanLossforPlotingTest.append(y)
    return x,y
        
def createDfForDb():
    df = pd.DataFrame()
    df["mean_train_loss"]= meanLossforPlotingTrain
    df["mean_test_loss"]= meanLossforPlotingTest
    return df
 
######################################################################################################################################################
###################################### Stopt das Training wenn sich mit beim Trainieren der Loss nicht mehr verändert ################################
######################################################################################################################################################
def early_stopping(twoBeforeCurrentLoss, oneBeforeCurrentLoss, current_loss):
    if current_loss == oneBeforeCurrentLoss and current_loss == twoBeforeCurrentLoss:
            return True

###############################################################################################################################
##################################   Speiechert das Model einer jeden epoche   ################################################
###############################################################################################################################
def saveModel(model, filename):
    torch.save(model, filename)

################################################################################################################################
##################################  Zieht sich aus der Liste loss_vals den kleinsten Wert  #####################################
################################################################################################################################
def bestModelfromTraining():
    minLoss = min(meanLossforPlotingTest)
    return minLoss

################################################################################################################################
############################       Löscht alle Modelle bis auf das effizienteste        ########################################
################################################################################################################################
def deleteAllModelsWhichArentTheBest():
    for i in meanLossforPlotingTest:
        if i != bestModelfromTraining():
            itemToString = str(i)
            path = "models/models_with_mean_test_loss_"+itemToString+".path.tar"
            os.remove(path)

################################################################################################################################
########################   Lädt das best performende Modell wieder (derzeit kein Gebrauch)         #############################
################################################################################################################################          
# def loadBestModel():
#     itemToString = str(bestModelfromTraining())
#     path = "models/models_with_loss_"+itemToString+".path.tar"
#     net = torch.load(path)
#     net.eval()
#     return net 

if __name__ == "__main__":
    main()

# ####################################### Besprechen: ###############################################################
# # 1. Datensatz in Trainings Vali Test Set unterteilen, wie müssen die dann durchlaufen? durch 1 Model mehrere Datensätze? Forschleife um epoch Forschleife mit 
# # If bedingung dass wenn test datensatz durchgelaufen ist, dann vali und danach test datensatz? was dann machen wenn training abgebrochen wird, dann trotzdem 
# # mit vali und test weitermachen?
# # 2. Durch das Model gehen, schauen wo man verbessernd ansetzen könnte 