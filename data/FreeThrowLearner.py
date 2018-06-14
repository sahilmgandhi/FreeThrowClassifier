import numpy as np
import matplotlib as plt
from sklearn import linear_model
from sklearn.model_selection import train_test_split
import pandas as pd
import pickle

dataArr = []
indices = np.arange(0.01, 5.01, 0.1)
for i in indices:
    currFile = 'elbow{0:.2f}.csv'.format(i)
    currData = np.genfromtxt(currFile, delimiter=',')
    dataArr.append(currData)

accuracyArr = []
index = 0

for data in dataArr:
    train, test = train_test_split(data, test_size=0.3)
    X_train = train[:, [0, 1, 2, 6, 7, 8]]
    X_test = test[:, [0, 1, 2, 6, 7, 8]]
    Y_train = train[:, -1:].ravel()
    Y_test = test[:, -1:].ravel()

    logreg = linear_model.LogisticRegression(C=5)
    logreg.fit(X_train, Y_train)

    accuracy = logreg.score(X_test, Y_test)
    accuracyArr.append(accuracy)

    fileName = 'elbow{0:.02f}.sav'.format(indices[index])
    pickle.dump(logreg, open(fileName, 'wb'))
    index += 1

print(accuracyArr)

data = np.genfromtxt('wrist2.01.csv', delimiter=',')

train, test = train_test_split(data, test_size=0.3)
# print(train)
# print(test)
# print(data)
X_train = train[:, [0, 1, 2, 6, 7, 8]]
# print(X_train)
X_test = test[:, [0, 1, 2, 6, 7, 8]]
Y_train = train[:, -1:].ravel()
Y_test = test[:, -1:].ravel()
# print(Y)
# print(X)


h = 0.2
logreg = linear_model.LogisticRegression(C=5)
logreg.fit(X_train, Y_train)

accuracy = logreg.score(X_test, Y_test)
print(X_test[1].reshape(1, -1))
print(logreg.predict(X_test[1].reshape(1, -1)))
print("The accuracy was {}".format(accuracy))
