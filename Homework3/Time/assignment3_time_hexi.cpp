#include "mbed.h"
#include "Hexi_KW40Z.h"
#include "Hexi_OLED_SSD1351.h"
#include "OLED_types.h"
#include "OpenSans_Font.h"
#include "string.h"

#define LED_ON      0
#define LED_OFF     1

void UpdateSensorData(void);
void StartHaptic(void);
void StopHaptic(void const *n);
void txTask(void);

DigitalOut led1(LED1);
DigitalOut pin10(PTA10);
Serial pc(USBTX, USBRX);

/* Instantiate the Hexi KW40Z Driver (UART TX, UART RX) */
KW40Z kw40z_device(PTE24, PTE25);

/* Instantiate the SSD1351 OLED Driver */
SSD1351 oled(PTB22,PTB21,PTC13,PTB20,PTE6, PTD15); /* (MOSI,SCLK,POWER,CS,RST,DC) */

/* Text Buffer */
char text[10];
char dataIn[20];
char time_dis[11] = "  :  :  . ";
/* Ticker */
Ticker t;
short d_sec = 0;
short sec0 = 0;
short sec1 = 0;
short min0 = 0;
short min1 = 0;
short hr0 = 0;
short hr1 = 0;
short hr = 0;
bool block = true;
bool attached = false;
void displayTime()
{
    time_dis[0] = hr1 + 48;
    time_dis[1] = hr0 + 48;
    time_dis[3] = min1 + 48;
    time_dis[4] = min0 + 48;
    time_dis[6] = sec1 + 48;
    time_dis[7] = sec0 + 48;
    time_dis[9] = d_sec + 48;
    
    pin10 = sec0 % 2;
    strcpy((char *) text,"Time");
    //strcpy((char *) data2,"1234567890");
    oled.TextBox((uint8_t *)text,0,25,95,18);
    oled.TextBox((uint8_t *)time_dis,0,40,95,18);
    //pc.printf("%s\n\r", time_dis);
}

void tick()
{
    d_sec++;
    displayTime();
}
void AlertReceived(uint8_t *data, uint8_t length)
{
    data[19] = 0;
    hr1 =(short)(data[0] - 48);
    hr0 =(short)(data[1] - 48);
    min1 = (short)(data[3] - 48);
    min0 = (short)(data[4] - 48);
    sec1 = (short)(data[6] - 48);
    sec0 = (short)(data[7] - 48);
    d_sec = (short)(data[9] - 48);
    strcpy((char*)dataIn, (char*)data);
    //pc.printf("Received: %s\n\r", data);
    if(!attached) {
        t.attach(&tick, 0.1);
        attached = true;
    }

}

/********************************Main******************************************/

void ButtonRight(void)
{
    kw40z_device.ToggleAdvertisementMode();
    led1 = !led1;
}

void ButtonLeft(void)
{
    led1 = !led1;
    kw40z_device.ToggleAdvertisementMode();
}
void PassKey(void)
{
    strcpy((char *) text,"PAIR CODE");
    oled.TextBox((uint8_t *)text,0,25,95,18);

    /* Display Bond Pass Key in a 95px by 18px textbox at x=0,y=40 */
    sprintf(text,"%d", kw40z_device.GetPassKey());
    pc.printf("Pass Key: %s\n\r", text);
    oled.TextBox((uint8_t *)text,0,40,95,18);
    //pc.printf("Pass Key: %d", text);
    block = true;
}
void initDisplay(void)
{
    /* Turn on the backlight of the OLED Display */
    oled.DimScreenON();

    /* Fills the screen with solid black */
    oled.FillScreen(COLOR_BLACK);

    /* Get OLED Class Default Text Properties */
    oled_text_properties_t textProperties = {0};
    oled.GetTextProperties(&textProperties);

    textProperties.fontColor   = COLOR_WHITE;
    textProperties.alignParam = OLED_TEXT_ALIGN_CENTER;
    oled.SetTextProperties(&textProperties);
}


int main()
{

    kw40z_device.attach_alert(&AlertReceived);
    kw40z_device.attach_buttonLeft(&ButtonLeft);
    kw40z_device.attach_buttonRight(&ButtonRight);
    kw40z_device.attach_passkey(&PassKey);
    pc.printf("hello\n\r");

    while (kw40z_device.GetAdvertisementMode() != 0) {
        kw40z_device.ToggleAdvertisementMode();
    }
    pc.printf("Time: %s", text);
    oled.Label((uint8_t *)text,17,65);

    /* Change font color to white */
    //textProperties.fontColor   = COLOR_WHITE;
    //textProperties.alignParam = OLED_TEXT_ALIGN_CENTER;
    //oled.SetTextProperties(&textProperties);


    while (true) {
        if(d_sec >= 10) {
            sec0++;
            d_sec = 0;
        }
        if(sec0 >= 10) {
            sec1++;
            sec0 = 0;
        }
        if(sec1 >= 6) {
            min0++;
            sec1 = 0;
        }
        if(min0 >= 10) {
            min1++;
            min0 = 0;
        }
        if(min1 >= 6) {
            hr++;
            min1 = 0;
        }

        Thread::wait(50);
    }
}

/******************************End of Main*************************************/

