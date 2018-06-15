# FreeThrowClassifier

## Classifying the Mechanics of Basketball Free Throw Shots using Cross Validated Hexiwears Mounted at Multiple Strategic Positions

# Enabling Bluetooth on R-PI:

1) `sudo hciconfig hci0 up` -> Turns on bluetooth on Pi
2) `bluetoothctl`
    - `agent on`
    - `agent off`
    - `agent KeyboardOnly`
    - `scan on`
    - `pair __MAC__ADDRESS__` <- input the mac addresses of your 3 Hexiwears (you may have to `remove __MAC__ADDRESS__` and then repair them!)

# Modifying the Code

You will need to modify the following lines in dataGrabber.py, and put your Hexi's mac addresses instead:

``` python
elbow_hexi_addr = '00:2E:40:08:00:31'
wrist_hexi_addr = '00:06:40:08:00:31'
shoulder_hexi_addr = '00:35:40:08:00:48'
```
You may also choose to modify these lines by appending _90 to the .sav file for a different training model that we had:

``` python
for i in indices:
    currElbowFile = 'elbow{0:.2f}.sav'.format(i) # 'elbow{0:.2f}_90.sav for example
    currWristFile = 'wrist{0:.2f}.sav'.format(i)
    currShoulderFile = 'shoulder{0:.2f}.sav'.format(i)

    wristModels.append(pickle.load(open(currWristFile, 'rb')))
    elbowModels.append(pickle.load(open(currElbowFile, 'rb')))
    shoulderModels.append(pickle.load(open(currShoulderFile, 'rb')))
```

# Python Libraries Required

Therre are some python libraries that you will need to install. They can be installed via pip, though we have seen that can take some time on the Raspberry Pi. Thus you can run one of the following commands:

``` bash
sudo apt-get install python-numpy python-scipy python-matplotlib python-pandas python-sympy python-nose python-sklearn

# OR

pip install --no-cache-dir numpy scipy matplotlib pandas sympy sklear
```

# Hexiwear Code

The Hexiwear code is split into two parts, the wrist (under main_wrist.cpp in the FreeThrowInitialFSM directory), and the code for the shoulder and elbow under main.cpp. These pieces of code do not need to be changed in order to make this project work!

# Other misc. Code 

Under the "data" directory, we have the raw as well as processed data that we collected from the Hexiwears and the python script that we used to create the training models.

Under the "FreeThrowDataCollector" directory, we have the main.cpp that was used to collect the raw data from Hexiwear to use in the training step. 

Under the "Homework3" directory, we have some code (not complete yet) of assignment 3 as we worked on that in parallel with this project. 

# YouTube Link

[Video of the working demonstration!](https://youtu.be/2OUmcB8TJiI)
