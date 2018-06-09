import numpy as np
import matplotlib as plt
from sklearn import linear_model
from sklearn.model_selection import train_test_split
import pandas as pd


data = np.genfromtxt('wrist2.01.csv', delimiter=',')

train, test = train_test_split(data, test_size=0.3)
# print(train)
# print(test)
# print(data)
X_train = train[:, :-1]
X_test = test[:, :-1]
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
