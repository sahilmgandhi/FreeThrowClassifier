#ifndef main
#define main

#include "mbed.h"
#include "rtos.j"

#define LED_ON 0
#define LED_OFF 1

void UpdateSensorData(void);
void StartHaptic(void);
void StopHaptic(void const *n);
void txTask(void);

// Callback functions
void ButtonRight(void);
void ButtonLeft(void);
void PassKey(void);

/*
 * This function collects the raw data samples and places them into the
 * array for raw accel and raw gyro datas.
 */
void collectRawData(void);

/*
 * This function processes the raw data samples and places them into the
 * array for the processed accel and gyro datas.
 * Since we have to sent uint_8t, we should also make sure to multiply the
 * floats by 100, and then divide by 100 on the raspberry pi side!
 */
void processRawData(void);

/*
 * This function sends the processed data over to the Raspberry Pi.
 * It will exploit the sendAlert function of the k40z which can send 20 uint_8t
 * bytes at once!
 */
void sendProcessedData(void);

Serial pc(USBTX, USBRX);

DigitalOut blueLed(LED3);
DigitalOut haptic(PTB9);

/* Text Buffer */
char text[20];
float gyroData[400][3];
float accelData[400][3];

uint8_t processedGyroData[40][9];
uint8_t processedAccelData[40][9];

volatile bool connectedToPi = false;
volatile bool startGrabbingData = false;
bool foundInitSequence = false;

// Auxiliary Haptic Functions
void StartHaptic(void) {
  hapticTimer.start(50);
  haptic = 1;
}

void StopHaptic(void const *n) {
  haptic = 0;
  hapticTimer.stop();
}