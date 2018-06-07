#include "main.h"
#include "FXAS21002.h"
#include "FXOS8700.h"
#include "Hexi_KW40Z.h"
#include "Hexi_OLED_SSD1351.h"
#include "OLED_types.h"
#include "OpenSans_Font.h"
#include "mbed.h"
#include "string.h"

/* Define timer for haptic feedback */
RtosTimer hapticTimer(StopHaptic, osTimerOnce);

/* Instantiate the Hexi KW40Z Driver (UART TX, UART RX) */
KW40Z kw40z_device(PTE24, PTE25);

/* Instantiate the SSD1351 OLED Driver */
SSD1351 oled(PTB22, PTB21, PTC13, PTB20, PTE6,
             PTD15); /* (MOSI,SCLK,POWER,CS,RST,DC) */

/*Create a Thread to handle sending BLE Sensor Data */
Thread txThread;

/* Instantiate the gyroscope and accelerometer */
FXAS21002 gyro(PTC11, PTC10);
FXOS8700 accel(PTC11, PTC10);

/****************************Call Back Functions*******************************/
void ButtonRight(void) {
  StartHaptic();
  kw40z_device.ToggleAdvertisementMode();
}

void ButtonLeft(void) {
  StartHaptic();
  kw40z_device.ToggleAdvertisementMode();
}

void PassKey(void) {
  StartHaptic();
  strcpy((char *)text, "PAIR CODE");
  oled.TextBox((uint8_t *)text, 0, 25, 95, 18);

  /* Display Bond Pass Key in a 95px by 18px textbox at x=0,y=40 */
  sprintf(text, "%d", kw40z_device.GetPassKey());
  oled.TextBox((uint8_t *)text, 0, 40, 95, 18);
}
/***********************End of Call Back Functions*****************************/

/********************************Main******************************************/

int main() {
  /* Register callbacks to application functions */
  kw40z_device.attach_buttonLeft(&ButtonLeft);
  kw40z_device.attach_buttonRight(&ButtonRight);
  kw40z_device.attach_passkey(&PassKey);

  /* Turn on the backlight of the OLED Display */
  oled.DimScreenON();

  /* Fills the screen with solid black */
  oled.FillScreen(COLOR_BLACK);

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

  uint8_t prevLinkState = 0;
  uint8_t currLinkState = 0;

  while (1) {
    while (!foundInitSequence) {
      // Some code here to find initial sequence to start the action:

      // After finding the initial sequence, we want to break out of the loop
      foundInitSequence = true;
    }
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

void collectRawData(void) {
  // Fill out some better way to collect. Currently it will just go through and
  // fill up the array naively
  float gyro_data[3];
  float accel_data[3];
  for (int i = 0; i < 400; i++) {
    accel.acquire_accel_data_g(accel_data);
    gyro.acquire_gyro_data_dps(gyro_data);

    gyroData[i][0] = gyro_data[0];
    gyroData[i][1] = gyro_data[1];
    gyroData[i][2] = gyro_data[2];

    accelData[i][0] = accel_data[0];
    accelData[i][1] = accel_data[1];
    accelData[i][2] = accel_data[2];
    wait(0.01);
  }
}

void processRawData(void) {
  // The processed data here should convert from raw to uint_8t
  // Also we want to do some pre-processing and cleaning up here??

  int16_t gyro1 = 0, gyro2 = 0, gyro3 = 0, accel1 = 0, accel2 = 0, accel3 = 0;
  uint8_t gyro1sign = 0, gyro2sign = 0, gyro3sign = 0, accel1sign = 0,
          accel2sign = 0, accel3sign = 0;

  for (int i = 0; i < 40; i++) {
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

    processedGyroData[i][0] = gyro1sign;
    processedGyroData[i][1] = (gyro1 >> 8);
    processedGyroData[i][2] = (gyro1 & 0xff);
    processedGyroData[i][3] = gyro2sign;
    processedGyroData[i][4] = (gyro2 >> 8);
    processedGyroData[i][5] = (gyro2 & 0xff);
    processedGyroData[i][6] = gyro3sign;
    processedGyroData[i][7] = (gyro3 >> 8);
    processedGyroData[i][8] = (gyro3 & 0xff);

    processedAccelData[i][0] = accel1sign;
    processedAccelData[i][1] = (accel1 >> 8);
    processedAccelData[i][2] = (accel1 & 0xff);
    processedAccelData[i][3] = accel2sign;
    processedAccelData[i][4] = (accel2 >> 8);
    processedAccelData[i][5] = (accel2 & 0xff);
    processedAccelData[i][6] = accel3sign;
    processedAccelData[i][7] = (accel3 >> 8);
    processedAccelData[i][8] = (accel3 & 0xff);
  }
}

// This sends the data over to the Raspberry Pi
void sendProcessedData(void) {
  uint8_t message[19];
  for (int i = 0; i < 40; i++) {
    message[0] = 0;
    for (int j = 0; j < 9; j++) {
      message[1 + j] = processedGyroData[i][j];
      message[10 + j] = processedAccelData[i][j];
    }
    kw40z_device.sendAlert(message, 19);
    Thread::wait(50);
  }
}

/****************************** End Data Processing Functions
 * *******************/

/* txTask() transmits the sensor data */
void txTask(void) {

  while (true) {
    UpdateSensorData();

    /*Notify Hexiwear App that it is running Sensor Tag mode*/
    kw40z_device.SendSetApplicationMode(GUI_CURRENT_APP_SENSOR_TAG);

    /*The following is sending dummy data over BLE. Replace with real data*/

    /*Send Battery Level for 20% */
    kw40z_device.SendBatteryLevel(battery);
    uint8_t testStr[3] = {1, 2, 3};
    kw40z_device.sendAlert(testStr, 3);

    Thread::wait(1000);
  }
}

void UpdateSensorData(void) {
  battery -= 5;
  if (battery < 5)
    battery = 100;

  light += 20;
  if (light > 100)
    light = 0;

  humidity += 500;
  if (humidity > 8000)
    humidity = 2000;

  temperature -= 200;
  if (temperature < 200)
    temperature = 4200;

  pressure += 300;
  if (pressure > 10300)
    pressure = 7500;

  x += 1400;
  y -= 2300;
  z += 1700;
}

void StartHaptic(void) {
  hapticTimer.start(50);
  haptic = 1;
}

void StopHaptic(void const *n) {
  haptic = 0;
  hapticTimer.stop();
}