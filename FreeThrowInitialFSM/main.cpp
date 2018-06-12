#include "FXAS21002.h"
#include "FXOS8700.h"
#include "Hexi_KW40Z.h"
#include "Hexi_OLED_SSD1351.h"
#include "OLED_types.h"
#include "OpenSans_Font.h"
#include "mbed.h"
#include "string.h"

#define LED_ON 0
#define LED_OFF 1
#define DATA_SIZE 500
#define AVG_DATA_SIZE 50
#define SYSTICK_PERIOD .01

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

/* Define timer for haptic feedback */
RtosTimer hapticTimer(StopHaptic, osTimerOnce);

/* Instantiate the Hexi KW40Z Driver (UART TX, UART RX) */
KW40Z kw40z_device(PTE24, PTE25);

/* Instantiate the SSD1351 OLED Driver */
SSD1351 oled(PTB22, PTB21, PTC13, PTB20, PTE6, PTD15); /* (MOSI,SCLK,POWER,CS,RST,DC) */

/*Create a Thread to handle sending BLE Sensor Data */
Thread txThread;

/* Instantiate the gyroscope and accelerometer */
FXAS21002 gyro(PTC11, PTC10);
FXOS8700 accel(PTC11, PTC10);

/* Systick ticker for data collection */
Ticker systick;

/* Text Buffer */
char text[20];

uint8_t processedGyroData[AVG_DATA_SIZE][9];
uint8_t processedAccelData[AVG_DATA_SIZE][9];

volatile bool connectedToPi = false;
volatile bool startGrabbingData = false;
bool foundInitSequence = false;
volatile bool startCollection = false;

/**************************Data Collection Globals*****************************/
volatile bool doneCollecting = false;

// accelerometer data
volatile float x_accel = 0;
volatile float y_accel = 0;
volatile float z_accel = 0;

// gyroscope data
volatile float x_omega = 0;
volatile float x_theta = 0;

volatile float y_omega = 0;
volatile float y_theta = 0;

volatile float z_omega = 0;
volatile float z_theta = 0;

volatile int data_index = 0;

// gyroData[][0] = x-axis
// gyroData[][1] = y-axis
// gyroData[][2] = z-axis
float gyroData[DATA_SIZE][3];
float accelData[DATA_SIZE][3];
/************************End Data Collection Globals***************************/


// Auxiliary Haptic Functions
void StartHaptic(void)
{
    hapticTimer.start(50);
    haptic = 1;
}

void StopHaptic(void const *n)
{
    haptic = 0;
    hapticTimer.stop();
}

/****************************Call Back Functions*******************************/
void ButtonRight(void)
{
    StartHaptic();
    kw40z_device.ToggleAdvertisementMode();
    blueLed = !blueLed;
}

void ButtonLeft(void)
{
    StartHaptic();
    kw40z_device.ToggleAdvertisementMode();
    blueLed = !blueLed;
}

void PassKey(void)
{
    StartHaptic();
    strcpy((char *)text, "PAIR CODE");
    oled.TextBox((uint8_t *)text, 0, 25, 95, 18);

    /* Display Bond Pass Key in a 95px by 18px textbox at x=0,y=40 */
    sprintf(text, "%d", kw40z_device.GetPassKey());
    oled.TextBox((uint8_t *)text, 0, 40, 95, 18);
}

void AlertReceived(uint8_t *data, uint8_t length)
{
    StartHaptic();
    data[19] = 0;
    // pc.printf("%s\n\r", data);

    // data (our command) must 20 bytes long.
    // CMD for turning on: '11111111111111111111'
    if (data[4] == '1') {
        connectedToPi = true;
        // greenLed = LED_ON;
        //        redLed = LED_ON;

        // CMD for turning off: 'ledoffledoffledoffled'
    } else if (data[4] == '2') {
        // greenLed = LED_OFF;
        //        redLed = LED_OFF;
        startCollection = true;
    }
}
/***********************End of Call Back Functions*****************************/

/********************************Main******************************************/

int main()
{
    /* Register callbacks to application functions */
    kw40z_device.attach_buttonLeft(&ButtonLeft);
    kw40z_device.attach_buttonRight(&ButtonRight);
    kw40z_device.attach_passkey(&PassKey);
    kw40z_device.attach_alert(&AlertReceived);

    /* Turn on the backlight of the OLED Display */
    oled.DimScreenON();

    /* Fills the screen with solid black */
    oled.FillScreen(COLOR_BLACK);
    blueLed = 1;

    /* Get OLED Class Default Text Properties */
    oled_text_properties_t textProperties = {0};
    oled.GetTextProperties(&textProperties);

    /* Change font color to Blue */
    textProperties.fontColor = COLOR_BLUE;
    oled.SetTextProperties(&textProperties);

    /* Display Bluetooth Label at x=17,y=65 */
    strcpy((char *)text, "BLUETOOTH");
    oled.Label((uint8_t *)text, 17, 65);

    /* Change font color to white */
    textProperties.fontColor = COLOR_WHITE;
    textProperties.alignParam = OLED_TEXT_ALIGN_CENTER;
    oled.SetTextProperties(&textProperties);

    /* Display Label at x=22,y=80 */
    strcpy((char *)text, "Tap Below");
    oled.Label((uint8_t *)text, 22, 80);

    while (1) {
        while (!connectedToPi) {
            // Busy wait here until the PI has connected to the Hexi!
            Thread::wait(50);
        }
        while (!foundInitSequence) {
            // Some code here to find initial sequence to start the action:

            // After finding the initial sequence, we want to break out of the loop
            foundInitSequence = true;

            // We also want to send an alert to the Hexi (ONLY FOR THE WRIST ONE) that
            // we have found the sequence
        }
        
        // wait for message for the Pi
        while (!startCollection) {
            Thread::wait(50);
        }
        startCollection = false;
        
        collectRawData();
        processRawData();
        sendProcessedData();

        // Wait for two minutes before trying to go back into the init sequence
        // again in order for the ML on the python side to complete
        Thread::wait(120000);
        foundInitSequence = false;
    }

    // txThread.start(txTask); /*Start transmitting Sensor Tag Data */

    // while (true) {
    //   // blueLed = !kw40z_device.GetAdvertisementMode(); /*Indicate BLE
    //   // Advertisment Mode*/
    //   Thread::wait(50);
    // }
}

/******************************End of Main*************************************/

/****************************** Data Processing Functions *******************/

void updateValues()
{
    // stop arrays are full
    if (data_index == DATA_SIZE) {
        doneCollecting = true;
        return;
    }
    
    float dt = SYSTICK_PERIOD;
    float gyro_data[3];
    float accel_data[3];

    accel.acquire_accel_data_g(accel_data);
    gyro.acquire_gyro_data_dps(gyro_data);

    // convert to m/s^2
    x_accel = accel_data[0] * 9.8f;
    y_accel = accel_data[1] * 9.8f;
    z_accel = accel_data[2] * 9.8f;

    x_omega = gyro_data[0];
    y_omega = gyro_data[1];
    z_omega = gyro_data[2];

    // zero out readings for when stationary
    if (abs(x_accel) < 0.3f) {
        x_accel = 0;
    }
    if (abs(y_accel) < 0.3f) {
        y_accel = 0;
    }
    if (abs(z_accel) < 0.3f) {
        z_accel = 0;
    }

    if (abs(x_omega) < 0.5f) {
        x_omega = 0;
    }
    if (abs(y_omega) < 0.5f) {
        y_omega = 0;
    }
    if (abs(z_omega) < 0.5f) {
        z_omega = 0;
    }

    // integrate angular velocity
    x_theta += x_omega * dt;
    y_theta += y_omega * dt;
    z_theta += z_omega * dt;

    // store acceleration data
    accelData[data_index][0] = x_accel;
    accelData[data_index][1] = y_accel;
    accelData[data_index][2] = z_accel;

    // store gyro data
    gyroData[data_index][0] = x_theta;
    gyroData[data_index][1] = y_theta;
    gyroData[data_index][2] = z_theta;

    data_index++;
}
void resetValues()
{
    x_accel = 0;
    y_accel = 0;
    z_accel = 0;

    x_omega = 0;
    x_theta = 0;

    y_omega = 0;
    y_theta = 0;

    z_omega = 0;
    z_theta = 0;

    data_index = 0;
}

void collectRawData(void)
{
    // enable systick
    systick.attach(&updateValues, SYSTICK_PERIOD);

    doneCollecting = false;
    
    // wait for data collection to finish
    while (!doneCollecting) {
        ;
    }
    systick.detach();
    resetValues();
}

void processRawData(void)
{
    // The processed data here should convert from raw to uint_8t
    // Also we want to do some pre-processing and cleaning up here??

    int16_t gyro1 = 0, gyro2 = 0, gyro3 = 0, accel1 = 0, accel2 = 0, accel3 = 0;
    uint8_t gyro1sign = 0, gyro2sign = 0, gyro3sign = 0, accel1sign = 0, accel2sign = 0, accel3sign = 0;

    for (int i = 0; i < 50; i++) {
        gyro1 = gyroData[i * 10][0] * 100;
        gyro2 = gyroData[i * 10][1] * 100;
        gyro3 = gyroData[i * 10][2] * 100;

        accel1 = accelData[i * 10][0] * 100;
        accel2 = accelData[i * 10][1] * 100;
        accel3 = accelData[i * 10][2] * 100;

        gyro1sign = gyro1 > 0 ? 0 : 1;
        gyro2sign = gyro2 > 0 ? 0 : 1;
        gyro3sign = gyro3 > 0 ? 0 : 1;
        accel1sign = accel1 > 0 ? 0 : 1;
        accel2sign = accel2 > 0 ? 0 : 1;
        accel3sign = accel3 > 0 ? 0 : 1;

        gyro1 = abs(gyro1);
        gyro2 = abs(gyro2);
        gyro3 = abs(gyro3);
        accel1 = abs(accel1);
        accel2 = abs(accel2);
        accel3 = abs(accel3);

        processedGyroData[i][0] = (uint8_t)gyro1sign;
        processedGyroData[i][1] = (uint8_t)(gyro1 >> 8);
        processedGyroData[i][2] = (uint8_t)(gyro1 & 0xff);
        processedGyroData[i][3] = (uint8_t)gyro2sign;
        processedGyroData[i][4] = (uint8_t)(gyro2 >> 8);
        processedGyroData[i][5] = (uint8_t)(gyro2 & 0xff);
        processedGyroData[i][6] = (uint8_t)gyro3sign;
        processedGyroData[i][7] = (uint8_t)(gyro3 >> 8);
        processedGyroData[i][8] = (uint8_t)(gyro3 & 0xff);

        processedAccelData[i][0] = (uint8_t)accel1sign;
        processedAccelData[i][1] = (uint8_t)(accel1 >> 8);
        processedAccelData[i][2] = (uint8_t)(accel1 & 0xff);
        processedAccelData[i][3] = (uint8_t)accel2sign;
        processedAccelData[i][4] = (uint8_t)(accel2 >> 8);
        processedAccelData[i][5] = (uint8_t)(accel2 & 0xff);
        processedAccelData[i][6] = (uint8_t)accel3sign;
        processedAccelData[i][7] = (uint8_t)(accel3 >> 8);
        processedAccelData[i][8] = (uint8_t)(accel3 & 0xff);
    }
}

// This sends the data over to the Raspberry Pi
void sendProcessedData(void)
{
    uint8_t message[19];
    for (int i = 0; i < 40; i++) {
        message[0] = 0;
        for (int j = 0; j < 9; j++) {
            message[1 + j] = processedGyroData[i][j];
            message[10 + j] = processedAccelData[i][j];
        }
        kw40z_device.SendAlert(message, 19);
        Thread::wait(50);
    }
}

/****************************** End Data Processing Functions*******************/
