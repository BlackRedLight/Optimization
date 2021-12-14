#import matplotlib.pyplot as plt
import scipy.optimize as opt
import numpy as np
import os.path

dataFolder = 'logs'
logsFile = 'log.txt'
dataFile = 'data.txt'
LDefault = [127.5, 125.5, 123.5, 123.2 , 122.45]
FDefault = [19.4, 19.66, 19.96, 20.02, 20.1]
nameDefault = 'Default'
data = []
dataN = 1
sumLin = 0
sumExp = 0

# Exponential function
def funcExp(x, a, b):
    return a * np.exp(b * x)

# Linear function
def funcLin(x, a, b):
    return a * x + b

# Logging
def logWrite(text):
    logs = open(f'{dataFolder}\\{logsFile}', 'a+')
    logs.write(f'{text}\n')
    logs.close()
    print(text)

# Save new data in data.txt
def saveData(x, y, name):
    data = open(f'{dataFolder}\\{dataFile}', 'a+')
    data.write(f'{name};{x};{y}\n')
    data.close()
    logWrite('Data saved')

# Read existing data from data.txt
def readData():
    if os.path.isfile(f'{dataFolder}\\{dataFile}'):
        with open(f'{dataFolder}\\{dataFile}', 'r') as f:
            f = f.read()
            f = f.split('\n')
            f.remove('')
            for i in range(len(f)):
                data.append(f[i].split(';'))
            return data
    else:
        logWrite(f'Don\'t delete {dataFile}')



# Create logs and save file if not exists
if os.path.exists(f'{os.getcwd()}\\{dataFolder}') is False:
    os.mkdir(f'{os.getcwd()}\\{dataFolder}')
    logs = open(f'{dataFolder}\\{logsFile}', 'a+')
    logs.write('Created by Mikhaylov Danila\nversion 3.0\n')
    logs.close()
    saveData(LDefault, FDefault, nameDefault)
    logWrite('Default data generated')
    

# Define data
logWrite('Program started')
print('l - load saved data, n - enter new data, Enter - use default data')
inputData = input()
print()

if inputData == '':  #  use some default data
    dataName = nameDefault
    LValues = np.array(LDefault)
    FValues = np.array(FDefault)
elif inputData == 'n':  # take new data and save it in save file
    i = 0
    LValues = []
    FValues = []
    print('Enter data L;F (127.5;19.9)\n')
    while True:
        inputData = input()
        if inputData == '':
            print('Enter name for new data:')
            dataName = input()
            saveData(LValues, FValues, dataName)
            break
        try:
            inputData = inputData.split(';')
            LValues.append(float(inputData[0]))
            FValues.append(float(inputData[1]))
        except:
            logWrite('Wrong data')
    LValues = np.asarray(LValues)
    FValues = np.asarray(FValues)
elif inputData == 'l':  # load saved data and let user to choose
    Data = readData()
    for i in range(len(Data)):
        logWrite(f'{i}: {Data[i][0]}')
    dataN = int(input())
    LValues = np.asarray(Data[dataN][1][1:-1].split(','), dtype = np.float64, order = 'C')
    FValues = np.asarray(Data[dataN][2][1:-1].split(','), dtype = np.float64, order = 'C')
    dataName = Data[dataN][0]

# Define working data
logWrite(f'{dataName}:\nX:{LValues}\nY:{FValues}')
print()
xSamp = LValues
ySamp = FValues
xModel = np.linspace(xSamp.min(), xSamp.max(), 20)  #On X from min to max in 20 steps

# Guessing params of exponential function
logWrite('Guessing params')
p0 = [48, -0.01]
pExp, _ = opt.curve_fit(funcExp, xSamp, ySamp, p0 = p0)     
logWrite(f'Exponential params: {pExp}')
print()

# Guessing params of linear function
p0 = [-0.14, 37]
pLin, _ = opt.curve_fit(funcLin, xSamp, ySamp, p0 = p0)     
logWrite(f'Linear params: {pLin}')
print()

# Calculating functions
yModelExp = funcExp(xModel, *pExp)
yModelLin = funcLin(xModel, *pLin)

# Calculating sum of squares
for i in range(len(ySamp)):
    sumLin = sumLin + (ySamp[i] - funcLin(xSamp[i], pLin[0], pLin[1])) ** 2
for i in range(len(ySamp)):
    sumExp = sumExp + (ySamp[i] - funcExp(xSamp[i], pExp[0], pExp[1])) ** 2

# Plotting
#plt.plot(xSamp, ySamp, "ko", label="Data")
#plt.plot(xModel, yModelExp, "r--", label="Exp")
#plt.plot(xModel, yModelLin, "b--", label="Lin")
#plt.grid()
#plt.xlabel('Length (mm)')
#plt.ylabel('Frequency (kHz)')
#plt.title(dataName)
#plt.legend(loc = 'upper right')
#plt.show()

# Correction
LActual = float(input('Actual L: '))
FActual = float(input('Actual F: '))
print()

if sumLin < sumExp:
    c = FActual - (pLin[0] * LActual + pLin[1])
    logWrite(f'Using linear function\nf(x) = {round(pLin[0], 3)} * x + {round(pLin[1], 3)} + {round(c, 3)}\nSum of sqares = {sumLin}\n')
    print()
else:
    c = FActual - (pExp[0] * np.exp(pExp[1] * LActual))
    logWrite(f'Using exponential function\nf(x) = {round(pExp[0], 3)} * e ^ ({round(pExp[1], 3)} * x) + {round(c, 3)}\nSum of sqares = {sumExp}\n')

# Calculating needed lenght and frequency
while True:
    logWrite('l - calculate L, f - calculate F, Enter - exit')
    inputData = input()
    print()
    if inputData.lower() == 'f':
        inputData = float(input('Needed lenght: '))
        if sumLin > sumExp:
            Fcalc = pExp[0] * np.exp(pExp[1] * inputData) + c
            logWrite(f'F = {round(Fcalc, 3)} kHz')
            logWrite(f'dF = {round(Fcalc - (pExp[0] * np.exp(pExp[1] * LActual) + c), 3)} kHz')
        else:
            logWrite(f'F = {pLin[0] * inputData + pLin[1] + c} kHz')
        print()
    elif inputData.lower() == 'l':
        inputData = float(input('Needed frequency: '))
        if sumLin > sumExp:
            Lcalc = (np.log(-(c - inputData) / pExp[0])) / pExp[1]
            logWrite(f'L = {round(Lcalc, 3)} mm')
            logWrite(f'L = {round(Lcalc - ((np.log(-(c - FActual) / pExp[0])) / pExp[1]), 3)} mm')
        else:
            logWrite(f'L = {(inputData - pLin[1] - c) / pLin[0]} mm')
        print()
    elif inputData == '':
        logWrite('Program ended successfuly')
        break
    else:
        logWrite('Wrong command')