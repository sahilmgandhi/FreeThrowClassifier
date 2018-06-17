#include "Hexi_KW40Z.h"
#include "Hexi_OLED_SSD1351.h"
#include "OLED_types.h"
#include "OpenSans_Font.h"
#include "mbed.h"
#include "string.h"

#define LED_ON 1
#define LED_OFF 0

void UpdateSensorData(void);
void StartHaptic(void);
void StopHaptic(void const *n);
void txTask(void);

Serial pc(USBTX, USBRX);

// DigitalOut redLed(LED1);
DigitalOut greenLed(LED2);
DigitalOut blueLed(LED3);
DigitalOut haptic(PTB9);

/* Define timer for haptic feedback */
RtosTimer hapticTimer(StopHaptic, osTimerOnce);

/* Instantiate the Hexi KW40Z Driver (UART TX, UART RX) */
KW40Z kw40z_device(PTE24, PTE25);

/* Instantiate the SSD1351 OLED Driver */
SSD1351 oled(PTB22, PTB21, PTC13, PTB20, PTE6,
             PTD15); /* (MOSI,SCLK,POWER,CS,RST,DC) */

/*Create a Thread to handle sending BLE Sensor Data */
Thread txThread;

/* Text Buffer */
char text[20];

uint8_t buttonDir = 0;

uint8_t battery = 100;
uint8_t light = 0;
uint16_t humidity = 4500;
uint16_t temperature = 2000;
uint16_t pressure = 9000;
uint16_t x = 0;
uint16_t y = 5000;
uint16_t z = 10000;

volatile bool connectedToPi = false;

/****************************Call Back Functions*******************************/

void ButtonUp(void) {
  buttonDir = 1;
  kw40z_device.SendBatteryLevel(buttonDir);
}

void ButtonDown(void) {
  buttonDir = 2;
  kw40z_device.SendBatteryLevel(buttonDir);
}

void ButtonRight(void) {
  buttonDir = 3;
  kw40z_device.SendBatteryLevel(buttonDir);
}

void ButtonLeft(void) {
  buttonDir = 4;
  kw40z_device.SendBatteryLevel(buttonDir);
}

void PassKey(void) {
  StartHaptic();
  strcpy((char *)text, "PAIR CODE");
  oled.TextBox((uint8_t *)text, 0, 25, 95, 18);

  /* Display Bond Pass Key in a 95px by 18px textbox at x=0,y=40 */
  uint32_t passKey = kw40z_device.GetPassKey();
  sprintf(text, "%d", passKey);
  pc.printf(text);
  oled.TextBox((uint8_t *)text, 0, 40, 95, 18);
}

// Key modification: use the alert functionality enabled by the host-ble
// interface to define our own command.

void AlertReceived(uint8_t *data, uint8_t length) {
  StartHaptic();
  data[19] = 0;
  // pc.printf("%s\n\r", data);

  if (data[4] == '1') {
    // Now we can start looking for button presses!
    connectedToPi = true;
  }
}
/***********************End of Call Back Functions*****************************/

/********************************Main******************************************/

int main() {
  /* Register callbacks to application functions */
  kw40z_device.attach_passkey(&PassKey);
  kw40z_device.attach_alert(&AlertReceived);

  pc.printf("hello\n\r");

  blueLed = 1;
  greenLed = 1;
  //    redLed = 1;

  while (kw40z_device.GetAdvertisementMode() != 0) {
    kw40z_device.ToggleAdvertisementMode();
  }

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

  while (true) {
    if (connectedToPi) {
      // turn on all the button interrupts
      kw40z_device.attach_buttonLeft(&ButtonLeft);
      kw40z_device.attach_buttonRight(&ButtonRight);
      kw40z_device.attach_buttonUp(&ButtonUp);
      kw40z_device.attach_buttonDown(&ButtonDown);

      // Should only run once!
      connectedToPi = false;
    }
    Thread::wait(10);
  }
}

/******************************End of Main*************************************/

void StartHaptic(void) {
  hapticTimer.start(50);
  haptic = 1;
}

void StopHaptic(void const *n) {
  haptic = 0;
  hapticTimer.stop();
}
