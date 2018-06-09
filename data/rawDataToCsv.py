import numpy as np
import matplotlib as plt
from sklearn import linear_model
from sklearn.model_selection import train_test_split
import pandas as pd

# Change the name here
sheetMap = pd.read_excel('normal_shot.xlsx', sheet_name=None)

# Now you can list all sheets in the file
# print(sheetMap.keys())
wristData = {}
elbowData = {}
shoulderData = {}


zeroArr = np.zeros(500)
oneArr = np.ones(500)

for key in sheetMap:
    # Change this from zeroArr to oneArr
    sheetMap[key]['GoodShot?'] = oneArr
    sheetMap[key] = sheetMap[key].drop(
        sheetMap[key].columns[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]], axis=1)
    if "wrist" in key:
        wristArr = sheetMap[key].as_matrix()
        for i in range(0, 50):
            if str(round(wristArr[i][0], 2)) in wristData:
                wristData[str(round(wristArr[i][0], 2))
                          ].append(wristArr[i][1:])
            else:
                wristData[str(round(wristArr[i][0], 2))] = []
                wristData[str(round(wristArr[i][0], 2))
                          ].append(wristArr[i][1:])
    elif "elbow" in key:
        elbowArr = sheetMap[key].as_matrix()
        for i in range(0, 50):
            if str(round(elbowArr[i][0], 2)) in elbowData:
                elbowData[str(round(elbowArr[i][0], 2))
                          ].append(elbowArr[i][1:])
            else:
                elbowData[str(round(elbowArr[i][0], 2))] = []
                elbowData[str(round(elbowArr[i][0], 2))
                          ].append(elbowArr[i][1:])
    elif "should" in key:
        shoulderArr = sheetMap[key].as_matrix()
        for i in range(0, 50):
            if str(round(shoulderArr[i][0], 2)) in shoulderData:
                shoulderData[str(round(shoulderArr[i][0], 2))
                             ].append(shoulderArr[i][1:])
            else:
                shoulderData[str(round(shoulderArr[i][0], 2))] = []
                shoulderData[str(round(shoulderArr[i][0], 2))
                             ].append(shoulderArr[i][1:])

for key in wristData:
    for arr in wristData[key]:
        aa = [arr]
        a = np.asarray(aa)
        fileName = 'wrist'+str(key)+'.csv'
        with open(fileName, 'a') as f:
            np.savetxt(f, a, delimiter=",")

for key in elbowData:
    for arr in elbowData[key]:
        aa = [arr]
        a = np.asarray(aa)
        fileName = 'elbow'+str(key)+'.csv'
        with open(fileName, 'a') as f:
            np.savetxt(f, a, delimiter=",")

for key in shoulderData:
    for arr in shoulderData[key]:
        aa = [arr]
        a = np.asarray(aa)
        fileName = 'shoulder'+str(key)+'.csv'
        with open(fileName, 'a') as f:
            np.savetxt(f, a, delimiter=",")
